# Rendering playbook: from flat to cinematic

This is the checklist behind the V12 Celestial Observatory
(`demos/celestial-observatory-cinematic.html`). Each item names what it
fixes, where it lives in the V12 source, and how to apply it in other
tools. Open the demo and use **Compare** (or press `C`) to split the frame
into a flat baseline and the full stack. Each switch in the Render Stack
panel turns off one technique so you can see what it adds.

## 1. Light the scene with one physical source

**What it fixes:** Flat, unlit shapes read as stickers. Real objects have a
day side, a night side and a terminator between them.

- V12 lights every planet with a single `PointLight` at the sun. Its
  color comes from a 5772 K blackbody, the sun's real surface
  temperature (`blackbody()` in the source).
- Planet surfaces are procedural and injected into `MeshStandardMaterial`
  with `onBeforeCompile`. The ocean world gets low roughness where it has
  water, so it shows a specular glint.
- Bump detail comes from the procedural height field via screen-space
  derivatives (`perturbNormalArb2`), so no textures are needed. Gas and ice
  giants get zero bump because they have no solid surface.

**Elsewhere:** in Blender, Cinema 4D or Unreal, start with one key light
and a very dim fill. Add light only when you can say what it motivates.

## 2. Render in HDR, then tone map

**What it fixes:** Clipped highlights. Without tone mapping, anything
brighter than 1.0 becomes a flat white blob.

- The composer renders into a `HalfFloatType` target with 4× MSAA, so
  values above 1.0 survive until the end.
- `OutputPass` applies ACES Filmic by default. AgX and Khronos Neutral are
  one click away in the panel. Exposure is exposed in EV.

**Elsewhere:** in Blender, set View Transform to AgX (or Filmic) and grade
exposure in stops. Never grade on a clipped sRGB image.

## 3. Bloom only what is actually bright

**What it fixes:** Glow applied to everything looks cheap and hazy.

- `UnrealBloomPass` runs with threshold 1.0. Only HDR values bloom: the
  sun, star cores and the heads of the orbit trails. The UI lines and lit
  planets stay crisp.

## 4. Atmosphere and scattering

**What it fixes:** Planets look like billiard balls without a limb glow.

- Each world gets two additive shells. The inner front-face shell adds a
  Fresnel rim, and the outer back-face shell adds a soft halo that fades to
  zero at its edge.
- Both are lit from the sun side and shift warm near the terminator.
  A forward-scatter term brightens the limb when the planet is backlit.
- The sun has limb darkening, and the corona adds streamers and a thin
  anamorphic streak.

## 5. Build the backdrop, then light with it

**What it fixes:** An empty black background reads as unfinished.

- A procedural Milky Way is baked once into a 1024² cube map. It has a
  galactic band, a bright core, emission nebulae, and dust lanes plus
  filaments that cut through the band.
- The same cube map is prefiltered with `PMREMGenerator` into
  `scene.environment`. The galaxy faintly lights the night sides, which is
  image-based lighting.
- The band is oriented so it crosses the hero shot at about 35°, and ten
  distant spiral galaxies sit at 1600 units.

**Elsewhere:** use an HDRI for both background and lighting. Poly Haven
HDRIs are CC0.

## 6. Stars that look photographed

**What it fixes:** Uniform white dots look like noise.

- There are 20,000 stars. Brightness follows a power law, so most are
  faint and a few are bright.
- Color comes from a blackbody temperature between 3,000 and 12,000 K.
- Each star is a Gaussian point-spread function, windowed so the quad
  edges never show. Half of them sit along the galactic band.

## 7. Lines that hold up at any zoom

**What it fixes:** 1 px GL lines alias, shimmer and vanish at high DPI.

- Orbits use `Line2` screen-space thick lines. A small `onBeforeCompile`
  patch turns each orbit into a light trail that is brightest just behind
  its planet.
- `depthFunc = LessDepth` stops the round caps from double-blending at
  segment joints. Without it, lines look dashed.

## 8. Motion follows physics

- Planet speeds follow Kepler's third law (ω ∝ a^-1.5), so inner worlds
  move faster.
- The comet follows a real ellipse (e = 0.76) and speeds up at
  perihelion (Kepler's second law). Its blue ion tail points straight
  away from the sun, and its gold dust tail curves behind its motion.
- Planet shadows fall on the rings analytically, using a ray from each
  ring fragment toward the sun.

## 9. The camera is a lens, not a viewport

- A 35° vertical FOV reads like a normal-to-long lens, with less distortion
  than the 75° default.
- Moves ease in and out over 2.4 s. The fly-to camera keeps the target
  locked while it orbits.
- The final pass adds film grain (stronger in the shadows), a vignette
  and radial chromatic aberration. Keep all three subtle.
- Optional depth of field (`BokehPass`) focuses on the orbit target.

## 10. Ship it light

- The stills are JPEG at quality 90: 270–420 KB each, instead of a 4.2 MB
  PNG.
- The demo lowers its pixel ratio automatically when frame rate drops
  below 28 fps.
- It respects `prefers-reduced-motion`.

## Rendering stills from the demo

URL parameters make the scene scriptable for headless capture:

| Parameter | Effect |
|---|---|
| `ui=off` | hides the HUD for clean plates |
| `shot=hero\|horizon\|ringed\|comet\|top` | starts on a camera shot |
| `compare=0.5` | opens the split view with the divider at that fraction |
| `dpr=1` | pins the pixel ratio |
| `t=40` | advances the simulation 40 seconds before the first frame |

The V12 stills were captured with Playwright and Chromium:
`page.goto('…/celestial-observatory-cinematic.html?ui=off&shot=ringed')`,
wait for `window.__ready`, then `page.screenshot()`.
