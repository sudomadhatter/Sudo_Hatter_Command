#!/usr/bin/env python3
"""PostToolUse hook: nag an agent back to close-out law when a push/PR fails or main is targeted (SCC-381).

The measured problem: agents reach the end of a session and forget the close-out rules, attempting to
push directly to `main` or getting stranded when a push or pull request fails. The operator's ruling
(SCC-381): add a nag that tells agents what to go read and the exact door command to run when the PR
or push fails or when `main` is targeted.

⭐ WHY PostToolUse AND NOT PreToolUse.
  `PostToolUse` -> `hookSpecificOutput.additionalContext` REACHES the model verbatim.
  PreToolUse `permissionDecisionReason` and stderr do NOT reach the model cleanly.
  PostToolUse runs after the command, so it never blocks or wedges a headless session.

⛔ IT MUST NEVER BLOCK (tested in test_closeout_nag.py).
  Emits no `decision: "block"` and no `permissionDecision`.
  Fails open on unparseable stdin or any exception (exit 0).

Canonical source: `.agents/hooks/`. Deployed to `.claude/hooks/` — never hand-edit the copy.
"""
from __future__ import annotations

import json
import re
import sys

RULE_GIT_POLICY = ".agents/rules/git-policy.md"
SOP_DOC = "docs/_scc_sops_prds/workflows_testing_SOP.md"
QUICKREF_DOC = "docs/_scc_sops_prds/operator_workflows_quickref.md"

PROTECTED = ("main",)
GIT_OPTS = r"(?:\s+(?:-C\s+(?:'[^']*'|\"[^\"]*\"|\S+)|-c\s+\S+|--?[A-Za-z][\w-]*(?:=\S+)?))*"
GIT_CALL = r"\bgit" + GIT_OPTS + r"\s+"

FAIL_KEYWORDS = re.compile(
    r"(refused|rejected|failed to push|remote rejected|pre-push hook declined|"
    r"PUSH TO main REFUSED|permissionDecisionReason|already exists|"
    r"could not create pull request|pull request create failed|fatal:\s+|error:\s+failed)",
    re.IGNORECASE,
)


def strip_heredocs(text: str) -> str:
    """A heredoc BODY is data, not commands."""
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
    """(start, end) of every quoted run."""
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
    """A quoted string is an argument, not a command."""
    out = list(text)
    for start, end in quoted_spans(text):
        for i in range(start + 1, end):
            out[i] = " "
    return "".join(out)


def targets_main(cmd: str) -> bool:
    """True if cmd is a git push targeting main."""
    bc = r"[A-Za-z0-9/_.-]"
    for name in PROTECTED:
        if re.search(r"(?<!" + bc + r")" + re.escape(name) + r"(?!" + bc + r")", cmd):
            return True
    return False


def is_checkout_or_merge_to_main(clean_cmd: str) -> bool:
    """True if attempting to checkout or merge directly onto main outside sanctioned flows."""
    if re.search(r"\bgit\s+(checkout|switch)\s+main\b", clean_cmd):
        # A read-only checkout or merge into main
        return True
    if re.search(r"\bgit\s+merge\b.*?\bmain\b", clean_cmd):
        return True
    return False


def detect_violation(command: str, tool_response: dict | str | None) -> list[str]:
    """Detect if command violates close-out protocol or suffered a push/PR failure."""
    heredocs_gone = strip_heredocs(command)
    clean = strip_quoted(heredocs_gone)

    reasons: list[str] = []

    # 1. Did the command attempt a git push targeting main?
    is_git_push = bool(re.search(GIT_CALL + r"push\b", clean))
    if is_git_push and targets_main(clean):
        reasons.append("you attempted `git push` targeting `main`. Agents NEVER push directly to `main`.")

    # 2. Did the command attempt git checkout/merge onto main directly?
    elif is_checkout_or_merge_to_main(clean):
        reasons.append("you attempted to checkout or merge directly onto `main`. Do not land commits directly on `main`.")

    # 3. Did a git push or gh pr create FAIL?
    is_gh_pr_create = bool(re.search(r"\bgh\s+pr\s+create\b", clean))
    if is_git_push or is_gh_pr_create:
        has_failed = False
        resp_text = ""
        if isinstance(tool_response, dict):
            # Check exit codes
            for code_key in ("exit_code", "returncode", "exitCode"):
                code = tool_response.get(code_key)
                if code is not None and code != 0:
                    has_failed = True
                    break
            stdout = tool_response.get("stdout", "") or ""
            stderr = tool_response.get("stderr", "") or ""
            resp_text = f"{stdout}\n{stderr}"
        elif isinstance(tool_response, str):
            resp_text = tool_response

        if not has_failed and resp_text and FAIL_KEYWORDS.search(resp_text):
            has_failed = True

        if has_failed and not reasons:
            action = "git push" if is_git_push else "gh pr create"
            reasons.append(f"your `{action}` command failed or was refused.")

    return reasons


def generate_nag(reasons: list[str]) -> str:
    lead = " • " + "\n • ".join(reasons)
    return (
        f"close-out procedure check (SCC-381) —\n{lead}\n\n"
        f"Standing law on every platform ({RULE_GIT_POLICY}):\n"
        f" • AGENTS NEVER PUSH DIRECTLY TO `main`. `main` is reached only through a GitHub Pull Request "
        f"(for Task work) or /cicd-push-e2e with an operator sign-off token (for Epics).\n"
        f" • Task work (`chore/<KEY>-<slug>`):\n"
        f"   1. Ensure branch is clean and pushed: `git push -u origin chore/<KEY>-<slug>`\n"
        f"   2. Reconcile `walkthrough.md` `## Your Actions` (- [x] The merge itself — lands via this branch's PR)\n"
        f"   3. Tick outline locally: `python3 .agents/scripts/jira_ticket.py done --local --key <KEY> ...` and commit it\n"
        f"   4. Open PR and STOP: `gh pr create --base main --head \"$BRANCH\" --fill`\n"
        f"   5. Hand the PR URL to Mr. Hatter. He clicks Merge on GitHub.\n"
        f"   6. Resume after merge: `/smh-close-task-merge-tree --after-merge <KEY>`\n"
        f" • Story work (`claude/<KEY>-<slug>`):\n"
        f"   Use `/cicd-close-story-merge-tree`. It lands on the epic branch (`epic/<KEY>-<slug>`), NEVER `main`.\n"
        f" • What to go read:\n"
        f"   - {RULE_GIT_POLICY} (branch policy and write gates)\n"
        f"   - {SOP_DOC} §3 (lane lifecycles) & §10 (Complete Hooks & Nags Architecture)\n"
        f"   - {QUICKREF_DOC} (visual decision trees and rapid cheat-sheets)\n\n"
        f"The command already ran; nothing is blocked. Follow the close-out procedure for your lane."
    )


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        event = json.loads(raw)
    except Exception:
        return 0

    try:
        if event.get("tool_name") != "Bash":
            return 0
        command = (event.get("tool_input") or {}).get("command") or ""
        if not command:
            return 0
        tool_response = event.get("tool_response")

        violations = detect_violation(command, tool_response)
        if not violations:
            return 0

        nag = generate_nag(violations)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": nag,
            }
        }))
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
