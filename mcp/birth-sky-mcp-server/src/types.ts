import type { BodyName } from "./services/ephemeris.js";
import type { Moment } from "./services/time.js";

export type HouseSystem = "equal" | "whole_sign";
export type AspectName = "conjunction" | "sextile" | "square" | "trine" | "opposition";
export type PointName = BodyName | "Ascendant" | "Midheaven";

export interface ZodiacPoint {
  /** Ecliptic longitude, 0–360°. */
  lon: number;
  sign: string;
  sign_glyph: string;
  /** Degrees into the sign, 0–30. */
  degree: number;
  /** Degree and arcminute within the sign, e.g. 23°21′. */
  dm: string;
}

export interface ChartBody extends ZodiacPoint {
  name: BodyName;
  glyph: string;
  /** Ecliptic latitude in degrees. */
  lat: number;
  /** Daily motion in degrees; negative when retrograde. */
  speed: number;
  retrograde: boolean;
  /** House number, or null when no birthplace was given. */
  house: number | null;
}

export interface Aspect {
  a: PointName;
  b: PointName;
  aspect: AspectName;
  glyph: string;
  /** Exact angle of the aspect, e.g. 90. */
  angle: number;
  /** Distance from exact, in degrees. */
  orb: number;
  /** True when the faster body is moving toward exact; null when an angle is involved. */
  applying: boolean | null;
}

export interface Balance {
  elements: Record<"Fire" | "Earth" | "Air" | "Water", number>;
  modalities: Record<"Cardinal" | "Fixed" | "Mutable", number>;
  dominant_element: string;
  dominant_modality: string;
}

export interface MoonPhase {
  name: string;
  /** Percent of the disc lit. */
  illumination: number;
  /** Moon minus Sun longitude, 0–360°. */
  elongation: number;
  waxing: boolean;
}

export interface Chart {
  kind: "chart" | "sky";
  name: string | null;
  moment: Moment;
  location: { latitude: number; longitude: number; place: string | null } | null;
  house_system: HouseSystem | null;
  bodies: ChartBody[];
  angles: { ascendant: ZodiacPoint; midheaven: ZodiacPoint; descendant: ZodiacPoint; imum_coeli: ZodiacPoint } | null;
  houses: { house: number; cusp: ZodiacPoint }[] | null;
  nodes: { north: ZodiacPoint; south: ZodiacPoint };
  aspects: Aspect[];
  balance: Balance;
  moon_phase: MoonPhase;
  big_three: { sun: string; moon: string; rising: string | null };
  highlights: string[];
  precision_note: string;
}

export interface CrossAspect extends Aspect {
  /** Whose point `a` and `b` belong to. */
  a_owner: string;
  b_owner: string;
}

export interface Comparison {
  kind: "comparison";
  charts: [Chart, Chart];
  cross_aspects: CrossAspect[];
  shared_signs: string[];
  /** Where each person's bodies fall in the other's houses (only when both have birthplaces). */
  house_overlays: { owner: string; body: BodyName; in_houses_of: string; house: number }[];
  highlights: string[];
  precision_note: string;
}

export interface TransitHit {
  utc: string;
  transiting: BodyName;
  transiting_position: string;
  transiting_retrograde: boolean;
  aspect: AspectName;
  glyph: string;
  natal_point: PointName;
  natal_position: string;
}

export type SkyEventType = "ingress" | "station" | "new_moon" | "first_quarter" | "full_moon" | "last_quarter";

export interface SkyEvent {
  utc: string;
  type: SkyEventType;
  body: BodyName;
  /** One-line plain description, e.g. "Mars enters Leo". */
  summary: string;
  position: string;
  /** For ingresses: sign entered; for stations: "retrograde" or "direct". */
  detail: string;
  /** Approximate eclipse classification for new and full moons near a lunar node. */
  eclipse: "solar" | "lunar" | null;
}

export interface Page<T> {
  total: number;
  count: number;
  offset: number;
  has_more: boolean;
  next_offset: number | null;
  items: T[];
}
