---
name: agy-archive-never-delete-ruling
description: "AGY standing ruling (2026-07-25): the product NEVER deletes a student — roster removal is an ARCHIVE (hidden, fully retained); story 21.3 was RE-SPECIFIED into the archive story rather than descoped, because descoping it would have orphaned NFR4."
metadata: 
  node_type: memory
  type: project
  originSessionId: 27c1ed6c-690d-4f25-91b4-b537755e900d
  modified: 2026-07-25T17:44:50.389Z
---

**The product has no delete.** Removing a student from a school roster is an **archive** — hidden
from the active list, every record retained. The data is the asset. Deletion stays **manual and
backend-only** via `backend/scripts/firebase_user_manager.py`, at the operator's explicit decision.
Never ship a delete endpoint, script affordance, or UI action for student records.

The 21.1 per-student access toggle **already blocks access and is correct as built** — archive is the
*visibility* half, not a replacement. The two are separate fields, so the ruling pairs them:
archive sets membership `revoked` in the **same call** (else you get an invisible-but-still-entitled
student — the exact failure 21.1's default-OFF exists to prevent), and un-archive returns them
**off**, to be granted deliberately. Fail-closed both directions.

**The structural lesson — re-specify, don't descope.** Epic 21 held **21.3 "Delete a Student — NDA
Survives."** The instinct on a reversed decision is to mark it `descoped` and mint a new story. That
would have been wrong here: when 21.2 was descoped on 2026-07-24, **NFR4 (tenant isolation) was
re-homed onto 21.3** — `epics.md` literally reads *"NFR4 remains live and traces to 21.3."*
Descoping 21.3 orphans it. Since the *intent* (remove a student from a roster) was unchanged and only
the *mechanism* changed, the right move was to rewrite 21.3 in place: same ID, same FR (E21-FR3
re-worded), same NFR trace, same own-school-or-404 scoping. Before descoping any story, grep what
re-homed onto it during earlier descopes.

**Reconcile all five surfaces or the old spec regenerates.** ① reads `epics.md`, not your board:
- `sprint-status.yaml` — key renamed `21-3-student-delete-nda-survives` → `21-3-student-archive-never-delete`
  (no story file existed, so nothing was deleted — `7-8-load-testing` precedent)
- `epics.md` — E21-FR3, the story spec, the story-map row, **plus** E21-FR5 and 21.5's AC, which both
  said "deleted student"
- `test-design-epic-21.md` — **held at P1.** The destructive/unrecoverable basis is gone, but access
  semantics + NFR4 remain. Never re-score a story *downward* unilaterally; that quietly cuts required
  coverage. Flag it for the operator instead.
- `active-context.md` + the 21.2 walkthrough — both carried `Next: <old delete slug>` pointers
- the sprint board

Design record: `_my_resources/Open_Tasks/debug_7_24.md` § Archive, not delete (includes the rejected
"full revoke" alternative — clearing `users/{uid}.school_code` destroyed the roster row one-way and
cut the school off from the student's history).

Related: [[agy-has-real-nda-users]] (why the data is protected), [[settled-decisions-are-not-gaps]]
(a stale pointer is how a ruled-on decision gets re-proposed), [[agy-authz-claim-primary-ruling]]
(the descope process this refines), [[agy-story-files-canonical-dir]].

## ⚠ The cost of never-delete: BY-ID → BY-FIELD makes every superseded doc a live duplicate

*(Merged in 2026-08-09 from `agy-school-identity-ghost-doc-window`, retired: the incident closed, but this
shape is the standing price of the ruling above and belongs with it.)*

**The generalisable rule — ask it of any migration that re-keys a collection:** when a lookup changes
from **BY-ID** to **BY-FIELD**, every superseded record that still carries that field becomes a live
duplicate. Never-delete plus field-queries is the trap; **either one alone is fine.**

Story 21.4 (2026-07-30) re-keyed `schools/{school_id}` to a stable name-slug with `code` as a rotatable
FIELD and lookups as `.where("code","==",…)`. `migrate_school_identity.py` copied each old
`schools/{code}` doc forward and — correctly, per the ruling — left the original standing *with its
`code` field intact*. So a superseded doc kept answering: a redemption could land in the **ghost**
(`users/{uid}.school_id = <the code>`, invisible to any `school_id`-scoped roster, never activatable),
and **a rotated code did not go dead** because the ghost still matched it.

**Resolved without breaking the ruling:** the migration now *retires* each old doc as its last
per-school act — `code` → `code_retired`, plus `migrated_to` and `retired_at`. It deletes nothing, so
the document, its members, and the code's value all survive and it stays reversible. Pinned by `MIG-008`
(a rotated code stays dead) and `MIG-009` (`_is_old_model` checks `migrated_to` **first** — a retired doc
has no `code` left, and the old `data.get("code") or doc_id` fallback read its own id back). Safe
mid-rolling-deploy: pre-21.4 code resolves `schools.document(code)` by DOCUMENT ID and never reads the
field. `AdminScope`/JWT/`scoped_user_query` all bind `school_id` — **never** re-introduce a code-reading
gate. Related: [[agy-redemption-has-two-doors]], [[agy-school-seat-cap-fails-closed]].
