#!/bin/sh
# pre-push-main-approval — nothing reaches `main` without a single-use approval token.
#
# The law: .agents/rules/git-policy.md § "The write gate". Two commands mint a token, plus the
# operator's direct word. This file is the machine half of that table and nothing more.
#
#   /cicd-push-e2e              epic/<KEY>-<slug>  -> main   (full gate + e2e)
#   /smh-close-task-merge-tree  chore/<KEY>-<slug> -> main   (preflight + the lane's gate)
#
# /cicd-close-story-merge-tree is the EPIC-BRANCH door and is deliberately NOT here. Its own body
# says "main is untouched" — see git-policy.md's permission table.
#
# ─── Why this is a git hook and not a Claude hook ──────────────────────────────────────────
# It ran nowhere for weeks. `.claude/settings.json` invoked the PreToolUse gate as
# `powershell -Command "python ..."`, and the Mac has NEITHER binary — it exited 127, silently,
# every time. Six merges reached main on one sign-off because of it (2026-08-09, SCC-71/SCC-77).
# A git hook is the only layer both machines, all four agent platforms, and the operator's own
# terminal share. So this file is POSIX sh with no interpreter probe and no Python: the gate must
# not depend on the class of thing that broke it.
#
# ─── What this does and does not buy ───────────────────────────────────────────────────────
# An agent can write files, so an agent can write a token. This is NOT a security boundary
# against a determined agent, and it is not sold as one. It converts a silent violation into a
# deliberate, traceable one, and it kills the real SCC-71 failure mode: a close-out command whose
# body stays in context and still reads exactly as valid on task six as it did on task one.
#
# Kill switch:      .agents/scripts/git-hooks/DISABLE     (the file every gate here honors)
# Disarm entirely:  delete .agents/scripts/git-hooks/MAIN-PUSH-ENFORCE
# Bypass once:      git push --no-verify

PROTECTED_REF="refs/heads/main"
TTL_SECONDS=1800          # 30 minutes — a sign-off is for the merge in front of you, not the session

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/MAIN-PUSH-ENFORCE ] || exit 0

# The token lives in the COMMON git dir, never the per-worktree one: every lane on this machine
# shares a single token, so a sign-off cannot be minted in one worktree and silently spent in
# another. Under .git/, so it never travels with a clone and can never land in a commit.
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0

# ⛔⛔ USED AS GIT GIVES IT — no hand-rolled `case "$GIT_COMMON" in /*)` normalisation.
# The `cd "$REPO_ROOT"` above is what makes a relative answer safe, and an absolute one needs
# nothing. Normalising by hand is correct on POSIX and WRONG on the PC: git-for-windows answers
# `C:/Users/.../.git/worktrees/<lane>`, that does not match `/*`, and the repo root gets prepended
# to an already-absolute path. The gate then looks for the token somewhere that cannot exist and
# refuses EVERY push to main. Same trap `.githooks/pre-push` documents for `--git-path`; see
# mint-push-token.sh for the measured reproduction (SCC-171).
TOKEN="$GIT_COMMON/main-push-approval"

ZERO="0000000000000000000000000000000000000000"

refuse() {
  echo ""
  echo "  ⛔ PUSH TO main REFUSED — $1"
  echo ""
  echo "     main is reached exactly three ways (.agents/rules/git-policy.md):"
  echo "       /cicd-push-e2e               an epic branch, after the full gate + /cicd-e2e green"
  echo "       /smh-close-task-merge-tree   a chore branch, after the preflight + the lane's gate"
  echo "       the operator's direct in-the-moment approval"
  echo ""
  echo "     A sign-off authorises ONE merge and never carries forward (SCC-71)."
  echo "     Bypass once: git push --no-verify"
  echo ""
  exit 1
}

# stdin: <local ref> <local sha> <remote ref> <remote sha>, one line per ref being pushed.
# Whole-token match on the remote ref, so `epic/main-fix` and `chore/main-gate` never trip this.
while read -r local_ref local_sha remote_ref remote_sha; do
  [ "$remote_ref" = "$PROTECTED_REF" ] || continue

  if [ "$local_sha" = "$ZERO" ]; then
    refuse "this would DELETE main. There is no approval path for that."
  fi

  [ -f "$TOKEN" ] || refuse "no approval token."

  # Parse the token. Unknown keys are ignored so the format can grow without breaking old hooks.
  t_branch=""; t_tip=""; t_command=""; t_key=""; t_minted=""; t_approval=""
  while IFS='=' read -r k v; do
    case "$k" in
      branch)   t_branch=$v   ;;
      tip)      t_tip=$v      ;;
      command)  t_command=$v  ;;
      key)      t_key=$v      ;;
      minted)   t_minted=$v   ;;
      approval) t_approval=$v ;;
    esac
  done < "$TOKEN"

  # Every refusal below CONSUMES the token. A sign-off that failed its own checks is spent —
  # otherwise a stale token sits there inviting a retry until one push happens to match it.
  if [ -z "$t_tip" ] || [ -z "$t_minted" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is malformed (no tip / no timestamp). It has been discarded."
  fi

  # ⛔ NO APPROVAL RECORD, NO PUSH (SCC-37). The minter refuses to write a token without the
  # operator's words, so a WELL-FORMED token lacking them was written by hand or by a pre-SCC-37
  # flow — either way it carries a sign-off nobody can point at. After the malformed check on
  # purpose: garbage is reported as garbage, not as a missing approval. Consumed like every refusal.
  if [ -z "$t_approval" ]; then
    rm -f "$TOKEN"
    refuse "the token carries no operator-approval record.
        A main merge needs the operator's explicit words for THIS merge, recorded at mint time
        (mint-push-token.sh --operator-approval '<their exact words>', or typed at a terminal).
        Ticket-status permission is never merge permission. Token discarded."
  fi

  # ⛔ VALIDATE BEFORE ARITHMETIC. `$(( ))` in POSIX sh recursively expands its operands, so a
  # token containing `minted=z[$(...)]` EXECUTES that command, and a token containing `minted=now`
  # resolves to this script's own `now` variable — age 0, forever, TTL bypassed. Both were live
  # (SCC-77 review). Digits only, checked as a string, before the value goes anywhere near `$(( ))`.
  case "$t_minted" in
    ''|*[!0-9]*)
      rm -f "$TOKEN"
      refuse "the approval token's timestamp is not a number. It has been discarded." ;;
  esac

  now=$(date +%s)
  age=$((now - t_minted))
  if [ "$age" -lt 0 ] || [ "$age" -gt "$TTL_SECONDS" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is stale — minted ${age}s ago, limit ${TTL_SECONDS}s. It has been discarded."
  fi

  # The token names the sha it was minted for. A different sha means work appeared AFTER the
  # sign-off, so no gate has seen it.
  if [ "$t_tip" != "$local_sha" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is for $t_tip but this push carries $local_sha.
        Commits appeared after the sign-off, so no gate has seen them. Token discarded."
  fi

  # ⭐⭐ THE CHECK THAT ACTUALLY ENFORCES ONE-SIGN-OFF-ONE-MERGE.
  #
  # The sha check above is NOT sufficient and the first cut of this gate wrongly claimed it was.
  # A token authorises a PUSH; what SCC-71 needs gated is a MERGE. Merge six branches into main
  # locally, then mint once, then push once — `t_tip == local_sha` holds the whole way and six
  # merges land on one approval, which is the exact failure this gate exists to stop. Reproduced
  # during the SCC-77 review: one token, six merges on the remote, the approval line naming one
  # of them.
  #
  # The invariant that actually holds: `main` advances by EXACTLY ONE merge commit sitting
  # directly on top of what the remote already has. So the pushed commit's FIRST parent must be
  # the remote's current tip. Batching breaks it (the previous merge sits in between), and so
  # does a force-push rewind (the rewound tip is not a child of the remote's).
  if [ "$remote_sha" != "$ZERO" ]; then
    parent1=$(git rev-parse --verify --quiet "${local_sha}^1") || parent1=""
    if [ "$parent1" != "$remote_sha" ]; then
      rm -f "$TOKEN"
      refuse "this push does not advance main by exactly one merge.
        remote main is at $remote_sha
        the pushed commit's first parent is ${parent1:-<none>}
        One sign-off authorises ONE merge (SCC-71). Batching several merges into a single push,
        or rewinding main and force-pushing, both land here. Token discarded."
    fi

    # And the merge must be OF the branch the token names — otherwise the token is a blank cheque
    # that any merge can spend.
    if [ -n "$t_branch" ]; then
      merged=$(git rev-parse --verify --quiet "${local_sha}^2") || merged=""
      claimed=$(git rev-parse --verify --quiet "refs/heads/$t_branch") || claimed=""
      # ⛔⛔ THIS RUNG USED TO FAIL **OPEN**, AND IT IS THE ONLY ONE ENFORCING MERGE-NESS.
      # The comparison was guarded by `[ -n "$claimed" ]`, so when the token's branch did not
      # resolve LOCALLY the whole check was skipped — silently. Measured (SCC-172, ported from
      # the AVCH-59 edge lens, reproduced twice):
      #
      #   a PLAIN NON-MERGE COMMIT on main + a token naming a branch that never existed
      #     -> tip matches, ^1 == remote tip, `claimed` empty, check skipped -> ✅ APPROVED
      #   a real merge of chore/B + a token naming epic/A (remote-only, not checked out)
      #     -> ✅ APPROVED, and the gate PRINTS THE FALSE CLAIM BACK as if it had verified it
      #
      # The comment two lines up says the point is to stop the token being "a blank cheque that
      # any merge can spend" — the `-n` guard reopened exactly that, for exactly the inputs the
      # minter never validates (it requires `--branch` to be non-empty, never to EXIST).
      #
      # Reachable without adversarial intent: a fresh clone or the other machine, where you merge
      # `origin/chore/…` and `refs/heads/chore/…` was never created; a lane pruned before the
      # mint; a typo. So an unresolvable branch is a REFUSAL, and `^2` must exist unconditionally.
      if [ -z "$merged" ]; then
        rm -f "$TOKEN"
        refuse "this push does not carry a MERGE commit.
        The token authorises landing '$t_branch', but $local_sha has no second parent.
        A sign-off is for a merge; a plain commit pushed straight onto main is not one.
        Token discarded."
      fi
      if [ -z "$claimed" ]; then
        rm -f "$TOKEN"
        refuse "the token names '$t_branch', which does not resolve in this repository.
        The gate cannot verify that the merge it is looking at is the merge that was approved,
        and an unverifiable claim is not an approval. Re-mint from the tree that holds the
        branch. Token discarded."
      fi
      if [ "$merged" != "$claimed" ]; then
        rm -f "$TOKEN"
        refuse "the token authorises landing '$t_branch' ($claimed),
        but this merge's second parent is ${merged:-<none> (not a merge commit)}.
        A sign-off is for one named branch, not for whatever happens to be on main. Token discarded."
      fi
    fi
  else
    # ⛔⛔ THE ZERO CASE USED TO FALL STRAIGHT THROUGH TO "APPROVED".
    # Every check above — the one-merge invariant AND the branch binding — lives inside the
    # `remote_sha != ZERO` arm, and there was no `else`. So a push that CREATES `main` on a
    # remote skipped the lot. Measured (SCC-172, ported from AVCH-59): a bare remote with no
    # `main`, THREE stacked --no-ff merges, one hand-written token -> "✅ main push approved",
    # `* [new branch] main -> main`, and `rev-list --count --merges` on the remote said 3. That
    # is the exact SCC-71 failure this gate exists to stop, wearing a green banner.
    #
    # ⭐ And this repo's own test fixtures were driving EVERY behaviour case through this arm —
    # `gate()` defaulted `remote_sha` to ZERO — so the suite's happy path was green BECAUSE of
    # the hole. Closing it turned five existing cases red; that is the fixture being corrected,
    # not a regression.
    #
    # There is no reference tip to compare a first parent against, so the invariant genuinely
    # cannot be evaluated here — and an approval that cannot be checked is not an approval.
    # Creating `main` on a remote is not one of the doors, so refusing strands nobody:
    # `--no-verify` is right there for the one-off case of seeding a new remote.
    rm -f "$TOKEN"
    refuse "this push would CREATE '$PROTECTED_REF' on the remote, which has no main yet.
        With no remote tip there is nothing to check 'exactly one merge above' against, so the
        one-sign-off-one-merge invariant cannot be evaluated at all — and it is the invariant
        this gate exists for. Seeding a new remote is not one of the doors below.
        Token discarded."
  fi

  # Consumed BEFORE the push. There is no post-push hook, so this is the only available order —
  # and it fails in the safe direction: a rejected push (remote moved) needs a fresh sign-off,
  # which is correct, because re-running the door command re-runs the preflight against the
  # remote that moved.
  rm -f "$TOKEN"
  echo "  ✅ main push approved — ${t_command:-<unrecorded>} · ${t_key:-<no key>} · ${t_branch:-<no branch>} @ $local_sha"
  # ⛔ printf, NOT echo — the approval line is arbitrary operator prose. `echo` re-expands
  # backslash escapes in dash/ash/BusyBox, so a quote like "land it into C:\new-thing" prints with
  # a real newline in the middle and what is read back is NOT what the operator said. The entire
  # mechanism is a claim about verbatim words (SCC-37); it has to print them verbatim as well as
  # store them.
  printf '     AUTHORIZED BY OPERATOR: "%s"\n' "$t_approval"
  echo "     Token consumed. The next merge needs its own sign-off."
done

exit 0
