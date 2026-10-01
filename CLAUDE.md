# Design system rules

This repository has **two visual systems** and no front-end framework, bundler, or build step for styles. Know which one you are touching before you change or add UI, and when translating a Figma frame into code.

| Surface | Files | Look | Tokens live in |
|---|---|---|---|
| **Sushir 3D Studio** (portfolio + 3D demos) | `portfolio/index.html`, `portfolio/demos/*.html` | Observatory deck: near-black ground, sun gold / orbit teal / glyph violet, condensed display type | An inline `<style>` `:root` block at the top of **each** page |
| **Market Observatory** (Flask app) | `templates/index.html`, `static/styles.css`, `static/app.js` | Research dashboard: lime + cyan accents | `:root` in `static/styles.css` |
| **Sushir 3D Studio** (Birth Sky MCP view) | `mcp/birth-sky-mcp-server/ui/chart-view.html` | The studio look in one dark card (MCP Apps chart wheel) | Its own inline `:root`, same values as the studio block |

`public-demo/` is **generated** from the Flask template and `static/styles.css` by `scripts/build_public_demo.py`. Never edit `public-demo/` by hand. Change the source, then run `python scripts/build_public_demo.py`.

## 1. Token definitions

Tokens are plain CSS custom properties. There is no token pipeline (no Style Dictionary or JSON source), so **the `:root` block is the source of truth**.

### Studio / portfolio tokens

Every portfolio page repeats the same core block. Keep values identical across pages; a page may add only layout tokens it needs.

```css
/* portfolio/index.html (canonical values) */
:root{
  --ground:#04070c;            /* page background */
  --deck:#0a1018;              /* raised surface (index); demos use rgba(8,13,21,.8x) glass */
  --deck-2:#0e1621;            /* gradient partner for plates */
  --rule:rgba(214,232,255,.12);/* hairlines and borders (.14 on demos) */
  --ink:#eef3f7;               /* primary text */
  --haze:#8e9bab;              /* secondary text, labels */
  --sun:#f6c177;               /* primary accent, CTAs, "trigger"/"composite" */
  --orbit:#4fe0c8;             /* secondary accent, focus ring, links on hover */
  --glyph:#a898f0;             /* tertiary accent, logic nodes, constellations */
  --flare:#ff7a66;             /* warm alert, outputs, "live" dot */
  --frost:#b9d4ff;             /* fifth data color (beta in Factor Terrain) */
  --sun-soft:rgba(246,193,119,.14);
  --orbit-soft:rgba(79,224,200,.1);
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --body:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --radius:18px;
  color-scheme:dark;
}
```

Full-screen demo pages add safe-area layout tokens:

```css
--top:calc(env(safe-area-inset-top,0px) + 18px);
--bottom:calc(env(safe-area-inset-bottom,0px) + 18px);
--left:calc(env(safe-area-inset-left,0px) + 20px);
--right:calc(env(safe-area-inset-right,0px) + 20px);
```

The palette is sampled from `portfolio/media/astral-vault-v11-showpiece.png`. Do not introduce new hues. If a design needs a sixth data color, derive it from these and add it to every page's `:root`.

**3D scenes read the same tokens.** Every three.js page resolves colors from CSS at runtime, so a token change recolors the WebGL scene too:

```js
const css = getComputedStyle(document.documentElement), tok = n => css.getPropertyValue(n).trim();
const SUN = new THREE.Color(tok('--sun'));
```

Never hard-code a hex in scene code when a token exists. Exceptions today are one-off material tints (for example the core `#fff1d6` and the helix `#c9fff4`); keep those rare.

**Typography scale (studio).** The display face is always condensed via `font-stretch` (78–85%) at weight 800 with `letter-spacing:-.02em`.

| Role | Rule |
|---|---|
| Hero h1 | `clamp(3rem,6.4vw,5.8rem)`, `font-stretch:78%`, `line-height:.9` |
| Section h2 | `clamp(2.4rem,5.2vw,4.2rem)`, `font-stretch:82%` |
| Card h3 | `clamp(1.7rem,2.6vw,2.2rem)`, `font-stretch:85%` |
| Body | 16px IBM Plex Sans, `line-height:1.6` |
| Label / eyebrow | 10.5–11px IBM Plex Mono, uppercase, `letter-spacing:.12–.16em`, `color:var(--haze)` |
| Readouts / numbers | IBM Plex Mono with `font-variant-numeric:tabular-nums` |

Fonts load from one Google Fonts request, identical on every studio page:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,500..800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
```

### Market Observatory tokens

```css
/* static/styles.css */
:root {
  --bg: #080b10; --panel: rgba(18,23,31,.82); --panel-2: #111721;
  --line: rgba(255,255,255,.1); --text: #f5f7fb; --muted: #949dab;
  --accent: #b6f36b; --accent-2: #75d7ff; --danger: #ff8f8f; --radius: 22px;
}
```

Fonts are DM Sans for body and Space Grotesk for headings. **Do not mix the two systems**: studio tokens stay out of `static/styles.css`, and lime `#b6f36b` stays out of `portfolio/`.

### Spacing

There is no spacing scale token. Use these existing conventions:

- Page gutter is set once on the wrapper: `.wrap{max-width:1200px;margin-inline:auto;padding-inline:clamp(16px,4vw,40px)}`.
- Sections use `padding-block:clamp(64px,9vw,112px)`.
- Groups use `gap` (8, 10, 12, 16px) on flex or grid, never per-element margins.

## 2. Component library

There is no component framework. Components are **class-named HTML patterns** repeated inside each page. Reuse these names and styles instead of inventing new ones.

### Studio page (`portfolio/index.html`)

| Class | Purpose |
|---|---|
| `.nav` | Sticky glass bar; uses `top:calc(env(safe-area-inset-top,0px) + 12px)` |
| `.btn` + `.btn-sun` / `.btn-ghost` | Primary and secondary buttons |
| `.label` (+ `b` for a sun highlight) | Mono uppercase eyebrow |
| `.tag` | Mono category line on cards |
| `.scope` | Live WebGL stage: `img.scope-poster` fallback, `canvas`, `.hud` overlays, `.is-live` fades the canvas in |
| `.launch` | Pill links to the demos (`style="--c:var(--sun)"` sets the dot color) |
| `.plates` / `.plate` / `.plate-main` / `.plate-copy` | Work grid; `a.plate` is the whole card as a link |
| `.graph`, `.factors` | Inline SVG previews (see Icon system) |
| `.specs` | Three-cell definition grid |
| `.offers` / `.offer` (`.offer-lead` featured) | Service cards with a `footer` price row |
| `.steps` | Ordered process; numbering comes from a CSS counter plus `data-phase` |
| `.brief`, `.addr`, `.toolkit` | Contact card, copyable email, and skills chips |

### Demo "console" pattern (`portfolio/demos/*.html`)

Every 3D demo uses the same skeleton. Copy it for a new demo:

```html
<div class="scene" id="scene" aria-hidden="true"></div>   <!-- WebGL canvas host, touch-action:none -->
<div class="labels" id="labels"></div>                     <!-- HTML labels projected from 3D each frame -->
<header class="bar">…back link, h1, one-line intro…<span class="badge">Synthetic …</span></header>
<aside class="panel …" aria-live="polite">…selection readout…</aside>
<div class="controls">…<div class="seg" role="group">…</div> buttons…</div>
<div class="fallback" id="fallback" hidden><p id="fallback-text"></p></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
```

Shared behaviors that every demo must keep:

- **Fallback.** If `window.THREE` is missing or `new THREE.WebGLRenderer()` throws, call `fail(message)`. It shows `#fallback` and disables the controls.
- **Custom orbit rig.** Uses spherical `theta/phi/radius`, pointer-drag, wheel, and two-pointer pinch. A tap without drag (under 6px) raycasts to select.
- **Panels clear of the graph.** `camera.setViewOffset` shifts the scene away from the panels: left of the right panel on desktop, and up between the title and the bottom sheet on phones.
- **Label projection.** `v.project(camera)` produces screen coordinates, then `translate(x,y)`. Set `visibility:hidden` when `v.z>1`.
- **Reduced motion.** `matchMedia('(prefers-reduced-motion: reduce)')` disables drift, tours, and animated growth.
- **Seg state.** Segmented controls use `aria-pressed` for state, and `.seg button[aria-pressed="true"]` is styled with the sun tint.

There is no Storybook. `portfolio/README.md` documents each page, so update it when you add one.

### Market Observatory

Jinja template `templates/index.html` with `.site-header`, `.shell`, `.hero-layout`, `.panel`, `.offer-card`, `.primary-btn` / `.ghost-btn`, and the `.eyebrow` / `.kicker` labels. Behavior lives in `static/app.js` and talks to `/api/research` and `/api/config`.

## 3. Frameworks and libraries

- **Backend:** Flask 3 (`app.py`, `src/`), served by gunicorn (`Procfile`, `Dockerfile`).
- **Front end:** vanilla HTML, CSS, and JS. There is no React, Vue, Tailwind, or preprocessor.
- **3D:** three.js **r128** UMD global from cdnjs. Stay on this build unless you migrate every page, because later versions dropped the `three.min.js` global.
- **Build:** none for CSS or JS. The only generator is `scripts/build_public_demo.py`.
- **Tests:** pytest (`tests/`). CI (`.github/workflows/ci.yml`) runs `pytest -q` and `compileall`.

## 4. Asset management

- Portfolio images live in `portfolio/media/`. Ship a WebP web copy (about 1800px wide, quality ~80) next to the original, and reference it through `<picture>` with a PNG fallback:

  ```html
  <picture>
    <source srcset="media/astral-vault-v11-showpiece.webp" type="image/webp">
    <img src="media/astral-vault-v11-showpiece.png" alt="…" loading="lazy">
  </picture>
  ```

- **External hosts are allow-listed by test.** `tests/test_portfolio.py` fails if a portfolio page references anything outside these hosts:
  - `https://cdnjs.cloudflare.com/`
  - `https://fonts.googleapis.com` / `https://fonts.gstatic.com`
  - `https://github.com/windingsky9-droid/`

  Figma asset URLs must be downloaded into `portfolio/media/`, never hot-linked.
- Every relative `href` and `src` must resolve to a real file, which the same test enforces.
- Procedural textures (sun surface, planet bands, rings, glow sprites, glyph tiles) are drawn with `<canvas>` and turned into `THREE.CanvasTexture`. Prefer this over shipping texture images.
- There is no CDN configuration of our own. Pages are static files that can be served from any static host.

## 5. Icon system

There is **no icon library or icon folder**. Use the existing means only:

- **Unicode glyphs:** `↗` for external or new-tab links, `↘` for in-page jumps, `←` for back links, `⌕` for search in the Flask app.
- **CSS-drawn marks:** for example the brand `.mark` (a sun dot inside two rings, drawn with `::before` and `::after`) and status dots (`<i>` with `background:var(--c)` and a matching `box-shadow` glow).
- **Inline SVG** for small diagrams (`.graph`, `.factors`). Style SVG with classes that map to tokens, such as `.b-sun{fill:var(--sun)}`. Keep path data short; draw anything generative with canvas or WebGL instead.
- If a Figma design contains icons, export them as inline SVG using `currentColor` or token classes. Do not add an icon font or package.

## 6. Styling approach

- **Page-scoped inline CSS.** Each studio page carries its own `<style>`. `static/styles.css` is the only shared stylesheet, and it serves the Flask app alone.
- **Dark only, by design.** Studio pages set `color-scheme:dark` and an explicit `background` on `html` and `body`. There is no light theme.
- **Responsive breakpoints (max-width):**
  - Studio: `899px` (stack to one column; panels become bottom sheets; controls go full-width), `640px` (single-column specs and steps; trim the HUD), and `1100px` (narrower demo panels).
  - Flask app: `800px`.
- **Grid and flex with `minmax(0,…)`** so long text never widens the page. There is no automated overflow test; check pages at a 390px viewport before shipping.
- **Accessibility:**
  - Every page defines `:focus-visible{outline:2px solid var(--orbit)}`.
  - Every page has a `prefers-reduced-motion` block.
  - Canvas hosts use `aria-hidden="true"`.
  - Live readouts use `aria-live="polite"`.
- **Honesty labels.** Every demo must say its data is synthetic, which `test_demos_label_their_data_as_synthetic` enforces. Market visuals also say "not investment advice".

## 7. Project structure

```
app.py, wsgi.py, src/          Flask app and research/pricing providers
templates/, static/            Market Observatory UI (Jinja + one CSS + one JS)
public-demo/                   GENERATED static copy of the Flask UI (do not edit)
scripts/build_public_demo.py   generator for public-demo/
portfolio/index.html           Sushir 3D Studio page (live orrery hero)
portfolio/demos/               one self-contained HTML file per 3D demo
portfolio/media/               images (original + WebP)
tests/                         pytest, including portfolio link/host/synthetic checks
mcp/birth-sky-mcp-server/      TypeScript MCP server (birth charts) with an MCP Apps view; `npm test` there
docs/                          launch, revenue, and seller-kit notes
```

A new demo is **one self-contained HTML file** in `portfolio/demos/`. To add one:

1. Copy the console pattern and token block from an existing demo.
2. Link the demo from the `.launch` row and a `.plate` in `portfolio/index.html`.
3. List it in `portfolio/README.md`.
4. Run `pytest -q`.

## Figma → code workflow (Figma MCP)

1. `get_design_context` for the frame, then `get_screenshot` for visual truth. Use `get_variable_defs` to read Figma variables.
2. **Map Figma variables to the existing CSS tokens by value.** For example, `#F6C177` becomes `var(--sun)` and `#8E9BAB` becomes `var(--haze)`. If a Figma color has no token match, pick the nearest token rather than adding a literal.
3. Translate generated React or Tailwind output into this repo's **vanilla HTML and page-scoped CSS**, reusing the class patterns in section 2. Never add React, Tailwind, or a bundler.
4. Download Figma image assets into `portfolio/media/`, add a WebP copy, and reference them locally.
5. Handle icons according to section 5.
6. Verify:
   - `pytest -q` passes;
   - no horizontal overflow at 390px;
   - no console errors;
   - the WebGL fallback still renders when three.js is blocked.

### Studio Figma library

The studio tokens also live in Figma: [Sushir 3D Studio — Design System](https://www.figma.com/design/gD9czMXM2tz6yVWAAu9tCp), page **Foundations**. Every variable carries its CSS custom property as WEB code syntax, so `get_variable_defs` and Dev Mode return `var(--sun)` and not a hex value.

| Figma variable (collection `Studio`, mode `Dark`) | CSS token |
|---|---|
| `surface/ground`, `surface/deck`, `surface/deck-2` | `--ground`, `--deck`, `--deck-2` |
| `text/ink`, `text/haze` | `--ink`, `--haze` |
| `line/rule` | `--rule` |
| `accent/sun`, `accent/orbit`, `accent/glyph`, `accent/flare`, `accent/frost` | `--sun`, `--orbit`, `--glyph`, `--flare`, `--frost` |
| `accent/sun-soft`, `accent/orbit-soft` | `--sun-soft`, `--orbit-soft` |
| `radius/card` | `--radius` |

The text styles are `Display/Hero`, `Display/Section`, `Display/Card`, `Body/Default`, `Body/Button`, `Label/Eyebrow`, `Label/HUD`, `Readout/Value` and `Readout/Chip`. They match the type scale in section 1. Figma cannot set the width axis of Bricolage Grotesque, so apply the `font-stretch` from section 1 when you translate a Display style.

The file also has three components:

| Figma component | Maps to |
|---|---|
| `Button` (`Style=Primary`, `Style=Ghost`) | `.btn-sun`, `.btn-ghost` |
| `Chip` | `.toolkit li` |
| `Posture badge` (`Constructive`, `Mixed`, `Defensive`) | `.posture` in `demos/factor-terrain.html` |

When a token changes, update the page `:root` blocks first, then the matching Figma variable.
