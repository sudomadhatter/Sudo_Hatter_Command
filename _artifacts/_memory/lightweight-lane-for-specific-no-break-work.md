---
name: lightweight-lane-for-specific-no-break-work
description: "Operator ruling 2026-08-15 — not everything is a full /smh-quick-dev; a doc-only or otherwise can't-break ask gets ticket → edit → push, no plan-first stop or audit ceremony; the defined lane is SCC-162"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a052cb11-7154-410e-9d31-0ce6936470d9
  modified: 2026-08-15T07:07:35.385Z
---

**The ruling (2026-08-15, during SCC-161, the SOP bible audit):** *"we need to have a path outside the
workflow too, not everything is a full quick dev. sometimes I just want an agent to do something
specific. this is a prime example. this does not touch anything that can break. so we don't need to
over engineer it."* Earlier in the same turn: *"we are not running quick dev we are editing a doc thats
all"* and *"create a ticket, make the edits, push it."*

**Why:** the agent had opened the full Task-lane ceremony (plan-first STOP, worktree, self-audit, RED
assertion) on a doc-only edit. The operator's frustration was the same one behind [[review-findings-are-not-a-work-queue]]
("this exponential ticket creation makes no sense") — ceremony scaled to the ask, not to the risk.

**How to apply:** when the ask is specific, operator-directed, and touches nothing a gate would care about
beyond the Jira key (docs, a page rebuild, a reference fix — no deployable path, no hook/gate/script/rule
change): mint the ticket (agents mint; the operator's words are the decision), cut the `chore/<KEY>-<slug>`
lane so the commit carries a key, do the work, run the gates that apply mechanically (`run_all`,
`workflow_lint --toolkit-only`, the folder test if it is a SOP doc), commit explicit paths, push, and hand
back with a lean walkthrough (findings ledger + `## Your Actions`) — no plan approval stop, no self-audit,
no RED-first assertion, no review verdict unless asked. Do NOT ask "shall I mint / open a lane / write a
plan?" — that is the over-engineering. **The formal definition of this lane is SCC-162** (To Do); until it
lands, this memory is the rule. Still binding: [[main-merge-needs-operator-verbatim-approval]] — the merge to
`main` is still the operator's word through the door.
