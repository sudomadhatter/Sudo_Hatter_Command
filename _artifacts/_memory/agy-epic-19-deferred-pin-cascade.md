---
name: agy-epic-19-deferred-pin-cascade
description: "Epic 19 (adk 2.5.0/genai 2.12.1 upgrade) DEFERRED wholesale 2026-07-20 — adk 2.5.0 is a 4-family bump (fastapi≥0.133→starlette 1.x MAJOR, OTel 1.39–1.42.1, google-auth≥2.48.1), not two pins. AGY stays on adk 1.26.0/genai 1.64.0; deferral is AGY-only (brownfield) — Fresh/greenfield keeps the 2.5 era. 19.1 reds quarantined, never run ② on it."
metadata: 
  node_type: memory
  type: project
  originSessionId: d835c3ce-e2c6-4c32-b50c-20d47c58f588
  modified: 2026-07-21T04:00:04.470Z
---

**Epic 19 (AGY runtime upgrade to google-adk 2.5.0 + google-genai 2.12.1) is DEFERRED WHOLESALE**
(operator, 2026-07-20, discovered at ② Task 1 of story 19.1): pip is ResolutionImpossible with only the
two pins bumped — adk 2.5.0 forces `fastapi>=0.133` (→ **starlette 0.52.1 → 1.3.1 MAJOR**, under every
router) and `opentelemetry-api>=1.39,<=1.42.1` (whole OTel family 0.59b0 → 0.63b1); genai 2.12.1 forces
`google-auth>=2.48.1`. Resolver-proven landing set is in the 19.1 walkthrough. Operator: "we don't need
to change or upgrade ADK and this is too much."

**Scope:** AviationChat-only — brownfield exact-pin lattice is what makes the cascade costly. The
2.5-era runtime **remains the greenfield default**: Fresh_Workspace_BMAD keeps it (floors admit 2.5.x,
zero adk/genai call sites) and the old "propagate 19.1 pins to Fresh" follow-up is RETIRED.

**Standing state in AGY:** runtime stays adk 1.26.0 / genai 1.64.0. The ① red contract
`backend/tests/agents/test_story_19_1_runtime_pins_explicit_key_auth.py` is QUARANTINED — 5 reds carry
the `EPIC_19_DEFERRED` skip mark; the 2 tripwires (PINS-003 import surface, EVAL-001) stay live pinning
1.26.0 behavior. Board rows 19-1..19-4 + retro = `deferred`; story `Status: deferred`.

**How to apply:** never recommend running ② on 19.1 or picking up 19.x — the dependency map's Lane A is
deliberately empty. Known side-fact from the halt: greeting auth today is bare-Client env pickup (the
`api_key=` kwarg at `greeting/agent.py:26` is a silent no-op at 1.26.0) — an accepted, recorded state
while the epic sleeps. Revival = re-scope as a coordinated 4-family bump FIRST, then unskip the reds.
Related: [[fresh-workspace-living-template]], [[agy-story-files-canonical-dir]],
[[dev-flow-model-switch-stops]].
