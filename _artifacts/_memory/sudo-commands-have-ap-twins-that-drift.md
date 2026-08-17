---
name: sudo-commands-have-ap-twins-that-drift
description: "Commands ship in pairs and the pairs drift — a manual one beside its _AP autopilot twin, and a /cicd-* one (for CODE, in projects) beside its /smh-* one (for working on the SYSTEM itself). Obligations live in one and go missing in the other. Fix one, check the twin — same instruction for both kinds of pair."
metadata:
  type: project
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-08-17T18:33:33.388Z
---

The toolkit's dev-flow commands ship as **pairs**: a MANUAL command (e.g. `.agents/commands/sudo-code-review.md`, `sudo-dev-story-tests.md`, `sudo-self-audit.md`) and an `_AP` **autopilot twin** (`sudo-code-review_AP.md`, etc., tagged `platforms: [claude]`, invoked headlessly by `/autopilot_claude`). The two are NOT generated from one source — they're hand-maintained, so a behavior added to one can be **absent from the other**.

**Concrete drift found 2026-06-28:** the "update `walkthrough.md` after the review" step existed in full in `sudo-code-review_AP.md` but the word "walkthrough" never appeared in the MANUAL `sudo-code-review.md` — so manual reviews left the walkthrough stale (old status/test-count, no findings). Fixed by porting a manual-appropriate Step 5 into the manual command.

**Second drift, 2026-08-02 (the interactive one was wrong this time):** `sudo-dev-story-tests.md` Step 3 ordered the full-suite certification run BEFORE Step 4 (`bmad-testarch-automate`), the step that adds tests — so the pasted totals staled on arrival. The `_AP` twin had the correct order (expand → suite) all along. **Don't assume the twin is the stale one.**

**The fix pattern that ends this class: put shared invariants in `.agents/rules/`, not in both bodies.** Rule 4 of `tests-must-gate-for-real.md` now owns the test-certification contract (certify at the shipping SHA · the (totals, SHA) pair · citable forms · mutation-by-relocation), and ②, ②_AP, and ③ each carry a one-line reference instead of a copy. Rules are byte-identical across the lobby + all maintained projects, so there is one place to change. This also keeps command bodies under Antigravity's 11,500 B launcher threshold — a duplicated invariant costs bytes twice.

⭐ **The SAME instruction covers the `/cicd-*` ↔ `/smh-*` pair, which is the other kind of twin** (operator, 2026-08-17). `/cicd-*` is for **code** — project development under `Projects/`, story lanes, epic branches; `/smh-*` is for **working on the system itself**, the command centre repo. `cicd` is the one used far more.

⛔ **They are the SAME development system — do not read the split as two different flows.**
Operator, 2026-08-17: *"they are our same development system, the actual system we use for real
work on projects. the smh ones are only for working on the system. but they serve the same purpose,
just optimized for their tasks."*

**`/cicd-*` IS the development system** — the real one, used for real work on real projects, and the
one that matters most. **`/smh-*` is that same system turned inward**, and *only* for working on the
command centre itself. Same purpose, same plan-first gate, same artifact set, same review engine,
same close-out discipline, same two stops — each optimized for its own subject.

So **parity is the DEFAULT and divergence is the exception**, which is exactly why drift here is
damaging rather than harmless: most of the two bodies genuinely should match, so a difference is a
missing-parity bug until proven otherwise. And when the two disagree, `/cicd-*` is the one carrying
real project work — do not leave it the stale one while polishing the inward-facing twin.

What legitimately differs is only what the SUBJECT forces: the merge target (`origin/main` vs the epic branch), the spec source (`implementation_plan.md` vs the story file + certification), and the one-line ladder in `smh-target-resolution.md` — *"Every `/cicd-*` command operates on exactly ONE target — never the lobby."* Everything else — engine contracts, runtime probing, severity floors, evidence rules — belongs in both identically, and is best hoisted into a rule so there is one copy to change.

**How to apply:** when you fix or audit a command, immediately open its twin — the `_AP` one, **and the `cicd`/`smh` counterpart** — and diff the obligations — anything one does that the other should too is likely a missing-parity bug. If the fix is an *invariant* rather than a step, put it in a rule and reference it from both. Note the surfaces differ on purpose: `_AP` writes to the autopilot shared run folder; the manual one targets `_artifacts/<epic>/<story>/walkthrough.md` (the single closing doc per `artifacts-always-first`). After editing the master `.agents/`, run `/sync-agents` (lobby + each project) to propagate. Related: [[close-out-command-is-daniels-signoff]], [[toolkit-sync-covers-agents-not-docs]], [[autopilot-engine-is-project-local]].
