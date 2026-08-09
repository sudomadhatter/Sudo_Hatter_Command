#!/bin/sh
# pre-commit-encoding — block a commit that would introduce broken bytes.
#
# Installed as <hooks-dir>/pre-commit by install-encoding-hook.ps1. The hooks dir is
# `core.hooksPath` when set, else .git/hooks — NOT interchangeable: the lobby, AGY and
# Fresh all set core.hooksPath=.githooks, so an installer that assumed .git/hooks wrote a
# file git never reads and reported success. Where .githooks/ is tracked the hook TRAVELS
# through git and needs no per-machine install; where it is not, .git/ never travels and
# every clone installs once.
#
# Why a hook and not a rule: "normalise the lines you touch" has been losing this race for
# months. Mojibake is invisible in review — a Windows PowerShell 5.1 console renders
# perfectly good UTF-8 as `a-hat-euro` digraphs anyway, so neither the author nor the
# reviewer can tell corruption from a rendering artifact by eye. Only a byte-level check
# can, and only at commit time is it cheap.
#
# Scope is deliberately narrow — encoding only, staged files only. A full workflow_lint
# here would add seconds to every commit and the hook would be disabled within a week.
# The full lint belongs in CI.
#
# Kill switch: create scripts/git-hooks/DISABLE (untracked) to turn it off.
# Bypass once:  git commit --no-verify

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

# The linter lives in the vendored toolkit; a repo without it simply has no gate.
LINT=".agents/scripts/workflow_lint.py"
[ -f "$LINT" ] || exit 0

# Probe, never assume — and probe the SAME order as sop-currency.sh, or the two gates
# disagree about which machines they run on (SCC-49). The Mac has only `python3` (not even in
# a login shell), a python.org PC has only `python`, and `py` is the Windows launcher. The old
# line here was `PY=$(command -v python || command -v python3) || exit 0`: it never tried `py`,
# and on a box that has only `py` the whole substitution failed and the gate exited 0 — armed
# in name, checking nothing, silently. That is the worst shape a gate can take, and VS Code
# hides hook output, so nobody would ever have seen it.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "  ! pre-commit-encoding: no python interpreter found - check skipped, commit allowed."
  exit 0
fi

"$PY" "$LINT" --staged
exit $?
