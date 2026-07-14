---
IsArtifact: true
ArtifactMetadata:
  title: Lobby and Projects Map Update
  type: implementation_plan
  date: 2026-07-13
---
# Lobby and Projects Map Update

Reconcile the repo-maps, indexes, and open tasks lists for the Lobby and conformant projects.

## User Review Required

We have detected that two workspaces in the `Projects/` directory are currently NOT conformant with the workspace standard:
- [BRKN_Tattoos](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/BRKN_Tattoos) - Missing session ledger (`_artifacts/INDEX.md`) and continuity brief (`_artifacts/<bucket>/active-context.md`), and baseline `ebe65ed` not found in history.
- [RAG_Pipeline_AC](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/RAG_Pipeline_AC) - Missing `docs/repo-map.md`, several level-2 `INDEX.md` files, scripts, and session ledger.

Per the "conformance first" guardrail, these non-conformant workspaces will be skipped for reconciliation and flagged for manual setup.

## Open Questions

None at this stage.

## Proposed Changes

### Lobby (Sudo_Hatter_Command)
- Update [repo-map.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/docs/repo-map.md) by regenerating the AUTO block.
- Refresh the open-tasks list in [todo_list.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/_my_resources/open_tasks/todo_list.md) to match current tasks on disk.

### Projects/AGY_AVIATIONCHAT
- Update [repo-map.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/docs/repo-map.md) by regenerating the AUTO block.
- Reconcile depth-3 artifacts indexes:
  - Add missing session rows in `_artifacts/epic_11/INDEX.md`, `_artifacts/epic_8/INDEX.md`, `_artifacts/tea/INDEX.md`, and `_artifacts/_main/INDEX.md`.
  - Remove stale rows in `_artifacts/tea/INDEX.md`.
- Refresh the open-tasks list in `_my_resources/open_tasks/todo_list.md`.

### Projects/Fresh_Workspace_BMAD
- Update [repo-map.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/Fresh_Workspace_BMAD/docs/repo-map.md) by regenerating the AUTO block and removing dead curated path references.
- Refresh the open-tasks list in `_my_resources/open_tasks/todo_list.md`.

## Verification Plan
- Run the drift linter (`python .agents/scripts/check_maps.py --all`) and verify all conformant workspaces exit with 0 (clean).
