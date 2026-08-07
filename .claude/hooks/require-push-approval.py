#!/usr/bin/env python3
"""PreToolUse hook: protected-branch write gate.

Two jobs, both `permissionDecision=ask` (never a hard block — Daniel can always wave one through):

  1. `git push` targeting main (however wrapped in loops/functions/&&/subshells).
     Pushes to the agent's own claude/*, epic/*, or chore/* branch pass straight through.
  2. `git commit` attempted while HEAD is main — i.e. in the SHARED checkout rather than on a
     branch. That is the move that bundles four teams' uncommitted files into one commit; under
     `worktree-per-story.md` the agent should be on a claude/* (or epic/chore) branch instead.

Fails OPEN: if HEAD cannot be resolved (not a repo, git missing, detached), the call is allowed.
This hook only ever sees the AGENT's Bash tool — Daniel's own terminal is never affected.

Canonical source: `.agents/hooks/`. Deployed to each workspace's `.claude/hooks/` — never hand-edit
the `.claude/hooks/` copy; edit here and re-deploy."""
import json, re, subprocess, sys

PROTECTED = ("main",)  # whole-token match below, so epic/main-fix or claude/maintenance never trip it


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
command = (data.get("tool_input") or {}).get("command", "")
cwd = data.get("cwd") or None


def targeted_protected_branch(cmd):
    # whole-token match: not flanked by branch-name chars, so `claude/main-fix` and `epic/main-page`
    # do NOT trip it, while `origin main`, `HEAD:main`, `foo:main`, `... main; done` all do.
    bc = r"[A-Za-z0-9/_.-]"
    for name in PROTECTED:
        if re.search(r"(?<!" + bc + r")" + re.escape(name) + r"(?!" + bc + r")", cmd):
            return name
    return None


def head_branch():
    """Current branch name, or None if it can't be resolved (fail open)."""
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                           cwd=cwd, capture_output=True, text=True, timeout=5)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    name = r.stdout.strip()
    return name or None


# 1 — pushes aimed at an owner branch
if re.search(r"\bgit\s+push\b", command):
    hit = targeted_protected_branch(command)
    if hit:
        ask(f"This git push targets `{hit}` — live production — and needs your per-push approval. "
            "Pushes to the agent's own claude/*, epic/*, or chore/* branch run free; only main is "
            "gated. Catches `git push` however it's wrapped.")

# 2 — commits attempted outside a worktree, on an owner branch
if re.search(r"\bgit\s+commit\b", command):
    head = head_branch()
    if head in PROTECTED:
        ask(f"This `git commit` would land directly on `{head}` — live production AND the shared "
            "checkout, where other teams' uncommitted work is sitting. Work belongs on a branch: a "
            "claude/* story worktree, the epic branch, or a chore/* branch merged back with sign-off. "
            "Approve only if you mean it.")

sys.exit(0)
