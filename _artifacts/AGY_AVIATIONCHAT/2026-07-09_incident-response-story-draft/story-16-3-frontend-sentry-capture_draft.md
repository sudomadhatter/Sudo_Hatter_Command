---
IsArtifact: true
ArtifactMetadata:
  title: "16.3 — Frontend Sentry Capture (browser crashes enter the funnel)"
  type: story
  date: 2026-07-09
Status: draft
Epic: 16 — Automated Incident Response
Story: 16.3
created: 2026-07-09
depends_on: none (parallelizable; 16.2's org-wide poll picks the new project up automatically)
source: _artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/
---

# Story 16.3: Frontend Sentry Capture — the browser half of "the site crashed"

> Daniel's memo: "we need to set this up for sure. the front end also needs to be covered so we
> can quick fix it." Today a crash in a student's browser reaches **nobody** — the frontend has no
> Sentry SDK; `ErrorBoundary.tsx` holds a commented-out capture TODO. This story wires
> `@sentry/nextjs` so browser crashes flow into the SAME Sentry org → same alert → same 16.2
> pipeline → same phone.

## Story

As **the engineering owner whose students hit the app from phones and browsers**,
I want **client-side crashes captured in Sentry with readable stack traces and zone tags**,
so that **"the site crashed" triggers the incident pipeline no matter which half of the stack
died — and the quick fix is one acceptance away.**

## Context & Motivation

Verified 2026-07-09:
- `frontend/package.json` has **no `@sentry/*` package**; the only capture point is a TODO:
  `frontend/src/components/ErrorBoundary.tsx:61-63`
  (`// Sentry.captureException(error, { tags: { zone: this.props.zone } });` — "Task 4 (AC-4)").
- The privacy policy **already discloses Sentry** as an error-tracking sub-processor
  (`frontend/src/app/privacy/page.tsx:195`) — the paperwork ran ahead of the plumbing.
- Backend precedent to mirror: DSN-gated no-op init, `send_default_pii=False`, SHA-256-hashed
  user ids (`backend/observability/sentry_init.py:81-90`), release tagging via `GIT_SHA`.

## Acceptance Criteria

1. **SDK installed + initialized.** `@sentry/nextjs` added (dependency install honors the
   ask-first gate — approving this story approves the dependency), with the Next.js instrumentation
   files for client, server, and edge runtimes. DSN from `NEXT_PUBLIC_SENTRY_DSN`; **unset DSN →
   clean no-op** (exact parity with the backend's Gate-2 behavior — local dev and tests stay
   silent).
2. **Privacy parity.** `sendDefaultPii: false`; user id, if attached at all, is hashed with the
   same scheme as the backend `_before_send`; no emails/names/request bodies in events. Error
   monitoring only — `tracesSampleRate: 0` (performance tracing is out of scope; keeps bundle cost
   and noise down).
3. **ErrorBoundary capture.** The `ErrorBoundary.tsx:61-63` TODO is implemented as designed:
   `captureException` with the `zone` tag, so the report names which UI zone died.
4. **New Sentry project + alert rule.** Frontend project (e.g. `javascript-nextjs`) in org
   `aviationchat`; alert rule error/fatal → email (mirror of the 11.5 rule). **No pipeline change
   needed** — 16.2 polls org-wide by contract.
5. **Readable stack traces (source maps).** Production builds upload source maps to Sentry
   (`withSentryConfig` in `next.config`; `SENTRY_AUTH_TOKEN` available at build time), and the
   release is tagged with the deploy SHA — a minified `a.b is not a function` report is a failed
   AC. Preflight (Task 0) confirms WHERE the frontend production build runs so the upload step
   lands in the right pipeline.
6. **Live verification.** A forced client error (dev/preview build) appears in the frontend Sentry
   project with a readable stack + zone tag, and the alert email fires. Full-funnel proof (crash →
   16.2 report on the phone) joins the epic close-out live-QA once 16.2 is live.

## Tasks / Subtasks

- [ ] Task 0 — Preflight: locate the frontend production build/deploy pipeline (not yet mapped —
      backend deploys via `deploy-backend.yml`; frontend's path to prod must be confirmed before
      the source-map step is designed)
- [ ] Task 1 — Install + init (AC: 1, 2): `@sentry/nextjs`, instrumentation files, DSN gating,
      PII config, `tracesSampleRate: 0`
- [ ] Task 2 — ErrorBoundary capture (AC: 3)
- [ ] Task 3 — Sentry project + alert rule + env plumbing (AC: 4): create project, DSN into the
      frontend env convention (`NEXT_PUBLIC_*`), alert rule (Daniel does the Sentry-UI leg — Human
      Prerequisites)
- [ ] Task 4 — Source maps + release tagging (AC: 5) per Task-0 findings
- [ ] Task 5 — Forced-error verification (AC: 6); paste the Sentry event link in Completion Notes

## Dev Notes

- **Bundle discipline:** errors-only config; no session replay, no tracing. If bundle-size checks
  exist in CI, the SDK addition must pass them (flag any exception explicitly).
- **Env conventions:** frontend already reads `NEXT_PUBLIC_FIREBASE_*` from env
  (`frontend/src/lib/firebase.ts:24-31`) — `NEXT_PUBLIC_SENTRY_DSN` follows the same pattern;
  document beside the backend block in `.env.example`.
- **DSNs are publishable identifiers, not secrets** (the 11.5 precedent: GitHub *variable*, not
  secret) — but `SENTRY_AUTH_TOKEN` (source-map upload) IS a secret.
- **Human Prerequisites (Daniel):** create the frontend Sentry project + alert rule in the UI
  (same walkthrough style as 11.5's); provide the DSN.
- **Cross-story contract:** the 16.1 runbook takes the project slug as input; the 16.2 poll is
  org-wide — this story plugs in with zero changes to either.

## References

- [Source: frontend/src/components/ErrorBoundary.tsx:61-63 — the anticipated capture point]
- [Source: frontend/src/app/privacy/page.tsx:195 — Sentry already disclosed]
- [Source: backend/observability/sentry_init.py — gating + PII parity model]
- [Source: _bmad/bmm/stories/story-11-5-production-alert-wiring.md — alert-rule + DSN-handling precedent]
