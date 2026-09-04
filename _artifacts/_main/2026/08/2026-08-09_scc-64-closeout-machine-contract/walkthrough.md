---
IsArtifact: true
ArtifactMetadata:
  title: SCC-64 Task close-out machine contract — walkthrough
  type: walkthrough
  date: 2026-08-09
---

# SCC-64 — the close-out target becomes a machine contract

Lane 1 of the agnostic-system program
([plan](../2026-08-09_agnostic-system-program/implementation_plan.md), approved 2026-08-09).

## What was wrong

The 2026-08-09 debrief of the failed Codex session landed on one structural weakness: the current
task is **inferred** from seven independent surfaces (branch, artifact folder, Jira ticket,
active-project pointer, dirty files, arguments, cwd), and when they disagree the agent picks a
winner. SCC-61 fixed the worst case at the **prompt** level — pin `--repo`/`--branch`, read the
echoed header. But a prose guard costs diligence, and diligence is the first thing a weaker model
loses. The preflight still *ran* without any statement of intent; `workflow_lint` still went
red/green on whichever product project sat in `.agents/active-project.txt`; stray memory files in a
sibling's tree still looked like generic dirt to be "cleaned".

## Task Checklist

- [x] `task_preflight.py`: `--expect-key` **required** — bare run exits 2 naming the flag; a
      resolved branch carrying a different key exits 2 naming **both keys** ("aimed at ANOTHER
      lane's branch"). Keys case-normalized.
- [x] `task_preflight.py`: `task.yaml` manifest cross-check — a manifest declaring this
      `task_key` must agree on `branch` (error on mismatch); absence is a **warning** that prints
      the schema.
- [x] `task_preflight.py`: dirty files under `_artifacts/_memory/` reported in their own block
      with the park-don't-sweep instruction, split from the generic uncommitted count.
- [x] `task_preflight.py`: in a no-deploy repo the printed gate is
      `workflow_lint.py --toolkit-only`.
- [x] `workflow_lint.py`: `--toolkit-only` stops **before** `resolve_project_root` (which falls
      back to cwd, then `active-project.txt`); refuses `--project` alongside; dies loudly outside
      a lobby.
- [x] `close-task-merge-tree.md`: Step 0 pins `EXPECTED_KEY` and authors `task.yaml`; Step 1
      passes `--expect-key`; preflight table gains **intent** + **manifest** rows; rules-in-force
      now points at `worktree-per-story.md` §"cwd is not intent".
- [x] `worktree-per-story.md`: notes the preflight's guard is now mechanical; the discipline
      still covers every other script.
- [x] Tests: 8 new SCC-64 cases in `test_task_preflight.py` (48/48), 3 in
      `test_workflow_lint.py` (22/22) including the bare-run contrast control.
- [x] SOP currency: §6 step 1 + §10 update block in `sudo_workflows_testing.md`.

## Evidence

| Gate | Result |
|---|---|
| `tests/run_all.py` | **10/10 files passed**, exit 0 (48/48 + 22/22 in the extended files) |
| `workflow_lint.py --toolkit-only` | exit 1 — 0 errors, **3 warnings (was 4)**: this change's rules-pointer fixed the pre-existing `close-task-merge-tree.md` rule-pointers warning; the remaining 3 pre-date the lane |
| `sop_currency.py --paths <changed>` | exit 0 |
| `sync-agents.ps1` | exit 0 — mirrors regenerated (`.agents/workflows/`, `.opencode/commands/`, `.sync-manifest.json`) |
| `task_preflight.py --expect-key SCC-64 …` | dogfood: `intent: SCC-64 matches the branch key` + `manifest: … agrees` (this task carries the first real `task.yaml`) |

## Decisions

- **Missing manifest = warning, not error.** Adoption is incremental; every pre-SCC-64 task has no
  manifest, and a check that reddens all history gets routed around. The warning prints the schema
  so authoring it is copy-paste.
- **`--toolkit-only` selection is derived, not asserted**: the preflight prints it when the repo
  has no deployable surface — the same derived fact that already decides the LANE.
- **The scripts now hold the assertion SCC-61 said they couldn't** — because SCC-61's missing
  piece was an *intent input*, not script logic. `--expect-key` supplies the intent; the
  mechanical comparison follows.

## Pitfalls

- **The fixture manifest broke the "no `_artifacts/` tree" test** — writing a default `task.yaml`
  into every fixture created the very tree that check looks for. The case now sets
  `manifest=False` explicitly; the failure was the check working.
- **A bare `=====` separator dies in zsh** (`=cmd` expansion), killing the rest of a compound
  gate command. Same family as `| tail` hiding an exit code: quote separators, run gates unpiped.

## Your Actions

- None required for this lane. Lanes 2 (memory routing) and 3 (uniform doors) follow per the
  program plan.
