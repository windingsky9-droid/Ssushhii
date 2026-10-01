# Sushi & Ismael

An interactive 3D binary star in the type system of the earlier Sushi & Ez build (Syncopate and IBM Plex Mono). Sushi burns red with a hot-pink corona, Ismael burns cool blue with an electric-cyan corona, and the two colors meet in violet.

Open `index.html` in a current browser. It loads three.js 0.160 and Google Fonts from their CDNs, so it needs a connection.

## What is in the scene

- **Two stars on a real Kepler orbit.** Equal mass (q = 1.00), eccentricity 0.12, a 44-second period. They speed up near periastron, and the telemetry panel reads out separation, phase and speed live.
- **Animated star surfaces.** Granulation with a network of dark lanes, sunspots and limb darkening come from 3D simplex noise. Sushi has a crimson body with coral-hot cells; Ismael has a cobalt body with ice-white cells.
- **Coronal loops.** Tubes of plasma flow along magnetic arches rooted in active regions, where the surface shows bright faculae around dark pores. Every so often a loop flares.
- **The bond.** A double helix of particles runs between the stars. The red strand flows toward Ismael and the blue strand flows toward Sushi, and pulses travel along the base-pair rungs.
- **Lit by both stars.** Three planets named after sushi (Tamago, Hamachi and Nori) are lit red on one side and blue on the other. The dust belts shift color the same way as the stars move around them.
- **Astrolabe ring.** Degree ticks, with both names engraved around the orbital plane.
- **Names in the sky.** SUSHI and ISMAEL are drawn as constellations: 11 letters made of 105 stars with diffraction spikes, which ignite letter by letter.
- **Hover or tap anything to see what it is.** Every constellation star has a catalog card: a Greek-letter name ordered by brightness (as real stars are named), a spectral class (red giants for Sushi, blue giants for Ismael), surface temperature, magnitude and the letter it belongs to. The main stars, planets, barycenter and memories have cards too, with live orbit readings.
- **Up close (chapters VI and VII).** The camera drops to each star's surface, then pulls back. When the page carries birth data, each star wears a wheel of the sky on the night that person was born: zodiac band, houses, the Ascendant and Midheaven, all ten bodies at their real degrees, and the aspect lines between them. Hover or tap a planet for its sign, degree, house, motion, height above the horizon and closest aspects. A profile card adds a live age, distance travelled around the Sun, and how far the light of that night has travelled past real stars.
- **Memories.** Type a memory and it rises out of the barycenter into its own orbit. Memories are kept in the viewer's browser only.
- **Sound (optional).** The two stars sound a perfect fifth apart (A3 and E4). Each tone pans with its star across the screen and swells as the stars draw close.

## Controls

- Drag to orbit and scroll to zoom.
- Click a star to fly to it, and click it again to go up close. Click or tap anything else to pin its info card. `Esc` closes it.
- Keys `1`–`7` jump between chapters and `T` toggles the guided tour.

Camera moves between chapters curve around the system instead of cutting through it, name tags glide instead of jumping, and the renderer lowers its resolution on its own if frames run slow.

This public copy carries no birth data and shows first names only. The birth wheels appear only when a `<script type="application/json" id="birth-skies">` block with `{ a, b }` chart data is added to the page, as the private build does. Without it, chapters VI and VII still fly in close to each star.
