#!/bin/bash
# SCC-376 — under STRICT sandbox, run the real house workloads through claude's Bash tool and
# collect every refusal. The fence is widened from THIS list, never from a guess.
cd ~/Sudo_Hatter_Command || exit 1
run() {  # $1 label  $2 command
  echo; echo "=== $1 ==="
  timeout 240 claude -p "Run exactly this shell command and print its complete output verbatim, including any error text and the exit code. Do not try any other approach: $2" \
    --output-format text < /dev/null 2>&1 | grep -vE '^(Ignoring|Permission allow rule|Warning: no stdin)' | tail -6
}
run "git config --global (hooksPath arming writes ~/.gitconfig)" \
    "git config --global scc376.probe yes && git config --global --unset scc376.probe && echo GITCONFIG-OK"
run "npm ci in AGY frontend (cache in ~/.npm)" \
    "cd Projects/AGY_AVIATIONCHAT/frontend && npm ci --silent 2>&1 | tail -3; echo exit=\$?"
run "pip install into the AGY venv (cache in ~/.cache/pip)" \
    "Projects/AGY_AVIATIONCHAT/backend/.venv/bin/pip install --quiet --upgrade pip 2>&1 | tail -3; echo exit=\$?"
run "the enforcement suite" \
    "python3 .agents/scripts/tests/test_settings_allowlist.py 2>&1 | tail -1; echo exit=\$?"
run "git worktree add under .claude/worktrees" \
    "git worktree add .claude/worktrees/scc376-probe -b scc376-probe 2>&1 | tail -2; git worktree remove --force .claude/worktrees/scc376-probe; git branch -D scc376-probe; echo WORKTREE-OK"
run "acli (excludedCommands)" "acli jira workitem view SCC-376 --fields status 2>&1 | head -3"
run "gh (excludedCommands)"   "gh pr list --limit 1 2>&1 | head -2; echo exit=\$?"
run "git fetch over HTTPS (network allowlist + gh credential helper)" \
    "git fetch origin 2>&1 | tail -2; echo exit=\$?"
run "python script writing the scratchpad-style temp dir" \
    "d=\$(mktemp -d) && echo ok > \$d/x && echo TMP-OK \$d"
