/** Builds the chart-wheel view (one self-contained HTML document) and registers it as an MCP Apps resource. */

import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { RESOURCE_MIME_TYPE, registerAppResource } from "@modelcontextprotocol/ext-apps/server";
import { VIEW_URI } from "./constants.js";

const require = createRequire(import.meta.url);

/**
 * The ext-apps view runtime is a minified ES module with one export list. It is wrapped in its own async scope
 * (its short top-level names would otherwise collide with the view's code) and exposed as a local `McpApps` object.
 */
function appRuntime(): string {
  const src = readFileSync(require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"), "utf8");
  const m = /export\s*\{([^}]*)\}\s*;?\s*$/.exec(src);
  if (!m) throw new Error("Unexpected @modelcontextprotocol/ext-apps bundle format: no trailing export list.");
  const entries = m[1].split(",").map((s) => s.trim()).filter(Boolean).map((spec) => {
    const [local, exported] = spec.split(/\s+as\s+/);
    return `${JSON.stringify(exported ?? local)}:${local}`;
  });
  return `const McpApps = await (async () => {\n${src.slice(0, m.index)}\nreturn {${entries.join(",")}};\n})();`;
}

let cached: string | null = null;
export function viewHtml(): string {
  if (cached) return cached;
  const template = readFileSync(new URL("../ui/chart-view.html", import.meta.url), "utf8");
  // A function replacer keeps `$` sequences in the bundle literal.
  cached = template.replace("/*__MCP_APPS__*/", () => appRuntime());
  return cached;
}

export function registerView(server: McpServer): void {
  const csp = { resourceDomains: ["https://fonts.googleapis.com", "https://fonts.gstatic.com"] };
  registerAppResource(server, "Birth Sky chart wheel", VIEW_URI, {
    description: "Interactive chart wheel for birth charts, the current sky and two-chart comparisons.",
    _meta: { ui: { csp, prefersBorder: false } },
  }, async () => ({
    contents: [{ uri: VIEW_URI, mimeType: RESOURCE_MIME_TYPE, text: viewHtml(), _meta: { ui: { csp, prefersBorder: false } } }],
  }));
}
