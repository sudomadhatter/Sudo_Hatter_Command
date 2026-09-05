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

⛔ That filter is a DENY-list, deliberately, and the review is why. The first cut carried an
allow-list of the four ask names read off those two threads. Zoo raises more than four:
`auto_approval_max_req_reached` is the ask it emits precisely BECAUSE auto-approval hit its cap and
the operator must intervene, and an allow-list drawn from a thin sample dropped it silently — the
exact "Zoo sits blocked and nobody knows" state this script exists to end. A notifier fails OPEN: a
spurious banner costs a glance, a missed one costs the whole feature. `completion_result` is the
only ask that is not a decision, and it is handled above the guards as a turn ending.

Stdlib only; runs as `python3` (Mac) / `python` (PC). CLI:
    zoo_notify.py --once            classify the newest thread and notify if it earns one
    zoo_notify.py --watch [--interval N]   poll the store and notify on transitions
    `--dry-run` is a MODIFIER on either mode, never a mode of its own: compose and print,
    open no network, raise no banner.
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
SETTING_CUSTOM_STORE = "zoo-code.customStoragePath"

# The ask vocabulary measured off two real threads (154 messages). Kept as a RECORD of what was
# observed, never as a filter — see the deny-list note in the module docstring. `classify` does not
# read this set, and must not: the store's real vocabulary is larger than any sample of it.
MEASURED_ASKS = {"command", "tool", "followup", "completion_result", "resume_completed_task"}


def user_dir(platform: str | None = None, home: Path | None = None,
             appdata: Path | None = None, xdg: Path | None = None) -> Path:
    """VS Code's `User` directory on this machine. [[one-pc-windows-and-wsl]]

    ⛔ This branched exactly TWO ways until SCC-396 — `win32`, else Mac — so Linux and WSL
    resolved to `~/Library/Application Support`, a path that cannot exist there. Nothing raised:
    `store_roots()` simply returned a missing directory and the caller reported zero threads,
    which reads identically to "Zoo was never used". `vscode_sync.get_vscode_user_dir()` has
    branched three ways all along; these two resolvers describe the same directory, so a
    disagreement between them is always a bug in one of them.
    """
    platform = platform if platform is not None else sys.platform
    # ⛔ An explicit `home` means a CALLER pinned the machine — a test with a fake HOME, almost
    # always — so the ambient `XDG_CONFIG_HOME` must not override it. The runner sets that
    # variable and the operator's boxes do not, so the first cut passed on both machines and
    # went red only in CI, reading the RUNNER's real config dir out of a tmpdir sandbox. That is
    # the hazard `test_main_actually_honours_custom_storage_path_end_to_end` already documents
    # for HOME/APPDATA: a test that silently escapes its sandbox and reads live user data is
    # worse than a red one. The env var is consulted only when resolving the LIVE machine.
    explicit_home = home is not None
    home = Path(home) if explicit_home else Path.home()
    if platform == "win32":
        base = Path(appdata) if appdata is not None else Path(
            os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif platform == "darwin":
        base = home / "Library" / "Application Support"
    elif xdg is not None:
        base = Path(xdg)
    else:
        env = None if explicit_home else os.environ.get("XDG_CONFIG_HOME")
        base = Path(env) if env else home / ".config"
    return base / "Code" / "User"


def user_dirs(platform: str | None = None, home: Path | None = None,
              appdata: Path | None = None, xdg: Path | None = None) -> list[Path]:
    """Every `User` directory this machine could hold — the local install AND the Remote server.

    Under VS Code Remote (WSL, SSH, dev containers) the extension runs SERVER-side and keeps its
    task store in the REMOTE home at `~/.vscode-server/data/User/globalStorage/`. Measured
    2026-09-04 on the live WSL box: the store was there while `~/.config/Code` did not exist at
    all, so fixing the Linux branch alone still reported zero (SCC-396).

    ⛔ Not the same question as `zoo_permissions_apply.candidate_dbs()`, which is correct as it
    stands and must not be "fixed" to match. That function hunts `state.vscdb` — the globalState
    database — which under WSL lives in the WINDOWS user-data-dir and is reached through /mnt/c;
    no `state.vscdb` exists in the distro (re-verified 2026-09-04). The task store and the
    globalState DB live in different places, and both notes are true at once.
    """
    # ⛔ Forward `home` UNRESOLVED: `user_dir` distinguishes "the caller pinned a home" from
    # "resolve the live machine", and pre-resolving here would erase that and let the ambient
    # XDG_CONFIG_HOME back into every test.
    dirs = [user_dir(platform, home, appdata, xdg)]
    resolved = Path(home) if home is not None else Path.home()
    remote = resolved / ".vscode-server" / "data" / "User"
    if remote not in dirs:
        dirs.append(remote)
    return dirs


def store_root(platform: str | None = None, home: Path | None = None,
               appdata: Path | None = None, custom: Path | None = None) -> Path:
    """Where Zoo keeps its per-task threads, in the DEFAULT profile.

    `zoo-code.customStoragePath` is a real Zoo setting — a watcher that ignores it happily polls an
    empty directory forever and reports success, so `read_custom_store` below wires it to the CLI.
    """
    if custom is not None:
        return Path(custom) / "tasks"
    return user_dir(platform, home, appdata) / "globalStorage" / EXTENSION_DIR / "tasks"


def read_custom_store(user: Path) -> Path | None:
    """`zoo-code.customStoragePath` out of user settings, or any named profile's settings.

    A parameter no entry point can reach is a claim, not a feature: `store_root(custom=…)` existed
    from the first cut and nothing ever passed it, so the documented setting was silently ignored.
    """
    candidates = [user / "settings.json"]
    profiles = user / "profiles"
    if profiles.is_dir():
        candidates += sorted(profiles.glob("*/settings.json"))
    for path in candidates:
        try:
            value = json.loads(path.read_text(encoding="utf-8")).get(SETTING_CUSTOM_STORE)
        except (OSError, ValueError, AttributeError):
            continue
        if value:
            return Path(value)
    return None


def store_roots(platform: str | None = None, home: Path | None = None,
                appdata: Path | None = None, custom: Path | None = None,
                xdg: Path | None = None) -> list[Path]:
    """Every thread store on this machine — the default profile AND each named profile.

    Its sibling `zoo_permissions_apply.py` already enumerates `profiles/*/globalStorage/` for this
    same extension, so a named profile is a live case in this system, not a hypothetical: resolving
    only the default one reports "is Zoo Code installed?" at a machine where it plainly is.
    """
    if custom is not None:
        return [Path(custom) / "tasks"]
    roots: list[Path] = []
    for index, user in enumerate(user_dirs(platform, home, appdata, xdg)):
        root = user / "globalStorage" / EXTENSION_DIR / "tasks"
        # ⛔ The FIRST root is returned whether or not it exists — `main` reads an all-missing
        # list as "Zoo is not installed" and exits 2, and that signal dies if this returns []. A
        # further candidate only earns a row when it is really on disk, or every machine would
        # report a Remote store it does not have.
        if index == 0 or root.is_dir():
            roots.append(root)
        profiles = user / "profiles"
        if profiles.is_dir():
            roots += sorted(profiles.glob(f"*/globalStorage/{EXTENSION_DIR}/tasks"))
    return roots


def classify(messages: list[dict]) -> str | None:
    """Does this thread's tail deserve to interrupt the operator? 'ask' | 'turn_end' | None.

    ⛔ `partial` is consulted for a `say` and NEVER for an `ask`, and that asymmetry is the whole
    SCC-355 fix. The first cut returned None for any tail flagged `partial: True` on the reasoning
    that a stream in flight is not a decision point — true of narration, false of an ask. Zoo
    clears the flag when its OWN matcher auto-approves and leaves it standing when the operator
    must answer, so the guard threw away precisely the asks it existed to catch: measured on the
    live store, 13 of the 16 `tool` asks that wanted the operator (81%), `tool` being the
    `newTask` subagent launch. Ten asks on disk carry `partial=True` AND `isAnswered=True` —
    Zoo stamped the answer on top and never cleared it, which is the proof it is a resting state
    and not a transient one.
    """
    if not messages:
        return None
    last = messages[-1]
    kind = last.get("type")
    if kind == "ask":
        if last.get("ask") == "completion_result":
            return "turn_end"
        if last.get("isAnswered") is True:   # never literal False in the store — absent means open
            return None
        if last.get("autoApprovalDecision") is not None:
            return None                      # Zoo already decided; the operator was not needed
        return "ask"                         # deny-list: every OTHER ask wants him. Fail open.
    if last.get("partial") is True:          # a SAY still streaming is not a decision point
        return None
    if kind == "say" and last.get("say") == "completion_result":
        return "turn_end"
    return None


def thread_signature(messages: list[dict], event: str | None) -> tuple:
    """What makes THIS notification distinct from the last one on the same thread.

    ⛔ Keying on the event word alone loses a second ask: the operator answers #1, Zoo raises #2,
    and if both land inside one poll interval the state never left "ask", so the transition test
    says "not news" and the second decision is dropped in silence. The tail's own `ts` is what
    actually distinguishes them.
    """
    if not messages:
        return (event, 0, None)
    return (event, len(messages), messages[-1].get("ts"))


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


# PowerShell's own AppUserModelID. A toast raised with an unregistered AppId is silently dropped on
# some Windows builds, and this is the documented id for notifying from PowerShell itself.
_PS_APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"


def banner_cmd(payload: dict, platform: str | None = None) -> list[str] | None:
    """The desktop banner argv for this machine, or None where we have no banner channel.

    Mac uses terminal-notifier, the same binary Claude's notify.sh uses — and the same Focus-mode
    caveat applies: a Work Focus swallows the banner while everything still exits 0, so a silent
    Mac is not proof the notifier failed. [[claude-notifications-hook-schema-and-ntfy]]

    ⛔ The PC branch CONSTRUCTS AND SHOWS a toast. The first cut loaded the WinRT type, threw it
    away through `Out-Null`, and then `Write-Output`-ed the text into a pipe `send()` captures —
    so nothing ever appeared on screen while the run reported `banner=sent`. That is a check that
    cannot fail, authored on a Mac, exactly the shape [[mac-authored-code-hides-windows-bugs]]
    warns about. `$ErrorActionPreference='Stop'` makes a failure a non-zero exit, which `send()`
    now reads instead of assuming success.
    """
    platform = platform if platform is not None else sys.platform
    if platform == "darwin":
        return ["terminal-notifier", "-title", payload["title"], "-message", payload["message"]]
    if platform == "win32":
        title = json.dumps(payload["title"])
        message = json.dumps(payload["message"])
        ps = (
            "$ErrorActionPreference='Stop'; "
            "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,"
            "ContentType=WindowsRuntime]|Out-Null; "
            "[Windows.UI.Notifications.ToastNotification,Windows.UI.Notifications,"
            "ContentType=WindowsRuntime]|Out-Null; "
            "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
            "[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            "$n=$t.GetElementsByTagName('text'); "
            f"$n.Item(0).AppendChild($t.CreateTextNode({title}))|Out-Null; "
            f"$n.Item(1).AppendChild($t.CreateTextNode({message}))|Out-Null; "
            f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{_PS_APP_ID}')"
            ".Show([Windows.UI.Notifications.ToastNotification]::new($t))"
        )
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
            proc = subprocess.run(cmd, check=False, capture_output=True, timeout=10)
            # ⛔ Read the exit code. `check=False` plus an unconditional "sent" reported success
            # for a notifier that ran and failed — the false green the plan's own Risk section
            # says B4 must be able to tell apart from "never fired".
            result["banner"] = "sent" if proc.returncode == 0 else f"failed: exit {proc.returncode}"
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
    def mtime(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:                      # a task dir deleted between the glob and the stat
            return -1.0
    files = sorted(root.glob("*/ui_messages.json"), key=mtime, reverse=True)
    return files[0] if files else None


def read_thread(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):            # Zoo rewrites this file constantly; a mid-write read
        return []                            # is the normal case, not the exotic one
    return data if isinstance(data, list) else []


def project_name(thread: Path | None = None) -> str:
    """The project the TASK belongs to — read from its own `history_item.json`.

    ⛔ Not `Path.cwd().name`. One `--watch` daemon polls the whole store, so a cwd-derived name
    stamps every project's banner with whatever directory the watcher happened to start in. This
    is the half of Claude-parity a copied idiom loses: `notify.sh` is a per-session hook that runs
    INSIDE the session's cwd, so the field is true there and false here.
    """
    if thread is not None:
        try:
            workspace = json.loads(
                (thread.parent / "history_item.json").read_text(encoding="utf-8")).get("workspace")
            if workspace:
                return Path(workspace).name
        except (OSError, ValueError, AttributeError):
            pass
        return thread.parent.name            # the task id: opaque, but never the WRONG project
    return Path.cwd().name


def self_test(dry_run: bool = False) -> int:
    """Fire one sample notification NOW and report honestly. Exit 1 if a channel did not fire.

    Proving this live used to mean waiting for a real Zoo ask, which is not a check anybody runs.
    This is the same `send()` the watcher calls, so a green self-test on a machine is real evidence
    that machine's channels work — and on the PC it is the only way to find out that a toast never
    displays, because a banner that silently shows nothing is indistinguishable from a quiet one.
    """
    payload = compose("ask", "self-test", "zoo_notify.py --self-test")
    outcome = send(payload, dry_run=dry_run)
    print(f"zoo-notify: self-test -> banner={outcome['banner']} push={outcome['push']}")
    print(f"  {payload['title']} | {payload['message']}")
    if dry_run:
        return 0
    failed = sorted(k for k, v in outcome.items() if str(v).startswith("failed:"))
    if failed:
        print(f"zoo-notify: {' and '.join(failed)} did not fire")
        return 1
    if banner_cmd(payload) is None:
        print("zoo-notify: no banner channel on this platform - the push is the only signal")
    else:
        print("zoo-notify: both channels reported OK. If NO banner appeared on screen, the "
              "channel is broken even though this exited 0 - on a Mac check Focus mode first.")
    return 0


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
    payload = compose(event, project_name(path), messages[-1].get("text", ""))
    outcome = send(payload, dry_run=dry_run)
    print(f"zoo-notify: {event} -> banner={outcome['banner']} push={outcome['push']}")
    print(f"  {payload['title']} | {payload['message']}")
    return 0


def watch(roots: list[Path], interval: int, dry_run: bool = False, fresh: int = 300) -> int:
    """Poll every store and notify on a genuine transition.

    ⛔ The FIRST sweep primes and sends nothing. Zoo keeps one directory per task forever, and a
    finished thread's tail stays `ask/completion_result` on disk — which classifies `turn_end`. So
    a watcher starting with an empty `seen` treats the entire backlog as fresh news and pages the
    operator once per historical thread, every restart. That is the failure the module docstring
    opens by naming, arriving through the other door.

    ⭐ ONE exception, and it is narrow (SCC-355). Once this runs as a launchd agent it restarts at
    every login and after every crash, and asks measurably sit open for 17+ minutes — so
    "restarted while Zoo is blocked waiting" is the routine case, not the exotic one, and a
    totally silent prime loses exactly the page that mattered. During priming an **unanswered
    ask** whose thread was written within `fresh` seconds still pages. Stale asks stay silent, and
    a turn-end never takes the exception at any age: it is not blocking anyone. `fresh=0` restores
    the always-silent prime.
    """
    print(f"zoo-notify: watching {len(roots)} store(s) every {interval}s (ctrl-c to stop)")
    seen: dict[str, tuple[float, tuple]] = {}
    started = time.time()
    priming = True
    try:
        while True:
            for root in roots:
                for path in root.glob("*/ui_messages.json"):
                    try:
                        mtime = path.stat().st_mtime
                    except OSError:
                        continue
                    prev = seen.get(str(path))
                    if prev and prev[0] == mtime:
                        continue
                    messages = read_thread(path)     # read ONCE - a second read can lose the race
                    event = classify(messages)       # and hand back [], which then indexes [-1]
                    signature = thread_signature(messages, event)
                    seen[str(path)] = (mtime, signature)
                    # priming is silent EXCEPT for an ask Zoo is blocked on right now
                    if priming and not (fresh and event == "ask"
                                        and started - mtime <= fresh):
                        continue
                    # only a TRANSITION notifies - a rewritten file in the same state is not news
                    if event and (not prev or prev[1] != signature):
                        payload = compose(event, project_name(path),
                                          messages[-1].get("text", ""))
                        outcome = send(payload, dry_run=dry_run)
                        print(f"zoo-notify: {path.parent.name} {event} -> "
                              f"banner={outcome['banner']} push={outcome['push']}")
            if priming:
                print(f"zoo-notify: primed on {len(seen)} existing thread(s) - watching for new")
                priming = False
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nzoo-notify: stopped")
        return 0


def _interval(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("--interval must be at least 1 second")
    return value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="classify the newest thread and notify")
    mode.add_argument("--watch", action="store_true", help="poll the store and notify on changes")
    mode.add_argument("--self-test", action="store_true",
                      help="fire one sample notification now and report; exit 1 if a channel failed")
    ap.add_argument("--interval", type=_interval, default=5, help="seconds between polls (--watch)")
    # ⛔ Wired to the CLI deliberately: this module already shipped one parameter no entry point
    # could reach (`store_root(custom=…)`), and a documented setting nothing can pass is a claim,
    # not a feature. `--prime-window 0` restores the always-silent prime.
    ap.add_argument("--prime-window", type=int, default=300, metavar="SECONDS",
                    help="on startup, still page for an unanswered ask newer than this "
                         "(default 300; 0 = prime in total silence)")
    ap.add_argument("--dry-run", action="store_true", help="compose only; no banner, no push")
    ap.add_argument("--store", type=Path, default=None, help="override the thread store root")
    args = ap.parse_args()
    if args.self_test:                       # proves the CHANNELS; needs no thread store at all
        return self_test(args.dry_run)
    if args.store:
        roots = [Path(args.store)]
    else:
        # Under Remote the settings.json that carries `customStoragePath` sits beside the
        # server-side store, not in the local User dir — ask every candidate (SCC-396).
        custom = next((c for c in (read_custom_store(u) for u in user_dirs()) if c), None)
        roots = store_roots(custom=custom)
    live = [r for r in roots if r.is_dir()]
    if not live:
        print(f"zoo-notify: no store at {', '.join(str(r) for r in roots)} "
              f"- is Zoo Code installed for this user?")
        return 2
    if args.watch:
        return watch(live, args.interval, args.dry_run, fresh=max(0, args.prime_window))
    return once(live[0], args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
