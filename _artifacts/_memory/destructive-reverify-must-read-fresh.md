---
name: destructive-reverify-must-read-fresh
description: "A destructive helper that re-verifies its caller's condition against a PROCESS CACHE silently no-ops when the two disagree — the decline looks identical to success. Read fresh on the destructive path; log every decline."
metadata: 
  node_type: memory
  type: project
  originSessionId: d9adc5bc-e814-4396-b913-62eac264ecce
  modified: 2026-08-03T01:30:17.968Z
---

A safety pattern that quietly cancels itself. The caller decides to delete by reading **live** state;
the destructive helper re-verifies the same fact against a **process-lifetime cache**. Flip the flag
after the process started and the two disagree — trigger says "wipe", re-verify says "not mine",
the function returns `{}` and **logs nothing**. The operator performs the act, believes the data is
gone, and it survives. The decline is indistinguishable from a clean run.

Found 2026-08-02 (story 21.8b ③) in `demo_quarantine.clear_prospect_residue`:
`schools_service.set_member_access` decided to wipe from the `schools/{id}` doc it had **just
fetched**; `_is_demo_school_id` re-verified against the once-per-process demo-school SET.

**Two rules fell out, and they are separable:**

1. **Split the polarity by cost, not by tidiness.** The hot read-path keeps its cache (that cache is
   the entire reason the predicate is affordable on every graded session). The **destructive** path
   reads the doc **fresh** — one extra Firestore read, on an operator-initiated action that already
   costs a round trip. Symmetry here is the bug; the asymmetry is the design.
2. **Every decline on a destructive path LOGS.** "Did nothing" and "did the job" must never look
   alike from the outside. `clear_prospect_residue` had four ways to return `{}` (master account,
   unreadable doc, not-a-demo-member, nothing to delete) and only two of them logged.

**Related trap in the same class:** the function that WRITES the flag never invalidated its own
process's cache, despite the docstring naming that exact affordance. **The setter clears its own
cache** — the one invalidation that is free. Other processes (each Cloud Run instance) still need a
restart, which is an operational instruction, not something to pretend away.

**How to apply:**
- Grep for process-level caches before adding a destructive path near one. In AGY that is
  `demo_quarantine._demo_school_ids`, `demo_master`'s uid cache, and the ACP context cache.
- Any `if not <predicate>: return` inside a destructive helper needs a log line stating WHY it
  declined — with enough identity to act on (uid + the reason class).
- A cache whose value is set by an operator act needs an invalidation call **inside the setter**, and
  a restart instruction anywhere the multi-process case matters.
- Never hold a cache lock across the I/O that populates it — an outage then serializes every caller
  behind one hanging call. Double-check outside the lock; a duplicate query on a cold-start race is
  benign.

Related: [[agy-authz-claim-primary-ruling]], [[agy-corpus-is-the-asset]],
[[wedged-backend-fans-out-three-symptoms]].
