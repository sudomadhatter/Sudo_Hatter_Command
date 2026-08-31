#!/usr/bin/env python3
"""Zoo Code notifications — desktop banner + ntfy phone push, parity with Claude (SCC-355).

Claude Code pings the operator through `~/.claude/settings.json` Notification + Stop hooks into
`~/.claude/notify.sh`. Zoo Code has no equivalent and cannot get one the same way: v3.80.1's
manifest contributes 19 settings keys and 20 commands, and NOT ONE is a notification, a sound, or
an event hook. So there is no hook to hang this on, and the trigger is instead the thread store Zoo
already writes on every turn.

⭐ The signal that matters is `autoApprovalDecision`. Zoo records its own verdict per ask:
"approve" (auto-approved, the operator was never needed), "deny", or None (the matcher had no
opinion, so it ASKED). Across the two real threads measured at plan time that split was 34 / 5 / 14
— so a notifier that fired on every ask would page the operator 34 times for the 14 that wanted
him, and he would mute it inside a day.

Stdlib only; runs as `python3` (Mac) / `python` (PC). CLI:
    zoo_notify.py --once            classify the newest thread and notify if it earns one
    zoo_notify.py --watch [--interval N]   poll the store and notify on transitions
    zoo_notify.py --dry-run ...     compose and print; open no network, raise no banner
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DEFAULT_TOPIC = "mac-sudo-command"
EXTENSION_DIR = "zoocodeorganization.zoo-code"

# Asks that represent a decision the operator has to make. `completion_result` is deliberately
# absent — it is a turn ending, not a question, and it is handled before this set is consulted.
DECISION_ASKS = {"command", "tool", "followup", "resume_completed_task"}


def store_root(platform: str | None = None, home: Path | None = None,
               appdata: Path | None = None, custom: Path | None = None) -> Path:
    """Where Zoo keeps its per-task threads. BOTH machines, and the configurable override.

    `zoo-code.customStoragePath` is a real Zoo setting — a watcher that ignores it happily polls an
    empty directory forever and reports success. [[two-machines-mac-and-pc]]
    """
    if custom is not None:
        return Path(custom) / "tasks"
    platform = platform if platform is not None else sys.platform
    home = Path(home) if home is not None else Path.home()
    if platform == "win32":
        base = Path(appdata) if appdata is not None else Path(
            os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    else:
        base = home / "Library" / "Application Support"
    return base / "Code" / "User" / "globalStorage" / EXTENSION_DIR / "tasks"


def classify(messages: list[dict]) -> str | None:
    """Does this thread's tail deserve to interrupt the operator? 'ask' | 'turn_end' | None."""
    if not messages:
        return None
    last = messages[-1]
    if last.get("partial") is True:          # a stream in flight is not a decision point
        return None
    kind = last.get("type")
    if kind == "ask":
        if last.get("ask") == "completion_result":
            return "turn_end"
        if last.get("isAnswered") is True:   # never literal False in the store — absent means open
            return None
        if last.get("autoApprovalDecision") is not None:
            return None                      # Zoo already decided; the operator was not needed
        if last.get("ask") in DECISION_ASKS:
            return "ask"
        return None
    if kind == "say" and last.get("say") == "completion_result":
        return "turn_end"
    return None


def ntfy_url() -> str:
    """The topic is public by name; NTFY_TOPIC in ~/.zshenv overrides it on both machines."""
    return "https://ntfy.sh/" + (os.environ.get("NTFY_TOPIC") or DEFAULT_TOPIC)


def compose(event: str, project: str, text: str) -> dict:
    """Pure. Composes what the operator sees. Opens nothing."""
    first = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    if len(first) > 120:
        first = first[:117] + "..."
    if event == "ask":
        title = "Zoo Code - needs you"
        body = f"{project}: waiting on approval" + (f" - {first}" if first else "")
    else:
        title = "Zoo Code - turn complete"
        body = f"{project}: finished" + (f" - {first}" if first else "")
    return {"title": title, "message": body, "ntfy_url": ntfy_url(), "event": event}


def banner_cmd(payload: dict, platform: str | None = None) -> list[str] | None:
    """The desktop banner argv for this machine, or None where we have no banner channel.

    Mac uses terminal-notifier, the same binary Claude's notify.sh uses — and the same Focus-mode
    caveat applies: a Work Focus swallows the banner while everything still exits 0, so a silent
    Mac is not proof the notifier failed. [[claude-notifications-mac-and-phone]]
    """
    platform = platform if platform is not None else sys.platform
    if platform == "darwin":
        return ["terminal-notifier", "-title", payload["title"], "-message", payload["message"]]
    if platform == "win32":
        ps = (f"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications,"
              f" ContentType = WindowsRuntime] | Out-Null; "
              f"Write-Output {json.dumps(payload['title'] + ': ' + payload['message'])}")
        return ["powershell", "-NoProfile", "-Command", ps]
    return None


def send(payload: dict, dry_run: bool = False) -> dict:
    """Fire both channels. Never raises on a channel that is missing — the other still lands."""
    result = {"banner": "skipped", "push": "skipped"}
    if dry_run:
        return result
    cmd = banner_cmd(payload)
    if cmd:
        try:
            subprocess.run(cmd, check=False, capture_output=True, timeout=10)
            result["banner"] = "sent"
        except (OSError, subprocess.SubprocessError) as exc:
            result["banner"] = f"failed: {exc}"
    try:
        req = urllib.request.Request(
            payload["ntfy_url"], data=payload["message"].encode("utf-8"),
            headers={"Title": payload["title"]})
        urllib.request.urlopen(req, timeout=10).close()
        result["push"] = "sent"
    except Exception as exc:                     # noqa: BLE001 - a push failure must not kill it
        result["push"] = f"failed: {exc}"
    return result


def newest_thread(root: Path) -> Path | None:
    files = sorted(root.glob("*/ui_messages.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def read_thread(path: Path) -> list[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def _project_name() -> str:
    return Path.cwd().name


def once(root: Path, dry_run: bool = False) -> int:
    path = newest_thread(root)
    if path is None:
        print(f"zoo-notify: no threads under {root}")
        return 0
    messages = read_thread(path)
    event = classify(messages)
    if event is None:
        print(f"zoo-notify: {path.parent.name} needs nothing")
        return 0
    payload = compose(event, _project_name(), messages[-1].get("text", ""))
    outcome = send(payload, dry_run=dry_run)
    print(f"zoo-notify: {event} -> banner={outcome['banner']} push={outcome['push']}")
    print(f"  {payload['title']} | {payload['message']}")
    return 0


def watch(root: Path, interval: int, dry_run: bool = False) -> int:
    print(f"zoo-notify: watching {root} every {interval}s (ctrl-c to stop)")
    seen: dict[str, tuple[float, str | None]] = {}
    try:
        while True:
            for path in root.glob("*/ui_messages.json"):
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    continue
                prev = seen.get(str(path))
                if prev and prev[0] == mtime:
                    continue
                event = classify(read_thread(path))
                seen[str(path)] = (mtime, event)
                # only a TRANSITION notifies - a rewritten file in the same state is not news
                if event and (not prev or prev[1] != event):
                    messages = read_thread(path)
                    payload = compose(event, _project_name(), messages[-1].get("text", ""))
                    outcome = send(payload, dry_run=dry_run)
                    print(f"zoo-notify: {path.parent.name} {event} -> "
                          f"banner={outcome['banner']} push={outcome['push']}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nzoo-notify: stopped")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="classify the newest thread and notify")
    mode.add_argument("--watch", action="store_true", help="poll the store and notify on changes")
    ap.add_argument("--interval", type=int, default=5, help="seconds between polls (--watch)")
    ap.add_argument("--dry-run", action="store_true", help="compose only; no banner, no push")
    ap.add_argument("--store", type=Path, default=None, help="override the thread store root")
    args = ap.parse_args()
    root = Path(args.store) if args.store else store_root()
    if not root.is_dir():
        print(f"zoo-notify: no store at {root} - is Zoo Code installed for this user?")
        return 2
    return watch(root, args.interval, args.dry_run) if args.watch else once(root, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
