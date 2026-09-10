# SCC-435 — Upgrade visual-fx-3d and /smh-designer with Full React Three Fiber and Drei Suite

**Ticket:** SCC-435 (Task under Epic SCC-33)  
**Lane:** `chore/SCC-435-r3f-drei-suite`, cut from `main` at `3641749a`  
**Plan:** [implementation_plan.md](implementation_plan.md)  
**Date:** 2026-09-09  

## What this closes, in one paragraph

Upgrades Pillar 4 of Caterpillar's design engineering system from a basic outline with hacky SVG filters to the production-grade **Poimandres (`pmndrs`)** ecosystem: [`@react-three/fiber`](https://github.com/pmndrs/react-three-fiber) and [`@react-three/drei`](https://github.com/pmndrs/drei). Replaces the synthetic 2D SVG displacement filter hack (`liquid-glass-js`) with Drei's battle-tested `MeshTransmissionMaterial` for authentic Apple VisionOS-grade physical optical glass refraction with chromatic edge dispersion and roughness in 3D WebGL space. Adds production component recipes for tactile 3D Spring Tilt Cards (`<PresentationControls>` with Apple 2-parameter spring physics), glTF asset compilation via `gltfjsx`, and DOM-in-3D pinning (`<Html>`). Enforces non-negotiable performance invariants (`frameloop="demand"`, `dpr={[1, 1.5]}`, off-screen pause via `IntersectionObserver`, and WebGL resource cleanup). Synchronizes changes across `/smh-designer`, Zoo's `smh-team-caterpillar`, the house `frontend_UI_design_guide.md`, and operator SOPs via `/smh-sync-agents`.

## Task Checklist

- [x] **Pillar 4 Core Engine (`visual-fx-3d/SKILL.md`):** Replaced placeholder octahedron and SVG filter with full Poimandres suite (`three`, `@react-three/fiber`, `@react-three/drei`, `gltfjsx`).
- [x] **Asset Compilation Pipeline:** Documented standard `npx gltfjsx` workflow to compile `.glb`/`.gltf` 3D product models into modular, typed React components with Draco compression.
- [x] **Component Recipe 1 (Spring Tilt Card):** Built tactile card pattern with `@react-three/drei`'s `<PresentationControls>`, `<Float>`, and `<ContactShadows>` adhering to Apple spring physics.
- [x] **Component Recipe 2 (Physical Glass):** Implemented `MeshTransmissionMaterial` recipe with physical refraction (`ior`), light transmission, chromatic aberration, roughness, and anisotropy.
- [x] **Component Recipe 3 (3D DOM Pinning):** Added `<Html>` recipe for pinning reactive React badges/tooltips directly to 3D mesh coordinates.
- [x] **Performance Invariants:** Codified `frameloop="demand"`, `dpr={[1, 1.5]}`, `touch-none`, viewport pausing via `IntersectionObserver`, and resource disposal.
- [x] **Master Command (`/smh-designer`):** Updated Pillar 4 definition and Capabilities Menu (`[3D]` and `[LG]`) to reflect R3F, Drei, and physical transmission glass.
- [x] **Zoo Mode (`smh-team-caterpillar.md`):** Aligned Caterpillar designer persona to the updated 3D suite.
- [x] **Documentation & SOPs:** Updated `docs/_scc_sops_prds/frontend_UI_design_guide.md` and `docs/_scc_sops_prds/workflows_testing_SOP.md`.
- [x] **Mirror Sync:** Propagated changes to `.claude/skills/visual-fx-3d/`, `.opencode/commands/smh-designer.md`, and `.agents/.sync-manifest.json` via `sync-agents.ps1`.
- [x] **Verification & Linting:** Passed `sop_currency.py`, `test_command_surfaces.py` (343/343), `test_permission_parity.py` (102/102), `test_settings_allowlist.py` (28/28), and `check_maps.py`.

## Evidence

### Test Suite Ledger

| Suite | Scope | Result | Details |
|---|---|---|---|
| `sop_currency.py` | SOP currency gate | **PASS** | Exit code 0 |
| `test_command_surfaces.py` | Command surfaces & CS-25 design invariants | **343/343 PASS** | Exit code 0 |
| `test_permission_parity.py` | Cross-platform permission parity | **102/102 PASS** | Exit code 0 |
| `test_settings_allowlist.py` | Allowlist syntax & invariants | **28/28 PASS** | Exit code 0 |
| `check_maps.py` | Map & INDEX consistency | **PASS** | All maps & INDEXes agree with disk |

## Step 0.7 — re-derivation

1. **Did anything this diff references move, rename or delete on main?** No. `git diff --name-only main...HEAD` shows only targeted design skill and documentation files.
2. **True overlap and merge result.** Overlap is empty. No conflicting lines or files.
3. **Sibling lanes and landing order.** Only `chore/SCC-431-zoo-remote` exists in parallel; zero overlapping file paths.

## Code Review (2026-09-09)

lenses_run:
- `blind-hunter` · `ok`
- `edge-case-hunter` · `ok`
- `code-standards` · `ok`
- `acceptance-auditor` · `ok`
- `test-adequacy-auditor` · `ok`

lenses_na: none

dispositions: per-lens: blind-hunter=0/0/0 · edge-case-hunter=0/0/0 · code-standards=0/0/0 · acceptance-auditor=0/0/0 · test-adequacy-auditor=0/0/0

drift: undeclared=0 · unimplemented=0 · incomplete=0

Verdict: PASS @ HEAD

## Your Actions

None. The PR is merged, all tests passed, and the R3F/Drei design engine is live.
