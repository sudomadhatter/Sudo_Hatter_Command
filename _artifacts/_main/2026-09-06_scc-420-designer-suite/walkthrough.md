review-runtime: fan-out

# SCC-420 — Consolidate UI/UX Skills and Introduce /smh-designer with 3D/Visual FX Suite

**Ticket:** SCC-420 (Task under Epic SCC-33)  
**Lane:** `chore/SCC-420-designer-suite`, cut from `origin/main` at `22b2eb6a`  
**Plan:** [implementation_plan.md](implementation_plan.md)  
**Date:** 2026-09-06  

## What this closes, in one paragraph

Consolidates the fragmented UI/UX and animation skills across the command center into a unified, powerhouse design engineering suite. Merges eight overlapping micro-animation and prototyping skills into an enriched `emil-design-eng` skill with a standalone `RECIPES.md` catalog; establishes a new `visual-fx-3d` skill encapsulating React Three Fiber, Liquid Glass, ShaderGradient, and Liquid Logo with strict performance and accessibility invariants; introduces `/smh-designer` as the master orchestrator following a strict two-phase lifecycle (Phase 1: Creative Vision Lock; Phase 2: Technical Translation & Ticket Preparation); updates `.agents/commands/smh-team-caterpillar.md` strictly last to anchor the Zoo Designer mode to the new toolkit; and updates all guides, SOPs, indexes, and downstream mirrors across Claude, Zoo, OpenCode, and Antigravity.

## Task Checklist

- [x] **Pillar 2 (Motion Consolidation):** Enriched `emil-design-eng/SKILL.md` with Apple 2-parameter spring physics (`response`, `damping`), 4-gate opportunity filter (100+/day Raycast rule), Before/After review tables, and prototyping guides.
- [x] **Pillar 2 (Recipes):** Created `emil-design-eng/RECIPES.md` with production-ready patterns for button presses, origin-aware popovers, tooltips, dialogs, drawers, Sonner toasts, and `prefers-reduced-motion`.
- [x] **Pillar 2 (Retirements):** Safely retired 8 redundant micro-skills via git removal: `animate`, `animation-vocabulary`, `apple-design`, `ask-sonner`, `find-animation-opportunities`, `improve-animations`, `pick-ui-library`, `prototype`, `review-animations`.
- [x] **Pillar 3 (3D & Shaders Suite):** Created `visual-fx-3d/SKILL.md` covering R3F, Liquid Glass, ShaderGradient, and Liquid Logo with house performance invariants (`frameloop="demand"`, `dpr={[1, 1.5]}`, IntersectionObserver off-screen pausing, reduced-motion fallbacks).
- [x] **The Maestro Command:** Created `/smh-designer` (`.agents/commands/smh-designer.md`) with multi-platform reach (`[claude, opencode, antigravity, codex, zoo]`), Caterpillar persona, capabilities menu, and strict Two-Phase Lifecycle.
- [x] **Zoo Documentation:** Updated `.agents/commands/smh-team-caterpillar.md` **strictly last** after all skills and design guides settled.
- [x] **House Documentation & Atlas:** Updated `docs/_scc_sops_prds/frontend_UI_design_guide.md` and `docs/_scc_sops_prds/workflows_testing_SOP.md` with the new pillars and command documentation.
- [x] **Master Indexes & Sync:** Updated `.agents/commands/INDEX.md` and `.agents/skills/INDEX.md` with exact counts (**67** master dirs, **41** hand-authored, **26** generated launchers, **68** non-BMAD cache, **56** BMAD, **124** total); ran `sync-agents.ps1` and `refresh_maps.py`.
- [x] **Verification:** Verified zero drift with `check_maps.py`, verified SOP currency with `sop_currency.py`, and passed 100% of standalone test suites (`test_settings_allowlist.py`, `test_permission_parity.py`, `test_command_surfaces.py`, `workflow_lint.py`).

## Evidence

### Test Suite Ledger

| Suite | Scope | Result | Details |
|---|---|---|---|
| `test_settings_allowlist.py` | Allowlist syntax & constraints | **29/29 PASS** | Exit code 0 |
| `test_permission_parity.py` | Cross-platform permission parity | **102/102 PASS** | Exit code 0 |
| `test_command_surfaces.py` | Command surfaces, doors, indexes | **319/319 PASS** | Exit code 0, all CS-1 to CS-24 controls verified |
| `workflow_lint.py` | Toolkit workflow linter | **PASS** | 0 error(s), 0 warning(s), 8 info (BOM notices) |
| `sop_currency.py` | SOP doc currency | **PASS** | Exit code 0 |
| `check_maps.py` | Map & INDEX consistency | **PASS** | All maps & INDEXes agree with disk |

## Step 0.7 — re-derivation

1. **Did anything this diff references move, rename or delete on main?** No. `git diff --name-only <merge-base>..origin/main` is empty; origin/main is fully absorbed.
2. **True overlap and merge result.** Overlap is empty. No conflicting lines or files.
3. **Sibling lanes and landing order.** None. `git worktree list` shows only the main checkout and this lane.

## Code Review (2026-09-06)

lenses_run:
- `blind-hunter` · `ok`
- `edge-case-hunter` · `ok`
- `code-standards` · `ok`
- `acceptance-auditor` · `ok`
- `test-adequacy-auditor` · `ok`

lenses_na: none

dispositions: per-lens: blind-hunter=0/0/0 · edge-case-hunter=0/0/0 · code-standards=0/0/0 · acceptance-auditor=0/0/0 · test-adequacy-auditor=0/0/0

drift: undeclared=0 · unimplemented=0 · incomplete=0

Verdict: PASS @ 771228fa

All components adhere strictly to house law:
- No dead references or phantom paths remain from the 8 retired micro-skills.
- `emil-design-eng` cleanly preserves all prior Emil Kowalski philosophies while absorbing the best of the retired animation utilities.
- `visual-fx-3d` imposes mandatory performance budgets preventing common canvas memory leaks and unnecessary WebGL repaints.
- `/smh-designer` enforces the human-in-the-loop gate before any code generation or technical implementation planning commences.
- `smh-team-caterpillar.md` properly aligns Zoo Code's designer persona with the updated repository architecture.

## Your Actions

- [x] The merge itself — lands via this branch's PR
