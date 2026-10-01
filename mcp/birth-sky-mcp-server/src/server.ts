import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SERVER_NAME, SERVER_VERSION } from "./constants.js";
import { registerTools } from "./tools.js";
import { registerView } from "./view.js";

/** A fully configured Birth Sky server, not yet connected to a transport. */
export function createBirthSkyServer(): McpServer {
  const server = new McpServer({ name: SERVER_NAME, version: SERVER_VERSION });
  registerTools(server);
  registerView(server);
  return server;
}
