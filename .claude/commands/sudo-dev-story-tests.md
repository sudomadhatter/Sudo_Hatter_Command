---
description: Develop a story test-first — plan, auto self-audit the plan, implement, then auto-expand coverage. Step ② of the sudo dev flow.
---

# /sudo-dev-story-tests — Plan → Self-Audit → Implement → Automate (②)

Thin orchestrator — drives the existing dev workflows so the story is built against the red tests from ①
and ends with expanded coverage. Project-scoped (targets THIS repo).

> Flow position: `sudo-write-story-tests` → **`sudo-dev-story-tests`** → `sudo-code-review`.

## Step 1 — Plan
Invoke the **`bmad-dev-story`** skill in PLAN mode for the story in `$ARGUMENTS`. Produce its
`implementation_plan.md`.

## Step 2 — Self-audit the plan (automatic, the moment the plan is written)
Immediately invoke **`/sudo-self-audit`** against the just-written plan — the pre-dev adversarial
stress-test (gaps, over-engineering, contract breaks) BEFORE any code. Fold its findings back into the
plan. (Human-lane equivalent of autopilot Stage 2.)

## Step 3 — Implement
Invoke the **`bmad-dev-story`** skill in IMPLEMENT mode: apply the audit, write the code, and drive the
① red tests to green. Run the relevant suite(s) and paste the **actual** output (constitution rule). If a
test fails, find root cause before fixing.

## Step 4 — Automate (expand coverage)
Invoke the **`bmad-testarch-automate`** skill to expand API / UI / contract coverage around what was
built — closing gaps the ATDD pass did not reach.

## Done
Report: plan-vs-built deltas, audit findings applied, tests now green (paste output), coverage added.
Hand to `sudo-code-review`. **Do NOT commit or flip story status.**

Optional additional input: $ARGUMENTS
