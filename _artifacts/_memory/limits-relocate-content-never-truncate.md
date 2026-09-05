---
name: limits-relocate-content-never-truncate
description: "The 8/10 KB artifact caps were REMOVED 2026-08-08 (SCC-51). A limit is legitimate only when going over it means content is in the wrong file; if the only lever is destroying substance, it is a defect."
metadata:
  probe: "test -e .agents/rules/artifacts-always-first.md"
  node_type: memory
  type: feedback
  originSessionId: f3e01c24-9b74-4562-ba18-4cc66697fffd
  modified: 2026-08-08T00:00:00.000Z
---

**The caps are GONE.** `implementation_plan.md` ≤ 8 KB and `walkthrough.md` ≤ 10 KB were set 2026-08-02
and **removed 2026-08-08 (SCC-51, operator ruling)** — from the rule, both BMAD tomls, the commands, the
opencode mirror, and `workflow_lint.py` (`_BUDGETS` + `check_artifact_budgets()` deleted; two guard tests
now FAIL if a byte threshold returns). Do not re-apply them, and do not "compress to fit" — there is no
number to fit.

**The test that separates a good limit from a bad one:**

- **Legitimate** — going over means *the wrong content is in this file*. The fix MOVES or DELETES content
  that belongs elsewhere. Nothing is lost.
- **Harmful** — going over means *you found more than expected*. The rule forbids a second file, so the
  only lever left is destroying substance — and the substance is findings, ACs, evidence.

The plan cap failed that test structurally: it shipped in the same commit that made
`implementation_plan.md` a **two-author** doc (the dev writes it, `/sudo-self-audit` appends §7 into it).
A fixed cap on a two-author doc squeezes the second author — the auditor, the one voice you least want
truncated. It was never validated against a real audit, and the first Full audit under it compressed its
own findings to fit.

**Why (Daniel, 2026-08-08):** *"there can not be hard limits… I see it as a huuuuge threat to qualtiy."*
And on the same breath, the boundary: *"make sure you dont take out all the stuff. some stuff needs limits."*

**How to apply:**
- **KEPT, deliberately** — `active-context.md` ≤ 20 KB, the board note budget + board size cap, autopilot
  `-MaxCost`, quick-dev's soft 900–1600-token spec range. All pass the test: over means stale state to
  delete or work to hand off, never a finding to lose. Also kept: **never split into a second file** —
  that is a structure rule, not a size rule.
- **The standard that replaced the cap** lives in `.agents/rules/artifacts-always-first.md` — *dense, not
  short*: every line carries a decision, a constraint, a finding, or evidence; cut restatement and filler.
  **Length is never a reason to omit a finding, an AC, or a piece of evidence.**
- When a doc feels bloated, remove what does not inform a decision — never truncate what does.
- Do not invent a byte gate for a doc the rules don't cover. The older mistake this memory used to record
  still stands: I once imposed a self-made size gate on an AGY quick-reference catalog and reported
  "missed my own size gate" against a target that never existed.

Related: [[story-artifacts-two-doc-close]] · [[active-context-pointer-budget]] ·
[[workflow-enforcement-scripts]] · [[settled-decisions-are-not-gaps]]
