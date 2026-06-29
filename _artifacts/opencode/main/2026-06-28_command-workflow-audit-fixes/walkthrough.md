# Walkthrough — Command/workflow audit follow-up fixes

**Date:** 2026-06-28  
**Workspace:** Sudo_Hatter_Command home base  
**Session type:** System / cross-project work  
**Artifact folder:** `_artifacts/opencode/main/2026-06-28_command-workflow-audit-fixes/`

## What changed & why

Daniel asked for an audit of the command/workflow setup in the home base, plus constructive criticism and verification that the commands work. The audit surfaced a strong, self-consistent propagation pipeline, but several concrete issues. Daniel elected to keep the actual `Projects/` folder names as-is (they match the git repos) and fix the surrounding references and tooling.

### Changes made

1. **`router.md`** — updated the four converted project paths to match the real `Projects/` folder names:
   - `Projects/aviationChat-AGY/` → `Projects/AGY_AVIATIONCHAT/`
   - `Projects/clean-bmad-workspace/` → `Projects/Fresh_Workspace_BMAD/`
   - `Projects/ingestion-Pipeline-AC/` → `Projects/Ingestion_pipeline_AvCh/`
   - `Projects/openCode/` → `Projects/OpenCode/`

2. **`.gitignore`** — removed the seven stale root-level project ignores (`/aviationChat-AGY/`, `/fresh-workspace-bmad/`, `/jetChat-AGY/`, `/B&L WorldWide/`, `/NEXGen Films/`, `/ingestion-Pipeline-AAvCh/`, `/openCode/`). All projects now live under `Projects/` (already ignored).

3. **`.agents/commands/INDEX.md`** — added `platforms: []` frontmatter so the index doc stops registering as an invocable `/INDEX` command across Claude, opencode, and Antigravity.

4. **`.agents/commands/slash_command_updating.md`** — corrected the command count from "36" to "37" and added a `-WhatIf` preview example.

5. **`.agents/commands/sync-agents.md`** — documented the new `-WhatIf` / `-DryRun` switch.

6. **`.agents/scripts/sync-agents.ps1`** — added preview mode:
   - New `[Alias('DryRun')][switch]$WhatIf` parameter, passed through to all sync helpers.
   - All file copies, directory creates, and deletions now print `WHATIF:` messages instead of mutating disk when the switch is set.
   - `Get-CommandPlatforms` now honors an explicit `platforms: []` as "nowhere" while still treating missing frontmatter as universal.
   - Fixed the `WHATIF:` message for `Sync-Dir` so it prints the destination path, not `System.Object[]`.

7. **`.agents/commands/1_update-maps.md`** — clarified that `--dry-run` is an agent-level stop-after-report signal, not a flag for `check_maps.py` (the script does not accept it).

8. **Instruction fixes for opencode artifact placement:**
   - **`AGENTS.md` §5 + §7** — made the opencode namespace rule explicit: opencode home-base artifacts go to `_artifacts/opencode/_main/` (or `opencode/<project>/`), never directly to `_artifacts/_main/`.
   - **`.agents/rules/artifacts-always-first.md`** — same clarification at the top of the artifact-location instructions, plus updated project-folder examples.

### Sync propagation
Ran `/sync-agents` after the command/script edits. Verified the mirrored copies updated:

```text
sync-agents: .claude\commands   -> 37 cmds
sync-agents: .opencode\commands -> 33 cmds
sync-agents: opencode global -> 33 cmds
sync-agents: antigravity global -> 32 cmds
```

`INDEX.md` was deleted from `.claude/commands/`, `.opencode/commands/`, `~/.config/opencode/commands/`, and `~/.gemini/antigravity/global_workflows/` because of the new `platforms: []` frontmatter.

## Live verification output

### Syntax check of sync-agents.ps1
```text
syntax OK
```

### `/sync-agents -WhatIf` preview
Preview mode ran cleanly and reported would-copy/would-delete actions for every surface without touching disk.

### Global-cache alias preview (`slash_command_updating -WhatIf`)
```text
& ".agents\scripts\sync-agents.ps1" -GlobalsOnly -WhatIf
sync-agents: opencode global -> 33 cmds
sync-agents: antigravity global -> 32 cmds
```

### `/bmad-help` smoke test
```text
bmad-help skill reachable
```

### `/1_update-maps` smoke test
Ran the underlying fan-out linter:

```text
python .agents\scripts\check_maps.py --all
FAN-OUT COMPLETE - 4 workspace(s) linted, 1 skipped
```

The linter correctly resolved the renamed project folders (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, `Ingestion_pipeline_AvCh`) and skipped `OpenCode` because it has no `AGENTS.md`. `Ingestion_pipeline_AvCh/` is flagged as non-conformant, which is expected for a pending project.

### Final diff summary
```text
 18 files changed, 148 insertions(+), 351 deletions(-)
```

`.claude/commands/INDEX.md` and `.opencode/commands/INDEX.md` are deleted. The only deletion outside our scope is `_my_resources/open_tasks/testing_strategy_e2e.md` (233 lines), which was already removed before this session started.

## Out of scope / still open

- **`.opencode/node_modules/`** — the 52 MB `node_modules` tree under `.opencode/` is still on disk. Daniel asked for clarification before deleting; I held off since it is correctly ignored by `.gitignore`/`.opencode/.gitignore`.
- **`1_update-maps --dry-run`** — the command doc now says `--dry-run` stops the agent before edits, but the underlying `check_maps.py` script does not accept a `--dry-run` flag. The read-mode default behavior is safe; a future cleanup could add native `--dry-run` support to the script.
- **Pending projects** (`jetChat-AGY`, `B&L WorldWide`, `NEXGen Films`) stay in `router.md` as pending and are not yet scaffolded in `Projects/`.

## Task Checklist

- [x] Create `implementation_plan.md` and get Daniel's approval on the fix list
- [x] Update `router.md` project paths to actual `Projects/` folder names
- [x] Clean stale root-level entries from `.gitignore`
- [x] Add `platforms: []` frontmatter to `.agents/commands/INDEX.md`
- [x] Update `slash_command_updating.md` command count and add `-WhatIf` example
- [x] Add `-WhatIf` / `-DryRun` preview mode to `sync-agents.ps1`
- [x] Document `-WhatIf` in `.agents/commands/sync-agents.md`
- [x] Clarify `--dry-run` behavior in `.agents/commands/1_update-maps.md`
- [x] Re-sync commands/skills/agents into `.claude/`, `.opencode/`, and global caches
- [x] Run live smoke tests (`sync-agents -WhatIf`, globals-only `-WhatIf`, `bmad-help` reachability, `check_maps --all`)
- [x] Update `AGENTS.md` and `.agents/rules/artifacts-always-first.md` to direct opencode artifacts to `_artifacts/opencode/_main/`
- [ ] Decide whether to delete `.opencode/node_modules/` and remove it if approved
- [ ] `git add / commit / push` the lobby changes (see Your Actions)

## Your Actions

All changes are uncommitted in the lobby repo. Review the diff, then commit on the appropriate branch (`main_debug` per `git-policy.md`) and push:

```powershell
cd C:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command
git add router.md .gitignore AGENTS.md .agents/commands/1_update-maps.md .agents/commands/INDEX.md .agents/commands/slash_command_updating.md .agents/commands/sync-agents.md .agents/rules/artifacts-always-first.md .agents/scripts/sync-agents.ps1
git commit -m "chore(home-base): align router/gitignore to real project folders, add sync -WhatIf, hide INDEX from command palette" -m "- router.md now points to Projects/AGY_AVIATIONCHAT, Fresh_Workspace_BMAD, Ingestion_pipeline_AvCh, OpenCode" -m "- .gitignore retired stale root-level project entries" -m "- .agents/commands/INDEX.md excluded via platforms: []" -m "- slash_command_updating count fixed (37) and documents -WhatIf" -m "- sync-agents.ps1 gains -WhatIf/-DryRun preview mode" -m "- AGENTS.md + artifacts-always-first.md: opencode artifacts go to _artifacts/opencode/_main/"
git push origin main_debug
```

After pushing, **restart opencode** so the refreshed global command caches are picked up in other projects.
