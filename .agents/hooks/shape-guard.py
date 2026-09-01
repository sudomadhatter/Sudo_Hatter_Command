#!/usr/bin/env python3
"""PostToolUse hook: nag an agent back to `command-shape.md` at the moment it breaks it (SCC-369).

⛔ THE MEASURED PROBLEM. `command-shape.md` was already standing law on EVERY platform — summarized
in `AGENTS.md` §6, restated in `zoo-team.md` for every Zoo seat, keyworded into `rule-trigger.py`,
and it fires as a `UserPromptSubmit` injection. It was still violated in **1,946 of 8,355 Bash calls
across 25 sessions — 23.3% of every Bash call made in the transcripts.** Of 1,247 `git -C`
invocations, 521 named a verb the allow list cannot pre-approve: every one an approval stop that
would have been silent in the `cd <abs> && git <verb>` shape the rule already mandates.

Distribution was never the gap; compliance was. So this file does not restate the law — it points
at it, once, attached to the exact command that broke it. The operator's ruling (2026-09-01): to
correct an agent that keeps deviating from a rule, add a nag, not another copy of the rule.

⭐ WHY PostToolUse AND NOT PreToolUse. Established by probe, not assumption:
  `PostToolUse` → `hookSpecificOutput.additionalContext`  REACHES the model, verbatim.
  `systemMessage` · hook stderr · `PreToolUse` allow + `permissionDecisionReason`  do NOT.
PostToolUse also runs AFTER the command, so this file cannot block, slow or wedge a headless
session no matter how wrong it is. Cost measured at ~36 ms, off the critical path.

⛔ IT MUST NEVER BLOCK, AND THAT IS TESTED (`test_shape_guard.test_never_blocks`).
`permissionDecision: "ask"` becomes an auto-DENY in auto mode (see `require-push-approval.py`'s
header) and a PostToolUse `decision: "block"` feeds an error to the model. Either would strand a
headless run over a style note. This file emits neither key, on any path.

⛔ IT ALSO CANNOT PROTECT AGAINST A DESTRUCTIVE COMMAND — it speaks after the damage. `git add -A`
and `git worktree remove --force` are deliberately NOT nagged here; they belong in a PreToolUse
guard. See `.agents/rules/command-shape.md` §Nag.

⛔ FAILS OPEN, always. Unparseable stdin, a missing key, any exception at all → say nothing, exit 0.
Same discipline as `guard-cwd-escape.py`: a guard that cannot judge has learned nothing.

Canonical source: `.agents/hooks/`. Deployed to `.claude/hooks/` — never hand-edit the copy.
"""
from __future__ import annotations

import json
import re
import sys

RULE = ".agents/rules/command-shape.md"

# A "gate" is a command whose EXIT CODE is the thing you wanted. Piping one reports the pipe's
# status instead, and `head` can SIGPIPE it mid-run.
GATE = re.compile(r"(run_all\.py|pytest|vitest|\bruff\b|\bpyrefly\b|\btsc\b|"
                  r"test_[a-z0-9_]+\.py|npm (run )?(test|lint))")


def strip_heredocs(text: str) -> str:
    """A heredoc BODY is data, not commands — counting it as commands is a false positive."""
    out: list[str] = []
    terminator: str | None = None
    for line in text.split("\n"):
        if terminator is not None:
            if line.strip() == terminator:
                terminator = None
            continue
        out.append(line)
        m = re.search(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", line)
        if m:
            terminator = m.group(1)
    return "\n".join(out)


def quoted_spans(text: str) -> list[tuple[int, int]]:
    """(start, end) of every quoted run. A `;` inside one is TEXT, not a separator.

    ⛔ Rule 2 cannot use `strip_quoted` — `$?` lives inside the quotes it would delete — so it
    needs the positions instead, to ask whether the SEPARATOR it matched was real shell syntax or
    a character inside somebody's argument (SCC-369 review: `grep -rn '; echo "EXIT=$?"' …` and
    `git commit -m "fix; echo $? was wrong"` both nagged, and rule 1 already had the control that
    rule 2 lacked).
    """
    spans: list[tuple[int, int]] = []
    i, n = 0, len(text)
    while i < n:
        if text[i] in "\"'":
            close = text.find(text[i], i + 1)
            if close == -1:
                break
            spans.append((i, close))
            i = close + 1
        else:
            i += 1
    return spans


def strip_quoted(text: str) -> str:
    """A quoted string is an ARGUMENT: `grep "git -C"` is a search, never a use.

    ⛔ ONE left-to-right pass, never two regex passes. Stripping `'…'` before `"…"` let an
    APOSTROPHE inside a double-quoted string pair with a later apostrophe and swallow everything
    between them: `echo "it's here" && git -C /repo status && echo "that's all"` went silent on a
    genuine rule-1 violation, and the scan under-counted it. Measured at 2 hidden violations in
    the live corpus (SCC-369 review). Blanks the contents in place so offsets stay usable.
    """
    out = list(text)
    for start, end in quoted_spans(text):
        for i in range(start + 1, end):
            out[i] = " "
    return "".join(out)


_ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# Words that DEFER to a later word for the real command: interpreters, runners, wrappers.
_DEFERS = re.compile(r"^(env|time|nohup|exec|command|sudo|xargs|npx|npm|pnpm|yarn|uv|poetry|"
                     r"pipenv|cargo|python3?|py|sh|bash|zsh|node|run)$")


def command_prefix(piece: str) -> str:
    """The head of a pipe piece — the command being RUN, not its arguments.

    ⛔ `sed -n '1,80p' tests/test_x.py` is a READER whose argument happens to be a gate's filename;
    `python3 tests/test_x.py` runs it. The first cut of this file matched the gate pattern anywhere
    in the piece and could not tell them apart, so reading a test file was nagged as piping a gate
    — measured at 170 of 779 rule-3 hits, 21.8%, which also inflated the published baseline the
    whole ruling rests on (SCC-369 review, two lenses independently).
    """
    words = [w for w in piece.split() if not _ENV_ASSIGN.match(w)]
    head: list[str] = []
    for w in words:
        head.append(w)
        if w.startswith("-") or _DEFERS.match(w.rsplit("/", 1)[-1]):
            continue          # a flag or a wrapper: the real command is still ahead
        break
    return " ".join(head)


def violations(command: str) -> list[str]:
    """Return one nag line per broken rule. Empty list means correctly shaped — say nothing."""
    heredocs_gone = strip_heredocs(command)
    clean = strip_quoted(heredocs_gone)
    found: list[str] = []

    # Rule 1 — the `-C` spelling. Checked on quote-stripped text so a search for the literal
    # is not mistaken for a use of it.
    if re.search(r"(^|[;&|(\s])git\s+-C\s", clean):
        found.append(
            f"{RULE} rule 1 — you used the `git -C <path>` spelling. Zoo denies it outright, and "
            f"on Claude Code only the handful of verbs with an explicit `git -C * <verb>` allow "
            f"rule get through — any other verb stops and waits for a human. "
            f"Write `cd <abs path> && git <verb> …` in ONE line instead; `git commit`, `git add`, "
            f"`git fetch`, `git push`, `git checkout` and `git worktree` are all already allowed "
            f"in that shape, on both platforms.")

    # Rule 2 — the exit-echo tail. Checked WITHOUT quote-stripping: `$?` lives inside the quotes
    # (`echo "EXIT=$?"`), so stripping them deletes the very thing being detected.
    spans = quoted_spans(heredocs_gone)
    # ⛔ A NEWLINE is a command separator too. Requiring `;` or `&&` missed every multi-line call
    # whose second line IS the echo — 225 of them in the live corpus, under-reporting rule 2 by
    # ~2.7 points against the figure this lane published as law (SCC-369 review).
    tail = re.compile(r"(;|&&|\n)[ \t]*echo\s+[^|;&\n]*\$\?")
    if any(not any(s <= m.start() <= e for s, e in spans)
           for m in tail.finditer(heredocs_gone)):
        found.append(
            f"{RULE} rule 2 — drop the `; echo \"EXIT=$?\"` tail. The tail becomes the shell's "
            f"reported status, so a DEAD GATE can exit 0 behind it. The harness already shows you "
            f"the exit code.")

    # Rule 3 — a piped gate. The gate must sit IMMEDIATELY left of a pipe; a pipe anywhere in a
    # long `&&` chain is not evidence about the gate.
    for segment in re.split(r"&&|\|\||;|\n", clean):
        parts = segment.split("|")
        if len(parts) > 1 and any(GATE.search(command_prefix(p)) for p in parts[:-1]):
            found.append(
                f"{RULE} rule 3 — you piped a gate. A pipe reports the LAST command's status, not "
                f"the gate's, and `head` can SIGPIPE it mid-run. Redirect instead: "
                f"`<gate> > out.txt 2>&1` then read the file.")
            break

    return found


def main() -> int:
    try:
        event = json.loads(sys.stdin.read())
    except Exception:
        return 0  # fails open — unparseable stdin is not a verdict about the command
    try:
        if event.get("tool_name") != "Bash":
            return 0
        command = (event.get("tool_input") or {}).get("command") or ""
        if not command:
            return 0
        found = violations(command)
        if not found:
            return 0  # silence is the correct answer for a correctly-shaped command
        body = ("command-shape check — this call broke standing law that every platform "
                "loads.\n\n" + "\n\n".join(f"• {line}" for line in found)
                + "\n\nThe command already ran; nothing is blocked. Shape the NEXT one correctly.")
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": body,
        }}))
    except Exception:
        return 0  # fails open on anything at all
    return 0


if __name__ == "__main__":
    sys.exit(main())
