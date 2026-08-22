#!/usr/bin/env python3
"""PreToolUse hook: auto-ALLOW the narrow shape of Bash command that can only touch this
session's scratchpad.

The friction this exists to remove:

  Every verification lane - /smh-code-review most of all - builds a throwaway runtime harness
  under `/private/tmp/claude-<uid>/<project>/<session-id>/scratchpad/`, then runs it. Twenty-odd
  `mkdir`/`bash`/`python3`/`rm -rf` approvals per run, for a directory that dies with the session.
  Settings cannot pre-grant it: `Bash(...)` rules match the command string by PREFIX, never a
  path, and the scratchpad path carries a per-session id, so a literal rule written today matches
  nothing tomorrow. A PreToolUse hook is the only layer that sees the resolved command.

⛔ THE ARCHITECTURE, AND WHY THE FIRST ONE WAS THROWN AWAY (SCC-263 review).

The first implementation asked "are all the ABSOLUTE PATHS I can find inside the sandbox?" - a
DENY-list over a surface it had to recognise first. Five review lenses reproduced twelve escapes
in it, and every single one had the same shape: something the regexes did not recognise AS a path
was treated as harmless.

    rm -rf /<sandbox>/rt .agents      -> ALLOWED. `.agents` is relative; nothing collected it.
    rm -rf .git # cleanup /<sandbox>  -> ALLOWED. A path in a COMMENT satisfied "sandbox present".
    bash /<sandbox>/r.sh > "out.txt"  -> ALLOWED. The redirect regex excluded quote characters.
    bash /<sandbox>/r.sh >&out.txt    -> ALLOWED. `>&FILE` writes a FILE; it was read as an fd dup.
    tar -C/<repo> -xf /<sandbox>/p.tar-> ALLOWED. A path glued to a flag is invisible to a lookbehind.
    "curl" ... / \\curl ... / /usr/bin/curl -> ALLOWED. The deny-list needed a delimiter before the word.
    git -C /<sandbox>/r log && git reset --hard -> ALLOWED. One well-formed -C licensed every bare git.

That list is not a set of bugs to patch. It is what a deny-list over shell syntax always
degrades into: the parser is the security boundary, and a regex is not a shell parser. Patching a
thirteenth hole moves the fourteenth.

So this version inverts it into an ALLOW-list of SHAPES, and everything it does not positively
recognise is refused:

  1. NO SHELL METACHARACTERS AT ALL. One simple command per call. No `;`, `&`, `|`, `<`, `>`,
     backtick, `$`, quotes, backslash, glob, brace, `#`, or newline. This single rule kills the
     comment escape, both redirect escapes, the chaining escapes and every quoting escape at once,
     because none of those constructs can survive to be misparsed.
     ⭐ It costs less than it looks: `chmod +x X && bash X` becomes two Bash calls, and BOTH are
     auto-allowed. Two silent calls beat one prompted call.
  2. THE EXECUTABLE IS A BARE NAME FROM A LITERAL LIST. Not a path - so `/usr/bin/sudo`,
     `/usr/bin/git` and `/opt/homebrew/bin/curl` are refused by construction rather than by a
     delimiter the next escape works around. There is no `SAFE_PREFIXES` any more: nothing outside
     the sandbox is readable OR writable, and the read/write asymmetry that leaked write
     permission into `/usr/local` and `/opt/homebrew` cannot exist.
  3. EVERY NON-FLAG TOKEN IS AN ABSOLUTE PATH INSIDE THIS SESSION'S SCRATCHPAD. Relative
     arguments are refused outright - `.agents`, `out.txt`, `conftest.py` are not paths this hook
     can resolve, and it no longer pretends otherwise. A `--flag=VALUE` is split and its VALUE
     held to the same bar, so a path glued to a flag is checked rather than hidden.
  4. THE SANDBOX IS THIS SESSION'S, not the uid's. The old root stopped at `claude-<uid>/`, two
     levels too high, so `rm -rf /private/tmp/claude-501/` was allowed and would have wiped every
     concurrently running lane's harness. The root must now be a full
     `claude-<uid>/<project>/<session>/scratchpad` - and when the payload carries `session_id`,
     the path must contain THAT session's id.

⛔ TWO LEGAL OUTPUTS: `allow`, or SILENCE. Never `ask`, never `deny`.
`ask` is auto-DENY in non-interactive mode, so a hook that emitted it would block the very lanes
it exists to unblock. Refusing here means printing NOTHING and letting the normal approval prompt
happen - this hook can only ever REMOVE a prompt it is certain about, never ADD one.

⛔ FAILS SILENT, always. Unparseable stdin, any exception at all -> print nothing, exit 0.

WHAT THIS STILL DOES NOT DEFEND AGAINST, stated plainly: `bash /<sandbox>/x.sh` runs whatever the
agent wrote into that file, and writing into the scratchpad was never gated. The hook removes the
prompt on RUNNING agent-authored code, not on authoring it. That is the deliberate trade; the
twelve escapes above were not.

Canonical source: `.agents/hooks/`. Deployed to `.claude/hooks/` - never hand-edit the copy."""
import json
import re
import sys

# Rule 4. A full session scratchpad, never a prefix of one: `/tmp/claude-<uid>/<project>/<session>/
# scratchpad`. `/tmp` is a symlink to `/private/tmp` on macOS, so both spellings must be accepted.
SANDBOX_RE = re.compile(
    r"^/(?:private/)?tmp/claude-\d+/[^/]+/[0-9A-Za-z][0-9A-Za-z_-]{7,}/scratchpad(?:/|$)")

# Rule 1. Anything that makes this more than ONE simple command, or that makes token boundaries a
# matter of interpretation. `#` is here because a path inside a comment is text the shell discards
# and the old hook counted as proof of sandboxing.
FORBIDDEN = set("`$|&;<>()[]{}*?!#~'\"\\\n\r")

# Rule 2. Bare names only. An absolute path is NOT accepted here, which is what makes the
# `/usr/bin/<denied>` class unreachable instead of merely inconvenient.
ALLOWED = frozenset({
    "mkdir", "rmdir", "rm", "cp", "mv", "touch", "chmod", "ln",
    "ls", "cat", "head", "tail", "wc", "diff", "cmp", "file", "stat", "du",
    "bash", "sh", "python3", "python", "node",
})

# `chmod`'s mode argument is the one non-flag, non-path token this hook accepts, and only in
# first position, and only for chmod: `+x`, `755`, `u+rw,go-w`.
MODE_RE = re.compile(r"^[0-7]{3,4}$|^[ugoa]*[+\-=][rwxXst]+(?:,[ugoa]*[+\-=][rwxXst]+)*$")

FLAG_RE = re.compile(r"^-{1,2}[A-Za-z0-9][A-Za-z0-9-]*$")
FLAG_WITH_VALUE_RE = re.compile(r"^(-{1,2}[A-Za-z0-9][A-Za-z0-9-]*)=(.*)$")


def sandboxed(token: str, session_id: str) -> bool:
    """A token is acceptable only as an absolute path inside THIS session's scratchpad."""
    if not SANDBOX_RE.match(token):
        return False
    # Rule 4's second half. `session_id` is advisory: the payload does not always carry one, and a
    # subagent may report its parent's. When it IS present it must appear in the path, which pins
    # the grant to this session rather than to any session of this uid.
    if session_id and f"/{session_id}/" not in token:
        return False
    return True


def permitted(command: str, session_id: str) -> bool:
    # 1: one simple command, unambiguously tokenizable by whitespace alone.
    if FORBIDDEN & set(command):
        return False
    tokens = command.split()
    if not tokens:
        return False

    # 2: a bare name from the list. `/` in the executable is refused, not resolved.
    argv0, args = tokens[0], tokens[1:]
    if argv0 not in ALLOWED:
        return False

    # 3: every remaining token is a flag, or a path inside the sandbox.
    saw_path = False
    for i, tok in enumerate(args):
        if argv0 == "chmod" and i == 0 and MODE_RE.match(tok):
            continue
        flagged = FLAG_WITH_VALUE_RE.match(tok)
        if flagged:
            # `--out=/x` - the VALUE is held to the same bar the bare token would be, which is
            # what the old lookbehind hid.
            if not sandboxed(flagged.group(2), session_id):
                return False
            saw_path = True
            continue
        if FLAG_RE.match(tok):
            continue
        if not sandboxed(tok, session_id):
            return False
        saw_path = True

    # A command of nothing but flags names no subject; there is nothing to be sure about.
    return saw_path


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return
    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str) or not command.strip():
        return
    session_id = payload.get("session_id") or ""
    if not isinstance(session_id, str):
        session_id = ""

    if not permitted(command, session_id):
        return

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "scratchpad-only: one simple command, allow-listed, every "
                                    "argument inside this session's disposable scratchpad",
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - a convenience hook must never become a blocker.
        pass
    sys.exit(0)
