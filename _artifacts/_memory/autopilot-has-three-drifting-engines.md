---
name: autopilot-has-three-drifting-engines
description: Autopilot has THREE engine implementations that drift; a behavior fix must land in all three or artifacts/logic diverge per-launch-path.
metadata: 
  node_type: memory
  type: project
  originSessionId: 8e12878a-edee-4d32-a3c7-a19bacf03bf9
  modified: 2026-08-03T00:37:49.445Z
---

**UPDATE 2026-08-07 (SCC-31): now TWO engines.** `/autopilot_mobile` and its `workflow.js` were deleted
(operator ruling) — mobile drives the desktop via Remote Control, so the desktop engines are the only
autopilots. A fix must land in the remaining two. Original note:

Autopilot runs through one of **three** engine implementations, each launched by a different command, each a
hand-maintained copy that drifts:
- `scripts/autopilot-dev-story.ps1` — **claude** engine (`/autopilot_claude`).
- `scripts/autopilot-dev-story-opencode.ps1` — **opencode** engine (`/autopilot_opencode`).
- `scripts/autopilot_mobile.workflow.js` + `/autopilot_mobile.md` — **mobile/Workflow** engine (the `.js`
  trusts the `folder` the command computes; the folder logic lives in the command, not the script).

**Why:** on 2026-07-03 story 11-18's opencode run dropped its folder at the `_artifacts/` root — the opencode
engine had been forked from a *pre-fix* claude engine and never got the `epic_<E>/` nesting block the claude
engine already had. Same class as [[autopilot-mobile-mirrors-claude]] and [[autopilot-engine-is-project-local]].

**How to apply:** when you change autopilot *behavior* (folder placement, gate, flip, effort), fix it in ALL
THREE paths (claude .ps1, opencode .ps1, mobile command) and dry-run each — don't assume `/autopilot_claude`
being correct means `/autopilot_opencode` is. The `.ps1` engines are project-local (not synced), so edit each
project's copy (AGY + Fresh) directly; the commands ARE synced via `/sync-agents`. Story placement itself is
governed by [[artifacts-always-first]] → `_artifacts/epic_<E>/<story>/` (TEA stories → `tea/` bucket).

**2026-08-02 update — FOUR launchers, still three engines.** `/autopilot_deepseek4` exists now, but it is a
LANE, not a fourth engine: its own header says "the orchestrator is the *same* `scripts/autopilot-dev-story.ps1`;
the only difference is the `-Deepseek4` flag" (Dev stages 1+3 on DeepSeek V4 Pro via OpenRouter, QA stays
Claude — Opus audit, Fable review, board at xhigh). So an engine fix in claude's ps1 reaches deepseek4 for
free; do NOT hunt for a deepseek engine copy. Stage-content propagation is a different axis: claude +
opencode + deepseek4 all invoke the `sudo-*_AP` stage commands (one twin patch covers all three lanes), while
**mobile inlines its own copy of the stage content in its Workflow prompts** — port stage-content changes
there explicitly ([[autopilot-mobile-mirrors-claude]]).
