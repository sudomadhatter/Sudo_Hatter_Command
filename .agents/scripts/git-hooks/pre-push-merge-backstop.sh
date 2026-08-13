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
#     AND is not an ancestor of origin/main.
#
# ⛔ THE `origin/main` HALF IS WHAT MAKES IT USABLE. After a sibling lands and you absorb `main`,
# that sibling's commits are ancestors of your lane too — the single most common thing a lane does.
# Keying on containment alone would refuse it. Asking whether the foreign lane is reachable from
# origin/main separates "landed, so it is everyone's" from "still someone else's work in flight".
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
  echo "     also contains:  $2   — which is NOT reachable from origin/main"
  echo ""
  echo "     A fast-forward merge creates no commit, so no commit-time hook could refuse it"
  echo "     (SCC-144). This is the net for that. The usual cause is a merge run from the wrong"
  echo "     working directory — a cd is not a lock across steps (SCC-97)."
  echo ""
  echo "     Remedy:  git log --oneline origin/main..$1     # see what actually rode along"
  echo "              git reset --hard origin/$1            # if the lane was already pushed"
  echo "     If '$2' genuinely belongs in this lane, land it on main first."
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

  lane=${remote_ref#refs/heads/}

  # "Landed" means landed on the REMOTE. A local `main` is not a fallback for this — it can be
  # arbitrarily ahead of, or behind, what the rest of the system has actually seen.
  base=$(git rev-parse --verify --quiet refs/remotes/origin/main) || base=""
  if [ -z "$base" ]; then
    echo "  ⓘ merge-target backstop: no origin/main in this clone, so there is no reference"
    echo "    point for 'already landed' — declined to judge '$lane'. Push allowed."
    continue
  fi

  for other in $(git for-each-ref --format='%(refname:short)' refs/heads/chore refs/heads/claude 2>/dev/null); do
    [ "$other" = "$lane" ] && continue
    git merge-base --is-ancestor "$other" "$local_sha" 2>/dev/null || continue
    git merge-base --is-ancestor "$other" "$base" 2>/dev/null && continue
    refuse "$lane" "$other"
  done
done

exit $STATUS
