#!/usr/bin/env python3
"""Install `zoo_notify.py --watch` as a background service, once per machine (SCC-355).

⛔ Why this exists, stated plainly: SCC-355 shipped the notifier and an SOP line telling the
operator to run `python3 .agents/scripts/zoo_notify.py --watch`, and shipped nothing that runs it.
`--watch` is a FOREGROUND blocking poll loop — Zoo contributes no event hook, so a live process is
the only possible trigger — and no process ever existed. The feature was 100% silent on the Mac
from the day it landed until the operator reported it. The classifier bug fixed alongside this
would have made it *partly* silent; this gap made it *entirely* silent, and it is the bigger half.

An instruction a human must remember is not a delivery mechanism. This is:

    zoo_notify_install.py                 what is installed right now (read-only, the default)
    zoo_notify_install.py --apply         install it and start it
    zoo_notify_install.py --remove        stop it and uninstall it
    `--dry-run` modifies --apply/--remove; `--json` makes the status machine-readable.

Mac -> a launchd agent at ~/Library/LaunchAgents/com.sudohatter.zoo-notify.plist, RunAtLoad +
KeepAlive, so it starts at login and restarts if it dies. PC -> a `.cmd` in the Startup folder
run through `pythonw` so no console window appears. Stdlib only, both machines.
[[two-machines-mac-and-pc]]
"""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import subprocess
import sys
from pathlib import Path

LABEL = "com.sudohatter.zoo-notify"
DEFAULT_TOPIC = "mac-sudo-command"
SCRIPT_PARTS = (".agents", "scripts", "zoo_notify.py")

# launchd's own PATH is /usr/bin:/bin:/usr/sbin:/sbin and NOTHING else. terminal-notifier is a
# Homebrew binary, so an agent inheriting that default loses the banner while the ntfy push keeps
# working — the "it half works" report, which is harder to diagnose than total silence.
_MAC_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"


def notifier_path(repo: Path) -> Path:
    return Path(repo).resolve().joinpath(*SCRIPT_PARTS)


def interpreter(platform: str) -> str:
    """The interpreter launchd should run.

    ⛔ NEVER `sys.executable`. Measured while building this: inside this repo `sys.executable` was
    `Projects/AGY_AVIATIONCHAT/backend/.venv/bin/python3` — a project virtualenv. Baking that into
    a login agent ties the operator's notifications to one project's venv, and rebuilding or
    deleting it kills notifications silently. The command centre is stdlib-only by law, so the
    SYSTEM interpreter is both sufficient and stable.
    """
    if platform == "win32":
        return "pythonw"
    for candidate in ("/usr/bin/python3", "/opt/homebrew/bin/python3", "/usr/local/bin/python3"):
        if Path(candidate).exists():
            return candidate
    return "/usr/bin/python3"


def plist_path(home: Path) -> Path:
    return Path(home) / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def startup_path(home: Path) -> Path:
    return (Path(home) / "AppData" / "Roaming" / "Microsoft" / "Windows"
            / "Start Menu" / "Programs" / "Startup" / "zoo-notify.cmd")


def target_path(home: Path, platform: str) -> Path | None:
    if platform == "darwin":
        return plist_path(home)
    if platform == "win32":
        return startup_path(home)
    return None


def build_plist(repo: Path, home: Path, platform: str = "darwin",
                topic: str | None = None) -> dict:
    """The launchd job. Every key here answers a way the first delivery failed."""
    logs = Path(home) / "Library" / "Logs"
    return {
        "Label": LABEL,
        "ProgramArguments": [interpreter(platform), str(notifier_path(repo)), "--watch"],
        "RunAtLoad": True,      # start at login, so the operator never types the command
        "KeepAlive": True,      # restart if it dies, so one crash is not permanent silence
        "EnvironmentVariables": {
            # ⛔ launchd does not source ~/.zshrc, where NTFY_TOPIC actually lives. It equals the
            # built-in default today, so this would have failed silently only once he changed it.
            # [[zshrc-is-invisible-to-automation]]
            "NTFY_TOPIC": topic or os.environ.get("NTFY_TOPIC") or DEFAULT_TOPIC,
            "PATH": _MAC_PATH,
            # ⛔ Without this the log below is EMPTY. Python block-buffers stdout whenever it is
            # not a TTY, and a poll loop never writes enough to flush — so the agent runs, launchctl
            # lists it, and the one file you would look at to confirm it is working says nothing.
            # Measured on the first live install, not read off the code.
            "PYTHONUNBUFFERED": "1",
        },
        # A background process with no log is indistinguishable from one that never started.
        "StandardOutPath": str(logs / "zoo-notify.log"),
        "StandardErrorPath": str(logs / "zoo-notify.err.log"),
    }


def build_cmd(repo: Path, topic: str | None = None) -> str:
    """The PC's Startup entry. CRLF, because cmd.exe mis-parses LF-only batch files."""
    lines = [
        "@echo off",
        "rem Zoo Code notifier (SCC-355) - installed by zoo_notify_install.py --apply",
        f"set NTFY_TOPIC={topic or os.environ.get('NTFY_TOPIC') or DEFAULT_TOPIC}",
        "set PYTHONUNBUFFERED=1",
        f'start "" /min pythonw "{Path(repo).resolve().joinpath(*SCRIPT_PARTS)}" --watch',
        "",
    ]
    return "\r\n".join(lines)


def _installed_script(target: Path, platform: str) -> Path | None:
    """The notifier path recorded INSIDE the installed artifact — not the one we would write."""
    try:
        if platform == "darwin":
            args = plistlib.loads(target.read_bytes()).get("ProgramArguments") or []
            return Path(args[1]) if len(args) > 1 else None
        body = target.read_text(encoding="utf-8")
        for chunk in body.split('"'):
            if chunk.endswith("zoo_notify.py"):
                return Path(chunk)
    except (OSError, ValueError, IndexError, plistlib.InvalidFileException):
        return None
    return None


def status(home: Path, platform: str | None = None) -> dict:
    """What is installed RIGHT NOW — read-only, and it verifies more than 'loaded'.

    ⭐ `launchctl list` showing the label is NOT proof the thing works: the plist embeds this
    repo's ABSOLUTE path, so moving or renaming the repo leaves a happily-loaded agent pointing at
    nothing. Only reading the recorded path back and checking it on disk catches that.
    """
    platform = platform if platform is not None else sys.platform
    target = target_path(Path(home), platform)
    if target is None:
        return {"installed": False, "script_exists": None, "target": None,
                "note": f"{platform} is not a supported platform for this installer"}
    if not target.exists():
        return {"installed": False, "script_exists": None, "target": str(target),
                "note": "not installed - run with --apply"}
    script = _installed_script(target, platform)
    return {
        "installed": True,
        "target": str(target),
        "script": str(script) if script else None,
        "script_exists": bool(script and script.exists()),
        "note": None if (script and script.exists())
                else "the installed job points at a path that no longer exists - re-run --apply",
    }


def _launchctl(args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(["launchctl", *args], capture_output=True, encoding="utf-8", text=True, timeout=30)
        return proc.returncode, (proc.stderr or proc.stdout or "").strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)


def apply(repo: Path, home: Path | None = None, platform: str | None = None,
          topic: str | None = None, load: bool = True, dry_run: bool = False) -> int:
    platform = platform if platform is not None else sys.platform
    home = Path(home) if home is not None else Path.home()
    target = target_path(home, platform)
    if target is None:
        print(f"zoo-notify-install: {platform} is not supported - nothing installed")
        return 2

    # ⛔ A login agent outlives any lane. `--repo` defaults to the tree this script is standing in,
    # and toolkit work is built inside `.claude/worktrees/<lane>/` — which close-out PRUNES. Baking
    # that path in gives the operator a loaded job pointing at a deleted directory from his next
    # login onward, with nothing on screen to say so. Refuse and name the checkout that persists.
    repo = Path(repo).resolve()
    if "worktrees" in repo.parts:
        main = Path(*repo.parts[:repo.parts.index(".claude")]) if ".claude" in repo.parts else None
        print(f"zoo-notify-install: REFUSED - {repo} is a git worktree, and it gets pruned.")
        print("  A login agent must point at the main checkout, which persists:")
        print(f"  zoo_notify_install.py --apply --repo {main or '<the main checkout>'}")
        return 2

    if platform == "darwin":
        payload = plistlib.dumps(build_plist(repo, home, platform, topic))
    else:
        payload = build_cmd(repo, topic).encode("utf-8")

    if dry_run:
        print(f"zoo-notify-install: DRY RUN - would write {target}")
        print(payload.decode("utf-8", "replace"))
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    if platform == "darwin":
        (home / "Library" / "Logs").mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)

    # ⛔ House law: on a write, verify the FILE - never `$?`.
    report = status(home, platform)
    if not report["installed"]:
        print(f"zoo-notify-install: wrote {target} but it does not read back - ABORT")
        return 1
    print(f"zoo-notify-install: wrote {target}")
    print(f"  runs: {report.get('script')}")
    if not report["script_exists"]:
        print(f"  WARNING: that path does not exist on disk - {report['note']}")
        return 1

    if load and platform == "darwin":
        _launchctl(["bootout", f"gui/{os.getuid()}/{LABEL}"])          # idempotent re-install
        rc, err = _launchctl(["bootstrap", f"gui/{os.getuid()}", str(target)])
        if rc != 0:
            rc, err = _launchctl(["load", "-w", str(target)])          # legacy fallback
        print("  launchctl: started" if rc == 0 else f"  WARNING: launchctl refused it: {err}")
        return 0 if rc == 0 else 1
    if load and platform == "win32":
        print("  it starts at your next login - or double-click the .cmd to start it now")
    return 0


def remove(home: Path | None = None, platform: str | None = None,
           unload: bool = True, dry_run: bool = False) -> int:
    platform = platform if platform is not None else sys.platform
    home = Path(home) if home is not None else Path.home()
    target = target_path(home, platform)
    if target is None or not target.exists():
        print("zoo-notify-install: nothing installed - nothing to remove")
        return 0
    if dry_run:
        print(f"zoo-notify-install: DRY RUN - would remove {target}")
        return 0
    if unload and platform == "darwin":
        _launchctl(["bootout", f"gui/{os.getuid()}/{LABEL}"])
    target.unlink()
    print(f"zoo-notify-install: removed {target}")
    return 0


def _print_status(report: dict) -> int:
    if not report["installed"]:
        print(f"zoo-notify-install: NOT installed - {report.get('note')}")
        return 1
    mark = "ok" if report["script_exists"] else "BROKEN"
    print(f"zoo-notify-install: installed [{mark}]  {report['target']}")
    print(f"  runs: {report.get('script')}")
    if report.get("note"):
        print(f"  WARNING: {report['note']}")
    return 0 if report["script_exists"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="install and start the watcher")
    mode.add_argument("--remove", action="store_true", help="stop and uninstall the watcher")
    ap.add_argument("--status", action="store_true", help="report what is installed (the default)")
    ap.add_argument("--dry-run", action="store_true", help="compose only; write nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable status")
    ap.add_argument("--topic", default=None, help=f"ntfy topic (default {DEFAULT_TOPIC})")
    ap.add_argument("--home", type=Path, default=None, help="override HOME (tests)")
    ap.add_argument("--platform", default=None, help="override the platform (tests)")
    ap.add_argument("--repo", type=Path, default=None, help="repo root (default: this script's)")
    args = ap.parse_args()

    repo = args.repo or Path(__file__).resolve().parents[2]
    home = args.home or Path.home()
    platform = args.platform or sys.platform

    if args.apply:
        return apply(repo, home, platform, args.topic, dry_run=args.dry_run)
    if args.remove:
        return remove(home, platform, dry_run=args.dry_run)
    report = status(home, platform)
    if args.json:
        print(json.dumps(report, indent=1))
        return 0 if report["installed"] and report["script_exists"] else 1
    return _print_status(report)


if __name__ == "__main__":
    sys.exit(main())
