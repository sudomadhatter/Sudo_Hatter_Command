---
IsArtifact: true
ArtifactMetadata:
  title: "Register Epic 16 (Automated Incident Response) + stories 16.1–16.3 in AGY_AVIATIONCHAT"
  type: implementation_plan
  date: 2026-07-09
---

# Implementation Plan — register Epic 16 + three stories

## Goal

Land the Automated Incident Response epic in the project tracker. The feature: a Sentry alert
(frontend or backend) fires a **headless Claude agent in GitHub Actions** — PC off — which runs a
triage runbook and delivers a full incident report + solution to Daniel's phone (GitHub issue push
+ email); acceptance is one tap in mobile Claude Code (Level 1) or merging a ready-made fix PR
(Level 2).

## Decision record (Daniel, 2026-07-09 — memos + chip answers; full log in the brainstorm doc §DECISION)

- Epic 16 approved (memo: "yes"). Frontend coverage confirmed (memo: "for sure").
- NOT a `/` command — always-live, hook-triggered, PC-independent (memo).
- **Webhook from day one** — no cron/polling phase ("why wait?").
- **Claude Code Routines = primary runtime** ("I trust the beta"), with the **GitHub Actions lane
  built dormant as the rollback** — the relay's `TARGET` env flip is the whole migration.
- **Level 2 from day one**: fix pre-built + tests + PR open; accepting = merge (pipeline never
  merges).
- **Notifications: GitHub issue only** (native email + app push).
- **Build-history (`_artifacts`) lookup is conditional** — only when the agent is struggling, not
  every incident.
- **Monitors + fixes `main` (production)** — "debug is where we build, main is live": crashes come
  from the live deploy built from `main`; triage anchors at the event's release SHA; incident PRs
  target `main`; the merge stays Daniel's manual button; hotfix back-merge to `main_debug` flagged
  in every PR footer. (Deliberate owner carve-out of the "never PR to main" rule, this lane only.)

## The story set (drafts in this folder)

| Story | File | One-liner |
|---|---|---|
| 16.1 | [story-16-1-sentry-incident-triage-agent_v2.md](story-16-1-sentry-incident-triage-agent_v2.md) | The triage **runbook** (`.github/claude/incident-triage.md`) both lanes execute; local drill harness |
| 16.2 | [story-16-2-always-live-trigger-pipeline_draft.md](story-16-2-always-live-trigger-pipeline_draft.md) | **THE story**: Sentry webhook → relay (signature + dedupe + log pre-fetch + `TARGET` switch) → **Routine** builds fix + opens PR (Level 2) → GitHub issue on the phone; dormant GH-Actions rollback lane, drilled |
| 16.3 | [story-16-3-frontend-sentry-capture_draft.md](story-16-3-frontend-sentry-capture_draft.md) | `@sentry/nextjs` + ErrorBoundary capture + FE Sentry project + source maps → same funnel |

(v1 of 16.1 stays in this folder untouched — it carries Daniel's md-feedback memos.)

## Files touched on "approved" (execution order)

1. `Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-1-incident-triage-runbook.md` — from the
   v2 draft (artifact frontmatter stripped; `Status: ready-for-dev`).
2. `…/stories/story-16-2-always-live-trigger-pipeline.md` — from the draft (`Status: backlog`,
   blocked_by 16.1).
3. `…/stories/story-16-3-frontend-sentry-capture.md` — from the draft (`Status: backlog`,
   parallelizable).
4. `Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml` — append
   the Epic 16 block (`epic-16: backlog` + rows `16-1` / `16-2` / `16-3`, mirroring existing epic
   block format; YAML parse-checked).

Nothing else. Each story's build gets its own plan + approval; the notable ask-first gates ahead
(GH secrets, `roles/logging.viewer` IAM grant, `@sentry/nextjs` dependency) are flagged inside
their stories' Task 0 / Human Prerequisites.

## Recommended dev order

16.1 (brain + local drill) → 16.2 (pipeline + phone drill) · 16.3 in parallel any time after 16.1
starts. Epic close-out live-QA = full-funnel proof: forced FE + BE crashes → two phone reports.

## Open items (non-blocking, verify during 16.2 Task 0)

- Routines beta: endpoint auth + billing model + beta-header pinning (primary-lane preflight).
- Confirm fallback-lane auth: `ANTHROPIC_API_KEY` (Console billing) — subscription OAuth tokens in
  CI were reported disallowed by a secondary source; verify against official docs at setup.
- Frontend production build/deploy pipeline location (16.3 Task 0) for the source-map step.

## Verification plan

- Story files match the house shape (frontmatter keys per 11.5/15.1).
- `sprint-status.yaml` parses (python -c yaml.safe_load) and diffs show ONLY the Epic 16 block.
- Daniel eyeballs all three in place; status flips are his call.

---

## Amendment 2 (2026-07-09) — bind BDD/ATDD + test-review into the placed stories

Daniel: "we need to follow our procedures for bdd and atdd." The sudo dev flow already imposes
them at dev time (`/sudo-bdd-tests` = Step 2 "BDD Vision Lock" of `/sudo-write-story-tests`,
vendored in the project's `.agents/commands/`; `pytest-bdd>=7.0.0` pinned at
`backend/requirements.txt:54`; `vitest` + `@playwright/test` present in `frontend/package.json`).
This amendment binds the procedures **in the story text** so every lane — autopilot, direct
`bmad-dev-story`, a hand session — sees them, not just the sudo loop.

### Files touched on "approved" (all additive; no status changes; no new files)

1. **`story-16-2-always-live-trigger-pipeline.md`** — the **BDD pilot (testing-audit P2-8)**:
   - NEW **AC-8**: relay behaviors locked as a `pytest-bdd` `.feature` contract via the Vision
     Lock BEFORE implementation — scenarios: invalid signature → reject · duplicate
     `incident:<short-id>` → drop · `TARGET` routing (routines/github) · `INCIDENTS_PAUSED` → no
     fire; ATDD red → green; `.feature` → `backend/tests/features/`, steps → `backend/tests/bdd/`
     (relay outside `backend/` → contract lives beside the relay's test tree, choice recorded);
     pilot proof = `pr-check` collects the `.feature` run with zero config change.
   - NEW **AC-9**: `/testarch-test-review` verdict recorded in Completion Notes before
     `review` → `done`.
   - Task 1 gains AC-8 (contract-first ordering); NEW Task 6 (test-review gate); Dev Notes
     bullet: pilot rationale + machinery refs.
2. **`story-16-3-frontend-sentry-capture.md`**:
   - NEW **AC-7**: Vitest unit tests written from the ACs FIRST (ATDD order, red → green) —
     unset DSN → clean no-op init; ErrorBoundary calls `captureException` with the `zone` tag
     (mock `@sentry/nextjs`). `pytest-bdd` is the Python-side dialect; the FE Gherkin layer is
     Playwright, explicit-E2E-only → the crash→phone journey belongs to the epic close-out
     live-QA, not this story. `/testarch-test-review` before `review` → `done`.
   - NEW Task 6 (tests-first + test-review gate).
3. **`story-16-1-incident-triage-runbook.md`** — Dev Notes bullet: **documented BDD waiver** —
   no product code (markdown runbook + thin drill command), so Vision Lock and test-review do
   not apply; the skip is recorded as an explicit waiver in Completion Notes per the audit's
   gate rules, and the forced-failure drill (AC-8) IS the acceptance evidence. The BDD lane
   starts at 16.2.
4. **`sprint-status.yaml`** — one TDAD/BDD line added to the Epic 16 header comment; per-story
   comment tags (16-2 "★ BDD PILOT (P2-8)", 16-1 waiver, 16-3 vitest tests-first + review gate).
   YAML re-parse-checked after the edit.

### Why 16.2 is the pilot

The audit's forward-only rule — "every new story goes through `/sudo-bdd-tests` → `.feature`
contract → ATDD red" — needs a first story to prove the loop (P2-8). The relay is ideal:
small greenfield Python with four crisp, externally-observable behaviors, and it lands the
repo's first `.feature` with zero CI config change.
