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
# It refuses ONLY known-bad topologies. An incident lane — `claude/incident-<short-id-lower>`, the
# ONLY shape the incident pipeline creates (cicd-mobile-error-team.md), and it MATCHES the
# `claude/*` glob — is positively classified by a carve-out ABOVE the story arm; ABSORBING main
# (or an epic) into it is allowed outright, and its hotfix landing ON main is deliberately
# unjudged, because an emergency local merge must never eat a story-lane refusal mid-incident
# (SCC-149/SCC-154; this comment once claimed a bare
# incident prefix was outside the branch model while no such arm existed and the real prefix
# classified as STORY). Its four pairings with story and chore lanes are REFUSED since SCC-154 —
# they previously fell to the unjudged default, and a story or chore lane exchanging work with an
# incident lane is the SCC-97 wrong-target shape wearing an incident name. A branch no arm
# classifies, or a merge whose source cannot be named at all, is ALLOWED — with a line saying
# so. And where one sha carries several branch names, ANY legal name wins — except through
# `unknown`: an incident name never launders a refusable sibling name (unknown ≠ allow).
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
#
# ⛔ EVERY PARENT, NOT THE FIRST — AND THAT MEANS READING THE FILE. On an OCTOPUS merge MERGE_HEAD
# holds one sha per line, and BOTH rev-parse forms return only the first: `--verify --quiet` prints
# it and exits 0 rather than failing, and bare `rev-parse MERGE_HEAD` does the same. So
# `git merge main <sibling-lane>` from a lane was judged on `main` alone, returned allow, and
# sealed a commit whose later parent was an illegal source — position-dependently, since reversing
# the arguments refused. Measured; found by two review lenses.
#
# ⭐ `--git-path`, never a literal `.git/MERGE_HEAD`: in a worktree `.git` is a FILE. This is the
# same probe the F-D half of this lane fixed in the two sibling gates, and reading the file rather
# than asking rev-parse is what makes the octopus case answerable at all.
MERGE_HEAD_FILE=$(git rev-parse --git-path MERGE_HEAD 2>/dev/null)
MERGE_SHAS=""
if [ -n "$MERGE_HEAD_FILE" ] && [ -f "$MERGE_HEAD_FILE" ]; then
  MERGE_SHAS=$(sed '/^$/d' "$MERGE_HEAD_FILE")
fi

# ─── The squash path, which writes no MERGE_HEAD at all ────────────────────────────────────
# `git merge --squash` is documented as not recording MERGE_HEAD, and it rewrites history, so the
# source is not an ancestor of the result either — meaning NEITHER this guard nor the pre-push
# backstop could see it. That made it a second silent hole, not the "one measured blind spot" the
# backstop's header claimed. What git does leave is SQUASH_MSG, listing the squashed commits, and
# the first one is the tip of the branch that was squashed — which is all the naming machinery
# below needs.
if [ -z "$MERGE_SHAS" ]; then
  SQUASH_FILE=$(git rev-parse --git-path SQUASH_MSG 2>/dev/null)
  if [ -n "$SQUASH_FILE" ] && [ -f "$SQUASH_FILE" ]; then
    MERGE_SHAS=$(sed -n 's/^commit \([0-9a-f]\{7,\}\)$/\1/p' "$SQUASH_FILE" | head -1)
  fi
fi

[ -n "$MERGE_SHAS" ] || exit 0

# ─── Naming a source ───────────────────────────────────────────────────────────────────────
# A sha is not a branch. Collect every name that points at it — local branches first, then
# remote-tracking ones (`git merge origin/main` is an everyday move), with `origin/` stripped so
# `origin/main` and `main` classify identically. If nothing points at it, fall back to the message
# git itself wrote, which names the branch even after that branch is deleted.
names_for() {
  _n=$(
    {
      git branch --points-at "$1" --format='%(refname:short)' 2>/dev/null
      git branch -r --points-at "$1" --format='%(refname:short)' 2>/dev/null
    } | sed 's#^origin/##' | sed '/^$/d' | sort -u
  )
  if [ -z "$_n" ]; then
    _msg=$(git rev-parse --git-path MERGE_MSG 2>/dev/null)
    if [ -n "$_msg" ] && [ -f "$_msg" ]; then
      _n=$(sed -n "1s/^Merge \(remote-tracking \)\{0,1\}branch '\([^']*\)'.*/\2/p" \
           "$_msg" | sed 's#^origin/##')
    fi
  fi
  printf '%s\n' "$_n"
}

# ─── The branch model, as a function ───────────────────────────────────────────────────────
classify() {
  case "$1" in
    main)      echo main ;;
    epic/*)    echo epic ;;
    chore/*)   echo chore ;;
    # ⛔ ORDER IS LOAD-BEARING: `claude/incident-*` sits ABOVE `claude/*` because `case` is
    # first-match — below it this arm is dead code and a real incident lane classifies as story
    # (SCC-149; the same first-match shape SCC-148 fixed in task_preflight's WRONG_LANE).
    claude/incident-*) echo incident ;;
    claude/*)  echo story ;;
    *)         echo unknown ;;
  esac
}

# judge <target-class> <source-class>  ->  allow | refuse | unknown
judge() {
  case "$1:$2" in
    # ⭐ The ABSORB is sanctioned OUTRIGHT (SCC-154 review): an incident TARGET taking main
    # (or an epic) in is the everyday mid-incident move, and `allow` — not `unknown` — is
    # what lets any-legal-name-wins protect it when a freshly-cut sibling lane's tip
    # coincides with main's (an incident target otherwise has NO allow arm, so a coincident
    # story name forced a story-lane refusal onto the emergency path — the false red this
    # file's own charter prices above a miss, measured by the review).
    incident:main|incident:epic)  echo allow ;;
    # ⛔ ORDER IS LOAD-BEARING (SCC-154): these four sit ABOVE the incident wildcard because
    # `case` is first-match — below it they are dead code and the pairs fall back to unjudged,
    # which is exactly where the SCC-149 review measured them. An incident lane exchanges work
    # with main (or an epic, absorbing) and NEVER with a story or chore lane: that pairing is
    # the SCC-97 wrong-target shape wearing an incident name.
    story:incident|chore:incident|incident:story|incident:chore) echo refuse ;;
    # Everything else incident-shaped (the hotfix landing on main or an epic, incident with
    # unknown, incident with incident) is positively classified, then DELIBERATELY unjudged —
    # those merges are the incident pipeline's business (/cicd-mobile-error-team), and the one
    # local merge that matters, an emergency hotfix onto main, must never eat a refusal
    # mid-incident (SCC-149).
    incident:*|*:incident)        echo unknown ;;
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
    incident) echo "claude/incident-* is the incident pipeline's lane (/cicd-mobile-error-team); it exchanges work with main (or an epic), never with a story or chore lane" ;;
    *)       echo "see .agents/rules/git-policy.md § Branch model" ;;
  esac
}

TARGET_CLASS=$(classify "$TARGET")

REFUSED=""
REFUSED_SRC=""
REFUSED_CLASS=""
UNJUDGED=""
UNJUDGED_NAMES=""
ANY_NAMED=""
INCIDENT_SEEN=""
[ "$TARGET_CLASS" = "incident" ] && INCIDENT_SEEN=1

# ⭐ ONE VERDICT PER SOURCE, and the aggregate refuses if ANY source is unambiguously in the wrong
# place. Within a single source, ANY LEGAL NAME WINS — one sha can carry several branch names and
# the bias there is deliberately toward the false negative. ACROSS sources it is the opposite: an
# octopus merge with one legal and one illegal parent is not ambiguous, it is illegal.
for sha in $MERGE_SHAS; do
  CANDIDATES=$(names_for "$sha")
  src_allowed=""
  src_refused=""
  src_refused_name=""
  src_refused_class=""
  seen=""

  for name in $CANDIDATES; do
    seen=1
    ANY_NAMED=1
    # The same branch by another name (`git merge origin/<self>`) is never a target violation.
    if [ "$name" = "$TARGET" ]; then
      src_allowed=1
      continue
    fi
    SRC_CLASS=$(classify "$name")
    [ "$SRC_CLASS" = "incident" ] && INCIDENT_SEEN=1
    case "$(judge "$TARGET_CLASS" "$SRC_CLASS")" in
      allow)  src_allowed=1 ;;
      refuse) src_refused=1; src_refused_name=$name; src_refused_class=$SRC_CLASS ;;
    esac
  done

  if [ -n "$src_allowed" ]; then
    continue
  fi
  if [ -n "$src_refused" ]; then
    REFUSED=1
    REFUSED_SRC=$src_refused_name
    REFUSED_CLASS=$src_refused_class
    continue
  fi
  # Nothing judgeable about this source — record it so the decision is announced, never silent.
  UNJUDGED=1
  if [ -z "$seen" ]; then
    UNJUDGED_NAMES="$UNJUDGED_NAMES $sha"
  else
    UNJUDGED_NAMES="$UNJUDGED_NAMES $(printf '%s' "$CANDIDATES" | tr '\n' '/')"
  fi
done

if [ -z "$REFUSED" ]; then
  if [ -n "$UNJUDGED" ]; then
    if [ -z "$ANY_NAMED" ]; then
      echo "  ⓘ merge-target-guard: nothing names$UNJUDGED_NAMES, so the source branch could not"
      echo "    be determined — declined to judge, merge allowed. The pre-push backstop still"
      echo "    sees it."
      if [ -n "$INCIDENT_SEEN" ]; then
        echo "    (claude/incident-* is the incident pipeline's lane — /cicd-mobile-error-team"
        echo "    owns it. Positively classified, deliberately unjudged; not a gap. SCC-149)"
      fi
    elif [ -n "$INCIDENT_SEEN" ]; then
      # SCC-154 (finding 3): the incident line REPLACES the generic one. "Positively
      # classified" printed one line under "outside the branch model" was this guard
      # contradicting itself about the one class it classifies on purpose — and the pairing
      # is runtime-assembled, so no source grep could ever see it.
      echo "  ⓘ merge-target-guard: '$TARGET' <-$UNJUDGED_NAMES — claude/incident-* is the"
      echo "    incident pipeline's lane (/cicd-mobile-error-team owns it): positively"
      echo "    classified, deliberately unjudged, not a gap (SCC-149). Merge allowed."
    else
      echo "  ⓘ merge-target-guard: '$TARGET' <-$UNJUDGED_NAMES is outside the branch model"
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
