# Rendering playbook: from flat to cinematic

This is the checklist behind the V13 Celestial Observatory
(`demos/celestial-observatory-cinematic.html`). Each item names what it
fixes, where it lives in the V13 source, and how to apply it in other
tools. Open the demo and use **Compare** (or press `C`) to split the frame
into a flat baseline and the full stack. Each switch in the Render Stack
panel turns off one technique so you can see what it adds.

## 1. Light the scene with one physical source

**What it fixes:** Flat, unlit shapes read as stickers. Real objects have a
day side, a night side and a terminator between them.

- V13 lights every planet with a single `PointLight` at the sun. Its
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
  patch shades each line as a glowing tube (a bright core plus a soft
  falloff, using the line's cross-section UV). It adds a light trail
  that is brightest just behind the planet, and energy pulses that flow
  along the orbit. Aspect lines carry pulses from one world to the other.
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

## 10. Sharpen, then add depth cues

- **Contrast-adaptive sharpening** (CAS) runs in the last pass. It
  sharpens most where local contrast is low and leaves already sharp
  edges alone, so it recovers detail softened by bloom and MSAA without
  halos.
- **Parallax dust:** 1,400 faint grains live in a 60-unit box that wraps
  around the camera. They are nearly invisible when still, but they sell
  depth as soon as you orbit or fly.
- **Scale layers:** five moons, an outer icy belt of 9,000 points, and
  deep-sky objects give the eye near, middle and far planes. The
  deep-sky set is a ring nebula with a white-dwarf core, two irregular
  dwarf galaxies, and a young cluster with diffraction spikes.

## 11. Make the image explain itself

- The Render Stack groups switches into Light, Sky, Lines & Data, and
  Camera. A pipeline strip shows the order each frame is built in
  (Geometry › Light › Bloom › Tone › Lens › Sharpen › Display) and dims
  any stage that is switched off.
- The target card adds a short field-guide paragraph for each body, and
  the mission log records aspects forming, comet perihelion and planet
  years as they happen.
- Free roam (`F`, or the button) flies the camera with W A S D, Q/E for
  down and up, drag to look, and Shift to boost.

## 12. Bend light with a screen-space lens

**What it fixes:** A black hole drawn as a black disc reads as a sticker.
What sells it is the light around it.

- EREBUS's accretion disk is ordinary geometry: a ring mesh, near edge-on,
  with Keplerian shear (the inner gas laps the outer) and relativistic
  Doppler beaming, so the side moving toward the camera is brighter and
  bluer.
- The last post pass treats EREBUS as a point lens. Each pixel at angle θ
  from the hole samples the image at θ − θE²/θ. That one formula creates
  the Einstein ring, lifts the far side of the disk over the shadow and
  folds a second image under it.
- The Einstein radius is set in world units and projected every frame, so
  a telephoto lens magnifies it correctly. The near side of the disk is
  composited back over the shadow.

**Elsewhere:** in Blender, a real black hole needs a ray-marched shader
(for example, bending rays in an OSL script). For a poster, the same θE²/θ
remap works as a displacement map in Nuke or After Effects.

## 13. Periodic signals and stellar activity

- The pulsar's beams sweep a cone around its spin axis. The axis is tilted
  so one beam always crosses the camera. The flash is measured from the
  angle between the beam and the line of sight, never faked on a timer. The
  target card plots it as a live radio trace.
- Magnetic loops arch off the sun as thick lines with flowing pulses. Every
  half minute or so, one flares: the loop brightens, the corona swells, and
  the mission log records the flare class.
- Meteors are short gradient lines anchored where the camera was when they
  appeared, so they stay put while you orbit.

## 14. Direct the camera, and let the image explain itself

- **Director mode** (`T`) runs an eight-shot tour with letterbox bars and
  a caption that names the technique on screen. Each move eases over
  3.6 s, and focal length tweens with position, so a move into a
  telephoto shot reads as a real lens change.
- **Traits reading.** Every world carries three traits. The aspect web now
  tracks ten aspects, from the conjunction through the quincunx. Each one
  turns into a sentence by quality: fusing, easy, tense, polar,
  adjusting, gifted or a quiet thread. A mood meter weights them by how
  exact they are. This is a playful interpretation layer on top of live
  geometry.
- **Sound** (`M`) is synthesized with the Web Audio API: a drone, a sub,
  a noise "solar wind", a click for each pulsar pulse, a chime when a
  major aspect forms, and a low swell for flares. It stays off until you
  turn it on.

## 15. Ship it light

- The stills are JPEG at quality 90: 230–420 KB each, instead of a 4.2 MB
  PNG.
- The demo lowers its pixel ratio automatically when frame rate drops
  below 28 fps. Render-scale presets (Eco 1×, Balanced up to 2×, Ultra up to
  2.5× supersampling) and a live frame-time graph sit in the Performance
  panel.
- It respects `prefers-reduced-motion`.

## Rendering stills from the demo

URL parameters make the scene scriptable for headless capture:

| Parameter | Effect |
|---|---|
| `ui=off` | hides the HUD for clean plates |
| `shot=hero\|horizon\|ringed\|comet\|top\|erebus\|pulsar` | starts on a camera shot |
| `tour=3` | starts the director tour at shot 3, with the letterbox and caption |
| `quality=eco\|balanced\|ultra` | sets the render scale |
| `compare=0.5` | opens the split view with the divider at that fraction |
| `dpr=1` | pins the pixel ratio |
| `t=40` | advances the simulation 40 seconds before the first frame |

The V13 stills were captured with Playwright and Chromium:
`page.goto('…/celestial-observatory-cinematic.html?ui=off&shot=ringed')`,
wait for `window.__ready`, then `page.screenshot()`.
