# Implementation Plan: VGPU Toolbelt Integration & 3D Stack Streamlining (SCC-186)

Integrate Vercel Labs' WebGPU library ([`vercel-labs/vgpu`](https://github.com/vercel-labs/vgpu)) into the command center UI toolbelt under standing ticket [SCC-186](https://sudo-command.atlassian.net/browse/SCC-186). Streamline the 3D stack by specializing [`.agents/skills/visual-fx-3d/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md) on spatial 3D models and optical glass, while migrating ambient fluid/plasma shaders to `vgpu` with a mandatory mobile fallback.

---

## User Review Required

> [!IMPORTANT]
> **Architectural Separation of Concerns:**
> 1. **`vgpu`**: Owns all 2D/compute shaders, fullscreen fluid meshes, plasma noise, and particle visualizers (~25KB gzipped, typed WGSL, zero-GPU headless CI testable).
> 2. **`visual-fx-3d`**: Retained and specialized for declarative 3D scene graphs, glTF/GLB product models, camera rigs (`pmndrs/react-three-fiber`), and optical glass refraction (`dashersw/liquid-glass-js`).
> 3. **Mobile Safety Invariant**: WebGPU is not supported on older devices (iOS $\le 17$, older Android, default Linux Firefox). All `vgpu` components MUST guard on `navigator.gpu` and gracefully fall back to CSS gradients or SVG canvas to prevent blank rectangles on mobile viewports.

---

## Proposed Changes

 Group files by component and order logically.

### 1. Master Toolkit Skills (`.agents/skills/`)

#### [NEW] [`.agents/skills/vgpu/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/vgpu/SKILL.md)
- Complete master skill defining `vgpu` integration:
  - Architecture: single `Gpu` context, typed WGSL modules, fullscreen render passes, compute pipeline.
  - Performance: ~25KB bundle vs ~250KB Three.js/ShaderGradient.
  - Headless CI & Testing: `@vgpu/adapter-mock` for zero-hardware deterministic tests, `@vgpu/adapter-node` (Dawn) for server-side execution.
  - Mobile Safety Invariant: `navigator.gpu` detection with CSS/SVG graceful degradation.
  - Component recipes: Fullscreen Fluid Ambient Mesh, Audio/Interaction Reactive Plasma, Particle Simulation.

#### [MODIFY] [`.agents/skills/visual-fx-3d/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md)
- Prune obsolete and bloated `ShaderGradient` and standalone canvas shader hacks.
- Specialize on declarative 3D scene graphs, glTF/GLB models, spatial lighting (`pmndrs/react-three-fiber` + `@react-three/drei`), and VisionOS optical glass refraction (`dashersw/liquid-glass-js`).
- Cross-reference `vgpu` for 2D/ambient shader meshes.

#### [MODIFY] [`.agents/skills/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/INDEX.md)
- Register `vgpu` in the master skill index with trigger, platform, and load classification.

---

### 2. Designer Command & SOP Documentation

#### [MODIFY] [`.agents/commands/smh-designer.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-designer.md)
- Update Pillar 3: **3D, Shaders & Physical Materials** to feature both `vgpu` (next-gen WebGPU shaders) and `visual-fx-3d` (R3F spatial scenes & Liquid Glass).
- Update the Capabilities Menu table:
  - Add/update `[WG]` WebGPU Shaders (`vgpu`) for ultra-lean ambient mesh & plasma backgrounds.
  - Refine `[3D]` for spatial product models, glTF scenes, and floating geometry cards (`visual-fx-3d`).
  - Retain `[LG]` Liquid Glass (`visual-fx-3d`).

#### [MODIFY] [`docs/_scc_sops_prds/frontend_UI_design_guide.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/frontend_UI_design_guide.md)
- Update Section 4: Architectural guidance distinguishing WebGPU shaders (`vgpu`) from 3D spatial models (`visual-fx-3d`).
- Update Section 7: Agent Skill Routing Matrix to include `vgpu`.
- Update Section 8: Pre-delivery checklist to verify `navigator.gpu` fallback handling.

---

### 3. Synchronization & Parity

#### [SYNC] Mirrors across platforms
- Run mirror synchronization to propagate `.agents/skills/vgpu` to `.claude/skills/`, `.opencode/`, etc.
- Verify platform parity and permissions.

---

## Verification Plan

### Automated Tests
1. Run master test suite:
   ```bash
   python3 .agents/scripts/tests/run_all.py
   ```
2. Verify maps & links:
   ```bash
   python3 .agents/scripts/check_maps.py
   python3 .agents/scripts/check_links.py
   ```
3. Verify skill frontmatter and index integrity:
   ```bash
   python3 -c "import scripts.tests.test_skills_index as t; t.run()" # or run via run_all.py
   ```

### Manual Verification
- Review generated `vgpu` skill documentation recipes for WGSL syntax accuracy, imports, and fallback logic.
- Verify that `/smh-designer` command triggers and capabilities menu clearly differentiate when to reach for `vgpu` vs `visual-fx-3d`.
