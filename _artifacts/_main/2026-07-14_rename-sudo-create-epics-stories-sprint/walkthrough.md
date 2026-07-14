---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — Rename /sudo-create-epics-stories-sprint to /sudo-write-epics-stories-sprint"
  type: walkthrough
  date: 2026-07-14
---

# Walkthrough — Rename /sudo-create-epics-stories-sprint to /sudo-write-epics-stories-sprint

The task to rename the epic kickoff command/workflow `/sudo-create-epics-stories-sprint` to `/sudo-write-epics-stories-sprint` has been fully executed across all surfaces and workspaces.

## Changes Made & Rationale

1. **Master Command & Skill (Lobby)**:
   - Created the new command file [.agents/commands/sudo-write-epics-stories-sprint.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-write-epics-stories-sprint.md) and skill folder [.agents/skills/sudo-write-epics-stories-sprint/](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/skills/sudo-write-epics-stories-sprint/SKILL.md).
   - Deleted the old master command `.agents/commands/sudo-create-epics-stories-sprint.md` and skill folder `.agents/skills/sudo-create-epics-stories-sprint/`.
   - Updated the commands catalog [.agents/commands/INDEX.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/INDEX.md).

2. **Lobby Documentation**:
   - Replaced all references in the workflow testing guide [_my_resources/diagrams_guides/workflows_tea_testing/sudo_workflows_testing.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/_my_resources/diagrams_guides/workflows_tea_testing/sudo_workflows_testing.md).

3. **AviationChat Project Documentation**:
   - Replaced historical and status references in `Projects/AGY_AVIATIONCHAT`:
     - [epics.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/planning-artifacts/epics.md)
     - [sprint-status.yaml](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml)
     - [sprint-dependency-map.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_my_resources/Open_Tasks/sprint-dependency-map.md)

4. **Clean-Up & Synchronization**:
   - Manually cleaned up old `sudo-create-epics-stories-sprint` files in Lobby, `Projects/AGY_AVIATIONCHAT`, and `Projects/Fresh_Workspace_BMAD`.
   - Ran `sync-agents.ps1` for the Lobby to update local folders and global caches (opencode global, Antigravity global, Codex prompts, Codex skills).
   - Ran `sync-agents.ps1` targeting both projects to vendor the new master `.agents` toolkit and update their local tool dirs.

## Task Checklist

- [x] Rename master command file `.agents/commands/sudo-create-epics-stories-sprint.md` to `sudo-write-epics-stories-sprint.md` and edit content references
- [x] Rename master skill folder `.agents/skills/sudo-create-epics-stories-sprint/` to `sudo-write-epics-stories-sprint/` and edit `SKILL.md`
- [x] Update reference in commands catalog `.agents/commands/INDEX.md`
- [x] Update references in `_my_resources/diagrams_guides/workflows_tea_testing/sudo_workflows_testing.md`
- [x] Update references in `Projects/AGY_AVIATIONCHAT/` logs/status files (`sprint-dependency-map.md`, `epics.md`, `sprint-status.yaml`)
- [x] Perform clean deletion of old `sudo-create-epics-stories-sprint` files in all 3 workspaces (Lobby, AviationChat, Fresh_Workspace_BMAD)
- [x] Run sync script for the lobby, AviationChat, and Fresh_Workspace_BMAD
- [x] Verify execution and outputs in all locations

## Your Actions

To finalize the changes, please run the following commit commands in each of your workspaces:

### 1. Lobby Workspace (`Sudo_Hatter_Command`)
```bash
git add .agents/commands/INDEX.md .agents/commands/sudo-create-epics-stories-sprint.md .agents/commands/sudo-write-epics-stories-sprint.md .agents/skills/sudo-create-epics-stories-sprint/ .agents/skills/sudo-write-epics-stories-sprint/ .agents/workflows/sudo-create-epics-stories-sprint.md .agents/workflows/sudo-write-epics-stories-sprint.md .claude/skills/sudo-create-epics-stories-sprint/ .claude/skills/sudo-write-epics-stories-sprint/ .opencode/commands/sudo-create-epics-stories-sprint.md .opencode/commands/sudo-write-epics-stories-sprint.md _my_resources/diagrams_guides/workflows_tea_testing/sudo_workflows_testing.md
git commit -m "chore(agents): rename /sudo-create-epics-stories-sprint to /sudo-write-epics-stories-sprint"
```

### 2. AviationChat Workspace (`Projects/AGY_AVIATIONCHAT`)
```bash
git -C Projects/AGY_AVIATIONCHAT add .agents/commands/INDEX.md .agents/commands/sudo-create-epics-stories-sprint.md .agents/commands/sudo-write-epics-stories-sprint.md .agents/skills/sudo-create-epics-stories-sprint/ .agents/skills/sudo-write-epics-stories-sprint/ .agents/workflows/sudo-create-epics-stories-sprint.md .agents/workflows/sudo-write-epics-stories-sprint.md .claude/skills/sudo-create-epics-stories-sprint/ .claude/skills/sudo-write-epics-stories-sprint/ .opencode/commands/sudo-create-epics-stories-sprint.md .opencode/commands/sudo-write-epics-stories-sprint.md _bmad-output/implementation-artifacts/sprint-status.yaml _bmad-output/planning-artifacts/epics.md _my_resources/open_tasks/sprint-dependency-map.md
git -C Projects/AGY_AVIATIONCHAT commit -m "chore(agents): sync /sudo-write-epics-stories-sprint rename from master lobby"
```

### 3. Fresh Workspace (`Projects/Fresh_Workspace_BMAD`)
```bash
git -C Projects/Fresh_Workspace_BMAD add .agents/commands/INDEX.md .agents/commands/sudo-create-epics-stories-sprint.md .agents/commands/sudo-write-epics-stories-sprint.md .agents/skills/sudo-create-epics-stories-sprint/ .agents/skills/sudo-write-epics-stories-sprint/ .agents/workflows/sudo-create-epics-stories-sprint.md .agents/workflows/sudo-write-epics-stories-sprint.md .claude/skills/sudo-create-epics-stories-sprint/ .claude/skills/sudo-write-epics-stories-sprint/ .opencode/commands/sudo-create-epics-stories-sprint.md .opencode/commands/sudo-write-epics-stories-sprint.md
git -C Projects/Fresh_Workspace_BMAD commit -m "chore(agents): sync /sudo-write-epics-stories-sprint rename from master lobby"
```

> [!NOTE]
> Please restart `opencode` after committing to allow the updated global command caches to be reloaded correctly.
