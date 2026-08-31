#!/usr/bin/env python3
"""Read a chat, find the commands that stopped for approval, propose the allow rows (SCC-354).

Growing an agent's allow list means re-reading a session by eye to work out which prefix would
have let a blocked command through. This does that reading.

⭐ It exists for Zoo, and the asymmetry is the whole reason. Claude Code offers "don't ask again"
in its own approval prompt, so its allow list grows as you work. Zoo has no such affordance: its
decisions live in VS Code `globalState`, the tracked `.vscode/settings.json` seeds that store
ONCE on a fresh machine, and denies never seed at all. Zoo is the platform that cannot help
itself. [[zoo-approvals-decision-store]]

⛔ It PRINTS. It writes no store, on any platform — not the tracked settings file, not the
memento, not `.claude/settings.json`. The operator picks the rows and applies them; a door that
edits an approval list is a door that can approve things on its own behalf.

Stdlib only; runs as `python3` (Mac / CI Linux) and `python` (PC).
"""
from __future__ import annotations

import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _notify():
    """Import zoo_notify.py by path — it is a script, not a package member.

    Its `store_roots()` and `read_thread()` already solve Zoo store discovery, including
    `zoo-code.customStoragePath` and named VS Code profiles. Re-deriving them here would be a
    second answer to a question this repo has already answered once and tested.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("zoo_notify", SCRIPTS / "zoo_notify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def blocked_commands(messages: list[dict]) -> list[str]:
    """The commands Zoo actually STOPPED on, oldest first, de-duplicated.

    `autoApprovalDecision is None` is Zoo's own record that its matcher had no opinion and the
    operator was needed. An ask Zoo auto-approved ("approve") never blocked anyone and already
    runs, so proposing a row for it is noise; one it denied ("deny") was refused by the fence on
    purpose, and the fence is not what this door grows.

    `partial` is a stream still in flight — Zoo rewrites `ui_messages.json` on every token, so a
    half-written command is the normal case here, not the exotic one.
    """
    out: list[str] = []
    for msg in messages:
        if msg.get("type") != "ask" or msg.get("ask") != "command":
            continue
        if msg.get("partial") is True or msg.get("autoApprovalDecision") is not None:
            continue
        text = (msg.get("text") or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def zoo_threads(roots: list[Path] | None = None) -> list[Path]:
    """Every `ui_messages.json` on this machine, newest thread first."""
    m = _notify()
    roots = roots if roots is not None else m.store_roots()
    found: list[Path] = []
    for root in roots:
        if root.is_dir():
            found += sorted(root.glob("*/ui_messages.json"),
                            key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def _matcher():
    """The matcher mirror — ONE module, the same one the 78-row battery pins (SCC-354 A1)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("zoo_matcher", SCRIPTS / "zoo_matcher.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def propose(cmd: str, allow: list[str], deny: list[str]) -> str | None:
    """The shortest allow row that would have let `cmd` through — subject to the breadth floor.

    ⛔ The floor is not a nicety, and the shortest prefix on its own is a hole. Measured against
    the live lists: the shortest prefix that flips `npx create-next-app my-app` to auto_approve
    is the single character `n`, and it leaks NONE of the 78 destructive battery rows — so a
    proposer checked only for "does it work" and "does it leak the battery" emits it, and that
    row then auto-approves `npm publish`, `node evil.js`, `nc -l 4444` and
    `netsh advfirewall set allprofiles state off`. The battery is a fence around what this house
    already knew to fear; it is not a definition of safe.

    So candidates are TOKEN BOUNDARIES only — `npx`, then `npx create-next-app`, and so on. A row
    never stops inside a token it does not complete, which is what makes "shortest" mean
    "narrowest family" instead of "fewest characters".

    Returns None when no boundary flips it: the command is denied by the fence, and growing the
    allow list is the wrong answer to that. The fence is not what this door grows.
    """
    decide = _matcher().decide
    tokens = cmd.split()
    for k in range(1, len(tokens) + 1):
        row = " ".join(tokens[:k])
        if decide(cmd, allow + [row], deny) == "auto_approve":
            return row
    return None
