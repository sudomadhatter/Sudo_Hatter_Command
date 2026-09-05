---
name: claude-notifications-hook-schema-and-ntfy
description: "Claude Code notifications: the `Notification`/`Stop` hook value MUST be the array form — a plain string is silently ignored, no error, the hook just never fires. The phone push rides ntfy topic `mac-sudo-command`, which is a LEGACY NAME and still the live topic in zoo_notify.py. `~/.claude/notify.sh` is the local script. Re-checked on this PC 2026-09-04."
metadata:
  node_type: memory
  type: reference
  probe: "grep -q 'mac-sudo-command' .agents/scripts/zoo_notify.py"
  modified: 2026-09-04
---

> ⛔ Renamed from `claude-notifications-mac-and-phone` on 2026-09-04 (SCC-401). The Mac half of the
> old file described `terminal-notifier`, `osascript` and macOS Focus modes on a machine that no
> longer exists ([[one-pc-windows-and-wsl]]) — `terminal-notifier` is not installed here and cannot
> be. What survives is the part that was never about macOS at all.

## The one that costs a cycle every time: the hook schema

**A plain-string hook value is silently ignored.** `"Stop": "cmd"` is accepted, raises no error,
and simply never fires. Claude Code requires the array form:

```json
"Stop": [{"hooks": [{"type": "command", "command": "~/.claude/notify.sh"}]}]
```

This is the [[suite-red-file-may-have-run-nothing]] family — a configuration that *parses* is not a
configuration that *runs*, and nothing tells you the difference. Verify by triggering it, never by
reading the JSON back.

## What is live on this PC

- `~/.claude/notify.sh` — the local notification script (present, executable; not tracked in the
  repo, so it does not travel to a fresh clone — set it up per checkout).
- **ntfy topic `mac-sudo-command`** — still the `DEFAULT_TOPIC` in both `.agents/scripts/zoo_notify.py`
  and `zoo_notify_install.py`. ⚠️ The name is **legacy** and no longer describes anything: there is
  no Mac. It is kept because renaming a topic silently drops every subscribed device until each one
  is re-subscribed by hand. **Do not "fix" the name casually** — it is an identifier, not a
  description.
- The topic is **public by name**. If it ever carries more than generic "turn completed" text,
  switch to a long random topic via `NTFY_TOPIC`, exported from `~/.profile`
  ([[interactive-startup-files-are-invisible-to-automation]]) so automation actually sees it.

## Retired with the Mac

macOS Focus modes swallowing banners while the script still exits 0 and the phone push still
arrives; `terminal-notifier` and the `osascript` fallback; the launchd agent. Kept here as the
reason the *phone* leg exists at all — the desktop leg was always the unreliable one.
