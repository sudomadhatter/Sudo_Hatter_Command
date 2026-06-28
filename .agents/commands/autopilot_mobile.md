---
description: Mobile-native autopilot — the web/cloud port of /autopilot_claude. Runs the same 4-stage Dev/QA story pipeline (Plan -> Audit -> Implement -> Review+Fix) on the Workflow engine instead of PowerShell, so it works on Claude Code web + mobile. Each stage is a fresh-context Opus subagent at high reasoning effort. Never commits, never marks the story done.
platforms: [claude]
---

# /autopilot_mobile — Autonomous Story Pipeline (cloud/mobile)

> **Why this exists.** The local `/autopilot_claude` drives `powershell.exe` + nested `claude` CLI
> subprocesses — neither exists in the Claude Code web/mobile environment. This command does the same
> job with the in-environment **Workflow** tool: 4 stages, each a **fresh-context subagent**, handing
> off through artifact files. The fresh context per stage is the whole point — Stage 4's review is
> genuinely blind (a new agent that did NOT write the code), which a single chat can never do.

Run the pipeline for the story in `$ARGUMENTS` (a story id like `11.16`, or a path to the story `.md`).

## Parameters (fixed by Daniel, 2026-06-26)

- **Model:** `opus` on all four stages.
- **Reasoning effort:** `high` on all four stages (the native form of the script's "think hard").
- **Context:** a brand-new subagent per stage (blind review).

## What to do

### 1. Resolve the story
- If `$ARGUMENTS` is empty, ask which story and STOP.
- If it's a path that exists, use it. Otherwise match `_bmad/bmm/stories/*.md` whose name contains the
  id in either dotted (`8.15`) or dashed (`8-15`) form. No match → tell Daniel and STOP. More than one
  match → list them, ask which, STOP (never guess).
- Read the story's frontmatter `baseline_commit:` (first ~15 lines) if present — it's the scope anchor
  passed to the implement/review stages.

### 2. Resolve the canonical artifact folder
- Slug = `autopilot-<id>` with non-alphanumerics collapsed to `-` (e.g. `autopilot-8-15`).
- Epic = the leading number of the story id (`14.6` → `14`). A story **nests under its epic bucket**
  `_artifacts/epic_<epic>/` — **create the epic folder if it isn't there yet** (per `artifacts-always-first`:
  stories live under their epic). If the id has no leading epic number, fall back to the `_artifacts/` root.
- Reuse an existing `_artifacts/epic_<epic>/*_<slug>/` folder (or a pre-fix `_artifacts/*_<slug>/` at the
  root) if one exists — prefer the one that already holds `implementation_plan.md` — so a resume finds prior
  artifacts; otherwise mint `_artifacts/epic_<epic>/<today>_<slug>/`. Create the folder.

### 3. Compute the resume start-stage (artifact-presence skip)
A stage is "complete" iff its handoff artifact exists on disk:
`implementation_plan.md` (1) · `self-audit-stress-test.md` (2) · `walkthrough.md` (3) · `code-review.md` (4).
`startStage` = the first stage whose artifact is missing (1 on a clean run). Tell Daniel which stages
will be skipped.

### 4. Live task list + run-status marker
- Create a TaskCreate list mirroring the four stages; mark `startStage` `in_progress`, the rest
  `pending` (skip the already-complete ones as `completed`).
- Write `<folder>/_RUN-STATUS.md` = **📱 MOBILE RUN — IN PROGRESS — NOT FINISHED** (so a crashed/partial
  run can never read as a finished story, and the run is flagged as mobile-made).
- **Tag the run as mobile-made** (`mobile-mode.md` Override 3): this is a `CLAUDE_CODE_REMOTE` run, so add
  `mobile: true` to each artifact's `ArtifactMetadata` frontmatter and prefix the `_artifacts/INDEX.md`
  row (and `walkthrough.md` H1) with **📱**, so Daniel can find mobile runs later for a desktop re-pass.

### 5. Launch the workflow
Call the **Workflow** tool with the committed orchestrator and the resolved args:

```
Workflow({
  scriptPath: 'scripts/autopilot_mobile.workflow.js',
  args: { story: '<id>', storyFile: '<abs path>', folder: '<abs folder>',
          baselineCommit: '<sha or empty>', startStage: <N> }
})
```

It runs in the background and notifies on completion. As stage `log()` lines stream in, advance the
TaskCreate list. The workflow returns a structured debrief: `{ status, stages[], haltedAt?, ... }`.

### 6. On return — gate, then debrief
- **status `halted`** (a `PIPELINE_BLOCKER`): stamp `_RUN-STATUS.md` HALTED, mark the current task
  blocked, report the blocker reason. Resumable: re-run the command (completed stages auto-skip) or
  Workflow `resumeFromRunId`.
- **status `crashed` / `artifact-missing`**: stamp `_RUN-STATUS.md` CRASHED, report which stage,
  note it's resumable.
- **status `complete`**: run the **independent test gate** yourself (do NOT trust the agents' pasted
  output):
  - Derive scope from the baseline diff (`git diff --name-only <baseline>`): backend changes →
    `pytest backend/tests -q`; frontend changes → `npm test -- --run` in `frontend/`. No baseline →
    run both.
  - **Container caveat:** if there's no `.venv`/`python` (backend) or no `npm` (frontend), the runner
    is missing — stamp `_RUN-STATUS.md` **TESTS UNVERIFIED — RUNNER MISSING** and say so plainly; do
    NOT claim green. (Same honesty rule as the PowerShell gate.)
  - Red suite → stamp **TESTS RED — NOT FINISHED**, point at the output, stop. (If the red is a
    parallel team's WIP, confirm this story's own tests pass and note it.)
  - Green → stamp `_RUN-STATUS.md` **PIPELINE COMPLETE — but NOT closed out**.

### 7. Final debrief (mobile-summarized)
Read `<folder>/walkthrough.md` (top: **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL**) and
`<folder>/decisions-log.md`. Post a SHORT inline summary: total cost (from the workflow result),
artifacts written, the out-of-spec decisions, any open questions, and the test-gate result. Offer to
paste the full walkthrough. (CLAUDE_CODE_REMOTE is true on web/mobile — summarize, don't wall-of-text.)

## Guardrails (do not override)

- The audit's findings + fixes always flow into Stage 3. The run only HALTS on an explicit
  `PIPELINE_BLOCKER` (contradictory ACs, missing dependency, a human-only product call).
- **QA owns the loop close:** Stage 4 reviews AND applies fixes itself, then writes OUT-OF-SPEC
  DECISIONS + OPEN QUESTIONS at the top of `walkthrough.md`.
- **New-dependency policy (A):** a stage self-installs + pins a needed dep, logs it in
  `decisions-log.md`, and banners it under "NEW DEPENDENCIES" in the walkthrough — never silently.
- The pipeline **never** runs `git commit`/`push` and **never** marks the story `done`. Human
  close-out is always required.

## After it completes — Daniel's close-out (not automated)

1. Review `walkthrough.md` (OUT-OF-SPEC DECISIONS + OPEN QUESTIONS) and `decisions-log.md`.
2. Answer open questions; run `/update-sprint-context` to close the story.
3. Commit when satisfied (the pipeline never commits).

## On-demand status

While a run is going, just ask "status" — read `<folder>/_RUN-STATUS.md` (re-stamped at each
transition with the current stage) and report it.
