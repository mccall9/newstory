import type { McpServer } from "@modelcontextprotocol/server";
import { registerAccountTools } from "./account.js";
import { registerEngagementTools } from "./engagement.js";
import { registerPublishingTools } from "./publishing.js";
import { registerResearchTools } from "./research.js";

export function registerTools(server: McpServer) {
  registerAccountTools(server);
  registerPublishingTools(server);
  registerEngagementTools(server);
  registerResearchTools(server);
}
