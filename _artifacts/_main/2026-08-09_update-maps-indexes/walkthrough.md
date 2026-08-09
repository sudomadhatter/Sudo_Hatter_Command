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
- [x] Trace the missing Codex `/close-task-merge-tree` entry to the product boundary: the synced custom
  prompt was available only as `/prompts:close-task-merge-tree`, while no native skill existed.
- [x] Add and validate the native `close-task-merge-tree` skill, retain one canonical guarded command body,
  and retire the duplicate Claude command plus deprecated Codex prompt copy.
- [x] Correct `/sync-agents`: its engine already served the thin model, but its command text still promised
  retired project `-Target` / `-Maintained` vendoring and identical top-level Codex slash commands.
- [x] Sync and verify every supported surface, including the negative checks for the retired prompt/duplicate.

## Evidence

| Claim | Proof |
|---|---|
| Lobby deterministic map/index checks | `python3 .agents/scripts/check_maps.py --all` → AUTO, repo-map paths, folder coverage, INDEX paths, level-2, depth-3, structure, context, and Tier-2 law all `[ok]` |
| Month coverage | June: 25 folders / 25 rows; July: 31 folders / 31 rows |
| Shared ledger coverage | 83 `_main` index rows; zero missing from live + archive; live 50, archive 58, zero duplicate ledger keys |
| NEXgen checks | All deterministic checks `[ok]`; only its pre-commit baseline asks for `--set-anchor` |
| GitNexus lobby | 86 nodes / 76 edges; status `up-to-date` at `f5eb89d` |
| GitNexus AviationChat | FTS repaired, interrupted incremental state forced a clean full rebuild; 50,194 nodes / 119,624 edges / 546 clusters / 300 flows; status `up-to-date` at `ae37edc` |
| Native skill structure | bundled `quick_validate.py` → `Skill is valid!` (PyYAML isolated under `/private/tmp`) |
| Command-surface regression | `test_command_surfaces.py` → 5/5 passed |
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` → 10/10 files passed; new aggregate totals include 103/103 Jira-feed cases and 39/39 Task-preflight cases |
| Toolkit lint | `workflow_lint.py --project Projects/NEXgen-VR-Director` → 0 errors, 2 pre-existing warnings, 10 info; the default active AviationChat target separately reports its pre-existing missing Story 19.5 file |
| Sync publish | Claude 19 commands + native skill; opencode 48 commands; Antigravity 27 workflows; Codex 18 legacy prompts + 56 BMAD skills |
| Surface verification | native skill present in `.agents/skills` and `.claude/skills`; direct command present in opencode + Antigravity; duplicate `.claude/commands` and `~/.codex/prompts` copies absent |
| Maps + SOP | lobby `check_maps.py` all `[ok]`; `sop_currency.py` accepts the actual usage-surface paths with the quick-reference in the same change |

## Decisions Made

- Codex cannot be made to expose an arbitrary repo-defined top-level `/close-task-merge-tree`. The supported
  entry is `/skills` → `close-task-merge-tree` or `$close-task-merge-tree`; deprecated custom prompts remain
  namespaced `/prompts:<name>`.
- `.agents/commands/close-task-merge-tree.md` remains the single workflow body. The native skill is a thin
  launcher so the merge, Jira, and pruning gates cannot drift between tools.
- The sync engine did not need a new copy path: it already publishes `.agents/skills` to Claude and Codex
  already discovers the repo directory. Its stale operator instructions were corrected to match that engine.
- A command with a native Claude/Codex skill twin uses `platforms: [opencode, antigravity]`, preventing a
  duplicate Claude menu entry and a deprecated Codex prompt twin while preserving both direct command menus.

## Pitfalls Found

- File existence was a false positive for availability: `~/.codex/prompts/close-task-merge-tree.md` existed,
  but Codex could only expose it under the `/prompts:` namespace after a restart.
- `/sync-agents` documentation had survived the thin-model migration even though the executable has loudly
  rejected project targets and `-Maintained` since 2026-08-07.
- Codex skill catalogs are captured when a chat starts. This running chat cannot prove picker visibility after
  the edit; a new chat or IDE reload is required even though disk layout and validation are green.
- The bundled skill validator assumes PyYAML. This machine lacked it, so validation used a temporary dependency
  under `/private/tmp` rather than modifying the machine Python installation.

## Deferred Findings

The fan-out remains non-zero only for two known AviationChat findings outside this navigation pass:

1. `scripts/git-hooks/INDEX.md` names `.git/hooks`, while the repository uses `core.hooksPath=.githooks`;
   the documented board-hook installation needs retirement or redesign, not a pointer-only edit.
2. `frontend/test-results/` is ignored generated Playwright output; creating a tracked `INDEX.md` inside it
   would be false documentation. The linter needs a separate generated-output exemption.

Additional existing toolkit warnings remain out of scope: `sudo-push-e2e.md` has no frontmatter and
`sudo-merge-epic-workingtrees.md` does not point at `git-policy.md`. The active AviationChat board also names
Story 19.5 without a corresponding story file. None was introduced or concealed by SCC-59.

## Gate Verdict

**Verdict: PASS.** The native skill validates, the focused surface contract passes 5/5, the full enforcement
suite passes 10/10 files, toolkit lint has zero errors on the neutral NEXgen target, map/index checks are clean,
and SOP currency is satisfied. No deployable surface exists in the command-center repository.

## Follow-ons / Still Owed

- Start a new Codex chat or reload the IDE, then use `/skills` or `$close-task-merge-tree`; restart opencode to
  refresh its global command catalog.
- Address the explicitly deferred AviationChat map/linter defects and the pre-existing toolkit warnings in
  their own scoped Tasks.

## Your Actions

The operator ruled that the whole three-repository reconciliation belongs in this close-out. Git still
requires one commit per repository, and AviationChat's armed gate requires its own AVCH key, but this
close-out owns all three landings before SCC-59 moves to Done: NEXgen under SCC-59, AviationChat under
AVCH-51 on the existing Epic 19 branch, then the lobby merge and prune.

The invoked Task close-out owns the remaining repository landings, Jira records, branch pruning, and the
commit-based baseline/GitNexus refresh. After the commits exist, run:

```bash
python3 .agents/scripts/check_maps.py --set-anchor --all
node .gitnexus/run.cjs analyze --index-only
node Projects/AGY_AVIATIONCHAT/.gitnexus/run.cjs analyze --index-only Projects/AGY_AVIATIONCHAT
```
