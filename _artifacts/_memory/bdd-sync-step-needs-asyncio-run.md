---
name: bdd-sync-step-needs-asyncio-run
description: "AGY pytest-bdd sync steps driving an async fn must use asyncio.run, not get_event_loop().run_until_complete (raises on Py 3.12+/3.14)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5982af64-8a60-4381-b7a0-127ce0237a10
---

A pytest-bdd `@when`/step is a **sync** function; to drive an `async def` production seam it must use
`asyncio.run(coro)`. The old `asyncio.get_event_loop().run_until_complete(coro)` **raises**
`RuntimeError: There is no current event loop in thread 'MainThread'` on Python 3.12+ (AGY runs on
**pythoncore-3.14**) — `get_event_loop()` no longer auto-creates a loop when none is running.

**Why:** In a ① ATDD skip-guarded RED step, this bug is *masked* — the earlier `ImportError` (missing
production fn) fires first, so the step "goes RED" and looks correct. At ② dev the import resolves and the
latent harness bug surfaces as 5 red scenarios that are NOT a production failure. Fix the harness (swap to
`asyncio.run`), assertions untouched — don't chase the production code.

**How to apply:** when authoring pytest-bdd step adapters in ① that call an async executor, write
`asyncio.run(execute_x(...))` from the start. Seen in 17.10's `test_hr_attach_school_code_steps.py::_attach`.
Related: [[agy-frontend-vitest-harness]], [[test-debt-stories-are-characterization]], [[agy-canonical-test-venv]].
