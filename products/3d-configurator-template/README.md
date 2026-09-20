# Real-Time 3D Product Configurator

A product configurator that runs in the customer's browser. They change the
colour, finish, hardware and cushion and the product re-renders immediately —
not a video, not a pre-rendered turntable, not a sprite sheet.

**Four complete products. One file. 51 KB. Zero dependencies.**

Headphones, a cosmetic bottle, a table lamp and a three-legged side table,
switchable from a tab, all drawn by one renderer — because the question you
are really asking is "will this work for *my* product", and four unrelated
shapes is the only honest answer to that.

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
| Brand name, logo text, headings, CTA, currency | the `CONFIG` block — clearly fenced, at the top |
| A product's options, prices and build codes | its `groups` array inside `PRODUCTS` |
| How an option maps to a surface | that product's `material()` |
| **A product's actual shape** | that product's `build()` |
| Which product loads first | `CONFIG.defaultProduct` |
| The four lighting presets | the `ENVS` array (shared by all products) |

### Adding a fifth product

Add one entry to `PRODUCTS` and it appears in the switcher. Nothing else
changes — the renderer knows nothing about headphones, bottles, lamps or
tables. The lamp and the table were both added exactly this way: one object
each, no other edit.

```js
candle: {
  label: 'Candle', name: 'VESSEL 220G', codePrefix: 'VES1', basePrice: 42,
  camera: { yaw: -0.4, pitch: 0.12, dist: 3.6, target: [0, 0, 0] },
  aoX: 1.0, groundY: -0.6,
  groups: [ /* same shape as the two below */ ],
  material(key, o) { /* map a part name to { c, m, r } */ },
  build(up, add)   { /* up(geometry) once, add(geo, partName, pos, rot) */ }
}
```

`groundY` is where that product's floor sits, and `aoX` squashes the contact
shadow along X — 0.58 for something wide like headphones, 1.0 for something
upright like a bottle. A product may also define `hidden(partName, options)`
to drop a part entirely: the bottle uses it so the "None" label option removes
the band instead of painting it, and the lamp uses it to swap between three
different base geometries from one control.

**Profiles must run bottom-to-top.** `lathe()` derives both the outward normals
and the triangle winding from the direction of travel, so a profile written
top-down comes out inside-out: it renders unlit, and a flat cap disappears
entirely because backface culling removes it. If a new part looks strangely
dark or is missing, check this first.

**Parts are placed with `add(geometry, partName, position, rotation)`**, where
rotation is `[x, y, z]` applied as Rz·Ry·Rx. To array something around an axis
and splay it outward — the table's legs — rotate about X first and then about
Y: `[tilt, angle, 0]`. Doing it the other way tilts every copy in the same
world direction instead of its own.

### Colours are linear, not hex

Option colours are `[r, g, b]` in **linear** space, each 0–1 — not sRGB hex.
The renderer does its own tone mapping and gamma, so a linear value is what the
shading maths needs.

The renderer's lighting is deliberately high-contrast: a dim sky with a broad
warm softbox and one tight specular source, which is how product photography is
actually lit. Under a flat bright sky, black renders as grey and gold renders
as silver, because a metal's only colour is what it reflects.

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

## Shareable configurations

Every change writes the configuration into the URL as the build code itself:

```
https://yourstore.com/configurator/#FRM1-MAR-LQ-BRS-RNG:neon
                                    ^^^^ ^^^^^^^^^^^^^^^ ^^^^
                                  product     options   lighting
```

Opening that link restores the exact product, every option and the lighting
preset. The **Copy link** button puts it on the clipboard, falling back to
selecting the URL where clipboard access is blocked (it needs a secure
context, so it will not work over plain `http://`).

Because the fragment is the same string shown in the spec panel, a customer
quoting `FRM1-MAR-LQ-BRS-RNG` in an email and a customer sending you a link
are giving you the same information.

A link whose product or any option is unrecognised is ignored **entirely** and
the default configuration loads. That is deliberate: a half-restored spec is
worse than an obviously fresh one, because the customer cannot tell which
parts survived.

## Analytics

The configurator calls a hook on every meaningful interaction:

```js
window.__configuratorTrack = function (event, props) {
  // send it wherever you already send events
};
```

| Event | Properties |
|---|---|
| `product_changed` | `product` |
| `option_changed` | `product`, `option`, `value` |
| `link_copied` | `code`, `copied` |
| `view_downloaded` | `code` |
| `cta_clicked` | `product`, `code` |

**Nothing is sent anywhere unless you define that function.** There is no
analytics provider baked in, no default endpoint and no key — a file you paid
for should not report back to whoever sold it to you. Wire it to PostHog,
Plausible, GA, Segment or your own endpoint in three lines, or leave it unset
and the calls are silent no-ops.

The hook is wrapped in try/catch at the call site, so a broken or blocked
analytics script cannot take the configurator down with it.

`cta_clicked` is the one worth a funnel: it fires when someone clicks your
call to action with a configuration on screen, and it carries the build code
they had chosen.

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
- **Large, smooth metal surfaces look subtler than they would under a real HDR
  environment.** A metal shows only what it reflects, and an analytic sky has
  far less detail than a photographed room, so a big polished panel reads
  calmer than it would in a renderer that ships an environment map. Small metal
  parts — trim, hardware, caps — are unaffected. This is the trade for shipping
  no texture files at all.
- **The sample products are headphones, a cosmetic bottle and a table lamp.**
  Reshaping one into your product is real work — an hour or two if it is a turned or moulded
  shape, longer if it is not.
- **Labels are geometry, not artwork.** The bottle's label is a coloured band
  standing proud of the body. Printing an actual logo or text on it needs a
  texture, which this file does not ship.

---

## Licence

See `LICENSE.txt`.
