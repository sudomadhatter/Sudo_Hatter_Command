---
name: admin-credentials-drift-from-doc
description: AGY admin login debugging — live creds re-verified IN SYNC with login_testing_credentials.md 2026-07-25; bcrypt-check the live doc first, then suspect a wedged local backend (the "Server timed out" string is client-only)
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ed33e53-8983-4d0f-a973-5aa1c676933b
  modified: 2026-07-25T15:10:59.136Z
---

`_my_resources/_quick_reference/login_testing_credentials.md` is the operator's *intended* credential
list, NOT a readback of production. Live `admin_credentials/{email}` docs have drifted from it.

Confirmed 2026-07-24: `team@aviationchat.org`'s live password was `testpilotadmin`, not the documented
`testpilotadmin1215` — set by `backend/update_school_admin.py`, a loose script at `backend/` root
(commit 3882f0c4, "live debugging session, working on the log in fails for admin and sudo admin") that
did `remove_admin()` + `create_admin(password="testpilotadmin")`. Its sibling `backend/fix_sudo_pass.py`
reset the owner's password and force-stamped `super_admin` claims. **Both deleted 2026-07-24** — but the
class recurs: Phase 0 deleted 8 such scripts and swept only `backend/scripts/`, missing these two one
level up. (`backend/fix_sudo_pass.py` + `backend/add_secret.py` are back on disk and TRACKED as of
2026-07-25 on `main_debug` — the deletion landed on some other branch. Re-sweep.)

**Re-verified 2026-07-25 — the drift is GONE. All three live `admin_credentials` docs now bcrypt-match
the doc exactly** (`sudomadhatter@gmail.com`/`sudoadmin1215` super_admin·owner; `team@aviationchat.org`/
`testpilotadmin1215` school_admin·TESTPILOT; `demo@aviationchat.org`/`demo1215` school_admin·ACDEMO),
every `role` valid. So a login failure today is NOT credential drift — check the request path first.
That session's real cause was a **wedged local backend**: a long-running uvicorn on :8000 served
`/health` in 3ms while EVERY Firestore-backed route hung forever; the frontend's 15s `AbortController`
in `frontend/src/lib/adminApi.ts` turned that into the misleading *"Server timed out. Is the backend
running?"* (a client-only string the server never sends). A fresh uvicorn on a spare port from identical
code logged both accounts in at 0.7s. **Restart the dev backend before debugging anything.**

**Why:** admin auth is standalone bcrypt+JWT in `admin_credentials`, isolated from Firebase Auth, so
nothing reconciles it against the doc and a wrong password looks like broken login code.

**How to apply:** when an AGY admin login fails, FIRST read the live doc and bcrypt-check the candidate
passwords before touching auth code — one script, `GOOGLE_APPLICATION_CREDENTIALS=auth_keys/service-account.json`,
`bcrypt.checkpw(candidate, doc["password_hash"])`. Confirm `role` + `school_code` in the same read. Then
grep `backend/` (not just `backend/scripts/`) for any new credential-mutating orphan. Related:
[[agy-admin-role-fail-closed]], [[agy-has-real-nda-users]].
