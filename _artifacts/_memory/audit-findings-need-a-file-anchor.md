---
name: audit-findings-need-a-file-anchor
description: Adversarial fan-out audits manufacture findings; a finding with no file anchor is noise. Never build an audit-of-the-audit.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 71813977-199f-4dde-b2e1-ae56691de0e5
  modified: 2026-08-19T05:34:08.062Z
---

An audit lens handed a `findings[]` schema **will fill it**. On 2026-08-18 an 8-lens fan-out over one
implementation plan returned 44 findings / 13 HIGH; the operator judged roughly half to be agents
producing findings to succeed at the assigned task. The per-finding refutation pass meant to remove
them was the slowest phase, unfinished at 35 min, and killed — so the run delivered nothing.

**Why:** production of findings is cheap and front-loaded; filtering is expensive and back-loaded,
and it is O(n) over an n the production stage is incentivised to inflate. The schema is the real
incentive — the prose disposition test ("only REAL defects") is something the model rationalises past.
The only findings that survived were **measured against files**; everything reasoned-about-the-plan was
noise. An unanchored finding compares the plan to a counterfactual; an anchored one compares it to a file.

**How to apply:**
- **Anchor or it does not exist.** Every finding names an existing file path (with the literal text
  read) or an existing plan step number. No anchor → delete it, do not demote it.
- **Demand coverage, not findings.** The lens returns the checks it ran and what it read. Full
  coverage with zero findings is a *complete, successful* run — that is what makes "I found nothing"
  a valid deliverable.
- **Never build an audit-of-the-audit.** Operator ruling 2026-08-19: a separate refutation pass over
  findings is not effective. Fold the counter-case into the lens that already has the file open.
- **Corroboration promotes, never demotes.** Multi-lens agreement is *salience, not truth* — correlated
  lenses are not independent samples. It sets sort order only; a single lens finding a structural
  blocker is still top severity. Multi-lens without an anchor is consensus hallucination.
- **No hard-coded minute budgets or finding caps.** Rejected by the operator: audits differ in
  complexity, so fixed numbers are a risk. Scope by measured blast radius instead.
- **Judgment is not banned — it is denied a severity.** Beliefs with no check behind them go in a
  non-blocking observations section, never counted.
- **Over-engineering ships only as a ledger**, never an opinion: artefacts the plan *creates* vs the
  acceptance row requiring each. The finding is "no acceptance row requires this", never "this is
  unnecessary".

Rebuild tracked as SCC-225. Related: [[review-findings-are-not-a-work-queue]] ·
[[prose-pinning-guards-are-vacuous]] · [[tests-must-gate-for-real]] · [[settled-decisions-are-not-gaps]]
