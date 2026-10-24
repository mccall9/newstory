import type { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { facebookGraph } from "../instagram/client.js";
import { safe } from "./util.js";

const POST_FIELDS = "id,caption,media_type,permalink,timestamp,like_count,comments_count";

export function registerResearchTools(server: McpServer) {
  server.registerTool(
    "ig_business_discovery",
    {
      title: "Analisar outra conta",
      description:
        "Dados públicos e posts recentes de outra conta Business/Creator (pelo @). Útil para estudar concorrentes e referências.",
      inputSchema: z.object({
        username: z.string().min(1).describe("Sem @"),
        posts: z.number().int().min(1).max(50).default(12),
      }),
    },
    safe(async ({ username, posts }) => {
      const fb = facebookGraph();
      const user = username.replace(/^@/, "");
      const res = await fb.get(fb.userId, {
        fields: `business_discovery.username(${user}){username,name,biography,website,followers_count,follows_count,media_count,media.limit(${posts}){${POST_FIELDS}}}`,
      });
      return res.business_discovery;
    }),
  );

  server.registerTool(
    "ig_hashtag_media",
    {
      title: "Posts de uma hashtag",
      description:
        "Posts em alta (top) ou recentes de uma hashtag. Atenção: a Meta limita a 30 hashtags diferentes a cada 7 dias.",
      inputSchema: z.object({
        hashtag: z.string().min(1).describe("Sem #"),
        sort: z.enum(["top", "recent"]).default("top"),
        limit: z.number().int().min(1).max(50).default(25),
      }),
    },
    safe(async ({ hashtag, sort, limit }) => {
      const fb = facebookGraph();
      const search = await fb.get<{ data: { id: string }[] }>("ig_hashtag_search", {
        user_id: fb.userId,
        q: hashtag.replace(/^#/, ""),
      });
      const id = search.data[0]?.id;
      if (!id) return { hashtag, data: [] };
      const edge = sort === "top" ? "top_media" : "recent_media";
      return fb.get(`${id}/${edge}`, { user_id: fb.userId, fields: POST_FIELDS, limit });
    }),
  );
}
