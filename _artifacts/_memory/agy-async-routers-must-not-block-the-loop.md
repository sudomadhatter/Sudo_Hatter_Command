---
name: agy-async-routers-must-not-block-the-loop
description: "Sync Firestore calls inside an `async def` FastAPI route freeze every concurrent SSE stream on that worker — project-context.md §Sync-Only Mandate already mandates asyncio.to_thread, and it gets violated anyway; grep for it when touching any async router"
metadata: 
  node_type: memory
  type: project
  originSessionId: fd0be18a-da49-4433-b48f-a3bff6f02bf6
  modified: 2026-07-27T04:02:41.899Z
---

**The rule already exists and is written down** — `_bmad-output/project-context.md`:

> line 57 (§ Sync-Only Mandate): *"From async contexts, wrap sync I/O in `asyncio.to_thread()` (never
> block the event loop)."*
> line 129: *"ALL bulk synchronous Firestore fetches MUST be wrapped in `asyncio.to_thread()` … a single
> blocking `doc_ref.get()` loop over 34 documents can hang the entire SSE stream for 13+ seconds."*

**2026-07-26 (story 21.5 ③, independent pass).** All three new NDA-vault doors in `backend/routers/nda.py`
were `async def` calling a synchronous whole-collection Firestore stream **directly** — the per-record
export scanned the entire collection per request. It shipped through ①, ② **and** a full builder-authored
review pass. The same diff's `sudo_admin.py` backups endpoints used `asyncio.to_thread` correctly, so the
story contained both the rule and its violation.

**Why this needs a memory even though it is already a written rule:** the rule lives in a file nobody
re-reads mid-implementation, the violation is invisible in tests (mocked Firestore returns instantly, so
every suite stays green), and the symptom in production is *other people's* requests getting slow — never
the endpoint you are looking at. AGY streams SSE chat, so the blast radius is every concurrent learner on
that worker, not the admin who clicked.

**How to apply:**
- Touching any `async def` route that reads Firestore? Grep the file for `asyncio.to_thread`. Absent =
  suspect, not fine. **20 of 36 routers comply**, including every other `require_super_admin` admin router
  (`admin_dashboard.py`, `admin_cost.py`, `admin_evolution.py`) — copy their shape.
- `await asyncio.to_thread(fn, *args)` for a sync helper; `await asyncio.to_thread(lambda: list(q.stream()))`
  for an inline query. Behaviour-preserving — mock-based tests do not notice the change.
- Sync-Only also means: no `firestore.AsyncClient`, and `ThreadPoolExecutor` (not `asyncio.gather`) for
  concurrent reads. For fire-and-forget writes hold a strong ref to the `create_task`.
- When you fix one, put the rule citation in the docstring. An uncited convention gets "optimised" back.

Related: [[agy-true-p0-surface]], [[new-read-on-shared-endpoint-regresses-siblings]],
[[stubbed-children-make-green-vacuous]].
