---
name: a-defer-needs-a-structural-blocker
description: "A deferral is only legal with a STRUCTURAL blocker (another live lane owns the file / fix is in another repo / an open operator decision). Never a blocker: 'I'd have to edit a file.' Before deferring on a dilemma, look for the third door."
metadata:
  type: feedback
---

**The rule:** `deferred-work.md` defines exactly three blockers — another live lane owns the file,
the fix lives in another repo, or it waits on an open operator decision. Nothing else parks work.
There is no such thing as a blocker on *editing a file*: frozen / `UNMAINTAINED` / "don't restamp"
markers govern maintenance obligations, not write access.

**Why:** the operator's challenge, 2026-08-18 — *"is there no way for you to fix this? since when do
we have blockers on editing files?"* On SCC-205 I deferred the eight `-AP` law assertions in
`test_review_engine.py` and reported it as blocked. Both horns I named were true (deleting the
`-AP` files breaks three autopilot engines that invoke them by name; un-pinning them from
`CALLER_FILES` breaks the completeness row) — **and the dilemma was still false.** Nothing coupled
`CALLER_FILES` to a CHECKS row. The third door was to keep the file pinned as a *caller* and stop
asserting its *content*. A defensible-sounding dilemma is the easiest way to smuggle a non-blocker
past the ledger's own rules.

**How to apply:** before writing a ledger entry, name the third door explicitly and say why it does
not work — if you can't, there isn't a blocker and the fix belongs in the lane that found it. When
the blocker is "an open decision," ask the operator instead of parking: the ruling here took one
sentence and the fix took minutes. Prove a removal rather than assuming it (case count fell
873 → 849, exactly 8 rows × 3 checks).
Related: [[review-findings-are-not-a-work-queue]] · [[settled-decisions-are-not-gaps]] ·
[[blocking-gates-need-a-quoted-ruling]].
