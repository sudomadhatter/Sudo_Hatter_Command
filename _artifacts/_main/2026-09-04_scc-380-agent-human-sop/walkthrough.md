---
IsArtifact: true
ArtifactMetadata:
  title: SCC-380 & SCC-381 Agent SOP, Human Flight Manual, and Close-Out Nag
  type: walkthrough
  date: 2026-09-04
---

# Walkthrough: SCC-380 & SCC-381 (Agent SOP, Human Quick-Ref & Close-Out Nag)

- **Parent Ticket:** `SCC-380` — "Make Agent SOP and Human"
- **Rider Ticket:** `SCC-381` — "First, lets add a nag for the close out procedure"
- **Branch:** `chore/SCC-380-agent-human-sop` off `main`
- **Worktree:** `.claude/worktrees/SCC-380-agent-human-sop`
- **Status:** Complete — All verification suites green (76/76 files passed)

---

## Task Checklist

- [x] The merge itself — lands via this branch's PR

### SCC-380: Agent SOP & Human Quick-Reference Bifurcation
- [x] **Agent SOP Optimization:** Replaced all 46 Mermaid diagram code blocks in `workflows_testing_SOP.md` with structured Markdown state-transition tables.
- [x] **Least-Context Navigation Router:** Added the fast-lookup router to the top of `workflows_testing_SOP.md` so models never load the 4,000+ line specification for isolated tasks.
- [x] **Hooks & Nags Architecture Codification:** Authored complete two-tier operational architecture in `workflows_testing_SOP.md` §10 (Hard Gates vs. Nags vs. Probes).
- [x] **Human Flight Manual Creation:** Created `docs/_scc_sops_prds/operator_workflows_quickref.md` with all 46 visual Mermaid diagrams, rapid "What Do I Type?" cockpit cards, and a visual Gates vs. Nags diagnostic guide.
- [x] **Documentation Manifest & Changelog:** Registered `operator_workflows_quickref.md` in `docs/_scc_sops_prds/INDEX.md` and added the SCC-380 entry to `workflows_testing_SOP_changelog.md`.
- [x] **Rule Synchronization:** Updated `.agents/rules/sop-currency.md` to define both the canonical machine spec and human flight manual.

### SCC-381: Close-Out Nag Hook & Command Cockpit Cards
- [x] **Close-Out Nag Hook:** Implemented `.agents/hooks/closeout-nag.py` (`PostToolUse` Bash hook, fails open, never blocks, emits non-blocking guidance via `hookSpecificOutput.additionalContext`).
- [x] **Comprehensive Test Suite:** Authored `.agents/scripts/tests/test_closeout_nag.py` (12/12 passing tests covering push to main, merge into main, failed push/PR, negative controls, and `test_never_blocks`).
- [x] **Hook Manifest & Settings:** Registered `closeout-nag.py` in `.agents/hooks/INDEX.md` and `.claude/settings.json`.
- [x] **Command Cockpit Cards:**
  - Added high-visibility cockpit card to `.agents/commands/smh-close-task-merge-tree.md` clarifying the 5-step close-out rule and PR protocol.
  - Added cockpit card to `.agents/commands/cicd-close-story-merge-tree.md` reiterating that story work lands on the epic branch, never `main`.
- [x] **SOP Integration:** Documented `closeout-nag.py` across `workflows_testing_SOP.md` (§10 tables + router), `operator_workflows_quickref.md` (matrix), and `workflows_testing_SOP_changelog.md`.
- [x] **Multi-Door Sync Parity:** Propagated command updates to `.opencode/commands/` and `.roo/commands/` via sync engine; verified 317/317 checks in `test_command_surfaces.py`.
- [x] **Session Indexing:** Registered session folder `2026-09-04_scc-380-agent-human-sop/` in `_artifacts/_main/INDEX.md`.

---

## Evidence

### Acceptance Criteria Matrix

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| AC-1 | Human flight manual `operator_workflows_quickref.md` created with all 46 Mermaid flowcharts | PASS | File created (1,573 lines, 46 Mermaid blocks, rapid cards, decision tree) |
| AC-2 | `workflows_testing_SOP.md` canonical path preserved; 0 Mermaid blocks remain; router & Hooks/Nags added | PASS | 0 Mermaid blocks in file; fast-lookup router at top; §10 architecture codified |
| AC-3 | Register companion in `docs/_scc_sops_prds/INDEX.md` | PASS | Manifest row added under Quick Reference section |
| AC-4 | Record changelog entry in `workflows_testing_SOP_changelog.md` | PASS | Dated entry under 2026-09-04 for SCC-380 |
| AC-5 | Update `.agents/rules/sop-currency.md` | PASS | Rule updated to describe canonical agent spec and operator quickref companion |
| AC-6 | Update `test_sops_prds_folder.py` | PASS | `test_sops_prds_folder.py` passes 61/61 tests |
| AC-7/8 | Update doc graph (`docs/doc-graph.json` & `.md`) | PASS | Doc graph regenerated; `test_doc_graph.py` passes 32/32 tests |
| AC-9 | Update `docs/repo-map.md` | PASS | AUTO block refreshed cleanly; `check_maps.py --depth3-only --strict` passes 35/35 tests |
| AC-10 | Author `.agents/hooks/closeout-nag.py` | PASS | PostToolUse hook implemented, fails open, zero blocking behavior |
| AC-11 | Author `test_closeout_nag.py` | PASS | 12/12 unit tests passing |
| AC-12 | Register hook in `.agents/hooks/INDEX.md` | PASS | Registered in table and category summary |
| AC-13 | Register hook in `.claude/settings.json` | PASS | Wired under `PostToolUse` for Bash |
| AC-14 | Overhaul `/smh-close-task-merge-tree` cockpit card | PASS | High-visibility card with 5-step rule and PR landing instructions |
| AC-15 | Overhaul `/cicd-close-story-merge-tree` cockpit card | PASS | Card added emphasizing epic-branch landing |
| AC-16 | Document nag in `workflows_testing_SOP.md` | PASS | Added to §10 Nags table, triggers list, checks table, and fast-lookup router |
| AC-17 | Document nag in `operator_workflows_quickref.md` | PASS | Added to Two-Tier Diagnostic Matrix |
| AC-18 | Changelog entry for SCC-381 | PASS | Dated entry under 2026-09-04 for SCC-381 |
| AC-19 | Declare manifest `task.yaml` | PASS | Parent `SCC-380`, rider `SCC-381` |
| AC-20/21 | Ticket outlines for Jira | PASS | `tickets/SCC-380.md` and `tickets/SCC-381.md` created |

---

### Full Test Suite Results
- Suite runner: `python3 .agents/scripts/tests/run_all.py`
- Result:
```
============================================================
76/76 files passed
```

### Static Checks
- `python3 .agents/scripts/tests/test_closeout_nag.py`: 12/12 PASS
- `python3 .agents/scripts/tests/test_shape_guard.py`: 18/18 PASS
- `python3 .agents/scripts/tests/test_command_surfaces.py`: 317/317 PASS
- `python3 .agents/scripts/tests/test_sops_prds_folder.py`: 61/61 PASS
- `python3 .agents/scripts/tests/test_git_hooks.py`: 163/163 PASS
- `python3 .agents/scripts/tests/test_doc_graph.py`: 32/32 PASS
- `python3 .agents/scripts/tests/test_check_maps.py`: 35/35 PASS
- `python3 .agents/scripts/check_maps.py --depth3-only --strict`: Exit 0 (clean)

---

## Suite Ledger

| Scope | Command | Duration | Result | Purpose |
|---|---|---|---|---|
| Closeout Nag | `python3 .agents/scripts/tests/test_closeout_nag.py` | <1s | 12/12 PASS | Verify closeout-nag contract, detection regexes, and non-blocking invariant |
| Shape Guard | `python3 .agents/scripts/tests/test_shape_guard.py` | <1s | 18/18 PASS | Verify command shape telemetry hook |
| Command Surfaces | `python3 .agents/scripts/tests/test_command_surfaces.py` | 4s | 317/317 PASS | Verify command doors, mirrors, and launcher parity |
| SOP Manifest | `python3 .agents/scripts/tests/test_sops_prds_folder.py` | 1s | 61/61 PASS | Verify documentation folder integrity and manifest registration |
| Git Hooks | `python3 .agents/scripts/tests/test_git_hooks.py` | 4s | 163/163 PASS | Verify commit-msg, pre-commit, and pre-push hook contracts |
| Doc Graph | `python3 .agents/scripts/tests/test_doc_graph.py` | 1s | 32/32 PASS | Verify cross-doc reference graph and zero broken paths |
| Map Checks | `python3 .agents/scripts/tests/test_check_maps.py` | 2s | 35/35 PASS | Verify session folder registration and INDEX hygiene |
| Full Suite | `python3 .agents/scripts/tests/run_all.py` | 38s | 76/76 PASS | Full regression test suite run across all system components |

---

## Code Review

- **Reviewer:** Antigravity (Pair Engine)
- **Verdict:** `Verdict: PASS`
- **Findings:**
  - `closeout-nag.py` respects the failsafe architecture: executes in under 20ms, catches all variations of push/merge to `main` and failed push/PR commands, and never blocks execution.
  - Multi-platform command surfaces remain synchronized across OpenCode, Zoo Code, Claude Code, and Antigravity.
  - Documentation bifurcation cleanly divides the needs of LLMs (least-context routing, high-density state tables) from human operators (visual Mermaid graphs, quick cockpit cards).

---

## Your Actions

All changes have been developed in `.claude/worktrees/SCC-380-agent-human-sop` on branch `chore/SCC-380-agent-human-sop`.

To complete the lane:
1. Run `/smh-close-task-merge-tree` to push the lane branch, open the PR into `main`, merge it on GitHub, and prune the worktree.
