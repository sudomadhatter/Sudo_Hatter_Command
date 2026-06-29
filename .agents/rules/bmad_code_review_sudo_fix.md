---
name: bmad_code_review_fast_path
description: "Activates when the bmad-code-review skill or workflow runs in this solo-agent setup. Run all review layers yourself sequentially (no subagents), do not stop at checkpoints, and persist findings to code-review.md."
---

# BMAD Code Review — Solo Agent Auto-Pilot

**Activates when:** The `bmad-code-review` skill or workflow is invoked.

## Core Mandate: No Swarm, No Stopping

You are running in a **single-agent environment**. You do NOT have access to subagents, parallel workers, or a swarm. Every instruction in the code review workflow that references "launching subagents," "parallel review layers," or "generating prompt files and halting" must be adapted to solo sequential execution.

**You MUST NOT stop to ask the user for confirmation at any checkpoint.** Run the entire workflow end-to-end in a single turn. The user triggered this review because they want results — not a conversation about reviewing.

---

## Step 1 Overrides (Gather Context)

When the workflow asks these questions, use these defaults silently — do not present them as choices:

| Workflow Question | Auto-Answer |
|---|---|
| **"What do you want to review?"** | Uncommitted changes (`git diff HEAD`) — staged + unstaged. |
| **"Is there a spec or story file?"** | Yes. Use the story file path from the user's prompt. If none was provided, scan `_bmad/bmm/stories/` for any file with `Status: ready-for-review` or `review`. If nothing found, proceed with `review_mode = "no-spec"`. |
| **"Confirm summary before proceeding?"** (§ CHECKPOINT) | Skip. Print a one-line summary (files changed, lines ±, review mode) and immediately continue. Do NOT halt. |
| **Chunking offer for large diffs** | Decline chunking. Proceed with the full diff. |

---

## Step 2 Overrides (Review) — Solo Sequential Execution

**This is the critical override.** The workflow says to launch three subagents in parallel. You cannot do that. Instead:

1. **Run each review layer yourself, sequentially, in the same turn.** Do not generate prompt files. Do not halt. Do not ask the user to run anything in a separate session.

2. **Execution order:**
   - **Pass 1 — Blind Hunter.** Mentally reset. Look at `{diff_output}` ONLY. No spec, no project context. Find bugs, logic errors, security issues, and code smells from the diff alone. Produce a markdown list of findings.
   - **Pass 2 — Edge Case Hunter.** Now use your full project read access alongside the diff. Walk every branching path, boundary condition, null check, error path, race condition, and type coercion edge. Produce findings as a structured list with `location`, `trigger_condition`, `potential_consequence`.
   - **Pass 3 — Acceptance Auditor.** (Skip if `review_mode = "no-spec"`.) Load the spec/story file and any context docs. Check the diff against acceptance criteria, spec intent, and specified behavior. Flag violations, deviations, and missing implementation. Produce a markdown list with title, AC reference, and evidence.

3. **Between passes:** Do NOT summarize or present intermediate results to the user. Just accumulate findings internally and continue.

4. **After all passes:** Proceed directly to Step 3 (Triage). No halting.

---

## Step 3 Overrides (Triage)

No changes to triage logic. Run normalization, deduplication, and classification exactly as written. Do NOT halt or ask the user for input during triage.

---

## Step 4 Overrides (Present and Act)

### Decision-Needed Findings
If `decision_needed` findings exist, **this is the ONE exception** where you present them — the user genuinely must make a judgment call. Present them clearly and halt for input.

### Patch Findings
Do NOT ask "How would you like to handle the patches?" — default to:
- If `{spec_file}` is set: **Leave as action items** in the story file.
- If `{spec_file}` is NOT set: **List all patches** in the output with file, line, and suggested fix. Do not auto-apply.

### Sprint Status Update
Run the story status update and sprint-status.yaml sync automatically — no confirmation needed.

---

## Close-Out

After the workflow completes:
1. Explicitly confirm: "✅ Story `<key>` closed out. Both `story file` and `sprint-status.yaml` updated to `done`."
2. Append git push command: "🚀 **Don't forget to commit and push!** `git add -A && git commit -m 'feat(epic-N): Story X.Y.Z — <Title>' && git push`"

---

## Summary of Behavioral Overrides

| Workflow Behavior | Override |
|---|---|
| Launch parallel subagents | Run all three layers yourself, sequentially |
| Generate prompt files and halt | Never. Run inline. |
| Halt at checkpoints for confirmation | Skip all halts except `decision_needed` |
| Ask what to review | Default to uncommitted changes |
| Ask about spec file | Auto-discover or proceed without |
| Ask how to handle patches | Default to action items (spec) or list (no spec) |
| Present options for next steps | Skip — end the workflow |
