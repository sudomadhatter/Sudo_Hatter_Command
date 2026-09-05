---
name: sudo-commands-have-ap-twins-that-drift
description: "The MAINTAINED twin pair is /cicd-* (for CODE, in projects) beside /smh-* (for working on the SYSTEM itself) — obligations live in one and go missing in the other, so fix one and check the twin. The old _AP autopilot twins are ABANDONED as of SCC-209 (2026-08-18): frozen, unmaintained, never diffed or ported to."
metadata:
  probe: "test -e .agents/rules"
  type: project
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-08-17T18:33:33.388Z
---

⛔ **The `_AP` autopilot twins are ABANDONED — do not maintain them** (operator ruling, SCC-209, 2026-08-18). `.agents/commands/cicd-*-AP.md` are headless adaptations invoked by the autopilot engines; the lane does not work and will be rewritten from scratch. All three files carry an `UNMAINTAINED` marker, `workflow_lint`'s twin-freshness check and its `ap_reconciled` stamp are deleted, and the files are KEPT only because three engines still invoke them by name. Never diff one against its primary, port law into it, or restamp it. Historically they *were* a drift pair, in both directions — that history is closed, not a reason to resume.

**The pair that IS maintained is `/cicd-*` ↔ `/smh-*`**, and it drifts the same way: a behaviour added to one is absent from the other, because nothing generates either from one source.

**The fix pattern that ends this class: put shared invariants in `.agents/rules/`, not in both bodies.** Rule 4 of `tests-must-gate-for-real.md` now owns the test-certification contract (certify at the shipping SHA · the (totals, SHA) pair · citable forms · mutation-by-relocation), and the dev/review commands each carry a one-line reference instead of a copy. Rules are byte-identical across the lobby + all maintained projects, so there is one place to change. ⛔ Hoist for single-source-of-truth value ONLY — **not** to save bytes: an oversized body now gets an auto-generated thin launcher, so size is handled and is no longer an argument.

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

**How to apply:** when you fix or audit a command, immediately open its `cicd`/`smh` counterpart and diff the obligations — anything one does that the other should too is likely a missing-parity bug. If the fix is an *invariant* rather than a step, put it in a rule and reference it from both. After editing the master `.agents/`, run `/sync-agents` (lobby + each project) to propagate. Related: [[close-out-command-is-daniels-signoff]], [[toolkit-sync-covers-agents-not-docs]], [[autopilot-engine-is-project-local]].
