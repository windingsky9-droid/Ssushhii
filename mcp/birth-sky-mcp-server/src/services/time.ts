/** Turns a local date and clock time plus a time zone (IANA name or fixed UTC offset) into a UTC instant. */

import { MAX_YEAR, MIN_YEAR } from "../constants.js";

export interface MomentInput {
  date: string;
  time?: string;
  timezone?: string;
  utc_offset?: number;
}

export interface Moment {
  /** Milliseconds since the Unix epoch, UTC. */
  ms: number;
  utc: string;
  /** Local wall-clock date and time as given, `YYYY-MM-DD HH:MM`. */
  local: string;
  /** Offset from UTC in hours at that instant, e.g. -5 or 5.5. */
  utc_offset: number;
  /** IANA zone if one was given. */
  timezone: string | null;
  /** Short zone label such as CDT or GMT+5:30. */
  zone_label: string;
}

export class InputError extends Error {}

const DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
const TIME_RE = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/;

function zoneFormatter(timeZone: string): Intl.DateTimeFormat {
  try {
    return new Intl.DateTimeFormat("en-US", {
      timeZone, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit", timeZoneName: "short",
    });
  } catch {
    throw new InputError(
      `Unknown time zone '${timeZone}'. Use an IANA name such as 'America/Chicago', 'Europe/London' or 'Asia/Kolkata', or pass utc_offset in hours instead.`,
    );
  }
}

/** Offset of an IANA zone from UTC, in minutes, at a UTC instant. Includes historical rules (DST, war time, LMT). */
function offsetMinutes(fmt: Intl.DateTimeFormat, ms: number): { minutes: number; label: string } {
  const parts = Object.fromEntries(fmt.formatToParts(new Date(ms)).map((p) => [p.type, p.value]));
  const asUtc = Date.UTC(+parts.year, +parts.month - 1, +parts.day, +parts.hour % 24, +parts.minute, +parts.second);
  const minutes = Math.round((asUtc - Math.floor(ms / 1000) * 1000) / 60000);
  // Intl only names some zones (CDT, GMT); show the rest as UTC−6 rather than GMT-6.
  const name = parts.timeZoneName && !/^GMT[+-]/.test(parts.timeZoneName) ? parts.timeZoneName : timeZoneLabel(minutes / 60);
  return { minutes, label: name };
}

function timeZoneLabel(hours: number): string {
  if (hours === 0) return "UTC";
  const sign = hours < 0 ? "−" : "+";
  const a = Math.abs(hours), h = Math.floor(a), m = Math.round((a - h) * 60);
  return `UTC${sign}${h}${m ? ":" + String(m).padStart(2, "0") : ""}`;
}

const pad = (n: number): string => String(n).padStart(2, "0");

export function resolveMoment(input: MomentInput): Moment {
  const dm = DATE_RE.exec(input.date.trim());
  if (!dm) throw new InputError(`Date '${input.date}' is not in YYYY-MM-DD form, e.g. '1999-07-04'.`);
  const [y, mo, d] = [+dm[1], +dm[2], +dm[3]];
  if (y < MIN_YEAR || y > MAX_YEAR) {
    throw new InputError(`Year ${y} is outside the supported range ${MIN_YEAR}–${MAX_YEAR}, where the ephemeris is accurate to a few arcminutes.`);
  }
  const check = new Date(Date.UTC(y, mo - 1, d));
  if (check.getUTCMonth() !== mo - 1 || check.getUTCDate() !== d) throw new InputError(`Date '${input.date}' does not exist.`);

  const tm = TIME_RE.exec((input.time ?? "12:00").trim());
  if (!tm) throw new InputError(`Time '${input.time}' is not in 24-hour HH:MM form, e.g. '18:45' for 6:45 p.m.`);
  const [hh, mi, ss] = [+tm[1], +tm[2], tm[3] ? +tm[3] : 0];
  if (hh > 23 || mi > 59 || ss > 59) throw new InputError(`Time '${input.time}' is out of range.`);

  const wall = Date.UTC(y, mo - 1, d, hh, mi, ss);
  let ms: number, offset: number, label: string;
  if (input.utc_offset !== undefined) {
    offset = input.utc_offset;
    ms = wall - offset * 3600e3;
    label = timeZoneLabel(offset);
  } else if (input.timezone) {
    const fmt = zoneFormatter(input.timezone);
    // Two passes settle the offset across DST transitions.
    let o = offsetMinutes(fmt, wall);
    ms = wall - o.minutes * 60e3;
    o = offsetMinutes(fmt, ms);
    ms = wall - o.minutes * 60e3;
    offset = o.minutes / 60;
    label = o.label;
  } else {
    throw new InputError(
      "Give either 'timezone' (an IANA name such as 'America/Mexico_City') or 'utc_offset' in hours. The time zone decides the UTC instant, which moves the Moon about 0.5° per hour and the rising sign about 1° every 4 minutes.",
    );
  }
  return {
    ms,
    utc: new Date(ms).toISOString().replace(".000Z", "Z"),
    local: `${y}-${pad(mo)}-${pad(d)} ${pad(hh)}:${pad(mi)}`,
    utc_offset: offset,
    timezone: input.utc_offset === undefined ? input.timezone ?? null : null,
    zone_label: label,
  };
}

/** A UTC instant as a Moment with offset 0, for ranges and "now". */
export function utcMoment(ms: number): Moment {
  const t = new Date(ms);
  return {
    ms,
    utc: t.toISOString().replace(/\.\d{3}Z$/, "Z"),
    local: `${t.getUTCFullYear()}-${pad(t.getUTCMonth() + 1)}-${pad(t.getUTCDate())} ${pad(t.getUTCHours())}:${pad(t.getUTCMinutes())}`,
    utc_offset: 0,
    timezone: "UTC",
    zone_label: "UTC",
  };
}

/** Parses a YYYY-MM-DD date (start of day, UTC) for range searches. */
export function parseDay(s: string, field: string): number {
  const m = DATE_RE.exec(s.trim());
  if (!m) throw new InputError(`${field} '${s}' is not in YYYY-MM-DD form.`);
  const y = +m[1];
  if (y < MIN_YEAR || y > MAX_YEAR) throw new InputError(`${field} year ${y} is outside ${MIN_YEAR}–${MAX_YEAR}.`);
  return Date.UTC(y, +m[2] - 1, +m[3]);
}
