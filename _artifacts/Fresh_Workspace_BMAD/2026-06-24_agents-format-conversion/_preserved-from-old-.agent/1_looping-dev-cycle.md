---
description: Looping multi-model dev cycle — drives a story through 5 stages alternating GLM 5.2 (primary) and Opus 4.8 (subagents). Plan → audit → dev → review → fix+sign-off+close. Invoked with /1_looping-dev-cycle.
---

# Looping Multi-Model Dev Cycle (`/1_looping-dev-cycle`)

> Drives a single story from `ready-for-dev` to `done` through five stages. Two stages
> run on **Opus 4.8** (via the `opus-auditor` and `opus-reviewer` subagents); three run
> on the primary **GLM 5.2** session. Opus stages execute as child sessions via the Task
> tool and return structured artifacts. No manual paste handoff.

## Pre-Flight

1. **Resolve the story.** Read `_bmad-output/implementation-artifacts/sprint-status.yaml`
   and find the first story with status `ready-for-dev` (or accept a story path from
   Daniel). Store `story_path`, `story_key`.
2. **Create the run folder:** `_opencode_artifacts/<YYYY-MM-DD>_<story-slug>/`. All
   artifacts for this run land here. Store `artifact_dir` and `slug`.
3. **Confirm subagents registered:** `opus-auditor` and `opus-reviewer` must appear as
   invokable subagent types (defined in `.opencode/agent/`). If either is missing, HALT
   and tell Daniel to create them first.
4. **Capture baseline commit:** Run `git rev-parse HEAD` → store as `baseline_commit`
   (used by the reviewer in Stage 4).

## Stage 1 — Plan (GLM)

**Goal:** Produce an `implementation_plan.md` for the story.

1. Load the story file. Extract: Story summary, Acceptance Criteria, Tasks/Subtasks,
   Dev Notes.
2. Read `_bmad-output/project-context.md` + the relevant component spec.
3. Write `implementation_plan.md` to `{artifact_dir}/`. Follow the plan-first protocol
   from `AGENTS.md` §1: file-by-file changes, AC ↔ task traceability, test strategy,
   verification approach.
4. Emit the absolute path to the plan.

> **Constitution carve-out (loop-only):** Do NOT prompt Daniel for the word "approved"
> here. Within `/1_looping-dev-cycle`, the Opus auditor's `Go` verdict (Stage 2)
> substitutes for the manual approval gate. See `.agent/rules/constitution.md` →
> "Exception — `/1_looping-dev-cycle` only". This applies ONLY inside this workflow.

## Stage 2 — Audit (Opus 4.8 via opus-auditor)

**Goal:** Adversarial pre-dev audit of the plan; catch gaps before code is written.

1. **Invoke the `opus-auditor` subagent** via the Task tool. Pass in the task prompt:
   - `plan_path` = `{artifact_dir}/implementation_plan.md`
   - `story_path` = `{story_path}`
   - `slug` = `{slug}`
   - `artifact_dir` = `{artifact_dir}`
   - A short note: "Run the self-audit-stress-test workflow against this plan. Write
     findings to `{artifact_dir}/audit-findings.md`. Return verdict + path + counts."

2. **On return**, read `{artifact_dir}/audit-findings.md`. Extract `verdict`.

3. **Branch on verdict:**
   - `Go` → proceed to Stage 3.
   - `NEEDS-REVISION` → apply every finding's `fix` to `implementation_plan.md`
     inline, then re-invoke `opus-auditor` (increment `audit_round`). **Max 2 retries.**
     If still `NEEDS-REVISION` after round 3 → HALT and surface the findings to Daniel.
   - `UNSAFE` → HALT immediately and surface the findings to Daniel. Do not retry.

4. Record the final verdict + audit rounds in the run's `walkthrough.md` later.

## Stage 3 — Dev (GLM)

**Goal:** Implement the story per the (audited) plan.

1. **Re-enter `bmad-dev-story`** from Step 4 onward:
   - Mark the story `in-progress` in `sprint-status.yaml`.
   - Set `baseline_commit` in the story file frontmatter if not already set.
2. **Execute tasks/subtasks in order**, red-green-refactor. Write tests first. Run the
   full suite after each task. Do not skip steps.
3. **When all tasks complete** → bmad-dev-story Step 9 flips story status to `review`
   and `sprint-status.yaml` to `review`.
4. Do NOT mark `done` here. Do NOT run code review here — that is Stage 4's job.
5. Emit: story path, files changed count, test result summary.

## Stage 4 — Review (Opus 4.8 via opus-reviewer)

**Goal:** Adversarial post-implementation code review; write findings into the story
file so `bmad-dev-story` auto-resumes in Stage 5.

1. **Invoke the `opus-reviewer` subagent** via the Task tool. Pass:
   - `story_path` = `{story_path}`
   - `story_key` = `{story_key}`
   - `baseline_commit` = `{baseline_commit}`
   - `slug` = `{slug}`
   - `artifact_dir` = `{artifact_dir}`
   - A short note: "Run bmad-code-review (fast-path) against the diff since
     `{baseline_commit}`. Write the Senior Developer Review (AI) section into the story
     file and mirror to `{artifact_dir}/review-findings.md`. Do NOT flip status to done."

2. **On return**, parse the reviewer's message for:
   - `outcome` (Approve / Changes Requested / Blocked)
   - counts (total, High, Med, Low, `decision_needed`)
   - path to `review-findings.md`

3. **Branch on outcome:**
   - `Blocked` → HALT and surface to Daniel.
   - `decision_needed` findings exist → HALT and present them to Daniel (the ONE
     exception per the fast-path rule). Await judgment, then proceed.
   - `Approve` with zero High/Med items → skip Stage 5 fixes, go straight to the
     human sign-off gate.
   - `Changes Requested` or any High/Med items → proceed to Stage 5.

## Stage 5 — Fix + Sign-off + Close (GLM)

**Goal:** Resolve every review finding, then close the story under human sign-off.

1. **Re-enter `bmad-dev-story`.** Step 3 will auto-detect the "Senior Developer Review
   (AI)" section written by the reviewer and set `review_continuation = true`. It will
   prioritize the `Review Follow-ups (AI)` items (marked `[AI-Review]`).
2. **Fix every review follow-up.** For each: implement the fix, run the relevant tests,
   mark the `[AI-Review]` checkbox in both `Review Follow-ups (AI)` AND the matching
   `Action Items` entry. Record in Completion Notes.
3. **When all follow-ups resolved** → bmad-dev-story Step 8/9 re-validates the full DoD.
4. **HALT for human sign-off.** Present to Daniel:
   - Story key + title
   - Audit verdict (Stage 2) + rounds
   - Review outcome (Stage 4) + finding counts
   - Fixes applied (Stage 5)
   - Final test suite result
   - Prompt: **"Ready for final sign-off? Reply 'sign off' to close the story."**

5. **On Daniel's "sign off":** Run the `/1_ccps_update-active-context` workflow. It will:
   - Flip the story file Status AND `sprint-status.yaml` entry to `done`.
   - Update `active-context.md` (move to Completed, extract learnings, prune).
   - Sync component specs and `repo-map.md` if structure changed.

6. **Write `walkthrough.md`** to `{artifact_dir}/` with:
   - Summary of all 5 stages
   - Actual test output pasted
   - Audit + review verdicts
   - "Your Actions" section: manual steps + the git commit command for Daniel to run.
   - Do NOT run `git commit` yourself.

## Failure Modes & Halts

| Condition | Action |
|---|---|
| opus-auditor returns `UNSAFE` | HALT, surface findings to Daniel |
| opus-auditor returns `NEEDS-REVISION` 3× | HALT, surface findings to Daniel |
| opus-reviewer returns `Blocked` | HALT, surface to Daniel |
| `decision_needed` findings exist | HALT, present for Daniel's judgment |
| Tests fail during Stage 3 or 5 | bmad-dev-story's own HALT rules apply |
| Subagent not registered | HALT at Pre-Flight, tell Daniel to create it |
| Daniel does not say "sign off" | Do not close the story. Wait. |

## Artifacts Produced (per run)

```
_opencode_artifacts/<YYYY-MM-DD>_<story-slug>/
├── implementation_plan.md     ← GLM (Stage 1), patched in Stage 2 if needed
├── audit-findings.md          ← opus-auditor (Stage 2), one per round
├── review-findings.md         ← opus-reviewer (Stage 4), mirrored into story file
└── walkthrough.md             ← GLM (Stage 5 close-out)
```

## Constitution Compliance

This workflow operates under the **loop-only carve-out** in
`.agent/rules/constitution.md` → "🚫 Hard Stops" → "Exception — `/1_looping-dev-cycle`
only". The Opus auditor `Go` verdict substitutes for the manual "approved" phrase **only**
at the Stage 2 → Stage 3 transition. All other constitution hard-stops remain in force:
no `git commit`/`git push`, no fabricated citations, no new Firestore clients, etc.
