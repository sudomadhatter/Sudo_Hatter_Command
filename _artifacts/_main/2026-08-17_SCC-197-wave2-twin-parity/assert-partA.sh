#!/usr/bin/env bash
# SCC-209 Part A - the acceptance assertions, as one scripted pass.
# Acceptance #1 (AP enforcement gone), #3 (files kept + marked), #2 (suite green).
# Run from anywhere; resolves the lobby from this file's location.
LOBBY="$(cd "$(dirname "$0")/../../.." && pwd)"
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS | $1"; else echo "FAIL | $1  (got '$2', want '$3')"; fail=1; fi; }

n=$(grep -c 'check_ap_twins\|AP_RECONCILED\|ap_reconciled\|_last_commit_sha\|_last_commit_ts' "$LOBBY/.agents/scripts/workflow_lint.py")
chk "A1 workflow_lint.py carries no AP-twin machinery" "$n" "0"

n=$(grep -c 'check_ap_twins\|ap_reconciled' "$LOBBY/.agents/scripts/tests/test_workflow_lint.py")
chk "A2 test_workflow_lint.py carries no AP-twin block" "$n" "0"

n=$(grep -rl 'ap_reconciled' "$LOBBY/.agents/commands/" 2>/dev/null | wc -l | tr -d ' ')
chk "A3 no command file carries an ap_reconciled stamp" "$n" "0"

n=$(ls "$LOBBY"/.agents/commands/*-AP.md 2>/dev/null | wc -l | tr -d ' ')
chk "A4 the three -AP files are still present" "$n" "3"

n=$(grep -l 'UNMAINTAINED' "$LOBBY"/.agents/commands/*-AP.md 2>/dev/null | wc -l | tr -d ' ')
chk "A5 all three -AP files carry the UNMAINTAINED marker" "$n" "3"

n=$(grep -c 'twin drift' "$LOBBY/.agents/commands/smh-clean-code-audit.md")
chk "A6 no command advertises AP-twin drift as part of its gate" "$n" "0"

exit $fail
