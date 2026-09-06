# Frontend & UI/UX Design Guide

**The house standard for world-class, fluid, production-ready interfaces.** This procedural guide establishes how agents and operators design, build, animate, and audit user interfaces across all projects in the command center.

Consolidates the four pillars of house UI craft:
1. **Design System & Visual Intelligence**: [`.agents/skills/ui-ux-pro-max`](../../.agents/skills/ui-ux-pro-max/SKILL.md) — 67 styles, 96 color palettes, 57 font pairings, 99 UX heuristics, and stack guidelines via `search.py`.
2. **Master Motion Engine & Fluid Interactions**: [`.agents/skills/emil-design-eng`](../../.agents/skills/emil-design-eng/SKILL.md) — Consolidated Emil Kowalski motion craft, Apple 2-parameter spring physics, 4-gate opportunity filter, sub-300ms budget, and Before/After review tables.
3. **3D, WebGL Shaders & Physical Materials**: [`.agents/skills/visual-fx-3d`](../../.agents/skills/visual-fx-3d/SKILL.md) — React Three Fiber (R3F), ShaderGradient fluid meshes, Liquid Glass optical refraction, and Liquid Logo plasma shaders.
4. **Rich Media & Platform Specialists**: [`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md) (green-screen to alpha WebM), [`.agents/skills/animate-expo`](../../.agents/skills/animate-expo/SKILL.md) (React Native / Expo), [`.agents/skills/write-swift`](../../.agents/skills/write-swift/SKILL.md) (iOS native).

Front door: **`/smh-designer`** ([`.agents/commands/smh-designer.md`](../../.agents/commands/smh-designer.md)) — activates **🦋 Caterpillar** with the Two-Phase Creative Vision Lock lifecycle.

---

## 1. The Four Pillars of UI Excellence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       HOUSE FRONTEND DESIGN ARCHITECTURE                     │
├──────────────────────────────┬──────────────────────────────┬───────────────┤
│ 1. VISUAL SYSTEM & TOKENS    │ 2. FLUID MOTION & CRAFT      │ 3. 3D & FX    │
│ • ui-ux-pro-max              │ • emil-design-eng (Merged)   │ • visual-fx-3d│
│   (67 styles, 96 palettes,   │   (Philosophy, Apple springs,│   (R3F 3D,    │
│    57 font pairings, search) │    recipes, review audit,    │    Shaders,   │
│                              │    opportunity gate)         │    Glass,     │
│                              │                              │    Logo)      │
├──────────────────────────────┴──────────────────────────────┼───────────────┤
│ 4. SPECIALIZED COMPANIONS                                   │ 5. MAESTRO    │
│ • webm-alpha-video (Green screen MP4 → Alpha WebM)          │ • /smh-designer
│ • animate-expo (React Native / Expo Reanimated)             │   (Two-phase  │
│ • write-swift (Native iOS Swift UI)                         │    vision lock│
└─────────────────────────────────────────────────────────────┴───────────────┘
```

---

## 2. Universal Animation & Motion Law

Great animation is unseen correctness. In our systems, animation is not decoration tacked on after layout; it is the physical feedback layer that connects user intention to state change.

### The Decision Framework
Before writing any animation code, walk these four questions in order:

1. **Should this animate at all?**
   - **100+ times/day (command palettes, keyboard shortcuts, fast navigation):** **NO animation. Ever.** Raycast-style instant state changes.
   - **Tens of times/day (hover effects, list selects):** Ultra-fast ($\le 150\text{ms}$) or no motion.
   - **Occasional (modals, drawers, toasts):** Standard smooth animation ($150\text{--}300\text{ms}$).
   - **First-time / milestone (onboarding, success celebrations):** Expressive, delightful motion.

2. **What easing should it use?**
   - **Entering elements:** `ease-out` (starts instantly, feels responsive to the user's action).
   - **Exiting elements:** `ease-out` or fast `ease-in-out` ($\le 200\text{ms}$).
   - **Moving / morphing on-screen:** `ease-in-out` or physical spring.
   - ⛔ **NEVER use `ease-in` for UI animations.** It delays the initial movement, making the app feel laggy and sluggish.
   - **Custom curves beat default CSS:**
     ```css
     /* Strong ease-out for snappy UI */
     --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
     /* Natural on-screen movement */
     --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
     /* iOS-style sheet/drawer curve */
     --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
     ```

3. **How fast should it be?**
   - **Button press feedback:** $100\text{--}160\text{ms}$.
   - **Tooltips & popovers:** $125\text{--}200\text{ms}$.
   - **Dropdowns & selects:** $150\text{--}250\text{ms}$.
   - **Modals & bottom sheets:** $200\text{--}350\text{ms}$.
   - **Hard Rule:** Standard UI interactions must stay under $300\text{ms}$.

4. **Springs vs Duration?**
   - Use **springs** for gesture-driven interactions, drag-and-drop, drawers, and interruptible UI.
   - **Apple 2-parameter spring model:**
     - Default UI (no bounce): `damping: 1.0`, `response: 0.3-0.4s` (`{ type: "spring", duration: 0.4, bounce: 0 }`).
     - Momentum flick / throw: `damping: ~0.8`, `response: 0.3-0.4s` (`{ type: "spring", duration: 0.4, bounce: 0.2 }`).

---

## 3. Core Component Building Rules

### A. Buttons & Pressables
- **Instant feedback on press:** Always add `transform: scale(0.97)` on `:active`.
  ```css
  .button {
    transition: transform 160ms ease-out;
  }
  .button:active {
    transform: scale(0.97);
  }
  ```
- **Never animate from `scale(0)`:** Nothing in reality appears from a mathematical point. Start from `scale(0.95)` with `opacity: 0`.

### B. Popovers, Dropdowns & Modals
- **Origin awareness:** Popovers and dropdowns must scale in from their triggering button (`transform-origin: var(--transform-origin)`).
- **Modals are exempt:** Modals appear centered in the viewport and keep `transform-origin: center`.

### C. Tooltips
- **First hover:** Normal brief delay (~300ms) to avoid accidental triggers while scanning.
- **Subsequent hovers:** Instant appearance (`transition-duration: 0ms`) while the pointer moves across sibling toolbar icons.

### D. Translucent Materials & Depth
- Translucent chrome (`backdrop-filter: blur(20px) saturate(180%)`) lets content scroll beneath navigation bars without feeling disconnected.
- Never stack light translucent layers on other translucent layers (legibility collapse).
- In dark mode, use subtle semi-transparent white borders (`border: 1px solid rgba(255, 255, 255, 0.1)`) instead of black borders.

---

## 4. 3D, WebGL Shaders & Physical Materials ([`visual-fx-3d`](../../.agents/skills/visual-fx-3d/SKILL.md))

Modern interfaces incorporate physical depth, optical light refraction, and GPU-accelerated fluid shaders. We support four standard engines:

1. **React Three Fiber (R3F) (`pmndrs/react-three-fiber`):** Declarative 3D canvas for spatial cards, product models, and interactive geometric accents.
   - **Constraint:** Always use `frameloop="demand"` and cap `dpr={[1, 1.5]}` so the GPU completely idles when static.
2. **Liquid Glass (`dashersw/liquid-glass-js`):** Apple VisionOS-style realistic optical glass refraction with chromatic edge dispersion and specular highlights.
   - **Constraint:** Never stack two refractive layers directly over each other. Provide a clean `backdrop-filter: blur(20px)` fallback.
3. **ShaderGradient (`ruucm/shadergradient`):** High-performance 3D fluid animated gradient mesh backgrounds.
   - **Constraint:** Keep ambient wave speeds low ($\le 0.3$) and pause via `IntersectionObserver` when scrolled off-screen.
4. **Liquid Logo (`collidingScopes/liquid-logo`):** Real-time liquid metal and plasma fragment shaders mapped to SVG brand marks and typography.

---

## 5. Rich Media & Transparent Video ([`webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md))

When user interfaces require floating video elements (e.g. animated mascots, floating holographic badges, voice-assistant reaction avatars):
- Green-screen MP4 videos can be converted to true transparent WebM videos (`VP9` codec with `yuva420p` pixel format).
- Run the ffmpeg chromakey conversion pipeline via [`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md):
  ```bash
  ffmpeg -i input_greenscreen.mp4 -vf "colorkey=0x00FF00:0.3:0.1,format=yuva420p" -c:v libvpx-vp9 -b:v 2M output_alpha.webm
  ```
- Embed cleanly in web frontends with `<video autoPlay loop muted playsInline className="pointer-events-none ...">`.

---

## 6. The Two-Phase Creative Vision Lock Lifecycle (`/smh-designer`)

Front-end design is sensory. To avoid coding the wrong visual aesthetic, [`/smh-designer`](../../.agents/commands/smh-designer.md) enforces a two-phase gate:

```
Phase 1: Creative Discovery & Vision Lock
  ↳ Interview on aesthetic mood, physics, and materials
  ↳ Deliver Creative Vision Brief
  ↳ ⛔ STOP FOR APPROVAL: Mr. Hatter confirms "Approved"

Phase 2: Technical Translation & Ticket Minting
  ↳ Deliver formal implementation_plan.md + mint/shape Jira ticket via acli
  ↳ ⛔ STOP FOR APPROVAL: Mr. Hatter confirms "Approved"

Phase 3: Development Hand-off
  ↳ Launch /smh-quick-dev or /cicd-dev-story-tests
```

---

## 7. Agent Skill Routing Matrix

When an agent needs to perform UI/UX work, route to the appropriate consolidated master skill:

| Task | Primary Skill | Supporting Resources / Capabilities |
|---|---|---|
| Complete design systems, color palettes, font pairings, styles | [`.agents/skills/ui-ux-pro-max`](../../.agents/skills/ui-ux-pro-max/SKILL.md) | `search.py --design-system` |
| Motion craft, animations, easings, spring physics, review tables, toasts | [`.agents/skills/emil-design-eng`](../../.agents/skills/emil-design-eng/SKILL.md) | `RECIPES.md` · Apple 2-parameter springs · Before/After tables |
| 3D scenes, WebGL shaders, liquid glass refraction, liquid logos | [`.agents/skills/visual-fx-3d`](../../.agents/skills/visual-fx-3d/SKILL.md) | R3F · ShaderGradient · Liquid Glass · Liquid Logo |
| Mobile gestures & animations (React Native / Expo Reanimated) | [`.agents/skills/animate-expo`](../../.agents/skills/animate-expo/SKILL.md) | Worklets & reanimated recipes |
| Apple platform UI & native Swift motion | [`.agents/skills/write-swift`](../../.agents/skills/write-swift/SKILL.md) | Native SwiftUI springs & gestures |
| Converting green-screen assets to transparent WebM video overlays | [`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md) | ffmpeg colorkey scripts |
| End-to-end design engineering persona with Two-Phase Vision Lock | [`.agents/commands/smh-designer.md`](../../.agents/commands/smh-designer.md) | 🦋 Caterpillar — Brainstorm, Audit, Scaffold & Build |

---

## 8. Pre-Delivery UI Quality Checklist

Before completing any frontend story, chore, or UI refactor, verify against this checklist:

### Visual Quality
- [ ] **No Emoji Icons:** Use consistent SVG icon sets (Lucide, Heroicons, Simple Icons) instead of emoji characters.
- [ ] **Stable Hover States:** Use color/background/shadow transitions on hover; never use scale transforms that cause layout shifts on sibling elements.
- [ ] **High Contrast Text:** Minimum 4.5:1 contrast ratio in both Light and Dark modes.
- [ ] **Border Visibility:** In dark mode, borders use subtle white opacity (`rgba(255, 255, 255, 0.1)`); in light mode, clean neutral borders (`#E2E8F0`).

### Motion & Interaction
- [ ] **Press Feedback:** All clickable cards, buttons, and list items have `cursor: pointer` and `:active` scale feedback (`scale(0.97)`).
- [ ] **GPU Acceleration:** Only animate `transform` and `opacity`. Never animate `height`, `width`, `padding`, or `margin` directly.
- [ ] **No `ease-in` on Enters:** All enter transitions use `ease-out` or custom spring physics.
- [ ] **Animation Duration Budget:** All UI transitions complete in $\le 300\text{ms}$.
- [ ] **Interruptibility:** Gesture-driven components (sheets, drawers, sliders) update 1:1 with pointer events and hand off velocity smoothly on release.
- [ ] **Accessibility:** All animations respect `@media (prefers-reduced-motion: reduce)` by falling back to gentle crossfades or static states.
