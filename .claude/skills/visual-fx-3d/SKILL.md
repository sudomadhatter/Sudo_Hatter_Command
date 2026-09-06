---
name: visual-fx-3d
description: Modern 3D scenes, WebGL shaders, refractive liquid glass, and fluid physical materials. Covers React Three Fiber (R3F), ShaderGradient, Liquid Glass, and Liquid Logo.
---

# Visual FX & 3D Materials

The house engine for high-end modern visual craft: spatial 3D scenes, fluid animated gradient meshes, optical refractive glass, and organic liquid typography.

This skill integrates four foundational open-source toolkits:
1. **React Three Fiber (R3F)** (`pmndrs/react-three-fiber`): Declarative 3D scene graphs in React.
2. **Liquid Glass** (`dashersw/liquid-glass-js`): Apple VisionOS-grade physical optical glass refraction with chromatic edge dispersion.
3. **ShaderGradient** (`ruucm/shadergradient`): Fluid 3D animated gradient mesh backgrounds.
4. **Liquid Logo** (`collidingScopes/liquid-logo`): Real-time liquid metal and plasma shaders for brand marks and typography.

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

## 3. ShaderGradient (`ruucm/shadergradient`)

Fluid 3D animated gradient mesh backgrounds powered by Three.js and custom WebGL shaders.

### Installation
```bash
npm i @shadergradient/react @react-three/fiber three three-stdlib camera-controls
npm i -D @types/three
```

### Component Recipe: Atmospheric Background
```tsx
import React from 'react';
import { ShaderGradientCanvas, ShaderGradient } from '@shadergradient/react';

export function AmbientBackground() {
  return (
    <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none opacity-85">
      <ShaderGradientCanvas dpr={[1, 1.5]}>
        <ShaderGradient
          control="props"
          type="waterPlane"
          color1="#1e1b4b"
          color2="#312e81"
          color3="#09090b"
          uSpeed={0.2}
          uStrength={1.2}
          uDensity={1.1}
          grain="on"
          lightType="3d"
          brightness={1.0}
        />
      </ShaderGradientCanvas>
    </div>
  );
}
```
- **Performance Rule:** Keep `uSpeed` low ($\le 0.3$) for background ambiance. Fast animations distract users from reading content.

---

## 4. Liquid Logo (`collidingScopes/liquid-logo`)

Real-time liquid metal and plasma shaders that follow the contours of an uploaded SVG logo or icon mask.

### Mechanics
- Renders an organic plasma distortion shader into an HTML5 `<canvas>`.
- Samples the alpha channel of the logo so fluid ripples and metallic specular highlights stay tightly contained within the brand mark's silhouette.

### Component Recipe: Liquid Metal Brand Mark
```tsx
import React, { useEffect, useRef } from 'react';

export function LiquidLogo({ maskSrc, width = 120, height = 40 }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frameId: number;
    let t = 0;
    const img = new Image();
    img.src = maskSrc;

    img.onload = () => {
      const render = () => {
        t += 0.02;
        // Plasma math inside canvas context
        ctx.clearRect(0, 0, width, height);
        // Draw fluid pattern masked to logo image
        ctx.drawImage(img, 0, 0, width, height);
        ctx.globalCompositeOperation = 'source-in';
        const grad = ctx.createLinearGradient(0, 0, width * Math.cos(t), height * Math.sin(t));
        grad.addColorStop(0, '#818cf8');
        grad.addColorStop(0.5, '#c084fc');
        grad.addColorStop(1, '#38bdf8');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);
        ctx.globalCompositeOperation = 'source-over';

        frameId = requestAnimationFrame(render);
      };
      render();
    };

    return () => cancelAnimationFrame(frameId);
  }, [maskSrc, width, height]);

  return <canvas ref={canvasRef} width={width} height={height} className="cursor-pointer" />;
}
```

---

## 5. Non-Negotiable Performance & Safety Invariants

| Category | House Law |
|---|---|
| **GPU Invariant** | Always cap canvas resolution with `dpr={[1, 1.5]}`. Never run unbounded `dpr={window.devicePixelRatio}`. |
| **Battery Invariant** | Use `frameloop="demand"` on R3F canvases. The canvas must not draw when static. |
| **Viewport Pause** | Use an `IntersectionObserver` to halt requestAnimationFrame when the canvas scrolls out of view. |
| **Accessibility Gate** | Always honor `@media (prefers-reduced-motion: reduce)`: replace dynamic shaders with static CSS linear gradients. |
| **Text Legibility** | Never place body text directly over moving high-frequency shader noise. Always place high-opacity backing cards (`bg-neutral-950/75`) between text and shaders. |
