# Poimandres (`pmndrs`) 3D Production Recipes

Production-ready, copy-pasteable React component recipes covering the 8 core tools and capabilities of the **Poimandres (`pmndrs`)** 3D ecosystem.

---

## 1. Core Canvas & Interactive Mesh (`@react-three/fiber`)

A self-contained interactive 3D box with hover animations, pointer events, and on-demand battery-conserving render loop.

```tsx
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import type * as THREE from 'three';

interface InteractiveBoxProps {
  position: [number, number, number];
  color?: string;
  hoverColor?: string;
}

export function InteractiveBox({ position, color = '#4f46e5', hoverColor = '#ec4899' }: InteractiveBoxProps) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const [hovered, setHovered] = useState(false);
  const [active, setActive] = useState(false);

  // Rotate gently on render-loop
  useFrame((_, delta) => {
    meshRef.current.rotation.x += delta * 0.5;
    meshRef.current.rotation.y += delta * 0.7;
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      scale={active ? 1.4 : 1}
      onClick={(e) => {
        e.stopPropagation();
        setActive(!active);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial
        color={hovered ? hoverColor : color}
        roughness={0.2}
        metalness={0.8}
      />
    </mesh>
  );
}

export function BasicScene() {
  return (
    <div style={{ width: '100%', height: '400px', background: '#09090b' }}>
      <Canvas
        frameloop="demand"
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 4], fov: 50 }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={1.5} />
        <InteractiveBox position={[0, 0, 0]} />
      </Canvas>
    </div>
  );
}
```

---

## 2. Product Studio Staging with HDR Lighting (`@react-three/drei`)

Photorealistic product presentation with zero-config HDRI studio lighting, soft floor contact shadows, and organic floating.

```tsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stage, Float, ContactShadows, Environment, Center } from '@react-three/drei';

function ProductMesh() {
  return (
    <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh castShadow receiveShadow>
        <torusKnotGeometry args={[0.8, 0.28, 128, 32]} />
        <meshStandardMaterial
          color="#10b981"
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>
    </Float>
  );
}

export function ProductStage() {
  return (
    <div style={{ width: '100%', height: '500px', borderRadius: '16px', overflow: 'hidden' }}>
      <Canvas
        frameloop="demand"
        dpr={[1, 1.5]}
        camera={{ position: [0, 1, 4], fov: 45 }}
        shadows
      >
        <Suspense fallback={null}>
          {/* Preset HDRI environment for instant reflections */}
          <Environment preset="city" />

          {/* Automatic centering and lighting */}
          <Center top>
            <ProductMesh />
          </Center>

          {/* Clean soft contact shadows on the ground */}
          <ContactShadows
            position={[0, 0, 0]}
            opacity={0.65}
            scale={8}
            blur={2.5}
            far={4}
            color="#000000"
          />
        </Suspense>
      </Canvas>
    </div>
  );
}
```

---

## 3. Scroll-Driven 3D Storytelling (`@react-three/drei` `ScrollControls`)

Apple-style storytelling where standard page scrolling drives 3D object rotation, position, and camera animation.

```tsx
import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { ScrollControls, useScroll, Float } from '@react-three/drei';
import type * as THREE from 'three';

function ScrolledModel() {
  const meshRef = useRef<THREE.Mesh>(null!);
  const scroll = useScroll();

  useFrame(() => {
    // offset runs from 0 (top of page) to 1 (bottom of page)
    const progress = scroll.offset;

    // Continuous smooth rotation driven by scroll position
    meshRef.current.rotation.y = progress * Math.PI * 4;
    meshRef.current.rotation.x = Math.sin(progress * Math.PI) * 0.5;

    // Move model across X axis during scroll
    meshRef.current.position.x = (progress - 0.5) * 3;
  });

  return (
    <Float speed={2}>
      <mesh ref={meshRef}>
        <octahedronGeometry args={[1.5, 0]} />
        <meshNormalMaterial wireframe={false} />
      </mesh>
    </Float>
  );
}

export function ScrollStorytelling() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas frameloop="demand" dpr={[1, 1.5]}>
        {/* pages={3} creates 3 full viewport heights of virtual scrollable space */}
        <ScrollControls pages={3} damping={0.25}>
          <ScrolledModel />
        </ScrollControls>
      </Canvas>
    </div>
  );
}
```

---

## 4. Apple VisionOS Physical Optical Glass (`MeshTransmissionMaterial`)

Physical glass with real optical thickness, light transmission, surface roughness, and chromatic edge dispersion.

```tsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { MeshTransmissionMaterial, Float, Environment, Text } from '@react-three/drei';

function GlassBadge() {
  return (
    <group>
      {/* Background 3D element visible through the glass */}
      <mesh position={[0, 0, -1]}>
        <sphereGeometry args={[0.9, 32, 32]} />
        <meshStandardMaterial color="#f97316" roughness={0.1} />
      </mesh>

      {/* Front Optical Glass Panel */}
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.3}>
        <mesh position={[0, 0, 0.5]}>
          <roundedBoxGeometry args={[2.4, 1.4, 0.1, 8, 0.05]} />
          <MeshTransmissionMaterial
            backside={false}
            samples={16}
            resolution={512}
            transmission={1.0}
            roughness={0.12}
            thickness={0.6}
            ior={1.35}
            chromaticAberration={0.06}
            anisotropy={0.3}
            distortion={0.15}
            distortionScale={0.3}
            temporalDistortion={0.05}
            color="#ffffff"
          />
        </mesh>

        <Text
          position={[0, 0, 0.6]}
          fontSize={0.22}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          VISION OS GLASS
        </Text>
      </Float>
    </group>
  );
}

export function PhysicalGlassScene() {
  return (
    <div style={{ width: '100%', height: '450px', background: '#18181b' }}>
      <Canvas frameloop="demand" dpr={[1, 1.5]} camera={{ position: [0, 0, 3.5], fov: 45 }}>
        <Suspense fallback={null}>
          <Environment preset="studio" />
          <GlassBadge />
        </Suspense>
      </Canvas>
    </div>
  );
}
```

---

## 5. Spatial UI: Pinning HTML Buttons into 3D (`@react-three/drei` `<Html>`)

Seamlessly pin native interactive HTML/CSS UI components (tooltips, buttons, cards) onto 3D coordinates.

```tsx
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Html, PresentationControls } from '@react-three/drei';
import type * as THREE from 'three';

function CardWithPinnedUI() {
  const meshRef = useRef<THREE.Mesh>(null!);
  const [likes, setLikes] = useState(0);

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2.8, 0.1]} />
      <meshStandardMaterial color="#27272a" roughness={0.4} metalness={0.2} />

      {/* Pinned interactive HTML element */}
      <Html
        position={[0, -0.9, 0.08]}
        center
        transform
        distanceFactor={6}
      >
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '8px',
          padding: '8px 16px',
          display: 'flex',
          gap: '8px',
          alignItems: 'center',
          color: 'white',
          fontFamily: 'sans-serif',
          fontSize: '13px',
          userSelect: 'none'
        }}>
          <span>Likes: {likes}</span>
          <button
            onClick={() => setLikes((prev) => prev + 1)}
            style={{
              background: '#6366f1',
              border: 'none',
              borderRadius: '4px',
              color: 'white',
              padding: '4px 8px',
              cursor: 'pointer'
            }}
          >
            +1
          </button>
        </div>
      </Html>
    </mesh>
  );
}

export function SpatialUIScene() {
  return (
    <div style={{ width: '100%', height: '450px' }}>
      <Canvas frameloop="demand" dpr={[1, 1.5]}>
        <ambientLight intensity={0.7} />
        <PresentationControls snap speed={1.5} polar={[-0.3, 0.3]} azimuth={[-0.5, 0.5]}>
          <CardWithPinnedUI />
        </PresentationControls>
      </Canvas>
    </div>
  );
}
```

---

## 6. Cinematic Post-Processing Pipeline (`@react-three/postprocessing`)

Adds bloom, lens depth-of-field blur, and subtle chromatic aberration to give 3D scenes a polished cinematic finish.

```tsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Float, Environment } from '@react-three/drei';
import {
  EffectComposer,
  Bloom,
  DepthOfField,
  ChromaticAberration,
  Vignette
} from '@react-three/postprocessing';
import * as THREE from 'three';

function GlowingCrystal() {
  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={1}>
      <mesh>
        <octahedronGeometry args={[1.2, 0]} />
        {/* Emissive intensity triggers the bloom threshold */}
        <meshStandardMaterial
          color="#06b6d4"
          emissive="#06b6d4"
          emissiveIntensity={2.5}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>
    </Float>
  );
}

export function CinematicScene() {
  return (
    <div style={{ width: '100%', height: '500px', background: '#000000' }}>
      <Canvas frameloop="demand" dpr={[1, 1.5]} camera={{ position: [0, 0, 4], fov: 50 }}>
        <Suspense fallback={null}>
          <Environment preset="night" />
          <GlowingCrystal />

          {/* Post-processing effect stack */}
          <EffectComposer multisampling={4}>
            {/* Soft bloom triggered by emissive elements */}
            <Bloom
              intensity={1.2}
              luminanceThreshold={0.8}
              luminanceSmoothing={0.3}
              mipmapBlur
            />
            {/* Film camera lens blur */}
            <DepthOfField
              focusDistance={0.02}
              focalLength={0.5}
              bokehScale={2.5}
            />
            {/* Edge prism color separation */}
            <ChromaticAberration
              offset={new THREE.Vector2(0.002, 0.002)}
              radialModulation
              modulationOffset={0.4}
            />
            {/* Lens edge focus */}
            <Vignette offset={0.3} darkness={0.65} />
          </EffectComposer>
        </Suspense>
      </Canvas>
    </div>
  );
}
```

---

## 7. Real-Time Rigid Body Physics (`@react-three/rapier`)

Interactive physical simulation with gravity, bouncy collisions, and rigid body dynamics.

```tsx
import React from 'react';
import { Canvas } from '@react-three/fiber';
import { Physics, RigidBody, CuboidCollider } from '@react-three/rapier';

function FallingSpheres() {
  const count = 12;
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <RigidBody
          key={i}
          position={[
            (Math.random() - 0.5) * 2,
            3 + i * 0.8,
            (Math.random() - 0.5) * 2
          ]}
          restitution={0.7} // High bounciness
          colliders="ball"
        >
          <mesh castShadow>
            <sphereGeometry args={[0.25, 24, 24]} />
            <meshStandardMaterial
              color={i % 2 === 0 ? '#3b82f6' : '#ec4899'}
              roughness={0.2}
              metalness={0.5}
            />
          </mesh>
        </RigidBody>
      ))}
    </>
  );
}

export function PhysicsScene() {
  return (
    <div style={{ width: '100%', height: '500px', background: '#09090b' }}>
      <Canvas shadows camera={{ position: [0, 3, 6], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} castShadow />

        <Physics gravity={[0, -9.81, 0]}>
          {/* Static Floor */}
          <RigidBody type="fixed" position={[0, -1, 0]} restitution={0.5}>
            <mesh receiveShadow>
              <boxGeometry args={[10, 0.2, 10]} />
              <meshStandardMaterial color="#18181b" />
            </mesh>
          </RigidBody>

          {/* Dynamic falling bouncy balls */}
          <FallingSpheres />
        </Physics>
      </Canvas>
    </div>
  );
}
```

---

## 8. Live Parameter Dials in the Browser (`leva` `useControls`)

Slide-out control panel enabling live real-time visual tweaking with the operator during design review.

```tsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { MeshTransmissionMaterial, Float, Environment } from '@react-three/drei';
import { useControls } from 'leva';

function TunableGlass() {
  // Live dials rendered into an in-browser GUI panel
  const config = useControls('Glass Material Dials', {
    transmission: { value: 1.0, min: 0.0, max: 1.0, step: 0.05 },
    roughness: { value: 0.15, min: 0.0, max: 1.0, step: 0.01 },
    ior: { value: 1.3, min: 1.0, max: 2.5, step: 0.05 },
    thickness: { value: 0.5, min: 0.0, max: 2.0, step: 0.1 },
    chromaticAberration: { value: 0.05, min: 0.0, max: 0.3, step: 0.01 },
    distortion: { value: 0.2, min: 0.0, max: 1.0, step: 0.05 },
    color: '#ffffff',
  });

  return (
    <Float speed={1.5}>
      <mesh>
        <torusGeometry args={[1, 0.35, 32, 64]} />
        <MeshTransmissionMaterial {...config} />
      </mesh>
    </Float>
  );
}

export function TunableScene() {
  return (
    <div style={{ width: '100%', height: '500px' }}>
      <Canvas frameloop="demand" dpr={[1, 1.5]}>
        <Suspense fallback={null}>
          <Environment preset="city" />
          <TunableGlass />
        </Suspense>
      </Canvas>
    </div>
  );
}
```
