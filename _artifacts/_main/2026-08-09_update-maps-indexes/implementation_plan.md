---
IsArtifact: true
ArtifactMetadata:
  title: Update maps and indexes after artifact year/month reorganization
  type: implementation_plan
  date: 2026-08-09
---

# Implementation Plan — Update Maps and Indexes

## Goal

Reconcile the lobby and maintained project navigation artifacts against disk after the June and July
home-base sessions moved under year/month folders. Preserve unrelated parallel work and leave every
deterministic or substantive exception explicit.

## Approved scope

1. Reconcile the home-base artifact ledgers:
   - update 56 moved paths in `_artifacts/_main/INDEX.md`;
   - add missing recent session rows;
   - create `2026/06/INDEX.md` and `2026/07/INDEX.md`;
   - backfill uncovered root-ledger sessions, restore newest-first order, and archive overflow to keep
     the live ledger at roughly 50 rows.
2. Repair navigation references affected by the move in the root ledger, active context, archive, and
   `_artifacts` README structure descriptions.
3. Refresh only the `## Open Work` manifest in the home-base `todo_list.md`, preserving Daniel's prose.
4. Reconcile AviationChat's new Epic 19 session and NEXgen's ledger ordering in their owning repos.
5. Delete the approved duplicate `2026/06/proposal_graphrag_executiblity.md`; its canonical content
   already lives in `2026-08-07_command-center-workflow-memory/implementation_plan.md`.
6. Re-run the fan-out linter. Keep the generated Playwright-output false positive and the obsolete
   AviationChat board-hook instructions visible as deferred defects rather than disguising them.
7. Refresh GitNexus for the lobby and AviationChat during this pass, then rerun after commit if the
   commit-based freshness stamp changes.

## Scope addendum — make Task close-out native in Codex

The close-out preflight exposed a command-surface defect that belongs in SCC-59 before the branch
lands. The command was not absent from disk: `sync-agents.ps1` had copied it to
`~/.codex/prompts/close-task-merge-tree.md`. The defect is that Codex custom prompts are deprecated and
are namespaced as `/prompts:close-task-merge-tree`; Codex does not turn that file into the documented
top-level `/close-task-merge-tree`. The supported reusable surface is an Agent Skill, selected with
`/skills` or `$close-task-merge-tree`. Unlike the other close-out workflows, this command has no native
skill twin, so it was also absent from the Codex skill catalog.

8. Add `.agents/skills/close-task-merge-tree/SKILL.md` as a thin launcher that reads and executes the
   canonical `.agents/commands/close-task-merge-tree.md` end to end; include validated Codex UI metadata
   in `agents/openai.yaml`.
9. Limit the command wrapper to `platforms: [opencode, antigravity]`. Claude receives the native skill
   through `.claude/skills`; Codex discovers it directly from `.agents/skills`; neither should retain a
   second, stale command/prompt entry.
10. Correct `.agents/commands/INDEX.md`, `.agents/skills/INDEX.md`, `/sync-agents`, and the operator
    quick-reference so they state the real platform syntax: direct `/close-task-merge-tree` where the
    command/skill surface supports it; `/skills` or `$close-task-merge-tree` in Codex. Remove the stale
    `/sync-agents` claims that project targets and `-Maintained` still vendor the tier-1 toolkit; its engine
    has already refused both since the thin-model migration. Do not claim Codex supports arbitrary
    repo-defined top-level slash commands.
11. Add a focused regression test asserting that this high-risk merge workflow has a native skill twin,
    that the twin delegates to the canonical command body, and that the deprecated Codex prompt copy is
    excluded by frontmatter.
12. Validate the new skill, run the workflow suite, dry-run and then apply `/sync-agents`, verify the
    Claude/opencode/Antigravity mirrors and Codex skill discovery layout, and confirm the stale Codex
    prompt is pruned. A new Codex chat/reload is required before its skill catalog refreshes.
13. Update the walkthrough, commit and push this addendum on `chore/SCC-59-update-maps-indexes`, refresh
    the lobby and AviationChat GitNexus commit stamps, then resume `/close-task-merge-tree` for the
    three-repository close-out already requested.

## Boundaries

- Do not edit or stage unrelated SCC-56 or operator prose changes.
- Do not create an INDEX inside generated `frontend/test-results` output.
- Do not rewrite the obsolete AviationChat hook behavior during this navigation-only pass.
- Keep `.agents/commands/close-task-merge-tree.md` as the single source of workflow behavior; the new
  skill must be a launcher, not a duplicated 11 KB body.
- Do not promise a Codex top-level custom slash command that the product does not support.
- Commit, push, merge, and prune only through the already-invoked `/close-task-merge-tree` contract.

## Verification

- Run `python3 .agents/scripts/check_maps.py --all` and classify every remaining failure.
- Verify every June/July session folder has a matching monthly and `_main` row.
- Verify the live root ledger has 50 newest rows and every archived row remains present.
- Verify open-work manifests match disk and Daniel's prose diff is preserved.
- Verify only approved files changed in each repository.
- Run the skill validator and the focused command-surface regression test.
- Run `python3 .agents/scripts/tests/run_all.py` and `python3 .agents/scripts/workflow_lint.py`.
- Run `sync-agents.ps1 -WhatIf`, then the real sync; verify the deprecated Codex prompt is gone and the
  repo-native skill exists on the supported discovery surface.
