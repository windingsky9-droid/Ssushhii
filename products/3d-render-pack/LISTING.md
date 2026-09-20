# Gumroad listing — copy and paste

Second product, same account. If the configurator template isn't listed yet,
list it first — the steps in `../3d-configurator-template/LISTING.md` cover
account setup and payouts, and you only do those once.

## Product name

```
384 Studio Product Renders — 2000×2000, Royalty-Free
```

## Price

```
29
```

USD, one-time.

**Why 29.** Stock render and mockup packs cluster at $15–49. At 384 files
that's about 7½ cents a render, which is an easy yes for anyone who needs
three of them. It also sits deliberately below the $49 configurator template,
because this is the impulse buy and that is the considered one — and someone
who buys this for $29 is exactly who buys that for $49 next.

## Summary

```
384 royalty-free 3D product renders at 2000×2000. Four products, six colourways each, four lighting setups, four camera angles — one consistent studio rig across every frame.
```

---

## Description (paste into the description box)

**384 studio product renders. One lighting rig. No photography.**

Four products — over-ear headphones, a cosmetic pump bottle, a table lamp and
a three-legged side table — in six colourways each, shot under four lighting
setups from four camera angles. 2000 × 2000 PNG.

**Why they match, and stock photos don't**

Every frame came out of the same hand-written WebGL2 renderer: identical
lighting rig, identical camera geometry, identical tone mapping. Put twelve of
these in a grid and they look like one shoot, because they are. Twelve stock
photos from three photographers never will.

**What's inside**

- 4 products × 6 colourways × 4 lighting presets × 4 camera angles = 384 PNGs
- 2000 × 2000, 8-bit RGB
- `manifest.csv` — every file mapped to product, colourway, build code, lighting and angle
- Self-describing filenames: `bottle_SER1-AMB-GL-SLV-IVO_studio_hero.png`
- Lighting: Studio, Sunset, Showroom, Neon
- Angles: hero three-quarter, front, high three-quarter, profile

**Good for**

E-commerce listings and category tiles · ad creative · pitch decks and case
studies · UI mockups that need a believable product · design-system
placeholders you replace with real photography later.

**Read this before buying**

- **No alpha channel.** These are finished studio scenes — backdrop, ground
  plane and contact shadow baked in. They are not cut-outs and will need
  masking if you want them on another background.
- **Not editable mockups.** No PSD, no smart object. The white band on the
  bottle is geometry, not a placeholder for your label.
- **Not real products.** ORBIT ONE, SERUM 30ML, ARC TABLE LAMP and FORM 62 are
  invented. Don't present them as products you sell.
- **Not photorealistic.** Analytic lighting, not a captured HDR environment.
  It reads as a clean product render, which is the point — but it is not a
  photograph.

I would rather lose the sale than take it and give you a refund.

**Licence**

Commercial use, unlimited projects, no attribution. Don't resell the renders
themselves as a stock pack.

---

## Gallery — upload in this order

1. The contact sheet (`contact-sheet.png`) — 384 files in one image is the
   whole pitch; lead with it.
2. A headphones hero at full resolution
3. A bottle colourway row — same product, six finishes, proving the range
4. The same product under all four lighting presets
5. A lamp or table hero

## Tags

```
3d renders, product renders, stock images, mockup, ecommerce, product photography, royalty free, studio lighting, png, product mockup
```

## Category

Design → Graphics, or Photography → Stock.

---

## Building the upload

The renders are outputs, not sources — the generator lives in
`tools/render-farm/`. To produce the set:

```sh
cd tools/render-farm
pip install playwright && playwright install chromium
python render_farm.py 0 1000
zip -r ../../3d-render-pack-vol1.zip renders ../../products/3d-render-pack/README.md ../../products/3d-render-pack/LICENSE.txt
```

About 13 minutes on software rendering, and considerably less on a machine
with a real GPU. The result is roughly 290 MB.

Want it bigger? `python render_farm.py 0 1400` gives 2800 × 2800 and a
"4K-ready" line in the listing.
