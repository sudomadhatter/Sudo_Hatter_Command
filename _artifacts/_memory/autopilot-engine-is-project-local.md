---
name: autopilot-engine-is-project-local
description: "The autopilot-dev-story.ps1 gate engine is maintained per-project (copies have diverged); sync-agents never propagates scripts/. The lobby (\"main\") holds only the spec doc."
metadata: 
  node_type: memory
  type: project
  originSessionId: 82caeb9d-cf7a-4ce4-8471-9efb9c2f6c9a
---

`scripts/autopilot-dev-story.ps1` (the headless Dev/QA story engine + independent test gate) lives **independently in each project**, never in the lobby. `sync-agents.ps1` only propagates `commands/ skills/ hooks/ opencode-agents/` — **never `scripts/`** — so the two copies have drifted: `AGY_AVIATIONCHAT` (~1191 lines, superset: baseline-red snapshot + flaky-confirm) vs `Fresh_Workspace_BMAD` (~817 lines, simpler gate). Confirmed 2026-07-03: Fresh_Workspace has `Invoke-TestGate` but **NO `Capture-BaselineRedSet`** — so it runs the backend suite **once** (gate only), while AGY runs it **twice** (pre-Stage-3 baseline snapshot + post-Stage-4 gate). Consequence: baseline-only optimizations apply to **AGY only**; there is nothing to trim in Fresh_Workspace's gate. The `auto` test-scope `default {}` block is byte-identical in both, so a gate patch must be applied to **each** project copy by hand.

The lobby (Sudo_Hatter_Command / "main") has **no** engine — git history confirms it was never tracked there. Its only autopilot artifact is the canonical spec doc `.agents/workflows/autopilot_bmad_dev_loop.md` (documents `-TestScope`, gate phases). So "fix the autopilot on main" = update that spec doc; the functional fix goes in the project engines. See also [[grep-skips-gitignored-projects]].

**Why:** "fix this on main, aviationchat, fresh-workspace" maps to: spec-doc edit in the lobby master + engine edit in each of the two project repos (`Projects/AGY_AVIATIONCHAT`, `Projects/Fresh_Workspace_BMAD`), both on `main_debug`.
**How to apply:** Edit `Projects/<proj>/scripts/autopilot-dev-story.ps1` in BOTH projects, then the lobby spec doc. Validate with `[System.Management.Automation.Language.Parser]::ParseFile`. Run `sync-agents.ps1` to refresh the doc's vendored project copies.
