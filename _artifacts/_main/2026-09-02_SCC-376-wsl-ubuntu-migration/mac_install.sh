#!/bin/bash
# SCC-376 — install the ONE portable ~/.claude/settings.json + ~/.claude/notify.sh on the Mac.
# Backs up both with a timestamp, installs straight from the branch (no checkout), validates the JSON
# before anything is replaced, diffs the rules against the backup, instruments what the agent cannot see
# from the PC, and fires the notifier once. Never prints a secret.
#
# Run on the Mac (one line):
#   cd ~/Sudo_Hatter_Command && git fetch origin chore/SCC-376-wsl-ubuntu-plan && git show FETCH_HEAD:_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/mac_install.sh > /tmp/mac_install.sh && bash /tmp/mac_install.sh
set -u
LANE=_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration
cd ~/Sudo_Hatter_Command || { echo "no ~/Sudo_Hatter_Command"; exit 1; }
git fetch origin chore/SCC-376-wsl-ubuntu-plan --quiet || { echo "fetch failed"; exit 1; }
STAMP=$(date +%Y%m%d-%H%M%S)
BAK="$HOME/.claude/settings.json.pre-scc376.$STAMP"

echo "== backup =="
cp ~/.claude/settings.json "$BAK" && echo "settings.json -> $BAK"
[ -f ~/.claude/notify.sh ] && cp ~/.claude/notify.sh ~/.claude/notify.sh.pre-scc376.$STAMP && echo "notify.sh     -> ~/.claude/notify.sh.pre-scc376.$STAMP"

echo; echo "== install =="
if git show FETCH_HEAD:$LANE/claude-user-settings.portable.json > ~/.claude/settings.json.new \
   && python3 -c 'import json,sys; json.load(open(sys.argv[1]))' ~/.claude/settings.json.new; then
  mv ~/.claude/settings.json.new ~/.claude/settings.json && echo "settings.json installed (valid JSON)"
else
  rm -f ~/.claude/settings.json.new; echo "INSTALL FAILED — settings.json unchanged, backup untouched"; exit 1
fi
git show FETCH_HEAD:$LANE/notify.sh > ~/.claude/notify.sh && chmod +x ~/.claude/notify.sh && echo "notify.sh installed"
echo "sha256 settings.json: $(shasum -a 256 ~/.claude/settings.json | cut -c1-16)   (must equal the Linux sha in the plan)"
python3 - <<'EOF'
import json, os
d = json.load(open(os.path.expanduser("~/.claude/settings.json")))
sb = d["sandbox"]
print("allow rules:", len(d["permissions"]["allow"]), "| defaultMode:", d["permissions"]["defaultMode"],
      "| sandbox:", sb["enabled"], "| hatch:", "open (Mac behaviour)" if "allowUnsandboxedCommands" not in sb else sb["allowUnsandboxedCommands"])
print("allowWrite:", sb["filesystem"]["allowWrite"])
print("hooks:", {k: len(v) for k, v in d["hooks"].items()})
EOF

echo; echo "== rules: what changed on THIS Mac vs the backup (a '-' line = a rule the Mac had that the portable file lacks; tell the agent) =="
python3 - "$BAK" <<'EOF'
import json, os, sys
old = json.load(open(sys.argv[1])); new = json.load(open(os.path.expanduser("~/.claude/settings.json")))
a, b = set(old["permissions"]["allow"]), set(new["permissions"]["allow"])
for r in sorted(a - b): print("  -", r)
for r in sorted(b - a): print("  +", r)
print("  (", len(a - b), "removed,", len(b - a), "added )")
EOF

echo; echo "== instrument — paste this block back =="
echo "conductor: hook.sh $([ -x ~/.conductor/hook.sh ] && echo present || echo absent) | Conductor.app $([ -d /Applications/Conductor.app ] && echo installed || echo not-installed)"
echo "GITHUB_TOKEN: $([ -n "${GITHUB_TOKEN:-}" ] && echo SET || echo unset) in this shell | exported from: $(grep -l GITHUB_TOKEN ~/.zshenv ~/.zprofile ~/.zshrc ~/.profile ~/.bash_profile 2>/dev/null | tr '\n' ' ')"
echo "core.hooksPath: $(git config --show-origin --get core.hooksPath 2>/dev/null || echo UNSET) (effective, from the lobby) | global: $(git config --global core.hooksPath 2>/dev/null || echo unset)"
echo "node: $(node -v 2>/dev/null || echo none) | python3: $(python3 -V 2>/dev/null || echo none) | grep: $(grep --version 2>/dev/null | head -1)"
echo "banner app: $([ -x /opt/homebrew/bin/terminal-notifier ] && echo /opt/homebrew/bin/terminal-notifier || command -v terminal-notifier || echo osascript-fallback)"

echo; echo "== notifier self-test (banner + phone, a real Stop-shaped payload) =="
printf '%s' '{"hook_event_name":"Stop","cwd":"'"$HOME"'/Sudo_Hatter_Command","last_assistant_message":"**SCC-376** Mac install complete: the portable notifier works"}' \
  | ~/.claude/notify.sh 'Claude Code' 'Turn completed'; echo "notify.sh exit=$?   (a banner and a phone push should have arrived)"
