# 3D launch kit: get the observatory seen, then get paid

This kit turns the Celestial Observatory into attention and income. It has
five parts: where to post and what to say, a Fiverr gig for 3D work, store
listings for two digital packs, how the money reaches you, and a posting
rhythm that doesn't get flagged as spam. You post from your own accounts;
nothing here posts automatically.

## Before you post

1. **Put the portfolio online.** Every post below needs one public link.
   The portfolio folder is static, so any static host works: your Upfling
   site, GitHub Pages, Netlify or Cloudflare Pages. Upload the contents of
   `portfolio/`.
2. **Add a way to pay you.** Paste your Ko-fi, Buy Me a Coffee, GitHub
   Sponsors or Stripe Payment Link into `portfolio/site-config.js`. The
   "Support the studio" section turns on by itself.
3. **Record a 20-second clip.** Open the demo with `?tour`, full screen,
   and screen-record the director tour. Video gets far more reach than a
   still on every platform below. On Windows, Win+Alt+R records with the
   Xbox Game Bar.

Replace `YOUR-LINK` below with the live portfolio URL. The demo link is
`YOUR-LINK/demos/celestial-observatory-cinematic.html`.

## Where to post, and what to say

Post in one place per day, not all at once. Read each community's rules
first: several allow self-promotion only on certain days or with a flair.

### Three.js forum (Showcase category)

**Title:** Celestial Observatory: a real-time solar system with a lensing black hole and a live chart wheel

**Body:**
> I built a real-time observatory in three.js r170. Everything is lit by
> one 5772 K blackbody sun with ACES tone mapping and HDR bloom. The black
> hole bends the frame with a screen-space point lens, so the far side of
> the disk lifts over the shadow. The newest version reads the sky as a
> chart: each body shows its zodiac sign and degree, and a wheel draws the
> aspect web around the camera.
>
> Press C for a flat-versus-full split, T for the director tour, Z for the
> chart wheel. Demo: YOUR-LINK/demos/celestial-observatory-cinematic.html
>
> Happy to answer questions about the lensing pass or the render stack.

### Reddit: r/threejs, r/webgl, r/creativecoding

Post the screen recording as a video, not a link. Put the link in the
first comment.

**Title:** I made a real-time solar system in three.js that bends light around a black hole

**First comment:**
> Live demo (desktop recommended): YOUR-LINK/demos/celestial-observatory-cinematic.html
> Stack: three.js r170, a half-float MSAA target, bloom, ACES, and a custom
> lens pass for the Einstein ring. Press C to compare against a flat
> render. The render-stack panel lets you turn each technique off to see
> what it adds.

For **r/proceduralgeneration**, lead with the procedural planets and the
baked Milky Way. For **r/space**, check the self-promotion rules first and
lead with the pulsar and black hole.

### Hacker News (Show HN)

Post once, on a weekday morning US time, and stay around for an hour to
answer comments.

**Title:** Show HN: A real-time WebGL observatory with gravitational lensing

**Text:**
> A single HTML file with three.js. It renders physically lit procedural
> planets, a black hole with a screen-space point lens, a pulsar, and a
> chart wheel that reads each body's position live. The render stack can
> be switched off one technique at a time, and C splits the frame against
> a flat baseline. I wrote up the techniques in a playbook in the repo.

### X, Bluesky, Threads

**Post 1 (video):**
> Real-time black hole in the browser. The disk is real geometry, and a
> lens pass bends it into an Einstein ring. three.js, one HTML file.
> YOUR-LINK #threejs #webgl #creativecoding

**Post 2 (still of the chart wheel):**
> V14 reads the sky as a chart: every planet shows its sign and degree, and
> the wheel draws the aspects around the camera. Press Z in the demo.
> YOUR-LINK #threejs #gamedev

**Post 3 (split screen):**
> Same scene, flat on the left, full render stack on the right. One
> physical light, HDR, ACES tone mapping, bloom and a lens pass.
> YOUR-LINK #webgl #rendering

### Portfolio sites: Behance, Dribbble, ArtStation

Upload the V14 stills from `portfolio/media/` and the screen recording. Use
the title "Celestial Observatory" and link the live demo in the
description. These sites are where studios look for freelancers.

### The Sky Wheel: the easiest thing to share

`YOUR-LINK/demos/sky-wheel.html` shows where the real planets were at any
moment from 1800 to 2050. People look up their own birthday, save the chart
card, and post it, which carries your link with it. Lead with that.

**r/astrology, r/AskAstrologers** (read the self-promotion rules; some ask
for a flair or a specific day):
> I built a free chart wheel that runs entirely in your browser. Pick a date,
> time and city and it shows signs, degrees, retrogrades, whole-sign houses,
> aspects with days until exact, the Moon's phase and the next 45 days of
> ingresses and stations. Nothing is sent anywhere. I checked the positions
> against the PyEphem library: within a quarter of a degree from 1800 to 2050.
> Feedback welcome: YOUR-LINK/demos/sky-wheel.html

**r/dataisbeautiful or r/InternetIsBeautiful** (strict rules; post as a tool,
no hype):
> A chart wheel of the real sky for any date since 1800, with a slider to
> watch planets go retrograde.

**TikTok, Reels, Shorts** (screen-record, 15 seconds):
1. Type a birthday and pick a city.
2. Tap Play at 1 week/s and let Mercury loop backwards.
3. End on Save chart card.

Caption: "the sky the day you were born, in 10 seconds (free, no signup)".

**X or Threads:**
> What the sky looked like the moment you were born: signs, houses, aspects,
> Moon phase. Free, in your browser, nothing uploaded.
> YOUR-LINK/demos/sky-wheel.html

A Fiverr gig can grow from this, "I will build a custom astrology or
astronomy web app". The Sky Wheel is the proof piece.

## Fiverr gig 4: interactive 3D scenes

This complements the three gigs in `FIVERR_SELLER_KIT.md`.

**Title:** I will build an interactive 3D WebGL scene or product showcase

**Search tags:** threejs, webgl, 3d website, interactive 3d, product viewer

**Basic, $40:** One interactive three.js scene: a model or procedural
object, lighting, orbit controls, responsive layout. 3-day delivery.

**Standard, $120:** A cinematic scene with HDR lighting, bloom, tone
mapping, a guided camera tour and a loading screen. 5-day delivery.

**Premium, $300:** A full interactive showcase with a custom shader
effect, UI panels, performance presets for phones, and a handoff README.
7-day delivery.

**Gig description:**
> I build real-time 3D for the web with three.js. See the Celestial
> Observatory in my portfolio: physically based light, HDR, a custom lens
> shader, and a director-style camera. I'll scope your scene first, then
> deliver a single fast-loading page you can host anywhere, with the
> source and a README.

**Gallery:** the V14 hero, the black hole plate, the chart wheel HUD, and
the screen recording.

## The two packs

Both sell as instant downloads on Gumroad, itch.io or Ko-fi Shop, and all
three pay out to your own account. Price them to clear the fixed fees:
Gumroad keeps 10% + $0.50 of a direct sale and card processing takes
2.9% + $0.30, so a $3 product leaves about $1.80, while $5 leaves about
$3.55 and $12 leaves about $9.65. Sales that come through Gumroad's own
Discover marketplace pay a flat 30% instead.

### Celestial Observatory Wallpaper Pack

A pack of stills rendered straight from the demo: eight desktop wallpapers
at 2560×1440 and four phone wallpapers at 1179×2556.

**Title:** Celestial Observatory Wallpaper Pack

**Price:** $5, or pay-what-you-want with a $5 minimum.

**Description:**
> Twelve renders from a real-time WebGL observatory: a black hole bending
> its own accretion disk into an Einstein ring, a pulsar sweeping its beams
> through a nebula, a ringed giant in its own shadow, a comet and more.
> Eight desktop wallpapers (2560×1440) and four phone wallpapers
> (1179×2556). For personal use on your own devices.

**License line:** Personal use only. No resale or redistribution.

**Cover image:** the black hole plate, 1280×720, with a 600×600 thumbnail.

### Zodiac Constellations: 12 Star Map Prints

All twelve zodiac constellations drawn from real star positions, down to
magnitude 8, with each figure, its official border, a sky grid and the
Milky Way where it crosses the field. Printable wall art is one of the most
searched digital downloads, and a zodiac sign makes an easy gift.

**What is in the ZIP (60 files, 23 MB):**
- Midnight and Cream colorways for every sign
- Print 4×5 at 2400×3000 (8×10 in at 300 dpi, 16×20 in)
- A-sizes at 2480×3508 (A4 at 300 dpi, A3)
- Twelve phone wallpapers at 1179×2556, with the top left clear for the
  lock-screen clock

**Price:** $12 for the full set. A single-sign listing at $4 can come
later if buyers ask for one sign only.

**Description:**
> All twelve zodiac constellations, drawn from real star positions down to
> the faint stars you would see with binoculars. Each print shows the
> constellation figure, its official border, a sky grid and the Milky Way
> where it crosses the field. Print and frame them for your home or give
> one as a gift.

**Tags:** zodiac, astrology, constellation, star map, printable wall art,
digital print, celestial decor.

**Credit line (keep it in the README inside the ZIP):** star data from
d3-celestial, © 2015 Olaf Frohn, BSD 3-Clause license.

**Posts that fit this pack:** the Midnight Scorpio next to the Cream
Scorpio ("which one would you hang?"), a phone mockup of your own sign,
and a short clip scrolling through all twelve.

## How the money reaches you

1. In Gumroad, open **Settings → Payments**. Choose Individual unless you
   have business registration papers, and use your full legal name and a
   street address.
2. Pick **bank** or **PayPal**. Gumroad does not let you switch from bank to
   PayPal later. Bank payouts go through Stripe's identity checks (date of
   birth, a government ID number such as an SSN, sometimes a photo ID).
   PayPal payouts only need your name, address, phone and PayPal email, and
   take 2% per payout.
3. Set the schedule (weekly, monthly or quarterly). Sales wait in your
   Gumroad balance and pay out once the balance reaches $100.
4. From your bank or PayPal, move the money to Cash App, Apple Pay or a
   card the usual way.
5. Sellers aged 13 to 17 can sell, but in the US a parent or guardian has
   to be added to the payout settings before Gumroad pays out.

The money always sits in your own account. No one else, Claude included,
holds it for you.

## A rhythm that doesn't get flagged

- One community per day. Posting the same text to ten places in an hour
  looks like spam to moderators and filters.
- Answer every comment in the first hour. Replies push the post up and
  turn viewers into followers.
- Each post links to one place, the portfolio. The support section and
  the service cards take it from there.
- Keep a note of which post brought which message or sale, and do more of
  what works.

## What not to claim

- Don't promise investment returns or predictions. The chart reading is a
  playful layer on synthetic geometry.
- Don't use private names or birth data in public posts or demos.
- Don't buy followers or votes. It gets accounts banned from the
  communities above.
