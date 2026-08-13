#!/bin/sh
# merge-target-guard — does this merge land where you think it does? (SCC-144)
#
# Every other gate in this system checks the branch you merge FROM. `--expect-key`, the preflight's
# header line, `main_write_gate.py`, the push token — all of them. NOTHING checked the branch you
# merge INTO, and on 2026-08-11 that cost a production merge commit on a sibling lane's branch
# (SCC-97, commit 0b380d4): a `cd` in one tool call, the shell's working directory silently
# reverting between calls, and a bare `git merge` in a later one. It printed success. The file list
# and the message both read correctly, because the message says `-> main` only because someone
# typed that. It was caught by suspicion.
#
# The law this enforces: .agents/rules/git-policy.md § "Branch model". `main` is the only long-lived
# branch; `epic/*` and `chore/*` are cut from it and land back on it; `claude/*` story lanes land on
# their `epic/*`.
#
# ⛔⛔ WHY THIS RUNS FROM `commit-msg` AND NOT FROM `pre-merge-commit` — MEASURED, NOT ASSUMED.
#
# SCC-144 was written to build `.githooks/pre-merge-commit`, on the reasoning that its target is
# HEAD and its source is `git rev-parse MERGE_HEAD`. Half of that is true. A trace of a real merge
# in a real repo (2026-08-13) found:
#
#   merge path            pre-merge-commit    MERGE_HEAD there   commit-msg   MERGE_HEAD there
#   clean auto-merge      FIRES               ABSENT             FIRES        present
#   conflicted merge      NEVER FIRES         --                 FIRES        present
#   fast-forward          never fires         --                 never fires  --
#
# `pre-merge-commit` runs BEFORE git writes MERGE_HEAD (and before MERGE_MSG), so it fires with no
# way to name what is being merged in — it can see the target and nothing else, and every rule in
# the branch model is a rule about a PAIR. And on the conflicted path — the one a multi-lane
# landing hits constantly, four conflict classes in one 2026-08-13 run — it never fires at all,
# because the commit is then made by `git commit`, not by `git merge`.
#
# `commit-msg` fires on BOTH merge paths and has MERGE_HEAD in both. So the guard lives here. A
# `pre-merge-commit` hook was written first and DELETED rather than shipped decorative: a gate that
# cannot answer its own question is the vacuous green this system keeps closing.
#
# The refusal is one step later than planned and no weaker: a failing `commit-msg` aborts the
# commit, so no merge commit is created either way. It leaves the merge IN PROGRESS rather than
# untouched, which is why the remedy printed below is `git merge --abort`.
#
# ⓘ Two of the three gates on this dispatcher EXEMPT merges (`commit-msg-jira.sh`,
# `sop-currency.sh` — git writes those messages, so blocking them blocks the tool). This one exists
# ONLY for merges. Same hook, opposite carve-out, on purpose.
#
# ─── Why POSIX sh with no Python and no interpreter probe ──────────────────────────────────
# The same reason `pre-push-main-approval.sh` is: five Claude hooks were once wired to
# `powershell -Command "python ..."` and the Mac has NEITHER binary. They exited 127, silently, for
# weeks (SCC-71/SCC-77). A gate must not depend on the class of thing that broke the last gate.
#
# ─── What it refuses, and what it deliberately does not ────────────────────────────────────
# It refuses ONLY known-bad topologies. An unclassified branch (`incident-*` is explicitly outside
# the branch model), or a merge whose source cannot be named at all, is ALLOWED — with a line
# saying so. And where one sha carries several branch names, ANY legal name wins.
#
# That bias is deliberate and it is not laziness. A gate that blocks a correct merge is one an
# operator learns to route around, and this repo has already shipped four of those (`hooks_armed`
# hard-blocking close-out over a README in `.githooks/`, over a `.gitignore`, over a `~` in a path;
# `check_maps` false-STALEing every worktree). The ambiguous case is still caught at push time by
# pre-push-merge-backstop.sh. A missed catch costs one more layer; a false red costs the gate.
#
# Kill switch:      .agents/scripts/git-hooks/DISABLE     (the file every gate here honors)
# Disarm entirely:  delete .agents/scripts/git-hooks/MERGE-TARGET-ENFORCE
# Bypass once:      git merge --no-verify
#
# ⛔ `--no-verify` skipping this hook is ACCEPTED, not a hole to be closed later. It is an explicit,
# auditable override — the same posture as `[sop-ok]` on the SOP gate. The failure this guard exists
# to stop is the SILENT one; a person typing `--no-verify` has made a decision and left a record of
# it in their shell history. Do not "fix" this.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

ENFORCE=1
[ -f .agents/scripts/git-hooks/MERGE-TARGET-ENFORCE ] || ENFORCE=0

# The branch RECEIVING the merge. HEAD is still the target while the merge commit is being made —
# measured, not assumed, on both the auto-merge and the conflicted path.
TARGET=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ -n "$TARGET" ] || exit 0
[ "$TARGET" = "HEAD" ] && exit 0          # detached — there is no branch to judge

# What is being merged IN. `git rev-parse MERGE_HEAD` and NOT the path `.git/MERGE_HEAD`: in a
# worktree `.git` is a FILE, so a path probe is always false there — which is exactly the bug this
# lane also fixed in commit-msg-jira.sh and sop-currency.sh. Every lane in this system is a worktree.
#
# No MERGE_HEAD means this is an ordinary commit, which is not this gate's business — the two gates
# that run after it are the ones for those.
MERGE_SHA=$(git rev-parse --verify --quiet MERGE_HEAD) || exit 0

# ─── Naming the source ─────────────────────────────────────────────────────────────────────
# A sha is not a branch. Collect every name that points at it — local branches first, then
# remote-tracking ones (`git merge origin/main` is an everyday move), with `origin/` stripped so
# `origin/main` and `main` classify identically. If nothing points at it, fall back to the message
# git itself wrote, which names the branch even after that branch is deleted.
CANDIDATES=$(
  {
    git branch --points-at "$MERGE_SHA" --format='%(refname:short)' 2>/dev/null
    git branch -r --points-at "$MERGE_SHA" --format='%(refname:short)' 2>/dev/null
  } | sed 's#^origin/##' | sed '/^$/d' | sort -u
)

if [ -z "$CANDIDATES" ]; then
  MERGE_MSG_FILE=$(git rev-parse --git-path MERGE_MSG 2>/dev/null)
  if [ -n "$MERGE_MSG_FILE" ] && [ -f "$MERGE_MSG_FILE" ]; then
    CANDIDATES=$(sed -n "1s/^Merge \(remote-tracking \)\{0,1\}branch '\([^']*\)'.*/\2/p" \
                 "$MERGE_MSG_FILE" | sed 's#^origin/##')
  fi
fi

# ─── The branch model, as a function ───────────────────────────────────────────────────────
classify() {
  case "$1" in
    main)      echo main ;;
    epic/*)    echo epic ;;
    chore/*)   echo chore ;;
    claude/*)  echo story ;;
    *)         echo unknown ;;
  esac
}

# judge <target-class> <source-class>  ->  allow | refuse | unknown
judge() {
  case "$1:$2" in
    unknown:*|*:unknown)          echo unknown ;;
    main:main|main:epic|main:chore) echo allow ;;
    main:story)                   echo refuse ;;
    epic:main|epic:story)         echo allow ;;
    epic:epic|epic:chore)         echo refuse ;;
    chore:main)                   echo allow ;;
    chore:chore|chore:epic|chore:story) echo refuse ;;
    story:main|story:epic)        echo allow ;;
    story:story|story:chore)      echo refuse ;;
    *)                            echo unknown ;;
  esac
}

# Where a branch of this class is allowed to land — so the refusal tells you what to do, not just
# what you did. A diagnosis with no remedy is half a gate.
destination() {
  case "$1" in
    chore)   echo "a chore/* lane merges into main (/smh-close-task-merge-tree)" ;;
    epic)    echo "an epic/* branch merges into main (/cicd-push-e2e)" ;;
    story)   echo "a claude/* story lane merges into ITS epic/* branch" ;;
    main)    echo "main is absorbed INTO a lane, never the other way around" ;;
    *)       echo "see .agents/rules/git-policy.md § Branch model" ;;
  esac
}

TARGET_CLASS=$(classify "$TARGET")

ALLOWED=""
REFUSED=""
REFUSED_SRC=""
REFUSED_CLASS=""
SEEN=""

for name in $CANDIDATES; do
  SEEN=1
  # The same branch by another name (`git merge origin/<self>`) is never a target violation.
  if [ "$name" = "$TARGET" ]; then
    ALLOWED=1
    continue
  fi
  SRC_CLASS=$(classify "$name")
  case "$(judge "$TARGET_CLASS" "$SRC_CLASS")" in
    allow)  ALLOWED=1 ;;
    refuse) REFUSED=1; REFUSED_SRC=$name; REFUSED_CLASS=$SRC_CLASS ;;
  esac
done

# ⭐ ANY ALLOW WINS. Only a source that is unambiguously in the wrong place is refused.
if [ -n "$ALLOWED" ] || [ -z "$REFUSED" ]; then
  if [ -z "$ALLOWED" ] && [ -z "$REFUSED" ]; then
    if [ -z "$SEEN" ]; then
      echo "  ⓘ merge-target-guard: nothing names $MERGE_SHA, so the source branch could not be"
      echo "    determined — declined to judge, merge allowed. The pre-push backstop still sees it."
    else
      echo "  ⓘ merge-target-guard: '$TARGET' <- '$CANDIDATES' is outside the branch model"
      echo "    (.agents/rules/git-policy.md), so this guard declined to judge it. Merge allowed."
    fi
  fi
  exit 0
fi

# ─── The refusal ───────────────────────────────────────────────────────────────────────────
SIGNATURE=""
if [ "$TARGET_CLASS" = "chore" ] && [ "$REFUSED_CLASS" = "chore" ]; then
  SIGNATURE="  ⛔ This is the SCC-97 signature exactly: one lane's work landing on a SIBLING LANE.
     On 2026-08-11 it printed success and was caught only by suspicion.
"
fi

BANNER="  ⛔ MERGE REFUSED — wrong TARGET branch"
[ "$ENFORCE" = "1" ] || BANNER="  ⚠ merge-target-guard: this merge is WRONG, but the gate is disarmed"

echo ""
echo "$BANNER"
echo ""
echo "     target (the branch RECEIVING it):  $TARGET   [$TARGET_CLASS]"
echo "     source (what is being merged in):  $REFUSED_SRC   [$REFUSED_CLASS]"
echo ""
printf '%s' "$SIGNATURE"
echo "     Rule: .agents/rules/git-policy.md § Branch model —"
echo "       $(destination "$REFUSED_CLASS")"
echo ""
echo "     A merge onto the wrong LOCAL branch is never pushed, so no push-time gate ever"
echo "     sees it. This hook is the only layer that can refuse it."
echo ""
echo "     Remedy:  git merge --abort   then re-check where you are standing:"
echo "                git -C \"\$REPO\" rev-parse --abbrev-ref HEAD"
echo "              A cd is not a lock across steps — pass -C on every git call."
echo "     Bypass once: git merge --no-verify"
echo ""

[ "$ENFORCE" = "1" ] || exit 0
exit 1
