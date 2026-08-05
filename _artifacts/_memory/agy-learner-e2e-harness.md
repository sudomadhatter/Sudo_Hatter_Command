---
name: agy-learner-e2e-harness
description: "AGY's ONE e2e suite (TEA-16 journeys, 20 tests incl. admin + greeting + correction) — emulators + Playwright via `npm run test:e2e`; root config is an ALIAS of journeys config; 3 gotchas (CSP connect-src, projectId=demo-agy, named-DB seeding) + admin mocks need contract shapes."
metadata: 
  node_type: memory
  type: project
  originSessionId: 06ab6c4e-b51a-4707-bf79-83fed4364620
---

Since TEA-16 (2026-07-03), AGY has a **learner-auth E2E harness**: `frontend/npm run test:e2e` →
`e2e/run-e2e.mjs` wraps Playwright (`playwright.journeys.config.ts`, port 3100, fresh server) in
`firebase emulators:exec --only auth,firestore --project demo-agy`, seeding two learners
(`learner@e2e.test` = entitled claim, `locked@e2e.test` = un-entitled). Docs: `frontend/e2e/journeys/README.md`.
Authenticated-learner E2E is no longer blocked — don't re-punt it like hanger-talk.spec did.
**Since 2026-07-14 this harness IS the promotion gate:** `/sudo-e2e` wraps it (GREEN/RED verdict)
and `/sudo-push-e2e` paths B/C refuse to touch `main` until it's GREEN
([[command-surface-restructure-2026-07-14]]). Hermetic — backend is network-mocked, no uvicorn.

**Why:** Three non-obvious breakages cost most of the session:
1. **CSP silently blocks the emulators** — `next.config.ts` `connect-src` doesn't allow
   `127.0.0.1:9099/8080`; login just hangs on the password step with no visible error (only a
   console CSP violation). Fixed flag-gated; if a future CSP edit drops `emulatorConnectSrc`, the
   whole pack reds out the same silent way.
2. **Client projectId must equal the emulator project (`demo-agy`)** or Auth/Firestore scope to a
   different namespace and never see the seeds — set via env in the journeys config, not .env.
3. **Firestore seeding must target the NAMED db** (`aviationchat-database`) via REST
   `projects/demo-agy/databases/aviationchat-database/documents/...` + `Authorization: Bearer owner`;
   the default-db path writes into the void.

**How to apply:** New authenticated journeys → put specs in `frontend/e2e/journeys/`, mock backend
with `mockLearnerBackend(page, overrides)` (SSE via `sseBody`/`fulfillSSE`), log in with
`loginAsLearner(page, {locked?})`; admin-surface journeys use `seedAdminSession` +
`mockAdminBackend` (same file). Everything E2E-only is gated on
`NEXT_PUBLIC_USE_FIREBASE_EMULATOR` — set ONLY by the journeys webServer env, never in any .env.
Java 17 needed (see [[firestore-rules-tests-need-java]]); reuses
firebase-tools from `firebase/tests/node_modules` ([[tea-retrofit-active-initiative]]).

**2026-07-17 restructure:** journeys/ is now the ONLY pack (20 tests) — legacy root specs
(chat/sudo_admin*) were ported in (admin-routing, admin-management, greeting-chat) plus a new
verification-correction P0 safety journey; `playwright.config.ts` is an ALIAS re-exporting the
journeys config (no more testIgnore split), and global-setup fail-fasts with guidance if the
emulators aren't up. CI `frontend-e2e` is a HARD gate (continue-on-error deleted). Gotcha #4
learned porting admin: `mockAdminBackend` defaults MUST serve contract shapes —
`/api/admin/cohort-summary` is consumed RAW (no envelope); an empty `{}` crash-loops the
/sudo_admin shell (`card.value.toFixed` → Next dev overlay → every tab click "detaches")
([[atdd-mock-shape-must-match-backend-contract]]).
