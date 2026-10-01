/**
 * Low-precision geocentric ephemeris after Paul Schlyter, "How to compute planetary positions".
 *
 * Returns tropical ecliptic longitudes of date. Against PyEphem the worst error found between
 * 1900 and 2100 is about 6 arcminutes (Pluto); the Sun and Moon stay within about 2 arcminutes.
 */

export const BODY_NAMES = [
  "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
] as const;
export type BodyName = (typeof BODY_NAMES)[number];

export interface EclipticPosition {
  /** Ecliptic longitude in degrees, 0 to 360. */
  lon: number;
  /** Ecliptic latitude in degrees. */
  lat: number;
}

export type Positions = Record<BodyName, EclipticPosition>;

const R = Math.PI / 180;
export const rev = (x: number): number => ((x % 360) + 360) % 360;
/** Signed difference a − b folded into (−180, 180]. */
export const diff180 = (a: number, b: number): number => {
  const d = rev(a - b);
  return d > 180 ? d - 360 : d;
};
const sin = (x: number): number => Math.sin(x * R);
const cos = (x: number): number => Math.cos(x * R);
const atan2 = (y: number, x: number): number => Math.atan2(y, x) / R;

type Elements = [N: number, i: number, w: number, a: number, e: number, M: number];

const EL: Record<Exclude<BodyName, "Pluto">, (d: number) => Elements> = {
  Sun: (d) => [0, 0, 282.9404 + 4.70935e-5 * d, 1, 0.016709 - 1.151e-9 * d, 356.047 + 0.9856002585 * d],
  Moon: (d) => [125.1228 - 0.0529538083 * d, 5.1454, 318.0634 + 0.1643573223 * d, 60.2666, 0.0549, 115.3654 + 13.0649929509 * d],
  Mercury: (d) => [48.3313 + 3.24587e-5 * d, 7.0047 + 5e-8 * d, 29.1241 + 1.01444e-5 * d, 0.387098, 0.205635 + 5.59e-10 * d, 168.6562 + 4.0923344368 * d],
  Venus: (d) => [76.6799 + 2.4659e-5 * d, 3.3946 + 2.75e-8 * d, 54.891 + 1.38374e-5 * d, 0.72333, 0.006773 - 1.302e-9 * d, 48.0052 + 1.6021302244 * d],
  Mars: (d) => [49.5574 + 2.11081e-5 * d, 1.8497 - 1.78e-8 * d, 286.5016 + 2.92961e-5 * d, 1.523688, 0.093405 + 2.516e-9 * d, 18.6021 + 0.5240207766 * d],
  Jupiter: (d) => [100.4542 + 2.76854e-5 * d, 1.303 - 1.557e-7 * d, 273.8777 + 1.64505e-5 * d, 5.20256, 0.048498 + 4.469e-9 * d, 19.895 + 0.0830853001 * d],
  Saturn: (d) => [113.6634 + 2.3898e-5 * d, 2.4886 - 1.081e-7 * d, 339.3939 + 2.97661e-5 * d, 9.55475, 0.055546 - 9.499e-9 * d, 316.967 + 0.0334442282 * d],
  Uranus: (d) => [74.0005 + 1.3978e-5 * d, 0.7733 + 1.9e-8 * d, 96.6612 + 3.0565e-5 * d, 19.18171 - 1.55e-8 * d, 0.047318 + 7.45e-9 * d, 142.5905 + 0.011725806 * d],
  Neptune: (d) => [131.7806 + 3.0173e-5 * d, 1.77 - 2.55e-7 * d, 272.8461 - 6.027e-6 * d, 30.05826 + 3.313e-8 * d, 0.008606 + 2.15e-9 * d, 260.2471 + 0.005995147 * d],
};

function orbit([N, i, w, a, e, M0]: Elements): [number, number, number] {
  const M = rev(M0);
  let E = M + (e / R) * sin(M) * (1 + e * cos(M));
  for (let k = 0; k < 8; k++) E -= (E - (e / R) * sin(E) - M) / (1 - e * cos(E));
  const xv = a * (cos(E) - e);
  const yv = a * Math.sqrt(1 - e * e) * sin(E);
  const v = atan2(yv, xv);
  const r = Math.hypot(xv, yv);
  const u = v + w;
  return [
    r * (cos(N) * cos(u) - sin(N) * sin(u) * cos(i)),
    r * (sin(N) * cos(u) + cos(N) * sin(u) * cos(i)),
    r * sin(u) * sin(i),
  ];
}

/** Days since 2000 Jan 0.0 UT, Schlyter's epoch. */
const dayNumber = (ms: number): number => ms / 864e5 + 2440587.5 - 2451543.5;

/** Geocentric ecliptic positions of the ten bodies at a UTC instant (milliseconds since the Unix epoch). */
export function positions(ms: number): Positions {
  const d = dayNumber(ms);
  const sE = EL.Sun(d);
  const [xs, ys] = orbit(sE);
  const out = {} as Positions;
  out.Sun = { lon: rev(atan2(ys, xs)), lat: 0 };

  // Moon, with the main perturbation terms.
  const mE = EL.Moon(d);
  const [xm, ym, zm] = orbit(mE);
  let lon = atan2(ym, xm);
  let lat = atan2(zm, Math.hypot(xm, ym));
  const Ms = rev(sE[5]), Mm = rev(mE[5]);
  const Ls = Ms + sE[2], Lm = Mm + mE[2] + mE[0];
  const D = Lm - Ls, F = Lm - mE[0];
  lon += -1.274 * sin(Mm - 2 * D) + 0.658 * sin(2 * D) - 0.186 * sin(Ms) - 0.059 * sin(2 * Mm - 2 * D) - 0.057 * sin(Mm - 2 * D + Ms)
    + 0.053 * sin(Mm + 2 * D) + 0.046 * sin(2 * D - Ms) + 0.041 * sin(Mm - Ms) - 0.035 * sin(D) - 0.031 * sin(Mm + Ms)
    - 0.015 * sin(2 * F - 2 * D) + 0.011 * sin(Mm - 4 * D);
  lat += -0.173 * sin(F - 2 * D) - 0.055 * sin(Mm - F - 2 * D) - 0.046 * sin(Mm + F - 2 * D) + 0.033 * sin(F + 2 * D) + 0.017 * sin(2 * Mm + F);
  out.Moon = { lon: rev(lon), lat };

  const Mj = rev(EL.Jupiter(d)[5]), Msa = rev(EL.Saturn(d)[5]), Mu = rev(EL.Uranus(d)[5]);
  for (const name of ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"] as const) {
    let [x, y, z] = orbit(EL[name](d));
    let hl = atan2(y, x);
    let hb = atan2(z, Math.hypot(x, y));
    const r = Math.hypot(x, y, z);
    if (name === "Jupiter") {
      hl += -0.332 * sin(2 * Mj - 5 * Msa - 67.6) - 0.056 * sin(2 * Mj - 2 * Msa + 21) + 0.042 * sin(3 * Mj - 5 * Msa + 21)
        - 0.036 * sin(Mj - 2 * Msa) + 0.022 * cos(Mj - Msa) + 0.023 * sin(2 * Mj - 3 * Msa + 52) - 0.016 * sin(Mj - 5 * Msa - 69);
    }
    if (name === "Saturn") {
      hl += 0.812 * sin(2 * Mj - 5 * Msa - 67.6) - 0.229 * cos(2 * Mj - 4 * Msa - 2) + 0.119 * sin(Mj - 2 * Msa - 3)
        + 0.046 * sin(2 * Mj - 6 * Msa - 69) + 0.014 * sin(Mj - 3 * Msa + 32);
      hb += -0.02 * cos(2 * Mj - 4 * Msa - 2) + 0.018 * sin(2 * Mj - 6 * Msa - 49);
    }
    if (name === "Uranus") hl += 0.04 * sin(Msa - 2 * Mu + 6) + 0.035 * sin(Msa - 3 * Mu + 33) - 0.015 * sin(Mj - Mu + 20);
    x = r * cos(hl) * cos(hb);
    y = r * sin(hl) * cos(hb);
    z = r * sin(hb);
    const xg = x + xs, yg = y + ys;
    out[name] = { lon: rev(atan2(yg, xg)), lat: atan2(z, Math.hypot(xg, yg)) };
  }

  // Pluto: Schlyter's fitted series (heliocentric), converted to geocentric.
  const S = 50.03 + 0.033459652 * d, P = 238.95 + 0.003968789 * d;
  const pl = 238.9508 + 0.00400703 * d - 19.799 * sin(P) + 19.848 * cos(P) + 0.897 * sin(2 * P) - 4.956 * cos(2 * P) + 0.61 * sin(3 * P)
    + 1.211 * cos(3 * P) - 0.341 * sin(4 * P) - 0.19 * cos(4 * P) + 0.128 * sin(5 * P) - 0.034 * cos(5 * P) - 0.038 * sin(6 * P)
    + 0.031 * cos(6 * P) + 0.02 * sin(S - P) - 0.01 * cos(S - P);
  const pb = -3.9082 - 5.453 * sin(P) - 14.975 * cos(P) + 3.527 * sin(2 * P) + 1.673 * cos(2 * P) - 1.051 * sin(3 * P) + 0.328 * cos(3 * P)
    + 0.179 * sin(4 * P) - 0.292 * cos(4 * P) + 0.019 * sin(5 * P) + 0.1 * cos(5 * P) - 0.031 * sin(6 * P) - 0.026 * cos(6 * P) + 0.011 * cos(S - P);
  const pr = 40.72 + 6.68 * cos(P) + 6.9 * sin(P) - 1.18 * cos(2 * P) - 0.03 * sin(2 * P) + 0.15 * cos(3 * P) - 0.14 * sin(3 * P);
  const px = pr * cos(pl) * cos(pb), py = pr * sin(pl) * cos(pb), pz = pr * sin(pb);
  out.Pluto = { lon: rev(atan2(py + ys, px + xs)), lat: atan2(pz, Math.hypot(px + xs, py + ys)) };
  return out;
}

/** Daily motion in degrees (negative when retrograde), from a two-hour central difference. */
export function speeds(ms: number): Record<BodyName, number> {
  const h = 3600e3;
  const a = positions(ms - h), b = positions(ms + h);
  const out = {} as Record<BodyName, number>;
  for (const k of BODY_NAMES) out[k] = diff180(b[k].lon, a[k].lon) * 12;
  return out;
}

export interface Angles {
  asc: number;
  mc: number;
  /** Mean lunar north node. */
  node: number;
}

/** Ascendant, Midheaven and mean node for a UTC instant and a place (latitude °N, longitude °E). */
export function angles(ms: number, lat: number, lonEast: number): Angles {
  const jd = ms / 864e5 + 2440587.5;
  const T = (jd - 2451545) / 36525;
  const gmst = rev(280.46061837 + 360.98564736629 * (jd - 2451545) + 0.000387933 * T * T - (T * T * T) / 38710000);
  const ramc = rev(gmst + lonEast);
  const eps = 23.43929111 - 0.0130041667 * T;
  const asc = rev(atan2(cos(ramc), -(sin(ramc) * cos(eps) + Math.tan(lat * R) * sin(eps))));
  const mc = rev(atan2(sin(ramc), cos(ramc) * cos(eps)));
  const node = rev(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T);
  return { asc, mc, node };
}
