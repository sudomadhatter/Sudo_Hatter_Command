---
IsArtifact: true
ArtifactMetadata:
  title: "Map and index reconciliation after research_docs renames"
  type: implementation_plan
  date: 2026-07-28
---

# Implementation Plan — Map and Index Reconciliation

## Goal

Reconcile the lobby and maintained workspaces after the `research_docs` renames, plus the deterministic map and ledger drift found by `/update-maps-indexes`.

## Verified Proposed Edits

### Lobby

1. Regenerate the AUTO block in [docs/repo-map.md](../../../../../docs/repo-map.md) in its declared `content` mode. The linter identified `prds/` and `prd-NEXgen-VR-Director-2026-07-28/` as present on disk but absent from the generated block; the curated map is already valid.
2. Repair the rollout-source links in [router.md](../../../../../router.md) and [docs/workspace-standard.md](../../../../../docs/workspace-standard.md) to the real root source: `_my_resources/research_docs/implementation-plan_folder-as-workspace-routing-system.md`.
3. Refresh only the auto-managed file manifest in [_my_resources/open_tasks/todo_list.md](../../../../../_my_resources/open_tasks/todo_list.md): remove the two entries whose files no longer exist. Preserve Daniel's numbered prose and checkpoint metadata verbatim.
4. Add the missing session row for Fresh Workspace's existing `2026-07-28_rename-research-docs/` folder to [_artifacts/Fresh_Workspace_BMAD/INDEX.md](../../../../Fresh_Workspace_BMAD/INDEX.md).
5. At close-out, add this map-reconciliation session to [_artifacts/_main/INDEX.md](../../../INDEX.md).

### Fresh_Workspace_BMAD

1. Update [_my_resources/README.md](../../../Projects/Fresh_Workspace_BMAD/_my_resources/README.md) to inventory `research_docs/` rather than `docs/`.

### AGY_AVIATIONCHAT

1. Repair [docs/workspace-standard.md](../../../Projects/AGY_AVIATIONCHAT/docs/workspace-standard.md) so its rollout source points to the existing local snapshot `docs/file_structure_rules/master-implementation-plan.md`.

### NEXgen-VR-Director

1. Correct [docs/workspace-standard.md](../../../Projects/NEXgen-VR-Director/docs/workspace-standard.md) to cite its existing local source `_my_resources/research_docs/implementation-plan_folder-as-workspace-routing-system.md`, rather than the nonexistent `master-implementation-plan.md`.

## Verification

1. Re-run `python .agents/scripts/check_maps.py --all` and require the deterministic checks to be clean.
2. Verify every repaired rollout source resolves on disk.
3. Confirm the Fresh ledger row is present and the lobby open-tasks manifest exactly matches its directory.
4. Confirm the AUTO block preserves `mode=content` and contains the two newly detected top-level folders.

## Deliberately Flagged — No Edit Without Your Direction

1. Fresh Workspace's `docs/workspace-standard.md` cites a master-plan file absent from both its `research_docs/` directory and its local documentation. The skeleton's self-contained reference strategy needs a content decision, not a blind pointer replacement.
2. The lobby's Commands INDEX cites `_my_resources/research_docs/sudo-adviser-board-REFERENCE.md`, but that file is absent and no similarly named replacement was found. This is unrelated to the rename and needs an authoring decision.

## Explicit Non-Edits

- The master `.agents` family indexes already cover the newly added/renamed commands, skills, rules, and workflows; generated `sudo-*` workflow mirrors are intentionally not indexed.
- AGY, Fresh, and NEX generated repo-map blocks are current; no project map regeneration is needed.
- All project open-task manifests except the lobby's already match their directories.
- No context-hygiene, Tier-2 local-law, or project-index maintenance is required beyond the Fresh home-base bucket row.
