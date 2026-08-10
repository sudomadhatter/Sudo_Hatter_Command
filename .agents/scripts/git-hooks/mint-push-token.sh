#!/bin/sh
# mint-push-token — write the single-use approval token that pre-push-main-approval.sh spends.
#
# Called by the two commands that are allowed to land on `main`, at their sign-off step, AFTER the
# merge commit exists and immediately BEFORE the push:
#
#   /smh-close-task-merge-tree   Step 3
#   /cicd-push-e2e               Step 4
#
# Usage:
#   sh .agents/scripts/git-hooks/mint-push-token.sh \
#        --command /smh-close-task-merge-tree --branch chore/SCC-77-main-write-gate --key SCC-77
#
# POSIX sh, no Python, by the same rule as the gate itself: nothing in this path may depend on an
# interpreter that exists on one machine and not the other. That defect is what SCC-77 is fixing.
#
# The token records the sha it was minted for. Anything committed after this runs will be REFUSED
# at the push — which is the point. Mint last, then push.

usage() {
  echo "usage: mint-push-token.sh --command <cmd> --branch <branch> [--key <JIRA-KEY>]" >&2
  exit 2
}

CMD=""; BRANCH=""; KEY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --command) CMD="$2";    shift 2 ;;
    --branch)  BRANCH="$2"; shift 2 ;;
    --key)     KEY="$2";    shift 2 ;;
    -h|--help) usage ;;
    *) echo "mint-push-token: unknown argument '$1'" >&2; usage ;;
  esac
done

[ -n "$CMD" ]    || { echo "mint-push-token: --command is required — the token records WHICH door authorised this." >&2; exit 2; }
[ -n "$BRANCH" ] || { echo "mint-push-token: --branch is required — the token records WHAT is being landed." >&2; exit 2; }

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "mint-push-token: not inside a git repository." >&2; exit 2; }
cd "$REPO_ROOT" || exit 2

# The token authorises a push of THIS commit to main, so HEAD must already be the merge commit on
# main. Minting from anywhere else records a tip the push will not carry, and the gate would refuse
# it — better to fail here, with a reason, than at the push with a mismatch.
HEAD_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ "$HEAD_BRANCH" != "main" ]; then
  echo "mint-push-token: HEAD is '$HEAD_BRANCH', not 'main'." >&2
  echo "  Mint AFTER 'git merge $BRANCH --no-ff' and BEFORE 'git push origin main'." >&2
  exit 2
fi

TIP=$(git rev-parse HEAD) || exit 2

GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 2
case "$GIT_COMMON" in
  /*) : ;;
  *)  GIT_COMMON="$REPO_ROOT/$GIT_COMMON" ;;
esac
TOKEN="$GIT_COMMON/main-push-approval"

# An unspent token already sitting there is a prior sign-off that never became a push. Overwriting
# is correct — the new one is the current intent — but it is never silent: an un-spent token means
# a merge was authorised and then abandoned, and that is worth a look.
if [ -f "$TOKEN" ]; then
  echo "  ⚠ an unspent approval token was already present — overwriting it."
  echo "    A previous sign-off never reached a push. Previous contents:"
  sed 's/^/      /' "$TOKEN"
fi

umask 077
{
  echo "branch=$BRANCH"
  echo "tip=$TIP"
  echo "command=$CMD"
  echo "key=$KEY"
  echo "minted=$(date +%s)"
} > "$TOKEN"

echo "  🔑 main-push token minted — $CMD · ${KEY:-<no key>} · $BRANCH @ $TIP"
echo "     Single use, 30-minute limit, spent by the next push to main. Do not commit after this."
