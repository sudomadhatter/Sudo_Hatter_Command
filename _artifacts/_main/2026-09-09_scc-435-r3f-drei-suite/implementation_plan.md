# Upgrade visual-fx-3d and /smh-designer with Full pmndrs (R3F + Drei) Suite

Upgrade Pillar 4 of the Caterpillar design system from a basic outline with hacky SVG filters to the production-grade **Poimandres (`pmndrs`)** ecosystem: [`@react-three/fiber`](https://github.com/pmndrs/react-three-fiber) and [`@react-three/drei`](https://github.com/pmndrs/drei).

## User Review Required

> [!IMPORTANT]
> **Subbing out `liquid-glass-js` for `MeshTransmissionMaterial`:**
> The previous `visual-fx-3d` design relied on an SVG displacement filter hack (`feDisplacementMap` + `feTurbulence`) for "Liquid Glass". We are substituting this with Drei's `MeshTransmissionMaterial`, which provides true physical optical refraction, chromatic dispersion, roughness, and light transmission in 3D WebGL space at 60fps.
>
> **Bundle and Battery Boundaries:**
> We maintain the strict boundary established with `vgpu`:
> - 2D fullscreen fluid meshes & ambient shaders: remain in [`vgpu`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/vgpu/SKILL.md) (~25KB, typed WGSL).
> - 3D spatial models, interactive tilt cards, and physical transmission glass: belong in [`visual-fx-3d`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md) with mandatory `frameloop="demand"` and `dpr={[1, 1.5]}`.

## Proposed Changes

### Worktree & Branch Isolation
- Work will take place in an isolated worktree at `.claude/worktrees/scc-435-r3f-drei-suite` on branch `chore/SCC-435-r3f-drei-suite` cut from `main`.

---

### Pillar 4 Master Skill: `visual-fx-3d`

#### [MODIFY] [visual-fx-3d/SKILL.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md)
- Replace basic octahedron and SVG filter hacks with full production `pmndrs` architecture:
  1. **Core Ecosystem Stack:** `three`, `@react-three/fiber`, `@react-three/drei`, `@types/three`.
  2. **The `gltfjsx` Pipeline:** Standard procedure to compile `.glb` / `.gltf` 3D product models into declarative, typed JSX components.
  3. **Component Recipe 1: Tactile 3D Spring Tilt Card (`PresentationControls` + `Float` + `ContactShadows`):** Responsive touch/mouse tilt with spring physics matching our Emil Kowalski motion doctrine.
  4. **Component Recipe 2: Physical Optical Glass Refraction (`MeshTransmissionMaterial`):** Real Apple VisionOS-grade physical transmission with chromatic aberration, roughness, thickness, and anisotropy.
  5. **Component Recipe 3: 3D Spatial DOM Pinning (`<Html>`):** Pinning responsive React DOM badges/buttons directly to 3D mesh coordinates.
  6. **On-Demand Performance & Battery Invariants:**
     - `frameloop="demand"` + explicit `invalidate()` event triggers.
     - `dpr={[1, 1.5]}` pixel ratio clamping.
     - WebGL context disposal / cleanup on unmount to prevent browser memory leaks.
     - `IntersectionObserver` pause on scroll out of viewport.

---

### Command & Persona: `/smh-designer` & Caterpillar

#### [MODIFY] [smh-designer.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-designer.md)
- Update Pillar 4 description and Capabilities Menu:
  - `[3D]`: 3D Spatial UI (React Three Fiber, Drei spatial models, `gltfjsx` assets, spring tilt cards).
  - `[LG]`: Physical Transmission Glass (`MeshTransmissionMaterial` optical refraction and chromatic aberration).
- Align persona guidance to recommend R3F declarative components for spatial UI.

#### [MODIFY] [smh-team-caterpillar.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-team-caterpillar.md)
- Update Zoo Caterpillar designer mode summary to reflect `visual-fx-3d` (React Three Fiber, Drei, MeshTransmissionMaterial) instead of retired legacy placeholders.

---

### House Documentation & SOPs

#### [MODIFY] [frontend_UI_design_guide.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/frontend_UI_design_guide.md)
- Update Section 4.B and Section 7 table:
  - Document R3F + Drei as the official house 3D spatial engine.
  - Detail `gltfjsx` asset compilation and `MeshTransmissionMaterial` physical glass parameters.
  - Retain `vgpu` for 2D WGSL surface shaders.

#### [MODIFY] [workflows_testing_SOP.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
- Verify and update the `/smh-designer` entry if command syntax or capability codes are updated, satisfying `sop_currency.py`.

---

### Toolkit Synchronization & Mirrors

#### [RUN] `/smh-sync-agents` (`pwsh .agents/scripts/sync-agents.ps1`)
- Mirror changes from `.agents/skills/visual-fx-3d/` and `.agents/commands/smh-designer.md` to `.claude/`, `.opencode/`, etc.

## Verification Plan

### Automated Test Suites
Run the standard command center verification gates:
```bash
# 1. SOP currency check
python3 .agents/scripts/sop_currency.py --paths .agents/commands/smh-designer.md docs/_scc_sops_prds/workflows_testing_SOP.md

# 2. Command surface and index verification
pytest tests/test_command_surfaces.py
pytest tests/test_permission_parity.py
pytest tests/test_settings_allowlist.py

# 3. Maps and integrity check
python3 .agents/scripts/check_maps.py
```

### Manual Verification
- Review rendered recipes in `visual-fx-3d/SKILL.md` to confirm TypeScript syntax validity, prop correctness against `@react-three/drei` v9+, and strict adherence to `frameloop="demand"`.
