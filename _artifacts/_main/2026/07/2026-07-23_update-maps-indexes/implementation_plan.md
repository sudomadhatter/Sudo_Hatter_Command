---
IsArtifact: true
ArtifactMetadata:
  title: "Fan-out map and index reconciliation"
  type: implementation_plan
  date: 2026-07-23
---

# Fan-out map and index reconciliation

## Goal

Bring the maintained home-base workspaces' generated maps and artifact ledgers into agreement with disk, without changing curated routing prose, protected open-task notes, or source code.

## Scope and proposed file changes

### Lobby

- `docs/repo-map.md` — regenerate only the AUTO block in its declared `content` mode; remove three no-longer-present `_bmad-output/` child folders from the generated tree.
- `_artifacts/AGY_AVIATIONCHAT/INDEX.md` — add the unlisted `2026-07-22_epic-21-avch-demo-portal/` session.
- `_artifacts/_main/INDEX.md` — add the unlisted `2026-07-22_operator-profile-rule/` and `2026-07-22_pipeline-conversion-and-sop/` sessions.

### Projects/AGY_AVIATIONCHAT

- `docs/repo-map.md` — regenerate only the AUTO block in its declared `content` mode, including the linter-detected folder drift.
- `frontend/test-results/INDEX.md` — create the required level-2 inventory for `.last-run.json`.
- `_artifacts/epic_debug_1/INDEX.md` — add the two unlisted debugging-story session folders.
- `_artifacts/epic_debug_2/INDEX.md` — create the required depth-3 session ledger for its two session folders.
- `_artifacts/_main/INDEX.md` — add the unlisted `2026-07-21_voice-session-continuity/` session.

### Projects/Fresh_Workspace_BMAD

- `docs/repo-map.md` — regenerate only the AUTO block in its declared `auto` mode.

## Explicit non-changes

- No curated `repo-map` routing entries: all curated paths and top-level coverage are current.
- No `_my_resources/open_tasks/todo_list.md` change: every `## Open Work` manifest matches its task files.
- No Tier-2 law or AGENTS/README pointer repair: the linter reports the laws as correct, and the renamed command has no stale maintained-workspace AGENTS/README reference.
- Do not alter AviationChat's 391-line active context automatically. It has no dated session blocks, so a safe mechanical archive boundary cannot be inferred; the linter warning will remain a flagged authoring decision.
- Do not run GitNexus indexing, change git safety configuration, commit, push, or set reconciliation anchors.

## Execution order

1. Regenerate each map in the mode and with the ignore set already declared by that map.
2. Reconcile the listed artifact ledgers and create the missing level-2 index.
3. Re-run the fan-out linter and verify that all fatal drift is clear.
4. Record a walkthrough with the linter output and hand off the remaining GitNexus, active-context, git-safety, commit, and anchor actions.

## Verification

Run `python .agents/scripts/check_maps.py --all`. Expected result: no AUTO-map, level-2-index, or depth-3-ledger failures; the lobby GitNexus stale-index hint and AviationChat active-context review-length hint remain deliberately informational.
