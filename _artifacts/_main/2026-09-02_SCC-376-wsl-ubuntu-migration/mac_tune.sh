#!/bin/bash
# SCC-376 — the two Mac fixes the install report exposed. Both reversible; both print before and after.
#   1. Conductor.app is not installed, but ~/.conductor/hook.sh remains, so the 11 guarded hooks still
#      fork a dead app's script on every event (PreToolUse/PostToolUse = every tool call). Renaming the
#      folder makes all 11 silent no-ops, with the settings file unchanged on both machines.
#   2. core.hooksPath was UNSET globally. The house arms gates per machine with
#      `git config --global core.hooksPath .githooks`; set only if it is unset at every level.
# Run on the Mac:
#   cd ~/Sudo_Hatter_Command && git fetch origin chore/SCC-376-wsl-ubuntu-plan && git show FETCH_HEAD:_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/mac_tune.sh > /tmp/mac_tune.sh && bash /tmp/mac_tune.sh
set -u
STAMP=$(date +%Y%m%d-%H%M%S)

echo "== 1. Conductor leftovers =="
if [ -d /Applications/Conductor.app ]; then
  echo "Conductor.app is installed — leaving ~/.conductor alone"
elif [ -d ~/.conductor ]; then
  mv ~/.conductor ~/.conductor.retired-scc376.$STAMP && echo "~/.conductor -> ~/.conductor.retired-scc376.$STAMP   (a rename; undo with mv)"
else
  echo "~/.conductor absent — nothing to do"
fi
echo "guard now: $([ -x ~/.conductor/hook.sh ] && echo 'hook.sh present, the 11 hooks still fire' || echo 'hook.sh absent, the 11 hooks are silent no-ops')"

echo; echo "== 2. git gates (core.hooksPath) =="
cd ~/Sudo_Hatter_Command || { echo "no ~/Sudo_Hatter_Command"; exit 1; }
BEFORE=$(git config --show-origin --get core.hooksPath 2>/dev/null)
if [ -n "$BEFORE" ]; then
  echo "already armed: $BEFORE"
else
  git config --global core.hooksPath .githooks && echo "armed: $(git config --show-origin --get core.hooksPath)"
fi
echo "lobby .githooks payload: $(ls .githooks 2>/dev/null | tr '\n' ' ')"
echo "AGY hooksPath: $(git -C Projects/AGY_AVIATIONCHAT config --show-origin --get core.hooksPath 2>/dev/null || echo 'inherits global')"
