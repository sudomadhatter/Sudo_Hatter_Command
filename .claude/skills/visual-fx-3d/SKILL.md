---
name: visual-fx-3d
description: Declarative 3D scenes, spatial models, and optical physical glass materials. Covers React Three Fiber (R3F), Drei, and Liquid Glass refraction. For 2D/compute shaders and ambient fluid meshes, see vgpu.
---

# Visual FX & 3D Materials (Spatial Models & Glass)

The house engine for high-end modern 3D spatial craft: declarative 3D scene graphs, glTF product models, spatial lighting, and Apple VisionOS optical glass refraction.

> **Architecture Note:** Ambient fluid mesh backgrounds, 2D canvas shaders, and plasma noise have migrated to [`.agents/skills/vgpu`](../vgpu/SKILL.md). `visual-fx-3d` is dedicated to spatial 3D models and optical refraction.

This skill integrates two foundational open-source toolkits:
1. **React Three Fiber (R3F)** (`pmndrs/react-three-fiber`): Declarative 3D scene graphs, camera rigs, and glTF models in React.
2. **Liquid Glass** (`dashersw/liquid-glass-js`): Apple VisionOS-grade physical optical glass refraction with chromatic edge dispersion.

---

## 1. React Three Fiber (`pmndrs/react-three-fiber`)

Declarative Three.js for React. Expresses 3D objects, lighting, cameras, and materials using standard JSX.

### Installation
```bash
npm i three @react-three/fiber @react-three/drei
npm i -D @types/three
```

### House Rules
- **Always use `frameloop="demand"` for UI elements.** The GPU will idle at 0% when the scene is static, rendering only when state or interaction invalidates the frame.
- **Cap pixel ratio:** Set `dpr={[1, 1.5]}` on `<Canvas>` to prevent GPU thermal throttling on high-DPI displays.
- **Wrap in Suspense:** Always provide a clean skeleton or fallback while 3D assets/materials load.

### Component Recipe: Floating 3D Geometric Card
```tsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Float } from '@react-three/drei';

export function FloatingMeshCard() {
  return (
    <div className="w-full h-80 rounded-2xl bg-neutral-950 border border-neutral-800 overflow-hidden relative">
      <Canvas frameloop="demand" dpr={[1, 1.5]} camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1.2} />
        <Suspense fallback={null}>
          <Float speed={2} rotationIntensity={1.2} floatIntensity={1.5}>
            <mesh>
              <octahedronGeometry args={[1.2, 0]} />
              <meshStandardMaterial
                color="#6366f1"
                metalness={0.7}
                roughness={0.2}
                wireframe={false}
              />
            </mesh>
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}
```

---

## 2. Liquid Glass (`dashersw/liquid-glass-js`)

Creates physical optical glass that refracts and bends the pixels behind it, mimicking realistic lens physics with subtle chromatic aberration (red/cyan fringes along edges).

### Mechanics
- Combines backdrop blurring (`backdrop-filter: blur(...)`) with an SVG displacement filter (`feDisplacementMap` + `feTurbulence`) or custom WebGL shader.
- Warps background content based on element curvature and cursor position.

### Component Recipe: Refractive Glass Panel
```tsx
import React from 'react';

export function LiquidGlassCard({ children, className = '' }) {
  return (
    <div className="relative group">
      {/* Hidden SVG displacement filter for optical refraction */}
      <svg className="hidden">
        <defs>
          <filter id="liquid-glass-refract" x="0%" y="0%" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>

      <div
        className={`relative overflow-hidden rounded-2xl border border-white/15 bg-white/5 backdrop-blur-2xl shadow-2xl transition-all duration-200 active:scale-[0.98] ${className}`}
        style={{
          boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.2), 0 20px 40px rgba(0, 0, 0, 0.4)',
        }}
      >
        {/* Prismatic edge highlight */}
        <div className="pointer-events-none absolute inset-0 rounded-2xl border border-indigo-500/20 mix-blend-overlay" />
        {children}
      </div>
    </div>
  );
}
```
- **Constraint:** Never stack two translucent refractive layers on top of each other (causes legibility collapse).
- **Fallback:** On unsupported browsers or low-power devices, degrades gracefully to `backdrop-filter: blur(20px)`.

---

## 3. Shader Meshes & 2D Compute Shaders: Route to `vgpu`

For 2D ambient fluid mesh backgrounds, dynamic plasma shaders, audio visualizers, or particle simulations, **do not load Three.js**:
- Route directly to [`.agents/skills/vgpu`](../vgpu/SKILL.md).
- Uses `vercel-labs/vgpu` (~25KB gzipped vs ~250KB Three.js).
- Native typed WGSL shaders with zero CPU overhead.
- Deterministic headless CI testing via `@vgpu/adapter-mock` (zero GPU hardware required in CI).
- Mandatory mobile fallback: guards against missing `navigator.gpu` on older phones (iOS $\le 17$, older Android).

---

## 5. Non-Negotiable Performance & Safety Invariants

| Category | House Law |
|---|---|
| **GPU Invariant** | Always cap canvas resolution with `dpr={[1, 1.5]}`. Never run unbounded `dpr={window.devicePixelRatio}`. |
| **Battery Invariant** | Use `frameloop="demand"` on R3F canvases. The canvas must not draw when static. |
| **Viewport Pause** | Use an `IntersectionObserver` to halt requestAnimationFrame when the canvas scrolls out of view. |
| **Accessibility Gate** | Always honor `@media (prefers-reduced-motion: reduce)`: replace dynamic shaders with static CSS linear gradients. |
| **Text Legibility** | Never place body text directly over moving high-frequency shader noise. Always place high-opacity backing cards (`bg-neutral-950/75`) between text and shaders. |
