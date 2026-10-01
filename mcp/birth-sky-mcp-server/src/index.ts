#!/usr/bin/env node
/**
 * Birth Sky MCP server: birth charts, chart comparison, transits and sky events from a built-in ephemeris,
 * with an MCP Apps chart-wheel view. No network access or API keys are needed.
 *
 * Transport: stdio by default. Set TRANSPORT=http (and optionally PORT, default 3000) for stateless
 * streamable HTTP on 127.0.0.1.
 */

import { createServer, type IncomingMessage } from "node:http";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SERVER_NAME, SERVER_VERSION } from "./constants.js";
import { createBirthSkyServer } from "./server.js";

async function runStdio(): Promise<void> {
  await createBirthSkyServer().connect(new StdioServerTransport());
  console.error(`${SERVER_NAME} ${SERVER_VERSION} running on stdio`);
}

function readJson(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => {
      size += c.length;
      if (size > 1_000_000) { reject(new Error("Request body too large")); req.destroy(); return; }
      chunks.push(c);
    });
    req.on("end", () => {
      try { resolve(chunks.length ? JSON.parse(Buffer.concat(chunks).toString("utf8")) : undefined); } catch (e) { reject(e); }
    });
    req.on("error", reject);
  });
}

async function runHttp(): Promise<void> {
  const port = Number.parseInt(process.env.PORT ?? "3000", 10);
  const host = process.env.HOST ?? "127.0.0.1";
  const allowedHosts = [`127.0.0.1:${port}`, `localhost:${port}`, ...(process.env.ALLOWED_HOSTS?.split(",").map((h) => h.trim()).filter(Boolean) ?? [])];
  const http = createServer(async (req, res) => {
    if (req.url?.split("?")[0] !== "/mcp") { res.writeHead(404).end("Not found. The MCP endpoint is /mcp."); return; }
    if (req.method !== "POST") { res.writeHead(405, { Allow: "POST" }).end("Use POST (stateless streamable HTTP)."); return; }
    try {
      const body = await readJson(req);
      // A fresh server and transport per request keeps the endpoint stateless.
      const server = createBirthSkyServer();
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined, enableJsonResponse: true, enableDnsRebindingProtection: true, allowedHosts,
      });
      res.on("close", () => { void transport.close(); void server.close(); });
      await server.connect(transport);
      await transport.handleRequest(req, res, body);
    } catch (e) {
      if (!res.headersSent) res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ jsonrpc: "2.0", error: { code: -32700, message: `Bad request: ${e instanceof Error ? e.message : String(e)}` }, id: null }));
    }
  });
  http.listen(port, host, () => console.error(`${SERVER_NAME} ${SERVER_VERSION} on http://${host}:${port}/mcp`));
}

if (process.argv.includes("--help") || process.argv.includes("-h")) {
  console.error(`${SERVER_NAME} ${SERVER_VERSION}\n\nUsage: birth-sky-mcp-server            (stdio)\n       TRANSPORT=http PORT=3000 birth-sky-mcp-server   (streamable HTTP on 127.0.0.1)`);
  process.exit(0);
}
(process.env.TRANSPORT === "http" ? runHttp() : runStdio()).catch((e) => {
  console.error("Server error:", e);
  process.exit(1);
});
