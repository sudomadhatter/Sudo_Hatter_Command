---
name: vgpu
description: High-performance WebGPU shader engine using typed WGSL modules, fullscreen effect passes, GPU compute, audio-reactive ripples, and particle simulations. Official Vercel Labs vgpu toolkit with zero-GPU headless CI test adapters and mandatory mobile fallback.
---

# WebGPU Shader & Compute Engine (`vercel-labs/vgpu`)

The house engine for next-generation WebGPU visual effects: typed WGSL shaders, fullscreen ambient mesh backgrounds, interactive fluid ripples, particle simulations, and high-throughput GPU compute.

Integrated from Vercel Labs' [`vercel-labs/vgpu`](https://github.com/vercel-labs/vgpu).

---

## 1. Architectural Role & Distinction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VISUAL FX & GRAPHICS DUAL ENGINE                       │
├─────────────────────────────────────────┬───────────────────────────────────┤
│ 1. WEBGPU SHADER ENGINE (vgpu)          │ 2. 3D SPATIAL SCENES (visual-fx-3d│
├─────────────────────────────────────────┼───────────────────────────────────┤
│ • Fullscreen ambient fluid meshes       │ • Declarative 3D scene graphs     │
│ • Interactive plasma & ripples          │ • glTF / GLB product models       │
│ • Audio-reactive visualizers            │ • Spatial lighting & camera rigs  │
│ • GPU particle simulations              │ • Optical liquid glass refraction │
│ • ~25KB gzipped bundle                  │ • React Three Fiber (R3F) & Drei  │
│ • Zero-GPU headless CI testable         │ • ~250KB+ bundle (spatial engine) │
└─────────────────────────────────────────┴───────────────────────────────────┘
```

> **House Rule:** Use `vgpu` for 2D surface shaders, fluid backdrops, and compute passes. Use `visual-fx-3d` strictly when rendering actual 3D spatial geometry, glTF models, or optical refraction panels.

---

## 2. Installation & Ecosystem

```bash
# Core WebGPU toolkit
npm i vgpu

# Headless adapters for CI/CD tests and server-side execution
npm i -D @vgpu/adapter-mock @vgpu/adapter-node
```

---

## 3. Mobile-First Safety & Graceful Fallback Invariant

> **AVCH-133 Invariant:** WebGPU is supported on modern desktop browsers (Chrome 113+, Edge 113+, Safari 18+) and iOS 18+. Older devices, Safari on iOS $\le 17$, older Android handsets, and default Linux Firefox **do not support WebGPU**.
> 
> ⛔ **NEVER instantiate a WebGPU canvas without guarding `navigator.gpu`.** If `navigator.gpu` is undefined or initialization rejects, you MUST gracefully degrade to a high-performance CSS gradient or static SVG background. Never display a blank rectangle or crash the render tree.

### The Standard Guard Pattern
```tsx
import React, { useEffect, useState } from 'react';

export function useWebGPUSupport(): boolean {
  const [supported, setSupported] = useState<boolean>(false);

  useEffect(() => {
    if (typeof navigator !== 'undefined' && 'gpu' in navigator && navigator.gpu) {
      navigator.gpu.requestAdapter().then((adapter) => {
        setSupported(Boolean(adapter));
      }).catch(() => {
        setSupported(false);
      });
    } else {
      setSupported(false);
    }
  }, []);

  return supported;
}
```

---

## 4. Component Recipe: Fullscreen Fluid Ambient Mesh

A responsive, battery-conscious background mesh using typed WGSL shaders with automatic CSS gradient fallback.

```tsx
'use client';

import React, { useEffect, useRef, useState } from 'react';

const SHADER_WGSL = /* wgsl */ `
struct Uniforms {
  time: f32,
  width: f32,
  height: f32,
  speed: f32,
};

@group(0) @binding(0) var<uniform> u: Uniforms;

struct VertexOutput {
  @builtin(position) position: vec4f,
  @location(0) uv: vec2f,
};

@vertex
fn vs_main(@builtin(vertex_index) vertex_index: u32) -> VertexOutput {
  var pos = array<vec2f, 6>(
    vec2f(-1.0, -1.0), vec2f(1.0, -1.0), vec2f(-1.0, 1.0),
    vec2f(-1.0, 1.0), vec2f(1.0, -1.0), vec2f(1.0, 1.0)
  );
  var out: VertexOutput;
  out.position = vec4f(pos[vertex_index], 0.0, 1.0);
  out.uv = pos[vertex_index] * 0.5 + 0.5;
  return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
  let uv = in.uv;
  let t = u.time * u.speed * 0.3;
  
  // Ambient fluid sinusoidal harmonic waves
  let wave1 = sin(uv.x * 3.0 + t) * cos(uv.y * 2.0 + t * 0.5);
  let wave2 = cos(uv.x * 2.5 - t * 0.8) * sin(uv.y * 3.5 + t);
  let fluid = (wave1 + wave2) * 0.5 + 0.5;

  let colorA = vec3f(0.04, 0.04, 0.08); // Deep obsidian
  let colorB = vec3f(0.24, 0.18, 0.55); // Indigo twilight
  let colorC = vec3f(0.08, 0.42, 0.65); // Teal luminescence

  let mixed = mix(colorA, colorB, fluid);
  let final_color = mix(mixed, colorC, uv.y * 0.4 + wave1 * 0.2);

  return vec4f(final_color, 0.85);
}
`;

export function AmbientFluidMesh() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [gpuAvailable, setGpuAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    if (typeof navigator === 'undefined' || !navigator.gpu) {
      setGpuAvailable(false);
      return;
    }

    let animationFrameId: number;
    let device: GPUDevice;
    let context: GPUCanvasContext;

    async function initWebGPU() {
      try {
        const adapter = await navigator.gpu.requestAdapter({ powerPreference: 'low-power' });
        if (!adapter) {
          setGpuAvailable(false);
          return;
        }

        device = await adapter.requestDevice();
        const canvas = canvasRef.current;
        if (!canvas) return;

        context = canvas.getContext('webgpu') as GPUCanvasContext;
        const format = navigator.gpu.getPreferredCanvasFormat();
        context.configure({ device, format, alphaMode: 'premultiplied' });

        const module = device.createShaderModule({ code: SHADER_WGSL });
        const pipeline = device.createRenderPipeline({
          layout: 'auto',
          vertex: { module, entryPoint: 'vs_main' },
          fragment: { module, entryPoint: 'fs_main', targets: [{ format }] },
          primitive: { topology: 'triangle-list' },
        });

        // 4 x f32 uniforms (16 bytes aligned)
        const uniformBuffer = device.createBuffer({
          size: 16,
          usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
        });

        const bindGroup = device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [{ binding: 0, resource: { buffer: uniformBuffer } }],
        });

        setGpuAvailable(true);
        let startTime = performance.now();

        const render = (now: number) => {
          const elapsed = (now - startTime) / 1000;
          const uniformData = new Float32Array([
            elapsed,
            canvas.width,
            canvas.height,
            0.5, // ambient speed scalar
          ]);
          device.queue.writeBuffer(uniformBuffer, 0, uniformData.buffer);

          const commandEncoder = device.createCommandEncoder();
          const textureView = context.getCurrentTexture().createView();
          const passEncoder = commandEncoder.beginRenderPass({
            colorAttachments: [
              {
                view: textureView,
                clearValue: { r: 0.04, g: 0.04, b: 0.08, a: 1.0 },
                loadOp: 'clear',
                storeOp: 'store',
              },
            ],
          });

          passEncoder.setPipeline(pipeline);
          passEncoder.setBindGroup(0, bindGroup);
          passEncoder.draw(6);
          passEncoder.end();

          device.queue.submit([commandEncoder.finish()]);
          animationFrameId = requestAnimationFrame(render);
        };

        animationFrameId = requestAnimationFrame(render);
      } catch {
        setGpuAvailable(false);
      }
    }

    initWebGPU();

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (device) device.destroy();
    };
  }, []);

  // Fallback view for older mobile phones or non-WebGPU browsers
  if (gpuAvailable === false) {
    return (
      <div
        className="absolute inset-0 -z-10 pointer-events-none opacity-80"
        style={{
          background: 'radial-gradient(ellipse at 50% 20%, #1e1b4b 0%, #09090b 80%)',
        }}
      />
    );
  }

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full -z-10 pointer-events-none"
      style={{ opacity: gpuAvailable ? 0.85 : 0 }}
    />
  );
}
```

---

## 5. Headless CI & Testing Invariant

Running WebGL in CI is notoriously flaky due to headless GPU driver crashes. In contrast, `vgpu` supports deterministic headless testing via `@vgpu/adapter-mock`:

```ts
import { describe, it, expect } from 'vitest';
import { createMockAdapter } from '@vgpu/adapter-mock';

describe('WebGPU Shaders in CI', () => {
  it('initializes GPU device and validates pipeline compilation without hardware', async () => {
    const mockAdapter = createMockAdapter();
    const device = await mockAdapter.requestDevice();
    
    expect(device).toBeDefined();

    const shaderModule = device.createShaderModule({
      code: /* wgsl */ `
        @vertex fn vs() -> @builtin(position) vec4f {
          return vec4f(0.0, 0.0, 0.0, 1.0);
        }
        @fragment fn fs() -> @location(0) vec4f {
          return vec4f(1.0, 0.0, 0.0, 1.0);
        }
      `,
    });

    expect(shaderModule).toBeDefined();
  });
});
```

---

## 6. Pre-Flight Checklist for WebGPU Features

Before shipping any `vgpu` feature:
- [ ] **Mobile Fallback Present:** `navigator.gpu` guarded with zero-crash CSS/SVG fallback.
- [ ] **Battery/Power Preference:** `requestAdapter({ powerPreference: 'low-power' })` specified.
- [ ] **Clean Destruction:** `device.destroy()` called in component cleanup unmount hook.
- [ ] **Capped Pixel Ratio:** Set canvas width/height scaled by `Math.min(window.devicePixelRatio, 1.5)` to avoid mobile thermal throttling.
- [ ] **Accessibility:** Check `@media (prefers-reduced-motion: reduce)` to pause or freeze the animation loop.

