# Claude Code Permissions & Sandbox in Git Worktrees

Reference guide for configuring Claude Code permissions, OS sandboxing, and git worktree asset linking.

## Overview

When Claude Code executes inside a Git worktree (`.claude/worktrees/*`), it looks for its configuration within that worktree directory. Because local settings are machine-specific and gitignored, they must be linked into each worktree so the agent inherits all approved permissions and sandbox policies.

---

## Architecture & Configuration

### 1. Settings Hierarchy

1. **User Global (`~/.claude/settings.json`)**: Machine-level fallback configuration.
2. **Project Tracked (`.claude/settings.json`)**: Committed git settings (hooks, worktree base ref, ask rules).
3. **Project Local (`.claude/settings.local.json`)**: Gitignored machine settings containing:
   - `sandbox.enabled: true`
   - `sandbox.autoAllowBashIfSandboxed: true`
   - `sandbox.filesystem.allowWrite: [...]`
   - `permissions.allow: [...]` (80+ approved command patterns)

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

### 3. Sandbox Filesystem Boundaries

To prevent permission prompts during diff analysis and code review commands (e.g. `/smh-code-review`), ensure `/tmp` and `/private/tmp` are explicitly allowed in `sandbox.filesystem.allowWrite`:

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": [
        "/Users/sudohatter/Sudo_Hatter_Command",
        "/Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees",
        "/Users/sudohatter/Sudo_Hatter_Command/.git",
        "/Users/sudohatter/Sudo_Hatter_Command/Projects",
        "/tmp",
        "/private/tmp"
      ]
    }
  }
}
```

---

## Verification

To verify that the asset linker correctly mounts and unlinks local Claude settings:

```bash
python3 .agents/scripts/tests/test_link_worktree_assets.py --on-main
```

