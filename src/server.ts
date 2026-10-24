import type { McpServer } from "@modelcontextprotocol/server";
import { registerAccountTools } from "./tools/account.js";
import { registerEngagementTools } from "./tools/engagement.js";
import { registerPublishingTools } from "./tools/publishing.js";
import { registerResearchTools } from "./tools/research.js";

export function registerTools(server: McpServer) {
  registerAccountTools(server);
  registerPublishingTools(server);
  registerEngagementTools(server);
  registerResearchTools(server);
}
