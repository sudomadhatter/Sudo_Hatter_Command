---
name: review-findings-are-not-a-work-queue
description: "Review findings are never a ticket source — survivors of the relevance gate are fixed IN THREAD in the same lane. SCC-160 shipped the gate but was ruled NOT the full fix; the ruling + owed recut live ON THE TICKET (SCC-160 comment, 2026-08-15), not here."
metadata:
  type: feedback
---

**The rule:** review hunters are pointed at finding; volume is their metric. A finding that is
not worth implementing dies in triage with a one-line reason (engine step-03 relevance gate).
A finding that survives is **fixed in this thread, in this lane, before the verdict** — never a
residue ticket, never a "proposed decided" ticket, never a ticket-ruling row in `## Your Actions`
(that row holds the ticket on Review Required forever via `jira_feed finish`).

**Why:** a ticket the operator must rule on is still a ticket every story spawns — the loop
never drains. SCC-160's Ticket A/B row was judged the same loop under a new name.

**How to apply:** the operator develops from Jira, not from memory — the verbatim ruling, what
stands, and the owed recut (engine + both review commands + AP twin + test_review_engine pins +
the SCC-160 walkthrough row) are the 2026-08-15 comment on SCC-160. Read it before touching the
review engine. Do NOT pre-empt: the recut waits on the operator's notes from SCC-38's run.
Related: [[settled-decisions-are-not-gaps]] · [[review-status-means-needs-operator]] ·
[[prose-pinning-guards-are-vacuous]].
