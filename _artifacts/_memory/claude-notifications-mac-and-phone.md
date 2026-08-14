---
name: claude-notifications-mac-and-phone
description: "Claude Code notifications on the Mac — hook schema must be the array form, and the Work Focus must allow terminal-notifier; phone rides ntfy topic mac-sudo-command."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0912f56a-53dc-450f-9edb-bd0acf239834
  modified: 2026-08-14T10:44:12.321Z
---

Notification pipeline (Mac, set up 2026-08-14): `~/.claude/settings.json` `Notification` + `Stop` hooks → `~/.claude/notify.sh` → terminal-notifier banner (osascript only as fallback — both at once = duplicate banners; no chime, operator's choice) + ntfy.sh push to topic `mac-sudo-command` (phone must be subscribed in the ntfy app). The banner text = project folder + first line of `last_assistant_message` from the hook payload; there is NO chat-title field anywhere in the payload or on disk (UI-layer only, verified 2026-08-14) — the payload keeps landing in `~/.claude/last-hook-input.json` for future field checks.

Two silent failure modes already hit once — check these FIRST:
- **A plain-string hook value is silently ignored.** Gemini wrote `"Stop": "cmd"`; Claude Code requires `[{"hooks": [{"type": "command", "command": ...}]}]`. No error is raised — the hook just never fires, on every surface.
- **A Focus mode (e.g. Work) swallows banners** from apps not on its allow-list while the script still exits 0 and the phone push still arrives. terminal-notifier + Script Editor must be in System Settings → Focus → Work → Allowed Notifications. Suppressed banners still land in Notification Center history — that's how to tell delivery-works-but-display-suppressed from not-firing.

ntfy topic is public by name — if it ever carries more than generic "turn completed" text, switch to a long random topic via `NTFY_TOPIC` in `~/.zshenv` ([[zshrc-is-invisible-to-automation]]) on both machines ([[two-machines-mac-and-pc]] — PC side has no notify.sh yet).
