# Prompt library

The prompts behind the studio's work, and the prompts for what comes next.
Each one is ready to paste into a coding assistant that can run a shell
(Claude Code, for example) from a checkout of this repository.

## What makes these prompts work

Every prompt here has the same five parts. A prompt that comes back generic is
usually missing one of them.

| Part | What it says | Example |
|---|---|---|
| **Outcome** | What exists when the work is done | A 1920×1080 Cycles still of two name displays |
| **Inputs** | The files, names and data to use | `blender/duo_display.py`, the names ALPHA and BRAVO |
| **Look** | Concrete visual references, not adjectives | Teal and orange spotlights, volumetric haze, AgX Punchy |
| **Constraints** | Limits that shape the solution | Blender 4.2 LTS, no add-ons, under 10 minutes on a 4-core CPU |
| **Proof** | How the assistant shows it worked | Render stages 1 and 6 at 960×540 and show both |

The proof line matters most. An assistant that has to render, screenshot or
run tests before it reports back catches its own mistakes: in this build, the
first renders showed a crystal floating off the arc and washed-out close-ups,
and both were fixed before anything was committed.

## The Duo Display, stage by stage

These six prompts rebuild [the Duo Display](../blender/) from nothing. They
are the prompts in the [making-of video](../portfolio/media/duo-display-making-of.mp4),
with the constraints and proof spelled out.

### 1 · Blockout

```text
Write one Python script that builds a scene in Blender 4.2 LTS run headless
(blender -b --factory-startup --python). Two display monoliths side by side:
each is a stacked hex-prism pedestal, a column, a back plate and a screen,
with a name as extruded, bevelled 3D text. Fit one scale to both names so
they share a letter height. Take the names, fonts and output folder as
command-line arguments. Clay material and one key light only, so we judge
proportions. Render a 960x540 hero shot at 32 samples and show it to me.
```

### 2 · Materials

```text
Give the Duo Display real materials, built from shader nodes in the script:
brushed metal for the pedestals, dark glass screens with holographic
scanlines (a sine wave over the screen's Y coordinate driving emission),
glowing type with metal side walls, and a grid floor that fades with
distance. Left side cyan 00E1FF, right side orange FF8A1F. Re-render the
same 960x540 hero shot and show it next to the blockout.
```

### 3 · Lighting

```text
Light the Duo Display like a stage: a coloured spotlight behind and above each
display, aimed down through it; a large soft key from camera left; a warm
fill from the right; a cool rim from behind. Use area and spot lights only,
no HDRI. Keep the screens readable, not blown out. Show the result.
```

### 4 · Set dressing

```text
Dress the set: HUD corner brackets on each screen, a wireframe icosphere core
inside an orbit ring above each display, a glowing Bezier arc joining the two
cores with a crystal at its apex, vertical light strips in the background
and a few hundred dust motes. Build everything procedurally with bmesh and
curves. Render and check that nothing floats or clips.
```

### 5 · Atmosphere

```text
Add volumetric haze with a Principled Volume box around the set, so the
spotlights turn into visible god rays. Keep the render under 90 seconds at
960x540 and 32 samples on a 4-core CPU: raise the volume step rate and turn
off volume bounces. Show me the before and after.
```

### 6 · Lens and grade

```text
Finish the Duo Display like a film frame: depth of field focused on the
names, the AgX view transform with the Punchy look, a compositor with bloom,
two-way anamorphic streaks and a touch of lens dispersion. Add hero, left,
right and wide camera shots with per-shot exposure. Render the hero shot at
1920x1080 and 64 samples with OpenImageDenoise, and save the .blend with
fonts packed.
```

### The build log

```text
Add a --stage 1-6 flag to duo_display.py that builds the scene only up to
that stage, and a --sample-ladder flag that renders 1, 2, 4 ... 64 samples
with no denoiser. Then write a Pillow + ffmpeg script that stamps each frame
with its stage name and turns the frames into a timelapse MP4 and GIF, a
contact sheet, a before/after split and a convergence animation.
```

## Upgrade prompts: the next renders

Each of these extends `blender/duo_display.py`. They are ordered from quick to
ambitious.

### Turntable

```text
Add --turntable SECONDS to duo_display.py: parent the hero camera to an empty
at the set's centre, keyframe a linear 0-360 degree rotation, and render a
1280x720 PNG sequence at 25 fps, 32 samples with OIDN and motion blur on.
Assemble it into an H.264 MP4 with ffmpeg (CRF 18) and a looping GIF. Render
the first 2 seconds first and show me a frame before doing the rest.
```

### Name reveal

```text
Animate the names so they write themselves on over 2 seconds: drive a
shader mask across each word's X axis with a keyframed value, add a bright
leading edge that blooms, and flicker the screens on with a short noise
burst. Export 1280x720 at 25 fps, then show me frames at 0.5, 1 and 2 s.
```

### Holotable

```text
Between the two displays, add a Halo-style holographic map table: a low hex
pedestal projecting a translucent hex-grid terrain built from a noise
texture, with scanlines and an additive emission shader that fades at the
edges. Light it only with its own glow. Keep the overall render time within
20% of the current hero shot.
```

### Live stats on the screens

```text
Add --stats-json PATH to duo_display.py. Read a JSON file with each
player's name, rank, K/D and accuracy, and print the numbers as a second
line of glowing text on each screen, sized to fit. Make a sample JSON with
made-up numbers, render with it, and show me the frame.
```

### Rain and wet floor

```text
Make it rain: a particle system of thin, motion-blurred streaks lit by the
spotlights, a wet floor using a noise-driven roughness map so the
reflections break up, and ripple rings where drops land. Compare render
times before and after and keep the increase under 2x.
```

## Real-time prompts

### Port the Duo Display to the browser

```text
Recreate the Duo Display as a single-file three.js r160 page loaded through
an importmap: RoundedBoxGeometry pedestals, TextGeometry names from a
typeface JSON of Chakra Petch, MeshPhysicalMaterial metal and clearcoat
glass, emissive type, UnrealBloomPass and an OutputPass with ACES tone
mapping, and OrbitControls with damping. Hold 60 fps on a laptop. Test it in
headless Chromium, take a screenshot at 1280x720 and show it to me.
```

### Upgrade the observatory

```text
Open portfolio/demos/celestial-observatory-cinematic.html. Add a 20-second
cinematic intro that flies the camera from the edge of the star field to the
ringed world, with eased timing and a title card, skippable with any key.
Keep every existing URL parameter working. Record it to MP4 with Playwright
in the deterministic capture mode and show me three frames.
```

## Research prompts

### Player dossier

```text
Research the public Halo Infinite record for the gamertag <NAME>: ranked CSR
and tier, K/D, KDA, accuracy, win rate, medals, best maps and modes, and the
last 15 matches. Use only public pages (Halo Waypoint, Halo Data Hive, Leaf,
Halopedia) and cite the source and date for every number. Then build a
one-page visual scouting report: a radar of strengths, a form strip of
recent matches, and plain-language coaching on angles, movement and teaming
up, each point tied to a number. Mark anything you could not verify.
```

## Repository prompts

### README that sells the work

```text
Rewrite this repository's README so a visitor understands the best work in
10 seconds: a hero image, badges for the real stack, a three-image gallery
that links to each project, a projects table with one-line descriptions, and
a mermaid diagram of how the projects connect. Keep every existing section
and link. Check that every image and link resolves before you finish.
```

### GitHub profile

```text
Write a GitHub profile README for windingsky9-droid: a one-line intro, the
three strongest projects with a still or GIF each, the stack as a compact
badge row, and what I am building now. Under 80 lines, no stat-card widgets
that break when a third-party service goes down.
```

## Making your own

Start from the five parts, and put the proof line last so it is the final
thing the assistant reads:

```text
Outcome:     <what exists when you are done>
Inputs:      <files, names, data>
Look:        <colours, lighting, references>
Constraints: <versions, time and size limits, what not to touch>
Proof:       <render / screenshot / test, and show it to me>
```
