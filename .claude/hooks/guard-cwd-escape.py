#!/usr/bin/env python3
"""PreToolUse hook: a TOP-LEVEL `cd` out of the workspace silently retargets the whole session.

The bug this exists to make impossible (SCC-182, measured twice on SCC-164's own lane):

  The Bash tool's cwd persists between calls UNTIL a command ends outside the workspace root -
  /tmp, the session scratchpad, a sibling repo. The harness then resets cwd to the PRIMARY
  working directory, which is the MAIN checkout and never the worktree you are working in. It
  says so in one line. Every relative path afterwards reads MAIN.

  Nothing errors. The same path exists in both trees and both are valid git repos, so the wrong
  answer is well-formed: `mutation_sweep.py` was written into the main checkout, and a structural
  read of "the lane's" test file was main's 333-line copy while the lane's was 463.

The remedy is verified, not assumed:

    ( cd /tmp && ... )   -> after the call, cwd UNCHANGED, no reset
    cd /tmp && ...       -> reset to the main checkout

A subshell runs the work in a child whose cwd change dies with it. So this hook is narrow on
purpose: it flags a `cd` only when it is a real command, at paren depth 0, leaving the workspace.
`git -C`, absolute paths, the subshell form, and any `cd` that stays inside all pass untouched.

⛔ FAILS OPEN, always. Unparseable stdin, an unresolvable workspace root, a variable it cannot
expand, any exception at all -> allow. A guard that cannot judge has learned nothing, and one
that blocks on confusion is worse than the bug it chases. (SCC-77's rule, the other half: a hook
that cannot run must never fail SILENTLY - but this one is advisory, so silence IS the allow.)

Canonical source: `.agents/hooks/`. Deployed to `.claude/hooks/` - never hand-edit the copy."""
import json
import os
import sys

KEYWORDS = {"{", "}", "!", "time", "do", "then", "else", "elif", "fi", "done", "sudo", "command"}
CD = {"cd", "pushd"}


def allow() -> None:
    sys.exit(0)


def ask(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def segments(cmd: str) -> list[tuple[str, int]]:
    """Split into command segments, carrying each one's PAREN DEPTH.

    Quotes, escapes, `#` comments and heredoc BODIES are skipped, because a `cd` inside any of
    them is text, not a command - `echo "cd /tmp"` must not trip a gate about changing directory.
    """
    out: list[tuple[str, int]] = []
    buf: list[str] = []
    depth = 0
    sq = dq = False
    i, n = 0, len(cmd)
    while i < n:
        ch = cmd[i]
        if sq:
            if ch == "'":
                sq = False
            buf.append(ch); i += 1; continue
        if dq:
            if ch == "\\" and i + 1 < n:
                buf.append(cmd[i:i + 2]); i += 2; continue
            if ch == '"':
                dq = False
            buf.append(ch); i += 1; continue
        if ch == "\\" and i + 1 < n:
            buf.append(cmd[i:i + 2]); i += 2; continue
        if ch == "'":
            sq = True; buf.append(ch); i += 1; continue
        if ch == '"':
            dq = True; buf.append(ch); i += 1; continue
        if ch == "#" and (not buf or buf[-1].isspace()):
            j = cmd.find("\n", i)
            i = n if j < 0 else j
            continue
        if cmd.startswith("<<", i):
            i = _skip_heredoc(cmd, i, n)
            continue
        if ch == "(":
            out.append(("".join(buf), depth)); buf = []; depth += 1; i += 1; continue
        if ch == ")":
            out.append(("".join(buf), depth)); buf = []; depth = max(0, depth - 1); i += 1; continue
        if ch in ";&|\n":
            out.append(("".join(buf), depth)); buf = []; i += 1; continue
        buf.append(ch); i += 1
    out.append(("".join(buf), depth))
    return out


def _skip_heredoc(cmd: str, i: int, n: int) -> int:
    """Advance past `<<DELIM ... DELIM`. On any doubt, advance one char - never loop forever."""
    k = i + 2
    if k < n and cmd[k] == "-":
        k += 1
    while k < n and cmd[k] in " \t":
        k += 1
    quote = cmd[k] if k < n and cmd[k] in "'\"" else None
    if quote:
        k += 1
    start = k
    while k < n and (cmd[k] != quote if quote else cmd[k] not in " \t\n;&|)"):
        k += 1
    delim = cmd[start:k]
    if not delim:
        return i + 2
    eol = cmd.find("\n", k)
    if eol < 0:
        return n
    j = eol + 1
    while j <= n:
        nl = cmd.find("\n", j)
        line = cmd[j:n if nl < 0 else nl]
        if line.strip() == delim:
            return n if nl < 0 else nl
        if nl < 0:
            return n
        j = nl + 1
    return n


def first_word_and_arg(seg: str) -> tuple[str, str]:
    """The segment's command and its first non-flag argument, past keywords and VAR=x prefixes."""
    words = seg.split()
    while words and (words[0] in KEYWORDS or ("=" in words[0] and not words[0].startswith("-"))):
        words.pop(0)
    if not words:
        return "", ""
    cmdname = words[0]
    rest = [w for w in words[1:] if not w.startswith("-") or w == "-"]
    return cmdname, (rest[0] if rest else "")


def unquote(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    return s


def leaves_workspace(arg: str, root: str, cwd: str) -> bool | None:
    """True = leaves, False = stays, None = cannot tell (caller allows)."""
    arg = unquote(arg.strip())
    if arg == "" or arg == "-" or arg == "~" or arg.startswith("~/"):
        return True                                   # $HOME, or an unknowable $OLDPWD
    if arg in ("$HOME", "${HOME}", '"$HOME"'):
        return True
    if "$" in arg or "`" in arg:
        return None                                   # an unexpanded variable: cannot judge
    base = cwd if not os.path.isabs(arg) else "/"
    if not os.path.isabs(arg) and not base:
        return None
    target = os.path.normpath(arg if os.path.isabs(arg) else os.path.join(base, arg))
    for r in {os.path.normpath(root), os.path.realpath(root)}:
        if target == r or target.startswith(r.rstrip("/") + "/"):
            return False
    return True


REASON = (
    "⛔ `{cmd} {arg}` leaves the workspace, and this shell's cwd does not survive it.\n"
    "The harness resets cwd to the PRIMARY working directory — the MAIN checkout — so every "
    "relative path in your NEXT calls reads main, not the worktree you are working in. It does "
    "not error: the same file exists in both trees, so you get a well-formed answer about the "
    "wrong tree. That is how a script got written into main, and how main's stale copy of a test "
    "file was read as the lane's.\n\n"
    "Two remedies, both verified:\n"
    "  1. Run it in a subshell — the cd dies with the child and cwd is untouched:\n"
    "       ( cd {arg} && <your command> )\n"
    "  2. Better: do not cd at all. Use `git -C /abs/path ...` and absolute paths for every "
    "read and write.\n\n"
    "If you genuinely mean to move this shell out of the workspace, approve this call."
)


def main() -> None:
    # No local try/except here: `allow()` raises SystemExit, which `except Exception` does not
    # catch, so the outer handler at the bottom already turns any parse failure into an allow.
    # A second one would be unreachable-by-behaviour - a mutant that deletes it cannot be killed.
    data = json.load(sys.stdin)
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        allow()
    command = (data.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        allow()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or ""
    if not root or not os.path.isdir(root):
        allow()
    cwd = data.get("cwd") or root

    for seg, depth in segments(command):
        if depth > 0:
            continue                                   # inside ( … ): the sanctioned form
        name, arg = first_word_and_arg(seg)
        if name not in CD:
            continue
        verdict = leaves_workspace(arg, root, cwd)
        if verdict:
            ask(REASON.format(cmd=name, arg=arg or "~"))
    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        allow()
