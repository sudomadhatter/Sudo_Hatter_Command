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
