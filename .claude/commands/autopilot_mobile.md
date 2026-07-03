---
description: Mobile-native autopilot — the web/cloud port of /autopilot_claude. Runs the same 4-stage Dev/QA story pipeline (Plan -> Audit -> Implement -> Review+Fix) on the Workflow engine instead of PowerShell, so it works on Claude Code web + mobile. Each stage is a fresh-context subagent — Opus on the Dev stages (max effort), Fable on the QA stages (Audit high, Review+Fix xhigh), mirroring /autopilot_claude's per-stage effort ladder. Flips the story to review on a green regression-only gate; never commits, never marks the story done.
platforms: [claude]
---

# /autopilot_mobile — Autonomous Story Pipeline (cloud/mobile)

> **Why this exists.** The local `/autopilot_claude` drives `powershell.exe` + nested `claude` CLI
> subprocesses — neither exists in the Claude Code web/mobile environment. This command does the same
> job with the in-environment **Workflow** tool: 4 stages, each a **fresh-context subagent**, handing
> off through artifact files. The fresh context per stage is the whole point — Stage 4's review is
> genuinely blind (a new agent that did NOT write the code), which a single chat can never do.

Run the pipeline for the story in `$ARGUMENTS` (a story id like `11.16`, or a path to the story `.md`).

## Parameters (fixed by Daniel, 2026-06-26; QA lane -> Fable, 2026-07-02; effort ladder mirrored 2026-07-03)

- **Model:** `opus` on the Dev stages (1 Plan, 3 Implement); `fable` on the QA stages (2 Audit,
  4 Review+Fix) — the strongest tier on the last gates before the human, matching /autopilot_claude's split.
- **Reasoning effort (per stage, NOT uniform):** mirrors /autopilot_claude's effort ladder
  (`-DevEffort`/`-AuditEffort`/`-ReviewEffort`). The Opus Dev lane runs at `max` (cheaper tier — spend the
  depth there); the Fable QA lane is dialed back. Effort is per-call, so the two QA stages differ:

  | Stage | Model | Effort |
  |---|---|---|
  | 1 Plan (Dev) | opus | **max** |
  | 2 Audit (QA) | fable | high |
  | 3 Implement (Dev) | opus | **max** |
  | 4 Review+Fix (QA) | fable | **xhigh** |

  (This supersedes the old "high on all four / think hard" convention — depth is set explicitly per stage,
  configured in `scripts/autopilot_mobile.workflow.js`'s `STAGES`.)
- **Context:** a brand-new subagent per stage (blind review).

## What to do

### 0. Resolve the target project (FIRST)
This command runs from the **command center (lobby)** and drives the pipeline inside exactly ONE child
project under `Projects/`, never the lobby (same pattern as the `/sudo-*` commands):
- **Self fast-path (check FIRST):** if this repo has **no** `Projects/` subfolder, you ARE the project -
  `PROJECT_ROOT = .`; skip the rest of Step 0.
- **Inline override:** if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, consume that
  token as the project and write it alone into `_my_resources/active-project.txt` (overwrite).
- **Active pointer:** else read `_my_resources/active-project.txt` if it names a folder under `Projects/`.
- **Ask:** else STOP and ask *"Which project? (e.g. AGY_AVIATIONCHAT)"* - never guess, never run on the lobby.

Resolve `PROJECT_ROOT` to an **absolute** path (`Projects/<name>` or `.` → its absolute form; the Workflow
sandbox needs absolutes) and **echo** `Target: <PROJECT_ROOT>`. Everything below - the story lookup,
`_bmad/...`, `_artifacts/...`, the workflow script, and the test gate - resolves **under `PROJECT_ROOT`**.
The story argument that remains after this step is `<STORY>`.

### 1. Resolve the story
- If `<STORY>` is empty, ask which story and STOP.
- If it's a path that exists, use it. Otherwise match `<PROJECT_ROOT>/_bmad/bmm/stories/*.md` whose name
  contains the id in either dotted (`8.15`) or dashed (`8-15`) form. No match → tell Daniel and STOP. More
  than one match → list them, ask which, STOP (never guess).
- Read the story's frontmatter `baseline_commit:` (first ~15 lines) if present — it's the scope anchor
  passed to the implement/review stages.

### 2. Resolve the canonical artifact folder (all under `<PROJECT_ROOT>`)
- Slug = `autopilot-<id>` with non-alphanumerics collapsed to `-` (e.g. `autopilot-8-15`).
- Epic = the leading number of the story id (`14.6` → `14`). A story **nests under its epic bucket**
  `<PROJECT_ROOT>/_artifacts/epic_<epic>/` — **create the epic folder if it isn't there yet** (per
  `artifacts-always-first`: stories live under their epic). If the id has no leading epic number, fall back
  to the `<PROJECT_ROOT>/_artifacts/` root.
- Reuse an existing `<PROJECT_ROOT>/_artifacts/epic_<epic>/*_<slug>/` folder (or a pre-fix
  `<PROJECT_ROOT>/_artifacts/*_<slug>/` at the root) if one exists — prefer the one that already holds
  `implementation_plan.md` — so a resume finds prior artifacts; otherwise mint
  `<PROJECT_ROOT>/_artifacts/epic_<epic>/<today>_<slug>/`. Create the folder. Use its **absolute** path as
  `<folder>` below.

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
  `mobile: true` to each artifact's `ArtifactMetadata` frontmatter and prefix the
  `<PROJECT_ROOT>/_artifacts/INDEX.md` row (and `walkthrough.md` H1) with **📱**, so Daniel can find mobile
  runs later for a desktop re-pass.

### 5. Snapshot the pre-existing red set (baseline), THEN launch the workflow

**5a. Baseline snapshot (regression-only gate, mirrors /autopilot_claude).** Before the workflow writes
any code, capture the tree's ALREADY-red tests so the final gate fails ONLY on NEW regressions this run
introduces — never on tests a parallel team already broke. Do this **only when the implement stage has not
yet run** (`startStage <= 3`) AND no cached baseline exists; on a resume where Stage 3 is already done, a
fresh baseline would be tainted by this run's own code, so reuse the cached one instead.
- Cache path: `<folder>/_pipeline/baseline-red.txt` (create `_pipeline/` if absent). If it already exists,
  skip capture and reuse it.
- Scope it the same way the gate does (from the baseline diff): if the story only touches `frontend/`,
  skip the backend baseline. Otherwise, from `<PROJECT_ROOT>`, run the backend suite once
  (`pytest backend/tests -q`) and write the set of failing test ids (one per line) to the cache file.
- **Runner missing** (no `.venv`/`python`): write the sentinel `RUNNER-MISSING` into the cache and move on
  — step 6 will honestly report UNVERIFIED rather than claim green.

**5b. Launch.** Call the **Workflow** tool with the committed orchestrator and the resolved args:

```
Workflow({
  scriptPath: '<PROJECT_ROOT>/scripts/autopilot_mobile.workflow.js',
  args: { story: '<id>', storyFile: '<abs path>', folder: '<abs folder>',
          baselineCommit: '<sha or empty>', startStage: <N>,
          projectRoot: '<abs PROJECT_ROOT>', projectName: '<project folder name, or "this project">' }
})
```

Pass `projectRoot` as an **absolute** path: the workflow's stage agents `cd` into it before running any
shell command (tests, git, installs), so the cwd-relative test steps work even when you launched from the
lobby. It runs in the background and notifies on completion. As stage `log()` lines stream in, advance the
TaskCreate list. The workflow returns a structured debrief: `{ status, stages[], haltedAt?, ... }`.

### 6. On return — gate, then debrief
- **status `halted`** (a `PIPELINE_BLOCKER`): stamp `_RUN-STATUS.md` HALTED, mark the current task
  blocked, report the blocker reason. Resumable: re-run the command (completed stages auto-skip) or
  Workflow `resumeFromRunId`.
- **status `crashed` / `artifact-missing`**: stamp `_RUN-STATUS.md` CRASHED, report which stage,
  note it's resumable.
- **status `complete`**: run the **independent test gate** yourself (do NOT trust the agents' pasted
  output). **Run every gate command from `<PROJECT_ROOT>`** (`cd` there first) so bare paths resolve:
  - Derive scope from the baseline diff (`git -C <PROJECT_ROOT> diff --name-only <baseline>`): backend
    changes → `pytest backend/tests -q`; frontend changes → `npm test -- --run` in `frontend/`. No
    baseline → run both.
  - **Container caveat:** if there's no `.venv`/`python` (backend) or no `npm` (frontend) under
    `<PROJECT_ROOT>`, the runner is missing — stamp `_RUN-STATUS.md` **TESTS UNVERIFIED — RUNNER MISSING**
    and say so plainly; do NOT claim green. (Also honor the `RUNNER-MISSING` sentinel from step 5a.)
  - **Baseline diff (regression-only, mirrors /autopilot_claude):** the raw suite result is NOT the
    verdict. Diff the now-red set against `<folder>/_pipeline/baseline-red.txt` from step 5a:
    - **Any red id NOT in the baseline** = a NEW failure this run introduced → stamp
      **TESTS RED — NOT FINISHED**, list the new failures, point at the output, stop.
    - **All red ids are in the baseline** (0 new) = GREEN vs baseline → the story introduced zero
      regressions; the pre-existing red is a parallel team's WIP, not this run. Proceed as green.
    - **No baseline cached** (missing/`RUNNER-MISSING`) → fall back to the raw full-suite verdict and say
      so (any red fails, per the old honesty rule).
  - Green (vs baseline) → **flip the story to `review`** (see below), then stamp `_RUN-STATUS.md`
    **PIPELINE COMPLETE — but NOT closed out**.

- **Auto-flip to `review` on a green gate (mirrors /autopilot_claude's `Set-StoryReview`).** A green gate
  means the dev+review work is genuinely complete and awaiting Daniel, so advance the story's lifecycle to
  `review` (the BMAD "Dev finishes → review" step) — in BOTH places, idempotently:
  - Story `.md` frontmatter: `Status: ready-for-dev|in-progress` → `review` (leave `review`/`done` alone).
  - `sprint-status.yaml`: the story's key `ready-for-dev|in-progress` → `review` (preserve any trailing comment).
  - **NEVER flip to `done`** — the human owns `review → done`. This is **best-effort**: a flip hiccup is a
    warning, never a crash of an already-green run (Daniel can flip by hand at close-out). Only flip after
    the gate is green AND `code-review.md` exists (a Stage-4 no-op must not silently advance the story).

### 7. Final debrief (mobile-summarized)
Read `<folder>/walkthrough.md` (top: **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL**) and
`<folder>/decisions-log.md`. Post a SHORT inline summary: total cost (from the workflow result),
artifacts written, the out-of-spec decisions, any open questions, and the test-gate result. Offer to
paste the full walkthrough. (CLAUDE_CODE_REMOTE is true on web/mobile — summarize, don't wall-of-text.)

## Guardrails (do not override)

- The audit's findings + fixes always flow into Stage 3. The run only HALTS on an explicit
  `PIPELINE_BLOCKER` (contradictory ACs, missing dependency, a human-only product call).
- **QA owns the loop close:** Stage 4 reviews AND applies fixes itself, then writes OUT-OF-SPEC
  DECISIONS + OPEN QUESTIONS at the top of `walkthrough.md`, and **appends a `## Close-Out Handoff`
  block at the bottom** — the pre-routed learnings (incl. Claude-memory candidates) that
  `/sudo-update-sprint-memory` lifts at close-out so it never re-derives.
- **New-dependency policy (A):** a stage self-installs + pins a needed dep, logs it in
  `decisions-log.md`, and banners it under "NEW DEPENDENCIES" in the walkthrough — never silently.
- **Story-status flip (review only):** on a clean COMPLETE with a GREEN independent gate, the command
  advances the story to `review` in BOTH the story `.md` and `sprint-status.yaml`, idempotently (only
  `ready-for-dev`/`in-progress` advance). It **never** flips to `done` (the human owns `review → done`)
  and the flip is best-effort (a hiccup warns, never crashes a finished run). See step 6.
- **Per-stage cost:** the local `/autopilot_claude` caps each stage with `-MaxStageCost`
  (`--max-budget-usd`). The Workflow engine has no per-stage USD budget knob, so mobile relies on the
  engine's own token budget for the turn instead — there is intentionally no dollar-per-stage cap here.
- The pipeline **never** runs `git commit`/`push` and **never** marks the story `done`. Human
  close-out is always required.

## After it completes — Daniel's close-out (not automated)

1. Review `walkthrough.md` (OUT-OF-SPEC DECISIONS + OPEN QUESTIONS, and the `## Close-Out Handoff` block
   at the bottom) and `decisions-log.md`.
2. The story is already at **`review`** (the command flipped it on the green gate). Answer any open
   questions, run `/sudo-update-sprint-memory` (it lifts the Close-Out Handoff), then flip `review → done`
   when satisfied.
3. Commit when satisfied (the pipeline never commits).

## On-demand status

While a run is going, just ask "status" — read `<folder>/_RUN-STATUS.md` (re-stamped at each
transition with the current stage) and report it.
