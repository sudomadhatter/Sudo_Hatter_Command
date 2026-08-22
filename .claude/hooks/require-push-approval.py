#!/usr/bin/env python3
"""PreToolUse hook: protected-branch write gate.

Two jobs, both `permissionDecision=ask` (never a hard block — Daniel can always wave one through):

  1. `git push` targeting main (however wrapped in loops/functions/&&/subshells — and however the
     git invocation itself is spelled: `git push`, `git -C <path> push`, `git -c k=v push`,
     `git --no-pager push` all count). Pushes to the agent's own claude/*, epic/*, or chore/*
     branch pass straight through.
  2. `git commit` attempted while HEAD is main — i.e. in the SHARED checkout rather than on a
     branch. That is the move that bundles four teams' uncommitted files into one commit; under
     `worktree-per-story.md` the agent should be on a claude/* (or epic/chore) branch instead.
     HEAD is resolved at the repo the command actually targets: a `-C <path>` beats the session
     cwd (the F7 gap: a lobby-cwd session pushing into a project repo via `git -C`).

Fails OPEN: if HEAD cannot be resolved (not a repo, git missing, detached), the call is allowed.
This hook only ever sees the AGENT's Bash tool — Daniel's own terminal is never affected by it.

# JIRA-HOOK: ticket-state gate mounts here — the "agents cannot push until the ticket is moved"
# contract enforces at this seat (check the story's Jira status before allowing a push that lands
# on epic/* or main). Separate story; not built yet.

Canonical source: `.agents/hooks/`. Deployed to each workspace's `.claude/hooks/` — never hand-edit
the `.claude/hooks/` copy; edit here and re-deploy."""
import json, re, shlex, subprocess, sys, time

PROTECTED = ("main",)  # whole-token match below, so epic/main-fix or claude/maintenance never trip it

# A git invocation with any run of pre-subcommand options: `-C <path>` / `-c k=v` (argument-taking,
# matched WITH their argument so the subcommand test doesn't land on the argument), plus generic
# `-x` / `--long[=val]` flags. `(?i:...)` is off — git is case-sensitive. Space-separated argument
# forms of other flags (`--git-dir x`) are not chased; -C/-c cover the forms agents actually emit.
GIT_OPTS = r"(?:\s+(?:-C\s+(?:'[^']*'|\"[^\"]*\"|\S+)|-c\s+\S+|--?[A-Za-z][\w-]*(?:=\S+)?))*"
GIT_CALL = r"\bgit" + GIT_OPTS + r"\s+"


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


def effective_git_cwd(cmd):
    """The repo the git command actually targets: the first `-C <path>` if present, else the session
    cwd. Quoted paths are unwrapped via shlex; a relative -C resolves against cwd (git semantics)."""
    m = re.search(r"\bgit\s+(?:-c\s+\S+\s+|--?[A-Za-z][\w-]*(?:=\S+)?\s+)*-C\s+('[^']*'|\"[^\"]*\"|\S+)", cmd)
    if not m:
        return cwd
    raw = m.group(1)
    try:
        path = shlex.split(raw)[0] if raw else raw
    except ValueError:
        path = raw.strip("'\"")
    if not path:
        return cwd
    import os
    return path if os.path.isabs(path) else (os.path.join(cwd, path) if cwd else path)


def head_branch(at):
    """Current branch name at `at`, or None if it can't be resolved (fail open)."""
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                           cwd=at, capture_output=True, text=True, timeout=5)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    name = r.stdout.strip()
    return name or None


def fresh_token_present(at):
    """True when a valid, unexpired approval token already covers this push.

    SCC-77: `.githooks/pre-push` is now the authoritative gate, and it checks far more than this
    hook can (one-merge-only, the named branch, the exact sha). Asking again on top of it is not a
    second opinion — it is a second *prompt*, and `permissionDecision: "ask"` becomes an auto-DENY
    in auto mode. That combination strands a headless close-out with `main` merged locally, the
    push denied, and the token going stale in 30 minutes: a full re-gate to recover.

    So when the operator has already signed off (a token exists, names HEAD, and is inside its TTL)
    this layer stands down and lets the git hook do the deciding. Fails toward ASKING: any doubt,
    any error, and the prompt still fires.
    """
    try:
        common = subprocess.run(["git", "-C", at, "rev-parse", "--git-common-dir"],
                                capture_output=True, text=True, timeout=5)
        head = subprocess.run(["git", "-C", at, "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=5)
        if common.returncode != 0 or head.returncode != 0:
            return False
        base = common.stdout.strip()
        if not base.startswith("/"):
            top = subprocess.run(["git", "-C", at, "rev-parse", "--show-toplevel"],
                                 capture_output=True, text=True, timeout=5)
            if top.returncode != 0:
                return False
            base = f"{top.stdout.strip()}/{base}"
        with open(f"{base}/main-push-approval", encoding="utf-8") as fh:
            fields = dict(
                line.rstrip("\n").split("=", 1) for line in fh if "=" in line)
        if fields.get("tip") != head.stdout.strip():
            return False
        return (time.time() - int(fields["minted"])) <= 1800
    except Exception:
        return False


# 1 — pushes aimed at an owner branch (catches `git push` AND `git -C <path> push` etc.)
if re.search(GIT_CALL + r"push\b", command):
    hit = targeted_protected_branch(command)
    if hit and not fresh_token_present(effective_git_cwd(command)):
        ask(f"This git push targets `{hit}` — live production — and needs your per-push approval. "
            "Pushes to the agent's own claude/*, epic/*, or chore/* branch run free; only main is "
            "gated. Catches `git push` however it's wrapped, including `git -C <path> push`. "
            "No approval token is present: if you meant to ship, the door command "
            "(/cicd-push-e2e or /smh-close-task-merge-tree) mints one at its sign-off step.")

# 2 — commits attempted outside a worktree, on an owner branch (HEAD read at the -C target, not cwd)
if re.search(GIT_CALL + r"commit\b", command):
    head = head_branch(effective_git_cwd(command))
    if head in PROTECTED:
        ask(f"This `git commit` would land directly on `{head}` — live production AND the shared "
            "checkout, where other teams' uncommitted work is sitting. Work belongs on a branch: a "
            "claude/* story worktree, the epic branch, or a chore/* branch merged back with sign-off. "
            "Approve only if you mean it.")

sys.exit(0)
