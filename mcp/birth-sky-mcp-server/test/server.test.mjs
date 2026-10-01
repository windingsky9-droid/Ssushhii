// End-to-end tests: a real MCP client talks to the built server over stdio.
// Run `npm run build` first; `npm test` does both.
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { request } from "node:http";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const entry = fileURLToPath(new URL("../dist/index.js", import.meta.url));

// Reference positions from PyEphem (geocentric, ecliptic of date).
const REF = {
  apollo11: { Sun: 117.9106, Moon: 187.8737, Mercury: 115.8428, Venus: 75.0374, Mars: 242.7733, Jupiter: 180.7462, Saturn: 38.098, Uranus: 180.69, Neptune: 236.023, Pluto: 173.0078, Ascendant: 229.646, Midheaven: 145.3189 },
  j2000: { Sun: 280.369, Moon: 223.3237, Mercury: 271.8894, Venus: 241.5659, Mars: 327.9634, Jupiter: 25.2531, Saturn: 40.3956, Uranus: 314.8093, Neptune: 303.1933, Pluto: 251.4538, Ascendant: 24.2652, Midheaven: 279.6096 },
};
const APOLLO = { name: "Apollo 11 landing", date: "1969-07-20", time: "20:17", utc_offset: 0, latitude: 29.5593, longitude: -95.09, place: "Houston" };
const J2000 = { name: "J2000", date: "2000-01-01", time: "12:00", timezone: "Europe/London", latitude: 51.4779, longitude: -0.0015, place: "Greenwich" };

let client;
before(async () => {
  client = new Client({ name: "birth-sky-test", version: "1.0.0" });
  await client.connect(new StdioClientTransport({ command: process.execPath, args: [entry], stderr: "ignore" }));
});
after(async () => { await client?.close(); });

const call = (name, args) => client.callTool({ name, arguments: args });
const sep = (a, b) => { const d = Math.abs(((a - b) % 360 + 540) % 360 - 180); return d; };

test("lists five read-only tools; the chart tools point at the view", async () => {
  const { tools } = await client.listTools();
  const names = tools.map((t) => t.name).sort();
  assert.deepEqual(names, ["birthsky_compare_charts", "birthsky_compute_chart", "birthsky_find_events", "birthsky_find_transits", "birthsky_get_sky"]);
  for (const t of tools) {
    assert.equal(t.annotations.readOnlyHint, true, t.name);
    assert.equal(t.annotations.destructiveHint, false, t.name);
    assert.ok(t.description.length > 300, `${t.name} has a full description`);
  }
  const withUi = tools.filter((t) => t._meta?.ui?.resourceUri === "ui://birth-sky/chart-view.html").map((t) => t.name).sort();
  assert.deepEqual(withUi, ["birthsky_compare_charts", "birthsky_compute_chart", "birthsky_get_sky"]);
});

test("serves the chart view as a self-contained MCP Apps resource", async () => {
  const { resources } = await client.listResources();
  assert.ok(resources.some((r) => r.uri === "ui://birth-sky/chart-view.html"));
  const { contents } = await client.readResource({ uri: "ui://birth-sky/chart-view.html" });
  const [c] = contents;
  assert.equal(c.mimeType, "text/html;profile=mcp-app");
  assert.ok(!c.text.includes("/*__MCP_APPS__*/"), "runtime is inlined");
  assert.match(c.text, /const McpApps = await \(async \(\) => \{/);
  assert.match(c.text, /return \{[^}]*"App":/);
  assert.ok(!/<script[^>]+src=/.test(c.text), "no external scripts");
  assert.deepEqual(c._meta.ui.csp.resourceDomains, ["https://fonts.googleapis.com", "https://fonts.gstatic.com"]);
});

for (const [key, args] of [["apollo11", APOLLO], ["j2000", J2000]]) {
  test(`positions match PyEphem within 7′ (${key})`, async () => {
    const r = await call("birthsky_compute_chart", args);
    assert.ok(!r.isError, JSON.stringify(r.content));
    const c = r.structuredContent;
    for (const b of c.bodies) assert.ok(sep(b.lon, REF[key][b.name]) < 0.12, `${b.name}: ${b.lon} vs ${REF[key][b.name]}`);
    assert.ok(sep(c.angles.ascendant.lon, REF[key].Ascendant) < 0.1, "Ascendant");
    assert.ok(sep(c.angles.midheaven.lon, REF[key].Midheaven) < 0.1, "Midheaven");
    assert.equal(c.houses.length, 12);
    assert.match(r.content[0].text, /## Positions/);
  });
}

test("Apollo 11 chart: Sun in Cancer, Moon in Libra, Scorpio rising", async () => {
  const c = (await call("birthsky_compute_chart", APOLLO)).structuredContent;
  assert.deepEqual(c.big_three, { sun: "Cancer", moon: "Libra", rising: "Scorpio" });
  assert.ok(c.aspects.every((a, i, all) => i === 0 || all[i - 1].orb <= a.orb), "aspects sorted by orb");
});

test("historical time zones resolve to the right UTC instant", async () => {
  const chi = (await call("birthsky_compute_chart", { date: "1999-07-04", time: "15:30", timezone: "America/Chicago" })).structuredContent;
  assert.equal(chi.moment.utc, "1999-07-04T20:30:00Z");
  assert.equal(chi.moment.utc_offset, -5);
  const mex = (await call("birthsky_compute_chart", { date: "1970-03-01", time: "08:00", timezone: "America/Mexico_City" })).structuredContent;
  assert.equal(mex.moment.utc, "1970-03-01T14:00:00Z");
  assert.equal(mex.angles, null, "no place, no angles");
  assert.equal(mex.big_three.rising, null);
});

test("errors explain how to fix the input", async () => {
  const noZone = await call("birthsky_compute_chart", { date: "1999-07-04", time: "15:30" });
  assert.equal(noZone.isError, true);
  assert.match(noZone.content[0].text, /timezone/);
  const badZone = await call("birthsky_compute_chart", { date: "1999-07-04", timezone: "Mars/Olympus" });
  assert.match(badZone.content[0].text, /Unknown time zone/);
  const badDate = await call("birthsky_compute_chart", { date: "2001-02-30", timezone: "UTC" });
  assert.match(badDate.content[0].text, /does not exist/);
  const lone = await call("birthsky_compute_chart", { date: "1999-07-04", timezone: "UTC", latitude: 10 });
  assert.match(lone.content[0].text, /both latitude and longitude/);
  const longRange = await call("birthsky_find_events", { start_date: "2020-01-01", end_date: "2030-01-01" });
  assert.match(longRange.content[0].text, /limit is 1830 days/);
});

test("finds Mercury's April 2024 retrograde station and the four 2024 eclipses", async () => {
  const st = (await call("birthsky_find_events", { start_date: "2024-03-25", end_date: "2024-04-30", types: ["station"], bodies: ["Mercury"] })).structuredContent;
  assert.equal(st.total, 2);
  assert.equal(st.items[0].detail, "retrograde");
  assert.ok(Math.abs(Date.parse(st.items[0].utc) - Date.parse("2024-04-01T22:14Z")) < 3600e3, st.items[0].utc);
  const lun = (await call("birthsky_find_events", { start_date: "2024-01-01", end_date: "2024-12-31", types: ["new_moon", "full_moon"], limit: 200 })).structuredContent;
  const ecl = lun.items.filter((e) => e.eclipse);
  assert.deepEqual(ecl.map((e) => `${e.utc.slice(0, 10)} ${e.eclipse}`), ["2024-03-25 lunar", "2024-04-08 solar", "2024-09-18 lunar", "2024-10-02 solar"]);
});

test("transit search finds the J2000 Saturn return and pages correctly", async () => {
  const args = { natal: J2000, start_date: "2028-01-01", end_date: "2030-12-31", transiting: ["Saturn"], natal_points: ["Saturn"], aspects: ["conjunction"] };
  const r = (await call("birthsky_find_transits", args)).structuredContent;
  // PyEphem: exact on 2028-07-21 08:03, 2028-09-24 18:30 (retrograde) and 2029-04-01 21:18 UTC.
  const ref = ["2028-07-21T08:03Z", "2028-09-24T18:30Z", "2029-04-01T21:18Z"];
  assert.equal(r.total, 3, r.items.map((h) => h.utc).join(","));
  r.items.forEach((h, i) => assert.ok(Math.abs(Date.parse(h.utc) - Date.parse(ref[i])) < 12 * 3600e3, `${h.utc} vs ${ref[i]}`));
  assert.deepEqual(r.items.map((h) => h.transiting_retrograde), [false, true, false]);
  const all = (await call("birthsky_find_transits", { natal: J2000, start_date: "2026-01-01", end_date: "2026-12-31" })).structuredContent;
  const p2 = (await call("birthsky_find_transits", { natal: J2000, start_date: "2026-01-01", end_date: "2026-12-31", offset: 50, limit: 50 })).structuredContent;
  assert.equal(all.count, Math.min(50, all.total));
  assert.equal(all.has_more, all.total > 50);
  if (all.total > 50) assert.equal(p2.items[0].utc >= all.items[49].utc, true);
});

test("compare_charts returns cross aspects, shared signs and overlays", async () => {
  const r = await call("birthsky_compare_charts", { person_a: APOLLO, person_b: J2000 });
  const x = r.structuredContent;
  assert.equal(x.kind, "comparison");
  assert.equal(x.charts.length, 2);
  assert.ok(x.cross_aspects.length > 5);
  assert.ok(x.cross_aspects.every((a, i, all) => i === 0 || all[i - 1].orb <= a.orb));
  assert.equal(x.house_overlays.length, 20);
  assert.match(r.content[0].text, /Where the charts meet/);
});

test("get_sky works with no arguments and lists upcoming events", async () => {
  const r = await call("birthsky_get_sky", {});
  assert.ok(!r.isError);
  assert.equal(r.structuredContent.kind, "sky");
  assert.ok(Array.isArray(r.structuredContent.upcoming) && r.structuredContent.upcoming.length > 0);
  const json = await call("birthsky_get_sky", { date: "2024-04-08", time: "18:18", timezone: "UTC", upcoming_days: 0, response_format: "json" });
  assert.equal(JSON.parse(json.content[0].text).moon_phase.name, "New Moon");
});

test("streamable HTTP transport answers tools/list", async () => {
  const port = 3900 + Math.floor(Math.random() * 90);
  const child = spawn(process.execPath, [entry], { env: { ...process.env, TRANSPORT: "http", PORT: String(port) }, stdio: ["ignore", "ignore", "pipe"] });
  try {
    await new Promise((res, rej) => { child.stderr.on("data", (d) => { if (String(d).includes("/mcp")) res(); }); setTimeout(() => rej(new Error("server did not start")), 8000); });
    const res = await fetch(`http://127.0.0.1:${port}/mcp`, {
      method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json, text/event-stream" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }),
    });
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.equal(body.result.tools.length, 5);
    const status = await new Promise((res, rej) => {
      const req = request({ host: "127.0.0.1", port, path: "/mcp", method: "POST", headers: { Host: "evil.example", "Content-Type": "application/json", Accept: "application/json, text/event-stream" } }, (r) => { r.resume(); res(r.statusCode); });
      req.on("error", rej);
      req.end(JSON.stringify({ jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }));
    });
    assert.equal(status, 403, "DNS rebinding protection rejects foreign Host headers");
  } finally {
    child.kill();
  }
});
