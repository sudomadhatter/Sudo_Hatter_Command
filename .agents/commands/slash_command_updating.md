---
description: Refresh the machine-global command caches (Antigravity global_workflows + opencode global commands) from the canonical master. Thin alias for `/sync-agents -GlobalsOnly`; purges ghosts, preserves bmad-*.
---

# /slash_command_updating — refresh the global command caches

**This is now a thin alias.** The global caches are refreshed by the one unified engine, `sync-agents.ps1`
(see `/sync-agents`). This command runs the **globals-only** pass — the canonical `.agents/commands/` set
(the same canonical command set Claude uses) is mirror-synced into:

- `~/.gemini/antigravity/global_workflows` (Antigravity calls our commands "workflows")
- `~/.config/opencode/commands`

Mirror-exact: stale ghosts are purged, `bmad-*` (BMAD's own global install) is preserved, and per-command
`platforms:` frontmatter is honored (a claude-only command is not pushed to the gemini/opencode caches).

## Run (PowerShell)

```powershell
& ".agents/scripts/sync-agents.ps1" -GlobalsOnly
```

Preview the global refresh without touching disk:

```powershell
& ".agents/scripts/sync-agents.ps1" -GlobalsOnly -WhatIf
```

**Notes:**
- Writing to `~/.config/opencode/**` and `~/.gemini/antigravity/**` may trigger an `external_directory: ask`
  prompt under opencode/Antigravity — confirm it.
- After running, **restart opencode** so the refreshed global config + commands are picked up in other projects.
- Prefer plain `/sync-agents` (no args) when you also want the lobby's local `.claude/`/`.opencode/` dirs
  refreshed in the same pass — it does both the locals and the globals.

Optional additional input: $ARGUMENTS
