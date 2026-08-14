#!/bin/sh
# pre-push-merge-backstop — the fast-forward net for the merge-target guard (SCC-144).
#
# merge-target-guard.sh refuses a merge that lands on the wrong branch, from `commit-msg`. It has
# one measured blind spot and this file is it:
#
#   A FAST-FORWARD MERGE CREATES NO COMMIT, so no commit-time hook runs at all. Measured on a real
#   repo: `git merge --ff-only` fires only `post-merge`, which is after the fact and cannot refuse.
#   And SCC-97's own RECOVERY deliberately used `--ff-only`, so this is not a hypothetical path.
#
# What a ff merge cannot hide is the evidence it leaves: ANOTHER LANE'S UNLANDED COMMITS ARE NOW
# CONTAINED IN YOURS. That is the whole check, and it is deliberately ONE check rather than an
# attempt to re-classify historical merge commits — those do not carry the branch names they were
# made on, `git name-rev` only guesses, and every wrong guess is a false red on the shipping path.
#
#   For a pushed `refs/heads/chore/*` or `refs/heads/claude/*`:
#     refuse if any OTHER local chore/claude branch is an ancestor of the pushed sha
#     AND is not reachable from this lane's own INTEGRATION BRANCH.
#
# ⛔ THE "ALREADY LANDED" HALF IS WHAT MAKES IT USABLE. After a sibling lands and you absorb the
# branch you integrate on, that sibling's commits are ancestors of your lane too — the single most
# common thing a lane does. Keying on containment alone would refuse it. Asking whether the foreign
# lane has already landed separates "landed, so it is everyone's" from "still in flight".
#
# ⛔⛔ AND "LANDED" IS NOT ALWAYS `origin/main`. The first cut of this file asked only about
# `origin/main`, which is right for a `chore/*` lane and WRONG FOR EVERY STORY LANE: a `claude/*`
# lane integrates on its `epic/*` branch, and an epic does not reach `main` until `/cicd-push-e2e`
# ships the whole epic. So the moment one story landed on the epic and a sibling absorbed it, this
# refused a push that `git-policy.md` marks FREE — no approval — and that `/cicd-park` performs
# verbatim (`git merge origin/epic/<KEY>-<slug>` then `git push -u origin claude/<KEY>-<slug>`).
# Park exists to stop work being stranded on one machine; refusing it strands the work.
#
# Found by three independent review lenses, two of which reproduced it end to end against a real
# remote. It is the exact failure this file's own header calls the expensive one, committed by the
# file that names it: the `origin/main` reasoning was derived for chore→main and then applied to
# story lanes without being re-derived. The reference set is now per-class.
#
# ⛔ AND IT NEVER RUNS ON `main` OR `epic/*`, ON PURPOSE. `/smh-close-task-merge-tree` merges
# chore/X into main and pushes main; at that moment chore/X is contained and unlanded BY
# DEFINITION — that is what landing IS. Gating it would refuse this system's primary shipping path
# on every close-out. Same for a story lane landing on its epic.
#
# ⓘ No `origin/main` means there is no reference point for "landed", so it declines and says so.
# Refusing on the absence of a reference point is the vacuous red — the mirror of the vacuous green
# this system keeps closing — and it would fire on the first push of a brand-new clone.
#
# Kill switch:      .agents/scripts/git-hooks/DISABLE
# Disarm entirely:  delete .agents/scripts/git-hooks/MERGE-TARGET-ENFORCE   (ONE flag, both halves)
# Bypass once:      git push --no-verify

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

ENFORCE=1
[ -f .agents/scripts/git-hooks/MERGE-TARGET-ENFORCE ] || ENFORCE=0

ZERO="0000000000000000000000000000000000000000"
STATUS=0

# Where a lane of this class lands, so the remedy names the operator's actual next move rather
# than a generic one. The first cut printed "land it on main first" at a story lane, which is the
# one thing merge-target-guard.sh refuses (`main:story` -> refuse).
integration_of() {
  case "$1" in
    # ⛔ ORDER IS LOAD-BEARING (SCC-154): the incident arm sits ABOVE `claude/*` — `case` is
    # first-match and the story glob matches incident names too. "its epic/* branch" here was
    # the SCC-148 misroute verbatim, printed by the enforcement machinery itself, to a phone,
    # mid-incident (SCC-149 C1): an incident branch lands on MAIN via the incident pipeline.
    claude/incident-*) echo "main via the incident pipeline (/cicd-mobile-error-team)" ;;
    claude/*) echo "its epic/* branch" ;;
    *)        echo "main" ;;
  esac
}

refuse() {   # $1 = the lane being pushed, $2 = the foreign lane riding on it
  if [ "$ENFORCE" = "1" ]; then
    echo ""
    echo "  ⛔ PUSH REFUSED — this lane is carrying another lane's unlanded work"
  else
    echo ""
    echo "  ⚠ merge-target backstop: this lane is carrying another lane's unlanded work,"
    echo "    but the gate is disarmed (no MERGE-TARGET-ENFORCE)."
  fi
  echo ""
  echo "     pushing:        $1"
  echo "     also contains:  $2   — which has NOT landed on $(integration_of "$2")"
  echo ""
  echo "     A fast-forward merge creates no commit, so no commit-time hook could refuse it"
  echo "     (SCC-144). This is the net for that. The usual cause is a merge run from the wrong"
  echo "     working directory — a cd is not a lock across steps (SCC-97)."
  echo ""
  echo "     Remedy:  git log --oneline $BASE_DESC..$1     # see what actually rode along"
  echo "              git reset --hard origin/$1            # ONLY if this lane was already pushed"
  echo "     If '$2' genuinely belongs in this lane, land it on $(integration_of "$2") first."
  echo "     Bypass once: git push --no-verify"
  echo ""
  [ "$ENFORCE" = "1" ] && STATUS=1
}

# stdin: <local ref> <local sha> <remote ref> <remote sha>, one line per ref being pushed.
while read -r local_ref local_sha remote_ref remote_sha; do
  case "$remote_ref" in
    refs/heads/chore/*|refs/heads/claude/*) ;;
    *) continue ;;
  esac
  [ "$local_sha" = "$ZERO" ] && continue        # a deletion carries no commits

  # An incident lane is the incident pipeline's business (/cicd-mobile-error-team) — same
  # posture as merge-target-guard's carve-out: its one legitimate merge is the emergency
  # hotfix onto main, and a refusal here lands on a phone mid-incident, the false red this
  # file's own header prices above a miss (SCC-149 C1). Sits BELOW the deletion check on
  # purpose (SCC-154 review): a branch deletion carries no commits, and announcing "Push
  # allowed" about one was noise.
  case "$remote_ref" in
    refs/heads/claude/incident-*)
      echo "  ⓘ merge-target backstop: '${remote_ref#refs/heads/}' is an incident lane —"
      echo "    /cicd-mobile-error-team owns it; declined to judge. Push allowed."
      continue ;;
  esac

  lane=${remote_ref#refs/heads/}

  # ─── Where "already landed" is measured from, per lane class ─────────────────────────────
  # Always the REMOTE. A local branch is not a fallback: it can be arbitrarily ahead of, or
  # behind, what the rest of the system has actually seen.
  #
  # A `chore/*` lane integrates on `main`. A `claude/*` story lane integrates on its `epic/*`,
  # which does not reach `main` until the epic ships — so for a story lane every remote epic
  # counts as a landing point too. That is deliberately a slight over-allow (a sibling landed on
  # a DIFFERENT epic also reads as landed); the alternative is refusing `/cicd-park` on a
  # policy-free push, and this file's own header rules that a false red costs more than a miss.
  BASES=$(git rev-parse --verify --quiet refs/remotes/origin/main)
  BASE_DESC="origin/main"
  case "$lane" in
    claude/*)
      epics=$(git for-each-ref --format='%(objectname)' refs/remotes/origin/epic 2>/dev/null)
      if [ -n "$epics" ]; then
        BASES="$BASES
$epics"
        BASE_DESC="origin/main or the epic"
      fi
      ;;
  esac
  BASES=$(printf '%s\n' "$BASES" | sed '/^$/d')

  if [ -z "$BASES" ]; then
    echo "  ⓘ merge-target backstop: no origin/main (nor any origin/epic/*) in this clone, so"
    echo "    there is no reference point for 'already landed' — declined to judge '$lane'."
    echo "    Push allowed."
    continue
  fi

  for other in $(git for-each-ref --format='%(refname:short)' refs/heads/chore refs/heads/claude 2>/dev/null); do
    [ "$other" = "$lane" ] && continue

    # ⛔ The LOCAL name too, not only the remote one. `git push origin chore/a:refs/heads/renamed`
    # makes `lane` the REMOTE name while `other` is a LOCAL one, so the check above misses and the
    # lane is reported as contaminated BY ITSELF. Found in review, reproduced.
    #
    # ⚠ And it has to be by NAME, not by sha. Skipping any `other` whose tip equals `$local_sha`
    # reads as the tighter fix and silently deletes the primary case: a lane contaminated by a
    # FAST-FORWARD sits at exactly the foreign lane's tip, which is the whole topology this file
    # exists to catch. That regression was caught by case G going red — it is in this comment so
    # the next person tightening this line knows what it costs.
    [ "$other" = "${local_ref#refs/heads/}" ] && continue

    git merge-base --is-ancestor "$other" "$local_sha" 2>/dev/null || continue

    landed=0
    for base in $BASES; do
      if git merge-base --is-ancestor "$other" "$base" 2>/dev/null; then
        landed=1
        break
      fi
    done
    [ "$landed" = "1" ] && continue

    refuse "$lane" "$other"
  done
done

exit $STATUS
