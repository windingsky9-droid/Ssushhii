# Gumroad listing — copy and paste

Everything below is ready to paste. Nothing here needs writing; it needs an
account, and the account has to be in your name because that is where the
money lands.

---

## The ten minutes only you can do

1. **gumroad.com** → Start selling → sign up with `windingsky9@gmail.com`.
2. Verify the email Gumroad sends.
3. **Settings → Payments** → connect a bank account or PayPal **in your own
   name**. Gumroad will not pay out until this exists. Nobody else can do
   this step for you, and anyone who offers to hold the money for you is
   running a scam.
4. **Products → New product → Digital product.**
5. Paste the fields below.
6. Upload `3d-product-configurator.zip` (build it with the command at the
   bottom of this file).
7. Upload the five images from `preview/` in the order given below.
8. Publish.

Steps 4–8 take about ten minutes. Step 3 is the one that decides whether any
of this turns into money.

---

## Product name

```
Real-Time 3D Product Configurator — Zero Dependencies, One File
```

## Price

```
49
```

USD, one-time. Not a subscription.

**Why 49.** The nearest comparable one-time template sells at $59. Hosted
configurator SaaS runs $10–$300 *per month*. An agency build of the same
thing quotes €3,000–50,000. $49 sits just under the one-time competitor and
is trivially justified against every monthly option — it pays for itself
before the first month of any SaaS alternative.

Do not discount it below $29. Below that, buyers assume it is a toy.

## Summary (the one-line field under the title)

```
A browser-native 3D product configurator in a single 54 KB HTML file. Four demo products, a working cart integration, no three.js, no build step.
```

---

## Description (paste into the rich-text description box)

**Your customer changes the colour and the product re-renders. Immediately.
Not a video. Not a pre-rendered turntable. Not a sprite sheet.**

This is a real-time 3D product configurator that runs entirely in the
browser, in **one HTML file, 54 KB, with zero dependencies.**

No three.js. No framework. No CDN request. No `.glb`, `.gltf`, `.obj` or
texture files to download — the geometry is generated in code when the page
loads, and the lighting is analytic, so there is no HDR environment map
either.

A configurator built the usual way ships 600 KB of library, plus a model,
plus textures, before the customer sees anything. This one is a single HTTP
request smaller than most hero images.

**Four complete products, switchable from a tab**

Headphones, a cosmetic bottle, a table lamp and a three-legged side table —
all drawn by the same renderer. Four unrelated shapes, because the question
you are actually asking is *"will this work for my product?"*, and four
unrelated shapes is the only honest answer to that.

Adding a fifth is one object in the `PRODUCTS` registry. The lamp and the
table were both added exactly that way — one entry each, no other edit.

**It reaches a cart**

The single biggest reason configurators get built and then never shipped is
that the chosen configuration never makes it into the basket. This one
posts the full selection — product, model, build code, price, currency,
every option — to the parent page via `postMessage`, with a worked
origin-checked example and a complete demo store included so you can see it
land in a cart end to end.

**What's included**

- `index.html` — the entire configurator, 54 KB, commented throughout
- `examples/store-demo/` — a working store page that receives the cart event
- `examples/embed-iframe.html` — the minimal embed
- `examples/shopify-liquid.txt` — a Shopify section drop-in
- `README.md` — 12 KB, including how to change a product's actual shape
- `LICENSE.txt`

**What you can change**

A clearly fenced `CONFIG` block at the top holds your brand name, headings,
product name, base price, currency and call-to-action. Below it, each
product owns its options, prices, build codes, materials and geometry. Four
lighting presets are shared.

**It also does**

- Shareable configuration URLs — every build has its own link, restored
  exactly, so customers can send a configuration to someone else
- Build codes (`ORB1-MAT-CHR-BLK`) for your order system
- Analytics hooks on every meaningful interaction — they ship inert, wired
  to nothing, so no tracker of mine is on your site
- Works on a phone: aspect-aware framing and 44px tap targets
- Runs from `file://` — double-click it and it works

**Requirements**

WebGL2, which is every browser since 2017. No server, no build step, no
`npm install`, no account with anyone.

**Licence**

Use it on unlimited projects of your own or your clients'. Don't resell the
template itself as a template.

---

## Gallery — upload in this order

| Order | File | Why it's there |
|---|---|---|
| 1 (cover) | `preview/screenshot-2.png` | The strongest single frame. This is the thumbnail that decides whether anyone clicks. |
| 2 | `preview/screenshot-1.png` | The configurator in full, panel and all |
| 3 | `preview/screenshot-3.png` | A second product — proves the renderer generalises |
| 4 | `preview/screenshot-5.png` | A third product and a different lighting preset |
| 5 | `preview/screenshot-4-mobile.png` | Phone viewport — answers the mobile objection before it's asked |

## Tags

```
3d, webgl, product configurator, ecommerce, shopify, html, javascript, no dependencies, product customizer, three-dimensional
```

## Category

Software / Web templates (or "Design → Web" if Gumroad offers it).

---

## Building the zip to upload

From the repository root:

```sh
cd products/3d-configurator-template
zip -r ../3d-product-configurator.zip . -x '.*'
```

That produces a ~1.1 MB archive of 15 files. `products/.gitignore` keeps the
zip out of git — rebuild it rather than committing it.

---

## After it's live

Post the live demo, not the product page, and let the demo sell it:

- **r/webdev** and **r/ecommerce** — lead with "I built a 3D configurator in
  one 54 KB file with no dependencies, here's the demo", link the live page,
  put the Gumroad link in a comment. Leading with the paid link gets removed.
- **Hacker News (Show HN)** — same framing. The zero-dependency angle is the
  story.
- **Shopify and WooCommerce community forums** — answer existing
  "how do I add a product customizer" threads with the demo.

Live demo: https://sushir-saxon.upfling.site/3d/index.html
Cart demo:  https://sushir-saxon.upfling.site/3d/store/index.html
