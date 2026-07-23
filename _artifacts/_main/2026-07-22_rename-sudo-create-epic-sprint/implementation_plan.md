# Rename /sudo-write-epics-stories-sprint to /sudo-create-epic-sprint

Rename the Phase A epic kickoff command `/sudo-write-epics-stories-sprint` to `/sudo-create-epic-sprint` across all platforms (Gemini, Claude, Codex, opencode), master `.agents` toolkit, project workspaces (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`), and all reference documentation files.

## User Review Required

> [!IMPORTANT]
> This change updates the canonical slash command name from `/sudo-write-epics-stories-sprint` to `/sudo-create-epic-sprint`.
> After approval, all agent platforms (Gemini, Claude, Codex, opencode) will recognize `/sudo-create-epic-sprint` for Phase A epic kickoff.

## Proposed Changes

### Master Toolkit (`.agents/`)

#### [NEW] [sudo-create-epic-sprint.md](file:///c:/Sudo_Hatter_Command/.agents/commands/sudo-create-epic-sprint.md)
- Create new command file from `.agents/commands/sudo-write-epics-stories-sprint.md` with updated title, frontmatter, and internal text references.

#### [DELETE] [sudo-write-epics-stories-sprint.md](file:///c:/Sudo_Hatter_Command/.agents/commands/sudo-write-epics-stories-sprint.md)
- Remove old command file.

#### [NEW] [SKILL.md](file:///c:/Sudo_Hatter_Command/.agents/skills/sudo-create-epic-sprint/SKILL.md)
- Rename skill folder `.agents/skills/sudo-write-epics-stories-sprint/` to `.agents/skills/sudo-create-epic-sprint/`.
- Update `name: sudo-create-epic-sprint` in YAML frontmatter and all internal text references.

#### [DELETE] [sudo-write-epics-stories-sprint](file:///c:/Sudo_Hatter_Command/.agents/skills/sudo-write-epics-stories-sprint/)
- Remove old skill folder.

#### [NEW] [sudo-create-epic-sprint.md](file:///c:/Sudo_Hatter_Command/.agents/workflows/sudo-create-epic-sprint.md)
- Create new workflow file from `.agents/workflows/sudo-write-epics-stories-sprint.md` with updated references.

#### [DELETE] [sudo-write-epics-stories-sprint.md](file:///c:/Sudo_Hatter_Command/.agents/workflows/sudo-write-epics-stories-sprint.md)
- Remove old workflow file.

#### [MODIFY] [INDEX.md](file:///c:/Sudo_Hatter_Command/.agents/commands/INDEX.md)
- Update entry for `sudo-create-epic-sprint.md`.

#### [MODIFY] [INDEX.md](file:///c:/Sudo_Hatter_Command/.agents/skills/INDEX.md)
- Update entry for `sudo-create-epic-sprint`.

#### [MODIFY] [INDEX.md](file:///c:/Sudo_Hatter_Command/.agents/workflows/INDEX.md)
- Update entry for `sudo-create-epic-sprint.md`.

#### [MODIFY] [sudo-boot-sprint-memory.md](file:///c:/Sudo_Hatter_Command/.agents/commands/sudo-boot-sprint-memory.md)
#### [MODIFY] [SKILL.md](file:///c:/Sudo_Hatter_Command/.agents/skills/sudo-boot-sprint-memory/SKILL.md)
#### [MODIFY] [sudo-boot-sprint-memory.md](file:///c:/Sudo_Hatter_Command/.agents/workflows/sudo-boot-sprint-memory.md)
- Update workflow step chain references to point to `/sudo-create-epic-sprint`.

---

### Reference Documentation & Flows

#### [MODIFY] [sudo_workflows_testing.md](file:///c:/Sudo_Hatter_Command/_my_resources/_quick_reference/sudo_workflows_testing.md)
- Replace all occurrences of `/sudo-write-epics-stories-sprint` and `sudo-write-epics-stories-sprint` with `/sudo-create-epic-sprint`.

#### [MODIFY] [tea_deep_reference.md](file:///c:/Sudo_Hatter_Command/_my_resources/diagrams_guides/workflows_tea_testing/tea_deep_reference.md)
- Replace all occurrences of `/sudo-write-epics-stories-sprint` and `sudo-write-epics-stories-sprint` with `/sudo-create-epic-sprint`.

#### [MODIFY] [sudo_workflows_testing.md](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md)
- Replace all occurrences with `/sudo-create-epic-sprint`.

#### [MODIFY] [epic-brief.md](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_artifacts/2026-07-22_epic-21-avch-demo-portal/epic-brief.md)
- Update next step reference to `/sudo-create-epic-sprint`.

#### [MODIFY] [sprint-status.yaml](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml)
#### [MODIFY] [epics.md](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/planning-artifacts/epics.md)
#### [MODIFY] [story-20.1-voice-session-continuity.md](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-20.1-voice-session-continuity.md)
- Update command references in notes and comments.

---

### Synchronization & Platform Deployment

#### [EXECUTE] Sync Master Toolkit across all platforms and projects
- Run `powershell -ExecutionPolicy Bypass -File .agents/scripts/sync-agents.ps1 -Maintained`
- Syncs master toolkit to:
  - Gemini / Antigravity machine-global workflow caches
  - Claude `.claude/commands/` and `.claude/skills/`
  - opencode `.opencode/commands/`
  - Codex `~/.codex/prompts/` and `~/.codex/skills/`
  - Maintained project toolkits (`Projects/AGY_AVIATIONCHAT` and `Projects/Fresh_Workspace_BMAD`).

---

### Verification & Documentation Graph

#### [EXECUTE] Reconcile maps, linter, and document graph
- Run `python .agents/scripts/check_maps.py --reconcile --all` to update `docs/doc-graph.json`, `docs/repo-map.md`, and all `INDEX.md` files.

#### [VERIFY] Grep audit for stale references
- Run a final `grep_search` across the lobby and projects to confirm zero stale occurrences of `sudo-write-epics-stories-sprint`.

## Verification Plan

### Automated Verification
- Run `sync-agents.ps1 -Maintained` to verify clean sync across all platforms and projects without error.
- Run `check_maps.py --all` to ensure no broken doc links, missing indexes, or stale command pointers exist.

### Manual Verification
- Verify file existence of `sudo-create-epic-sprint` in `.agents/commands/`, `.agents/skills/`, and `.agents/workflows/`.
- Verify file existence in `.claude/commands/`, `.opencode/commands/`, `.agents/` of child projects.
