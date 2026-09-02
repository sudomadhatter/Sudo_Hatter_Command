#!/bin/sh
# ~/.claude/notify.sh — ONE notifier for both machines (SCC-376).
#   Hooks run OUTSIDE the Bash sandbox (vendor doc), so this can reach the network freely.
#   Payload on stdin: Notification -> {message, cwd, notification_type}; Stop -> {last_assistant_message, cwd}.
#   Channels: ntfy push ALWAYS (phone; works from Mac and Linux) + a desktop banner where one exists
#   (terminal-notifier on macOS, notify-send on Linux). Never fails the hook: every path exits 0.
#   Usage in settings: "command": "~/.claude/notify.sh 'Claude Code' 'Turn completed'"
TITLE="${1:-Claude Code}"
FALLBACK="${2:-Update}"
TOPIC="${NTFY_TOPIC:-mac-sudo-command}"     # public by name; override via NTFY_TOPIC in ~/.profile / ~/.zshenv

PAYLOAD=$(cat 2>/dev/null)
# banner text = project folder + first line of the message (the shape the Mac already used)
BODY=$(printf '%s' "$PAYLOAD" | python3 -c '
import json,sys,os
try:
    d=json.load(sys.stdin)
except Exception:
    print(""); sys.exit(0)
msg=d.get("last_assistant_message") or d.get("message") or ""
first=next((l.strip() for l in msg.splitlines() if l.strip()), "")
proj=os.path.basename(d.get("cwd","") or "")
print((proj+": " if proj else "")+first[:180])
' 2>/dev/null)
[ -n "$BODY" ] || BODY="$FALLBACK"

# phone — the cross-platform channel
if command -v curl >/dev/null 2>&1; then
  curl -s -m 5 -H "Title: $TITLE" -d "$BODY" "https://ntfy.sh/$TOPIC" >/dev/null 2>&1 &
fi

# desktop banner, whichever exists (both absent is fine — the phone still got it)
if command -v terminal-notifier >/dev/null 2>&1; then
  terminal-notifier -title "$TITLE" -message "$BODY" >/dev/null 2>&1 &
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "$TITLE" "$BODY" >/dev/null 2>&1 &
fi
exit 0
