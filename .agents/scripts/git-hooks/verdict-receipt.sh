#!/bin/sh
# verdict-receipt — a staged `Verdict: PASS|CONCERNS` stamp needs a real suite receipt.
#
# The why, the rule, and the escape hatch live in one place:
#   .agents/scripts/verdict_receipt.py   (SCC-363; seat law: .agents/rules/zoo-team.md)
# This file is only the shell seam between git and that script. Keep it dumb.
#
# Runs from the commit-msg hook, not pre-commit, for the same reason sop-currency does:
# the escape hatch is a token in the commit message ([verdict-ok]), and pre-commit
# cannot see the message.
#
# Kill switch: .agents/scripts/git-hooks/DISABLE   (same file the other gates honor)
# Disarm to warn-only: delete .agents/scripts/git-hooks/VERDICT-ENFORCE
# Bypass once: git commit --no-verify

MSG_FILE="$1"
[ -n "$MSG_FILE" ] || exit 0

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/verdict_receipt.py ] || exit 0

# Probe, never assume (two-machines law): the Mac has only `python3`, a python.org PC
# has only `python`, `py` is the Windows launcher.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "  ! verdict-receipt: no python interpreter found - check skipped, commit allowed."
  exit 0
fi

# Carve-outs match the sop-currency gate exactly: git writes these messages, so blocking
# them blocks the tool rather than the author. `$(git rev-parse --git-dir)`, never the
# literal `.git/` - in a WORKTREE `.git` is a file (SCC-144).
GITDIR=$(git rev-parse --git-dir 2>/dev/null) || GITDIR=.git
if [ -f "$GITDIR/MERGE_HEAD" ] || [ -d "$GITDIR/rebase-merge" ] || [ -d "$GITDIR/rebase-apply" ]; then
  exit 0
fi

# ⛔ 'Merge '* IS DELIBERATELY ABSENT from this list (review finding, reproduced). Every real
# merge sets MERGE_HEAD and is already carved out by the STATE check above, so a subject-text
# case adds no merge coverage at all - it only adds an escape anyone can type:
# `git commit -m "Merge the review sections"` on a staged, receiptless PASS committed clean
# with no hook output. The state check is the merge carve-out; this list is only for the
# messages git writes on rebase/fixup paths that leave no state directory.
SUBJECT=$(grep -v '^#' "$MSG_FILE" | sed -e 's/[[:space:]]*$//' -e '/^$/d')
case "$SUBJECT" in
  'Revert "'*|'fixup! '*|'squash! '*) exit 0 ;;
esac

exec "$PY" .agents/scripts/verdict_receipt.py --repo . --message-file "$MSG_FILE"
