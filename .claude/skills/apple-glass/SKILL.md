---
name: apple-glass
description: "Mobile-first Apple frosted glass and liquid glass effects for web and native mobile. Tier 1: Apple HIG frosted glass with backdrop-filter, 180% saturation boost, and specular border highlights for 60/120fps mobile performance. Tier 2: Apple liquid glass with optical refraction, chromatic dispersion, and live DOM bending via samasante/liquid-glass without canvas screenshotting. Tier 3: Native mobile Liquid Glass for React Native (@callstack/liquid-glass) and SwiftUI iOS 26 (.glassEffect). Strict ban on desktop html2canvas and Three.js 3D canvas hacks for 2D UI."
---

# Apple Glass — Mobile-First Glass & Refraction Engine

The single source of truth for all **"frosted glass"**, **"apple glass"**, and **"liquid glass"** implementations across the command center and projects. 

Every recipe here is engineered **mobile-first**: locked 60/120fps scrolling on iOS Safari and Android Chrome, zero thermal throttling, zero WebGL context exhaustion, and full accessibility support.

---

## 1. The Mobile-First Invariant

Desktop web demos frequently cheat by taking canvas screenshots of the page (`html2canvas` in `dashersw/liquid-glass-js`) or spinning up full-screen 3D WebGL canvases with multi-pass Frame Buffer Objects (`MeshTransmissionMaterial` in Three.js).

On mobile devices, these desktop shortcuts fail catastrophically:
* **The Static Snapshot Trap:** `html2canvas` captures the page once at load time. When a mobile user scrolls, the glass displays a frozen, misplaced snapshot of the top of the page. Re-running `html2canvas` on scroll freezes the mobile CPU for 200–1,000ms per frame.
* **WebGL Context Limits:** Mobile Safari caps concurrent WebGL contexts at 8–16 system-wide. Adding separate WebGL canvases for navigation pills and cards quickly crashes the browser with `CONTEXT_LOST_WEBGL`.
* **Thermal Throttling & Battery Drain:** FBO multi-sampling (10 samples per pixel on a 3x Retina display) exhausts mobile GPUs within seconds.
* **Non-Refractive DOM:** 3D WebGL materials cannot refract HTML text, buttons, or inputs underneath them — only 3D geometry inside their own canvas.

**The House Rule:** 
1. Use **Tier 1 (CSS/Tailwind Compositor Glass)** for 95% of UI: cards, sheets, headers, navigation bars, and modals.
2. Use **Tier 2 (SDF Filter Live DOM Refraction via `@samasante/liquid-glass`)** only for dedicated refractive controls: Dynamic Island pills, floating action buttons, and slider thumbs.
3. Never use `html2canvas`, SVG foreignObject screenshotting, or 3D WebGL canvases for 2D UI elements.

---

## 2. Decision Matrix: Which Glass to Use

| Use Case | Recommended Engine | Platform | Performance |
|---|---|---|---|
| **Cards, Modals, Navigation Bars, Tab Bars, Dropdowns** | **Tier 1: Apple HIG Frosted Glass** | Web / Next.js / Tailwind | Native Compositor (120fps, 0 JS overhead) |
| **Interactive Lenses, Floating Pills, Dynamic Island, Sliders** | **Tier 2: Apple Liquid Glass (`@samasante/liquid-glass`)** | Web / Next.js / React | SVG SDF filter over live DOM (<5KB, 0 deps) |
| **Native iOS / iPadOS Apps (React Native)** | **Tier 3: `@callstack/liquid-glass`** | React Native / Expo | Native UIKit / SwiftUI bridge (120Hz ProMotion) |
| **Native iOS Apps (Swift / SwiftUI)** | **Tier 3: `.glassEffect()`** | iOS 26+ Native Swift | Apple Native Framework (`GlassEffectContainer`) |
| **True 3D Spatial Geometry / GLTF Models** | **[`visual-fx-3d`](../visual-fx-3d/SKILL.md)** | WebGL / R3F / Drei | Dedicated 3D Canvas only (not for DOM UI) |

---

## 3. Tier 1: Apple HIG Frosted Glass (CSS & Tailwind)

This is Apple's production standard for the iOS Control Center, Safari tab bars, Lock Screen widgets, and modal sheets. It runs entirely on the mobile GPU's hardware compositor without JavaScript overhead.

### The Apple Glass Formula
Authentic Apple frosted glass requires three coordinated optical layers:
1. **`backdrop-saturate-180`**: Apple's hallmark vibrancy. Boosts color saturation behind the glass by 180% to prevent the backdrop from looking like dull milky plastic.
2. **`backdrop-blur-xl` (or `backdrop-blur-2xl`)**: Heavy Gaussian blur that diffuses background shapes into pure ambient illumination.
3. **Sub-Pixel Specular Border (`border border-white/20`)**: A 1px translucent highlight simulating the physical cut edge of beveled glass catching ambient room light.
4. **Top Rim Sheen Gradient**: A 1px horizontal gradient across the top rim simulating overhead light reflection.

### Production Recipe: Floating Mobile Tab Bar / Nav Card

```tsx
export function AppleFrostedCard({ 
  children, 
  className = '' 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <div className={`
      relative overflow-hidden rounded-3xl
      /* Translucent Surface: Dark Mode vs Light Mode */
      bg-neutral-900/65 dark:bg-neutral-900/65 bg-white/75
      /* The Apple Formula */
      backdrop-blur-xl backdrop-saturate-180
      /* Sub-Pixel Specular Rim Border */
      border border-white/20 dark:border-white/10
      /* Subtle Ambient Shadow */
      shadow-[0_8px_32px_0_rgba(0,0,0,0.18)]
      /* Prevent iOS Safari composite bleed */
      transform-gpu isolation-isolate
      ${className}
    `}>
      {/* Top Specular Rim Reflection */}
      <div 
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 dark:via-white/20 to-transparent" 
      />
      
      {/* Interactive Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
```

### Mobile Touch Active States
When building touchable glass controls (chips, buttons, segmented controls), combine with Emil Kowalski spring motion and an inner glow:

```tsx
<button className="
  px-4 py-2.5 rounded-full text-sm font-medium text-white
  bg-white/10 hover:bg-white/15 active:bg-white/25
  backdrop-blur-lg backdrop-saturate-180
  border border-white/20 active:scale-95
  transition-all duration-150 ease-out
">
  Cockpit View
</button>
```

### Accessibility Fallback
Always respect user preferences for reduced transparency (`prefers-reduced-transparency`):
```css
@media (prefers-reduced-transparency: reduce) {
  .apple-glass {
    backdrop-filter: none !important;
    background-color: rgb(23 23 23 / 0.95) !important;
  }
}
```
In Tailwind: `contrast-more:bg-neutral-950/95 contrast-more:backdrop-blur-none`.

---

## 4. Tier 2: Apple Liquid Glass (Refractive Lens via `@samasante/liquid-glass`)

When an interface genuinely demands **physical optical refraction** (curved edge bending, chromatic dispersion, magnification) over live DOM content:

Install:
```bash
npm install @samasante/liquid-glass
```

### Why `@samasante/liquid-glass` Works on Mobile
- **Live DOM Refraction:** Directly wraps interactive HTML/React components. Text remains selectable, links remain clickable, buttons respond instantly to touch.
- **Signed Distance Field (SDF) Filters:** Calculates rounded-rectangle refraction mathematically rather than taking raster screenshots.
- **Hardened for WebKit on iOS Safari:**
  1. *1× Resolution Ceiling:* Bypasses Safari's texture size limit that causes other libraries to drop chromatic aberration.
  2. *Debounced Shape Regeneration:* The displacement map updates only when the pill expands or changes shape — scrolling or dragging moves the filter with zero re-calculation.
  3. *Cache-Busting Filter IDs:* Automatically invalidates WebKit's internal filter cache during animations so the lens never freezes.
  4. *Zero Dependencies:* Less than 5KB gzipped.

### Production Recipe: Refractive Floating Island Pill

```tsx
'use client';

import React from 'react';
import { Glass } from '@samasante/liquid-glass';

export function AppleLiquidPill({
  title = "Flight Plan Active",
  actionText = "View",
  onAction
}: {
  title?: string;
  actionText?: string;
  onAction?: () => void;
}) {
  return (
    <div className="fixed bottom-6 inset-x-0 flex justify-center z-50 pointer-events-none px-4">
      <div className="pointer-events-auto">
        <Glass
          width={320}
          height={58}
          radius={29}
          optics={{
            depth: 0.8,         // How far the edge refraction extends
            curvature: 0.35,     // Magnification curvature in center
            dispersion: 0.22,    // Subtle Apple prismatic chromatic fringing
            frost: 5,            // Frosted background blur
            sheen: 0.45,         // Specular highlight intensity
            sheenWidth: 0.2,     // Width of rim light
          }}
        >
          <div className="flex items-center justify-between w-full h-full px-5 text-white">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-sm font-medium tracking-tight">{title}</span>
            </div>
            
            <button
              onClick={onAction}
              className="px-3 py-1 rounded-full text-xs font-semibold bg-white/20 hover:bg-white/30 active:scale-95 transition-transform"
            >
              {actionText}
            </button>
          </div>
        </Glass>
      </div>
    </div>
  );
}
```

---

## 5. Tier 3: Native Mobile Apps (React Native & SwiftUI)

When building native mobile applications, use Apple's native platform materials directly.

### React Native / Expo (`@callstack/liquid-glass`)
For React Native iOS 26+ apps:
```bash
npm install @callstack/liquid-glass
```

```tsx
import { LiquidGlassView, LiquidGlassContainerView, isLiquidGlassSupported } from '@callstack/liquid-glass';
import { Text, PlatformColor } from 'react-native';

export function NativeGlassButton() {
  return (
    <LiquidGlassView
      style={{
        width: 200,
        height: 52,
        borderRadius: 26,
        justifyContent: 'center',
        alignItems: 'center',
        ...(!isLiquidGlassSupported && { backgroundColor: 'rgba(255,255,255,0.85)' })
      }}
      interactive
      effect="clear"
    >
      <Text style={{ color: PlatformColor('labelColor'), fontWeight: '600' }}>
        Confirm Flight
      </Text>
    </LiquidGlassView>
  );
}
```

### SwiftUI (iOS 26+ Native)
For iOS native code (handled via `write-swift`):
```swift
if #available(iOS 26, *) {
    GlassEffectContainer(spacing: 20) {
        HStack(spacing: 16) {
            Button("Overview") { }
                .buttonStyle(.glass)
            Button("Controls") { }
                .buttonStyle(.glassProminent)
        }
    }
} else {
    // Fallback for pre-iOS 26
    HStack(spacing: 16) {
        Button("Overview") { }
            .buttonStyle(.bordered)
        Button("Controls") { }
            .buttonStyle(.borderedProminent)
    }
}
```

---

## 6. Anti-Patterns & Hard Stops

| Anti-Pattern | Why It Is Forbidden | What to Use Instead |
|---|---|---|
| `html2canvas` / DOM Screenshotting | Freezes mobile CPU (200–1,000ms per frame), breaks on scroll, taints on CORS. | Tier 1 CSS `backdrop-filter` or Tier 2 `@samasante/liquid-glass`. |
| Three.js `MeshTransmissionMaterial` for 2D UI | FBO multi-sampling drains battery, crashes mobile WebGL context, cannot refract DOM. | Reserve `visual-fx-3d` strictly for 3D spatial models; use `apple-glass` for UI. |
| Mouse-bound glass (`rdev/liquid-glass-react`) | Completely broken on iOS Safari (displacement invisible); tied to desktop cursors. | Tier 1 CSS or Tier 2 `@samasante/liquid-glass`. |
| Experimental WebGPU HTML-in-Canvas | Requires desktop Chrome experimental flags (`canvas-draw-element`). Fails on mobile. | Standard WebKit-compatible SVG filters or CSS. |
| Nested glass without containers | Multi-pass blurs on overlapping transparent elements cause compositor artifacts. | Wrap related elements in a single container or use 1 blur layer with plain alpha children. |
| Skipping saturation boost | Standard `backdrop-blur` without `backdrop-saturate-180` produces a muddy gray film. | Always pair `backdrop-blur` with `backdrop-saturate-180` and `border-white/20`. |

---

## 7. Component Catalog

See [`RECIPES.md`](RECIPES.md) for full copy-paste TypeScript/Tailwind components:
1. `AppleFrostedCard` (Content card with sub-pixel border and top rim highlight)
2. `AppleMobileTabBar` (Floating bottom navigation dock with touch states)
3. `AppleLiquidPill` (Refractive lens pill with chromatic dispersion)
4. `AppleGlassModalSheet` (Mobile bottom sheet with spring drag)
5. `AppleGlassButton` (Micro-interaction tactile glass button)

