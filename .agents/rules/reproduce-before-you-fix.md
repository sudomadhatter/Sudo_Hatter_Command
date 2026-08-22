---
name: reproduce-before-you-fix
description: "Activates the moment something is reported broken — a bug, a red suite, an incident, 'it's not working', a Sentry alert. The house debug loop: reproduce → pin with a failing test SEEN red → falsify one hypothesis at a time → minimal fix at the cause → prove the test catches it by reverting the fix. No fix without a reproduction; no bug fix without a pinning test."
why: "Reproduce, locate, fix-and-verify plus the ten-minute rule are MIT 6.031; hypothesis ordering and falsify-don't-confirm are Verraes (2024)."
since: 2026-08-04
---

# Reproduce Before You Fix

## When This Applies

Anything reported broken, from the report until the fix is proven: a bug, a red suite, a production
incident, "it's not working," a Sentry alert. Claude, autopilot, and manual runs alike.

**Not** for building something new — that is the ATDD red phase (`tests-must-gate-for-real`). This rule
is for something that *used to work*, or was supposed to.

## The Trap

Debugging degrades into guessing, and guessing looks like work: each guess → edit → "try now" cycle
produces motion, a diff, and no knowledge. A fix with no reproduction fixes the bug you imagined. A test
written *after* the fix proves the code passes a test — not that the test would have caught the bug;
those are different claims. And a symptom patch closes the ticket while leaving the mechanism live
everywhere else it reaches.

## The Rule — five gates, in order

### G1 · REPRODUCE — name it, or you don't have it

The reproduction must be a **citable artifact** someone else could run: an exact command, a URL plus
click path, a Sentry event id, or a failing test. *"I read the code and I can see the bug"* is a
**hypothesis** — that belongs in G3.

Two legitimate exits, both endings rather than workarounds:

- **You can't observe it but Daniel can** (browser console, network, Firestore, UI) →
  `collaborative-debug-first`. One targeted log, one specific question, then resume at G1.5 with his
  output as the reproduction.
- **It genuinely does not reproduce** — heisenbug, prod-only, race, one Sentry event and nothing since.
  **Add observability, say so plainly, stop.** Naming a bug unreproducible is a real result; you cannot
  verify a fix for something you cannot trigger. (Same shape as `cicd-mobile-error-team`'s "not a fire.")

### G1.5 · MINIMIZE

Narrow to the smallest input, path, or dataset that still fails; strip one variable at a time. This
shrinks the hypothesis space, and it usually *is* the diagnosis — the last thing you removed that made
it stop failing is the thing.

### G2 · PIN — write the failing test and SEE it red

Write the test **before** the fix, run it, and **paste the red**. Not "this test will fail" — the actual
failure.

- The red must fail for the **right reason** — every asserted string, selector, endpoint, and
  precondition verified against real source. A test asserting copy that isn't in the codebase fails
  identically whether the bug exists or the test is fiction. Full treatment: `tests-must-gate-for-real` rule 1.
- **Name the test after the bug** — story id, issue number, Sentry short-id. Provenance survives the fix.
- **Commit the red**, even though it breaks the build for one commit. That commit is the evidence the
  bug was real, and the only moment its redness is cheap to demonstrate.
- A config/copy tweak that genuinely cannot carry a test: say so **explicitly**, in one line. Silence
  here reads as an oversight.

### G3 · FALSIFY — one hypothesis at a time, timeboxed

**List every hypothesis before testing any**, including the unlikely ones — an implausible candidate
often surfaces the real one. Don't debate them; write them down. Order by **probability ÷
cost-to-disprove**, cheap-and-likely first. Then for each, try to **disprove** it with the minimum change
or extra test that would rule it out, and stop the moment evidence lands either way. **One change, one
observation.** Never stack speculative fixes.

**Stop conditions — any one fires, you stop editing and escalate:**

| Signal | Threshold |
|---|---|
| Unsystematic poking with no hypothesis list | 10 minutes *(MIT 6.031's ten-minute rule)* |
| Hypotheses falsified with no new lead | 3 |
| Edits that produced no new evidence | 2 |

*(Thresholds are house-set, not literature — tune them if they prove wrong; don't ignore them.)*

Escalation is **not failure**. Hand over the reproduction, the minimized case, the red test, and the
list of what is now **ruled out** — that is real progress, and exactly what the next agent or Daniel
needs. In a `/cicd-quick-dev` lane it is the same signal as the EJECT tripwire: stop, this is not a
quick fix.

### G4 · FIX — minimal, at the cause

The smallest change that addresses the mechanism. **No** refactors, **no** drive-by cleanups, **no**
dependency bumps, **no** "while I'm in here." A symptom patch is not a fix; if you can't name the
mechanism, you are still in G3.

If the cause is **architectural** — the design permits this class of bug — fix the bug minimally and
record the architectural finding as a **follow-up**. Never rewrite a design under a bug ticket.

### G5 · PROVE — revert the fix, watch it go red

**Revert only the fix hunk. Re-run the pinning test. Confirm it goes red. Restore the fix.**

This is the gate everyone skips. A test that passes alongside a fix may be passing coincidentally, for a
reason unrelated to the change; reverting is the only cheap proof that *this* test catches *this* bug.
Never substitute **deleting** the guard — deletion kills the structural tests too and isolates nothing
(`tests-must-gate-for-real` rule 4).

Then run the **whole surrounding module suite**, not just the new test — a fix inside a shared handler
breaks siblings silently. Paste actual output. Remove the temporary debug logs.

## Contributing causes — plural, and the miss

Google SRE says *contributing causes*, not "the root cause," on purpose. Record three things:

1. **Mechanism** — why it broke, in a sentence or two, specific enough to search for elsewhere.
2. **Reach** — what else shares that mechanism. Then **actually go look.** One bug is a report; the same
   mechanism in four places is the finding.
3. **The miss** — why no existing test caught this. Usually the most valuable output of the session, and
   the one people forget to write down.

"Why does the architecture allow this bug?" (`karpathy-guidelines` §1) is a **written** answer here, not
a private thought. Postmortems are blameless: the subject is the system, never a person or an agent.

## Anti-Patterns

❌ Fixing before reproducing — "I can see the problem in the code," then an edit.
❌ A test written after the fix, never seen red — proves the code passes, not that the test guards.
❌ "I changed 3 things, try now."
❌ Deleting the guard to prove a test works — kills both tests, isolates nothing. Revert instead.
❌ Calling a symptom patch a fix because the ticket closed.
❌ Shipping without asking why nothing caught it.
❌ Guessing past a stop condition because the next idea feels promising. They always do.

## Why

Reproduce · locate · fix-and-verify and the ten-minute rule are **MIT 6.031**. Hypothesis lists,
probability ÷ time-to-disprove ordering, falsify-don't-confirm, and committing the failing test are
**Verraes, *How to Fix a Bug: Tests, Hypotheses, Timeboxes*** (2024). G1.5 is **delta debugging**. "Run
it first to confirm it fails, then fix, run again" is the regression-test consensus — TestRail,
CircleCI, and Black's contributing guide state it in those words. Contributing causes and blamelessness
are **Google SRE**.

House evidence for G2 and G5: AGY 2026-07-13, a spec asserting four UI strings that appear **0×** in the
frontend source — it never passed and never could, so it protected nothing while reading as coverage.
And AGY story 21.8b, where the first mutation check *deleted* the guard, killing the structural test
alongside it and isolating nothing; only relocating it proved the behavioral test carried its weight.
Both are diligence-shaped failures, which is why they are written down.

The halves of this rule already existed — `karpathy-guidelines` §1 (root cause before symptom),
`cicd-quick-dev` Step 3's review gate (one pinning regression test), `cicd-mobile-error-team` §4 (regression test
mandatory), `collaborative-debug-first` (instrument, don't speculate). What was missing across every
rule and command was **reproduction**: one grep for `reproduc*` over the whole `.agents/` tree returned
a single hit, about a disk path. That is the gap this closes.
