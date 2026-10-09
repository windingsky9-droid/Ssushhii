# Sushir 3D Studio portfolio

A buyer-facing portfolio: one landing page, two live WebGL demos, rendered
stills and the playbook behind them. Everything here is static HTML, so it
runs from any file server or static host.

## Preview it locally

From the repository root:

```bash
python scripts/serve_portfolio.py --open
```

That serves this folder at `http://127.0.0.1:4173` (local machine only).
On Windows, use `py` instead of `python`. To check that no page links to a
missing file:

```bash
python scripts/check_portfolio.py
```

## What's in the folder

| Path | What it is |
|---|---|
| `index.html` | Landing page: hero, selected work, services, process, about and contact. |
| `site-config.js` | Owner settings. Add your own donation or payment links here and the "Support the studio" section turns on. |
| `demos/celestial-observatory-cinematic.html` | V14 real-time WebGL2 observatory (three.js r170 from jsDelivr). |
| `demos/celestial-observatory-public.html` | The earlier lightweight 2D-canvas preview, for slow devices. |
| `demos/sky-wheel.html` | Sky Wheel: the real planets for any moment from 1800 to 2050, as a chart wheel set against the real stars, with an ephemeris, aspects, dignities, element balance and upcoming events. |
| `media/celestial-observatory-v14-hero.jpg` | Hero still: the ringed world with its sign tiles. |
| `media/celestial-observatory-v14-erebus.jpg` | Work card still: the lensing black hole as a clean plate. |
| `media/sky-wheel-card.jpg` | Work card still: the Sky Wheel for an evening in Los Angeles. |
| `media/celestial-observatory-v14-wheel.jpg` | The full HUD: target sign, aspect reading, chart wheel and ingress log. |
| `media/celestial-observatory-v15-sky.jpg` | The V15 real-sky shot: Leo and Cancer drawn from catalogue stars behind the ♌ tile. |
| `demos/archive/celestial-observatory-v14.html` | V14 frozen as it shipped, for comparison. |
| `media/archive/` | Earlier stills (V11 showpiece, V13 hero, black hole and pulsar), kept for reference. |
| `RENDERING_PLAYBOOK.md` | The nineteen techniques behind the observatory and how to reuse them. |

## The observatory

V15 keeps everything from V13 and V14: physically lit procedural planets, filmic
tone mapping, HDR bloom, image-based light, blackbody stars, a Keplerian
comet, five moons, deep-sky objects, a lensing black hole, a pulsar,
flares, meteors, a ten-aspect web with a traits reading, a narrated
director tour, synthesized sound and a compare split against a flat
baseline.

V14 reads the sky as a chart. Every body shows its zodiac sign and degree,
ingresses are logged as they happen, and the orrery card flips into a
chart wheel (`Z`) with aspect chords and fixed stars.

V15 puts the real sky behind it: 3,232 catalogue stars to magnitude 5.6
and the 88 constellation figures, set on the ecliptic so the zodiac
constellations line up with the sign tiles (about a sign apart, which is
precession). It adds lens ghosts that appear when the sun is on screen and
unblocked, a clean view (`H`) that hides the HUD, a deterministic capture
mode for frame-by-frame film rendering, and a frame cap (60 fps, or 30 with
**Cool** / `E`) so high-refresh laptops don't run hot.

Deep links open it in a specific mode:

| Link | Opens |
|---|---|
| `?tour` | the director tour |
| `?wheel&shot=ringed` | the chart wheel on the ringed world |
| `?shot=erebus` | the black hole |
| `?shot=pulsar` | the pulsar |
| `?compare` | the flat-versus-full split |
| `?shot=sky` | the real sky, with Leo behind the ♌ tile |
| `?ui=clean` | the clean view, no HUD |
| `?fps=30` | Cool mode from the start |

The full parameter list is at the end of `RENDERING_PLAYBOOK.md`.

## The Sky Wheel

`demos/sky-wheel.html` answers "where were the planets?" for any moment from
1800 to 2050. Pick a date, time and place, and it draws the chart wheel:

- signs, degrees and retrogrades for the Sun, Moon and planets through Pluto
- the Ascendant, Midheaven and whole-sign houses when a place is chosen
- aspects, with how many days until each one is exact
- the Moon's phase, and the next 45 days of sign changes, stations and
  lunations
- a slider and Play button that move time, so you can watch a retrograde
- a 1080×1350 chart card to save and share
- the real sky behind the wheel: 3,232 stars to magnitude 5.6, the
  constellation figures and the Milky Way, placed against the signs by
  ecliptic longitude and latitude, with the bright stars near the zodiac
  named
- essential dignities (at home, exalted, in detriment, in fall) and a tag
  when a planet sits within 1.5° of a bright fixed star
- a balance panel that weighs the chart's elements and modes and sums
  them up in one sentence

Positions come from JPL's Keplerian elements for the planets and a truncated
lunar theory for the Moon. They were checked against the PyEphem library at
240 dates: the largest error is 0.21° (Saturn), and the Moon stays within
0.08°. The Ascendant was checked by confirming that PyEphem puts the computed
point on the eastern horizon (within 0.006°). Everything runs in the browser.
Star, constellation and Milky Way data come from d3-celestial, © 2015 Olaf
Frohn, used under the BSD 3-Clause license.
When the page is hosted, Copy link shares a moment through `?d=`, `tz=` and
`place=` parameters.

## Taking payments and donations

Money goes straight to accounts you own. Nothing in this folder holds or
routes funds, and no secret keys belong in these files, because every file
is public once hosted.

1. Create a page that pays out to you: Ko-fi, Buy Me a Coffee, GitHub
   Sponsors, a Stripe Payment Link or a Fiverr gig.
2. Paste its `https://` link into `supportLinks` in `site-config.js`.
3. Reload the page. The support section and its nav link appear.

For client work, the service cards and the contact form route briefs to
email and to the GitHub issue template, so you confirm scope before any
payment.

`docs/LAUNCH_KIT_3D.md` has ready-to-post copy for getting the observatory
seen, a Fiverr gig for 3D work, and a store listing for a wallpaper pack.

## Privacy

The demos are synthetic public scenes. They contain no birth data, exact
locations or private names. Research and market visuals are illustrative
and make no investment promises.
