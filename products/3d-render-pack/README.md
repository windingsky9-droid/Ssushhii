# Studio Product Renders — Volume 1

384 royalty-free 3D product renders. 2000 × 2000 PNG. Studio-lit, four camera
angles, four lighting setups, twenty-four product configurations.

Nothing here was photographed, licensed or scraped. Every frame was generated
by a hand-written WebGL2 renderer — the same one that powers the live
configurator in this repository — which means the set is internally consistent
in a way stock photography never is: identical lighting rig, identical camera
geometry, identical tone mapping across all 384 files.

---

## What's in the set

| | |
|---|---|
| Products | Over-ear headphones, cosmetic pump bottle, table lamp, three-legged side table |
| Configurations | 24 (six colourways per product, each with its own finish, hardware and trim) |
| Lighting | 4 presets — Studio, Sunset, Showroom, Neon |
| Angles | 4 — hero three-quarter, front, high three-quarter, profile |
| Resolution | 2000 × 2000 px |
| Format | PNG, 8-bit RGB |
| Total | 4 products × 6 colourways × 4 lighting × 4 angles = **384 files** |

Every filename carries its own configuration, so the set is searchable without
opening anything:

```
bottle_SER1-AMB-GL-SLV-IVO_studio_hero.png
│      │                    │       └─ camera angle
│      │                    └───────── lighting preset
│      └────────────────────────────── build code (product + each option)
└───────────────────────────────────── product
```

`manifest.csv` maps every file to its product, model name, colourway, build
code, lighting preset and angle.

---

## What these are good for

- E-commerce listings, category tiles and hero images
- Ad creative and social posts
- Pitch decks, case studies and portfolio filler
- UI mockups that need a plausible product image
- Placeholder art in a design system, replaced later by real photography

## What these are *not*

Stated plainly, because a refund costs more than a lost sale:

- **No alpha channel.** Each render is a finished studio scene — gradient
  backdrop, ground plane and contact shadow baked in. These are not
  cut-out PNGs and cannot be composited onto another background without
  masking them yourself.
- **Not editable mockups.** There is no smart object, no PSD, no layer to drop
  your own label into. The white band on the bottle is geometry, not a
  placeholder.
- **Not real products.** ORBIT ONE, SERUM 30ML, ARC TABLE LAMP and FORM 62 are invented.
  Do not present them as products you actually sell unless you actually make
  them.
- **Not photorealistic.** The lighting is analytic — three directional lobes
  and a sky/ground gradient, not a captured HDR environment. It reads as a
  clean product render, not as a photograph.

---

## Licence

Commercial use permitted, including in products you sell. Modify freely.
Do not resell or redistribute the render files themselves as a stock pack,
on their own or as part of another pack. See `LICENSE.txt`.

---

## Regenerating, and changing anything

The renders are outputs, not sources. The generator is included in this
repository under `tools/render-farm/`, so the entire set is reproducible — and
adjustable. Change the resolution, add a colourway, add a lighting preset, add
an angle, and re-run:

```sh
python render_farm.py 0 1400     # all configurations, 2800 x 2800
```

That property matters more than the 384 files. A stock pack you cannot extend
is a dead end; this one regenerates to any size, and a fifth product is one
object in the renderer's `PRODUCTS` registry.
