---
name: bmad_code_review_sudo_fix
description: "Activates whenever the bmad-code-review skill or workflow runs (any agent, any platform). Run the review end-to-end in one pass — never halt to hand steps back to the user — then report findings to code-review.md. Never flip the story to done; stop at review."
activation: Model Decision (auto when the bmad-code-review skill or workflow runs)
---

# BMAD Code Review — Run-to-Completion Adapter

`bmad-code-review` is authored for a multi-agent swarm that halts to spawn subagents and asks for
confirmation at each checkpoint. Here it runs as ONE uninterrupted pass. The procedure (three review
layers → triage → present) is unchanged; only the orchestration below is overridden.

## The contract
- **Run to completion in one pass.** Carry out every step yourself — including anything the workflow
  phrases as "launch subagents," "generate prompt files and halt," or "stop for confirmation." Run the
  three layers sequentially, or fan them out as real subagents if you have them, but complete and
  synthesize all three before returning. Never return a partial review.
- **Silent defaults, no checkpoints.** Auto-answer the Step 1 questions; skip every confirmation pause.
- **Stop at `review`, never `done`.** The human close-out (`/sudo-update-sprint-memory`) owns `review → done`.
- **The one allowed stop:** a genuine `decision_needed` finding (Step 4) — a judgment call only the human can make.

## Step 1 — Context (auto-answer, don't ask)
| Workflow question | Answer |
|---|---|
| What to review? | Uncommitted changes (`git diff HEAD`) — staged + unstaged. |
| Spec/story file? | The path from the user's prompt; else scan `_bmad/bmm/stories/` for `Status: ready-for-review`/`review`; else `review_mode = "no-spec"`. |
| Confirm summary? | Print a one-line summary (files, ±lines, mode) and continue. |
| Chunk a large diff? | No — review the full diff. |

## Step 2 — Review (run all three layers, then continue)
1. **Blind Hunter** — `{diff_output}` ONLY (no spec, no project context). Bugs, logic errors, security, smells → findings list.
2. **Edge Case Hunter** — diff + full project read. Every branch, boundary, null, error path, race, type-coercion edge → list with `location`, `trigger_condition`, `potential_consequence`.
3. **Acceptance Auditor** (skip if `no-spec`) — diff vs the spec/story ACs. Violations, deviations, missing implementation → list with title, AC reference, evidence.

Accumulate findings internally (no intermediate summaries), then go straight to triage.

## Step 3 — Triage
Run the workflow's normalization, deduplication, and classification exactly as written — without pausing.

## Step 4 — Present & act
- **`decision_needed` findings** — the one exception: present them clearly and halt for the human's call.
- **Patch findings** — never ask how to handle them. If `{spec_file}` is set, leave them as action items in the story file; else list each (file, line, suggested fix) in the output. Do not auto-apply.
- **Status** — ensure the story is at `review` (idempotent — the dev step normally set it already). **Never write `done`** to the story file or `sprint-status.yaml`; this overrides step-04-present's `done` default.

## Close-out
1. Confirm: `✅ Story <key> reviewed — left at review for human close-out. Run /sudo-update-sprint-memory to advance review → done.`
2. Remind: `🚀 Commit & push: git add -A && git commit -m 'feat(epic-N): Story X.Y.Z — <Title>' && git push`
