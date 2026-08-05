---
name: agy-epic-keys-rot-silently
description: Epic keys in sprint-status.yaml go stale in four distinct ways — and a plausible stale REASON on the row is what keeps them alive.
metadata: 
  node_type: memory
  type: project
  originSessionId: b80fc075-1753-4842-9946-7a790b19dc98
  modified: 2026-08-02T18:48:30.750Z
---

The 2026-08-02 drift sweep closed **five** stale AGY epics (4, 8, 9, 14, 15) plus the 8.19 umbrella.
**Not one had any work owed** — every case was bookkeeping. Open epics went 6 → 2. Four failure modes:

1. **A stale reason-for-open is worse than no reason.** `epic-8` read *"Stories 8.1–8.9 done. Kept open
   for debugging stories"* — **both halves false** (43 children had shipped; no debugging story has ever
   keyed to epic 8 — debug-1/2/3 are their own epic keys). `epic-4` carried the *identical* false line,
   and the sprint-dependency-map faithfully repeated it for months. A plausible-sounding explanation
   answers the question that would otherwise trigger the audit. **Verify a status's stated reason
   against its children; never accept the note.**
2. **Umbrella/parent rows are structurally orphaned.** `8-19-two-tier-admin-umbrella` sat at
   `ready-for-dev` with 12/12 children done, precisely *because* its own note says "Do NOT implement
   directly; pick up a child" — no dev flow ever owns a parent, so no flow ever flips it.
   ⏳ **`12.3` is the same shape**, legitimately open at 5/7 (12.3.4 + 12.3.7 await the operator's live
   checkride pass). An **ORPHAN-PARENT WATCH** block now sits above its YAML row with the close
   condition: when those two flip to `done`, flip `12-3-igor-full-checkride` **and** `epic-12` in the
   *same* action. Don't leave the parent for "next time".
3. **A key can rot at its *creation* state, not just mid-flight.** `ready-for-dev` on a finished epic
   reads as *backlog*, not drift — so the sweep meant to catch it skips it. `epic-15` and `8.19` both.
4. **The missing-key hole.** A story with no key fires no drift check and is invisible to every
   readiness sweep. Three known: `4.27`/FR41 ✅, `8.12.2` ✅, debug-2.2 (the precedent).

**Before flipping any epic to `done`:** diff its `epics.md` story map against its keys — but know that
check is insufficient on its own, see [[agy-epics-md-is-partial]]. Related: [[story-status-flip-contract]],
[[sprint-dependency-map-recommends-stale-work]], [[landing-is-not-closeout]].
