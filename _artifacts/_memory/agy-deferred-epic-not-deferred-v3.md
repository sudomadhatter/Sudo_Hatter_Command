---
name: agy-deferred-epic-not-deferred-v3
description: "Future AGY work goes in a DEFERRED EPIC, never a deferred-v3 row under an otherwise-finished epic — that pattern holds the epic falsely open forever. Epic 22 is the precedent."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b80fc075-1753-4842-9946-7a790b19dc98
  modified: 2026-08-02T18:37:59.248Z
---

**Operator ruling, 2026-08-02 (Daniel):** *"V3 is not something that we are working on. If this is a
feature we want to add in the future it needs to be added to something else, we have full epics that
are deferred."*

**Why:** a `deferred-v3` row parked under an **otherwise-complete** epic keeps that epic falsely open
*forever* — and forever is literal, since the V3 pass is post-launch and explicitly not a lane being
worked. `epic-8` sat at 41/44 for months held open by exactly three such rows. Flipping it anyway
would contradict the board's own definition of `done` ("All stories in epic completed"); `descoped`
was equally wrong (these are "not yet", never "not ever").

**How to apply:** when parked work is the only thing holding an epic open, **mint a deferred epic and
relocate it**, then close the parent honestly. Precedent: `epic-22` (Evolution Engine V3 — Automated
Pedagogy Tuning) now holds 22.1/22.2/22.3, formerly 8.13/8.14/8.15. Leave the old ids as **comment-only
forwarding addresses** — not keys (a key re-holds the epic open), not deleted (a moved row with no
pointer is how work gets re-proposed from scratch). Like `epic-19`, a deferred epic is **outside** the
V3 pass; reviving it is a deliberate scoping decision.

Group parked work by what actually **binds** it — Epic 22's three share a *data precondition* (need
real student volume to tune against), not merely "we didn't get to it."

After this, **`epic-20` is the only board-tracked `deferred-v3` item.** `deferred-work.md` (35 items /
20 code reviews, unpruned since ~May) is still the V3 bucket. Related:
[[settled-decisions-are-not-gaps]], [[agy-epic-19-deferred-pin-cascade]], [[agy-epic-keys-rot-silently]].
