#!/bin/sh
# pre-push-main-approval — nothing reaches `main` without a single-use approval token.
#
# The law: .agents/rules/git-policy.md § "The write gate". Two commands mint a token, plus the
# operator's direct word. This file is the machine half of that table and nothing more.
#
#   /cicd-push-e2e              epic/<KEY>-<slug>  -> main   (full gate + e2e)
#   /smh-close-task-merge-tree  chore/<KEY>-<slug> -> main   (preflight + the lane's gate)
#
# /cicd-update-sprint-memory is the EPIC-BRANCH key and is deliberately NOT here. Its own body
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
case "$GIT_COMMON" in
  /*) : ;;                                  # already absolute
  *)  GIT_COMMON="$REPO_ROOT/$GIT_COMMON" ;;  # relative to the toplevel — resolve it
esac
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
  t_branch=""; t_tip=""; t_command=""; t_key=""; t_minted=""
  while IFS='=' read -r k v; do
    case "$k" in
      branch)  t_branch=$v  ;;
      tip)     t_tip=$v     ;;
      command) t_command=$v ;;
      key)     t_key=$v     ;;
      minted)  t_minted=$v  ;;
    esac
  done < "$TOKEN"

  # Every refusal below CONSUMES the token. A sign-off that failed its own checks is spent —
  # otherwise a stale token sits there inviting a retry until one push happens to match it.
  if [ -z "$t_tip" ] || [ -z "$t_minted" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is malformed (no tip / no timestamp). It has been discarded."
  fi

  now=$(date +%s)
  age=$((now - t_minted))
  if [ "$age" -lt 0 ] || [ "$age" -gt "$TTL_SECONDS" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is stale — minted ${age}s ago, limit ${TTL_SECONDS}s. It has been discarded."
  fi

  # ⭐ The check that matters. The token names the sha it was minted for. If what is actually
  # being pushed is a different commit, work appeared AFTER the sign-off and no gate has ever
  # seen it — which is precisely how six merges rode one approval.
  if [ "$t_tip" != "$local_sha" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is for $t_tip but this push carries $local_sha.
        Commits appeared after the sign-off, so no gate has seen them. Token discarded."
  fi

  # Consumed BEFORE the push. There is no post-push hook, so this is the only available order —
  # and it fails in the safe direction: a rejected push (remote moved) needs a fresh sign-off,
  # which is correct, because re-running the door command re-runs the preflight against the
  # remote that moved.
  rm -f "$TOKEN"
  echo "  ✅ main push approved — ${t_command:-<unrecorded>} · ${t_key:-<no key>} · ${t_branch:-<no branch>} @ $local_sha"
  echo "     Token consumed. The next merge needs its own sign-off."
done

exit 0
