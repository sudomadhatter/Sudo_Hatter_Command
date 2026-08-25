---
name: agy-has-real-nda-users
description: AGY_AVIATIONCHAT production has REAL NDA-signed beta users — never bulk-wipe users/ or Firebase Auth on the assumption it is all test data.
metadata: 
  node_type: memory
  type: project
  originSessionId: e09cdc62-ac2b-4838-bec1-339add00efb0
  modified: 2026-08-25T03:53:34.008Z
---

AGY_AVIATIONCHAT production (`aviationchat-database`) holds **real beta users, not test data**.
As of 2026-07-20, after cleanup: **7 `users/` docs, 6 of which carry `nda_signed_at`**, with signups
spanning Jan–Jul 2026 (incl. an Apple private-relay address). Firebase Auth holds 9 accounts.

**Why:** on 2026-07-20 the operator asked for a full `users/` + Auth wipe, stating "we dont have any
users at all... just old test data". A read-only audit disproved that before anything was deleted.
Two further traps a blanket wipe would have sprung:

1. `nda_signed_at` lives **on the `users/{uid}` document**. Deleting the doc destroys the only record
   that a person signed — and attorney ToS/Privacy is still outstanding before paid launch (tracked as
   an operator item on `sprint-dependency-map.md`; it is the last non-code blocker).
2. The three admin identities (`super_admin`/owner, a `school_admin`, and a demo account) are
   **interleaved in the same Firebase Auth list** as the learners — they are not in a separate bucket.
   Deleting "all Auth accounts" locks the operator out of the admin console.

**Update 2026-08-24 (story 19.3 ③ decision):** the operator restated the claim — "we only have
testing data there we have no users … even the NDAs are tests" — and ruled the nested
`lessons/{id}/session_feedback_log` rows wipeable on that basis. The 19.3 wipe honors this memory's
guards REGARDLESS of which reading is true: it never deletes `users/{uid}` docs, `nda_signatures`
stays keep-listed, and deletion is allowlist-only. So the ruling was safe to apply as scoped. The
open tension (operator's "all test data" vs the 2026-07-20 audit's 6 NDA-signed docs) matters only
if a users/-or-NDA wipe is ever requested — then this memory's audit-first rule still governs.

**How to apply:** never bulk-delete `users/` or Auth from a stated assumption. Run the read-only audit
first (`python -m backend.scripts.firebase_user_manager list`), show the operator the real inventory,
and delete only from an explicit allow-list of UIDs. The reusable purge tool
`backend/scripts/purge_and_repair_accounts.py` encodes the guards: allow-list only, re-reads each doc
at delete time and refuses on `nda_signed_at` or a protected uid/email, aborts on an ambiguous uid
prefix, and refuses to run without an existing backup. Exports go to `_my_resources/backups/`
(gitignored — they contain PII). Related: [[close-out-command-is-daniels-signoff]] covers when an
operator instruction IS authorisation; this is the counter-case where it is authorisation for a scope
that must first be verified against reality.
