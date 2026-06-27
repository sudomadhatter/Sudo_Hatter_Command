#!/usr/bin/env python3
"""PreToolUse hook: gate `git push` only when it targets a protected branch.
Pushes to the agent's own claude/* branch pass through; pushes to main/main_debug
(however wrapped in loops/functions/&&/subshells) force permissionDecision=ask.

Canonical source: `.agents/hooks/`. Deployed to each workspace's `.claude/hooks/` by
`/sync-agents` — never hand-edit the `.claude/hooks/` copy; edit here and re-sync."""
import json, re, sys

PROTECTED = ("main_debug", "main")  # longer name first so main_debug matches before the 'main' substring

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
command = (data.get("tool_input") or {}).get("command", "")
if not re.search(r"\bgit\s+push\b", command):
    sys.exit(0)

def targeted_protected_branch(cmd):
    # whole-token match: not flanked by branch-name chars, so `claude/main-fix` does NOT trip it,
    # while `origin main_debug`, `HEAD:main`, `foo:main_debug`, `... main_debug; done` all do.
    bc = r"[A-Za-z0-9/_.-]"
    for name in PROTECTED:
        if re.search(r"(?<!" + bc + r")" + re.escape(name) + r"(?!" + bc + r")", cmd):
            return name
    return None

hit = targeted_protected_branch(command)
if hit:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": (
            f"This git push targets `{hit}` — an owner branch — needs explicit per-push approval. "
            "Pushes to your own claude/* branch run free; only main/main_debug are gated. "
            "Catches `git push` however it's wrapped."),
    }}))
sys.exit(0)
