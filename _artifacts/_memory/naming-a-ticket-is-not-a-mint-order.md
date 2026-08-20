---
name: naming-a-ticket-is-not-a-mint-order
description: Operator naming a ticket key while saying "fix it now" means file under existing coverage in the CURRENT lane — never mint. Minting needs the explicit word "mint".
metadata:
  type: feedback
---

2026-08-20, SCC-225 lane: a resolver bug surfaced mid-ceremony. Operator said "just fix it now with
this ticket scc-234" — I minted a fresh subtask (SCC-239). Correction was immediate and emphatic:
*"noooo i do not want now task just fix it in this one"*, then *"i can do this forever running of
new tasks"*. The mint was deleted the same minute.

**Why:** naming a key while saying "fix it now" is the operator pointing at EXISTING coverage (even
a stale/deleted key from a ticket's index) — the intent is work-consolidation rung 1: the lane's own
ticket covers it as a checklist line / plan part. Minting multiplies tickets, which is the exact
failure `[[cross-repo-work-needs-a-ticket-per-repo]]`-era sprawl taught: "we are not developing 3
tasks for every 1 we try to fix."

**How to apply:** discovered work mid-lane defaults to a plan part keyed to the lane's own parent.
Reach for `acli jira workitem create` only on the operator's explicit mint word ("mint it", "new
ticket"). A named-but-dead key = file under the live parent, note the dead pointer at close-out.
Related: [[discovered-work-becomes-a-lettered-part]] · [[review-findings-are-not-a-work-queue]].
