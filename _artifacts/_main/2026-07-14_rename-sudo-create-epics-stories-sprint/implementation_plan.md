---
IsArtifact: true
ArtifactMetadata:
  title: "Rename /sudo-create-epics-stories-sprint to /sudo-write-epics-stories-sprint"
  type: implementation_plan
  date: 2026-07-14
---

# Rename /sudo-create-epics-stories-sprint to /sudo-write-epics-stories-sprint

Rename the epic kickoff workflow `/sudo-create-epics-stories-sprint` to `/sudo-write-epics-stories-sprint` to keep the naming convention uniform across the system (aligning with `/sudo-write-story-tests`).

## User Review Required

> [!IMPORTANT]
> Since `sync-agents.ps1` is additive for local tool directories and project workspaces (to prevent deleting project-specific custom files), the old `/sudo-create-epics-stories-sprint` files and directories will not be automatically deleted there. We must explicitly delete them in all three workspaces to prevent orphaned command/skill files.

## Proposed Changes

We will group the changes into:
1. Updating the Master `.agents/` toolkit in the lobby home base.
2. Updating Lobby-level documentation.
3. Performing a clean deletion of the old command, skill, and workflow files in all three workspaces.
4. Executing `sync-agents` to propagate the new files to all platforms (Claude, opencode, Antigravity, and Codex), global caches, and the three main workspaces.

---

### Master Toolkit (Lobby)

#### [NEW] [sudo-write-epics-stories-sprint.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-write-epics-stories-sprint.md)
We will rename and create the new master command file. The contents will be identical to the original except all references to `sudo-create-epics-stories-sprint` will be replaced with `sudo-write-epics-stories-sprint`.

#### [DELETE] [sudo-create-epics-stories-sprint.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-create-epics-stories-sprint.md)
The old master command file will be deleted.

#### [NEW] [SKILL.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/skills/sudo-write-epics-stories-sprint/SKILL.md)
We will rename and create the new skill file under `.agents/skills/sudo-write-epics-stories-sprint/`. The `name` frontmatter and file contents will be updated to reference `sudo-write-epics-stories-sprint`.

#### [DELETE] [SKILL.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/skills/sudo-create-epics-stories-sprint/SKILL.md)
The old skill folder and file will be deleted.

#### [MODIFY] [INDEX.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/INDEX.md)
We will update line 27 in the commands catalog to reference `sudo-write-epics-stories-sprint` instead of `sudo-create-epics-stories-sprint`.

---

### Home-Base Documentation

#### [MODIFY] [sudo_workflows_testing.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/_my_resources/diagrams_guides/workflows_tea_testing/sudo_workflows_testing.md)
We will update all occurrences of `/sudo-create-epics-stories-sprint` to `/sudo-write-epics-stories-sprint` (including text references, tables, and Mermaid flow diagrams).

---

### Project-Specific Documentation (Optional/Consistency)

We will also update references in historical logs and documentation under `Projects/AGY_AVIATIONCHAT` for maximum consistency:

#### [MODIFY] [sprint-dependency-map.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_my_resources/Open_Tasks/sprint-dependency-map.md)
Update historical reference in update logs.

#### [MODIFY] [epics.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/planning-artifacts/epics.md)
Update historical reference in intake logs.

#### [MODIFY] [sprint-status.yaml](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml)
Update status creation comment.

---

### Clean Up & Sync Execution

We will execute the following steps to delete the old files and synchronize the new files:

1. **Delete old files in Lobby**:
   - `.agents/workflows/sudo-create-epics-stories-sprint.md` (which was a generated mirror)
   - `.claude/commands/sudo-create-epics-stories-sprint.md`
   - `.opencode/commands/sudo-create-epics-stories-sprint.md`
   - `.claude/skills/sudo-create-epics-stories-sprint/` (directory)

2. **Delete old files in AGY_AVIATIONCHAT**:
   - `Projects/AGY_AVIATIONCHAT/.agents/commands/sudo-create-epics-stories-sprint.md`
   - `Projects/AGY_AVIATIONCHAT/.agents/workflows/sudo-create-epics-stories-sprint.md`
   - `Projects/AGY_AVIATIONCHAT/.agents/skills/sudo-create-epics-stories-sprint/` (directory)
   - `Projects/AGY_AVIATIONCHAT/.claude/commands/sudo-create-epics-stories-sprint.md`
   - `Projects/AGY_AVIATIONCHAT/.opencode/commands/sudo-create-epics-stories-sprint.md`
   - `Projects/AGY_AVIATIONCHAT/.claude/skills/sudo-create-epics-stories-sprint/` (directory)

3. **Delete old files in Fresh_Workspace_BMAD**:
   - `Projects/Fresh_Workspace_BMAD/.agents/commands/sudo-create-epics-stories-sprint.md`
   - `Projects/Fresh_Workspace_BMAD/.agents/workflows/sudo-create-epics-stories-sprint.md`
   - `Projects/Fresh_Workspace_BMAD/.agents/skills/sudo-create-epics-stories-sprint/` (directory)
   - `Projects/Fresh_Workspace_BMAD/.claude/commands/sudo-create-epics-stories-sprint.md`
   - `Projects/Fresh_Workspace_BMAD/.opencode/commands/sudo-create-epics-stories-sprint.md`
   - `Projects/Fresh_Workspace_BMAD/.claude/skills/sudo-create-epics-stories-sprint/` (directory)

4. **Run Sync Command**:
   - Run `& ".agents/scripts/sync-agents.ps1"` in Lobby.
   - Run `& ".agents/scripts/sync-agents.ps1" -Target "Projects/AGY_AVIATIONCHAT"`
   - Run `& ".agents/scripts/sync-agents.ps1" -Target "Projects/Fresh_Workspace_BMAD"`

---

## Verification Plan

We will verify:
1. Verify that `sync-agents.ps1` runs without errors.
2. Verify that `sudo-write-epics-stories-sprint.md` exists in:
   - Lobby master `.agents/commands/`
   - Lobby generated `.agents/workflows/`
   - Lobby local tool dirs `.claude/commands/` and `.opencode/commands/`
   - Global caches (e.g. `~/.gemini/antigravity/global_workflows/`, `~/.config/opencode/commands/`, `~/.codex/prompts/`)
   - Project `.agents/commands/`, `.agents/workflows/`, `.claude/commands/`, and `.opencode/commands/` (for both AviationChat and Fresh_Workspace_BMAD).
3. Verify that the skill `sudo-write-epics-stories-sprint` exists in Lobby skills, Codex global skills, and both projects.
4. Verify that the old `sudo-create-epics-stories-sprint` files have been completely cleaned up in all locations.
