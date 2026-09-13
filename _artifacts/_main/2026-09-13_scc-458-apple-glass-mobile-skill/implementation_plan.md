# Implementation Plan — Mobile-First Apple Glass Master Skill (SCC-458)

Retires desktop-bound glass hacks (`dashersw/liquid-glass-js` with `html2canvas` snapshotting, and Three.js `MeshTransmissionMaterial` in `visual-fx-3d`) and replaces them with a dedicated, mobile-first master skill: [`.agents/skills/apple-glass/SKILL.md`](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/apple-glass/SKILL.md). When Mr. Hatter asks for "frosted glass" or "apple glass", any agent will execute the exact, hardware-accelerated recipe tailored for mobile devices. Upon completion, this mobile-first architecture will also be published to the public [`sudomadhatter/design-engineer-skills`](https://github.com/sudomadhatter/design-engineer-skills) repository.

## User Review Required

> [!IMPORTANT]
> **Retiring 3D WebGL Canvas for 2D UI Glass:**
> We are explicitly deprecating Three.js `MeshTransmissionMaterial` for standard UI controls (buttons, cards, navigation bars). It will remain in [`visual-fx-3d`](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md) strictly for true 3D spatial models and GLTF product renders.
>
> **The Two-Tier Mobile Architecture:**
> 1. **Tier 1 (Apple HIG Frosted Glass — 95% of UI):** Hardware-composited CSS `backdrop-filter: blur(20px) saturate(180%)`, sub-pixel specular borders, and top sheen gradients. Zero JS overhead, locked 120fps on iPhone ProMotion / 60fps on Android.
> 2. **Tier 2 (Apple Liquid Glass — Optical Refraction):** Headless live-DOM SDF displacement via [`samasante/liquid-glass`](https://github.com/samasante/liquid-glass) for floating action buttons, Dynamic Island pills, and interactive sliders. Zero dependencies, no canvas screenshotting, and hardened for WebKit/iOS Safari memory constraints.
> 3. **Tier 3 (Native Mobile):** Documented bridges for React Native ([`@callstack/liquid-glass`](https://github.com/callstack/liquid-glass)) and native SwiftUI iOS 26 (`.glassEffect`).
>
> **Exporting to Standalone Repo:**
> Once verified locally in `Sudo_Hatter_Command`, we will mirror `apple-glass`, the updated `/smh-designer`, and `docs/frontend_UI_design_guide.md` into [`sudomadhatter/design-engineer-skills`](https://github.com/sudomadhatter/design-engineer-skills), run its `verify.py`, and push.

## Proposed Changes

Work is isolated in worktree `.claude/worktrees/scc-458-apple-glass-mobile-skill` on branch `chore/SCC-458-apple-glass-mobile-skill` cut from `main`.

---

### Phase 1: Command Center (`Sudo_Hatter_Command`)

#### Master Skill: `apple-glass`

##### [NEW] [apple-glass/SKILL.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/apple-glass/SKILL.md)
Create the master skill:
- **Frontmatter**: Trigger keywords (`apple glass`, `frosted glass`, `liquid glass`, `glassmorphism`, `glass button`, `glass card`).
- **The Mobile-First Invariant**: The fatal failure modes of desktop glass on mobile (snapshot lag, WebGL context loss, battery draw) and why mobile web demands compositor-level CSS or lightweight SVG SDF filters.
- **The Architecture Decision Matrix**: Clear guidelines choosing Tier 1 (Frosted Glass), Tier 2 (Liquid Refraction), or Tier 3 (Native iOS/React Native).
- **Tier 1 HIG Frosted Glass Engine**: Complete Tailwind recipes for cards, floating navigation bars, modal sheets, and pill buttons with the Apple 180% saturation boost and specular rim lighting.
- **Tier 2 Liquid Lens Engine**: Integration guide for `@samasante/liquid-glass` (DOM-wrapping, optics tuning: depth, curvature, dispersion, sheen, WebKit 1x resolution invariant).
- **Tier 3 Native Mobile Bridges**: `@callstack/liquid-glass` for React Native and SwiftUI iOS 26 `.glassEffect()` from `dpearson2699/swift-ios-skills`.
- **Hard Anti-Patterns**: Explicit ban on `html2canvas`, DOM screenshotting, desktop mouse containers, and 3D WebGL FBO multi-sampling for 2D UI elements.

##### [NEW] [apple-glass/RECIPES.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/apple-glass/RECIPES.md)
Author standalone, copy-paste-ready Next.js / React / Tailwind components:
1. `AppleFrostedCard`: Glass container with sub-pixel border, 180% saturation, and top specular sheen.
2. `AppleMobileTabBar`: Floating bottom navigation bar with responsive touch tap states.
3. `AppleLiquidPill`: Refractive floating action pill using `@samasante/liquid-glass`.
4. `AppleGlassModalSheet`: High-translucency mobile bottom sheet.
5. `AppleGlassButton`: Micro-interaction press physics with Emil Kowalski spring damping.

---

#### UI Orchestrator: `/smh-designer` & Caterpillar

##### [MODIFY] [smh-designer.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/commands/smh-designer.md)
- Update Pillar 4 and Capabilities Menu:
  - Update `[LG]` capability code from `Physical Glass (MeshTransmissionMaterial in visual-fx-3d)` to `Apple Glass & Frosted Glass ([apple-glass])`.
  - Add explicit guidance that all glass effects (frosted surfaces and liquid lenses) resolve to `apple-glass` and adhere strictly to mobile-first performance.

##### [MODIFY] [smh-team-caterpillar.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/commands/smh-team-caterpillar.md)
- Update Caterpillar's persona description: replace reference to `MeshTransmissionMaterial glass` with `apple-glass (mobile-first Apple frosted and optical liquid glass)`.

---

#### Clean Up 3D Skill: `visual-fx-3d`

##### [MODIFY] [visual-fx-3d/SKILL.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md)
- Update description and boundary rules: clarify that `visual-fx-3d` is strictly for 3D spatial scenes, glTF models, and Rapier physics.
- Add boundary note: For 2D/UI glass (cards, navigation, buttons), use `apple-glass`. Do not use `MeshTransmissionMaterial` for UI overlays.
- Keep `MeshTransmissionMaterial` strictly as an example of 3D spatial geometry (e.g., a 3D refractive sculpture or crystal inside a 3D scene), with explicit warning that it cannot refract HTML DOM elements.

##### [MODIFY] [visual-fx-3d/CATALOG.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/CATALOG.md) & [RECIPES.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/RECIPES.md)
- Add cross-reference pointing 2D UI glass requests to `apple-glass`.

---

#### Central Documentation & Indexes

##### [MODIFY] [skills/INDEX.md](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/skills/INDEX.md)
- Register `apple-glass` under Frontend / UI tools.

##### [MODIFY] [frontend_UI_design_guide.md](file:///Users/sudohatter/Sudo_Hatter_Command/docs/_scc_sops_prds/frontend_UI_design_guide.md)
- Update Section 4.B and Section 7 table to establish `apple-glass` as the official house standard for all frosted and refractive glass styling.
- Document the two-tier mobile architecture (Tier 1 CSS/Tailwind + Tier 2 `liquid-glass`).

##### [MODIFY] [workflows_testing_SOP.md](file:///Users/sudohatter/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
- Verify and update the `/smh-designer` entry with `apple-glass` capabilities, satisfying `sop_currency.py`.

##### [MODIFY] [_artifacts/_main/INDEX.md](file:///Users/sudohatter/Sudo_Hatter_Command/_artifacts/_main/INDEX.md)
- Append entry for `2026-09-13_scc-458-apple-glass-mobile-skill`.

##### [RUN] `/smh-sync-agents`
- Mirror changes from `.agents/skills/apple-glass/` and `.agents/commands/smh-designer.md` into `.claude/skills/`, `.opencode/`, etc.

---

### Phase 2: Standalone Public Repo (`design-engineer-skills`)

1. Clone or update `sudomadhatter/design-engineer-skills` into scratch directory.
2. Add `skills/apple-glass/` (portable version with relative paths and neutral persona).
3. Update `commands/smh-designer.md` and `docs/frontend_UI_design_guide.md` in `design-engineer-skills`.
4. Update `design-engineer-skills/README.md` and `CREDITS.md` with `@samasante/liquid-glass` credit.
5. Run `python3 verify.py` in `design-engineer-skills` to ensure 0 absolute paths, 0 broken links, and full integrity.
6. Commit and push to `sudomadhatter/design-engineer-skills` `main`.

---

## Verification Plan

### Automated Tests
Run gates inside the worktree:
```bash
# 1. SOP currency check (gating workflows_testing_SOP.md currency against /smh-designer)
python3 .agents/scripts/sop_currency.py --paths .agents/commands/smh-designer.md docs/_scc_sops_prds/workflows_testing_SOP.md

# 2. Command surface and index verification
pytest tests/test_command_surfaces.py
pytest tests/test_permission_parity.py
pytest tests/test_settings_allowlist.py

# 3. Repository maps and integrity check
python3 .agents/scripts/check_maps.py

# 4. Standalone repo integrity check
python3 verify.py (inside design-engineer-skills)
```

### Manual Verification
- Verify TypeScript and Tailwind syntax in `apple-glass/SKILL.md` and `apple-glass/RECIPES.md`.
- Validate that all imports in recipes match real packages (`@samasante/liquid-glass`, `@callstack/liquid-glass`).
- Confirm zero occurrences of `html2canvas` or DOM snapshot hacks across the new skill files.
