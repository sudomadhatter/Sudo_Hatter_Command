---
description: Run the project's real end-to-end suite (Firebase-emulator-backed, seeded users, hermetic — no live backend needed) and report a clear GREEN/RED verdict. The gate /sudo-push-e2e requires before anything lands on main; also runnable solo any time.
---

# /sudo-e2e — End-to-End Test Gate

Runs the project's **hermetic E2E harness** and turns the result into a promotion verdict. Green
here is the evidence that `main_debug` is safe to promote to `main` (`/sudo-push-e2e` paths B/C
call this and refuse to proceed on red). Run it solo whenever you want end-to-end confidence.

## Step 0 — Resolve the target project (FIRST — before anything else)
Run from the **command center** (the lobby), this operates on exactly ONE child project under
`Projects/`, never the lobby itself:
0. **Self (sub-project fast path)** — no `Projects/` subfolder here → you ARE the project:
   `PROJECT_ROOT = .`, skip ahead.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`,
   that is the target; consume the token. Write it to `.agents/active-project.txt`.
2. **Active pointer** — else read `.agents/active-project.txt`.
3. **Ask** — else STOP and ask.

Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`.

## Step 1 — Confirm the harness exists
Check `PROJECT_ROOT/frontend/e2e/run-e2e.mjs`. If missing, STOP: this project has no E2E harness
yet (AviationChat's is TEA-16; a new project needs `/testarch-framework` first). Never improvise a
substitute suite and call it the gate.

## Step 2 — Run the suite (one command; the harness manages everything)
From `PROJECT_ROOT/frontend`, as a **background process** (it takes minutes; keep the log readable):
```powershell
npm run test:e2e
```
What the harness does for you (do NOT hand-roll any of it):
- wraps Playwright in `firebase emulators:exec --only auth,firestore --project demo-agy`
- auto-discovers Java 17 (Adoptium) if `JAVA_HOME` is unset — the emulators need a JRE
- boots a FRESH frontend dev server on **port 3100** wired to the emulators (never reuses :3000)
- seeds the test users (entitled + locked learner) in global-setup
- network-mocks the FastAPI backend (`**/api/**`) — **no uvicorn required**; the run is hermetic
- runs the journey pack (`e2e/journeys/**`) serially for determinism

Pass-through args after `--` (e.g. one spec, headed): `npm run test:e2e -- journeys/auth-wall.spec.ts --headed`

**Known failure modes (fix these, don't blame the tests):**
- `firebase-tools not found` → run `npm install` in `PROJECT_ROOT/firebase/tests` once
- port 3100 already in use → reap the orphaned node process (confirm before killing), re-run
- `JAVA_HOME` error → install Java 17 / set `JAVA_HOME` for this shell
- **Never** run the suite via the default `playwright.config.ts` — the journeys config
  (`playwright.journeys.config.ts`, invoked by the harness) is the real gate; the default config
  is the older spec pack and is NOT this gate

## Step 3 — Report the verdict
Parse the run and post exactly one of:
- **`E2E GATE: GREEN`** — N/N journeys passed. Link the HTML report if written
  (`frontend/playwright-report/`). Safe to promote.
- **`E2E GATE: RED`** — list each failing spec + the one-line reason (assertion vs timeout vs
  harness/env). A harness/env failure is still RED — fix the env and re-run; never wave it through.

When called from `/sudo-push-e2e`, the verdict line + failing-spec list is the hand-back; the
promotion continues only on GREEN. When run solo and RED, suggest the lane
(`/sudo-quick-dev` or the ①②③ story loop) and offer to file the failures as bug docs.

Optional additional input (project · extra playwright args): $ARGUMENTS
