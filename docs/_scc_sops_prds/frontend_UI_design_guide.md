# Frontend & UI/UX Design Guide

**The house standard for world-class, fluid, production-ready interfaces.** This procedural guide establishes how agents and operators design, build, animate, and audit user interfaces across all projects in the command center.

Consolidates the three pillars of house UI craft:
1. **Design System & Visual Intelligence**: [`.agents/skills/ui-ux-pro-max`](../../.agents/skills/ui-ux-pro-max/SKILL.md) — 67 styles, 96 color palettes, 57 font pairings, 99 UX heuristics, and stack guidelines.
2. **Motion, Animation & Fluid Interactions**: The Emil Kowalski skill suite — [`.agents/skills/emil-design-eng`](../../.agents/skills/emil-design-eng/SKILL.md), [`.agents/skills/apple-design`](../../.agents/skills/apple-design/SKILL.md), [`.agents/skills/animate`](../../.agents/skills/animate/SKILL.md), [`.agents/skills/review-animations`](../../.agents/skills/review-animations/SKILL.md), and companions.
3. **Rich Visual Assets & Floating Elements**: [`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md) — green-screen MP4 to WebM conversion with true alpha transparency for floating badges and video overlays.

---

## 1. The Three Pillars of UI Excellence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       HOUSE FRONTEND DESIGN ARCHITECTURE                     │
├──────────────────────────────┬──────────────────────────────┬───────────────┤
│    1. VISUAL & DESIGN SYSTEM │      2. FLUID MOTION & UX    │ 3. ASSETS &   │
│                              │                              │    RICH MEDIA │
├──────────────────────────────┼──────────────────────────────┼───────────────┤
│ • ui-ux-pro-max              │ • emil-design-eng            │ • webm-alpha- │
│ • Typography & Optical Size  │ • apple-design (Springs)     │   video       │
│ • Color Palettes & Contrast  │ • animate / animate-expo     │ • Pure SVG    │
│ • Dark/Light Mode Invariants │ • review-animations          │   Icons       │
│ • Layout, Grids & Cards      │ • find-animation-opps        │ • Translucent │
│ • react-best-practices       │ • ask-sonner / prototype     │   Materials   │
└──────────────────────────────┴──────────────────────────────┴───────────────┘
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

## 4. Rich Media & Transparent Video ([`webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md))

When user interfaces require floating video elements (e.g. animated mascots, floating holographic badges, voice-assistant reaction avatars):
- Green-screen MP4 videos can be converted to true transparent WebM videos (`VP9` codec with `yuva420p` pixel format).
- Run the ffmpeg chromakey conversion pipeline via [`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md):
  ```bash
  ffmpeg -i input_greenscreen.mp4 -vf "colorkey=0x00FF00:0.3:0.1,format=yuva420p" -c:v libvpx-vp9 -b:v 2M output_alpha.webm
  ```
- Embed cleanly in web frontends with `<video autoPlay loop muted playsInline className="pointer-events-none ...">`.

---

## 5. Agent Skill Routing Matrix

When an agent needs to perform UI/UX work, route to the appropriate master skill:

| Task | Primary Skill | Supporting Resources |
|---|---|---|
| Creating or updating complete design systems, color palettes, font pairings, styles | [`.agents/skills/ui-ux-pro-max`](../../.agents/skills/ui-ux-pro-max/SKILL.md) | `search.py --design-system` |
| Designing or refining animations, easings, spring physics, and micro-interactions | [`.agents/skills/emil-design-eng`](../../.agents/skills/emil-design-eng/SKILL.md) | [`.agents/skills/animate`](../../.agents/skills/animate/SKILL.md) · [`.agents/skills/apple-design`](../../.agents/skills/apple-design/SKILL.md) |
| Reviewing/auditing motion code against industry animation standards | [`.agents/skills/review-animations`](../../.agents/skills/review-animations/SKILL.md) | [`.agents/skills/improve-animations`](../../.agents/skills/improve-animations/SKILL.md) |
| Spotting static UI elements that need motion or transition polish | [`.agents/skills/find-animation-opportunities`](../../.agents/skills/find-animation-opportunities/SKILL.md) | [`.agents/skills/animation-vocabulary`](../../.agents/skills/animation-vocabulary/SKILL.md) |
| Mobile animations & gestures (React Native / Expo Reanimated) | [`.agents/skills/animate-expo`](../../.agents/skills/animate-expo/SKILL.md) | Reanimated recipes & worklets |
| Apple platform UI, fluid gestures, and Swift motion | [`.agents/skills/apple-design`](../../.agents/skills/apple-design/SKILL.md) | [`.agents/skills/write-swift`](../../.agents/skills/write-swift/SKILL.md) |
| Toast notifications & stack management | [`.agents/skills/ask-sonner`](../../.agents/skills/ask-sonner/SKILL.md) | Sonner best practices |
| Converting green-screen assets to transparent WebM video overlays | [`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md) | ffmpeg colorkey scripts |
| Component library selection & evaluation | [`.agents/skills/pick-ui-library`](../../.agents/skills/pick-ui-library/SKILL.md) | Radix, Base UI, Shadcn |

---

## 6. Pre-Delivery UI Quality Checklist

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
