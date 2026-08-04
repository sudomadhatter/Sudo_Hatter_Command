#!/bin/sh
# pre-commit-encoding — block a commit that would introduce broken bytes.
#
# Installed as .git/hooks/pre-commit by install-encoding-hook.ps1 (machine-local: .git/
# never travels through GitHub, so every machine installs it once).
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

PY=$(command -v python || command -v python3) || exit 0

"$PY" "$LINT" --staged
exit $?
