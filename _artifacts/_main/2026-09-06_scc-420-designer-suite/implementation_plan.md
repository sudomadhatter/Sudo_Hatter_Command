# Implementation Plan — Front-End Designer Powerhouse & Visual FX Suite

Consolidate the fragmented UI/UX & motion skills into an integrated three-pillar powerhouse, introduce the universal `/smh-designer` command featuring a **Two-Phase Creative Vision Lock** lifecycle, incorporate the four modern visual FX engines (`react-three-fiber`, `liquid-glass-js`, `shadergradient`, `liquid-logo`), and update `.agents/commands/smh-team-caterpillar.md` last.

---

## User Review Required

> [!IMPORTANT]
> **Consolidation of 8 Overlapping Micro-Skills:**  
> The 8 micro-skills from `emilkowalski/skills` (`review-animations`, `improve-animations`, `find-animation-opportunities`, `apple-design`, `animate`, `animation-vocabulary`, `prototype`, `pick-ui-library`, and `ask-sonner`) will be retired as standalone directories and fully absorbed into [`emil-design-eng`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/emil-design-eng/SKILL.md) as one comprehensive, authoritative motion manual.

> [!IMPORTANT]
> **Sequencing Constraint:**  
> As instructed by Mr. Hatter, [`.agents/commands/smh-team-caterpillar.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-team-caterpillar.md) (the Zoo designer mode documentation) will be updated **last**, after the consolidated skills, new visual FX skill, and documentation have settled.

---

## Proposed Changes

### 1. Motion Skill Consolidation (Pillar 2)

#### [MODIFY] [`emil-design-eng/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/emil-design-eng/SKILL.md)
- Expand to become the **Master Motion Engine**.
- Absorb:
  - **The Opportunity Filter:** 100+/day Raycast rule, frequency vs. purpose check (from `find-animation-opportunities`).
  - **Apple Springs:** 2-parameter spring physics (`response`, `damping`) (from `apple-design`).
  - **Code Recipes:** CSS transitions, Framer Motion springs, enter/exit curves, and Sonner toast patterns (from `animate` and `ask-sonner`).
  - **Code Review & Audit Engine:** The mandatory `| Before | After | Why |` markdown review table and severity tiers (from `review-animations` and `improve-animations`).
  - **Prototyping & Library Matrix:** 3-variant comparison and library evaluation (from `prototype` and `pick-ui-library`).

#### [DELETE] Redundant Micro-Skills
- `review-animations/`
- `improve-animations/`
- `find-animation-opportunities/`
- `apple-design/`
- `animate/`
- `animation-vocabulary/`
- `prototype/`
- `pick-ui-library/`
- `ask-sonner/`

---

### 2. New 3D, Shaders & Physical Materials Engine (Pillar 3)

#### [NEW] [`.agents/skills/visual-fx-3d/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md)
- Encapsulates the four modern web repositories:
  - **React Three Fiber (R3F)** (`pmndrs/react-three-fiber`): Declarative 3D scenes, meshes, materials, lighting, cameras, on-demand rendering (`frameloop="demand"`).
  - **Liquid Glass** (`dashersw/liquid-glass-js`): Optical glass refraction, light bending, chromatic dispersion, and frosted overlays.
  - **ShaderGradient** (`ruucm/shadergradient`): Fluid 3D animated gradient mesh backgrounds.
  - **Liquid Logo** (`collidingScopes/liquid-logo`): WebGL plasma and liquid metal shaders mapped to SVG logos/marks.
- Includes installation guides, component recipes, GPU/battery constraints, and accessibility fallbacks (`@media (prefers-reduced-motion)`).

---

### 3. The Universal Front-End Designer Command (`/smh-designer`)

#### [NEW] [`.agents/commands/smh-designer.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-designer.md)
- Modeled directly on the activation ritual of [`bmad-agent-ux-designer`](file:///home/dlohn/Sudo_Hatter_Command/.agent/skills/bmad-agent-ux-designer/SKILL.md).
- Persona: **🦋 Caterpillar — Lead Design Engineer & Visual Craftsman**.
- Implements the **Two-Phase Lifecycle**:
  - **Phase 1: Creative Discovery & Vision Lock** (Conversational interview $\to$ Creative Vision Brief $\to$ Stop for Mr. Hatter's "Approved").
  - **Phase 2: Technical Translation & Ticket** (Translates vision into `implementation_plan.md` + mints/shapes Jira ticket via `acli` $\to$ Stop for Mr. Hatter's "Approved").
  - **Phase 3: Hand-off** (Launches directly into `/smh-quick-dev` or `/cicd-dev-story-tests`).
- Capabilities Menu: `[BS]` Brainstorm, `[DS]` Design System, `[FM]` Fluid Motion, `[3D]` 3D Canvas, `[SG]` Shader Gradients, `[LG]` Liquid Glass, `[LL]` Liquid Logo, `[AU]` Code Audit, `[CD]` Code Scaffolding.
- Universal platform reach: `platforms: [claude, opencode, antigravity, codex, zoo]`.

#### [NEW] [`.agents/skills/smh-designer/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/smh-designer/SKILL.md)
- Companion skill launcher providing native discovery across Antigravity, Codex, and Claude.

---

### 4. House Design Guide & SOP Currency

#### [MODIFY] [`docs/_scc_sops_prds/frontend_UI_design_guide.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/frontend_UI_design_guide.md)
- Update Section 1 with the consolidated 4-pillar architecture.
- Add **Pillar 4: 3D, WebGL Shaders & Physical Materials**.
- Update the Agent Skill Routing Matrix (Section 5) to reflect the consolidated skills.
- Add the Two-Phase Creative Vision Lock lifecycle documentation.

#### [MODIFY] [`docs/_scc_sops_prds/workflows_testing_SOP.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
- Document `/smh-designer` usage, intent, and workflow parameters for the operator.

#### [MODIFY] [`.agents/commands/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/INDEX.md) & [`.agents/skills/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/INDEX.md)
- Catalog `/smh-designer` and the consolidated skill set.
- Remove references to deleted micro-skills.

---

### 5. Zoo Designer Documentation (UPDATED LAST)

#### [MODIFY] [`.agents/commands/smh-team-caterpillar.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-team-caterpillar.md)
- **Updated last as mandated.**
- Update Caterpillar's door descriptions to point to the consolidated `emil-design-eng`, `visual-fx-3d`, `ui-ux-pro-max`, and `/smh-designer`.
- Remove dead references to `apple-design` and standalone micro-skills.

---

## Verification Plan

### Automated Tests
- `python3 tests/run_all.py` — Verifies all unit tests, memory store, and command parity.
- `python3 .agents/scripts/workflow_lint.py --toolkit-only` — Validates command frontmatter, naming, and platform reach.
- `python3 .agents/scripts/sop_currency.py` — Confirms `workflows_testing_SOP.md` matches all updated commands.

### Sync & Parity Verification
- Run `/smh-sync-agents` (or `python3 .agents/scripts/sync_agents.py` / `pwsh .agents/scripts/sync-agents.ps1`) to publish changes to `.claude/`, `.opencode/`, `.roo/`, and machine caches.
- Verify that `.roomodes` is generated cleanly and that Zoo mode `designer` reflects the updated Caterpillar documentation.
