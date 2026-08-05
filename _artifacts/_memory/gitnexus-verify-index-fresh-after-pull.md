---
name: gitnexus-verify-index-fresh-after-pull
description: "Before trusting any impact()-based test/blast-radius selection, verify the GitNexus index is fresh (indexed_commit == HEAD); a cross-machine git pull silently staleses it → fail-safe to running everything."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ced98160-a2c6-461e-9723-f5144bf2b6d9
---

Daniel's standing rule (2026-07-03, driving TEA-9/TIA): **always verify GitNexus is up to date before
trusting an `impact()`/`detect_changes()`-based selection** — because the index is machine-local and
gitignored (see [[gitnexus-index-not-actually-live]]), a `git pull` of work committed on ANOTHER computer
advances HEAD past the locally-indexed commit, so the local index is silently STALE and `impact()` will
select the WRONG tests (or reference symbols that no longer exist).

**Why:** the index doesn't travel with git; nothing auto-refreshes it after a pull. A stale-index selective
run looks like it worked but can skip exactly the tests the pulled change needs.

**How to apply:**
- Staleness test is HEAD-equality: **`indexed_commit == HEAD`** (read the indexed commit via
  `node .gitnexus/run.cjs status`; HEAD via `git rev-parse HEAD`). A **dirty working tree is NOT stale** —
  uncommitted changes are the intended input to a pre-push selection; requiring a clean tree defeats it.
- If not provably fresh → do NOT trust selection: **fail-safe to the full suite** (and nudge
  `node .gitnexus/run.cjs analyze` to re-enable fast selective runs). This is TEA-9's 3rd fail-safe trigger
  (`STALE_INDEX`), alongside empty-selection and impact-error.
- Compounds with the known under-selection bug ([[gitnexus-impact-misses-attribute-dispatch]]): impact() is
  a speed optimization with a full-suite floor, never the sole gate.
- `impact()`/`detect_changes()` are **MCP-only** (the CLI is `analyze|status|clean|wiki|list`), so a local
  script can read freshness via `status` but must source the affected-test report another way.

**Also automated in the lobby toolkit (2026-07-03):** `check_maps.py` **check 9** (non-fatal hint, runs on
every `/1_update-maps` incl. the `--all` fan-out) reads `<root>/.gitnexus/meta.json` → `lastCommit` and
compares to `git rev-parse HEAD`, per workspace — so routine map maintenance now surfaces a stale index
without waiting for a TIA run. Caveats: `--skip-git` indexes (the `.agents/` SUDO_COMMAND one) have no
`lastCommit` → check 9 can't see them (manual re-analyze after toolkit edits); meta.json is a simpler
freshness source than `run.cjs status` for scripts (pure JSON read, no node spawn). NB `meta.json` also
embeds the git remote URL **with credentials** — flagged to Daniel for PAT rotation.

**Now shipped as a tool (TEA-9, done 2026-07-03):** `scripts/tia_gate.ps1` → `backend/tia/` (in AGY) is the
local pre-push TIA gate that operationalizes exactly this rule. `backend/tia/gate.py` reads
`node .gitnexus/run.cjs status` for the indexed vs current commit; the pure `backend/tia/select.py`
(`is_index_fresh` = HEAD-equality, dirty ignored) drives a fail-safe ladder — `STALE_INDEX` / `IMPACT_ERROR`
/ `EMPTY_SELECTION` / hub-file / any unmapped file → RUN_ALL the full suite. Selection is file-level
(`git diff --name-only` → test-map), sidestepping the MCP-only limitation; GitNexus is used ONLY for the
freshness check. Run `./scripts/tia_gate.ps1 -DryRun` to see the decision; it's a fast local pre-check, NOT
the merge gate (the full suite stays the real gate — file-level TIA can under-select). See
[[tea-retrofit-active-initiative]].
