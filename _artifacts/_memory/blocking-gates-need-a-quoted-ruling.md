---
name: blocking-gates-need-a-quoted-ruling
description: "A NEW blocking gate (anything that can exit non-zero on a shipping path) is new LAW — it must be surfaced in the plan as its own decision with the operator's ruling quoted beside it, never derived as a corollary and shipped inside a bundle."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f6e3053-d4b6-40eb-8dd6-bfa2e3469d85
  modified: 2026-08-15T02:32:46.924Z
---

**The failure this comes from (2026-08-14):** SCC-119's ticket asked for a *placement* rule ("related tasks are made as sub tasks to the main task"). What shipped added a derived lifecycle ("the parent closes LAST") and a hard exit-2 gate (`check_children`, `CHILD_CLOSED = ("done","deferred")`). The rule text then labeled the whole section "Operator ruling" — laundering derived law under the ruling's authority. Weeks later it walled the SCC-156 close-out and demanded manual Jira edits the operator never asked for. Operator: *"This new order rule I did not ask for."*

**Why:** A plan approval covers the plan's *stated decisions*. A gate buried as an "obvious implication" rides that approval without ever being decided. The intent can be good and the manifestation still wrong — the operator's exact framing.

**How to apply:**
- Any change that adds a check that can BLOCK a shipping flow (preflight error, hook refusal, hard exit) gets its own heading in the plan — "NEW GATES THIS ADDS" — with the operator's quoted words justifying it. No quote → it is a proposal to surface, not law to ship.
- When writing rule docs, never put derived corollaries under an "Operator ruling" header. Attribute the ruling to exactly what was said; mark the rest as design.
- At plan time, if an operator order contradicts an existing gate's assumption (e.g. one-lane order vs [[parallel-ok-is-a-set-property]]-style machinery), flag the collision THEN — ask "what happens at close-out?" before building. See the SCC-156/159 rider hole.

Related: [[main-merge-needs-operator-verbatim-approval]] · [[one-shot-permission-persists-in-context]]
