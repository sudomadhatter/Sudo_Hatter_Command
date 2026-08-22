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
     held to the same bar, so a path glued to a flag is checked rather than hidden. The two
     exceptions are named and narrow: `chmod`'s mode in its first non-flag slot, and the digits
     after a counting flag (`head -n 5`).
  4. THE SANDBOX IS THIS SESSION'S, not the uid's. The first root stopped at `claude-<uid>/`, two
     levels too high, so `rm -rf /private/tmp/claude-501/` was allowed and would have wiped every
     concurrently running lane's harness. The root must be a full
     `claude-<uid>/<project>/<session>/scratchpad`, the uid must be THIS PROCESS'S, and when the
     payload carries `session_id` the session component must EQUAL it - matched positionally, not
     by containment. A containment test admitted a path under another live lane's session that
     merely had our id as a leaf directory name.

⛔ AND THE TWO THE REWRITE ITSELF GOT WRONG, found by a second review of THIS file:

  5. PATHS ARE NORMALISED BEFORE THEY ARE MATCHED. `SANDBOX_RE.match` is a PREFIX assertion - it
     stops at `scratchpad/` and never looks further - while `..` is ordinary text to a regex and
     to `str.split()`. So `/<sandbox>/../../../../../../Users/.../Sudo_Hatter_Command` matched,
     satisfied the session pin (the real id genuinely IS in the string), and was auto-approved for
     `rm -rf`. Version one banned `..` outright; this rewrite dropped the ban and did not replace
     it. `posixpath.normpath` FIRST, then match.
  6. NO TOOL WITH AN IMPLICIT DESTINATION. `ln -sf /<sandbox>/AGENTS.md` names one sandbox path
     and no destination at all - POSIX puts the link in the CURRENT DIRECTORY, and `-f` unlinks
     what is already there. No amount of argument inspection can see a destination the command
     string never contains, so the only defence is the allow-list, and `ln` is off it.

  ⭐ Rules 5 and 6 are a DIFFERENT class from the twelve above, and that is the lesson worth
  keeping. Those twelve were all "something not recognised AS a path was treated as harmless".
  These two are "a token correctly recognised as a path, correctly matched, and still resolving
  outside" - once because this compares strings where the kernel resolves a graph, once because
  the command supplies a destination the string never mentions. Getting the shell parser right
  did not make the FILESYSTEM safe.

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
import functools
import json
import os
import posixpath
import re
import sys

# ⛔ NOTHING AT MODULE LEVEL MAY RAISE, AND THIS BLOCK IS WHY THAT IS A RULE (SCC-267).
# `_UID = re.escape(f"claude-{os.getuid()}")` used to sit right here, at import time, OUTSIDE the
# `try/except` at the bottom of this file. `os.getuid` DOES NOT EXIST ON WINDOWS - so on the
# operator's second machine this hook raised `AttributeError` before `main()` was ever called and
# exited 1 with a traceback, on EVERY Bash call. The whole design rests on one promise - "it may
# only ever REMOVE a prompt it is certain about, never ADD one" - and the fail-safe wrapper that
# makes that promise true could not cover a crash that happened before it was installed.
# Everything below is therefore a FUNCTION, called from inside the wrapper, and every resolver
# answers `None` rather than raising. `None` means NO GRANT: this hook falls silent, and the
# operator gets the ordinary approval prompt they had before it existed.

# Where a machine says what its own scratchpad root is. Gitignored, one line, never committed -
# the same class as `core.hooksPath` and `~/.zshenv`: per-machine, and it never travels.
ROOT_FILE = (".claude", "scratchpad-root")


def _repo_root() -> str:
    """The repo this hook was loaded from. `CLAUDE_PROJECT_DIR` first (run-hook.sh exports it),
    then this file's own location - `<repo>/.agents/hooks/` and `<repo>/.claude/hooks/` are the
    same depth, so the master and the deployed copy resolve identically."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return env
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _configured_root() -> str | None:
    """The machine-local root override as a regex fragment, or None to fall through.

    ⛔ IT WIDENS THE ROOT, NEVER THE SHAPE. Whatever this names must still be followed by
    `/<project>/<session_id>/scratchpad`, session-pinned and normalised, exactly as the built-in
    root is - so a wrong entry here cannot grant more than one session's disposable directory.
    Anything it cannot fully validate returns None, which falls back to the built-in root; on a
    machine with no uid that means no grant at all.
    """
    path = os.path.join(_repo_root(), *ROOT_FILE)
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # ⛔ POSIX-spelled and absolute. A NATIVE Windows root (`C:\Users\...`) is refused here
        # rather than half-honoured, and that refusal is load-bearing: `\` is in FORBIDDEN, so a
        # command carrying a native Windows path is rejected by rule 1 no matter what this file
        # says. A root that can never match its own machine's commands is worse than none.
        if not line.startswith("/") or FORBIDDEN & set(line):
            return None
        norm = posixpath.normpath(line)
        # ⛔ At least two segments. `/` would make `/<anything>/<session>/scratchpad` grantable,
        # and a one-segment root is close enough to that to be worth refusing outright.
        if norm.count("/") < 2 or norm.endswith("/"):
            return None
        return re.escape(norm)
    return None


def _uid_root() -> str | None:
    """The built-in POSIX root as a regex fragment, or None where this process has no uid.

    ⛔ The uid is THIS PROCESS'S, never "any digits". A root accepting any digits accepted
    `/private/tmp/claude-999/…`, so a path under another account's tree satisfied the sandbox test
    (SCC-263 review, Edge Case Hunter). `getattr` rather than a bare call: on Windows the
    attribute is absent, and asking for it is what used to crash this file at import.
    """
    getuid = getattr(os, "getuid", None)
    if getuid is None:
        return None
    return rf"/(?:private/)?tmp/{re.escape(f'claude-{getuid()}')}"


@functools.lru_cache(maxsize=1)
def sandbox_root() -> str | None:
    """This machine's scratchpad root, as a regex fragment - or None, which means NO GRANT.

    The machine-local file wins when it validates, because a machine has exactly one scratchpad
    root and the built-in one describes only POSIX. Absent or unusable file -> the built-in root,
    so a Mac with no config behaves byte-for-byte as it did before this function existed.
    """
    try:
        return _configured_root() or _uid_root()
    except Exception:  # noqa: BLE001 - a resolver that raises must read as "no grant", not as a crash.
        return None


@functools.lru_cache(maxsize=4)
def sandbox_re(session_id: str) -> "re.Pattern[str] | None":
    """The ONE pattern, built around the session that is actually asking.

    ⛔ There is deliberately no session-agnostic pattern to fall back on. An earlier cut had two -
    a general `SANDBOX_RE` plus a positional pin applied only `if session_id` - so a payload
    carrying no session id was judged by shape alone and ANY live lane's scratchpad passed. Two
    regexes also meant the general one was barely load-bearing whenever a pin applied, which is
    how a mutation to it could survive. One pattern, no fallback, no drift.

    `/tmp` is a symlink to `/private/tmp` on macOS, so the built-in root accepts both spellings.
    Returns None when this machine has no resolvable root - the caller reads that as no grant.
    """
    root = sandbox_root()
    if root is None:
        return None
    return re.compile("^" + root + r"/[^/]+/"
                      + re.escape(session_id) + r"/scratchpad(?:/|$)")


# Rule 1. Anything that makes this more than ONE simple command, or that makes token boundaries a
# matter of interpretation. `#` is here because a path inside a comment is text the shell discards
# and the old hook counted as proof of sandboxing.
FORBIDDEN = set("`$|&;<>()[]{}*?!#~'\"\\\n\r")

# Rule 2. Bare names only. An absolute path is NOT accepted here, which is what makes the
# `/usr/bin/<denied>` class unreachable instead of merely inconvenient.
# ⛔ `ln` IS DELIBERATELY ABSENT, and this comment is why it must stay absent. `ln source` with a
# SINGLE operand is defined to create the link in the CURRENT DIRECTORY, named after the source's
# basename - and `-f` unlinks whatever is already there first. So `ln -sf /<sandbox>/AGENTS.md`
# passes every rule in this file (one allow-listed name, one flag, one genuinely sandboxed path,
# no `..`, no metacharacter) and DELETES the repo's own AGENTS.md, replacing it with a symlink to
# agent-authored content. The destination is one the command string never mentions, so no amount
# of argument inspection can catch it. Any future addition to this list must be checked for the
# same property: does this tool have an IMPLICIT destination? (SCC-263 review, Blind Hunter.)
ALLOWED = frozenset({
    "mkdir", "rmdir", "rm", "cp", "mv", "touch", "chmod",
    "ls", "cat", "head", "tail", "wc", "diff", "cmp", "file", "stat", "du",
    "bash", "sh", "python3", "python", "node",
})

# `chmod`'s mode argument is the one non-flag, non-path token this hook accepts, and only for
# chmod, and only in its first non-flag slot: `+x`, `755`, `u+rw,go-w`.
MODE_RE = re.compile(r"^[0-7]{3,4}$|^[ugoa]*[+\-=][rwxXst]+(?:,[ugoa]*[+\-=][rwxXst]+)*$")

# Flags whose VALUE is the next token and is a count, not a path. Without these, `head -n 5 X` and
# `tail -c 100 X` fall through to a prompt while `head -5 X` does not - friction the hook exists to
# remove. Scoped per command, and the value must be digits, so it can never name a file.
VALUE_FLAGS = {"head": {"-n", "-c"}, "tail": {"-n", "-c"}, "wc": {"-L"}}
COUNT_RE = re.compile(r"^\+?\d+$")

FLAG_RE = re.compile(r"^--$|^-{1,2}[A-Za-z0-9][A-Za-z0-9-]*$")
FLAG_WITH_VALUE_RE = re.compile(r"^(-{1,2}[A-Za-z0-9][A-Za-z0-9-]*)=(.*)$")


def sandboxed(token: str, session_id: str) -> bool:
    """A token is acceptable only as an absolute path inside THIS session's scratchpad.

    ⛔ NORMALISE BEFORE MATCHING. The pattern is a PREFIX assertion - it stops at `scratchpad/`
    and never looks further - while `..` is ordinary text to a regex and to `str.split()`. So
    `/<sandbox>/../../../../../../Users/.../Sudo_Hatter_Command` matched, satisfied the session
    check (the real id genuinely IS in the string), and was auto-approved for `rm -rf`. Two
    independent lenses reproduced it; version one banned `..` outright and the rewrite dropped
    that ban without replacing it (SCC-263 review).

    `normpath` is lexical, which is the right tool: the token often names a file that does not
    exist yet, so `realpath` would resolve nothing. A symlink already inside the sandbox can still
    point out, but planting one needs agent-authored code - the trade the module docstring
    declares - and `ln` is off the allow-list precisely so this hook cannot plant it.

    ⛔ NO SESSION ID, NO GRANT. `session_id` is not advisory: without it there is no way to tell
    this lane's disposable directory from a concurrently running one's, and the whole claim of
    this hook is that what it permits is disposable.
    """
    if not session_id or not token.startswith("/"):
        return False
    pattern = sandbox_re(session_id)
    if pattern is None:
        return False
    return bool(pattern.match(posixpath.normpath(token)))


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
    saw_mode = False
    expect_count = False
    for tok in args:
        if expect_count:
            # The value of a counting flag (`head -n 5`). Digits only, so it cannot name a file.
            expect_count = False
            if COUNT_RE.match(tok):
                continue
            return False
        # ⛔ The first non-flag slot BEFORE any path, not index 0. An index test refused the
        # canonical `chmod -R 755 X` (the `-R` occupies index 0); dropping the index test
        # without `not saw_path` then ALLOWED `chmod X +x`, where the mode is not a mode at
        # all. Both spellings are pinned in block F.
        if argv0 == "chmod" and not saw_mode and not saw_path and MODE_RE.match(tok):
            saw_mode = True
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
            expect_count = tok in VALUE_FLAGS.get(argv0, ())
            continue
        if not sandboxed(tok, session_id):
            return False
        saw_path = True

    # A flag left waiting for its value never got one, so the command is not the shape it looked.
    if expect_count:
        return False

    # A command of nothing but flags names no subject; there is nothing to be sure about.
    return saw_path


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return
    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str) or not command.strip():
        return
    session_id = payload.get("session_id")
    # A non-string or absent id is refused, never downgraded to "no pin" - that downgrade was
    # itself the fail-open (SCC-263 review, Edge Case Hunter).
    if not isinstance(session_id, str) or not session_id:
        return

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
