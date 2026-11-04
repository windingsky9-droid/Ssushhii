# Duo Display: a Blender build log

![Duo Display final render: two hex-pedestal displays reading SUSHIR and STUDIO, joined by a glowing arc, over a reflective grid floor with god rays and bokeh light strips](../portfolio/media/duo-display-hero.jpg)

Sushir 3D Studio's first path-traced piece. One Python script builds the
whole scene in Blender 4.2 LTS and renders it with Cycles. There's no hand
modelling and no `.blend` to keep in sync, and the two names are command-line
arguments. Every image on this page came out of the scripts in this folder.

| | |
|---|---|
| **Engine** | Blender 4.2 LTS · Cycles path tracing · OpenImageDenoise |
| **Scene** | 100% procedural, built by [`duo_display.py`](duo_display.py) |
| **Grade** | AgX "Punchy", bloom, anamorphic streaks, lens dispersion |
| **Type** | Chakra Petch (SIL Open Font License, in [`fonts/`](fonts/)) |
| **Final** | 1920×1080, 64 samples, about 8 minutes on a 4-core CPU |

## Watch it get built

The same shot rendered six times, one layer of upgrades per stage:

![Timelapse of the six build stages, from clay blockout to the graded final](../portfolio/media/duo-display-build-log.gif)

| Stage | Upgrade | What changes | Time at 960×540 |
|---|---|---|---|
| 1 | **Blockout** | Clay geometry and one key light. Proportions only. | 12 s |
| 2 | **Materials** | Brushed metal, glass screens with scanlines, emissive 3D type, a grid floor. | 13 s |
| 3 | **Lighting** | Coloured spots, rim, fill and a top light. | 15 s |
| 4 | **Set dressing** | HUD brackets, wireframe cores, the team-up arc and crystal, light strips, dust. | 33 s |
| 5 | **Atmosphere** | Volumetric haze turns the spotlights into god rays. | 74 s |
| 6 | **Lens + grade** | Depth of field, AgX Punchy, bloom, streaks and dispersion. | 71 s |

![Contact sheet of all six stages](../portfolio/media/duo-display-build-sheet.jpg)

![Split view: clay blockout on the left, final render on the right](../portfolio/media/duo-display-before-after.jpg)

## Why this beats a browser capture

The studio's earlier stills (V11 to V15) are Playwright screenshots of the
WebGL demos. Cycles renders this one by tracing light the way it actually
travels:

- **Real reflections.** The glossy floor mirrors the displays, the strips and
  the haze, from every angle.
- **Volumetric light.** Spotlights scatter through haze, so god rays come from
  the lighting itself instead of a painted overlay.
- **Physical depth of field.** Dust and light strips go out of focus as real
  bokeh.
- **Emissive geometry lights the scene.** The glowing type and frames cast
  coloured light on the metal around them.
- **Filmic grade.** AgX keeps saturated neon from clipping to flat white.

## Render it yourself

Install [Blender 4.2 LTS](https://www.blender.org/download/lts/4-2/), then
Pillow (`py -m pip install pillow`) and ffmpeg for the timelapse.

Windows (PowerShell), from the repository root:

```powershell
.\blender\render_build_log.ps1
.\blender\render_build_log.ps1 -Left ALPHA -Right BRAVO
```

macOS or Linux:

```bash
./blender/render_build_log.sh
LEFT=ALPHA RIGHT=BRAVO ./blender/render_build_log.sh
```

Output lands in `blender/renders/`, which Git ignores, so names you render
there stay on your machine.

One still, straight from Blender:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" -b --factory-startup `
	--python blender\duo_display.py -- --left ALPHA --right BRAVO `
	--font blender\fonts\ChakraPetch-Bold.ttf --font-sub blender\fonts\ChakraPetch-SemiBold.ttf `
	--shots hero --out blender\renders
```

## Options

| Option | Default | Does |
|---|---|---|
| `--left`, `--right` | `SUSHIR`, `STUDIO` | The two names. Both share one letter height. |
| `--left-sub`, `--right-sub` | `REAL-TIME 3D`, `CYCLES RENDER` | Subtitles under the names. |
| `--left-color`, `--right-color`, `--link-color` | `00E1FF`, `FF8A1F`, `B9A6FF` | Hex colours of each side and the arc. |
| `--shots` | `hero` | Any of `hero`, `left`, `right`, `wide`, comma-separated. |
| `--stage` | `6` | Build stage 1 to 6, as in the table above. |
| `--sample-ladder` | | Comma list such as `1,4,16,64`: renders once per count, no denoiser. |
| `--samples` | `128` | Cycles samples per pixel. |
| `--width`, `--height`, `--percent` | `1920`, `1080`, `100` | Resolution. |
| `--no-volume` | off | Skips the haze, which roughly halves render time. |
| `--save-blend`, `--pack` | | Saves the scene, with fonts packed in, to open in Blender. |

[`assemble_build_log.py`](assemble_build_log.py) turns the stage frames into
the timelapse (MP4 and GIF), the contact sheet, the before/after split and the
convergence animation, with Winding Sky labels on every frame.
