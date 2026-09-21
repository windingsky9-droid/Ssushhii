# Launch posts, written out

`LISTING.md` in each product says where to post. This file is what to post.

Everything here is drafted to be sent as-is. Three rules run through all of it,
and they are the difference between a launch and a ban:

1. **Lead with the demo, never the paid link.** The live configurator is the
   thing worth clicking. Communities remove posts that open with a price.
2. **Say it is yours.** "I built this" is fine everywhere. Pretending to be a
   happy customer is not, and it is the fastest way to lose an account.
3. **Answer replies for the first two hours.** A post with six answered
   comments outranks a better post with none, on every platform listed here.

Live demo:   <https://sushir-saxon.upfling.site/3d/index.html>
Cart demo:   <https://sushir-saxon.upfling.site/3d/store/index.html>
Renders:     <https://sushir-saxon.upfling.site/renders/index.html>
Free sample: <https://sushir-saxon.upfling.site/renders/sample/index.html>

Ten full-resolution renders are free, with no email gate. For the render pack
that is the better hook than the gallery — "ten free 2000×2000 renders" gets
clicked where "look at my gallery" does not, and it costs nothing to give.

---

## r/webdev

Best on a weekday morning, US time. Read their self-promotion rule before
posting — it changes, and it is enforced.

**Title**

```
I built a real-time 3D product configurator in one 61 KB HTML file — no three.js, no build step
```

**Body**

```
Demo: https://sushir-saxon.upfling.site/3d/index.html

Drag to orbit, change the colour/finish/hardware, switch between five
products. It re-shades on your GPU as you click.

The whole thing is one HTML file with a hand-written WebGL2 renderer. No
three.js, no framework, no CDN request, and no model files — the geometry is
generated in code at load, and the lighting is analytic, so there is no HDR
environment map either. That is the point: a configurator built the usual way
ships 600 KB of library plus a model plus textures before the customer sees
anything.

Things I got wrong that might save you time:

- The lathe winding was globally inverted, so every surface of revolution was
  front-facing on its inside and culling removed it. Gold rendered silver and
  a table top rendered as a black disc. I found it by writing a standalone
  cross-product script rather than squinting at the shader.
- Weighting every light equally in the diffuse term washes out matte
  surfaces. A pow(cos, s) lobe subtends about 2*pi/(s+1), so a sharpness-150
  pinpoint was contributing as much as a broad softbox.
- gl.clearColor has to go through the same tone map as the shader output, or
  the ground plane's far fade shows a hard seam against the background.

Happy to answer anything about the renderer.
```

Put the Gumroad link in a **comment**, not the post.

---

## Hacker News — Show HN

Post between 8 and 10am US Eastern on a weekday. One link, one short body.

**Title**

```
Show HN: A 3D product configurator in a single 61 KB HTML file, no dependencies
```

**Body**

```
https://sushir-saxon.upfling.site/3d/index.html

Hand-written WebGL2 — no three.js, no framework, no model files. Geometry is
generated procedurally at load and the lighting is analytic (sky/ground
gradient plus three directional lobes, roughness widening the lobes in place
of a prefiltered environment map), so the page ships no textures at all. One
HTTP request, smaller than most hero images.

Five products switchable from a tab, because "will this work for my product"
is the only question that matters and four unrelated shapes was the only
honest answer I had.

The hardest bug was a globally inverted lathe winding: every surface of
revolution was front-facing on its interior, so backface culling silently
removed it. It presented as bad materials — gold reading as silver — rather
than as missing geometry, which is why it survived so long.
```

Do not mention the price unless someone asks. On HN they will ask.

---

## r/ecommerce and r/shopify

Different framing: these readers care about conversion, not renderers.

**Title**

```
Built a browser 3D configurator that writes the chosen build straight into the cart — demo inside
```

**Body**

```
Demo: https://sushir-saxon.upfling.site/3d/store/index.html

The configurator is on the left, a normal product page on the right. Change
an option and the panel updates; Add to cart receives the full selection —
product, model, build code, price, every option — over postMessage.

Two things I would flag for anyone building this themselves, because both are
easy to get wrong and expensive:

- Check e.origin on the listener. Do not trust whatever page happens to be
  framing your configurator. Derive the expected origin from the iframe's own
  src rather than assuming same-origin, or it breaks the moment you move the
  configurator to a CDN.
- Never charge from the price the panel shows. It is computed client-side and
  editable in devtools. The charge has to come from a real variant or a
  server-side rule; send the build code as a line-item property.

The demo page says in as many words that it trusts the price only because it
is a demo.
```

---

## r/graphic_design, r/blender, r/DesignPorn — the render pack

Different product, different room. Lead with the free ten.

**Title**

```
600 studio product renders from a renderer I wrote myself — 10 of them free, full resolution
```

**Body**

```
Free ten: https://sushir-saxon.upfling.site/renders/sample/index.html
All thirty configurations: https://sushir-saxon.upfling.site/renders/index.html

2000x2000 PNG, commercial use, no attribution, no email gate.

Five products in six colourways each, under five lighting setups, from four
camera angles. Every frame came out of the same hand-written WebGL2 renderer,
so the whole set matches — same lighting rig, same camera geometry, same tone
mapping. That is the part stock photography cannot do: twelve photos from
three photographers never look like one shoot.

Worth saying plainly: no alpha channel, these are finished studio scenes with
the backdrop and contact shadow baked in. Not cut-outs, not editable mockups.
```

---

## Answering existing threads

Higher conversion than any new post, and almost nobody does it. Search
r/shopify, r/ecommerce and the Shopify community forums for **"product
customizer"**, **"3D product viewer"**, **"configurator app"**. Most threads
are people quoted $3,000+ by an agency or paying $99/month for an app.

Reply honestly, with the demo, and only if it genuinely fits:

```
If it helps, here's a working demo of the approach:
https://sushir-saxon.upfling.site/3d/index.html

It runs in one HTML file with no dependencies, so it embeds in a Shopify
section without an app. Full disclosure, I built it and I sell it as a
template — but the demo is free to poke at and the technique works whether
or not you buy anything.
```

The disclosure is not optional. It is also what makes the reply land.

---

## X / Bluesky

One post, the demo, one image. The render gallery is the better image.

```
A 3D product configurator that runs in one 61 KB HTML file.

No three.js. No framework. No model files — the geometry is written in code
and the lighting is analytic, so there are no textures to download either.

Five products, five lighting rigs, drag to orbit:
https://sushir-saxon.upfling.site/3d/index.html
```

---

## What to expect

Be honest with yourself about the numbers so a quiet first day does not read
as failure.

A good r/webdev post gets a few hundred visits. A Show HN that does not reach
the front page gets a few dozen. Template conversion on cold traffic runs
around 1–2%, so a few hundred visitors is a sale or two, not a windfall.

The point of the first launch is not revenue. It is finding out which of the
two products people actually click, so the second launch aims at that one.
