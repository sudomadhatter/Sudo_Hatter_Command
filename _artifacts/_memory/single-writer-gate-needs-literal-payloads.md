---
name: single-writer-gate-needs-literal-payloads
description: "The debug-1.5 single-writer gate AST-scans users/{uid} write sites — a variable or **spread payload it cannot read is an OFFENDER; keep dicts literal, never sanction the file"
metadata: 
  node_type: memory
  type: project
  originSessionId: 53787862-b9c8-4d97-bbe2-1b6379c921c0
  modified: 2026-07-26T02:52:15.899Z
---

`backend/tests/routers/test_hr_profile_single_writer.py::test_only_profile_service_writes_user_docs`
scans every `users/{uid}` write **statically**. It can only clear a payload it can *read*. A dict built
in a variable (`payload = {...}; if x: payload["k"] = v`) or splatted (`**base`) is opaque to the scan,
so it must assume the worst and fail — even when the payload provably touches none of the five
`CANONICAL_FIELDS` (name, call_sign, current_rating, checkride_type, checkride_date).

**Why:** the gate exists to stop a second writer of the identity fields from reappearing (the original
bug clobbered a call sign with a school code). Proving absence from an opaque expression is not something
a static scan can do, so opacity is treated as guilt. The conditional-dict form is the *natural* way to
write an optional field, which is exactly why this bites.

**How to apply:**
- Write both branches as **literal dicts** and let the `if` pick between them:
  `if email: ref.set({"active_session_id": sid, "email": email}, merge=True)` / `else: ref.set({...}, merge=True)`.
  Verbose, but readable to the gate. Carries an `AIDEV-NOTE` at `backend/routers/auth.py::create_session`.
- **Never resolve this by adding the file to `SANCTIONED_USER_WRITERS`** — that blunts the gate for every
  future writer in that module, which is the whole thing debug-1.5 exists to prevent.
- The `if` is doing double duty: it is also the clobber guard. `set(merge=True)` with `"email": ""` WIPES
  a populated field for any token lacking the claim.
- `email` is safe to write here; `name` is NOT — it is a `CANONICAL_FIELD` and belongs to
  `profile_service.set_field` alone. See [[agy-authz-claim-primary-ruling]] for the sibling
  "rulings live in docstrings, grep before writing" habit.

Surfaced by story debug-3.1 Fix 5 (2026-07-25), which failed this gate on its first implementation —
the triage doc never predicted it. Related: [[new-read-on-shared-endpoint-regresses-siblings]].
