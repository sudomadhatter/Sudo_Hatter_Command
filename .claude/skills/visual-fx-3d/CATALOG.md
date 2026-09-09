# Poimandres (`pmndrs`) 3D Tool & Component Catalog

A comprehensive encyclopedia of tools, components, hooks, and helpers across the **Poimandres (`pmndrs`)** 3D ecosystem for React Three Fiber. Grouped into 8 architectural domains.

---

## Ecosystem Package Directory

| Package | Purpose | Installation | Repository |
|---|---|---|---|
| **`@react-three/fiber`** | Core React renderer for Three.js | `npm i three @types/three @react-three/fiber` | [`pmndrs/react-three-fiber`](https://github.com/pmndrs/react-three-fiber) |
| **`@react-three/drei`** | Ready-made helpers, controls, shaders & staging | `npm i @react-three/drei` | [`pmndrs/drei`](https://github.com/pmndrs/drei) |
| **`@react-three/postprocessing`** | Cinematic post-processing effects pipeline | `npm i @react-three/postprocessing postprocessing` | [`pmndrs/postprocessing`](https://github.com/pmndrs/postprocessing) |
| **`@react-three/rapier`** | High-performance real-time rigid body physics | `npm i @react-three/rapier` | [`pmndrs/react-three-rapier`](https://github.com/pmndrs/react-three-rapier) |
| **`gltfjsx`** | CLI compiler transforming 3D `.glb` to typed React components | `npm i -D gltfjsx` | [`pmndrs/gltfjsx`](https://github.com/pmndrs/gltfjsx) |
| **`leva`** | Live GUI parameter control panel for real-time tweaking | `npm i leva` | [`pmndrs/leva`](https://github.com/pmndrs/leva) |
| **`maath`** | Math helpers, dampening, spring interpolation | `npm i maath` | [`pmndrs/maath`](https://github.com/pmndrs/maath) |

---

## 1. Core Engine & Render Loop (`@react-three/fiber`)

### `<Canvas>`
The root 3D viewport that instantiates the WebGL renderer, camera, and scene graph.
- **Import:** `import { Canvas } from '@react-three/fiber'`
- **Key Props:**
  - `frameloop="demand" | "always" | "never"`: `"demand"` only renders when state changes or invalidation occurs (mandatory for UI battery conservation).
  - `dpr={[1, 1.5]}`: Clamps pixel ratio to avoid rendering at 3x/4x on Retina screens.
  - `camera={{ position: [x, y, z], fov: 45, near: 0.1, far: 1000 }}`: Default camera setup.
  - `shadows`: Enables shadow maps across the scene.
  - `gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}`: WebGL context options.

### `useFrame((state, delta) => ...)`
Executes code on every rendered frame of the render-loop.
- **Import:** `import { useFrame } from '@react-three/fiber'`
- **Parameters:**
  - `state.clock.getElapsedTime()`: Total elapsed run time in seconds.
  - `state.camera`: Direct reference to active camera.
  - `state.pointer`: Normalized pointer coordinates `[-1, 1]`.
  - `delta`: Time in seconds between current and previous frame (use for frame-rate-independent physics and rotation).

### `useThree()`
Provides direct access to the internal Three.js state.
- **Import:** `import { useThree } from '@react-three/fiber'`
- **Returns:** `{ gl, scene, camera, size, viewport, raycaster, invalidate }`

### Pointer & Interaction Events
Native declarative pointer event handlers available on any `<mesh>`:
- `onClick={(e) => ...}`: Triggered on pointer click.
- `onPointerOver={(e) => ...}` / `onPointerOut={(e) => ...}`: Hover enter/leave.
- `onPointerDown={(e) => ...}` / `onPointerUp={(e) => ...}`: Press and release.
- `onPointerMove={(e) => ...}`: Pointer movement over mesh surface.
- `e.stopPropagation()`: Prevents the click/hover event from passing through to underlying 3D geometry.

---

## 2. Staging & Photorealistic Lighting (`@react-three/drei`)

### `<Environment>`
Loads high-dynamic-range environment maps (HDRIs) for photorealistic ambient reflections and global illumination without manual light rigging.
- **Import:** `import { Environment } from '@react-three/drei'`
- **Key Props:**
  - `preset="city" | "studio" | "sunset" | "dawn" | "night" | "warehouse" | "forest" | "apartment" | "park" | "lobby"`: Zero-config bundled HDR environment presets.
  - `files="/path/to/custom.hdr"`: Custom HDR or EXR environment map.
  - `background`: Sets the HDRI as the scene's visible background skybox.
  - `blur={0.5}`: Blurs the visible background while preserving sharp lighting reflections.

### `<Stage>`
All-in-one studio presentation wrapper. Automatically centers the child model, sets up soft ambient and directional lights, contact shadows, and an environment map.
- **Import:** `import { Stage } from '@react-three/drei'`
- **Key Props:** `intensity={0.5}`, `environment="city"`, `shadows={{ type: 'contact', opacity: 0.7 }}`, `adjustCamera={true}`.

### `<ContactShadows>`
High-performance screen/floor contact shadows calculated via an internal fast render pass without expensive cascaded depth maps.
- **Import:** `import { ContactShadows } from '@react-three/drei'`
- **Key Props:**
  - `position={[0, -1, 0]}`: Floor plane position.
  - `opacity={0.6}`: Shadow darkness.
  - `scale={10}`: Shadow spread size.
  - `blur={2}`: Shadow edge softness.
  - `resolution={512}`: Render buffer resolution.
  - `color="#000000"`: Custom tint for colored shadow diffusion.

### `<AccumulativeShadows>` & `<RandomizedLight>`
Soft, raytraced-quality contact shadows accumulated over multiple frames when static.
- **Import:** `import { AccumulativeShadows, RandomizedLight } from '@react-three/drei'`
- **Usage:** Ideal for static product showcases where photorealistic soft ground shadows are required.

### `<Float>`
Gives any 3D model or group a natural, organic floating/hovering animation without writing custom `useFrame` math.
- **Import:** `import { Float } from '@react-three/drei'`
- **Key Props:** `speed={2}`, `rotationIntensity={1}`, `floatIntensity={1}`, `floatingRange={[-0.1, 0.1]}`.

### `<Center>`
Calculates the accurate bounding box of its children and aligns them to the origin.
- **Import:** `import { Center } from '@react-three/drei'`
- **Key Props:** `top`, `bottom`, `left`, `right`, `front`, `back`.

### `<Sparkles>`
Floating ambient dust or glowing sparks.
- **Import:** `import { Sparkles } from '@react-three/drei'`
- **Key Props:** `count={50}`, `scale={4}`, `size={3}`, `speed={0.4}`, `noise={0.2}`, `color="#fff"`.

---

## 3. Camera & Viewport Controls (`@react-three/drei`)

### `<CameraControls>`
The most versatile, smooth camera manipulation tool for product inspection and animated transitions.
- **Import:** `import { CameraControls } from '@react-three/drei'`
- **Methods (via ref):**
  - `ref.current.setLookAt(eyeX, eyeY, eyeZ, targetX, targetY, targetZ, true)`: Smooth transition to a camera position.
  - `ref.current.fitToBox(meshOrBox, true)`: Frames any 3D model neatly within the viewport.
  - `ref.current.dolly(distance, true)`: Zooms in/out smoothly.

### `<ScrollControls>` & `useScroll()`
Connects standard page scroll progress directly to 3D scene animation and camera paths.
- **Import:** `import { ScrollControls, Scroll, useScroll } from '@react-three/drei'`
- **Key Props on `<ScrollControls>`:**
  - `pages={3}`: Virtual scroll length in viewport heights.
  - `damping={0.2}`: Smooth scroll inertia damping.
  - `horizontal={false}`: Toggle vertical vs horizontal scroll.
- **Hooks:**
  - `useScroll().offset`: Normalized scroll progress `[0, 1]`.
  - `useScroll().range(from, distance)`: Progress through a specific scroll segment.

### `<PresentationControls>`
Spring-damped constrained orbit controls tailored for interactive UI cards, badges, and product previews. Snaps back to resting position on release.
- **Import:** `import { PresentationControls } from '@react-three/drei'`
- **Key Props:**
  - `snap={true}`: Snaps back to origin on mouse release.
  - `speed={1.5}`: Sensitivity.
  - `zoom={1}`: Zoom allowance.
  - `polar={[-Math.PI / 4, Math.PI / 4]}`: Vertical tilt limits.
  - `azimuth={[-Math.PI / 4, Math.PI / 4]}`: Horizontal turn limits.
  - `config={{ mass: 1, tension: 170, friction: 26 }}`: Spring physics configuration.

### `<OrbitControls>`
Classic Three.js orbital inspection camera.
- **Import:** `import { OrbitControls } from '@react-three/drei'`
- **Key Props:** `enableZoom`, `enablePan`, `autoRotate`, `autoRotateSpeed`, `minPolarAngle`, `maxPolarAngle`.

### `<PivotControls>`
In-scene 3D transform gizmo with translate and rotate handles for interactive visual manipulation.
- **Import:** `import { PivotControls } from '@react-three/drei'`

---

## 4. Advanced Materials & Shaders (`@react-three/drei`)

### `<MeshTransmissionMaterial>`
Physical optical glass with true thickness, refraction, chromatic dispersion, and surface roughness. The gold standard for Apple VisionOS-grade physical glass in WebGL.
- **Import:** `import { MeshTransmissionMaterial } from '@react-three/drei'`
- **Key Props:**
  - `transmission={1}`: Light transmission ratio `[0, 1]`.
  - `roughness={0.15}`: Surface blur / frosted diffusion.
  - `ior={1.2}`: Index of refraction (glass ~ 1.5, water ~ 1.33, air ~ 1.0).
  - `chromaticAberration={0.05}`: Prism color edge separation.
  - `thickness={0.5}`: Physical material thickness for internal refraction.
  - `distortion={0.2}`: Surface refraction distortion.
  - `distortionScale={0.3}`: Distortion noise scale.
  - `temporalDistortion={0.1}`: Liquid shimmer animation over time.
  - `anisotropy={0.3}`: Directional light stretching.

### `<MeshReflectorMaterial>`
Real-time dynamic reflections on flat planes (glossy floors, polished marble, water).
- **Import:** `import { MeshReflectorMaterial } from '@react-three/drei'`
- **Key Props:** `blur={[300, 100]}`, `resolution={512}`, `mirror={0.7}`, `mixBlur={1}`, `mixStrength={1.5}`, `roughness={1}`, `depthScale={1.2}`.

### `<MeshDistortMaterial>` & `<MeshWobbleMaterial>`
Organic procedural vertex-distorting materials for liquid spheres, pulsating blobs, and tactile jelly UI elements.
- **Import:** `import { MeshDistortMaterial, MeshWobbleMaterial } from '@react-three/drei'`
- **Key Props:** `distort={0.4}`, `speed={2}`, `factor={0.6}`.

### `shaderMaterial`
Generates a custom Three.js shader material component with automatic getters/setters for uniforms.
- **Import:** `import { shaderMaterial } from '@react-three/drei'`

---

## 5. Spatial UI, DOM Pinning & Portals (`@react-three/drei`)

### `<Html>`
Pins standard React DOM elements (HTML, CSS, buttons, tooltips, cards) directly onto 3D coordinates in the scene.
- **Import:** `import { Html } from '@react-three/drei'`
- **Key Props:**
  - `position={[x, y, z]}`: 3D anchor position.
  - `center`: Centers the HTML element on the 3D point.
  - `distanceFactor={10}`: Scales HTML size relative to camera distance.
  - `occlude`: Occludes the HTML element behind solid 3D meshes.
  - `transform`: Projects the HTML element with full 3D CSS perspective transforms.

### `<Text>` & `<Text3D>`
- **`<Text>`**: Crisp 2D vector text in 3D space using signed distance fields (Troika).
  - `import { Text } from '@react-three/drei'`
  - `fontSize={0.5}`, `color="#fff"`, `anchorX="center"`, `anchorY="middle"`, `font="/fonts/Inter.woff"`.
- **`<Text3D>`**: True extruded geometric 3D solid text meshes.
  - `import { Text3D } from '@react-three/drei'`
  - `font="/fonts/helvetiker_regular.typeface.json"`, `size={0.75}`, `height={0.2}`, `bevelEnabled`.

### `<RenderTexture>`
Renders an independent 3D sub-scene or live UI component onto a texture mapped onto any 3D mesh surface.
- **Import:** `import { RenderTexture } from '@react-three/drei'`

---

## 6. 3D Asset Pipeline & Loaders (`gltfjsx` & `@react-three/drei`)

### `gltfjsx` CLI Tool
Compiles `.glb` / `.gltf` 3D files into typed, tree-shakeable React components with Draco compression.
- **CLI Command:**
  ```bash
  npx gltfjsx public/models/product.glb --transform --types -o src/components/3d/ProductModel.tsx
  ```
- **Advantages:** Direct access to individual mesh names, materials, and nodes via JSX props instead of imperative `scene.traverse()` loops.

### `useGLTF(url)`
Hook for loading 3D GLTF models with automatic caching and Draco decompression.
- **Import:** `import { useGLTF } from '@react-three/drei'`
- **Preloading:** `useGLTF.preload('/models/product-transformed.glb')`

### `useTexture(url | object)`
Hook for loading image textures with automatic encoding and filtering.
- **Import:** `import { useTexture } from '@react-three/drei'`

### `useAnimations(actions, ref)`
Extracts and controls skeletal animations bundled in GLTF models.
- **Import:** `import { useAnimations } from '@react-three/drei'`
- **Methods:** `actions['Walk']?.play()`, `actions['Run']?.crossFadeFrom(actions['Walk'], 0.5, true)`.

---

## 7. Cinematic Post-Processing (`@react-three/postprocessing`)

### `<EffectComposer>`
Wrapper for the post-processing render pipeline.
- **Import:** `import { EffectComposer } from '@react-three/postprocessing'`
- **Key Props:** `multisampling={4}`, `disableNormalPass={false}`.

### Core Effect Passes:
- **`<Bloom>`**: Soft emissive glow.
  - `intensity={1.2}`, `luminanceThreshold={0.8}`, `luminanceSmoothing={0.2}`, `mipmapBlur={true}`.
- **`<DepthOfField>`**: Cinematic camera lens blur.
  - `focusDistance={0.02}`, `focalLength={0.5}`, `bokehScale={3}`.
- **`<ChromaticAberration>`**: Optical color edge fringing.
  - `offset={[0.002, 0.002]}`, `radialModulation={true}`, `modulationOffset={0.5}`.
- **`<Vignette>`**: Edge darkening.
  - `offset={0.3}`, `darkness={0.7}`, `eskil={false}`.
- **`<Noise>`**: Fine film grain texture.
  - `opacity={0.02}`.

---

## 8. Real-Time Physics & Live Dials (`@react-three/rapier` & `leva`)

### `@react-three/rapier`
High-performance WebAssembly rigid-body physics.
- **`<Physics>`**: Physics world container (`gravity={[0, -9.81, 0]}`, `colliders="hull"`).
- **`<RigidBody>`**: Wraps any mesh with physical behavior.
  - `type="dynamic" | "fixed" | "kinematicPosition"`: Physical body type.
  - `colliders="cuboid" | "ball" | "hull" | "trimesh"`: Auto collision hull shape.
  - `restitution={0.6}`: Bounciness.
  - `friction={0.5}`: Surface friction.

### `leva`
Interactive browser GUI for live visual parameter tweaking.
- **Import:** `import { useControls } from 'leva'`
- **Usage:**
  ```tsx
  const { roughness, transmission, ior } = useControls('Glass Material', {
    roughness: { value: 0.15, min: 0, max: 1, step: 0.01 },
    transmission: { value: 1.0, min: 0, max: 1, step: 0.05 },
    ior: { value: 1.2, min: 1.0, max: 2.5, step: 0.05 },
  });
  ```
