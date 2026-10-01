/** Time searches: exact transits to a natal chart, and sky events (ingresses, stations, lunations) in a date range. */

import type { AspectName, Chart, PointName, SkyEvent, SkyEventType, TransitHit } from "../types.js";
import { ASPECTS, bisect, describe, SIGNS, signIndex, zodiacPoint } from "./astro.js";
import { BODY_NAMES, type BodyName, diff180, positions, rev, speeds } from "./ephemeris.js";

const HOUR = 3600e3, DAY = 864e5;
const iso = (ms: number): string => new Date(Math.round(ms / 60e3) * 60e3).toISOString().replace(":00.000Z", "Z");

/** Scan step per body: small enough that no body moves more than ~1.5° between samples. */
const stepFor = (b: BodyName): number => (b === "Moon" ? 2 * HOUR : b === "Mercury" || b === "Venus" || b === "Sun" ? 12 * HOUR : DAY);

/** Collects every instant in [start, end] where f changes sign continuously (|f| small on both sides). */
function roots(start: number, end: number, step: number, f: (t: number) => number, near = 20): number[] {
  const out: number[] = [];
  let t0 = start, f0 = f(t0);
  while (t0 < end) {
    const t1 = Math.min(t0 + step, end), f1 = f(t1);
    if (f0 !== 0 && Math.sign(f0) !== Math.sign(f1) && Math.abs(f0) < near && Math.abs(f1) < near) {
      const s0 = Math.sign(f0);
      out.push(bisect(t0, t1, (t) => Math.sign(f(t)) === s0));
    }
    t0 = t1; f0 = f1;
  }
  return out;
}

export interface TransitQuery {
  natal: Chart;
  start: number;
  end: number;
  transiting: BodyName[];
  natal_points: PointName[];
  aspects: AspectName[];
}

export function findTransits(q: TransitQuery): TransitHit[] {
  const natal = new Map<PointName, number>();
  for (const b of q.natal.bodies) natal.set(b.name, b.lon);
  if (q.natal.angles) {
    natal.set("Ascendant", q.natal.angles.ascendant.lon);
    natal.set("Midheaven", q.natal.angles.midheaven.lon);
  }
  const aspects = ASPECTS.filter((a) => q.aspects.includes(a.name));
  const hits: TransitHit[] = [];
  // Sample each body once on its own grid, then scan every natal target against the cached samples.
  const grids = new Map<number, { t: number[]; pos: ReturnType<typeof positions>[] }>();
  for (const body of q.transiting) {
    const step = stepFor(body);
    if (!grids.has(step)) {
      const t: number[] = [], pos: ReturnType<typeof positions>[] = [];
      for (let x = q.start; ; x = Math.min(x + step, q.end)) { t.push(x); pos.push(positions(x)); if (x >= q.end) break; }
      grids.set(step, { t, pos });
    }
  }
  for (const body of q.transiting) {
    const { t, pos } = grids.get(stepFor(body))!;
    const lons = pos.map((p) => p[body].lon);
    for (const point of q.natal_points) {
      const nl = natal.get(point);
      if (nl === undefined) continue;
      for (const asp of aspects) {
        const targets = asp.angle === 0 || asp.angle === 180 ? [asp.angle] : [asp.angle, -asp.angle];
        for (const off of targets) {
          const target = nl + off;
          for (let i = 1; i < t.length; i++) {
            const f0 = diff180(lons[i - 1], target), f1 = diff180(lons[i], target);
            if (f0 === 0 || Math.sign(f0) === Math.sign(f1) || Math.abs(f0) > 20 || Math.abs(f1) > 20) continue;
            const s0 = Math.sign(f0);
            const hit = bisect(t[i - 1], t[i], (x) => Math.sign(diff180(positions(x)[body].lon, target)) === s0);
            hits.push({
              utc: iso(hit), transiting: body, transiting_position: describe(zodiacPoint(positions(hit)[body].lon)),
              transiting_retrograde: speeds(hit)[body] < 0, aspect: asp.name, glyph: asp.glyph,
              natal_point: point, natal_position: describe(zodiacPoint(nl)),
            });
          }
        }
      }
    }
  }
  return hits.sort((a, b) => a.utc.localeCompare(b.utc));
}

const LUNATIONS: [SkyEventType, number, string][] = [
  ["new_moon", 0, "New Moon"], ["first_quarter", 90, "First Quarter Moon"], ["full_moon", 180, "Full Moon"], ["last_quarter", 270, "Last Quarter Moon"],
];

/**
 * Eclipse test from the Moon's ecliptic latitude at the syzygy (ecliptic limits about 1.5°).
 * It says whether an eclipse occurs somewhere on Earth, not its type or where it is visible.
 */
function eclipseAt(type: SkyEventType, moonLat: number): SkyEvent["eclipse"] {
  const b = Math.abs(moonLat);
  if (type === "new_moon") return b < 1.5 ? "solar" : null;
  if (type === "full_moon") return b < 1.55 ? "lunar" : null;
  return null;
}

export interface EventQuery {
  start: number;
  end: number;
  types: SkyEventType[];
  bodies: BodyName[];
}

export function findEvents(q: EventQuery): SkyEvent[] {
  const out: SkyEvent[] = [];
  if (q.types.includes("ingress")) {
    for (const body of q.bodies) {
      const step = stepFor(body);
      let t0 = q.start, s0 = signIndex(positions(t0)[body].lon);
      while (t0 < q.end) {
        const t1 = Math.min(t0 + step, q.end), s1 = signIndex(positions(t1)[body].lon);
        if (s1 !== s0) {
          const t = bisect(t0, t1, (x) => signIndex(positions(x)[body].lon) === s0);
          const lon = positions(t + 60e3)[body].lon;
          const backward = (s0 - s1 + 12) % 12 === 1;
          out.push({
            utc: iso(t), type: "ingress", body, summary: `${body} ${backward ? "moves back into" : "enters"} ${SIGNS[s1]}`,
            position: describe(zodiacPoint(lon)), detail: SIGNS[s1], eclipse: null,
          });
        }
        t0 = t1; s0 = s1;
      }
    }
  }
  if (q.types.includes("station")) {
    for (const body of q.bodies) {
      if (body === "Sun" || body === "Moon") continue;
      for (const t of roots(q.start, q.end, DAY, (x) => speeds(x)[body], Infinity)) {
        const goingRx = speeds(t + 6 * HOUR)[body] < 0;
        out.push({
          utc: iso(t), type: "station", body, summary: `${body} stations ${goingRx ? "retrograde" : "direct"}`,
          position: describe(zodiacPoint(positions(t)[body].lon)), detail: goingRx ? "retrograde" : "direct", eclipse: null,
        });
      }
    }
  }
  for (const [type, angle, label] of LUNATIONS) {
    if (!q.types.includes(type)) continue;
    const el = (x: number): number => { const p = positions(x); return diff180(rev(p.Moon.lon - p.Sun.lon), angle); };
    for (const t of roots(q.start, q.end, 6 * HOUR, el, 60)) {
      const p = positions(t);
      const eclipse = eclipseAt(type, p.Moon.lat);
      out.push({
        utc: iso(t), type, body: "Moon",
        summary: `${label} in ${zodiacPoint(p.Moon.lon).sign}${eclipse ? ` (${eclipse} eclipse)` : ""}`,
        position: describe(zodiacPoint(p.Moon.lon)), detail: label, eclipse,
      });
    }
  }
  return out.sort((a, b) => a.utc.localeCompare(b.utc));
}

export const DEFAULT_TRANSITING: BodyName[] = BODY_NAMES.filter((b) => b !== "Moon");
