---
name: bmad_code_review_sudo_fix
description: "Activates whenever the bmad-code-review skill or workflow runs (any agent, any platform). Run the review end-to-end in one pass — never halt to hand steps back to the user — then append findings to the walkthrough's ## Code Review section (artifacts-always-first §6). Never flip the story to done; stop at review."
since: 2026-06-29
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

## Step 2 — Review (TWO ingests, three layers)

Read scope is a budget, not an afterthought — the reviewer is usually the most expensive model in the
run. **Pull the material in exactly two reads, then think.** The three layers are three *questions asked
of context you already hold*, not three traversals of the tree.

- **Ingest 1 — the diff, alone.** Nothing else in context yet. This is what makes Layer 1 blind.
- **Ingest 2 — one batched grounding pull**, taken only *after* Layer 1 has produced its findings: each
  changed file whole, the direct callers/dependents of the changed symbols, the tests covering them, and
  the spec/story.

That is the read budget. **There is no "read the whole repo" pass** — an unbounded sweep burns the run's
budget and finds less than a targeted read of the blast radius. Do not add one back.

1. **Blind Hunter** — Ingest 1 ONLY (no spec, no story, no walkthrough, no project context). Bugs, logic
   errors, security, smells → findings list. It runs *before* Ingest 2 lands: reading the builder's
   account first imports exactly the bias this layer exists to zero out.
2. **Edge Case Hunter** — over Ingest 2. Every branch, boundary, null, error path, race, type-coercion
   edge, plus the callers you already pulled → list with `location`, `trigger_condition`,
   `potential_consequence`.
3. **Acceptance Auditor** (skip if `no-spec`) — over Ingest 2. Diff vs the spec/story ACs. Violations,
   deviations, missing implementation → list with title, AC reference, evidence.

**Top-ups must be earned.** When a layer surfaces a *specific* lead — an unresolved symbol, a caller you
did not anticipate — read that named file. Read because you can say what you are looking for, never "to
be thorough." One targeted top-up beats a second sweep; a second sweep is the failure mode.
**Never trade a real finding for tokens** — this is the last gate before the human, and a missed defect
costs far more than the read. Efficiency here means *not re-reading what you already hold*, never
reviewing less.

Accumulate findings internally (no intermediate summaries), then go straight to triage.

## Step 3 — Triage
Run the workflow's normalization, deduplication, and classification exactly as written — without pausing.

## Step 4 — Present & act
- **`decision_needed` findings** — the one exception: present them clearly and halt for the human's call.
- **Patch findings** — never ask how to handle them. If `{spec_file}` is set, leave them as action items in the story file; else list each (file, line, suggested fix) in the output. Do not auto-apply.
- **Status** — ensure the story is at `review` (idempotent — the dev step normally set it already). **Never write `done`** to the story file or `sprint-status.yaml`; this overrides step-04-present's `done` default.

## Close-out
1. Confirm: `✅ Story <key> reviewed — left at review for human close-out. Run /sudo-update-sprint-memory to advance review → done.`
2. Commit the reviewed work **inside the story worktree**, explicit paths only — never `git add -A`
   (it sweeps other teams' work in). Do NOT land it on `main_debug`; that is close-out's job:
   `git add <paths> && git commit -m 'feat(epic-N): Story X.Y.Z — <Title>'`
