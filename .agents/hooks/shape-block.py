#!/usr/bin/env python3
"""PreToolUse hook: refuse the two command shapes that cost the operator thirteen hours (SCC-415).

⛔ THE MEASURED PROBLEM. Across the 20 newest Claude sessions (10,527 Bash calls) the operator
spent 15 hours waiting on calls that were sandboxed, matched an allow rule, hit no sandbox
violation and were refused by nothing — and still stopped for him. Classified by SHAPE:

    heredoc  (`python3 - <<'PY' … PY`, `git commit -F - <<'MSG'`)   54 calls   7h 17m
    leading assignment  (`S=/tmp/x; python3 …`)                     40 calls   5h 44m

Thirteen of the fifteen hours are those two. `Bash(python3:*)` matches `python3` and then sees a
body it cannot judge; no rule begins with `S=`. Either way the call drops to the auto-mode
classifier, which takes 20–80 s and escalates to the operator. In the session that measured this,
`cd <abs> && …` compounds — 57 calls — never waited once, a `Write` to a file never prompted
(10 of 10), and `python3 <file>` never waited: so the reshape is free and the shapes are the cost.

Three earlier diagnoses were wrong and are recorded so nobody repeats them: it is NOT the sandbox
escalation gate (`/sandbox` fixes none of these), NOT `sandbox.excludedCommands` (that removes a
command from the sandbox and so LOSES the auto-approval — the opposite of the fix), and NOT the
stale "run git with the sandbox off" memory note (real, but 76 calls / 67 min).

⭐ WHY PreToolUse AND A BLOCK, NOT A NAG. `shape-guard.py` nags AFTER the command, which is the
right seat for a style rule. Here the operator's click IS the damage, and it happens before the
command runs — a nag arrives after he has already paid. Same logic that keeps `git add -A` a
PreToolUse concern (`command-shape.md` §Nag, limit 2). A deny returns to the AGENT with the
reshape; the operator is never involved. The cost is one extra model turn per bounce.

WHAT IT DECIDES, first match wins:

  1. A heredoc (`<<`) anywhere outside quotes → DENY, reason names the reshape (rule 5).
  2. A leading run of `NAME=<literal>` assignments → strip them; if what remains is ONE atom
     (no separator, no substitution) that ALREADY matches one of the operator's own allow rules on
     its own → ALLOW. The assignment adds nothing — the same "nothing new" proof
     `allow-readonly-chain.py` uses (SCC-287), and it borrows that hook's matcher rather than
     re-implementing it. A `NAME=$(…)`, a `$VAR`, a backtick, or a remainder carrying any
     separator is NOT stripped and falls through (rule 6).
  3. Anything else → silence: exit 0, no output, the normal permission flow unchanged.

⛔ IT NEVER EMITS THE ASK DECISION. An ask becomes an auto-DENY in auto mode and would strand a
headless run (see `require-push-approval.py`'s header). `test_shape_block.test_never_asks` pins
the JSON value out of this file entirely.

⛔ FAILS OPEN, always. Unparseable stdin, a missing sibling, any exception → say nothing, exit 0.
Same discipline as every hook beside it: a guard that cannot judge has learned nothing.

Canonical source: `.agents/hooks/`. Wired in `.claude/settings.json` through `run-hook.sh`,
inside the single `PreToolUse` Bash group, beside `allow-readonly-chain.py`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

RULE = ".agents/rules/command-shape.md"

# `<<` that is not part of `<<<` (a here-string) and sits OUTSIDE quotes — the quote-stripping
# happens before this is applied, so `python3 -c "print(1 << 2)"` and `grep '<<EOF'` never match.
_HEREDOC = re.compile(r"(?<!<)<<(?!<)")

# A literal value: a double-quoted string with no expansion inside, a single-quoted string, or a
# bare word carrying no separator, expansion, redirect or quote. `$` is excluded on purpose —
# `S=$TMPDIR` and `S=$(pwd)` are expansions this hook does not reason about, so they fall through.
_LITERAL = r"(?:\"[^\"$`()]*\"|'[^']*'|[^\s;&|$`()\"'<>]*)"
_ASSIGN_RUN = re.compile(r"^(?:\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*=" + _LITERAL + r"\s*;?\s*)+")

# Anything that makes the remainder MORE than one atom. `already_allowed` is a proof about one
# command string; it must never be asked about a chain.
_NOT_ONE_ATOM = re.compile(r"[;&|\n]|\$\(|`")

DENY_REASON = (
    f"{RULE} rule 5 — REFUSED before the permission gate: this call carries a heredoc (<<). "
    "The permission matcher reads only the first line, so the body falls to the auto-mode "
    "classifier and lands on the operator as a prompt — measured at 54 calls and 7h17m of his "
    "time across 20 sessions (SCC-415). Nothing ran. Reshape: write the payload with the Write "
    "tool — a script to the session scratchpad and run `python3 <that path>`; a commit message "
    "to a file and `git commit -F <file>`. Both shapes are already allowed, and a Write never "
    "prompts (measured 0 of 10)."
)

ALLOW_REASON = (
    "leading literal assignment stripped: `{rest}` already matches one of the operator's own "
    "allow rules on its own, so the assignment adds nothing "
    f"({RULE} rule 6, SCC-415; the same nothing-new proof as allow-readonly-chain)."
)


def _sibling(filename: str):
    """Load a hook that lives beside this one. Hooks are hyphenated files, not a package."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(
        filename.replace("-", "_").removesuffix(".py"), path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def has_heredoc(command: str) -> bool:
    guard = _sibling("shape-guard.py")
    return bool(_HEREDOC.search(guard.strip_quoted(command)))


def strip_leading_assignments(command: str) -> str | None:
    """The command with its leading literal assignments removed, or None when there were none."""
    m = _ASSIGN_RUN.match(command)
    if not m:
        return None
    rest = command[m.end():].strip()
    return rest or None


def decide(command: str) -> tuple[str, str] | None:
    """('deny' | 'allow', reason) — or None, which means stay silent."""
    if has_heredoc(command):
        return "deny", DENY_REASON
    rest = strip_leading_assignments(command)
    if rest and not _NOT_ONE_ATOM.search(rest):
        chain = _sibling("allow-readonly-chain.py")
        if chain.already_allowed(rest):
            return "allow", ALLOW_REASON.format(rest=rest[:80])
    return None


def main() -> int:
    try:
        event = json.loads(sys.stdin.read())
        if event.get("tool_name") != "Bash":
            return 0
        command = (event.get("tool_input") or {}).get("command") or ""
        if not isinstance(command, str) or not command.strip():
            return 0
        verdict = decide(command)
        if verdict is None:
            return 0
        decision, reason = verdict
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }}))
    except Exception:  # noqa: BLE001 — a guard that cannot judge says nothing.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
