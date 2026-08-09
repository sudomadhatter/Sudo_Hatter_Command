---
name: agy-domain-is-always-org
description: "AviationChat is ALWAYS aviationchat.org — every @aviationchat.com address in the repo was a typo, never a real account; Story 21.6 scrubbed all 17 and a CI grep gate now keeps live code at zero."
metadata: 
  node_type: memory
  type: project
  originSessionId: d66e2178-5d8a-4ad6-a3d7-69ee9388dda2
  modified: 2026-07-25T19:17:54.280Z
---

AGY (AviationChat) owns **`aviationchat.org`**. There is no `.com`. Every `@aviationchat.com` address that
was ever in this repo — `demo@`, `operator@`, `legacy@`, `admin@` — was a **typo**, not a real account.
Ratified by the operator 2026-07-23 and shipped as **Story 21.6** (done 2026-07-25).

**The five real accounts** (`_my_resources/_quick_reference/login_testing_credentials.md` is canonical):
`sudomadhatter@gmail.com` (super_admin·owner) · `team@aviationchat.org` (school_admin·TESTPILOT) ·
`demo@aviationchat.org` (school_admin·ACDEMO) · `schooltesting@aviationchat.org` ·
`solotesting@aviationchat.org` (students). Only the first three have `admin_credentials` docs — see
[[wedged-backend-fans-out-three-symptoms]] § the credential half.

**Enforced mechanically, not by discipline.** `backend/tests/routers/test_story_21_6_demo_account_model.py`
greps the tree for the forbidden domain and fails the suite on any hit. Two things about that gate matter
if you ever touch it:
- Its needles are **assembled from parts** so the gate does not self-match its own source. A gate that
  matches itself is a fiction test — ① caught exactly that trap here.
- It carries a *guard-the-guard* (`test_scan_roots_resolve`) so it can never pass by scanning nothing, plus
  a scan ceiling. Scope is `backend/`, `frontend/src`, `frontend/e2e`, `frontend/tests`, `.github`,
  `**/*.feature`. **`_artifacts/` and `_bmad*/` are deliberately carved out** — those are historical
  records and rewriting them would falsify history. A component spec is **not** history: fix those in place.

**Corollary — demo behaviour keys off the SCHOOL, never an email allowlist.** 21.6 deleted the `isDemoEmail`
/admin-bounce exemption outright (it was provably unreachable: `demo@aviationchat.org` is `school_admin`,
and `/admin` bounces `super_admin` only). Any future demo carve-out keys off `schools/ACDEMO` per 21-8/21-8b.
Do not reintroduce an address allowlist. The surviving `_DEMO_ADMIN_EMAILS` in `backend/routers/bug_reports.py`
is a *different*, intentional denylist on 4 sensitive endpoints — it is `.org`-only and its test iterates the
set rather than hardcoding an address. Leave it.

Corrects the `.com` account reference in [[agy-admin-role-fail-closed]]. Related: [[agy-has-real-nda-users]].
