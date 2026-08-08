#!/bin/sh
# sop-currency — require the SOP quick-reference to move when the system's USAGE moves.
#
# The why, the surface list, and the escape hatch all live in one place:
#   .agents/scripts/sop_currency.py   (and the law it enforces: .agents/rules/sop-currency.md)
# This file is only the shell seam between git and that script. Keep it dumb.
#
# Runs from the commit-msg hook, not pre-commit, for one reason: the escape hatch is a token
# in the commit message ([sop-ok]), and pre-commit cannot see the message.
#
# Kill switch: .agents/scripts/git-hooks/DISABLE   (same file the other gates honor)
# Disarm to warn-only: delete .agents/scripts/git-hooks/SOP-ENFORCE
# Bypass once: git commit --no-verify

MSG_FILE="$1"
[ -n "$MSG_FILE" ] || exit 0

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

# Only the command center carries the SOP doc. A project clone has no doc to keep current,
# so the gate has nothing to say there — same graceful degradation as the Jira gate in a
# repo with no jira.conf.
[ -f _my_resources/_quick_reference/sudo_workflows_testing.md ] || exit 0
[ -f .agents/scripts/sop_currency.py ] || exit 0

# ─── Interpreter ───────────────────────────────────────────────────────────────────────────
# This system is driven from BOTH a Mac and a Windows PC, and they disagree: the Mac has only
# `python3` (not even in a login shell), a python.org PC has only `python`, and `py` is the
# Windows launcher. That mismatch is what put a broken command in the SOP doc for weeks and is
# half the reason this gate exists — so hard-coding one name here would reproduce the very bug
# the gate was built to catch, in the enforcement layer itself. Probe, never assume.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "  ! sop-currency: no python interpreter found - check skipped, commit allowed."
  exit 0
fi

# Carve-outs match the Jira gate exactly: git writes these messages, so blocking them blocks
# the tool rather than the author.
if [ -f .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  exit 0
fi

SUBJECT=$(grep -v '^#' "$MSG_FILE" | sed -e 's/[[:space:]]*$//' -e '/^$/d')
case "$SUBJECT" in
  'Revert "'*|'Merge '*|'fixup! '*|'squash! '*) exit 0 ;;
esac

exec "$PY" .agents/scripts/sop_currency.py --repo . --message-file "$MSG_FILE"
