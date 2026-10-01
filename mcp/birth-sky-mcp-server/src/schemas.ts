import { z } from "zod";
import { BODY_NAMES } from "./services/ephemeris.js";

export const ResponseFormat = z.enum(["markdown", "json"]).default("markdown")
  .describe("'markdown' (default) for a readable report, 'json' for the full structured result.");

const Body = z.enum(BODY_NAMES);
const Aspect = z.enum(["conjunction", "sextile", "square", "trine", "opposition"]);
const Point = z.enum([...BODY_NAMES, "Ascendant", "Midheaven"]);

const DATE = /^\d{4}-\d{2}-\d{2}$/;
const TIME = /^\d{1,2}:\d{2}(:\d{2})?$/;

/** Fields that pin down one moment and (optionally) one place. */
export const birthShape = {
  name: z.string().trim().min(1).max(60).optional().describe("Label for the person or event, e.g. 'Ada'."),
  date: z.string().regex(DATE, "Use YYYY-MM-DD, e.g. '1999-07-04'.").describe("Local calendar date of birth, YYYY-MM-DD (1900–2100)."),
  time: z.string().regex(TIME, "Use 24-hour HH:MM, e.g. '18:45'.").default("12:00")
    .describe("Local 24-hour clock time, HH:MM (e.g. '06:30', '18:45'). If unknown use '12:00'; the Moon may then be off by up to 7° and the rising sign is unreliable."),
  timezone: z.string().trim().max(64).optional()
    .describe("IANA time zone of the birthplace, e.g. 'America/Chicago', 'America/Mexico_City', 'Asia/Kolkata'. Historical daylight-saving rules are applied. Preferred over utc_offset."),
  utc_offset: z.number().min(-14).max(14).optional()
    .describe("Fixed offset from UTC in hours at the birth moment, e.g. -5 or 5.5. Overrides timezone. Use when the zone is unknown but the offset is."),
  latitude: z.number().min(-66.5).max(66.5).optional()
    .describe("Birthplace latitude in degrees, north positive (e.g. 29.76 for Houston). Needed for the rising sign, Midheaven and houses."),
  longitude: z.number().min(-180).max(180).optional()
    .describe("Birthplace longitude in degrees, EAST positive, WEST negative (e.g. -95.37 for Houston)."),
  place: z.string().trim().max(80).optional().describe("Birthplace name for display, e.g. 'Houston, Texas'."),
};
export const BirthSchema = z.object(birthShape).strict();
export type BirthInput = z.infer<typeof BirthSchema>;

export const ChartInputSchema = z.object({
  ...birthShape,
  house_system: z.enum(["equal", "whole_sign"]).default("equal")
    .describe("'equal' (30° houses from the Ascendant degree, default) or 'whole_sign' (each sign is one house)."),
  response_format: ResponseFormat,
}).strict();

export const SkyInputSchema = z.object({
  date: z.string().regex(DATE, "Use YYYY-MM-DD.").optional().describe("Local date, YYYY-MM-DD. Omit for right now."),
  time: z.string().regex(TIME, "Use 24-hour HH:MM.").optional().describe("Local 24-hour time, HH:MM. Defaults to 12:00 when a date is given."),
  timezone: z.string().trim().max(64).optional().describe("IANA time zone for date/time, e.g. 'Europe/London'. Defaults to UTC."),
  utc_offset: z.number().min(-14).max(14).optional().describe("Fixed UTC offset in hours; overrides timezone."),
  latitude: z.number().min(-66.5).max(66.5).optional().describe("Observer latitude, north positive. Adds the rising sign and houses."),
  longitude: z.number().min(-180).max(180).optional().describe("Observer longitude, east positive, west negative."),
  place: z.string().trim().max(80).optional().describe("Place name for display."),
  upcoming_days: z.number().int().min(0).max(90).default(30)
    .describe("Also list sign changes, stations and lunations in this many days after the moment (0 to skip; default 30)."),
  response_format: ResponseFormat,
}).strict();

export const CompareInputSchema = z.object({
  person_a: BirthSchema.describe("First person's birth data. The comparison wheel uses this person's houses."),
  person_b: BirthSchema.describe("Second person's birth data."),
  response_format: ResponseFormat,
}).strict();

export const TransitsInputSchema = z.object({
  natal: BirthSchema.describe("Birth data of the chart that receives the transits."),
  start_date: z.string().regex(DATE, "Use YYYY-MM-DD.").describe("First day searched (UTC), YYYY-MM-DD."),
  end_date: z.string().regex(DATE, "Use YYYY-MM-DD.").describe("Last day searched (UTC, inclusive), YYYY-MM-DD. Up to 3 years after start_date, or 62 days when 'Moon' is transiting."),
  transiting: z.array(Body).min(1).optional()
    .describe("Moving bodies to track. Default: Sun through Pluto without the Moon (the Moon makes ~1 aspect per day per point)."),
  natal_points: z.array(Point).min(1).optional()
    .describe("Natal points to receive aspects. Default: all ten bodies plus Ascendant and Midheaven (angles only when the birthplace is given)."),
  aspects: z.array(Aspect).min(1).optional().describe("Aspect types. Default: all five major aspects."),
  limit: z.number().int().min(1).max(200).default(50).describe("Maximum hits to return (default 50)."),
  offset: z.number().int().min(0).default(0).describe("Hits to skip, for paging."),
  response_format: ResponseFormat,
}).strict();

export const EventsInputSchema = z.object({
  start_date: z.string().regex(DATE, "Use YYYY-MM-DD.").describe("First day searched (UTC), YYYY-MM-DD."),
  end_date: z.string().regex(DATE, "Use YYYY-MM-DD.").describe("Last day searched (UTC, inclusive). Up to 5 years after start_date, or 1 year when Moon ingresses are requested."),
  types: z.array(z.enum(["ingress", "station", "new_moon", "first_quarter", "full_moon", "last_quarter"])).min(1).optional()
    .describe("Event types. Default: all. 'ingress' = a body enters a sign; 'station' = a planet turns retrograde or direct; the rest are Moon phases (new and full moons flag eclipses)."),
  bodies: z.array(Body).min(1).optional()
    .describe("Bodies for ingresses and stations. Default: all except the Moon. Add 'Moon' to include its sign changes (every ~2.5 days)."),
  limit: z.number().int().min(1).max(200).default(50).describe("Maximum events to return (default 50)."),
  offset: z.number().int().min(0).default(0).describe("Events to skip, for paging."),
  response_format: ResponseFormat,
}).strict();
