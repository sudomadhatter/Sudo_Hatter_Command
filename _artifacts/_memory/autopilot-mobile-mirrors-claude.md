---
name: autopilot-mobile-mirrors-claude
description: "/autopilot_mobile is the Workflow-engine port of /autopilot_claude and drifts from it; claude's .ps1 is canonical — re-mirror mobile whenever claude changes."
metadata: 
  node_type: memory
  type: project
  originSessionId: a79df282-acd0-49ff-9d8f-339b9e1067c9
---

**⛔ RETIRED 2026-08-07 (SCC-31, operator ruling).** `/autopilot_mobile` and its `workflow.js` engine are
DELETED from every surface; the manifest ghost-purge clears the platform caches. Mobile drives the desktop
via Remote Control, which runs the real engines with the full local filesystem. Do not re-create it, and do
not mirror claude's engine into a mobile twin. Kept as history:

`/autopilot_mobile` is the web/cloud port of `/autopilot_claude` — same 4-stage Dev/QA pipeline, but on the **Workflow engine** (`Projects/<proj>/scripts/autopilot_mobile.workflow.js`, project-local, NOT synced) instead of PowerShell. The two are a drift-prone twin pair like the [[sudo-commands-have-ap-twins-that-drift]] `_AP` pairs.

**Canonical config lives in claude's `autopilot-dev-story.ps1`, not the command doc** (the `.md` abstracts it). When claude changes, re-mirror mobile.

**Why:** They were last reconciled 2026-07-03 — mobile had drifted (uniform `high` effort, no regression gate, no review-flip, no Close-Out Handoff).

**How to apply:** Mobile now mirrors claude's per-stage **effort ladder** (Stage1 Plan opus=max, Stage2 Audit fable=high, Stage3 Implement opus=max, Stage4 Review+Fix fable=xhigh — set in `workflow.js` STAGES), the **regression-only test gate** (baseline red snapshot cached at `<folder>/_pipeline/baseline-red.txt` before Stage 3, gate fails only on NEW ids — lives in the command `.md` step 5a/6, since the JS sandbox has no fs), the **auto-flip to `review`** on a green gate, and the **`## Close-Out Handoff`** block in Stage 4's prompt. The one thing that does NOT map: claude's `-MaxStageCost` per-stage USD cap (Workflow has no per-stage dollar budget — documented as intentional divergence). Command doc = master `.agents/commands/autopilot_mobile.md` (edit master + `/sync-agents`); the `workflow.js` engine is edited per-project ([[autopilot-engine-is-project-local]]).
