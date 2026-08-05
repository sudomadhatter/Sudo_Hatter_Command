---
name: sudo-admin-jsdom-oom-machine-bound
description: "CORRECTED 2026-07-26: the AGY /sudo_admin vitest 'machine-bound jsdom OOM' was never environmental — an unstable useRouter() mock drove an infinite synchronous render loop. Fixed in all 4 files; suite runs in 8s. Check mock identity stability before blaming the machine."
metadata:
  node_type: memory
  type: reference
  originSessionId: 6f87e86f-4915-43e9-92bf-47337a047e1e
  modified: 2026-07-27T01:57:08.472Z
---

⛔ **This memory previously said the `/sudo_admin` page suites OOM the jsdom worker on this laptop,
env-not-code, "trust component suites + CI". That was WRONG and it cost two full story passes** (21.5
① and ②) plus a recorded 2-day loop. Root-caused during 21.5's ③ review.

**The real cause — a test seam, not the machine.** All four `/sudo_admin` test files mocked the router
as `useRouter: () => ({ push: mockReplace, replace: mockReplace })` — a **fresh object every call**.
`page.tsx`'s route guard is `useEffect(..., [router])`, so a new router identity on every render
re-fires the guard → it calls `setOperator({...})` with a fresh object → `operator` changes → re-render
→ another router. **Infinite synchronous render loop.** Fix: hoist the object to a module constant.

**Why it masqueraded as an OOM.** Every render allocates, so the loop *does* exhaust the heap and *does*
print `Ineffective mark-compacts near heap limit` → `Worker exited unexpectedly`. The heap death is the
SYMPTOM. That is why raising `--max-old-space-size` only delays it, why `--no-file-parallelism` and
`singleFork` don't help, and why reaping workers never fixed anything. It also explains the useless
stack: the loop is **synchronous**, so `testTimeout` can never fire and vitest reports 0 tests run.

**The transferable lesson: an unstable object returned from a mocked hook can produce an infinite
render loop, and vitest reports that identically to an OOM.** Before concluding "environmental",
check whether any mocked hook returns a fresh object/array into a dependency array.

**Diagnostic ladder that actually worked** (each step ruled something out):
1. Audit processes — orphaned workers or not? (Here: none; all node procs legitimate.)
2. Raise heap + `--no-file-parallelism`. Still hangs → not memory, not contention.
3. Minimal probe in the same directory: bare assert, then `import()` the page, then render it.
   Passing → jsdom, directory and import are all fine.
4. Vary the auth mock. Hanging only once the guard reaches its `setState` localises it to an effect.
5. `testTimeout` never firing during a long hang **proves the loop is synchronous**.

**Result after the fix:** story file 7/7 in 4.05s (had never executed at all) · `src/app/sudo_admin`
4 files / 24 tests in 8.14s (3 of 4 previously hung forever) · full frontend suite completes for the
first time, 493 passed / 1 skipped in 111.64s.

⚠️ Those 3 sibling files (`top-tabs.red`, `dataset.red`, `render` — stories 8.19.7 / 17.2) had been
silently not running. They pass now, but nobody has audited what they assert against current source.

⚠️ CI runs `npm run test -- --run` over everything except `e2e/**` in ONE job, so a hanging page suite
hangs the whole frontend gate — never leave one in place as "someone else's file".

Related: [[agy-frontend-vitest-harness]] (jsdom rAF/timer gotchas) · [[vitest-full-suite-contends-across-lanes]] ·
[[e2e-gate-fiction-test-guardrails]] (the selectors here were real, not fiction — `role="tab"` verified in source).
