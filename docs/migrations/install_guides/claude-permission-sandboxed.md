# Claude Code Permissions & Sandbox in Git Worktrees

Reference guide for configuring Claude Code permissions, OS sandboxing, PreToolUse escape guards, and git worktree asset linking on Mac and PC.

## Overview

When Claude Code executes inside a Git worktree (`.claude/worktrees/*`), it looks for its configuration within that worktree directory. Because local settings are machine-specific and gitignored, they must be linked into each worktree so the agent inherits all approved permissions and sandbox policies without prompting.

---

## Architecture & Configuration

### 1. Settings Hierarchy

1. **User Global (`~/.claude/settings.json`)**: Machine-level fallback configuration (`sandbox.enabled: true`).
2. **Project Tracked (`.claude/settings.json`)**: Committed git settings (hooks, worktree base ref, ask rules).
3. **Project Local (`.claude/settings.local.json`)**: Gitignored machine settings containing:
   - `sandbox.enabled: true`
   - `sandbox.autoAllowBashIfSandboxed: true`
   - `sandbox.filesystem.allowWrite: [...]`
   - `permissions.allow: [...]` (Approved command patterns)

> [!IMPORTANT]
> Both the lobby (`Sudo_Hatter_Command/.claude/settings.local.json`) and individual project repositories (e.g. `Projects/AGY_AVIATIONCHAT/.claude/settings.local.json`) must carry local settings with `sandbox.enabled: true` and `autoAllowBashIfSandboxed: true`. If disabled locally, local settings override the global config and disable sandbox auto-approval.

### 2. Worktree Asset Linking

[`link-worktree-assets.py`](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/link-worktree-assets.py) automatically symlinks runtime assets into each newly created worktree:

```python
ASSETS = [
    ("node_modules", "dir"),
    ("auth_keys", "dir"),
    (".venv", "dir"),
    (".env", "file"),
    (".env.local", "file"),
    ("settings.local.json", "file"),
    ("scratchpad-root", "file"),
]
```

### 3. PreToolUse Escape Guard & Scratchpad Resolution

The [`guard-cwd-escape.py`](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/hooks/guard-cwd-escape.py) hook guards against `cd` commands that leave the workspace (which causes Claude's shell cwd to reset to the primary repo root). 

To prevent false-positive approval prompts during test harness and verification runs:
- On **macOS**: The hook recognizes the session's scratchpad root `/(?:private/)?tmp/claude-<uid>/` as safe.
- On **PC / Windows**: The hook reads the machine-local `.claude/scratchpad-root` file or Windows temp configuration.
- Generic directory escapes (`cd /tmp`, `cd ~`, `cd ../other-repo`) remain strictly guarded and require confirmation.

### 4. Direct `.agents/hooks` Execution (SCC-300)

Claude Code settings in `.claude/settings.json` execute hooks directly from `.agents/hooks/` through `run-hook.sh` (e.g. `sh "$CLAUDE_PROJECT_DIR/.agents/hooks/run-hook.sh" .agents/hooks/guard-cwd-escape.py`). The duplicate `.claude/hooks/` directory is retired and untracked from git, ensuring git merges involving hook changes are never denied by the OS sandbox.

### 5. Sandbox Filesystem Boundaries

Ensure `/tmp` and `/private/tmp` are explicitly allowed in `sandbox.filesystem.allowWrite` along with the project and worktree paths:

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": [
        "c:/Sudo_Hatter_Command",
        "c:/Sudo_Hatter_Command/.claude/worktrees",
        "c:/Sudo_Hatter_Command/.git",
        "c:/Sudo_Hatter_Command/Projects",
        "C:/Users/dlohn/AppData/Local/Temp",
        "C:/Users/dlohn/AppData/Local/Temp/claude",
        "/c/Sudo_Hatter_Command",
        "/c/Sudo_Hatter_Command/.claude/worktrees",
        "/c/Sudo_Hatter_Command/.git",
        "/c/Sudo_Hatter_Command/Projects",
        "/c/Users/dlohn/AppData/Local/Temp",
        "/c/Users/dlohn/AppData/Local/Temp/claude",
        "/tmp",
        "/private/tmp"
      ]
    }
  }
}
```

### 6. Project Scaffolding & Initializing Local Permissions

Because `.claude/settings.local.json` is machine-local and gitignored, cloning a repository from GitHub leaves `.claude/settings.local.json` absent. Without this file in the project root:
1. `link-worktree-assets.py` finds no `settings.local.json` to link into newly opened `.claude/worktrees/*` directories.
2. In both Claude Code and Antigravity/Gemini IDE, tool invocations inside worktrees fail prefix matching and trigger repetitive manual approval prompts.

#### The Canonical Tool Allowlist

Every project's `.claude/settings.local.json` (and `sudo-project-skeleton/.claude/settings.local.json.example-{pc,mac}`) must include the full standard toolchain:

```json
{
  "permissions": {
    "allow": [
      "Bash(cat:*)",
      "Bash(cd:*)",
      "Bash(echo:*)",
      "Bash(git:*)",
      "Bash(ls:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(grep:*)",
      "Bash(rg:*)",
      "Bash(find:*)",
      "Bash(sort:*)",
      "Bash(uniq:*)",
      "Bash(cut:*)",
      "Bash(wc:*)",
      "Bash(tr:*)",
      "Bash(sed:*)",
      "Bash(diff:*)",
      "Bash(cmp:*)",
      "Bash(stat:*)",
      "Bash(file:*)",
      "Bash(du:*)",
      "Bash(df:*)",
      "Bash(basename:*)",
      "Bash(dirname:*)",
      "Bash(readlink:*)",
      "Bash(which:*)",
      "Bash(date:*)",
      "Bash(pwd:*)",
      "Bash(printf:*)",
      "Bash(python:*)",
      "Bash(python3:*)",
      "Bash(python.exe:*)",
      "Bash(.venv/Scripts/python:*)",
      "Bash(.venv/Scripts/python.exe:*)",
      "Bash(acli:*)",
      "Bash(node:*)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(cargo:*)",
      "Bash(cargo.exe:*)",
      "Bash(rustc:*)",
      "Bash(rustc.exe:*)",
      "Bash(pytest:*)",
      "Bash(pytest.exe:*)",
      "Bash(pwsh:*)",
      "Bash(powershell:*)",
      "Bash(powershell.exe:*)"
    ]
  }
}
```

#### Automated Initialization During Scaffolding

`.agents/scripts/new-project.ps1` (and `/smh-new-project`) automatically seeds `.claude/settings.local.json` when cloning `sudo-project-skeleton` by copying the appropriate OS template (`settings.local.json.example-pc` or `settings.local.json.example-mac`) and configuring the project's own write boundaries.

---

## Verification

To verify that the asset linker correctly mounts and unlinks local Claude settings:

```bash
python3 .agents/scripts/tests/test_link_worktree_assets.py --on-main
```

To verify that the workspace escape guard allows scratchpad commands while blocking illegal escapes:

```bash
python3 .agents/scripts/tests/test_cwd_escape_hook.py --on-main
```
