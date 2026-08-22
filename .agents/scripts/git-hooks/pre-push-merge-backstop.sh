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
  # ⛔⛔ NEVER `--hard` HERE, AND THAT IS A MEASURED RULE, NOT A PREFERENCE (SCC-180).
  # This banner used to print `git reset --hard origin/$1`. On 2026-08-15 an agent read it as the
  # instruction it looks like, ran it in the lobby's MAIN CHECKOUT, and destroyed three other
  # sessions' uncommitted work. The main checkout hosts `_artifacts/_memory/`, which every session
  # on this machine writes, so it is never a clean tree — and there is no git hook for `reset`, so
  # nothing can refuse it afterwards. A refusal banner is read at the worst moment by whoever is
  # least sure; whatever it prints WILL be typed. So it prints the one that refuses instead.
  echo "     Remedy:  git log --oneline $BASE_DESC..$1     # see what actually rode along"
  echo "              git reset --keep origin/$1            # ONLY if this lane was already pushed"
  echo "                                                    # --keep REFUSES rather than discarding"
  echo "              git reset --soft HEAD~1               # to undo a local commit, tree untouched"
  echo "     ⛔ Never \`--hard\` in a shared checkout — it carries other sessions' uncommitted work."
  echo "     If '$2' genuinely belongs in this lane, land it on $(integration_of "$2") first."
  echo "     Bypass once: git push --no-verify"
  echo ""
  [ "$ENFORCE" = "1" ] && STATUS=1
}

# stdin: <local ref> <local sha> <remote ref> <remote sha>, one line per ref being pushed.
while read -r local_ref local_sha remote_ref remote_sha; do
  # ⓘ A PUSHED `epic/*` IS DELIBERATELY NOT JUDGED — a ruled omission, not an oversight
  # (SCC-163; operator, 2026-08-15: "A3. no we dont need it."). Two pairings therefore still
  # escape by fast-forward, and they are named here so the gap is recorded rather than merely
  # unnoticed:
  #
  #     epic:chore   refuse   — a chore lane ff'd into an epic branch
  #     epic:epic    refuse   — one epic ff'd into another
  #
  # Widening this line is NOT a one-word change, which is why it was declined. A pushed epic
  # needs its own THIRD candidate set: `refs/heads/claude` must be EXCLUDED for it, because
  # `epic:story` is `allow` and stories landing on the epic is what an epic IS — enumerating
  # them would refuse every ordinary epic push, on the `/cicd-push-e2e` shipping path. This
  # file's header prices that false red above a miss. Case EP4 pins the current behaviour, so
  # whoever widens it later gets a red that explains itself instead of a silent regression.
  case "$remote_ref" in
    refs/heads/chore/*|refs/heads/claude/*) ;;
    *) continue ;;
  esac
  [ "$local_sha" = "$ZERO" ] && continue        # a deletion carries no commits

  # An incident lane is the incident pipeline's business (/cicd-mobile-error-team) — same
  # posture as merge-target-guard's carve-out. Sits BELOW the deletion check on purpose
  # (SCC-154 review): a branch deletion carries no commits, and announcing "Push allowed"
  # about one was noise.
  #
  # ⛔ SCC-159 (finding 28) NARROWED this from a skip to a NOTE. Keyed on the pushed ref
  # alone, it waved an incident ref through carrying ANYTHING — while merge-target-guard
  # refuses that same content at commit time as story:incident / chore:incident. A
  # fast-forward creates no commit, so the ff variant of an already-refused merge escaped
  # BOTH gates, and it escaped them hardest during an incident, when mistakes are likeliest.
  # What the pipeline owns is the LANE, not other lanes' unlanded work riding inside it: the
  # containment loop below now runs for incident refs too, and `integration_of` keeps the
  # remedy pointed at main via the pipeline rather than the SCC-148 epic misroute.
  case "$remote_ref" in
    refs/heads/claude/incident-*)
      echo "  ⓘ merge-target backstop: '${remote_ref#refs/heads/}' is an incident lane —"
      echo "    /cicd-mobile-error-team owns it. Checking only that it carries no OTHER"
      echo "    lane's unlanded work; its own commits are its business." ;;
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
    # ⛔⛔ THE INCIDENT ARM SITS ABOVE `claude/*`, AND FOR THE SECOND TIME IN THIS FILE.
    # SCC-154 gave `integration_of()` this exact ordered arm because `case` is first-match and
    # the story glob swallows incident names. SCC-159 then removed the `continue` above — so
    # incident refs reached THIS switch for the first time, matched `claude/*`, and had every
    # `origin/epic/*` added as a landing point. An epic-landed story lane riding inside a
    # hotfix therefore scored "landed" and shipped to production through the one lane that
    # goes straight to main. Measured: identical content, `chore/*` REFUSED and
    # `claude/incident-*` ALLOWED (case G6e).
    #
    # The widening's own charter is why it cannot apply here: it exists to spare `/cicd-park`
    # on a STORY lane, which integrates on its epic. An incident lane integrates on MAIN —
    # `integration_of` says so three lines up — so for this class `origin/main` is the whole
    # reference set, exactly as it is for `chore/*`.
    claude/incident-*) ;;
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

  # ─── Which foreign lanes are even CANDIDATES, per lane class (SCC-163) ───────────────────
  # `refs/heads/epic` was absent here, so a `chore/*` lane that FAST-FORWARDED an epic carried
  # that epic's unlanded commits to the remote with nothing looking. `merge-target-guard.sh`
  # already rules `chore:epic -> refuse`; a ff writes no commit, so the guard never fired and
  # this loop was not looking. Reproduced end to end against a real remote before the fix.
  #
  # ⛔ IT IS KEYED ON THE LANE CLASS, AND THAT IS THE WHOLE FIX — a blanket `refs/heads/epic`
  # in the line below is WRONG and false-reds three ALLOW arms of the same judge table:
  #   story:epic    allow  — a story lane absorbing its own epic IS `/cicd-park`, run daily
  #   incident:epic allow  — "absorbing main (or an epic) is the everyday mid-incident move"
  #   epic:story    allow  — a pushed epic/* is declined at the ref filter above
  # Only `chore/*` integrates on `main` with an epic as genuinely foreign work. This mirrors
  # the BASES switch directly above: same question, same per-class answer, and for the same
  # reason the incident arm had to be added there twice (SCC-154, SCC-159).
  SCOPES="refs/heads/chore refs/heads/claude"
  case "$lane" in
    chore/*) SCOPES="$SCOPES refs/heads/epic" ;;
  esac

  for other in $(git for-each-ref --format='%(refname:short)' $SCOPES 2>/dev/null); do
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
