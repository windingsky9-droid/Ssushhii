# Real-Time 3D Product Configurator

A product configurator that runs in the customer's browser. They change the
colour, finish, hardware and cushion and the product re-renders immediately —
not a video, not a pre-rendered turntable, not a sprite sheet.

**One file. 36 KB. Zero dependencies.**

No three.js. No framework. No CDN request. No `.glb`, `.gltf`, `.obj` or
texture files to download — the geometry is generated in code when the page
loads, and the lighting is analytic, so there is no HDR environment map either.

That is the point. A configurator built the usual way ships 600 KB of library
plus a model plus textures before the customer sees anything. This one is a
single HTTP request that is smaller than most hero images.

---

## Quick start

1. Open `index.html` in a browser. It works from the filesystem — no build
   step, no server, no `npm install`.
2. Open it in a text editor and edit the `CONFIG` block near the top of the
   `<script>`. That is your brand name, headings, product name, base price
   and call-to-action.
3. Upload `index.html` anywhere that serves static files.

That is the whole deployment process.

---

## What you can change, and where

Everything lives in one file, in this order:

| I want to change… | Edit |
|---|---|
| Brand name, logo text, headings, CTA, base price | the `CONFIG` block — clearly fenced, at the top |
| The colour swatches | the `SHELLS` array |
| Matte / satin / gloss / anodised, and their surcharges | the `FINISHES` array |
| Hardware metals | the `METALS` array |
| Cushion materials | the `PADS` array |
| The four lighting presets | the `ENVS` array |
| **The product's actual shape** | the profiles passed to `lathe()` and `ring()` inside `start()` |

### Colours are linear, not hex

Material colours are `[r, g, b]` in **linear** space, each 0–1 — not sRGB hex.
The renderer does its own tone mapping and gamma, so a linear value is what the
shading maths needs.

To convert a hex colour you already have:

```js
const hexToLinear = h => [1,3,5].map(i =>
  Math.pow(parseInt(h.substr(i,2),16)/255, 2.2));

hexToLinear('1a1d22')   // -> [0.0075, 0.0094, 0.0136]
```

The on-screen swatch colour is derived from this automatically, so the picker
always matches what you see in 3D.

### Changing the product's shape

The whole model is built from two primitives:

- **`lathe(profile, segments)`** — revolves a 2D outline around the Y axis.
  A `profile` is a list of `[radius, height]` points. Repeat a point to get a
  hard crease; leave it single for a smooth one.
- **`ring(R, tube, y, seg, tubeSeg, squash)`** — a torus around the Y axis.
  Used for the trim, the badge and the ear cushion.

Between them they cover almost any turned or moulded object: bottles, jars,
lenses, speakers, cans, pots, wheels, lamps. `box()` handles the rest.

---

## Embedding it in a store

### Shopify

The simplest, most robust route is an iframe, because it keeps the
configurator's CSS from colliding with your theme's:

1. Upload `index.html` to **Settings → Files** (or any static host).
2. In your product template, add a Custom Liquid block containing
   `examples/embed-iframe.html`, with the `src` pointing at your uploaded file.

See `examples/shopify-liquid.txt` for the snippet, including a `postMessage`
listener if you want the customer's chosen configuration sent back to your
cart as a line-item property.

### Webflow / Squarespace / Wix

Add an Embed / Custom Code element and paste the same iframe snippet.

### WordPress

Upload `index.html` to your media library or `/wp-content/`, then add the
iframe snippet in a Custom HTML block.

---

## Browser support

WebGL2, which is every current browser: Chrome, Edge, Firefox, Safari 15+,
and mobile Safari and Chrome on Android.

If WebGL2 is missing the page does **not** show a blank canvas — it shows a
written explanation in the panel and every control still works. If you would
rather show a photograph there instead, that panel is `#fallback` in the
markup.

---

## Performance notes

- The renderer caps device pixel ratio at 2. On a 3× phone screen that is a
  deliberate trade: it is not visibly softer and it is more than twice as
  cheap to draw.
- The canvas is created with `preserveDrawingBuffer: true` so the "Download
  this view" button can work. If you remove that button, drop the flag too —
  it costs a little performance on some drivers.
- Draw calls scale with the number of parts, not the number of options. Adding
  twenty more colours costs nothing at runtime.

---

## What this is not

Being straight with you about the limits, because you are about to put it in
front of paying customers:

- **It is not a CAD importer.** It does not load `.glb`, `.step` or `.obj`.
  The geometry is written in code. If you need your exact CAD model, this is
  the wrong starting point.
- **It has no shadow mapping.** The contact shadow under the product is an
  analytic blob, not a real shadow pass. It looks right for a product on a
  seamless backdrop; it would not hold up in an architectural scene.
- **It has no cart or checkout.** It reports the configuration and a price.
  Wiring that into your cart is the `postMessage` example, and it is your
  store's job.
- **The sample product is a pair of headphones.** Reshaping it into your
  product is real work — an hour or two if it is a turned or moulded shape,
  longer if it is not.

---

## Licence

See `LICENSE.txt`.
