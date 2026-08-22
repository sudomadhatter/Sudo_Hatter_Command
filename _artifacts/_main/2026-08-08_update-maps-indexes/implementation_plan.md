---
IsArtifact: true
ArtifactMetadata:
  title: Fan-out Map and INDEX Reconciliation
  type: implementation_plan
  date: 2026-08-08
---

# Fan-out Map and INDEX Reconciliation

## Goal and boundaries

Reconcile the lobby plus the two maintained projects (`AGY_AVIATIONCHAT` and
`NEXgen-VR-Director`) against disk, preserving each repo-map's declared mode and changing only
navigation/ledger Markdown. The fan-out linter currently exits 1: lobby has one missing depth-3 row and a
context-prune hint; AviationChat has stale map content, a dead curated path, three missing level-2 INDEXes,
and a dead hook-index path; NEXgen is mechanically clean but its stored git anchor is no longer in history.

This run does not edit code, generated/vendor/cache content, protected task-note prose, BMAD-owned `_bmad/`,
or substantive workflow policy. It never commits, pushes, merges, deletes, re-indexes GitNexus, or sets map
anchors. Pre-existing lobby changes remain untouched except for the specifically authorized Open Work
manifest region in `todo_list.md`; AviationChat and NEXgen began clean.

## Approved edit batch

### Lobby

1. In [`_artifacts/INDEX.md`](../../../INDEX.md), add actionable session rows for
   `2026-08-07_toolkit-centralization/` and `2026-08-07_command-center-workflow-memory/`.
2. In [`_artifacts/_main/INDEX.md`](../INDEX.md), add the missing depth-3 row for
   `2026-08-07_command-center-workflow-memory/` using the plan's actual purpose and files.
3. Prune [`active-context.md`](../active-context.md) from 16 to the newest 10 session blocks by moving the
   oldest six blocks verbatim into [`active-context-archive.md`](../active-context-archive.md).
4. Refresh only the auto-listed manifest under `## Open Work` in
   [`todo_list.md`](../../../../_my_resources/open_tasks/todo_list.md): retain
   `plan_optimize-sudo-dev-story-tests.md` and add the three real files currently absent from the manifest
   (`architecture-decision-proposal-2026-08-05-firestore-schema-scope.md`,
   `git-hooks-board-stale-install.md`, and `proposal_graphrag_executiblity.md`). Preserve Daniel's prose and
   checkpoint comments byte-for-byte.
5. Repair the documented lobby repo-map regeneration command in
   [`docs/repo-map.md`](../../../../docs/repo-map.md) so it uses `--root .` and the default output, matching
   the workflow's no-`--output` contract. Its AUTO block is already current and will not change.

### AviationChat

1. Regenerate [`docs/repo-map.md`](../../../../Projects/AGY_AVIATIONCHAT/docs/repo-map.md) in `mode=content`
   with ignores `_my_resources,_bmad`; this removes two stale `ta_agent/` entries. Repair the curated dead
   `docs/workspace-standard.md` pointer to the command-center canonical copy and keep all other meaning.
2. Create the required tier-2 inventories
   [`rules/INDEX.md`](../../../../Projects/AGY_AVIATIONCHAT/.agents/rules/INDEX.md) and
   [`scripts/INDEX.md`](../../../../Projects/AGY_AVIATIONCHAT/.agents/scripts/INDEX.md), using the NEXgen thin
   project as the house pattern and listing AviationChat's actual project law/enforcement files.
3. Add the missing debug-4.1 session row to
   [`_artifacts/INDEX.md`](../../../../Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md), grounded in its existing
   walkthrough (HR relative-date resolution and streamlined rating flow; tests green; review PASS).
4. Refresh the explicit auto-listed contents in nine existing INDEXes, adding only tracked disk entries:
   31 implementation artifacts, 46 test artifacts, 1 router, 4 backend scripts, 5 services, 5 backend test
   entries, 1 Firebase test lockfile, 4 public assets, and 4 frontend source instrumentation/config files.
   Ignore `node_modules`, `__pycache__`, logs, and Playwright `test-results` because git explicitly ignores
   them.
5. Repair deterministic central-law pointers in the root [`AGENTS.md`](../../../../Projects/AGY_AVIATIONCHAT/AGENTS.md),
   artifact READMEs, and repo-map. In the root
   [`README.md`](../../../../Projects/AGY_AVIATIONCHAT/README.md), replace dead vendored-toolkit INDEX and
   local-workflow pointers with `.agents/INDEX.md` plus command-center locations, and repair the exact
   `/1_live_testing_team` rename to `/sudo-live-testing-team`.

### NEXgen VR Director

1. Add four missing 2026-07-28/29 migrated-session rows to
   [`_artifacts/INDEX.md`](../../../../Projects/NEXgen-VR-Director/_artifacts/INDEX.md), matching the complete
   project-local `_main/INDEX.md` ledger.
2. Refresh three explicit auto-listed INDEXes: five planning-artifact entries, four test-artifact entries,
   and the two backend test scaffold directories.
3. In the root [`AGENTS.md`](../../../../Projects/NEXgen-VR-Director/AGENTS.md), repair the dead local
   `.agents/workflows/autopilot_bmad_dev_loop.md` pointer to the command-center reference and rename the
   nonexistent `/autopilot` invocation to `/autopilot_claude`.
4. In the root [`README.md`](../../../../Projects/NEXgen-VR-Director/README.md), repair only stale structure
   claims from the thin conversion: `.agents/` owns project law rather than a vendored toolkit; per-tool dirs
   are config rather than synced command trees; remove nonexistent `opencode.json`; and state that home-base
   launches still save NEXgen history project-locally.

## Explicitly flagged and left untouched

- AviationChat's `scripts/git-hooks/INDEX.md` documents `board-stale-stamp.sh`, but that script was retired in
  commit `f2fdc62c`; the remaining installer still invokes the deleted script. This is a broken feature, not
  a pointer-only repair. Do not hide it by editing the INDEX; route it to a separate cleanup/deletion decision.
- AviationChat's ignored `frontend/test-results/` directory triggers the level-2 INDEX linter. Do not create
  an INDEX inside generated Playwright output; report this as a `check_maps.py` false positive.
- AviationChat's project guide still contains broader pre-thin workflow assertions and three retired `/1_*`
  commands without proven one-to-one replacements. NEXgen's project guide likewise contains old commit,
  task-list, artifact-routing, and vendoring law. Those are substantive authoring decisions, so this upkeep
  run flags them instead of rewriting meaning.
- GitNexus is stale in the lobby and AviationChat. Re-index commands are handed off after commits; the
  workflow never runs them.
- NEXgen's missing baseline is repaired only by Daniel's post-commit `--set-anchor --all`; never anchor an
  uncommitted tree.

## Execution and verification

1. After approval, create/enter short-lived keyed chore branches as policy allows without disturbing the
   lobby's existing dirty work; edit only the files above with explicit-path patches.
2. Regenerate only AviationChat's AUTO block in its declared mode. Re-read every edited manifest/INDEX and
   prove protected prose and ignored output were untouched.
3. Run `git diff --check` and inspect per-repo diffs/status. Grep repaired old names/paths to prove the scoped
   dead references are gone.
4. Run `python3 .agents/scripts/check_maps.py --all`. Expected residual red is limited to the two explicitly
   deferred AviationChat issues (broken retired hook inventory and ignored `test-results` false positive);
   every approved deterministic item must clear.
5. Write one [`walkthrough.md`](./walkthrough.md) with the final checklist, evidence, residual flags, and
   exact per-repo commit/anchor/GitNexus commands. Do not execute those delivery commands.

## Approval gate

Recommendation: approve this deterministic batch and keep the flagged behavioral-doc/hook cleanup separate;
folding it in would turn map upkeep into policy authoring and deletion work. No project file changes until
Daniel replies with the exact word **approved**.
