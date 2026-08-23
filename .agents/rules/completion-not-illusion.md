---
name: completion-not-illusion
description: "Activates for any workflow that produces polished intermediate artifacts (plans, audits, walkthroughs). A polished artifact is a claim, not proof of completion; mark incompleteness loudly."
trigger: model_decision
triggers: [done, complete, finished, is it ready, ship it]
# Intent-shaped: no glob can catch it, because the trigger is what the operator ASKS,
# not what gets opened. Antigravity judges `description:` against the request;
# `.agents/hooks/rule-trigger.py` matches these keywords and injects a pointer.

---

# Completion Is Earned, Not Implied (Artifacts != Done)

## When This Applies
Any workflow that produces polished intermediate artifacts - plans, audits, walkthroughs, status
banners - whether automated (e.g. the autopilot dev-story loop) or a manual session you drive
yourself. Applies to both Claude and manual / Antigravity workflows.

## The Trap
A confident, well-formatted artifact READS as completion. An `implementation_plan.md`, a thorough
audit, or a half-written `walkthrough.md` can look every bit as finished as a shipped story - so
partial work gets remembered (by you, by the next agent, by future-you) as done. The "PARTIAL"
banner scrolls past in a terminal; the polished file on disk is what survives.

## The Rule
1. **A polished artifact is a claim, not proof of completion.** Plans, audits, and drafts are
   intermediate. Completion requires explicit, verifiable signals: tests green with REAL pasted
   output, the walkthrough's "Your Actions" done, story status updated, and the change committed.
2. **Mark incompleteness LOUDLY and explicitly.** Never rely on the *absence* of a signal (no
   walkthrough, no diff, status still `ready-for-dev`) to convey "not done" - absence is exactly
   what is easy to miss. Stamp partial / paused / trial work with an unmistakable marker (a status
   line at the top of the artifact, a `_RUN-STATUS.md`, a banner) that names what is NOT done.
3. **Don't let a stopping point masquerade as a finish line.** A trial run, a `-MaxStage` stop, a
   plan awaiting approval, or a paused session are all INCOMPLETE until the close-out steps run.
   Say so plainly - in the artifact AND in your summary to the user.
4. **An unverified open box is not evidence of owed work** (SCC-298). The rule above runs in the
   other direction too: a `- [ ]` in `## Your Actions` is a CLAIM that something is still owed,
   and an unchecked claim is no more trustworthy pointing that way than the other. Agents are
   reliably bad at ticking a list, and worst at the rows that are the operator's - so at close-out
   you **reconcile before you close**: derive the check for each open row and run it, tick on what
   it returned; where no machine check exists, ASK the operator and tick on their word, quoted;
   what is neither proved nor answered stays open and gets reported. `jira_feed.py
   reconcile-actions` is the door, and it is mandatory in every command that runs
   `jira_feed.py finish`.
   ⛔ **Verifying is not self-certifying.** You record what a check returned or what the operator
   said - you never derive the evidence and accept it in the same breath. The one row you may not
   tick at all is the merge row: `finish` computes that from the repo (SCC-175), because a tick
   is a claim and the ancestry check is the answer.

## Why
Source: the autopilot loop's `-MaxStage 2` trial (2026-06-19) produced a plan + audit so polished
the partial run risked being remembered as a finished, hands-off story. The same illusion bites
manual work. The guard is cheap (an explicit marker); the failure - closing or shipping on
incomplete work - is not.
