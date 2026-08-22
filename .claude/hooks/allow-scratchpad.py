#!/usr/bin/env python3
"""PreToolUse hook: auto-ALLOW Bash commands that only touch the session scratchpad.

The friction this exists to remove:

  Every review/verification lane - /smh-code-review most of all - builds a throwaway runtime
  harness under `/private/tmp/claude-<uid>/<project>/<session-uuid>/scratchpad/`, then runs it.
  Twenty-odd `mkdir`/`bash`/`python3`/`rm -rf` calls against a directory that exists only for
  this session, each one stopping for an approval the operator has no way to pre-grant:

    - Bash permission rules in settings match the COMMAND STRING by prefix, never a path. There
      is no `Bash(<any command touching /path/**>)` form.
    - Even if there were, the scratchpad path carries a per-session UUID, so no literal rule
      written today matches tomorrow's session.

  A hook is the only layer that sees the resolved command and can answer "everything this
  writes is disposable". So this hook answers exactly that, and nothing wider.

THE RULE - all seven must hold, or the hook stays silent and the normal prompt happens:

  1. At least one absolute path in the command is inside the scratchpad root. (No sandbox
     path mentioned -> this is ordinary repo work -> not our business.)
  2. EVERY absolute path is inside the scratchpad root or a read-only system prefix
     (`/usr`, `/bin`, `/opt/homebrew`, ...). One path outside -> silent.
  3. No `..` anywhere. A relative escape from inside the sandbox lands outside it.
  4. No `~` / `$HOME` / `$CLAUDE_PROJECT_DIR` / other variable or command substitution in the
     command. An unexpanded path is a path this hook cannot judge.
  5. No command from the deny list: `sudo`, network egress (`curl`, `wget`, `ssh`, `scp`,
     `nc`, `rsync`), and the machine-level configuration tools.
  6. No `git` call without `-C <sandbox>`. Bare `git` reads the AMBIENT repo, not the sandbox,
     however many sandbox paths appear elsewhere on the line.
  7. Every redirect target (`>`, `>>`, `2>`, `&>`) and every `tee` argument is an ABSOLUTE
     sandbox path, or `/dev/null`-class, or an fd duplication (`2>&1`). ⛔ Rules 1-6 constrain
     ABSOLUTE paths, and a redirect target does not have to be one: `bash /<sandbox>/run.sh >
     out.txt` names exactly one absolute path, inside the sandbox, and writes `out.txt` into
     whatever cwd the Bash tool currently holds - the repo working tree. Found by this lane's
     own self-audit, and it fails in the house's most expensive shape: nothing errors, both
     paths are valid, and the transcript is identical to a correct run (SCC-182's scar).

WHAT THIS DOES AND DOES NOT BUY. It removes the prompt for running code the agent already
wrote unprompted (writing into the scratchpad is not gated today, so the script's CONTENTS were
never the thing under review - only the act of running it was). It grants nothing outside a
directory the harness deletes when the session ends.

FAILS SILENT, always. Unparseable stdin, an unresolvable root, any exception at all -> print
nothing, exit 0, operator gets the normal prompt. This hook may only ever REMOVE a prompt it is
certain about; it must never ADD one. It therefore never emits `ask` - `ask` is auto-DENY in
non-interactive mode, and a convenience hook that can deny is a hook that breaks the lane it
was written to unblock.

Canonical source: `.agents/hooks/`. Deployed to `.claude/hooks/` - never hand-edit the copy."""
import json
import re
import sys

# The scratchpad tree. `/tmp` is a symlink to `/private/tmp` on macOS, so both spellings reach
# the same bytes and both must be recognised. `claude-<uid>` is the harness's own naming.
SANDBOX_RE = re.compile(r"^/(private/)?tmp/claude-\d+/")

# Read-only-by-convention system prefixes. Interpreters and coreutils get named by absolute path
# often enough (`/usr/bin/env`, `/opt/homebrew/bin/python3`) that omitting them would silence the
# hook on the very commands it exists for.
SAFE_PREFIXES = (
    "/usr/", "/bin/", "/sbin/", "/opt/homebrew/", "/Library/", "/System/",
    "/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty",
)

# Commands that reach past the filesystem no matter which paths they are handed.
DENY_WORDS = re.compile(
    r"(?:^|[\s;&|(])(?:sudo|doas|su|curl|wget|ssh|scp|sftp|rsync|nc|ncat|telnet|"
    r"launchctl|crontab|osascript|defaults|systemsetup|diskutil|chown)(?:$|[\s;&|)])"
)

# Anything the shell would expand before the paths this hook checked became real.
UNEXPANDED = re.compile(r"(?:\$\(|`|\$\{?[A-Za-z_]|(?:^|[\s=:'\"])~/)")

# An absolute path token: a `/` that begins a word, then everything up to shell punctuation.
ABS_PATH = re.compile(r"(?<![\w.~=+-])/[^\s'\"<>|;&()\\]*")

# `git` anywhere on the line - its repo comes from cwd unless `-C` says otherwise.
GIT_CALL = re.compile(r"(?:^|[\s;&|(])git(?:$|\s)")

# A redirect and the token it writes to: `> x`, `>> x`, `2> x`, `&> x`, `2>&1`.
REDIRECT = re.compile(r"(?:\d+|&)?>{1,2}\s*(&?[^\s'\"<>|;&()]+|&\d+)")

# `tee` and its arguments, up to the next shell operator. Flags are skipped; the rest are
# write targets exactly as a redirect is, and were the half of rule 7 easiest to forget.
TEE = re.compile(r"(?:^|[\s;&|(])tee\b([^|;&<>()]*)")

# The only paths a redirect may WRITE to. Deliberately NOT `SAFE_PREFIXES`: those exist so an
# absolute interpreter (`/usr/bin/env`) can be READ, and `> /usr/local/lib/x` must never inherit
# that permission.
WRITE_OK = ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty")


def sandboxed(path: str) -> bool:
    return bool(SANDBOX_RE.match(path))


def safe(path: str) -> bool:
    return sandboxed(path) or path.startswith(SAFE_PREFIXES)


def writable(target: str) -> bool:
    """Rule 7's test for one write target."""
    t = target.strip("'\"")
    if t.startswith("&"):          # `2>&1` - an fd duplication, it opens no file
        return True
    return sandboxed(t) or t in WRITE_OK


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return
    command = payload.get("tool_input", {}).get("command", "")
    if not command.strip():
        return

    # 4 + 3: nothing this hook cannot resolve on its own.
    if UNEXPANDED.search(command) or ".." in command:
        return
    # 5: commands whose blast radius is not the filesystem.
    if DENY_WORDS.search(command):
        return

    paths = ABS_PATH.findall(command)
    # 1 + 2: at least one sandbox path, and every absolute path accounted for.
    if not any(sandboxed(p) for p in paths):
        return
    if not all(safe(p) for p in paths):
        return

    # 6: `git` with no `-C` reads whichever repo the cwd happens to be, sandbox paths or not.
    if GIT_CALL.search(command):
        targets = re.findall(r"-C\s+(\S+)", command)
        if not targets or not all(sandboxed(t.strip("'\"")) for t in targets):
            return

    # 7: a write target need not be absolute, so rules 1-2 never saw it.
    if not all(writable(t) for t in REDIRECT.findall(command)):
        return
    for m in TEE.finditer(command):
        if not all(writable(t) for t in m.group(1).split() if not t.startswith("-")):
            return

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "scratchpad-only: every path is inside the disposable session sandbox",
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - a convenience hook must never become a blocker.
        pass
    sys.exit(0)
