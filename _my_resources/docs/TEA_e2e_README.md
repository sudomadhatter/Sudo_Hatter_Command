# GAP-7 authenticated E2E journey pack (TEA-16)

Playwright E2E for the P0/P1 **learner** journeys — the level the TEA traceability matrix
(2026-07-02) flagged as systematically absent. Built on a Firebase **Auth + Firestore
emulator** harness so authenticated journeys run deterministically with no real
credentials, no live LLM, and no backend (TEA-2 determinism doctrine).

## Run

```bash
cd frontend
npm run test:e2e                 # all journeys
npm run test:e2e -- auth-wall    # one spec (filter)
npm run test:e2e -- --headed     # watch it
```

`npm run test:e2e` → `e2e/run-e2e.mjs`, which:
1. auto-discovers a Java 17 JRE (Adoptium) for the emulators — set `JAVA_HOME` yourself if
   it lives elsewhere (see memory `firestore-rules-tests-need-java`);
2. reuses the `firebase-tools` already installed for the TEA-12 rules suite
   (`firebase/tests/node_modules`) — no new frontend dependency;
3. wraps `playwright test --config playwright.journeys.config.ts` in
   `firebase emulators:exec --only auth,firestore --project demo-agy` so the emulators are
   live for `global-setup` seeding and the whole run, then torn down.

A **fresh** Next dev server boots on port **3100** carrying `NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true`
(never reused), so the client `connectAuthEmulator`/`connectFirestoreEmulator` calls in
`src/lib/firebase.ts` fire and the CSP in `next.config.ts` allows the emulator ports — both
gated on that flag, zero production impact.

## Harness pieces

| File | Role |
|------|------|
| `playwright.journeys.config.ts` | isolated config (port 3100, emulator env) — leaves the 3 legacy specs untouched |
| `e2e/run-e2e.mjs` | emulators:exec + playwright orchestration, Java auto-discovery |
| `e2e/global-setup.ts` | seeds two learners into the emulators |
| `e2e/support/learner.ts` | emulator REST seed helpers + the entitled/locked fixtures |
| `e2e/support/auth.ts` | `loginAsLearner(page, {locked?})` — drives the real sign-in form |
| `e2e/support/mockBackend.ts` | `**/api/**` route mock + `sseBody`/`fulfillSSE` for streamed lessons |

## Seeded learners

- **`learner@e2e.test`** — ENTITLED (`entitled` custom claim) → beta agents unlocked.
- **`locked@e2e.test`** — un-entitled → the beta lock fires.

Both get a Firestore `users/{uid}` profile so the dashboard treats onboarding as done.

## Journeys

1. **auth-wall** — unauth deep-link to `/dashboard` bounces to landing; authed learner is not evicted.
2. **entitlement-lock** — un-entitled learner hitting the Specialist funnel gets the closed-beta popup → `/earlyaccess`.
3. **verification-ordering** — the fast Specialist answer renders BEFORE the FAA-verified inline Sources badge (FR39-E ordering).

## Not covered here (documented follow-ups)

- The full 4-step lesson **progression** (overview → teach-me → Socratic → quiz) beyond the
  verification-ordering slice — the ordering/badge is the P0 heart; the multi-step quiz walk
  is a larger deterministic build, deferred.
- **Voice** journeys (Sully/Igor WebSocket) — the 4030 entitlement close is unit-covered
  (TEA-15); an E2E would need a mock WS server.
