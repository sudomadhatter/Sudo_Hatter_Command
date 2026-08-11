---
IsArtifact: true
ArtifactMetadata:
  title: SCC-83 walkthrough - the prose nobody checked, and the two doctrines that had gone stale inside it
  type: walkthrough
  date: 2026-08-11
---

# SCC-83 — Walkthrough: a path check that found stale *law*

**Date:** 2026-08-11 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Branch:** `chore/SCC-83-sop-content-audit` · **Base:** `ef0af3a`
**Subtasks:** SCC-84 · SCC-85 · SCC-86 · SCC-87

> **⛔ NOT merged.** Pushed, gated, handed back for `/smh-close-task-merge-tree`.

## Task Checklist

- [x] **SCC-87** — T9 added to `test_sops_prds_folder.py`, RED first, **16 controls**
  - Four of them exist because the RED found false-positive classes the plan had not predicted
- [x] **SCC-84/85/86** — all **12** genuine references fixed; **0 findings from a worktree AND from
      the main checkout**
- [x] **A8 / F4** — `INDEX.md` now states T9's scope, its environment-dependent reach, and that
      `git log` dates are meaningless in this folder
- [x] Gates: `run_all` 12/12 exit 0 · lint 0/0 exit 0 · `sop_currency` exit 0

## The question that produced this

*"Were you triggered to actually check the whole folder to make sure it's not stale?"*

**No — and nothing would have.** All three mechanisms answer *"does this pointer resolve."* None
answers *"is what this page says still true."* `check_maps` reads backticked paths **only inside
table rows**; T3 reads **markdown links**. A path in a sentence was seen by nothing.

## ⭐ The two findings that justify the whole ticket

Neither is a broken link. Both are **stale doctrine** that a path check walked me into.

**1. The artifact bucket rule taught the model that was inverted a fortnight earlier.**
`file_folder_structure+maintaining.md` said artifacts go *"where you work FROM (your cwd)"* — so a
project's history landed in the lobby whenever a chat happened to start there. That rule was
**inverted on 2026-07-30** (`project-first-artifact-locality`): location follows **ownership**,
project-local *even when the chat starts in the lobby*. The page taught the old model for twelve
days, and the only reason I looked at that paragraph is that a dead `_artifacts/AGY_AVIATIONCHAT/`
path sat inside it.

**2. The very next line named a source that was retired as an agent input.** It said *"pick up"*
surfaces `_my_resources/open_tasks/todo_list.md`. `AGENTS.md` §7 says **⛔ NOT from** that file —
retired 2026-08-09 because it is personal notes, it goes stale, and it duplicates live tickets.
**No path check could ever have caught this one** — the file exists. A human reading the paragraph
caught it, and the dead path is what put a human in the paragraph.

**3. And the SCC-63 over-rename had a survivor.** `tea_testing_guide.md` said
`cicd-code-review-tea-9-tia-ci.md`; the file on disk is `sudo-code-review-…`. Commit `3eea4d0`
fixed exactly this in 5 masters + 2 rules — **and missed this doc, because at that moment it lived
in `_my_resources/`, which the sweep is forbidden to scan.** The SCC-74 thesis demonstrating itself.

## ⭐ 181 → 28 → 12: the number was the hard part

| Sweep | Reported | Why it was wrong |
|---|---|---|
| First, crude | **181** | bare filenames counted as paths; run from a worktree where `Projects/` is an empty stub |
| Ground-truthed | 28 | separated bare names, project-relative, non-path tokens |
| T9, from a worktree | 25 | still counted things a stubbed project owns |
| **T9, from the main checkout** | **12** | the truth |

**The 25-vs-12 gap was nearly a shipped defect.** Fix the 12 and every lane would still have gone
red on 13 findings its author could not fix — which is how a gate gets ignored, then deleted. So
T9 asserts only what is provable **without** the projects when any is stubbed, and prints how many
it could not see. A reduced run is visible; it never reads as a clean one.

## The RED earned its keep four times

Every one of these was found by running it, not by designing it:

1. **Relative tokens.** `../workspace-standard.md` is correct and T9 called it dead — I resolved
   against the repo root instead of the containing file.
2. **The explicit `Projects/` form.** My A3c control covered `backend/…` (first segment absent) but
   `Projects/AGY_AVIATIONCHAT/scripts/` sails past it, because `Projects/` *does* exist. **The
   control had a hole in exactly the trap it was written for.**
3. **A shadowed parameter.** The mis-path lookup assigned `base = Path(t).name`, clobbering the
   `base` parameter after the first token. The suite crashed rather than lying — the good outcome.
4. **A fixture asserting the wrong target.** `../top.md` from `fx/docs` is `fx/top.md`; I had
   created `fx/docs/top.md`, so the control failed for its own reason, not the code's.

Three more classes surfaced when T9 ran against the real docs and flagged things that were **not
defects** — each now a control:

- **Struck-through paths.** Line 11 already read ``~~`…master-implementation-plan.md`~~ — **gone**``.
  Reporting it asks the author to delete the line recording the removal.
- **Provenance folders.** *"Consolidated from `_my_resources/_quick_reference/`"* is the doc doing
  its job. Exempt at folder level; a **file** under them is not — that is a live instruction to open
  something that moved, and two of those were real defects.
- **Runtime output.** `_artifacts/_autopilot-run.log` exists only while a run is live.

Same inversion as T4's `DISCUSSED_AS_RETIRED`, one tier down: **the literal appears most often in
the prose about its own removal.**

## Evidence

**RED** (worktree, after the controls were corrected):
```
T9 controls green: 13
[FAIL] T9 every prose path reference resolves:
    autopilot_bmad_dev_loop.md -> .claude/commands/cicd-autopilot-claude.md (moved -> .agents/commands/...)
    jira_integration_guide.md  -> _my_resources/_quick_reference/git_walkthrough_settings.md (moved -> docs/_scc_sops_prds/...)
    jira_integration_guide.md  -> _my_resources/_quick_reference/jira_manual.md (moved -> docs/_scc_sops_prds/...)
```
**GREEN**, both environments:
```
WORKTREE (9 stubs): 0 finding(s)      MAIN CHECKOUT: 0 finding(s), 1 stubbed
T9 controls green: 16 · -- 34/34 passed -- · run_all 12/12 exit 0
```

## Your Actions

Branch pushed, preflight to follow. **Landing-order:** `chore/SCC-77-main-write-gate` also touches
`workflows_testing_SOP.md`; `git merge-tree` verified clean either way — whoever lands second merges
main down.

**Still owed, unchanged and deliberately not done here:** whether `tea_testing_guide.md` belongs in
the lobby at all (48 project-relative refs) is an **AVCH** architecture call; AGY's stale
`sudo_workflows_testing.md` needs its own key in that repo.
