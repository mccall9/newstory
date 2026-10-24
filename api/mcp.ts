import { createMcpHandler } from "mcp-handler";
import { hasSecret } from "../src/auth.js";
import { env } from "../src/config.js";
import { registerTools } from "../src/tools/index.js";

const handler = createMcpHandler(registerTools, {
  serverInfo: { name: "instagram-mcp", version: "0.1.0" },
});

async function guarded(req: Request): Promise<Response> {
  if (!hasSecret(req, env("MCP_AUTH_TOKEN"))) return new Response("Unauthorized", { status: 401 });
  return handler(req);
}

export { guarded as GET, guarded as POST, guarded as DELETE };
