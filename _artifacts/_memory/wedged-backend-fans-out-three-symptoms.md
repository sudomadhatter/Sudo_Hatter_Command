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
retry. Never trust `/health` as evidence the backend is healthy. Related:
[[agy-error-envelope-shapes]], [[relocating-drops-mount-guards]].

## The credential half — check it second, and it is currently CLEAN

*(Merged in 2026-08-09 from `admin-credentials-drift-from-doc`, retired: its drift was re-verified gone
and its diagnostic belongs on the same chain as the wedge it was mistaken for.)*

`_my_resources/_quick_reference/login_testing_credentials.md` is the operator's *intended* list, **not a
readback of production** — admin auth is standalone bcrypt+JWT in `admin_credentials`, isolated from
Firebase Auth, so nothing reconciles it against the doc and a wrong password looks like broken code.
It **did** drift once (2026-07-24: `team@aviationchat.org` was `testpilotadmin`, not `…1215`, set by a
loose `backend/update_school_admin.py`), which is why this was ever a separate memory.

**Re-verified 2026-07-25: the drift is GONE** — all three live docs bcrypt-match the doc, every `role`
valid. So a login failure today is **not** credential drift; it is the wedge above.

**If you must check anyway:** one script with
`GOOGLE_APPLICATION_CREDENTIALS=auth_keys/service-account.json` →
`bcrypt.checkpw(candidate, doc["password_hash"])`, confirming `role` + `school_code` in the same read.
Then grep **`backend/`**, not just `backend/scripts/` — the original sweep missed two credential-mutating
orphans one level up. Status 2026-08-09: `update_school_admin.py` and `fix_sudo_pass.py` are **gone**;
`backend/add_secret.py` is still on disk and tracked (adds a secret, does not mutate passwords — lower
risk, but it is the same orphan class). Related: [[agy-admin-role-fail-closed]], [[agy-has-real-nda-users]].
