---
name: story-artifacts-two-doc-close
description: "Since 2026-08-02 a story closes with TWO living docs — plan (+## Self-Audit) and walkthrough (+## Code Review with the Verdict line close-out greps); standalone audit/review files are retired, TEA files kept."
metadata: 
  probe: "test -e _artifacts/AGENTS.md"
  node_type: memory
  type: project
  originSessionId: 38c898a4-0e4e-4347-b130-b313acf7f0ec
  modified: 2026-08-03T18:17:37.535Z
---

**The two-doc close (ruled 2026-08-02, all four repos).** A story/session ends with exactly two living
docs in its `_artifacts/` folder: `implementation_plan.md` — `/sudo-self-audit` APPENDS
`## Self-Audit (<date>)` into it (canonical line `Audit verdict: GO | NO-GO`) — and `walkthrough.md`,
outline-first (`## Task Checklist` outline with pitfalls indented under tasks that fought back →
`## Evidence` (ONE AC matrix + latest totals + SHA, re-runs REPLACE) → `## Suite Ledger` →
`## Code Review (<date>)` appended by ③ with FIRST line `Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>` →
`## Your Actions`). **No byte cap** — dense, not short (the 8/10 KB caps were removed 2026-08-08,
SCC-51; see [[limits-relocate-content-never-truncate]]).

**Why:** story 8.23.2 audit showed ~57 KB written per story with findings ×3, AC matrix ×4, test pastes
×6 across `self-audit-stress-test.md` / `sudo-code-review-<story>.md` / walkthrough — ~50-55% of it
duplicate. Cost: every downstream step re-read 4-5 docs.

**How to apply:**
- Close-out's done-flip and both merge flows grep the walkthrough's `Verdict:` line; stories closed
  BEFORE 2026-08-02 keep standalone files — fall back to
  `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`, never write a new one.
- Autopilot stage-completeness is section-based now: stage 2 = `Audit verdict:` in the plan, stage 4 =
  `## Code Review` in the walkthrough (`Test-DocSection` in all 6 project `.ps1` engines — patched via
  one git patch, AGY canonical; Fresh/NEXgen are byte-identical twins).
- TEA test-artifacts (`atdd-checklist-*`, `automation-summary-*`, `certification-*.json`) stay
  standalone BY RULING — don't re-propose folding them.
- Propagated: lobby masters + [[sudo-commands-have-ap-twins-that-drift]] `_AP` twins +
  [[autopilot-engine-is-project-local]] desktop engines + AGY/Fresh/NEXgen rules, TOMLs,
  reference, `_artifacts/AGENTS.md`, via hand-copy (rules) + `/sync-agents` (commands).
