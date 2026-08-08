---
IsArtifact: true
type: walkthrough
date: 2026-08-08
workspace: _main
---

# Update maps and indexes — walkthrough

## Outcome

Reconciled the lobby and both maintained projects against disk. The lobby and NEXgen now pass every
deterministic map/index check. AGY passes the generated map, folder coverage, artifact depth, structure,
context, and local-law checks; two substantive items remain visible rather than being papered over:

1. `scripts/git-hooks/INDEX.md` still points at `.git/hooks` while the retired
   `board-stale-stamp.sh` is still invoked by the installer. That is a hook implementation repair, not an
   index-only change.
2. `frontend/test-results/` is ignored generated output, but the generic level-2 check currently requires
   an `INDEX.md` there. Adding a tracked index to generated output would encode the wrong ownership model;
   the checker needs a scoped exception or the output location needs redesign.

Daniel explicitly approved close-out after the audit. AGY commit `c95599d3` was merged to `main` as
`3213fe36`; NEXgen commit `27f0197` was merged to `main` as `1c46348`. Both chore branches and both main
merges were pushed. The lobby commit is built with an isolated Git index so the concurrent command-center
lane's uncommitted files are not swept into this task. No generated-output index or retired-hook repair is
included.

## Task Checklist

- [x] Loaded the command, workflow, lobby law, project law, and both maintained project maps.
- [x] Audited all maintained workspaces and recorded why six other project directories were skipped.
- [x] Wrote the implementation plan, presented it in full, and received Daniel's approval.
- [x] Regenerated the AGY repo-map AUTO block in its declared content mode.
- [x] Reconciled tracked folder and artifact inventories in AGY and NEXgen.
- [x] Added missing project-owned `.agents/rules/INDEX.md` and `.agents/scripts/INDEX.md` in AGY.
- [x] Repaired dead central-toolkit, workspace-standard, and renamed command references.
- [x] Reconciled lobby artifact ledgers and the live open-task file manifest.
- [x] Pruned the lobby active context from 16 to 10 dated blocks and archived all six removed blocks.
- [x] Re-ran the fan-out checker and isolated the two remaining AGY defects.
- [x] Verified owned diffs for whitespace errors; repository-wide lobby warnings belong to a parallel lane.
- [x] Daniel approved close-out; push each chore branch, merge it to `main`, and push each main branch.
- [x] Refresh map anchors and the two stale GitNexus graphs after the merges.

## Evidence

| Goal | Result | Evidence |
|---|---|---|
| Lobby deterministic drift | PASS | `check_maps.py --all`: AUTO, paths, folder coverage, INDEX paths, depth, structure, context, and Tier-2 law all clean. |
| AGY deterministic drift | CONCERNS | All checks clean except the retired `.git/hooks` reference and generated `frontend/test-results/INDEX.md` requirement described above. |
| NEXgen deterministic drift | PASS | All map/index/structure/context checks clean; its missing historical anchor is a post-commit maintenance signal. |
| Active-context hygiene | PASS | 10 dated blocks remain active; 6 removed blocks are under `Archived 2026-08-08`. |
| Tracked inventory coverage | PASS | Custom omission sweeps returned no unlisted tracked entries after 101 AGY and 11 NEXgen rows were added/refreshed. |
| Rename/reference sweep | PASS | Dead local toolkit links, `/1_live_testing_team`, NEXgen's old autopilot workflow path, `/autopilot`, and the nonexistent `opencode.json` tree entry were removed or replaced. |
| Whitespace check | PASS for owned paths | AGY and NEXgen `git diff --check` are clean; lobby owned paths are clean. Repository-wide lobby warnings are in `_artifacts/_memory/windows-authored-code-hides-posix-bugs.md` and a pre-existing todo-list hunk from the parallel lane. |

## Suite Ledger

| Command | Result |
|---|---|
| `python3 .agents/scripts/check_maps.py --all` | Expected nonzero: only the two documented AGY findings remain; lobby and NEXgen deterministic checks pass. |
| `git diff --check` in AGY | PASS |
| `git diff --check` in NEXgen | PASS |
| `git diff --check -- <owned lobby paths>` | PASS |
| Old-name/dead-reference `rg` sweeps | PASS after the final NEXgen `/autopilot_claude` correction |

## Changed Surfaces

- Lobby: artifact ledgers, active-context archive/prune, open-task manifest, and repo-map generator guidance.
- AGY branch `chore/AVCH-23-update-maps-indexes`: repo map; root/reference docs; two project-law indexes;
  artifact, BMAD-output, backend, Firebase, and frontend indexes.
- NEXgen branch `chore/SCC-31-update-maps-indexes`: root/reference docs plus artifact, planning, test, and
  backend-test indexes.

## Your Actions

No delivery action remains. The only follow-up is separate implementation work for the two AGY residuals:
retire or replace the broken board-stale installer contract, and teach the map checker how to treat ignored
generated-output directories.
