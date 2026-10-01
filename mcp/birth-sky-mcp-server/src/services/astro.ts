/** Chart construction on top of the ephemeris: signs, houses, aspects, balance, phases and plain-language highlights. */

import { PRECISION_NOTE } from "../constants.js";
import type {
  Aspect, AspectName, Balance, Chart, ChartBody, Comparison, CrossAspect, HouseSystem, MoonPhase, PointName, ZodiacPoint,
} from "../types.js";
import { angles, BODY_NAMES, type BodyName, diff180, positions, rev, speeds } from "./ephemeris.js";
import type { Moment } from "./time.js";

export const SIGNS = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
] as const;
export const SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
const ELEMENTS = ["Fire", "Earth", "Air", "Water"] as const;
const MODALITIES = ["Cardinal", "Fixed", "Mutable"] as const;

export const BODY_GLYPHS: Record<BodyName, string> = {
  Sun: "☉", Moon: "☽", Mercury: "☿", Venus: "♀", Mars: "♂", Jupiter: "♃", Saturn: "♄", Uranus: "♅", Neptune: "♆", Pluto: "♇",
};

export interface AspectDef { name: AspectName; angle: number; orb: number; glyph: string }
export const ASPECTS: AspectDef[] = [
  { name: "conjunction", angle: 0, orb: 8, glyph: "☌" },
  { name: "sextile", angle: 60, orb: 4, glyph: "⚹" },
  { name: "square", angle: 90, orb: 6, glyph: "□" },
  { name: "trine", angle: 120, orb: 7, glyph: "△" },
  { name: "opposition", angle: 180, orb: 8, glyph: "☍" },
];

export const signIndex = (lon: number): number => Math.floor(rev(lon) / 30) % 12;

/** Degree and arcminute, truncated (not rounded) so 2°44.9′ reads 2°44′, as ephemerides do. */
export function dm(x: number): string {
  const t = Math.floor(x * 60 + 1e-6);
  return `${Math.floor(t / 60)}°${String(t % 60).padStart(2, "0")}′`;
}

export function zodiacPoint(lon: number): ZodiacPoint {
  const l = rev(lon), s = signIndex(l);
  return { lon: round(l, 4), sign: SIGNS[s], sign_glyph: SIGN_GLYPHS[s], degree: round(l % 30, 4), dm: dm(l % 30) };
}

export const describe = (p: ZodiacPoint): string => `${p.dm} ${p.sign}`;
const round = (x: number, n: number): number => Math.round(x * 10 ** n) / 10 ** n;
const sep = (a: number, b: number): number => Math.abs(diff180(a, b));
const isLuminary = (p: string): boolean => p === "Sun" || p === "Moon";
const ordinal = (n: number): string => n + (n % 10 === 1 && n !== 11 ? "st" : n % 10 === 2 && n !== 12 ? "nd" : n % 10 === 3 && n !== 13 ? "rd" : "th");

interface PointState { name: PointName; lon: number; speed: number | null }

/** Finds aspects between two point sets. `scale` shrinks every orb (0.75 for chart comparison). */
export function findAspects(A: PointState[], B: PointState[], same: boolean, scale = 1): Aspect[] {
  const out: Aspect[] = [];
  A.forEach((p, i) => B.forEach((q, j) => {
    if (same && j <= i) return;
    if (p.speed === null && q.speed === null) return; // angle to angle
    const s = sep(p.lon, q.lon);
    for (const asp of ASPECTS) {
      const lim = asp.orb * scale * (isLuminary(p.name) || isLuminary(q.name) ? 1 : 0.85);
      const orb = Math.abs(s - asp.angle);
      if (orb > lim) continue;
      let applying: boolean | null = null;
      if (p.speed !== null && q.speed !== null) {
        const later = Math.abs(sep(p.lon + p.speed / 24, q.lon + q.speed / 24) - asp.angle);
        applying = later < orb;
      }
      out.push({ a: p.name, b: q.name, aspect: asp.name, glyph: asp.glyph, angle: asp.angle, orb: round(orb, 3), applying });
    }
  }));
  return out.sort((x, y) => x.orb - y.orb);
}

export function balance(bodies: { lon: number }[]): Balance {
  const elements = { Fire: 0, Earth: 0, Air: 0, Water: 0 };
  const modalities = { Cardinal: 0, Fixed: 0, Mutable: 0 };
  for (const b of bodies) {
    const s = signIndex(b.lon);
    elements[ELEMENTS[s % 4]]++;
    modalities[MODALITIES[s % 3]]++;
  }
  const top = <K extends string>(r: Record<K, number>): string => {
    const max = Math.max(...Object.values<number>(r));
    return (Object.keys(r) as K[]).filter((k) => r[k] === max).join(" and ");
  };
  return { elements, modalities, dominant_element: top(elements), dominant_modality: top(modalities) };
}

const PHASES = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"];
export function moonPhase(sunLon: number, moonLon: number): MoonPhase {
  const el = rev(moonLon - sunLon);
  return {
    name: PHASES[Math.floor(rev(el + 22.5) / 45) % 8],
    illumination: Math.round(((1 - Math.cos((el * Math.PI) / 180)) / 2) * 100),
    elongation: round(el, 2),
    waxing: el < 180,
  };
}

/** Bisection for the instant in [t0, t1] where `pred` flips, to within one minute. */
export function bisect(t0: number, t1: number, pred: (t: number) => boolean): number {
  const start = pred(t0);
  let a = t0, b = t1;
  while (b - a > 30e3) {
    const m = (a + b) / 2;
    if (pred(m) === start) a = m; else b = m;
  }
  return (a + b) / 2;
}

const HOUR = 3600e3;
const fmtHours = (h: number): string => (h < 1.5 ? `${Math.round(h * 60)} minutes` : `${Math.round(h)} hours`);

function highlights(chart: Omit<Chart, "highlights">, ms: number): string[] {
  const out: string[] = [];
  const by = Object.fromEntries(chart.bodies.map((b) => [b.name, b])) as Record<BodyName, ChartBody>;
  const sun = by.Sun, moon = by.Moon;

  if (sun.house !== null) {
    const above = sun.house >= 7;
    out.push(`${above ? "Daytime" : "Night"} birth: the Sun was ${above ? "above" : "below"} the horizon, in the ${ordinal(sun.house)} house.`);
  }

  // Moon phase, with the distance to the nearest lunation when it is close.
  const ph = chart.moon_phase, rel = moon.speed - sun.speed;
  const toNew = (360 - ph.elongation) / rel * 24, sinceNew = ph.elongation / rel * 24, toFull = (180 - ph.elongation) / rel * 24;
  if (toNew < 30) out.push(`Born ${fmtHours(toNew)} before the New Moon, with the Moon ${dm(360 - ph.elongation)} behind the Sun.`);
  else if (sinceNew < 30) out.push(`Born ${fmtHours(sinceNew)} after the New Moon.`);
  else if (Math.abs(toFull) < 30) out.push(`Born ${fmtHours(Math.abs(toFull))} ${toFull > 0 ? "before" : "after"} the Full Moon.`);
  else out.push(`${ph.name} Moon, ${ph.illumination}% lit.`);

  // Sign boundaries the Moon or Sun had just crossed or were about to cross.
  for (const b of [moon, sun]) {
    if (b.degree < 1 || b.degree > 29) {
      const s0 = signIndex(b.lon);
      const step = b.name === "Moon" ? 6 * HOUR : 48 * HOUR;
      const back = b.degree < 1;
      const t = bisect(back ? ms - step : ms, back ? ms : ms + step, (x) => signIndex(positions(x)[b.name].lon) === (back ? signIndex(b.lon - 1) : s0));
      const hrs = Math.abs(ms - t) / HOUR;
      out.push(back
        ? `The ${b.name} had entered ${b.sign} only ${fmtHours(hrs)} earlier. A time more than ${fmtHours(hrs)} earlier puts it in ${SIGNS[(s0 + 11) % 12]}.`
        : `The ${b.name} was ${fmtHours(hrs)} from leaving ${b.sign} for ${SIGNS[(s0 + 1) % 12]}.`);
    }
  }

  // Rising sign sensitivity.
  if (chart.angles && chart.location) {
    const { latitude, longitude } = chart.location;
    const s0 = signIndex(chart.angles.ascendant.lon);
    const ascAt = (t: number): number => signIndex(angles(t, latitude, longitude).asc);
    let early = 0, late = 0;
    while (early < 240 && ascAt(ms - (early + 1) * 60e3) === s0) early++;
    while (late < 240 && ascAt(ms + (late + 1) * 60e3) === s0) late++;
    if (Math.min(early, late) < 20) {
      out.push(early < late
        ? `The rising sign turned ${chart.angles.ascendant.sign} only ${early + 1} minutes before this time; an earlier time gives ${SIGNS[(s0 + 11) % 12]} rising.`
        : `${chart.angles.ascendant.sign} rising holds for ${late + 1} more minutes; a later time gives ${SIGNS[(s0 + 1) % 12]} rising.`);
    }
  }

  // Stelliums.
  const bySign = new Map<number, string[]>();
  for (const b of chart.bodies) {
    const s = signIndex(b.lon);
    bySign.set(s, [...(bySign.get(s) ?? []), b.name]);
  }
  for (const [s, names] of bySign) {
    if (names.length >= 3) out.push(`${["", "", "", "Three", "Four", "Five", "Six", "Seven"][names.length]} bodies in ${SIGNS[s]}: ${names.join(", ")}.`);
  }

  const rx = chart.bodies.filter((b) => b.retrograde).map((b) => b.name);
  if (rx.length) {
    const list = rx.length === 1 ? rx[0] : `${rx.slice(0, -1).join(", ")} and ${rx[rx.length - 1]}`;
    out.push(`${list} ${rx.length === 1 ? "was" : "were"} retrograde.`);
  }
  out.push(`Dominant element: ${chart.balance.dominant_element}. Dominant mode: ${chart.balance.dominant_modality}.`);
  return out;
}

export interface ChartRequest {
  moment: Moment;
  name?: string | null;
  location?: { latitude: number; longitude: number; place?: string | null } | null;
  house_system?: HouseSystem;
  kind?: "chart" | "sky";
}

export function computeChart(req: ChartRequest): Chart {
  const ms = req.moment.ms;
  const pos = positions(ms), spd = speeds(ms);
  const loc = req.location ?? null;
  const ang = loc ? angles(ms, loc.latitude, loc.longitude) : angles(ms, 0, 0);
  const hs: HouseSystem | null = loc ? req.house_system ?? "equal" : null;
  const houseStart = hs === "whole_sign" ? signIndex(ang.asc) * 30 : ang.asc;
  const houseOf = (lon: number): number | null => (hs ? Math.floor(rev(lon - houseStart) / 30) + 1 : null);

  const bodies: ChartBody[] = BODY_NAMES.map((name) => ({
    name,
    glyph: BODY_GLYPHS[name],
    ...zodiacPoint(pos[name].lon),
    lat: round(pos[name].lat, 3),
    speed: round(spd[name], 4),
    retrograde: spd[name] < 0,
    house: houseOf(pos[name].lon),
  }));

  const pts: PointState[] = bodies.map((b) => ({ name: b.name, lon: b.lon, speed: b.speed }));
  if (loc) pts.push({ name: "Ascendant", lon: ang.asc, speed: null }, { name: "Midheaven", lon: ang.mc, speed: null });

  const base: Omit<Chart, "highlights"> = {
    kind: req.kind ?? "chart",
    name: req.name ?? null,
    moment: req.moment,
    location: loc ? { latitude: loc.latitude, longitude: loc.longitude, place: loc.place ?? null } : null,
    house_system: hs,
    bodies,
    angles: loc
      ? { ascendant: zodiacPoint(ang.asc), midheaven: zodiacPoint(ang.mc), descendant: zodiacPoint(ang.asc + 180), imum_coeli: zodiacPoint(ang.mc + 180) }
      : null,
    houses: hs ? Array.from({ length: 12 }, (_, i) => ({ house: i + 1, cusp: zodiacPoint(houseStart + i * 30) })) : null,
    nodes: { north: zodiacPoint(ang.node), south: zodiacPoint(ang.node + 180) },
    aspects: findAspects(pts, pts, true),
    balance: balance(bodies),
    moon_phase: moonPhase(pos.Sun.lon, pos.Moon.lon),
    big_three: { sun: SIGNS[signIndex(pos.Sun.lon)], moon: SIGNS[signIndex(pos.Moon.lon)], rising: loc ? SIGNS[signIndex(ang.asc)] : null },
    precision_note: PRECISION_NOTE,
  };
  return { ...base, highlights: highlights(base, ms) };
}

const pointStates = (c: Chart): PointState[] => {
  const pts: PointState[] = c.bodies.map((b) => ({ name: b.name, lon: b.lon, speed: b.speed }));
  if (c.angles) pts.push({ name: "Ascendant", lon: c.angles.ascendant.lon, speed: null }, { name: "Midheaven", lon: c.angles.midheaven.lon, speed: null });
  return pts;
};

export function compareCharts(a: Chart, b: Chart): Comparison {
  const na = a.name ?? "Person A", nb = b.name ?? "Person B";
  // Natal positions are fixed, so applying/separating has no meaning between two charts.
  const freeze = (p: PointState): PointState => ({ ...p, speed: p.speed === null ? null : 0 });
  const cross: CrossAspect[] = findAspects(pointStates(a).map(freeze), pointStates(b).map(freeze), false, 0.75)
    .map((x) => ({ ...x, applying: null, a_owner: na, b_owner: nb }));

  const shared: string[] = [];
  const pairs: [string, string | null, string | null][] = [
    ["Sun", a.big_three.sun, b.big_three.sun],
    ["Moon", a.big_three.moon, b.big_three.moon],
    ["Rising", a.big_three.rising, b.big_three.rising],
  ];
  for (const [what, x, y] of pairs) if (x && x === y) shared.push(`Both have the ${what} in ${x}.`);
  if (a.big_three.sun === b.big_three.moon) shared.push(`${na}'s Sun sign is ${nb}'s Moon sign (${a.big_three.sun}).`);
  if (b.big_three.sun === a.big_three.moon) shared.push(`${nb}'s Sun sign is ${na}'s Moon sign (${b.big_three.sun}).`);

  const overlays: Comparison["house_overlays"] = [];
  const overlay = (owner: string, src: Chart, host: Chart, hostName: string): void => {
    if (!host.houses) return;
    const start = host.houses[0].cusp.lon;
    for (const body of src.bodies) overlays.push({ owner, body: body.name, in_houses_of: hostName, house: Math.floor(rev(body.lon - start) / 30) + 1 });
  };
  overlay(na, a, b, nb);
  overlay(nb, b, a, na);

  const hl: string[] = [...shared];
  const tight = cross.filter((x) => x.orb < 1).length;
  hl.push(`${cross.length} cross-chart aspects within orb; ${tight} of them are within 1°.`);
  const sunMoon = cross.find((x) => (x.a === "Sun" && x.b === "Moon") || (x.a === "Moon" && x.b === "Sun"));
  if (sunMoon) hl.push(`${sunMoon.a_owner}'s ${sunMoon.a} ${sunMoon.aspect} ${sunMoon.b_owner}'s ${sunMoon.b} (orb ${dm(sunMoon.orb)}), a classic compatibility contact.`);
  const ea = a.balance.dominant_element, eb = b.balance.dominant_element;
  hl.push(ea === eb ? `Both charts lean ${ea}.` : `${na} leans ${ea}; ${nb} leans ${eb}.`);
  return { kind: "comparison", charts: [a, b], cross_aspects: cross, shared_signs: shared, house_overlays: overlays, highlights: hl, precision_note: PRECISION_NOTE };
}
