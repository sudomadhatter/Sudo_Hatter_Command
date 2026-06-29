# Implementation Plan — Command/workflow audit follow-up fixes

**Date:** 2026-06-28  
**Workspace:** Sudo_Hatter_Command home base  
**Status:** approved by Daniel (per answers to clarifying questions)

## Scope
Fix the non-folder-name issues surfaced in the command/workflow audit. Project folders themselves already match the git repos; update the surrounding references instead.

## Decisions
1. `router.md` paths corrected to match actual `Projects/` folder names.
2. `.gitignore` stale root-level project entries removed (all projects now live under `Projects/`).
3. `.agents/commands/INDEX.md` excluded from the invocable command surface via `platforms: []` (industry-standard pattern: an index doc, not a slash command).
4. `slash_command_updating.md` command count corrected from 36 → 37.
5. `sync-agents.ps1` gets `-WhatIf`/`-DryRun` support so users can preview changes safely.
6. After code edits, run `/sync-agents` to propagate, then smoke-test `/bmad-help`, `/sync-agents -WhatIf`, `/slash_command_updating`, and `/1_update-maps --dry-run`.

## Files to change

| File | Change |
|---|---|
| `router.md` | Update project paths: `aviationChat-AGY` → `AGY_AVIATIONCHAT`; `clean-bmad-workspace` → `Fresh_Workspace_BMAD`; `ingestion-Pipeline-AC` → `Ingestion_pipeline_AvCh`; `openCode` → `OpenCode`. Leave pending rows as pending. |
| `.gitignore` | Remove the legacy `/aviationChat-AGY/`, `/fresh-workspace-bmad/`, `/jetChat-AGY/`, `/B&L WorldWide/`, `/NEXGen Films/`, `/ingestion-Pipeline-AAvCh/`, `/openCode/` root-level ignores. `/Projects/` already ignores all project repos. |
| `.agents/commands/INDEX.md` | Add frontmatter: `description:` + `platforms: []`. |
| `.agents/commands/slash_command_updating.md` | Update "same 36 Claude uses" to "same 37 commands". Optionally mention `-WhatIf`. |
| `.agents/scripts/sync-agents.ps1` | Add `[Alias('DryRun')][switch]$WhatIf`; pass through to sync functions; replace writes with host messages in preview mode. Update comment/synopsis. |
| `.agents/commands/sync-agents.md` | Document the new `-WhatIf` / `-DryRun` switch. |

## Verification
1. `git diff --stat` shows only the intended files changed.
2. `.agents/scripts/sync-agents.ps1` parses cleanly (`powershell -Command "Get-Command .agents/scripts/sync-agents.ps1"` or syntax check).
3. Run `& .agents/scripts/sync-agents.ps1 -WhatIf` from lobby — output should list would-copy/would-delete actions, perform zero writes.
4. Run the real `/sync-agents` (no args) and confirm `.claude/commands/INDEX.md` and `.opencode/commands/INDEX.md` also pick up the `platforms: []` frontmatter (they should still be mirrored as files, just not invocable).
5. Smoke-test `/bmad-help test`, `/slash_command_updating`, `/1_update-maps --dry-run`.

## Risks
- `sync-agents.ps1` is a shared engine; adding a new switch changes no default behavior, so risk is low.
- `platforms: []` on `INDEX.md` relies on the script honoring an empty platform list as "nowhere". The current parser returns all platforms if frontmatter is missing; I will make the script respect an explicit empty list.
- Concurrent Claude/opencode processes may hold file locks during sync; smoke tests will be run after sync completes.
