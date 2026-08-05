---
name: agy-corpus-is-the-asset
description: "The real-user learning corpus is a future revenue line, not just training data — and the demo tenant is a disposable stage set whose data is placeholder BY DESIGN. That asymmetry is why the quarantine is strict and demo data is never precious."
metadata: 
  node_type: memory
  type: project
  originSessionId: d9adc5bc-e814-4396-b913-62eac264ecce
  modified: 2026-08-03T01:30:34.955Z
---

The operator's own framing, recorded verbatim during the 21.8b BDD lock (2026-08-02) because it
**re-frames how to reason about every demo/data decision**:

> The demo account exists so potential buyers can try the product fast without doing the whole lesson
> flow — "we would not do well with selling anything if this was the case." **None of that data should
> be kept.** It is NOT real data. The real users' data is one of our sources of future income and is
> critical — it must not be poisoned.

**Why it matters beyond one story.** Two conclusions follow that are easy to get backwards:

- **Demo data is disposable — treat it as a stage set.** Wiping a prospect's residue is not data loss,
  it is housekeeping. Do not design "safe" behavior around preserving it, do not ask whether to keep
  it, and do not weigh it against a real user's data at the same value. (This is why the 21.8b prospect
  wipe rides the operator's own revoke and simply deletes.)
- **The corpus is a monetizable asset, so contamination is a REVENUE bug, not a tidiness bug.** Story
  15.2's external-sale path exists because the dataset is saleable *because it is real*. A fake row is
  silent, cumulative, and — with no `school_id` on those records — unremovable. That asymmetry is what
  justifies failing CLOSED at the write boundary even though it drops some real rows on a Firestore
  hiccup: a dropped real row is recoverable next session, a fake row is forever.

**Do NOT confuse the two directions.** Per-user demo state (the debrief, the ledger, SARs) must keep
working — the demo has to feel real or it does not sell. Only the GLOBAL corpus refuses demo traffic.

The mechanism is `project-context.md` **Rule 11** (the quarantine, the Class A/B split, the fail
polarities, the AC5 gate). This memory is the *why* — the part that is not derivable from the code and
that gets re-litigated whenever someone proposes "preserving" demo data or relaxing the boundary.

Related: [[destructive-reverify-must-read-fresh]], [[agy-hanger-talk-is-the-free-tier]],
[[settled-decisions-are-not-gaps]], [[daniel-sells-hormozi-style]].
