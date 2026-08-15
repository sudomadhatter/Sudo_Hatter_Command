---
name: review-findings-are-not-a-work-queue
description: "Operator ruling 2026-08-15 (SCC-160): verified-TRUE is not worth-implementing — the review's triage owns a relevance gate and most little findings die there with a one-line reason; residue tickets ('ONE follow-on for the N deferred items') are retired in both directions."
metadata:
  type: feedback
---

**The ruling (2026-08-15, verbatim):** "this whole create a ticket for all the random little
findings is not effective and is a waste of time and resources. we need the agent who reviews the
code review to decide which are actually relivant to impliment. the agents who review this have
the goals of finding things, this doesnt mean they are all actually relivant to impliment this is
a flaw in our process."

**Why:** hunter agents are POINTED at finding — volume is their success metric. Treating every
verified-true finding as owed work converts that metric into a work queue: two consecutive
landings (SCC-154: 9 items, SCC-156: 16 items) each ended with a "deferred residue owed to ONE
follow-on ticket" action row handed to the operator. Both piles re-triaged under the new gate:
25 items → 8 survivors, 13 kills, 3 ledgered, 1 operator ruling — zero residue tickets.

**How to apply:** the law lives in `code-review-engine` step-03 (`### The relevance gate`) — a
true finding enters patch/defer only by passing one of three legs: (1) realistic damage path
TODAY with a named actor and moment, (2) it undermines evidence the house cites as proof
(verdicts, receipts, mutation-kill attribution, suite totals), (3) the operator asked. Fails all
three → dismissed with a one-line reason in the findings table. Default-dead classes: doc
symmetry, coverage-for-symmetry, style preference, prose pins ([[prose-pinning-guards-are-vacuous]]).
Survivors: fix in-lane, or ledger as a JUDGED ride-along (`_artifacts/_main/deferred-work.md` —
nothing in it is owed), or (rarely) PROPOSE one decided chore ticket naming why each item earned
it — the operator's word mints it. Never leave the operator a "mint the residue ticket" row
([[review-status-means-needs-operator]]); never file a ruled-on decision as a gap
([[settled-decisions-are-not-gaps]]).
