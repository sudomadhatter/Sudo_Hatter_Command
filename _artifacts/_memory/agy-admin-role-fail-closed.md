---
name: agy-admin-role-fail-closed
description: "AGY admin_credentials role now fails CLOSED (Story 21.12) — a roleless/invalid doc is DENIED, never a defaulted super_admin; the `.get(\"role\", ROLE_SUPER_ADMIN)` anti-pattern was the Phase-0 escalation; 2 defused-but-latent sibling sites remain filed."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e5732cc-c395-48f1-8e22-de8d91973d79
  modified: 2026-07-25T19:17:37.769Z
---

AGY (AviationChat) admin auth: as of **Story 21.12 (done 2026-07-24)** an `admin_credentials` doc whose
`role` is not exactly one of `_VALID_ROLES` (`super_admin` / `school_admin`) — key absent, `None`, `""`, or
unknown — **fails CLOSED**: no admin identity, no JWT, never a defaulted `super_admin`.

**Root cause it killed:** the Phase-0 roleless-credential privilege escalation. A roleless credential doc
rode `data.get("role", ROLE_SUPER_ADMIN)` all the way to a full-operator token (with its password printed on
`/about`). The `.get("role", <privileged-default>)` pattern is the escalation class — **never reintroduce it**;
a new consumer that defaults a missing role to a privileged value re-opens the hole.

> **Corrected 2026-07-25 (Story 21.6):** the escalated record was a **`.com` typo record**, not a real
> account — there is no `demo@aviationchat.com` and there never was (see [[agy-domain-is-always-org]]). It
> existed inert in **both** `admin_credentials` and Firebase Auth, was never signed into, had no
> `users/{uid}` and no NDA, and 21.6 purged it from both stores with the operator's authorisation. The real
> account is `demo@aviationchat.org` (`school_admin`/ACDEMO). Don't cite the `.com` address as a live
> account when reasoning about this class — cite the *pattern*.

**The contract (all in `backend/`):**
- `services/admin_auth_service.py:118` `authenticate()` — validates `role in _VALID_ROLES` **after** the
  password check (quiet under brute-force; the WARNING names the doc id, never secrets) → `return None` → the
  login route 401s with the byte-identical anti-enumeration copy `"Incorrect email or password."`.
- `services/admin_auth_service.py:300` `list_admins()` — surfaces the truthful `role=None` (the broken record
  stays VISIBLE to the operator, not masked as a full operator).
- `routers/admin_auth.py:316` login mint — indexes `admin_data["role"]` directly; a roleless identity reaching
  the mint is a 500 (loud), never a silent defaulted token.

**Two sibling defaults were deliberately LEFT (decision D3) — defused + test-pinned, filed as a follow-on:**
- `routers/sudo_admin.py:188` list projection `a.get("role", ROLE_SUPER_ADMIN)` — safe ONLY because
  `list_admins()` keeps the `role` key present as `None` (so `.get` returns `None`). If a future change made
  `list_admins` omit the key, this silently re-opens. Pinned by
  `test_list_admins_surfaces_roleless_doc_as_none_through_endpoint`.
- `services/admin_auth_service.py:~133` `generate_jwt(role: str = ROLE_SUPER_ADMIN)` signature default —
  unreachable via a fixed `authenticate()`; only the 2-arg default survives in a legacy unit test.

A future small story should flip both to fail-closed (churns ~12 dependent test files).

**⚠️ When you close one fail-open guard, grep for its structural siblings before calling the surface
complete.** Carried over from the 2026-07-13 pre-launch audit (its own memory retired 2026-07-25, fixes
shipped to `main` in `dea87746`): hardening `_verify_oidc` surfaced **F-1** — `main.py::_verify_probe_oidc`
had the byte-identical fail-open and was only caught by the ② self-audit. The same shape recurred in the
IDOR fix: two `auth.py` profile endpoints trusted a client-supplied `user_id` while the identical
`token_uid` guard already existed at `hr.py:137` / `hr.py:213`. **Mirror the sibling convention rather
than inventing a new envelope, and enumerate every caller of the pattern you're fixing.** Underlying
helpers (`get_student_profile` / `update_student_profile`) do raw `users/{uid}` I/O with NO authz — scoping
MUST live in the router.

Sibling of [[agy-school-seat-cap-fails-closed]]. Admin-surface pitfall detail lives in the
`admin-dashboard.md` component spec. Same "check the siblings" family as
[[new-read-on-shared-endpoint-regresses-siblings]].
