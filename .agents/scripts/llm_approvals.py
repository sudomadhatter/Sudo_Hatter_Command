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
import re
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


def render(roots: list[Path], threads: int, blocked: list[str],
           proposals: list[tuple[str, list[str]]]) -> str:
    """The whole output of the door, as a string. It builds text; it opens nothing.

    ⛔ ASCII only. This output is exactly the kind that gets redirected into a file and read on
    the other machine, and a decorative glyph is what took 22 files red on the PC when cp1252
    met it. [[mac-authored-code-hides-windows-bugs]]

    ⛔ The counts print even when they are all zero. "Nothing stopped for approval" and "the
    door is broken" are the same empty screen otherwise, and the operator cannot tell which
    from where he sits — the store root is a genuine environment fact (a worktree resolves a
    different count than the lobby), not a bug, and only the printed root makes it legible.
    """
    out = ["smh-llm-approvals - Zoo Code approval rows", ""]
    out.append("Scanned:")
    for root in roots:
        out.append(f"  {root}")
    out.append(f"  threads read: {threads}")
    out.append(f"  commands that stopped for approval: {len(blocked)}")
    out.append("")
    if not proposals:
        out.append("Nothing to propose: no command stopped for approval in the threads above.")
        out.append("If that is a surprise, check the root printed above is the store Zoo is using.")
        return "\n".join(out)
    out.append("Proposed allow rows - NOTHING IS WRITTEN, you pick:")
    out.append("")
    for row, covers in proposals:
        out.append(f'  "{row}"')
        for cmd in covers:
            out.append(f"      unblocks: {cmd}")
        out.append("")
    out.append("To apply: add the rows you want to .vscode/settings.json "
               "zoo-code.allowedCommands, quit VS Code fully, then run")
    out.append("  python3 .agents/scripts/zoo_permissions_apply.py --apply   (PC: python)")
    return "\n".join(out)


def group(blocked: list[str], allow: list[str],
          deny: list[str]) -> list[tuple[str, list[str]]]:
    """One proposed row per family, carrying every blocked command it would unblock.

    Three things drop out here rather than reaching the operator's pick-list:

      * a command the lists ALREADY auto-approve — it was blocked when Zoo asked, but the row
        that fixed it has since landed. Proposing it again is noise, and a pick-list nobody
        trusts is a pick-list nobody reads.
      * a command the fence DENIES — this door grows the allow list; the deny list is the fence
        and is not what it grows. Inventing a row for a denied command is the door taking the
        fence apart one proposal at a time.
      * a duplicate row — one row per family, with its commands listed under it, so the operator
        picks families rather than re-reading the same prefix five times.
    """
    matcher = _matcher()
    rows: dict[str, list[str]] = {}
    for cmd in blocked:
        if matcher.decide(cmd, allow, deny) == "auto_approve":
            continue
        row = propose(cmd, allow, deny)
        if row is None:
            continue
        rows.setdefault(row, []).append(cmd)
    return list(rows.items())


def live_lists() -> tuple[list[str], list[str]]:
    """The lists Zoo is ACTUALLY enforcing — the VS Code memento, not the tracked file.

    ⭐ This is the whole reason the door reads the store instead of `.vscode/settings.json`:
    that file seeds `globalState` once on a fresh machine and denies never seed at all, so the
    tracked file is a statement of intent and the memento is the enforced truth. Proposing rows
    against intent would tell the operator a command is covered when Zoo is still asking for it.
    [[zoo-approvals-decision-store]]

    Falls back to the tracked lists when no store can be read (a fresh clone, CI, a machine with
    no VS Code) — with the caller printing which was used, because "your lists are empty" and
    "I could not find your lists" are different problems.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "zoo_permissions_apply", SCRIPTS / "zoo_permissions_apply.py")
    apply_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(apply_mod)
    for db in apply_mod.candidate_dbs():
        memento = apply_mod.load_memento(db)
        if memento:
            return memento.get("allowedCommands", []), memento.get("deniedCommands", [])
    return apply_mod.tracked_lists()


DENIAL = "doesn't want to proceed with this tool use"


def claude_blocked_commands(lines: list[str]) -> list[str]:
    """The Bash commands a Claude session was refused, oldest first, de-duplicated.

    ⛔ The denial record does NOT carry the command. Claude writes the rejection as a
    `tool_result` holding an `is_error` flag and a `tool_use_id`, and the command lives in the
    earlier assistant `tool_use` block with that id. Grepping the session for the rejection text
    therefore finds every denial and can name none of them, which is the one thing this reader
    is for — so it walks forward, remembers each `tool_use`, and pairs the refusal back to it.

    Only `Bash` tools produce rows. A refused `Write` or `Edit` has no Bash rule that would have
    allowed it, and a proposed rule matching nothing is noise the operator has to rule out.
    """
    uses: dict[str, str] = {}
    out: list[str] = []
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:                   # a session being written while we read it
            continue
        content = (record.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Bash":
                cmd = (block.get("input") or {}).get("command")
                if cmd:
                    uses[block.get("id")] = cmd
            elif (block.get("type") == "tool_result" and block.get("is_error")
                    and DENIAL in str(block.get("content", ""))):
                cmd = uses.get(block.get("tool_use_id"))
                if cmd and cmd not in out:
                    out.append(cmd)
    return out


def command_words(cmd: str) -> list[str]:
    """The command WORD of every shell piece in `cmd` — what a `Bash(<word> *)` rule can name.

    ⛔ Not `cmd.split()[0]`. Found by running the door against real sessions: a refused command
    was `W=/Users/.../tree; cd "$W" && python3 ...`, and taking the first whitespace token
    proposed `Bash(W=/Users/.../tree; *)` — a rule matching exactly one string that will never
    be typed again, handed to the operator as if it were useful. Multi-line refusals were worse:
    the whole block became one "token", so one rule covered the first command and the operator
    re-approved the same block tomorrow for the second.

    It splits with `zoo_matcher.pieces()` — the same splitter the matcher itself uses, so the
    door and the thing it proposes rows for agree about where one command ends — and steps over
    leading `VAR=value` assignments, which are shell setup and not a command anyone can allow.
    """
    words: list[str] = []
    # Mask redirections BEFORE the split, exactly as `decide()` does — the splitter breaks on
    # `&`, so `2>&1` otherwise becomes a piece whose command word is the bare digit `1`.
    cmd = re.sub(r"\d*>&\d*", " ", cmd)
    for piece in _matcher().pieces(cmd):
        for token in piece.split():
            if "=" in token and not token.startswith("-"):
                continue                    # VAR=value: shell setup, not a command word
            if token and token not in words:
                words.append(token)
            break
    return words


def claude_handoff(repo: Path, blocked: list[str]) -> str:
    """A block to paste to another agent — because Claude Code cannot edit its own settings.

    ⭐ ONE store, resolved from where you stand. This workspace holds six `.claude/settings.json`
    files and every one of them differs, so "add it to .claude/settings.json" names nothing an
    agent can act on. The absolute path of the repo you ran the door in is the answer, and it is
    printed rather than described.

    The rule shape is this house's own — `Bash(npx *)`, a prefix and a star — read off the
    lobby's live allow list rather than remembered.
    """
    store = repo / ".claude" / "settings.json"
    if not blocked:
        return ("Claude: nothing was refused in the sessions read, so there is no hand-off "
                f"block. The store that would have been named is {store}.")
    rules = []
    for cmd in blocked:
        for word in command_words(cmd):
            rule = f"Bash({word} *)"
            if rule not in rules:
                rules.append(rule)
    if not rules:
        return ("Claude: commands were refused, but none of them starts with a command word a "
                f"Bash rule can name. The store is {store}; the refusals were:\n"
                + "\n".join(f"    {c}" for c in blocked))
    lines = [
        "Claude hand-off - paste this to an agent that can edit the file "
        "(Claude Code cannot edit its own settings):",
        "",
        f"  In {store}, add these to permissions.allow:",
        "",
    ]
    lines += [f"    \"{r}\"," for r in rules]
    lines += [
        "",
        "  They were refused in the sessions read:",
    ]
    lines += [f"    {c}" for c in blocked]
    return "\n".join(lines)


def repo_root(start: Path | None = None) -> Path:
    """The top of the tree you are standing in, walked up from `start` (default: cwd).

    ⛔ `.git` is a FILE in a worktree and a directory in a normal checkout, so the test is
    `exists()`. Checking `is_dir()` walks straight past every worktree in this repo and names
    the lobby's store instead — the wrong file, confidently.
    """
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".git").exists():
            return candidate
    return here


def claude_sessions(limit: int) -> list[Path]:
    """The newest session transcripts Claude Code has written on this machine."""
    root = Path.home() / ".claude" / "projects"
    if not root.is_dir():
        return []
    files = sorted(root.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Read Zoo threads, print the allow rows that would unblock them. "
                    "Writes nothing.")
    ap.add_argument("--limit", type=int, default=20,
                    help="how many of the newest threads to read (default 20)")
    args = ap.parse_args(argv)

    notify = _notify()
    roots = notify.store_roots()
    threads = zoo_threads(roots)[:args.limit]
    blocked: list[str] = []
    for thread in threads:
        for cmd in blocked_commands(notify.read_thread(thread)):
            if cmd not in blocked:
                blocked.append(cmd)
    allow, deny = live_lists()
    print(render(roots, len(threads), blocked, group(blocked, allow, deny)))

    # Claude gets a hand-off, not a writer: Claude Code cannot edit its own settings, so the
    # door prints a block to paste to an agent that can. Same reading, different ending.
    claude_blocked: list[str] = []
    for session in claude_sessions(args.limit):
        for cmd in claude_blocked_commands(session.read_text(encoding="utf-8",
                                                             errors="replace").splitlines()):
            if cmd not in claude_blocked:
                claude_blocked.append(cmd)
    print()
    print(claude_handoff(repo_root(), claude_blocked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
