---
name: artifact-budgets-are-scoped-not-universal
description: "The 8 KB / 10 KB artifact budgets bind in-flight STORY docs only — not _main/ initiative plans, not reference docs; don't invent size gates elsewhere."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 188cc8d4-fd46-4a29-ada3-f8934ab750ee
  modified: 2026-08-04T01:56:16.743Z
---

The HARD budgets in `.agents/rules/artifacts-always-first.md:40` — `implementation_plan.md` ≤ 8 KB,
`walkthrough.md` ≤ 10 KB — bind the **two living docs of an in-flight story**. They are NOT a house
style for every document. Daniel, 2026-08-03: *"that 8 is not a hard rule for everything."*

The tooling agrees and is the tiebreaker: the workflow-enforcement gate's own test case reads
`F7 _main/ initiative plans are out of scope`, and a CLOSED story's over-budget doc is counted as
history rather than warned. So `_artifacts/_main/` work, reference docs, and quick-reference docs are
all outside it.

**Why:** the budget exists because those two files are *living* — the audit appends into the plan and
the review appends into the walkthrough, so 8 KB has to cover both. That rationale doesn't transfer to
a doc nothing appends to.

**How to apply:** enforce the cap on story `implementation_plan.md` / `walkthrough.md`; treat
`_main/` plans as advisory. Never invent a byte gate for a doc the rules don't cover — I did that to an
AGY quick-reference doc, then reported "missed my own size gate" on a target that was never real.
Compressing a 38-command catalog to satisfy a self-imposed number makes the doc worse.

Related: [[story-artifacts-two-doc-close]] · [[active-context-pointer-budget]] ·
[[workflow-enforcement-scripts]]
