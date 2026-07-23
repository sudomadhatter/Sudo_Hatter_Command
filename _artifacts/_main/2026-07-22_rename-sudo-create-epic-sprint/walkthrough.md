# Walkthrough — Rename /sudo-write-epics-stories-sprint to /sudo-create-epic-sprint

The Phase A epic kickoff command has been renamed from `/sudo-write-epics-stories-sprint` to `/sudo-create-epic-sprint` across all platforms (Gemini, Claude, Codex, opencode), project workspaces (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`), reference documentation, and document graphs.

## Changes Made

### 1. Master Toolkit (`.agents/`)
- Renamed master command file `.agents/commands/sudo-write-epics-stories-sprint.md` → [sudo-create-epic-sprint.md](file:///c:/Sudo_Hatter_Command/.agents/commands/sudo-create-epic-sprint.md).
- Renamed master skill directory `.agents/skills/sudo-write-epics-stories-sprint/` → [.agents/skills/sudo-create-epic-sprint/](file:///c:/Sudo_Hatter_Command/.agents/skills/sudo-create-epic-sprint/SKILL.md) and updated `name: sudo-create-epic-sprint`.
- Renamed master workflow file `.agents/workflows/sudo-write-epics-stories-sprint.md` → [sudo-create-epic-sprint.md](file:///c:/Sudo_Hatter_Command/.agents/workflows/sudo-create-epic-sprint.md).
- Updated [commands/INDEX.md](file:///c:/Sudo_Hatter_Command/.agents/commands/INDEX.md) catalog entry.

### 2. Multi-Platform & Multi-Project Synchronization (`sync-agents`)
Executed `powershell -ExecutionPolicy Bypass -File .agents/scripts/sync-agents.ps1 -Maintained`:
- **Gemini / Antigravity**: Refreshed global workflows (`~/.gemini/antigravity/global_workflows`).
- **Claude**: Synced `.claude/commands/` and `.claude/skills/`.
- **opencode**: Synced `.opencode/commands/` and global commands (`~/.config/opencode/commands`). Purged retired `sudo-write-epics-stories-sprint.md`.
- **Codex**: Synced prompts (`~/.codex/prompts`) and skills (`~/.codex/skills`).
- **Child Projects**: Vendored updated `.agents/` and tool folders into [Projects/AGY_AVIATIONCHAT](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT) and [Projects/Fresh_Workspace_BMAD](file:///c:/Sudo_Hatter_Command/Projects/Fresh_Workspace_BMAD). Purged retired vendor files in both projects.

### 3. Reference Documentation & Flows
Updated all occurrences in:
- [_my_resources/_quick_reference/sudo_workflows_testing.md](file:///c:/Sudo_Hatter_Command/_my_resources/_quick_reference/sudo_workflows_testing.md) (diagrams, command tables, TEA call-graphs)
- [_my_resources/diagrams_guides/workflows_tea_testing/tea_deep_reference.md](file:///c:/Sudo_Hatter_Command/_my_resources/diagrams_guides/workflows_tea_testing/tea_deep_reference.md)
- [Projects/AGY_AVIATIONCHAT/_artifacts/2026-07-22_epic-21-avch-demo-portal/epic-brief.md](file:///c:/Sudo_Hatter_Command/_artifacts/AGY_AVIATIONCHAT/2026-07-22_epic-21-avch-demo-portal/epic-brief.md)
- [Projects/AGY_AVIATIONCHAT/_bmad-output/planning-artifacts/epics.md](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/planning-artifacts/epics.md)
- [Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml)
- [Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-20.1-voice-session-continuity.md](file:///c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-20.1-voice-session-continuity.md)

### 4. Graph & Maps Verification
- Regenerated document graph via `generate_doc_graph.py` ([docs/doc-graph.json](file:///c:/Sudo_Hatter_Command/docs/doc-graph.json)).
- Anchored maps baseline via `check_maps.py --all --set-anchor`.
- Verified zero stale references remaining across active codebase and reference guides.

## Verification Results

### Automated Verification
```text
sync-agents: -Maintained fan-out (lobby + .agents\maintained-projects.txt)
sync-agents: purged 1 retired .opencode command(s): sudo-write-epics-stories-sprint.md
sync-agents: AGY_AVIATIONCHAT: purged 3 retired vendor file(s)
sync-agents: Fresh_Workspace_BMAD: purged 3 retired vendor file(s)
doc-graph written: 243 docs | 231 edges
baseline anchored -> docs/.maps-state.json
```
