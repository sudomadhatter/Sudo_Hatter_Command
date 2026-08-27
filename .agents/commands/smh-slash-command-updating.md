---
description: Refresh the machine-global command caches (Antigravity global_workflows + opencode global commands) from the canonical master. Thin alias for `/smh-sync-agents -GlobalsOnly`; purges ghosts, preserves bmad-*.
---

# /smh-slash-command-updating — refresh the global command caches

**This is now a thin alias.** The global caches are refreshed by the one unified engine, `sync-agents.ps1`
(see `/smh-sync-agents`). This command runs the **globals-only** pass. **Each cache has its own source**
(SCC-332) — they are not two copies of one folder:

- `~/.gemini/antigravity/global_workflows` ← **`.agents/workflows/`**, the generated Antigravity door.
  Antigravity calls its invocable units "workflows" and **truncates any one over 12,000 chars instead of
  rejecting it**, so a big command must arrive as the generated thin launcher that points back at
  `.agents/commands/<name>.md`. Sourcing this cache from `commands/` bypasses that and ships cut-off bodies.
- `~/.config/opencode/commands` ← **`.agents/commands/`**, the full bodies. opencode has no size limit.

The globals pass regenerates `.agents/workflows/` first, so the cache is always mirrored from a fresh door set.
Mirror-exact: stale ghosts are purged, `bmad-*` (BMAD's own global install) is preserved, and per-file
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
- Prefer plain `/smh-sync-agents` (no args) when you also want the lobby's local `.claude/`/`.opencode/` dirs
  refreshed in the same pass — it does both the locals and the globals.

Optional additional input: $ARGUMENTS
