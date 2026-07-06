# /1_update-maps Workflow Execution

This plan details the proposed changes to reconcile the maps and INDEX files across the home base and all conformant projects, based on the output of the drift linter (`check_maps.py --all`).

## User Review Required
> [!IMPORTANT]
> Please review the proposed edits to the INDEX files and open-tasks manifests. Once approved, I will execute these changes and provide the GitNexus re-index commands for the stale workspaces.

## Proposed Changes

### Sudo_Hatter_Command (Lobby)

#### ✅ Accurate (no action)
- AUTO block is fresh
- repo-map paths, folder coverage, and structure conformance are clean

#### ✏️ Proposed edits
- `_artifacts/INDEX.md`: fix dead path `system/testing_work_flows_tea_sudo.md` → `system/tea_testing_work_flows_sudo.md` [reason: file was renamed]

#### 🗂️ Open-tasks list (`todo_list.md` → ## Open Work)
- Refresh manifest to reflect exactly 0 task files (no `.md` files present other than `todo_list.md` itself).

#### 🚩 Flagged — NOT mine to edit (needs you / another tool)
- `_my_resources/diagrams_guides/INDEX.md` and `_my_resources/diagrams_guides/system/tea_testing_guide_strategy.md` contain references to the old `testing_work_flows_tea_sudo.md` filename. These are in your protected area (`_my_resources/`) so I will leave them untouched.

#### 🔍 GitNexus index
- Sudo_Hatter_Command index is STALE (indexed at 9993428, HEAD is a600b25). Re-index command will be handed over at close-out.

---

### Projects/AGY_AVIATIONCHAT

#### ✅ Accurate (no action)
- repo-map paths, folder coverage, INDEX.md paths, and structure conformance are clean.

#### ✏️ Proposed edits
- `_artifacts/INDEX.md`: add row for new session folder `debugging` [reason: session folder exists, no row]

#### 🗂️ Open-tasks list (`todo_list.md` → ## Open Work)
- Update manifest to exactly match the current files in `open_tasks/`:
  - `admin_graph_rag_update.md`
  - `live_testing_credentials.md`
  - `looping_workflow_prp.md`
  - `production-readiness-audit.md`
  - `repo-map-auto-maintenance.md`
  - `sprint-dependency-map.md`

#### 🔍 GitNexus index
- AGY_AVIATIONCHAT index is STALE (indexed at baf098a, HEAD is c72ee49). Re-index command will be handed over at close-out.

#### AUTO block
- Regenerated (mode=content): Updates to component-specs, implementation-artifacts, utils, admin, scripts and frontend file counts.

---

### Projects/BRKN_Tattoos

#### ✏️ Proposed edits
- `docs/repo-map.md (CURATED)`: remove dead path `_bmad/bmm/stories` [reason: directory no longer exists on disk]
- `_artifacts/INDEX.md`: Create base file from house pattern [reason: missing session ledger required for conformance]
- `_artifacts/active-context.md`: Create base file from house pattern [reason: missing continuity brief required for conformance]

#### 🗂️ Open-tasks list (`todo_list.md` → ## Open Work)
- Refresh manifest to reflect exactly 0 task files (no `.md` files present other than `todo_list.md` itself).

#### AUTO block
- Regenerated (mode=auto): Various folders added/removed to reflect actual disk state.

---

### Projects/RAG_Pipeline_AC

#### 🚩 Flagged — NOT mine to edit (needs you / another tool)
- Workspace is NOT conformant (missing repo-map, maintenance scripts, session ledger, etc.). It appears to be half-built. I will skip reconciliation for this workspace to avoid forcing structure on a non-standard project.

## Verification Plan
1. Edit the files as proposed.
2. Verify that no paths under `_my_resources/` (other than the surgical open-tasks manifests) were touched.
3. Perform the close-out by handing over the GitNexus re-index commands for the stale workspaces.
