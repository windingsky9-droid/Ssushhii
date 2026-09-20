# render-farm

Turns the configurator into a render farm: every product, colourway, lighting
preset and camera angle, written out as PNG at whatever resolution you ask for.
This is what produced `products/3d-render-pack/`.

```sh
pip install playwright && playwright install chromium
python render_farm.py 0 1000          # all 480 configurations at 2000 x 2000
python render_farm.py 8 700           # eight-frame sample, fast
python render_farm.py 0 1400 ../../portfolio/3d/index.html
```

Arguments are `[limit] [css_side] [source.html]`. `css_side` is CSS pixels; the
page runs at `deviceScaleFactor: 2`, so `1000` yields a 2000 × 2000 canvas.
Output lands in `renders/`, alongside a `manifest.json`.

## How it drives the page

The renderer keeps its state — camera, selection, lighting index — inside
`start()`, so none of it is reachable from outside. Rather than ship a debug
hook in the file customers buy, `rig()` writes a throwaway copy with one line
injected at the point `start()` hands control to the draw loop, exposing
`window.__rig`. The original is never modified.

Three details that are load-bearing:

- **`toDataURL` reads the canvas backing store, not the screen.** The
  surrounding UI is irrelevant, so the script pins the canvas element to an
  exact square with inline styles instead of fighting the page's grid. Only
  `clientWidth`/`clientHeight` matter, because `resize()` derives the drawing
  buffer from them.
- **Three animation frames per shot.** The draw loop must run at least once
  after the state change; `preserveDrawingBuffer: true` keeps the last frame
  readable when the capture happens.
- **Per-product framing.** Each product's default camera was framed for a wide
  stage, and on a square canvas the page's own `fit` factor pushes it back
  further. `FRAME` holds a pull-in per product, tuned against a contact sheet —
  too tight clips the lamp's base and the headphone band, too loose wastes half
  the frame. Re-tune it with `probe.py` if you change a product's geometry:

```sh
python probe.py '{"headphones":0.92,"bottle":0.72,"lamp":0.55,"table":0.62,"speaker":0.60}'
```

That writes `probe.png`, one hero per product side by side.

## Adding to the set

The shot list is built from the renderer's own `PRODUCTS` registry, so a fifth
product appears in the output with no change here. Lighting presets come from
`ENVS` the same way. Only `ANGLES` and `FRAME` live in this script.
