---
name: agy-frontend-vitest-harness
description: "AGY frontend vitest gotchas from the first SpecialistChat component tests (tea-17): jsdom has NO requestAnimationFrame (stub with TRACKED setTimeouts + kill in afterEach), zustand singletons need fresh-nested-object resets (not by-reference snapshots), new SpecialistChat tests must EXTEND SpecialistChat.verification.test.tsx (import cost), shared factories live in src/__tests__/factories/. ALSO: a local vitest v4 run that hangs / OOMs on worker teardown (zero output, never returns) is an INFRA flake on a memory-pressured machine, NOT a test failure — verify the file in CI."
metadata: 
  node_type: memory
  type: project
  originSessionId: 06ab6c4e-b51a-4707-bf79-83fed4364620
---

Hard-won harness facts from writing AGY's first SpecialistChat-rendering vitest tests (tea-17, 2026-07-03):

- **jsdom has no `requestAnimationFrame`** (vitest doesn't enable `pretendToBeVisual`) — the SpecialistChat typewriter drain loop needs it. Stub with 16ms `setTimeout`s and **track the ids + clear them in afterEach**, or a failing test's still-rescheduling drain loop fires after `vi.unstubAllGlobals()` and cascades errors into the next test's report. Unmount (`cleanup()`) BEFORE unstubbing — RTL's auto-cleanup afterEach runs LIFO, i.e. after yours.
- **Zustand singleton reset:** `setState(capturedSnapshot, true)` restores nested objects BY REFERENCE — one future in-place mutation in product code silently corrupts the baseline for every later test. Reset with fresh objects: `setState({...snapshot, messages: [], state: {...snapshot.state}}, true)`.
- **Extend `src/components/__tests__/SpecialistChat.verification.test.tsx` for new SpecialistChat tests** — don't spawn sibling files: vitest re-executes the module graph per test FILE, and the 2169-line component + react-markdown/katex import is multi-second per file (tea-17 review convention note).
- **Product timers bleed across tests under real timers:** SpecialistChat schedules a 300ms post-stream menu-recovery and a 2s glow `setTimeout` that touch the module-global store — drain ~350ms in afterEach (or use fake timers) so they can't mutate the NEXT test's freshly-reset store.
- Shared test factories live in `frontend/src/__tests__/factories/` (e.g. `quizResult.ts` — the FR14-C QuizResultEntry shape used by both Drawer and useSessionStore suites); not matched by the test glob, safe from Next builds.
- The SSE seam for component tests: mock `@/lib/api` `authenticatedFetch` to return `{ok, body: {getReader}}` with `data: {...}\n\n` frames (no EventSource anywhere); a gated second `read()` lets a test hold `verification` back until the typewriter finished (pins the `setTimeout(remaining)` branch).

- **Local vitest v4 run hangs / OOMs on worker teardown (infra, not logic):** on a memory-pressured machine, `vitest run <file>` executes the tests in ~2.5s then the worker leaks on teardown — the process never returns and prints ZERO output, so it *looks* stuck/broken but the assertions already passed. Reproduced on BOTH the default fork pool AND `--pool=threads` (8.19.7 close-out, 2026-07-03, `sudo_admin.render.test.tsx`). Do NOT chase it as a test-logic failure or a red gate — confirm the file green in CI on a normal-memory runner. Pairs with the sudo-code-review gate treating it as a CONCERNS "verify in CI", never a FAIL.

- **A `vi.mock` factory may NOT close over a plain top-level `const` spy** — `vi.mock` is hoisted above module-body `const`s, so `const cap = vi.fn(); vi.mock("@sentry/nextjs", () => ({ captureException: cap }))` throws `Cannot access 'cap' before initialization` and the file collects **0 tests** (looks like a mysterious empty suite, not an assertion failure). Fix: define the spy via `vi.hoisted` — `const { captureException } = vi.hoisted(() => ({ captureException: vi.fn() }))` — same spy, same assertions, no weakening. GOTCHA: this can lie dormant through a RED phase and only surface at ② once the *code under test* actually imports the mocked module (Story 16.3, 2026-07-13 — the `.red.test.tsx` mocked `@sentry/nextjs` but ErrorBoundary only imported it in ②, so the hoisting bug masked the behavioral reds until green-phase). An import/collection error masking behavioral reds is the same class as [[bdd-sync-step-needs-asyncio-run]] — fix the harness, keep every assertion.

Relates to [[agy-learner-e2e-harness]] (the Playwright/emulator layer above this) and [[test-debt-stories-are-characterization]].
