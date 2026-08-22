---
name: bdd-vision-lock-rightsized
description: "2026-07-13 Epic 17 audit verdict: BDD Vision Lock conversation stays mandatory, standalone pytest-bdd demoted to opt-in (contract lives in the ATDD red files); ② got a mandatory self-audit STOP gate (model choice / fresh team / continue) — deliberately NOT in the _AP twin"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8910f437-c6ca-4c09-90b8-225de2fcf084
---

**Epic 17 BDD audit (2026-07-13) verdict + workflow change, synced to all surfaces same day:**

- The Vision Lock **conversation** proved its value (17.7 caught a stale story premise + 2 live defects;
  17.8 caught dataset drift); the standalone **pytest-bdd layer** did not (3 stories closed "no changes —
  correct as-is"; its own harness-bug class per [[bdd-sync-step-needs-asyncio-run]]; 17.7 shipped a
  `bdd: locked` with all contract files deleted — the phantom-contract lesson).
- **New default:** locked scenarios are codified INTO the story's ATDD red test file(s) (BDD-structured
  pytest / describe-it); standalone `.feature` + steps is **opt-in only**, chosen by the human at the lock.
  ②'s gate fails a `locked` record whose cited files are missing from disk.
- **New ② Step 2 = mandatory self-audit STOP gate:** after the plan is written, STOP and ask — (a) run
  /sudo-self-audit here (human may name a model, e.g. Fable for easy stories → subagent model override),
  (b) human takes implementation_plan.md to a fresh team and the flow waits, (c) "continue" resumes the
  remainder (2.5→3→4→5). Explicit skip → stub self-audit-stress-test.md recording the human decision.

**Why:** BDD time cost wasn't earning its keep as a mandatory artifact; the stop gate exists so the human
controls the audit lane/model per story.

**How to apply:** do NOT add the stop gate to `sudo-dev-story-tests_AP` — headless lanes can't stop; the
autopilot orchestrator owns per-stage model choice ([[autopilot-glm-hybrid-lane]]). Its BDD gate wording
was updated for parity (ATDD-file contracts default, `.feature` opt-in). Pre-Epic-18 stories carrying
`.feature` contracts stay valid (gate accepts both forms). Synced 2026-07-13 via /sync-agents to lobby,
opencode + antigravity globals, AGY_AVIATIONCHAT, Fresh_Workspace_BMAD.
Related: [[sudo-commands-have-ap-twins-that-drift]], [[red-file-hosts-expansion-tests]].
