# Sushir 3D Studio showcase

This is a buyer-facing portfolio package assembled from the existing 3D work in Downloads.

## Open it

Open `index.html` in a browser. The hero is a live WebGL orrery built with three.js that renders in the visitor's browser; if WebGL or the CDN is unavailable it falls back to the curated V11 showpiece still. The work plates launch the two interactive demos.

For a reliable local preview from PowerShell:

```powershell
py -m http.server 4173 --directory .
```

Then visit `http://127.0.0.1:4173`.

## What is included

- `index.html` — portfolio and lead-generation page with a live three.js orrery hero, live azimuth/elevation readouts, and a UTC clock.
- `media/astral-vault-v11-showpiece.png` — selected cinematic still (original, 3601 × 1639).
- `media/astral-vault-v11-showpiece.webp` — 1800 px web copy of the still (about 120 KB) used by the page; the PNG stays as the fallback.
- `demos/celestial-observatory-public.html` — self-contained synthetic public observatory preview with drag, zoom, focus, and snapshot controls.
- `demos/workflow-constellation.html` — the n8n 3D workflow study (originally `n8n-docs/docs/assets/3d-visualizations/workflow-3d.html`) rebuilt as an eight-node order-intake graph: orbit and pinch-zoom, node details, a conditional IF branch, animated data packets, and a replayable synthetic run log. Sample customers use `example.com` addresses and nothing leaves the page.

Both 3D pages load three.js r128 from cdnjs and fonts from Google Fonts; `tests/test_portfolio.py` checks that every local link resolves and that no other external host is referenced.

The private/name-specific source files remain in Downloads and were not copied into the public showcase. The interactive demo is a fresh synthetic public scene; it does not include personal birth data, exact locations, or private names. The portfolio uses scoped service language and does not promise investment returns.

## First-revenue use

Use the three service offers as the first commercial funnel: a tightly scoped API integration, a small dashboard, or a custom 3D/AI build. Confirm scope and licensing before accepting a project. The email and GitHub issue links are prepared but do not submit anything automatically.
