/** Markdown renderings of tool results, plus the shared paging and truncation helpers. */

import { CHARACTER_LIMIT } from "./constants.js";
import { describe, dm } from "./services/astro.js";
import type { Moment } from "./services/time.js";
import type { Chart, Comparison, Page, SkyEvent, TransitHit } from "./types.js";

export function paginate<T>(items: T[], offset: number, limit: number): Page<T> {
  const slice = items.slice(offset, offset + limit);
  const more = offset + slice.length < items.length;
  return { total: items.length, count: slice.length, offset, has_more: more, next_offset: more ? offset + slice.length : null, items: slice };
}

/** Keeps a text response under the character limit, ending with a hint on how to see the rest. */
export function clip(text: string, hint: string): string {
  if (text.length <= CHARACTER_LIMIT) return text;
  return `${text.slice(0, CHARACTER_LIMIT - 200).replace(/\n[^\n]*$/, "")}\n\n…Response truncated at ${CHARACTER_LIMIT} characters. ${hint}`;
}

export function when(m: Moment): string {
  const [date, time] = m.local.split(" ");
  const [y, mo, d] = date.split("-").map(Number);
  const [hh, mi] = time.split(":").map(Number);
  const day = new Date(Date.UTC(y, mo - 1, d)).toLocaleDateString("en-US", { weekday: "short", day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
  const clock = `${((hh + 11) % 12) + 1}:${String(mi).padStart(2, "0")} ${hh < 12 ? "a.m." : "p.m."}`;
  return m.zone_label === "UTC" ? `${day}, ${clock} UTC` : `${day}, ${clock} ${m.zone_label} (${m.utc.replace("T", " ").replace(/:00Z$/, " UTC").replace("Z", " UTC")})`;
}

const yesNo = (b: boolean | null): string => (b === null ? "" : b ? " · applying" : " · separating");

export function chartMarkdown(c: Chart): string {
  const L: string[] = [];
  const title = c.kind === "sky" ? "The sky" : c.name ? `${c.name}'s birth chart` : "Birth chart";
  L.push(`# ${title}`, "");
  L.push(`**${when(c.moment)}**${c.location ? ` · ${c.location.place ?? `${c.location.latitude}°, ${c.location.longitude}°`}` : ""}`, "");
  L.push(`**Sun** ${c.big_three.sun} · **Moon** ${c.big_three.moon}${c.big_three.rising ? ` · **Rising** ${c.big_three.rising}` : ""}`, "");
  for (const h of c.highlights) L.push(`- ${h}`);
  L.push("", "## Positions", "", `| Body | Sign | Degree |${c.house_system ? " House |" : ""} |`, `|---|---|---|${c.house_system ? "---|" : ""}---|`);
  for (const b of c.bodies) L.push(`| ${b.glyph} ${b.name} | ${b.sign} | ${b.dm} |${b.house !== null ? ` ${b.house} |` : ""} ${b.retrograde ? "℞ retrograde" : ""} |`);
  if (c.angles) {
    L.push(`| AC Ascendant | ${c.angles.ascendant.sign} | ${c.angles.ascendant.dm} | 1 | |`);
    L.push(`| MC Midheaven | ${c.angles.midheaven.sign} | ${c.angles.midheaven.dm} | 10 | |`);
  }
  L.push("", `Mean North Node ${describe(c.nodes.north)}. Moon phase: ${c.moon_phase.name}, ${c.moon_phase.illumination}% lit.`);
  if (c.house_system) L.push(`Houses: ${c.house_system === "equal" ? "equal, 30° each from the Ascendant" : "whole sign"}.`);
  L.push("", "## Aspects", "");
  if (!c.aspects.length) L.push("No major aspects within orb.");
  for (const a of c.aspects) L.push(`- ${a.a} ${a.glyph} ${a.aspect} ${a.b} — orb ${dm(a.orb)}${yesNo(a.applying)}`);
  const e = c.balance.elements, m = c.balance.modalities;
  L.push("", "## Balance of the ten bodies", "", `Fire ${e.Fire} · Earth ${e.Earth} · Air ${e.Air} · Water ${e.Water}`, `Cardinal ${m.Cardinal} · Fixed ${m.Fixed} · Mutable ${m.Mutable}`);
  L.push("", `_${c.precision_note}_`);
  return L.join("\n");
}

export function comparisonMarkdown(x: Comparison): string {
  const [a, b] = x.charts;
  const na = a.name ?? "Person A", nb = b.name ?? "Person B";
  const L: string[] = [`# ${na} & ${nb}`, ""];
  for (const c of [a, b]) {
    L.push(`**${c.name ?? "—"}** — ${when(c.moment)}${c.location?.place ? `, ${c.location.place}` : ""}`);
    L.push(`Sun ${c.big_three.sun} · Moon ${c.big_three.moon}${c.big_three.rising ? ` · Rising ${c.big_three.rising}` : ""}`, "");
  }
  for (const h of x.highlights) L.push(`- ${h}`);
  L.push("", "## Where the charts meet", "");
  if (!x.cross_aspects.length) L.push("No cross-chart aspects within orb.");
  for (const c of x.cross_aspects) L.push(`- ${c.a_owner}'s ${c.a} ${c.glyph} ${c.aspect} ${c.b_owner}'s ${c.b} — orb ${dm(c.orb)}`);
  if (x.house_overlays.length) {
    L.push("", "## House overlays", "");
    for (const owner of [na, nb]) {
      const rows = x.house_overlays.filter((o) => o.owner === owner);
      if (rows.length) L.push(`- ${owner}'s bodies in ${rows[0].in_houses_of}'s houses: ${rows.map((o) => `${o.body} ${o.house}`).join(", ")}`);
    }
  }
  L.push("", "## Balance", "", "| | Fire | Earth | Air | Water | Cardinal | Fixed | Mutable |", "|---|---|---|---|---|---|---|---|");
  for (const c of [a, b]) {
    const e = c.balance.elements, m = c.balance.modalities;
    L.push(`| ${c.name ?? "—"} | ${e.Fire} | ${e.Earth} | ${e.Air} | ${e.Water} | ${m.Cardinal} | ${m.Fixed} | ${m.Mutable} |`);
  }
  L.push("", `_${x.precision_note}_`);
  return L.join("\n");
}

export function transitsMarkdown(name: string | null, page: Page<TransitHit>, range: string): string {
  const L = [`# Transits to ${name ? `${name}'s` : "the"} chart, ${range}`, "", `${page.total} exact hits; showing ${page.offset + 1}–${page.offset + page.count}.`, ""];
  for (const h of page.items) {
    L.push(`- **${h.utc.replace("T", " ").replace("Z", " UTC")}** — ${h.transiting}${h.transiting_retrograde ? " ℞" : ""} ${h.glyph} ${h.aspect} natal ${h.natal_point} (${h.transiting_position} → ${h.natal_position})`);
  }
  if (page.has_more) L.push("", `More results: call again with offset=${page.next_offset}.`);
  return L.join("\n");
}

export function eventsMarkdown(page: Page<SkyEvent>, range: string): string {
  const L = [`# Sky events, ${range}`, "", `${page.total} events; showing ${page.total ? page.offset + 1 : 0}–${page.offset + page.count}.`, ""];
  for (const e of page.items) L.push(`- **${e.utc.replace("T", " ").replace("Z", " UTC")}** — ${e.summary} at ${e.position}`);
  if (page.has_more) L.push("", `More results: call again with offset=${page.next_offset}.`);
  return L.join("\n");
}
