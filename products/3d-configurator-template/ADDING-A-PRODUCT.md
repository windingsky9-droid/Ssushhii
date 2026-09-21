# Adding your own product

This is the part of the template that is real work, so it gets its own page.
Everything else is editing `CONFIG`. This is modelling.

The walkthrough builds `MONITOR 5`, the bookshelf speaker that ships with the
template, from nothing. It is a real transcript of the work, including three
failures — because all three make geometry **disappear** rather than look
wrong, and "nothing rendered" is a much harder symptom to read than
"rendered badly". If you hit one, you will recognise it here and save an
hour.

---

## The shape of a product

One entry in `PRODUCTS`. The renderer knows nothing about what it is drawing.

```js
speaker: {
  label: 'Speaker',            // tab text
  name: 'MONITOR 5',           // shown in the spec panel
  codePrefix: 'MON5',          // first segment of the build code
  basePrice: 299,
  camera: { yaw: -0.58, pitch: 0.17, dist: 3.60, target: [0, -0.02, 0] },
  aoX: 0.72,                   // contact-shadow squash along X
  groundY: -0.585,             // where this product's floor sits
  groups:   [ /* the option controls */ ],
  material(key, o) { /* part name -> { c, m, r } */ },
  hidden(key, o)   { /* optional: drop a part entirely */ },
  build(up, add)   { /* the geometry */ }
}
```

Add it, reload, and it appears in the switcher. Nothing else changes.

---

## Step 1 — decide the parts before writing geometry

`build()` names each piece, and `material()` answers for each name. Decide the
split first, because it is what makes the option controls mean anything.

For the speaker: `cab` (the cabinet), `baffle` (the dark front panel),
`cone`, `driver` (the metal flanges and tweeter dome), `grille`, `plinth`.

The important choice is **`cone` separate from `driver`**. The first version
put the whole driver in one part, so choosing brass turned the entire cone
into a brass disc — and left the `cone` branch of `material()` as dead code.
Splitting them means the trim swatch changes a ring and a dome while the cone
stays dark paper, which is both what a driver looks like and what makes the
control feel like it is doing something precise.

---

## Step 2 — geometry, and the rule that will bite you

Two builders cover almost everything:

- `box(w, h, d)` — centred on the origin.
- `lathe(profile, segments)` — a surface of revolution around **+Y**. The
  profile is a list of `[radius, height]` pairs.

`ring(R, tube, y, seg, tubeSeg)` is a lathe convenience for a torus.

### Direction of travel sets the normal

This is the rule. A lathe segment's normal is derived from the direction the
profile travels, so **the order of your points decides which side of the
surface is visible.** Get it backwards and backface culling deletes the
surface entirely. You do not get a dark shape or a flipped shadow. You get
nothing, and you go looking for a bug in your materials.

A cylinder makes the convention concrete: a profile running bottom-to-top,
outward, faces outward. That is the common case, and it is why every lathed
profile in this file runs bottom-to-top.

A speaker cone is the uncommon case. It is **concave** — you are looking at
the *inside* of the dish — so its profile runs from the outer surround
**inward and back** to the dust cap:

```js
// Surround (outermost, frontmost) -> dust cap (on the axis, furthest back).
const gWoof = up(lathe([
  [0.228,0.036],[0.216,0.032],[0.204,0.028],[0.184,0.023],
  [0.120,0.013],[0.052,0.006],[0.030,0.009],[0,0.012]
], 96));
```

Write those same points in the other order and the driver vanishes.

### Do not close the profile at the front

The first attempt ended with a point back on the axis, at the front. That
caps the cone with a flat disc, which is what you see instead of the cone —
triangulated into a pinwheel, so it reads as a shading bug rather than a
modelling one. End the profile at the rim.

### Facing a lathe somewhere other than up

Lathes revolve around +Y. To point one at the viewer, rotate a quarter turn
about X when you place it:

```js
const face = [Math.PI / 2, 0, 0];
add(gWoof, 'cone', [0, -0.205, 0.274], face);
```

`add(geometry, partName, position, rotation)` — rotation is `[x, y, z]` and is
applied before the translation.

---

## Step 3 — placement, in the coordinates you actually chose

Keep a running note of where surfaces are. The speaker's cabinet front is at
`z = 0.250`, the baffle sits 0.012 proud of it so its face is at `0.274`, and
everything mounted on the front is positioned relative to that number.

This is where the third failure happened. The grille was a thin panel at
`z = 0.285` while the woofer's flange reached `0.370` — so with the grille
fitted, both drivers poked straight through the thing meant to hide them.

Neither obvious fix works. Move the grille in front of `0.370` and it floats a
fifth of the cabinet's depth off the face. Recess the drivers and they vanish,
because the baffle is a solid box with no cutouts — anything behind its front
face is simply *inside* it.

What works is halving the dish and making the grille a shallow box that
**contains** the drivers:

```js
const gGril = up(box(0.585, 0.985, 0.052));   // spans the baffle face to 0.326
add(gGril, 'grille', [0, 0, 0.300]);           // deepest driver part: 0.319
```

The geometry interpenetrates, and that is fine — the grille encloses the
drivers laterally too, so no part of the overlap is ever visible. It is also
what a real grille is: a panel with depth sitting on the baffle.

---

## Step 4 — materials

`material(key, o)` receives the part name and the current options, and returns
`{ c, m, r }` — colour, metalness, roughness.

```js
material(key, o) {
  if (key === 'cab')
    return { c: o.cab.c, m: o.cab.m,
             r: Math.min(Math.max(o.cab.r + o.finish.dr, 0.05), 1.0) };
  if (key === 'driver') return { c: o.driver.c, m: o.driver.m, r: o.driver.r };
  if (key === 'cone')   return { c: [0.021,0.022,0.025], m: 0.0, r: 0.80 };
  if (key === 'grille') return { c: [0.031,0.033,0.037], m: 0.0, r: 0.93 };
  return { c: [0.027,0.028,0.032], m: 0.0, r: 0.60 };   // baffle, plinth
}
```

Two things worth copying:

**Finish shifts roughness, it does not replace the material.** `o.finish.dr` is
a delta, so a gloss walnut is still walnut. Replacing the whole material makes
every finish look like a different substance.

**`c` is linear, not sRGB hex.** The renderer does its own tone mapping and
gamma. Pasting a hex value is the single most common first mistake; the main
README has the conversion.

---

## Step 5 — look at it, at every step

Every one of the three failures above was invisible in the code and obvious in
a rendered frame. Load the page and look after each piece you add, rather than
writing the whole `build()` and then debugging a black rectangle.

If you are adding several products, `tools/render-farm/probe.py` in the source
repository renders one hero per product side by side, which is also how the
per-product camera framing was tuned.

---

## Framing

Last, set `camera`. `dist` is the orbit radius; `target` is what it looks at.

Two things catch people out. A product framed on a wide desktop stage will be
too tight on a square or portrait canvas, because the page backs the camera
off automatically below an aspect of 1.25. And `groundY` has to match the
bottom of your geometry, or the product floats above its own contact shadow.
