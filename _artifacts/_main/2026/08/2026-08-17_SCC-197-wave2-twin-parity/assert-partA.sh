#!/usr/bin/env bash
# SCC-209 Part A - the acceptance assertions, as one scripted pass.
# Acceptance #1 (AP enforcement gone), #3 (files kept + marked), #2 (suite green).
# Run from anywhere; resolves the lobby from this file's location.
LOBBY="$(cd "$(dirname "$0")/../../.." && pwd)"
# ⛔ `--red <ref>` reads the BLOBS at that ref, exactly as assert-scc205.sh does. The first cut
# had no arg handling at all: it always read the working tree AND silently ignored the flag, so
# `--red <any-ref>` returned 6/6 PASS - a script that reports green against every ref including
# ones where the machinery was still present. Part A's RED claim was real when it was run, and
# was NOT reproducible by the one artifact left behind to reproduce it.
REF=""
case "${1:-}" in
  "") ;;
  --red) REF="${2:?--red needs a ref}" ;;
  *) echo "unknown argument: $1 (only --red <ref> is supported)" >&2; exit 2 ;;
esac
src() { if [ -n "$REF" ]; then git -C "$LOBBY" show "$REF:$1" 2>/dev/null; else cat "$LOBBY/$1"; fi; }
# ⛔ LIST from the ref, filtered HERE - `git ls-tree` does not expand a shell glob in its
# pathspec, so the first cut listed nothing at every ref and A3/A4 reported the OPPOSITE of the
# truth (A3 "no stamps" green at a ref carrying two, A4 "3 files" red at a ref carrying three).
# A helper that silently returns empty makes every row built on it vacuous.
at() { if [ -n "$REF" ]; then git -C "$LOBBY" ls-tree -r --name-only "$REF" -- .agents/commands
       else git -C "$LOBBY" ls-files .agents/commands; fi | grep -E "$1"; }
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS | $1"; else echo "FAIL | $1  (got '$2', want '$3')"; fail=1; fi; }

n=$(src .agents/scripts/workflow_lint.py | grep -c 'check_ap_twins\|AP_RECONCILED\|ap_reconciled\|_last_commit_sha\|_last_commit_ts')
chk "A1 workflow_lint.py carries no AP-twin machinery" "$n" "0"

n=$(src .agents/scripts/tests/test_workflow_lint.py | grep -c 'check_ap_twins\|ap_reconciled')
chk "A2 test_workflow_lint.py carries no AP-twin block" "$n" "0"

n=0
for f in $(at '\.md$'); do src "$f" | grep -q 'ap_reconciled' && n=$((n+1)); done
chk "A3 no command file carries an ap_reconciled stamp" "$n" "0"

n=$(at '\-AP\.md$' | wc -l | tr -d ' ')
chk "A4 the three -AP files are still present" "$n" "3"

n=0
for f in $(at '\-AP\.md$'); do src "$f" | grep -q 'UNMAINTAINED' && n=$((n+1)); done
chk "A5 all three -AP files carry the UNMAINTAINED marker" "$n" "3"

n=$(src .agents/commands/smh-clean-code-audit.md | grep -c 'twin drift')
chk "A6 no command advertises AP-twin drift as part of its gate" "$n" "0"

exit $fail
