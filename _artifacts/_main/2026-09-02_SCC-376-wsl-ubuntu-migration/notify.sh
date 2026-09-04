#!/bin/sh
# ~/.claude/notify.sh — ONE notifier for both machines (SCC-376).
#   Folds in the Mac's own notifier (pasted 2026-09-02) so the swap loses nothing it did: a context
#   line (chat title if the payload ever carries one, else the project folder) + the first line of
#   Claude's reply with markdown stripped and a 140-char cap, the `Tags: robot` push, a debug copy of
#   the last payload, terminal-notifier -> osascript for the banner. Adds notify-send for Linux.
#   Hooks run OUTSIDE the Bash sandbox (vendor doc), so the network is reachable without an allowlist row.
#   stdin: Notification -> {message, cwd, notification_type}; Stop -> {last_assistant_message, cwd}.
#   Every path exits 0 — a notifier must never fail the hook.
#   settings: "command": "~/.claude/notify.sh 'Claude Code' 'Turn completed'"
TITLE="${1:-Claude Code}"
MESSAGE="${2:-Task finished or input needed!}"
NTFY_TOPIC="${NTFY_TOPIC:-mac-sudo-command}"   # public by name; override in ~/.zshenv (Mac) / ~/.profile (Linux)

# Read the payload in the foreground (only when stdin is a pipe — never hang on a terminal) ...
INPUT=""
if [ ! -t 0 ]; then
  INPUT="$(cat 2>/dev/null)"
fi

# ... then do ALL the work detached, immune to TERM. Measured 2026-09-02 on Linux: about 15 ms after
# the hook's shell exits, Claude sends SIGTERM to the hook's process group, and anything still running
# in it dies (a foreground push, a backgrounded curl, a detached subshell mid-python). Ignoring TERM in
# the detached body is inherited by python3 and curl (SIG_IGN survives exec), so the push completes;
# `setsid` would also work but does not exist on macOS. The hook itself returns instantly, so this
# costs the turn nothing whether the hook is async or not. The body runs for at most ~6 s (curl -m 5).
(
  trap '' TERM HUP INT
  if [ -n "$INPUT" ]; then
    printf '%s' "$INPUT" > "$HOME/.claude/last-hook-input.json" 2>/dev/null
    ENRICH="$(printf '%s' "$INPUT" | python3 -c '
import json, sys, os
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
title = d.get("title") or d.get("session_title") or d.get("topic") or ""
cwd = d.get("cwd") or ""
print(title or (os.path.basename(cwd) if cwd else ""))
msg = d.get("last_assistant_message") or d.get("message") or ""
snip = next((l.strip() for l in msg.splitlines() if l.strip()), "")
snip = snip.replace("**", "").replace("`", "").replace("\"", "").strip()
if len(snip) > 140:
    snip = snip[:137] + "..."
print(snip)
' 2>/dev/null)"
    CTX="$(printf '%s\n' "$ENRICH" | sed -n 1p)"
    SNIP="$(printf '%s\n' "$ENRICH" | sed -n 2p)"
    [ -n "$SNIP" ] && MESSAGE="$SNIP"
    [ -n "$CTX" ] && MESSAGE="$CTX — $MESSAGE"
  fi

  # Desktop banner — whichever exists on this machine (never more than one)
  if [ -x /opt/homebrew/bin/terminal-notifier ]; then
    /opt/homebrew/bin/terminal-notifier -title "$TITLE" -message "$MESSAGE"
  elif command -v terminal-notifier >/dev/null 2>&1; then
    terminal-notifier -title "$TITLE" -message "$MESSAGE"
  elif command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\""
  elif command -v notify-send >/dev/null 2>&1; then
    notify-send "$TITLE" "$MESSAGE"
  fi

  # Phone — the cross-platform channel
  if command -v curl >/dev/null 2>&1; then
    curl -s -m 5 -H "Title: $TITLE" -H "Tags: robot" -d "$MESSAGE" "https://ntfy.sh/$NTFY_TOPIC"
  fi
) >/dev/null 2>&1 </dev/null &
exit 0
