---
IsArtifact: true
ArtifactMetadata:
  title: "Place Story 16.1 (incident-response agent) into AGY_AVIATIONCHAT"
  type: implementation_plan
  date: 2026-07-09
---

# Implementation Plan — register Story 16.1 in the project

## Goal

Daniel asked for a story for the error-tracking / incident-response feature. The story is drafted
(research-grounded) at
[story-16-1-sentry-incident-triage-agent_draft.md](story-16-1-sentry-incident-triage-agent_draft.md).
This plan covers the ONLY project-file writes: placing the story and registering it in the sprint
tracker. (Building the workflow itself is the story's own dev session, with its own plan.)

## Research summary (read-only, done this session)

- Error reporter = **Sentry** (backend only): `backend/observability/sentry_init.py` (Story 7.9),
  wired live by Story 11.5 — fatal → email alert rule. Sentry MCP verified live from the command
  center 2026-07-09: org `aviationchat`, project `python-fastapi`.
- **No Firebase Cloud Functions** — backend logs = Cloud Run → Google Cloud Logging (project
  `aviationchat`); "check the logs" = `gcloud logging read`.
- **Frontend has no Sentry** (`ErrorBoundary.tsx:61-63` TODO) — browser crashes are invisible today.
- Stories live flat in `_bmad/bmm/stories/`; highest epic = 15; Epic 11 (prod hardening) is done +
  retrospected → new **Epic 16** proposed rather than reopening 11.

## Files touched on "approved" (execution order)

1. Copy the draft → `Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-1-sentry-incident-triage-agent.md`
   (strip the draft frontmatter wrapper; `Status: backlog` or `ready-for-dev` per Daniel).
2. `Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml` — add the
   Epic 16 block (`epic-16: backlog` + story row `16-1`; placeholder rows for 16.2/16.3 only if
   Daniel approves the epic scope).
3. Nothing else. (The `/sudo-incident-response` command itself is built when the story is dev'd.)

## Open questions (answers change the story before placement)

1. **Epic placement** — new Epic 16 (recommended) or elsewhere?
2. **Scope of "auto"** — 16.1 = on-demand workflow (recommended); auto-trigger = 16.2. OK?
3. **Frontend Sentry** — register 16.3 with the epic, or defer?

## Verification plan

- Story file lints against the existing story shape (frontmatter keys match 11.5/15.1 pattern).
- `sprint-status.yaml` stays valid YAML (parse check) and the new rows mirror existing epic blocks.
- Daniel eyeballs the story in the project location; status flip to `ready-for-dev` is his call.
