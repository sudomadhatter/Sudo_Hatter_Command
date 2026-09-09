---
name: visual-fx-3d
description: Declarative 3D scenes, spatial models, gltfjsx pipeline, interactive spring tilt cards, physical optical glass, and real-time physics. Complete Poimandres (pmndrs) suite covering React Three Fiber (R3F), Drei, Postprocessing, and Rapier. For 2D/compute shaders and ambient fluid meshes, see vgpu.
---

# Visual FX & 3D Spatial Materials ([`pmndrs/react-three-fiber`](https://github.com/pmndrs/react-three-fiber) Suite)

The house engine for high-end modern 3D spatial craft: declarative 3D scene graphs, glTF/GLB product models, tactile spring-damped tilt physics, Apple VisionOS-grade physical optical glass refraction, cinematic post-processing, and real-time rigid body physics.

> **Architecture Note:** Ambient fluid mesh backgrounds, 2D canvas shaders, and plasma noise have migrated to [`.agents/skills/vgpu`](../vgpu/SKILL.md). `visual-fx-3d` is dedicated to spatial 3D geometry, interactive 3D models, physical transmission materials, and real-time physics.

### Deep Reference Documentation
* **Component & Tool Encyclopedia:** [`CATALOG.md`](./CATALOG.md) (All 8 domains, 100+ components, imports, and props)
* **Working Implementation Recipes:** [`RECIPES.md`](./RECIPES.md) (Copy-pasteable code examples for each tool category)

---

## 1. Architectural Role & Distinction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VISUAL FX & GRAPHICS DUAL ENGINE                       │
├─────────────────────────────────────────┬───────────────────────────────────┤
│ 1. WEBGPU SHADER ENGINE (vgpu)          │ 2. 3D SPATIAL SCENES (visual-fx-3d)│
├─────────────────────────────────────────┼───────────────────────────────────┤
│ • Fullscreen ambient fluid meshes       │ • Declarative 3D scene graphs     │
│ • Interactive plasma & ripples          │ • glTF / GLB product models       │
│ • Audio-reactive visualizers            │ • Spatial lighting & camera rigs  │
│ • GPU particle simulations              │ • Optical physical glass (Drei)   │
│ • ~25KB gzipped bundle (typed WGSL)     │ • Interactive spring tilt cards   │
│ • Zero-GPU headless CI testable         │ • Cinematic post-processing passes│
│                                         │ • Real-time physics (Rapier)      │
│                                         │ • Full Poimandres Creative Suite  │
└─────────────────────────────────────────┴───────────────────────────────────┘
```

> **House Rule:** Use `vgpu` for 2D surface shaders, fluid backdrops, and compute passes. Use `visual-fx-3d` strictly when rendering actual 3D spatial geometry, glTF models, optical glass, or 3D physics.

---

## 2. Installation & Ecosystem Stack

Integrate the official **Poimandres (`pmndrs`)** toolkit:
* [`pmndrs/react-three-fiber`](https://github.com/pmndrs/react-three-fiber) — Core React Three.js renderer
* [`pmndrs/drei`](https://github.com/pmndrs/drei) — Abstractions, controls, staging, and shaders
* [`pmndrs/postprocessing`](https://github.com/pmndrs/postprocessing) — Cinematic bloom, DoF, and chromatic aberration
* [`pmndrs/react-three-rapier`](https://github.com/pmndrs/react-three-rapier) — Real-time WebAssembly physics
* [`pmndrs/gltfjsx`](https://github.com/pmndrs/gltfjsx) — JSX asset pipeline for 3D `.glb` models
* [`pmndrs/leva`](https://github.com/pmndrs/leva) — Live in-browser parameter tweak GUI

```bash
# Core 3D engine and production helpers
npm i three @react-three/fiber @react-three/drei

# Optional cinematic post-processing & physics
npm i @react-three/postprocessing postprocessing @react-three/rapier leva

# TypeScript definitions and glTF JSX compiler
npm i -D @types/three gltfjsx
```

---

## 3. The `gltfjsx` 3D Asset Pipeline

Never manually write imperative loaders for 3D meshes. Use `gltfjsx` to compile `.glb` / `.gltf` models into clean, declarative, typed React components with Draco compression:

```bash
# Compile and optimize 3D model into a typed React component
npx gltfjsx public/models/product.glb --transform --types -o src/components/3d/ProductModel.tsx
```

### Clean Consumption Pattern
```tsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Center, Environment } from '@react-three/drei';
import { ProductModel } from './ProductModel';

export function ProductViewer() {
  return (
    <div className="w-full h-96 relative">
      <Canvas frameloop="demand" dpr={[1, 1.5]} camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <Suspense fallback={null}>
          <Center>
            <ProductModel scale={1.2} />
          </Center>
          <Environment preset="city" />
        </Suspense>
      </Canvas>
    </div>
  );
}
```

---

## 4. Component Recipe: Tactile 3D Spring Tilt Card

A tactile 3D card utilizing `@react-three/drei`'s `<PresentationControls>` with Apple 2-parameter spring physics, floating momentum, and dynamic ground contact shadows.

```tsx
'use client';

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { PresentationControls, Float, ContactShadows } from '@react-three/drei';

export function SpatialTiltCard({ children }: { children?: React.ReactNode }) {
  return (
    <div className="relative w-full h-80 rounded-3xl bg-neutral-950 border border-white/10 overflow-hidden shadow-2xl">
      <Canvas
        frameloop="demand"
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 5], fov: 45 }}
        className="touch-none"
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[8, 8, 4]} intensity={1.4} />

        <Suspense fallback={null}>
          {/* Spring-damped presentation controls: responsive tilt on touch & mouse */}
          <PresentationControls
            global={false}
            snap={{ mass: 1, tension: 170, friction: 26 }}
            rotation={[0, 0, 0]}
            polar={[-0.25, 0.25]}
            azimuth={[-0.4, 0.4]}
          >
            <Float speed={2} rotationIntensity={0.6} floatIntensity={1.0}>
              <mesh>
                <boxGeometry args={[2.6, 1.6, 0.2]} />
                <meshStandardMaterial
                  color="#4f46e5"
                  metalness={0.6}
                  roughness={0.2}
                />
              </mesh>
            </Float>
          </PresentationControls>

          <ContactShadows position={[0, -1.4, 0]} opacity={0.4} scale={8} blur={2.5} />
        </Suspense>
      </Canvas>

      {children && (
        <div className="pointer-events-none absolute inset-0 p-6 flex flex-col justify-end">
          {children}
        </div>
      )}
    </div>
  );
}
```

---

## 5. Component Recipe: Physical Optical Glass (`MeshTransmissionMaterial`)

Replaces synthetic 2D SVG filter hacks with true Apple VisionOS-grade physical optical glass: light transmission, chromatic edge dispersion, internal roughness, and refraction index ($IOR$).

```tsx
'use client';

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { MeshTransmissionMaterial, Float } from '@react-three/drei';

export function OpticalGlassPill() {
  return (
    <div className="w-full h-80 relative rounded-3xl bg-neutral-950 overflow-hidden border border-white/10">
      <Canvas frameloop="demand" dpr={[1, 1.5]} camera={{ position: [0, 0, 4.5], fov: 45 }}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} />

        <Suspense fallback={null}>
          <Float speed={1.8} rotationIntensity={0.8} floatIntensity={1.2}>
            {/* Background spatial accent mesh being refracted */}
            <mesh position={[0.4, 0.2, -1]}>
              <sphereGeometry args={[0.8, 32, 32]} />
              <meshStandardMaterial color="#ec4899" roughness={0.1} metalness={0.8} />
            </mesh>

            {/* Foreground Physical Optical Glass Slab */}
            <mesh position={[0, 0, 0]}>
              <capsuleGeometry args={[0.7, 1.2, 16, 32]} />
              <MeshTransmissionMaterial
                backside
                samples={10}
                resolution={512}
                thickness={0.5}
                roughness={0.12}
                ior={1.52}
                chromaticAberration={0.08}
                anisotropy={0.15}
                distortion={0.25}
                distortionScale={0.3}
                temporalDistortion={0.1}
                color="#ffffff"
              />
            </mesh>
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}
```

### Optical Parameters Reference
* `ior`: Index of refraction (Glass is typically `1.5` to `1.54`).
* `thickness`: Physical depth of the optical medium creating depth parallax.
* `chromaticAberration`: Prismatic separation of RGB wavelengths along curved glass edges.
* `anisotropy`: Directional stretching of refracted highlights.
* `roughness`: Micro-surface dispersion (frosted vs crystalline finish).

---

## 6. Component Recipe: DOM Pinning in 3D Space (`<Html>`)

Pins standard HTML / React DOM components (badges, buttons, metric tags) to exact 3D coordinates inside the scene graph:

```tsx
import { Html } from '@react-three/drei';

export function AnnotatedSpatialNode({ position, label }: { position: [number, number, number]; label: string }) {
  return (
    <mesh position={position}>
      <sphereGeometry args={[0.1, 16, 16]} />
      <meshBasicMaterial color="#6366f1" />
      <Html distanceFactor={8} center position={[0, 0.25, 0]}>
        <div className="px-2.5 py-1 rounded-full bg-neutral-900/90 border border-white/20 text-xs font-medium text-white shadow-xl backdrop-blur-md whitespace-nowrap">
          {label}
        </div>
      </Html>
    </mesh>
  );
}
```

---

## 7. Non-Negotiable Performance & Safety Invariants

| Invariant | Law | Enforcement |
|---|---|---|
| **Demand-Driven Render** | Canvas MUST use `frameloop="demand"`. Idle GPU usage must be 0%. | Redraw only on interaction by calling `useThree((state) => state.invalidate)`. |
| **Capped Pixel Ratio** | Canvas MUST set `dpr={[1, 1.5]}`. Never unbounded `window.devicePixelRatio`. | Prevents GPU thermal throttling on mobile and 4K/Retina displays. |
| **Viewport Pause** | Canvas MUST halt rendering when scrolled out of viewport. | Wrap Canvas container with an `IntersectionObserver` that toggles rendering. |
| **Resource Disposal** | Never leak GPU geometries, materials, or textures. | Standard R3F automatic unmount cleanup; dispose manual textures/materials. |
| **Reduced Motion** | Always respect `@media (prefers-reduced-motion: reduce)`. | Disable `<Float>` and continuous rotations; render static camera posture. |
| **Mobile-First Touch** | Ensure `<Canvas>` handles touch gestures cleanly. | Add `touch-none` CSS class to Canvas container to prevent scroll interference. |
