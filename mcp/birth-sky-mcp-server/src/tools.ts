import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { registerAppTool } from "@modelcontextprotocol/ext-apps/server";
import { VIEW_URI } from "./constants.js";
import { chartMarkdown, clip, comparisonMarkdown, eventsMarkdown, paginate, transitsMarkdown } from "./format.js";
import {
  BirthSchema, type BirthInput, ChartInputSchema, CompareInputSchema, EventsInputSchema, SkyInputSchema, TransitsInputSchema,
} from "./schemas.js";
import { compareCharts, computeChart } from "./services/astro.js";
import { BODY_NAMES } from "./services/ephemeris.js";
import { DEFAULT_TRANSITING, findEvents, findTransits } from "./services/events.js";
import { InputError, parseDay, resolveMoment, utcMoment } from "./services/time.js";
import type { Chart, HouseSystem, PointName, SkyEventType } from "./types.js";

const DAY = 864e5;
const READ_ONLY = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false } as const;
const UI = { ui: { resourceUri: VIEW_URI } };

function ok(text: string, structured: object): CallToolResult {
  return { content: [{ type: "text", text }], structuredContent: structured as Record<string, unknown> };
}

function fail(error: unknown): CallToolResult {
  const msg = error instanceof InputError
    ? `Error: ${error.message}`
    : `Error: the calculation failed (${error instanceof Error ? error.message : String(error)}). Check the dates and coordinates and try again.`;
  return { isError: true, content: [{ type: "text", text: msg }] };
}

function birthChart(b: BirthInput, house_system: HouseSystem = "equal"): Chart {
  if ((b.latitude === undefined) !== (b.longitude === undefined)) {
    throw new InputError("Give both latitude and longitude for the birthplace, or neither (then the rising sign and houses are skipped).");
  }
  if (b.timezone === undefined && b.utc_offset === undefined) {
    throw new InputError(
      `No time zone for ${b.name ?? "this birth"}. Pass 'timezone' as an IANA name for the birthplace (e.g. 'America/Chicago') or 'utc_offset' in hours. The zone fixes the UTC moment, which moves the Moon about 0.5° and the rising sign about 15° per hour.`,
    );
  }
  const moment = resolveMoment({ date: b.date, time: b.time, timezone: b.timezone, utc_offset: b.utc_offset });
  const location = b.latitude !== undefined && b.longitude !== undefined ? { latitude: b.latitude, longitude: b.longitude, place: b.place ?? null } : null;
  return computeChart({ moment, name: b.name ?? null, location, house_system });
}

function dayRange(start: string, end: string, maxDays: number, why: string): [number, number] {
  const a = parseDay(start, "start_date"), b = parseDay(end, "end_date") + DAY;
  if (b <= a) throw new InputError("end_date must be on or after start_date.");
  if ((b - a) / DAY > maxDays) throw new InputError(`The range is ${Math.round((b - a) / DAY)} days; the limit is ${maxDays} days ${why}. Split it into smaller ranges.`);
  return [a, b];
}

const BIRTH_ARGS = `  - name (string, optional): label, e.g. 'Ada'
  - date (string): local date YYYY-MM-DD, 1900–2100
  - time (string): local 24-hour HH:MM (default '12:00' if unknown)
  - timezone (string): IANA zone of the birthplace, e.g. 'America/Chicago' (historical DST applied), OR
  - utc_offset (number): hours from UTC at birth, e.g. -6; one of timezone/utc_offset is required
  - latitude, longitude (numbers, optional): birthplace, north/EAST positive (west longitudes are negative); needed for rising sign, MC and houses
  - place (string, optional): birthplace name for display`;

export function registerTools(server: McpServer): void {
  registerAppTool(server, "birthsky_compute_chart", {
    title: "Compute a birth chart",
    description: `Compute a full natal (birth) chart: where the Sun, Moon and eight planets were in the tropical zodiac, the rising sign (Ascendant) and Midheaven, houses, major aspects, element/mode balance, Moon phase and plain-language highlights. Clients that support MCP Apps also show an interactive chart wheel.

Use for: "what's my zodiac / Sun / Moon / rising sign", "make my birth chart", "where was Venus when I was born". Don't use for two people (use birthsky_compare_charts), for the current sky (birthsky_get_sky), or for future dates against a chart (birthsky_find_transits).

Args:
${BIRTH_ARGS}
  - house_system ('equal' | 'whole_sign'): default 'equal'
  - response_format ('markdown' | 'json'): default 'markdown'

Returns: a chart report. structuredContent always holds the full chart: { kind: "chart", name, moment {utc, local, utc_offset, zone_label}, location, bodies[] {name, sign, degree, dm, lon, lat, speed, retrograde, house}, angles {ascendant, midheaven, descendant, imum_coeli}, houses[], nodes, aspects[] {a, b, aspect, orb, applying}, balance, moon_phase, big_three {sun, moon, rising}, highlights[] }.

Errors: invalid dates or times, unknown time zones, a missing time zone, or a lone latitude/longitude return an explanation of what to fix.`,
    inputSchema: ChartInputSchema,
    annotations: READ_ONLY,
    _meta: UI,
  }, async (args) => {
    try {
      const { response_format, house_system, ...birth } = args;
      const chart = birthChart(birth, house_system);
      return ok(response_format === "json" ? JSON.stringify(chart, null, 2) : chartMarkdown(chart), chart);
    } catch (e) { return fail(e); }
  });

  registerAppTool(server, "birthsky_get_sky", {
    title: "Show the sky at a moment",
    description: `Show where the Sun, Moon and planets are at a moment (default: right now), with the Moon phase and retrogrades, plus upcoming sign changes, retrograde stations and lunations. Adds the rising sign and houses when a latitude/longitude is given. Clients that support MCP Apps show the sky as a zodiac wheel.

Use for: "what sign is the Moon in today", "is Mercury retrograde right now", "what's the sky like on New Year's Eve". Don't use for a person's birth chart (use birthsky_compute_chart).

Args:
  - date (YYYY-MM-DD, optional), time (HH:MM, optional): omit both for now
  - timezone (IANA, optional, default UTC) or utc_offset (hours)
  - latitude, longitude, place (optional): observer location for rising sign and houses
  - upcoming_days (0–90, default 30): window for upcoming events
  - response_format ('markdown' | 'json')

Returns: the same chart structure as birthsky_compute_chart with kind "sky", plus upcoming[] events { utc, type, body, summary, position, eclipse }.`,
    inputSchema: SkyInputSchema,
    annotations: { ...READ_ONLY, idempotentHint: false },
    _meta: UI,
  }, async (args) => {
    try {
      if ((args.latitude === undefined) !== (args.longitude === undefined)) throw new InputError("Give both latitude and longitude, or neither.");
      const moment = args.date
        ? resolveMoment({ date: args.date, time: args.time ?? "12:00", timezone: args.timezone ?? (args.utc_offset === undefined ? "UTC" : undefined), utc_offset: args.utc_offset })
        : utcMoment(Math.floor(Date.now() / 60e3) * 60e3);
      const location = args.latitude !== undefined && args.longitude !== undefined ? { latitude: args.latitude, longitude: args.longitude, place: args.place ?? null } : null;
      const chart = computeChart({ moment, name: args.place ?? null, location, kind: "sky" });
      const upcoming = args.upcoming_days > 0
        ? findEvents({ start: moment.ms, end: moment.ms + args.upcoming_days * DAY, types: ["ingress", "station", "new_moon", "first_quarter", "full_moon", "last_quarter"], bodies: BODY_NAMES.filter((b) => b !== "Moon") })
        : [];
      const result = { ...chart, upcoming };
      if (args.response_format === "json") return ok(JSON.stringify(result, null, 2), result);
      let md = chartMarkdown(chart);
      if (upcoming.length) {
        md += `\n\n## Next ${args.upcoming_days} days\n\n${upcoming.map((e) => `- **${e.utc.replace("T", " ").replace("Z", " UTC")}** — ${e.summary} at ${e.position}`).join("\n")}`;
      }
      return ok(md, result);
    } catch (e) { return fail(e); }
  });

  registerAppTool(server, "birthsky_compare_charts", {
    title: "Compare two birth charts",
    description: `Compare two people's birth charts (synastry): each person's Sun, Moon and rising sign, every cross-chart aspect within orb (tightest first), signs they share, where each person's planets fall in the other's houses, and how their element balance differs. Clients that support MCP Apps show both charts on one wheel.

Use for: "compare my chart with my partner's", "are we compatible astrologically", "how do our charts connect". Don't use for a single chart (birthsky_compute_chart).

Args:
  - person_a, person_b (objects), each with:
${BIRTH_ARGS.replace(/^ {2}/gm, "    ")}
  - response_format ('markdown' | 'json')

Returns: { kind: "comparison", charts: [chartA, chartB], cross_aspects[] {a_owner, a, aspect, b_owner, b, orb}, shared_signs[], house_overlays[] {owner, body, in_houses_of, house}, highlights[] }. Cross-chart orbs are 75% of natal orbs.`,
    inputSchema: CompareInputSchema,
    annotations: READ_ONLY,
    _meta: UI,
  }, async (args) => {
    try {
      const a = birthChart(BirthSchema.parse(args.person_a)), b = birthChart(BirthSchema.parse(args.person_b));
      if (!a.name) a.name = "Person A";
      if (!b.name) b.name = "Person B";
      const cmp = compareCharts(a, b);
      return ok(args.response_format === "json" ? clip(JSON.stringify(cmp, null, 2), "Use response_format='markdown' for a shorter report.") : comparisonMarkdown(cmp), cmp);
    } catch (e) { return fail(e); }
  });

  server.registerTool("birthsky_find_transits", {
    title: "Find transits to a birth chart",
    description: `Find the exact dates when moving planets make major aspects to the points of a birth chart within a date range (e.g. "Saturn squares natal Sun on 2026-03-02"). Each hit is the moment the aspect is exact; retrograde planets can hit the same point up to three times.

Use for: "what's coming up in my chart this year", "when does Jupiter cross my Ascendant", "when is my Saturn return". Don't use for general sky events not tied to a chart (birthsky_find_events).

Args:
  - natal (object): birth data, fields as in birthsky_compute_chart (latitude/longitude needed for Ascendant/Midheaven targets)
  - start_date, end_date (YYYY-MM-DD, UTC, inclusive): up to 3 years apart, or 62 days when the Moon is in 'transiting'
  - transiting (array of body names, optional): default Sun–Pluto without the Moon
  - natal_points (array, optional): bodies and/or 'Ascendant', 'Midheaven'; default all
  - aspects (array, optional): of 'conjunction', 'sextile', 'square', 'trine', 'opposition'; default all
  - limit (1–200, default 50), offset (default 0): paging
  - response_format ('markdown' | 'json')

Returns: { natal_name, total, count, offset, has_more, next_offset, items[] { utc, transiting, transiting_position, transiting_retrograde, aspect, natal_point, natal_position } } sorted by time. Narrow with natal_points, transiting or aspects when total is large.`,
    inputSchema: TransitsInputSchema,
    annotations: READ_ONLY,
  }, async (args) => {
    try {
      const natal = birthChart(BirthSchema.parse(args.natal));
      const transiting = args.transiting ?? DEFAULT_TRANSITING;
      const [start, end] = dayRange(args.start_date, args.end_date, transiting.includes("Moon") ? 62 : 1100,
        transiting.includes("Moon") ? "when the Moon is included" : "for transit searches");
      const points: PointName[] = args.natal_points ?? [...BODY_NAMES, ...(natal.angles ? (["Ascendant", "Midheaven"] as const) : [])];
      if (!natal.angles && points.some((p) => p === "Ascendant" || p === "Midheaven")) {
        throw new InputError("Ascendant and Midheaven need the birthplace latitude and longitude in 'natal'.");
      }
      const hits = findTransits({ natal, start, end, transiting, natal_points: points, aspects: args.aspects ?? ["conjunction", "sextile", "square", "trine", "opposition"] });
      const page = paginate(hits, args.offset, args.limit);
      const result = { natal_name: natal.name, start_date: args.start_date, end_date: args.end_date, ...page };
      const range = `${args.start_date} to ${args.end_date}`;
      return ok(args.response_format === "json" ? JSON.stringify(result, null, 2) : transitsMarkdown(natal.name, page, range), result);
    } catch (e) { return fail(e); }
  });

  server.registerTool("birthsky_find_events", {
    title: "Find sky events in a date range",
    description: `List sky events between two dates: planets entering signs (ingresses), planets turning retrograde or direct (stations), and Moon phases (new, first quarter, full, last quarter), with eclipses flagged on new and full moons.

Use for: "when is Mercury retrograde in 2026", "when does Saturn enter Aries", "next full moon", "eclipses next year". Don't use for aspects to a person's chart (birthsky_find_transits).

Args:
  - start_date, end_date (YYYY-MM-DD, UTC, inclusive): up to 5 years apart (1 year if Moon ingresses are requested)
  - types (array, optional): 'ingress', 'station', 'new_moon', 'first_quarter', 'full_moon', 'last_quarter'; default all
  - bodies (array, optional): bodies for ingresses/stations; default all but the Moon
  - limit (1–200, default 50), offset (default 0): paging
  - response_format ('markdown' | 'json')

Returns: { total, count, offset, has_more, next_offset, items[] { utc, type, body, summary, position, detail, eclipse } } sorted by time. 'eclipse' is "solar" or "lunar" when an eclipse occurs somewhere on Earth, else null.`,
    inputSchema: EventsInputSchema,
    annotations: READ_ONLY,
  }, async (args) => {
    try {
      const bodies = args.bodies ?? BODY_NAMES.filter((b) => b !== "Moon");
      const types = (args.types ?? ["ingress", "station", "new_moon", "first_quarter", "full_moon", "last_quarter"]) as SkyEventType[];
      const moonIngress = bodies.includes("Moon") && types.includes("ingress");
      const [start, end] = dayRange(args.start_date, args.end_date, moonIngress ? 366 : 1830, moonIngress ? "when Moon ingresses are included" : "for event searches");
      const page = paginate(findEvents({ start, end, types, bodies }), args.offset, args.limit);
      const result = { start_date: args.start_date, end_date: args.end_date, ...page };
      return ok(args.response_format === "json" ? JSON.stringify(result, null, 2) : eventsMarkdown(page, `${args.start_date} to ${args.end_date}`), result);
    } catch (e) { return fail(e); }
  });
}
