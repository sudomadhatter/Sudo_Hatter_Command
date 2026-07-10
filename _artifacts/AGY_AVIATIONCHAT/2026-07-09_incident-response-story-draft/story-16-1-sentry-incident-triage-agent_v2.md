---
IsArtifact: true
ArtifactMetadata:
  title: "16.1 — Incident Triage Runbook (the brain) — v2"
  type: story
  date: 2026-07-09
Status: draft            # v2 after Daniel's review: NOT a /command product — the runbook both lanes execute
Epic: 16 — Automated Incident Response (approved by memo 2026-07-09)
Story: 16.1
created: 2026-07-09
depends_on: story-11-5-production-alert-wiring (done)
source: _artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/ (v1 + memos preserved alongside)
---

# Story 16.1: Incident Triage Runbook — the brain every lane runs

> **v2 change (Daniel's review):** the product is NOT a `/` command. It is a **canonical triage
> runbook file** that any Claude lane executes — above all the headless always-live pipeline
> (Story 16.2), and secondarily an interactive session during drills. A thin local command remains
> ONLY as the drill/test harness for this story's verification.

## Story

As **the engineering owner of a production aviation-education platform**,
I want **one canonical triage runbook — Sentry issue → correlated logs → failing code path →
build history → full incident report with a proposed fix — executable by a headless agent**,
so that **the always-live pipeline (16.2) has a tested brain to run the moment an alert fires,
and every incident produces the same complete report no matter which lane ran it.**

## Context & Motivation

Today the alert chain (Stories 7.9 + 11.5, live-verified) ends at the inbox: backend fatal →
Sentry (org `aviationchat`, project `python-fastapi`) → email. Everything after is manual. This
story builds the investigation brain; 16.2 wires it to an always-live trigger; 16.3 feeds
frontend crashes into the same funnel.

Verified grounding (2026-07-09 session):
- Backend logs = **Cloud Run → Google Cloud Logging** (no Firebase Functions exist); project `aviationchat`.
- Sentry MCP live from the command center (interactive lane); REST API + `SENTRY_AUTH_TOKEN` is
  the headless transport.
- Every shipped feature has a paper trail: story File Lists (`_bmad/bmm/stories/`), walkthroughs
  (`_artifacts/epic_<E>/<story>/`), component specs (`_bmad-output/component-specs/`).

## Acceptance Criteria

1. **The runbook file exists in-repo** at `.github/claude/incident-triage.md` (in `.github/` so the
   16.2 workflow checkout reads it natively; path final call at dev time). It defines the five
   steps below, each with an explicit graceful-degrade rule, and is written to be executed verbatim
   by a headless agent (no interactive questions; every ambiguity has a default).
2. **Step 1 — Sentry retrieval.** Given a Sentry issue id (or "latest unresolved error/fatal"):
   title, level, event count, first/last seen, environment, release (GIT_SHA), newest event's full
   stack trace + hashed user id. Transports: Sentry MCP (interactive) / REST with `SENTRY_AUTH_TOKEN`
   (headless; name documented in `.env.example`, value never in repo).
3. **Step 2 — Log correlation.** Google Cloud Logging, Cloud Run service, ±15-minute window around
   the event (`severity>=ERROR` first, widen only if inconclusive); relevant excerpts quoted.
   Unauthenticated `gcloud` → note the gap and continue (a partial report is still a report).
4. **Step 3 — Code-path mapping.** Top in-app stack frames resolved to `file:line`; direct file
   reads are the baseline (works headless); GitNexus `context`/`impact` enrichment when the graph
   is available (interactive lane) — never a blocker.
5. **Step 4 — Build-history context (CONDITIONAL + bounded).** Runs ONLY when the root cause is
   not already clear from trace + logs (self-assessed confidence below "high") — Daniel
   2026-07-09: "only if it needs to, not every time; if it's struggling to understand what broke
   it has the resources to go look at the way we built it." When it runs: identify the owning
   feature by matching stack files against story File Lists / component specs; read AT MOST the
   story file + its `walkthrough.md` + the matching spec. No tree crawls. No match → say so and
   move on. The report states whether this step ran and why.
6. **Step 5 — The report.** Template embedded in the runbook (single source), sections: **TL;DR**
   (what broke, severity, blast radius, confidence) · **Timeline** · **Evidence** (Sentry + logs) ·
   **Code path** · **Root-cause hypothesis (confidence-rated)** · **Proposed fix plan**
   (implementation-plan shaped) · **Suggested tests** · **Your Actions** (ends with the local-accept
   instructions — pull the `claude/incident-*` branch, test it, merge to `main`, then rebase
   `main_debug` onto `main`, per 16.2). Output
   location is parameterized: interactive → `_artifacts/debugging/<YYYY-MM-DD>_<issue-slug>/incident-report.md`;
   headless → the 16.2 contract (`claude/incident-<id>` branch). Every file reference a clickable
   link; no secrets; PII stays hashed (backend `_before_send` already guarantees this upstream).
7. **Read-only guarantee.** The runbook writes ONLY its report (artifacts folder or its own
   incident branch per lane). It never merges, never opens a PR, and never pushes to `main` or
   `main_debug` — the fix awaits acceptance (Level-2 auto-fix is 16.2's contract, pushed to an
   isolated `claude/incident-*` branch that Daniel pulls, tests, merges to `main`, then rebases
   `main_debug` onto `main` himself). Analysis is anchored at the event's release SHA (the `main`
   code that is actually live), not the `main_debug` working state.
8. **Drill harness + local drill.** A thin `/sudo-incident-response [issue-id|latest]` command
   (master `.agents/commands/`, vendored via `/sync-agents`) exists **solely to execute the runbook
   in drills** — it is the test harness, not the product. Local drill passes: forced failure via
   the Story-11.5 pattern (`_test_scripts/sentry_smoke_test.py`) → run the runbook → Daniel
   confirms the report names the planted failure, the correct file, and a sane fix plan. Story
   stays `review` until the drill passes. (The end-to-end headless drill is 16.2's AC.)

## Tasks / Subtasks

- [ ] Task 1 — Author `.github/claude/incident-triage.md` (AC: 1–7): five steps, degrade rules,
      embedded report template, lane-parameterized output, guardrails block
- [ ] Task 2 — Drill harness (AC: 8): thin command wrapping "execute the runbook"; `/sync-agents`
- [ ] Task 3 — Access docs (AC: 2, 3): `.env.example` gains commented `SENTRY_AUTH_TOKEN` beside
      the existing `SENTRY_DSN` block; runbook preflight documents `gcloud` auth expectation
- [ ] Task 4 — Local drill (AC: 8): forced P1 → runbook → report reviewed with Daniel; paste the
      report path + verdict in Completion Notes

## Dev Notes

- **Why in-repo, why `.github/`:** the 16.2 workflow must read the runbook on a bare CI checkout;
  `.agents/` vendoring is a desktop-tooling concern — the runbook is production ops surface.
- **Sentry org facts (verified live):** org `aviationchat`, region `https://us.sentry.io`, backend
  project `python-fastapi`; 16.3 adds the frontend project — the runbook takes the project slug as
  input rather than hardcoding it.
- **GitNexus headless caveat:** the CI runner has no GitNexus server; the runbook's baseline is
  therefore plain file reading, with graph enrichment as interactive bonus (AC-4).
- **Existing chain refs:** `backend/observability/sentry_init.py` (gates :39/:44, PII hash :81-90),
  `backend/utils/rkp_loader.py:19-52` (`fire_p1_alert`), callers `backend/main.py:264` +
  `backend/services/lesson_plan_builder.py:127`, `.github/workflows/deploy-backend.yml`
  (SENTRY_DSN + GIT_SHA).
- **Constitution alignment:** read-only triage; plan-first (the report's fix plan IS the next
  session's implementation plan); never `git commit`/`push` outside the pipeline's own incident
  branch; no secrets echoed.

## References

- [Source: _bmad/bmm/stories/story-11-5-production-alert-wiring.md — alert chain + smoke pattern]
- [Source: _artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/always-live-trigger-brainstorm.md — architecture decision record]
- [Source: docs/gitnexus.md]
