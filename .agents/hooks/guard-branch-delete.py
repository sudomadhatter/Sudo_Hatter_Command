#!/usr/bin/env python3
"""PreToolUse hook: a `git branch` DELETE is fenced by its TARGET LIST, not by its flag (SCC-411).

⛔ WHY A HOOK AND NOT A PERMISSION ROW — this is the whole reason the file exists.
`git branch -d` takes a LIST. Every permission grammar in this house matches from the LEFT: Zoo
takes a literal lowercased PREFIX, Antigravity takes a per-token anchored regex over a command's
LEADING tokens, Claude takes `Bash(<prefix>:*)`. None of the three can say *"exactly one argument,
and it starts with chore/"*, so the first target satisfies the rule and every target after it
rides free — with no shell metacharacter for a splitter to see. Measured against real git 2.43:

    $ git branch -d worktree-agent-x main
    Deleted branch worktree-agent-x (was 9dd7d8f).
    Deleted branch main (was 9dd7d8f).

Measured 2026-09-06 against the rendered lists at `aa408738`, every one reading ALLOW:

    git branch -d chore/SCC-1-x main   zoo=allow  claude=allow  antigravity=allow
    git branch -r -d origin/main       zoo=allow  claude=allow  antigravity=allow
    git branch -v -d main              zoo=allow  claude=allow  antigravity=allow
    git branch --delete main           zoo=allow  claude=ask    antigravity=allow

The last three are the same defect wearing a different hat: the deny row names the FIRST flag
(`git branch -[a-zA-Z]*[dD][a-zA-Z]*`), so ANY option in front of the delete flag walks past it —
and `-r`, `-v`, `-vv` and `--format` are granted on Claude as READS, which real git happily
accepts alongside a delete. Zoo and Antigravity get deny rows for the spellings their grammars
CAN express (`.agents/permissions/families.json`, `deny-git-branch`); the target-list escape stays
a documented residual there. Claude runs hooks, so here it closes properly.

⭐ THE SCOPE OF "FAILS OPEN", because this is the line the design turns on. Silence is the answer
to *"this is not a branch delete"* — a listing, a create, a rename, another verb, another tool,
malformed input. Silence is NOT the answer to *"this IS a branch delete and I cannot prove the
targets are safe"*: an unreadable target (`"$BRANCH"`, a backtick body, an unbalanced quote) is
DENIED, because the one command a shrugging guard would wave through is the one that laundered a
target past every other fence. Unreadable is not the same as harmless.

⛔ NEVER an ask. In auto mode an ask is an auto-DENY that strands a headless run, and the deny
here is the honest verdict anyway (`shape-block.py` carries the same law). Two outcomes only:
refuse, or say nothing.

Canonical source: `.agents/hooks/`. Wired in `.claude/settings.json`'s single `PreToolUse` Bash
group, dispatched through `run-hook.sh` like every sibling. Pinned by
`.agents/scripts/tests/test_guard_branch_delete.py`; named as a Claude-side fence in
`.agents/rules/git-policy.md`.
"""
from __future__ import annotations

import json
import re
import sys

RULE = ".agents/rules/git-policy.md"

# The branch namespaces an agent may delete. Everything else — `main`, a bare name, a
# remote-tracking ref — is the operator's.
LANE_PREFIXES = ("chore/", "claude/", "epic/")

# A git invocation carrying any run of pre-subcommand options, so `git -C <path> branch …` and
# `git -c k=v branch …` are seen. The long options below take their value as a SEPARATE token and
# would otherwise end the match: `git --work-tree /tmp branch -d victim` deleted the branch with
# the guard silent (SCC-411 review, blind lens F4). `--opt=value` is covered by the generic arm.
_GIT_SEPARATE_VALUE = r"--(?:work-tree|git-dir|namespace|super-prefix|exec-path)\s+\S+"
_GIT_OPTS = (r"(?:\s+(?:" + _GIT_SEPARATE_VALUE +
             r"|-C\s+(?:'[^']*'|\"[^\"]*\"|\S+)|-c\s+\S+|--?[A-Za-z][\w-]*(?:=\S+)?))*")
_GIT_BRANCH = re.compile(r"\bgit" + _GIT_OPTS + r"\s+branch\b")

# Options that swallow the NEXT token as their value, so the value is not read as a branch name.
#
# ⛔ THE SKIP IS NEVER ALLOWED TO EAT A FLAG, and that rule matters more than this list is
# accurate. Measured on real git 2.43 (SCC-411 review, two independent lenses): `--color`, `-t`
# and `--track` take an OPTIONAL argument, so git does NOT consume the next token — but this hook
# did, and the token it ate was `-d`:
#
#     $ git branch -v --color -d victim
#     Deleted branch victim (was fd0546a).        # hook: SILENT, and allow on all three platforms
#
# They are gone from the list, and `skip_value` now refuses any value starting with `-` — which is
# git's own parse-options rule for optional arguments, and makes a future misclassification here
# cost a false DENY (safe) instead of a silent delete of `main` (not). The survivors really do
# consume: `git branch --merged -d x` errors with "malformed object name -d".
_VALUE_FLAGS = frozenset({
    "--contains", "--no-contains", "--merged", "--no-merged", "--points-at",
    "--sort", "--format", "--set-upstream-to", "-u",
})

# What makes a token unreadable: the shell will substitute it and we cannot know the result.
_UNREADABLE = ("`", "$")

_QUOTES = "\"'`"
_SEPARATORS = "&|;\n"


def segments(command: str) -> list[str]:
    """Split on unquoted `&&`, `||`, `;`, `|`, `&` and newlines. NEVER refuses.

    ⛔ It must not have a "I don't understand this" exit. `allow-readonly-chain.py` refuses an
    odd shape because refusing there means *granting nothing*, which is safe. Refusing HERE would
    mean *fencing nothing*, which is the opposite — so an unbalanced quote simply ends the last
    segment and the tokens inside it come out unreadable, which the caller turns into a refusal.
    """
    out: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in command:
        if quote is not None:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in _QUOTES:
            quote = ch
            buf.append(ch)
            continue
        if ch in _SEPARATORS:
            out.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    out.append("".join(buf))
    return [s for s in (x.strip() for x in out) if s]


def tokenize(text: str) -> list[str]:
    """Whitespace-split, but never inside quotes. A quote that never closes still yields its
    token — unreadable, which is exactly what the caller needs to know."""
    out: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in text:
        if quote is not None:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in _QUOTES:
            quote = ch
            buf.append(ch)
            continue
        if ch.isspace():
            if buf:
                out.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


def is_lane_target(token: str) -> bool:
    """True only for a target we can READ and that names a lane branch.

    ⛔ Both halves are load-bearing and neither may be relaxed on its own. Drop the readability
    half and `git branch -d "$BRANCH"` passes; drop the namespace half and every target passes.
    """
    if any(mark in token for mark in _UNREADABLE):
        return False
    bare = token.replace('"', "").replace("'", "")
    return bare.startswith(LANE_PREFIXES)


def inspect_branch_tail(tail: str) -> tuple[bool, bool, list[str]]:
    """(carries a delete flag, carries a remotes flag, target tokens) for the text after `branch`."""
    delete = remote = False
    targets: list[str] = []
    skip_value = False
    flags_done = False
    for token in tokenize(tail):
        if skip_value:
            skip_value = False
            # ⛔ A VALUE THAT LOOKS LIKE A FLAG IS NOT A VALUE. git's own parse-options says so,
            # and this is the line that stops a mis-listed option from eating `-d` (SCC-411
            # review). Falling through re-reads the token as the flag it is.
            if not token.startswith("-"):
                continue
        if not flags_done and token == "--":
            flags_done = True
            continue
        if flags_done or not token.startswith("-") or token == "-":
            targets.append(token)
            continue
        if token.startswith("--"):
            name = token.split("=", 1)[0]
            if name == "--delete":
                delete = True
            elif name in ("--remotes", "--remote"):
                remote = True
            elif name in _VALUE_FLAGS and "=" not in token:
                skip_value = True
            continue
        # A short cluster is ONE token to getopt: `-rd` is `-r -d`, and `-Df` is `-D -f`.
        letters = token[1:]
        if any(ch in "dD" for ch in letters):
            delete = True
        if "r" in letters:
            remote = True
        if token in _VALUE_FLAGS:
            skip_value = True
    return delete, remote, targets


def mask_quoted(text: str) -> str:
    """`text`'s length, with every character inside a quoted span replaced by NUL.

    ⛔ A COMMAND'S TEXT IS NOT WHAT IT RUNS. `grep -rn "git branch -d main" .agents/` MENTIONS a
    delete; it does not perform one — and refusing it fenced this repo out of searching for its
    own literals, and out of writing the commit message that describes them (SCC-411 review,
    blind lens F3; the same scar `shape_scan.py` carries about counting a search as a use).

    The invocation is therefore searched for in this masked copy, while the tail is sliced from
    the ORIGINAL at the same offsets — so a quoted TARGET is still read in full and
    `git branch -d "chore/$B"` is still refused as unreadable.
    """
    out: list[str] = []
    quote: str | None = None
    for ch in text:
        if quote is not None:
            out.append("\x00")
            if ch == quote:
                quote = None
            continue
        if ch in _QUOTES:
            quote = ch
            out.append("\x00")
            continue
        out.append(ch)
    return "".join(out)


def strip_comment(segment: str, masked: str) -> tuple[str, str]:
    """Both strings cut at the first unquoted `#` that starts a word. What follows never runs."""
    for i, ch in enumerate(masked):
        if ch == "#" and (i == 0 or masked[i - 1].isspace()):
            return segment[:i], masked[:i]
    return segment, masked


# A segment whose executable is a shell reading its script from an argument. There the quoted
# span IS a command, so it must NOT be masked away: `bash -c "git branch -d main"` really deletes.
_SHELL_C = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:\S*/)?(?:ba|z|da|k|)sh\s+(?:-\S+\s+)*-\S*c")


def classify(command: str) -> tuple[str, str] | None:
    """('deny', reason), or None for silence. THE WHOLE DECISION LIVES HERE.

    ⛔ Not half here and half at the call site (the SCC-418 scar): a decision split across a
    predicate and the `if` that consumes it can be widened at the call site while every test of
    the predicate stays green. `main()` does no judging — it prints what this returns.
    """
    if "branch" not in command:
        return None
    # A backslash-newline is a line continuation: the shell rejoins it and runs ONE command, but
    # `segments()` split on the newline and handed the verb and its delete flag to two different
    # segments, so `git branch -v \<newline>-d victim` deleted with the guard silent (SCC-411
    # review, blind lens F2). Rejoin before splitting, exactly as the shell does.
    command = command.replace("\\\n", " ")
    for segment in segments(command):
        masked = segment if _SHELL_C.match(segment) else mask_quoted(segment)
        segment, masked = strip_comment(segment, masked)
        match = _GIT_BRANCH.search(masked)
        if not match:
            continue
        delete, remote, targets = inspect_branch_tail(segment[match.end():])
        if not delete:
            continue
        if remote:
            return "deny", (
                f"{RULE} — REFUSED: this deletes a REMOTE-TRACKING ref (`-r`/`--remotes` with a "
                f"delete flag), which is never a lane prune. `git branch -r -d origin/main` reads "
                f"as ALLOWED on all three platforms because every permission grammar matches the "
                f"first flag only (measured 2026-09-06, SCC-411). Nothing ran. If a remote branch "
                f"is what you meant, the ceremony is `git push origin --delete chore/<KEY>-<slug>`; "
                f"to refresh stale refs use `git fetch --prune`.")
        if not targets:
            # ⛔ FAILS CLOSED, per this file's own design law. A delete ALWAYS names a branch, so
            # "a delete with no readable target" means the target was consumed by an option this
            # parser mis-read — which is exactly how `git branch -d --color main` went silent
            # before the review (SCC-411). Silence here would be the shrug the docstring forbids.
            return "deny", (
                f"{RULE} — REFUSED: this is a `git branch` DELETE whose target list came back "
                f"EMPTY, so the branch being deleted cannot be read before it goes. That means an "
                f"option in the command swallowed it. Nothing ran. Re-issue the delete with the "
                f"branch named last and no option between the flag and the name: "
                f"`git branch -d chore/<KEY>-<slug>`.")
        unreadable = [t for t in targets if any(m in t for m in _UNREADABLE)]
        unsafe = [t for t in targets if not is_lane_target(t)]
        if not unsafe:
            continue
        if unreadable:
            return "deny", (
                f"{RULE} — REFUSED: this deletes branch(es) named by a substitution or variable "
                f"({', '.join(unreadable[:3])}), so the real target cannot be read before it is "
                f"deleted — `git branch -d chore/x `echo main`` deletes `main`. Nothing ran. "
                f"Resolve the name in a prior call and pass the literal; only `chore/`, `claude/` "
                f"and `epic/` branches are deletable by an agent.")
        return "deny", (
            f"{RULE} — REFUSED: `git branch -d` takes a LIST and this one names "
            f"{', '.join(unsafe[:4])}, which is outside the namespaces an agent may delete. Every "
            f"permission grammar here matches from the LEFT, so a leading `chore/` target "
            f"satisfies the rule and everything after it rides free (measured on real git 2.43: "
            f"`git branch -d worktree-agent-x main` deleted BOTH). Nothing ran. Delete only "
            f"`chore/`, `claude/` or `epic/` branches; `main` and bare names are the operator's.")
    return None


def main() -> int:
    try:
        event = json.loads(sys.stdin.read())
        if event.get("tool_name") != "Bash":
            return 0
        command = (event.get("tool_input") or {}).get("command") or ""
        if not isinstance(command, str) or not command.strip():
            return 0
        verdict = classify(command)
        if verdict is None:
            return 0
        decision, reason = verdict
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }}))
    except Exception:  # noqa: BLE001 — a guard that cannot read the EVENT says nothing.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
