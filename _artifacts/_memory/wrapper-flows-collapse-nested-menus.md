---
name: wrapper-flows-collapse-nested-menus
description: "In sudo-* orchestrated flows, never surface nested BMAD step-menus one-by-one — auto-continue them; human checkpoints ONLY at real decisions. Daniel called the menu-churn run \"painful\"."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 14571419-b1d2-4334-908f-ce5f376c7fd6
  modified: 2026-07-19T17:39:59.384Z
---

Running `/sudo-write-epics-stories-sprint` on 2026-07-19 (Epic 19), I surfaced every nested BMAD step-file
menu ([C] after requirements, epic design, stories, validation) as a full turn-stop, then launched
`bmad-sprint-planning` with its whole activation preamble. Daniel interrupted: "no i dont use bmad solo?",
"that was painful, and didnt flow or follow the way I work. this has never happened before."

**Why:** The sudo-* wrappers are thin orchestrators over BMAD skills. The BMAD step-menus exist for
STANDALONE greenfield use; inside an orchestration whose input is an already-approved source, they are pure
ceremony. Daniel's flow = one continuous pass with checkpoints ONLY where HE decides something (consolidated
content review; per-story risk-scoring chips). Five stalls where two belong reads as the agent "struggling."

**How to apply:** When a sudo-* command invokes nested BMAD skills over an approved requirements source,
auto-continue the skills' internal menus and present exactly the wrapper's designed checkpoints. Fixed
structurally 2026-07-19 in `sudo-write-epics-stories-sprint.md` ("FLOW CONTRACT" block: two human
checkpoints; Step 2 status-word bug `ready-for-dev`→`backlog` also fixed) — master + AGY + Fresh copies.
If another sudo-* wrapper shows the same nested-menu churn, apply the same contract and bake it into that
command body too ([[restate-alwayson-obligations-in-command-bodies]]). Real gaps (missing source,
contradictory scope) still surface and STOP — collapse ceremony, never judgment.
