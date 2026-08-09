---
IsArtifact: true
ArtifactMetadata:
  title: SCC-59 map and index reconciliation walkthrough
  type: walkthrough
  date: 2026-08-09
---

# SCC-59 — Maps and indexes reconciled after artifact date reorganization

The lobby and both conformant projects were reconciled against disk after the June and July home-base
sessions moved beneath `2026/<month>/`. Jira handling was corrected during the run: SCC-54 was not reused;
the required Tasks are SCC-59 (lobby, parent SCC-33) and AVCH-51 (AviationChat, parent AVCH-23).

## Task Checklist

- [x] Repoint 56 `_main/INDEX.md` rows and 30 live continuity/ledger references to `2026/06/` or
  `2026/07/`.
- [x] Create June and July month indexes covering all 25 and 31 session folders.
- [x] Backfill every uncovered `_main` session into the shared ledger, restore newest-first order,
  keep the newest 50 live rows, and preserve the other 58 in `INDEX-archive.md`.
- [x] Repair `_artifacts` structure descriptions and refresh only the generated Open Work manifest.
- [x] Remove the approved duplicate `2026/06/proposal_graphrag_executiblity.md`; the canonical August
  command-center workflow plan remains. The removed copy is recoverable from git history.
- [x] Reconcile AviationChat's Epic 19 bucket and NEXgen's project-local date ordering.
- [x] Run the fan-out linter and classify the two remaining AviationChat findings rather than hiding them.
- [x] Refresh the lobby and AviationChat GitNexus indexes.

## Evidence

| Claim | Proof |
|---|---|
| Lobby deterministic map/index checks | `python3 .agents/scripts/check_maps.py --all` → AUTO, repo-map paths, folder coverage, INDEX paths, level-2, depth-3, structure, context, and Tier-2 law all `[ok]` |
| Month coverage | June: 25 folders / 25 rows; July: 31 folders / 31 rows |
| Shared ledger coverage | 83 `_main` index rows; zero missing from live + archive; live 50, archive 58, zero duplicate ledger keys |
| NEXgen checks | All deterministic checks `[ok]`; only its pre-commit baseline asks for `--set-anchor` |
| GitNexus lobby | 86 nodes / 76 edges; status `up-to-date` at `f5eb89d` |
| GitNexus AviationChat | FTS repaired, interrupted incremental state forced a clean full rebuild; 50,194 nodes / 119,624 edges / 546 clusters / 300 flows; status `up-to-date` at `ae37edc` |

## Deferred Findings

The fan-out remains non-zero only for two known AviationChat findings outside this navigation pass:

1. `scripts/git-hooks/INDEX.md` names `.git/hooks`, while the repository uses `core.hooksPath=.githooks`;
   the documented board-hook installation needs retirement or redesign, not a pointer-only edit.
2. `frontend/test-results/` is ignored generated Playwright output; creating a tracked `INDEX.md` inside it
   would be false documentation. The linter needs a separate generated-output exemption.

## Your Actions

`/close-task-merge-tree` was invoked for the lobby branch. It owns the lobby commit, push, merge to `main`,
Jira Dev Record, transition to Done, and branch pruning. AviationChat and NEXgen remain separate repositories;
their explicit-path commands are in their project-local walkthroughs.

After those two project-local commits exist, update commit-based baselines and GitNexus stamps:

```bash
python3 .agents/scripts/check_maps.py --set-anchor --all
node .gitnexus/run.cjs analyze --index-only
node Projects/AGY_AVIATIONCHAT/.gitnexus/run.cjs analyze --index-only Projects/AGY_AVIATIONCHAT
```
