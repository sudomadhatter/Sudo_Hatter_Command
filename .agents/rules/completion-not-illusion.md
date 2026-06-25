---
name: completion-not-illusion
description: "Activates for any workflow that produces polished intermediate artifacts (plans, audits, walkthroughs). A polished artifact is a claim, not proof of completion; mark incompleteness loudly."
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

## Why
Source: the autopilot loop's `-MaxStage 2` trial (2026-06-19) produced a plan + audit so polished
the partial run risked being remembered as a finished, hands-off story. The same illusion bites
manual work. The guard is cheap (an explicit marker); the failure - closing or shipping on
incomplete work - is not.
