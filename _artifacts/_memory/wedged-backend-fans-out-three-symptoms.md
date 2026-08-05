---
name: wedged-backend-fans-out-three-symptoms
description: A wedged local uvicorn serves /health in 3ms while hanging EVERY Firestore route — it fans out into 3 unrelated-looking frontend errors; restart the dev backend before debugging AGY local auth
metadata: 
  node_type: memory
  type: project
  originSessionId: c171c7fb-ceb3-4170-9f44-54b851ef38d2
  modified: 2026-07-25T15:27:05.662Z
---

A long-running AGY dev `uvicorn` can wedge into a state where **non-dependency routes stay instant but
every Firestore-backed route hangs forever**. Observed 2026-07-25 (PID up ~20 min): `/health` 200 in
**3 ms**, `/openapi.json` 200 — but `POST /api/admin/auth/login` no response at 30 s, **including with a
bogus email** (proves it's the Firestore read, not credentials). A **fresh uvicorn on a spare port, same
commit, same machine, logged in at 0.7 s** — that A/B is the cheapest way to prove process-vs-code.

**It fans out into three symptoms that look like three different bugs:**
1. Admin login → *"Server timed out. Is the backend running?"* — a **client-only** string from the 15 s
   `AbortController` in `frontend/src/lib/adminApi.ts`. The server never sends it.
2. A different admin account → reads as **"the password is not working"** (same hang, generic failure).
3. Student side → `Unexpected token 'I', "Internal S"... is not valid JSON`, then
   *"Session not initialized — authenticatedFetch blocked before sessionReady."* Chain: Next rewrite hits
   `ECONNREFUSED` → returns **plain-text** `Internal Server Error` → `AuthContext.initSession()` parsed it
   → `SyntaxError` swallowed by its `catch` → `sessionReady` never true → the `api.ts` guard then blamed
   **the calling component** for a backend outage. Blocks school-code redemption and every gated call.

**Why:** a liveness probe that touches no dependency cannot detect this class of wedge, and each layer
rewrote the error into something that named the wrong culprit — so the operator hunts credentials, wifi,
and React components while the real fault is one hung process.

**How to apply:** when AGY local auth misbehaves, **restart the dev backend FIRST** — before reading auth
code. Then confirm with the two probes that actually discriminate: (a) login with a *bogus* email — if
that hangs too it's the Firestore read, not the password; (b) start a second uvicorn on a spare port and
retry. Never trust `/health` as evidence the backend is healthy. Credentials were verified in sync and
production was fine the whole time — see [[admin-credentials-drift-from-doc]]. Related:
[[agy-error-envelope-shapes]], [[relocating-drops-mount-guards]].
