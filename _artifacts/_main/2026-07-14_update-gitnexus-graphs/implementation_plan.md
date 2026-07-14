---
IsArtifact: true
ArtifactMetadata:
  title: Update GitNexus Graphs
  type: implementation_plan
  date: 2026-07-14
---

# Update GitNexus Graphs

This plan outlines the steps to update the GitNexus code intelligence graphs (indexes) for both the lobby (`Sudo_Hatter_Command`) and the active product project (`AGY_AVIATIONCHAT`). It ensures we follow the rules for what to index by verifying and refining the `.gitnexusignore` scopes.

## User Feedback Integrated
- **Exclude Dev Tooling**: Update `Projects/AGY_AVIATIONCHAT/.gitnexusignore` to ensure we only map components of the actual application (e.g., `backend/`, `frontend/`, `firebase/`, `config/`), and exclude development/testing tools and scripts (such as `load/`, `scripts/`, `_test_scripts/`, `auth_keys/`, `scratch/`, and root-level automation scripts).

## Proposed Changes

### [Component Name] GitNexus Configuration

#### [MODIFY] [.gitnexusignore](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/.gitnexusignore)
Add ignores for development/testing tools, scripts, and temporary credentials directories:
- `/load/` (k6 load tests)
- `/scripts/` (development/automation/seeding scripts)
- `/_test_scripts/` (development test debris)
- `/auth_keys/` (credentials/auth files)
- `/scratch/` (temporary scratch space)
- `/*.ps1` (deployment/automation scripts)
- `/fix.py` (root script helper)
- `/scratch_parser*.py` (root script helpers)

#### [MODIFY] [gitnexus.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/docs/gitnexus.md)
Update the documentation to match the new indexing scope.

### Execution Steps

1. Run the GitNexus analysis for the lobby:
   ```powershell
   node .gitnexus/run.cjs analyze
   ```
2. Run the GitNexus analysis for the active product project:
   ```powershell
   cd Projects/AGY_AVIATIONCHAT
   node .gitnexus/run.cjs analyze
   ```

## Rules for What to Index (Verification)

### Lobby (`Sudo_Hatter_Command/.gitnexusignore`)
- **Signal**: Maps only the manager/routing surface (root maps, `docs/`, `_system/`).
- **Excludes**:
  - `Projects/` (separate git repos, indexed independently)
  - `_artifacts/` (session memory/walkthroughs)
  - `_my_resources/` (personal tasks/notes)
  - `_bmad/`, `_bmad-output/` (agent framework files)
  - `_routing-canary/` (routing test fixtures)
  - `.agents/` (automatically skipped by GitNexus 1.6.8 due to dot-folder walker limitation).

### Product (`Projects/AGY_AVIATIONCHAT/.gitnexusignore`)
- **Signal**: Product code (`backend/`, `frontend/`, `docs/`, `firebase/`, `config/`).
- **Excludes**:
  - `_artifacts/`
  - `_my_resources/`
  - `_bmad/`, `_bmad-output/`
  - `/load/` (k6 load tests)
  - `/scripts/` (dev automation/setup scripts)
  - `/_test_scripts/`
  - `/auth_keys/`
  - `/scratch/`
  - `/*.ps1`, `/fix.py`, `/scratch_parser*.py`
  - Root-level test/debug debris (`*.out`, `*.bak`, etc.)

## Verification Plan

### Automated Tests / Checks
1. Run the map-check script with `--all` to verify that check 9 (GitNexus index freshness) passes:
   ```powershell
   python .agents/scripts/check_maps.py --all
   ```
2. Run `git status` in both repositories to verify what files were updated (typically `.gitnexus/` databases such as `lbug` and `meta.json`).
