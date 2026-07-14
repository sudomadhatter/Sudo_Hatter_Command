---
IsArtifact: true
ArtifactMetadata:
  title: Update GitNexus Graphs
  type: walkthrough
  date: 2026-07-14
---

# Walkthrough — Update GitNexus Graphs

We have updated the GitNexus graph indexes for both the lobby (`Sudo_Hatter_Command`) and the active product project (`AGY_AVIATIONCHAT`), keeping the product index focused only on core application components. We also created a guide explaining the machine-local nature of GitNexus index databases and how they are updated.

## Changes Made

1. **Refined Product Index Scope**:
   - Updated `Projects/AGY_AVIATIONCHAT/.gitnexusignore` to exclude development, deployment, and testing tooling from indexing. Excluded directories: `load/` (load tests), `scripts/` (development/automation/seeding scripts), `_test_scripts/` (test debris), `auth_keys/` (credentials), and `scratch/` (scratch files), along with root-level script files (`*.ps1`, `fix.py`, `scratch_parser*.py`).
   - Updated `Projects/AGY_AVIATIONCHAT/docs/gitnexus.md` to document the refined scope.

2. **Created GitNexus Sync Guide**:
   - Created [docs/gitnexus-sync.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/docs/gitnexus-sync.md) explaining that GitNexus index database files (such as `.gitnexus/lbug`) are ignored by Git and do not sync across machines. It outlines how the ignore rules and configurations sync, and how to re-index on other machines using `check_maps.py` and `node .gitnexus/run.cjs analyze`.
   - Added links referencing this guide at the end of both [docs/gitnexus.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/docs/gitnexus.md) and [Projects/AGY_AVIATIONCHAT/docs/gitnexus.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/docs/gitnexus.md).

3. **Re-Indexed Workspaces**:
   - Executed analysis for the lobby: `node .gitnexus/run.cjs analyze` from the lobby root.
   - Executed analysis for the product project: `node .gitnexus/run.cjs analyze` from `Projects/AGY_AVIATIONCHAT`. Both local graphs are now completely up-to-date with their respective `HEAD` commits.

4. **Regenerated AUTO Blocks & Resolved Drift**:
   - Regenerated the content-mode AUTO blocks for `docs/repo-map.md` and `Projects/AGY_AVIATIONCHAT/docs/repo-map.md` to match the current disk layout.
   - Resolved a pre-existing map linter failure in `Projects/AGY_AVIATIONCHAT/_artifacts/debugging/INDEX.md` by adding the missing row for the recent `2026-07-14_password-reset-fix/` session.

## Verification Results

We verified that the maps, indexes, and GitNexus index freshness are in perfect sync:

### Lobby Verification
```
==============================================================================
MAP & INDEX DRIFT LINT  (home base: Sudo_Hatter_Command)
==============================================================================
...
[AUTO block freshness]
  [ok] clean
[repo-map paths]
  [ok] clean
[INDEX.md paths]
  [ok] clean
[structure conformance]
  [ok] clean
[gitnexus index]  (hint only - does not fail the lint)
  [ok] index matches HEAD

All maps & INDEXes agree with disk. [ok]
```

### Product Verification
```
==============================================================================
MAP & INDEX DRIFT LINT  (BMAD project: AGY_AVIATIONCHAT)
==============================================================================
...
[AUTO block freshness]
  [ok] clean
[repo-map paths]
  [ok] clean
[INDEX.md paths]
  [ok] clean
[depth-3 _artifacts INDEX]
  [ok] clean
[structure conformance]
  [ok] clean
[gitnexus index]  (hint only - does not fail the lint)
  [ok] index matches HEAD

All maps & INDEXes agree with disk. [ok]
```

---

## Task Checklist
- [x] Update Projects/AGY_AVIATIONCHAT/.gitnexusignore (exclude dev tooling)
- [x] Update Projects/AGY_AVIATIONCHAT/docs/gitnexus.md (align symbol info)
- [x] Create docs/gitnexus-sync.md guide (explaining local-only graph index syncing behavior)
- [x] Add references to gitnexus-sync.md in both gitnexus.md files
- [x] Run GitNexus analysis on lobby (Sudo_Hatter_Command)
- [x] Run GitNexus analysis on product (AGY_AVIATIONCHAT)
- [x] Regenerate AUTO blocks in docs/repo-map.md for both repos
- [x] Reconcile missing index row in Projects/AGY_AVIATIONCHAT/_artifacts/debugging/INDEX.md
- [x] Verify index freshness using check_maps.py

---

## Your Actions

Please run these commands to commit the changes and re-anchor the map states across both repositories.

### 1. Commit Lobby Changes
In the lobby root repository, stage and commit the docs, sync guide, and artifacts updates:
```bash
git add _artifacts/INDEX.md _artifacts/_main/INDEX.md _artifacts/_main/2026-07-14_update-gitnexus-graphs/ docs/gitnexus.md docs/repo-map.md docs/gitnexus-sync.md docs/.maps-state.json && \
git commit -m "docs: exclude dev tooling from gitnexus, update repo-map, and add gitnexus sync guide"
```

### 2. Commit Product Changes
In the `Projects/AGY_AVIATIONCHAT` repository, stage and commit the ignore, documentation, and debug index changes:
```bash
git -C Projects/AGY_AVIATIONCHAT add .gitnexusignore docs/gitnexus.md docs/repo-map.md _artifacts/debugging/INDEX.md docs/.maps-state.json && \
git -C Projects/AGY_AVIATIONCHAT commit -m "docs: exclude dev tooling from gitnexus indexing and update maps"
```

### 3. Re-Anchor Map States
After committing, run the following command in the lobby root to baseline the map checks (this updates the `.maps-state.json` anchors and consumes the local commit journal):
```bash
python .agents/scripts/check_maps.py --set-anchor --all
```
