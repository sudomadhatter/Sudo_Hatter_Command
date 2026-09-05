---
name: autopilot-engine-is-project-local
description: "The autopilot-dev-story.ps1 gate engine is maintained per-project (copies have diverged); sync-agents never propagates scripts/. The lobby (\"main\") holds only the spec doc."
metadata: 
  probe: "test -e docs/_scc_sops_prds/autopilot_bmad_dev_loop.md"
  node_type: memory
  type: project
  originSessionId: 82caeb9d-cf7a-4ce4-8471-9efb9c2f6c9a
---

`scripts/autopilot-dev-story.ps1` (the headless Dev/QA story engine + independent test gate) lives **independently in each project**, never in the lobby. `sync-agents.ps1` only propagates `commands/ skills/ hooks/ opencode-agents/` — **never `scripts/`** — so the copies drift.

**Engines and Launchers (SCC-31 / SCC-63):**
Autopilot runs through desktop engine implementations that each require per-project maintenance:
- `scripts/autopilot-dev-story.ps1` — **Claude** engine (`/autopilot_claude`, `/autopilot_deepseek4` lane — DeepSeek V4 Pro via OpenRouter is a lane using the same `.ps1` with `-Deepseek4`).
- `scripts/autopilot-dev-story-opencode.ps1` — **Opencode** engine (`/autopilot_opencode`).
- `/autopilot_mobile` and `workflow.js` were **retired 2026-08-07 (SCC-31)** — mobile drives the desktop via Remote Control, so desktop engines are the only autopilots.

**Count per project (re-counted 2026-08-09):** `AGY_AVIATIONCHAT` 1500 · `NEXgen-VR-Director` 1500 · `sudo-project-skeleton` 1500 · `BRKN_Tattoos` 1275. `Fresh_Workspace_BMAD` no longer carries one at all. Re-count before trusting any line number.
Confirmed 2026-07-03: Fresh_Workspace has `Invoke-TestGate` but **NO `Capture-BaselineRedSet`** — so it runs the backend suite **once** (gate only), while AGY runs it **twice** (pre-Stage-3 baseline snapshot + post-Stage-4 gate). Consequence: baseline-only optimizations apply to **AGY only**; there is nothing to trim in Fresh_Workspace's gate. The `auto` test-scope `default {}` block is byte-identical in both, so a gate patch must be applied to **each** project copy by hand.

The lobby (Sudo_Hatter_Command / "main") has **no** engine — git history confirms it was never tracked there. Its only autopilot artifact is the canonical spec doc `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` (documents `-TestScope`, gate phases). So "fix the autopilot on main" = update that spec doc; the functional fix goes in the project engines. See also [[grep-skips-gitignored-projects]].

**Why:** "fix this on main, aviationchat, fresh-workspace" maps to: spec-doc edit in the lobby master + engine edit in each of the project repos (`Projects/AGY_AVIATIONCHAT`, `Projects/Fresh_Workspace_BMAD`), each on that repo's integration base (the live epic branch, else a `chore/*` branch off `main`).
**How to apply:** When you change autopilot behavior (folder placement, gate, flip, effort), fix it in both desktop engine paths (`scripts/autopilot-dev-story.ps1` and `scripts/autopilot-dev-story-opencode.ps1`) in the project repos, then the lobby spec doc. Validate with `[System.Management.Automation.Language.Parser]::ParseFile`. Run `sync-agents.ps1` to refresh the doc's vendored project copies. Story placement is governed by `.agents/rules/artifacts-always-first.md` → `_artifacts/epic_<E>/<story>/`.
