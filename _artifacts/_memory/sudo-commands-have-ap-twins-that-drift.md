---
name: sudo-commands-have-ap-twins-that-drift
description: Several sudo-* commands have a manual version AND an _AP autopilot twin; obligations live in one but go missing in the other. When auditing/fixing one, check the twin for parity.
metadata:
  type: project
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-08-03T01:33:18.563Z
---

The toolkit's dev-flow commands ship as **pairs**: a MANUAL command (e.g. `.agents/commands/sudo-code-review.md`, `sudo-dev-story-tests.md`, `sudo-self-audit.md`) and an `_AP` **autopilot twin** (`sudo-code-review_AP.md`, etc., tagged `platforms: [claude]`, invoked headlessly by `/autopilot_claude`). The two are NOT generated from one source — they're hand-maintained, so a behavior added to one can be **absent from the other**.

**Concrete drift found 2026-06-28:** the "update `walkthrough.md` after the review" step existed in full in `sudo-code-review_AP.md` but the word "walkthrough" never appeared in the MANUAL `sudo-code-review.md` — so manual reviews left the walkthrough stale (old status/test-count, no findings). Fixed by porting a manual-appropriate Step 5 into the manual command.

**Second drift, 2026-08-02 (the interactive one was wrong this time):** `sudo-dev-story-tests.md` Step 3 ordered the full-suite certification run BEFORE Step 4 (`bmad-testarch-automate`), the step that adds tests — so the pasted totals staled on arrival. The `_AP` twin had the correct order (expand → suite) all along. **Don't assume the twin is the stale one.**

**The fix pattern that ends this class: put shared invariants in `.agents/rules/`, not in both bodies.** Rule 4 of `tests-must-gate-for-real.md` now owns the test-certification contract (certify at the shipping SHA · the (totals, SHA) pair · citable forms · mutation-by-relocation), and ②, ②_AP, and ③ each carry a one-line reference instead of a copy. Rules are byte-identical across the lobby + all maintained projects, so there is one place to change. This also keeps command bodies under Antigravity's 11,500 B launcher threshold — a duplicated invariant costs bytes twice.

**How to apply:** when you fix or audit a `sudo-*` command, immediately open its `_AP` twin (and vice-versa) and diff the obligations — anything one does that the other should too is likely a missing-parity bug. If the fix is an *invariant* rather than a step, put it in a rule and reference it from both. Note the surfaces differ on purpose: `_AP` writes to the autopilot shared run folder; the manual one targets `_artifacts/<epic>/<story>/walkthrough.md` (the single closing doc per `artifacts-always-first`). After editing the master `.agents/`, run `/sync-agents` (lobby + each project) to propagate. Related: [[close-out-command-is-daniels-signoff]], [[toolkit-sync-covers-agents-not-docs]], [[autopilot-engine-is-project-local]].
