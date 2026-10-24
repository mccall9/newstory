import type { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { instagram } from "../instagram/client.js";
import { safe } from "./util.js";

const MEDIA_FIELDS =
  "id,caption,media_type,media_product_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count";

export function registerAccountTools(server: McpServer) {
  server.registerTool(
    "ig_get_profile",
    {
      title: "Perfil",
      description: "Dados da conta conectada: usuário, nome, seguidores, seguindo e total de posts.",
      inputSchema: z.object({}),
    },
    safe(async () => {
      const ig = instagram();
      return ig.get("me", {
        fields: "user_id,username,name,account_type,profile_picture_url,followers_count,follows_count,media_count,biography,website",
      });
    }),
  );

  server.registerTool(
    "ig_get_account_insights",
    {
      title: "Métricas da conta",
      description:
        "Métricas da conta no período (alcance, visualizações, interações, novos seguidores). Período máximo de 30 dias.",
      inputSchema: z.object({
        days: z.number().int().min(1).max(30).default(7).describe("Quantos dias para trás"),
        metrics: z
          .array(z.string())
          .default(["reach", "views", "total_interactions", "likes", "comments", "shares", "saves", "follows_and_unfollows"])
          .describe("Métricas da API de insights"),
      }),
    },
    safe(async ({ days, metrics }) => {
      const ig = instagram();
      const until = Math.floor(Date.now() / 1000);
      const since = until - days * 86_400;
      return ig.get(`${ig.userId}/insights`, {
        metric: metrics.join(","),
        period: "day",
        metric_type: "total_value",
        since,
        until,
      });
    }),
  );

  server.registerTool(
    "ig_list_media",
    {
      title: "Meus posts",
      description: "Lista os posts publicados na conta, do mais recente para o mais antigo, com curtidas e comentários.",
      inputSchema: z.object({
        limit: z.number().int().min(1).max(100).default(12),
        after: z.string().optional().describe("Cursor de paginação (paging.cursors.after da resposta anterior)"),
      }),
    },
    safe(async ({ limit, after }) => {
      const ig = instagram();
      return ig.get(`${ig.userId}/media`, { fields: MEDIA_FIELDS, limit, after });
    }),
  );

  server.registerTool(
    "ig_get_media",
    {
      title: "Detalhes de um post",
      description: "Dados de um post específico.",
      inputSchema: z.object({ media_id: z.string() }),
    },
    safe(async ({ media_id }) => instagram().get(media_id, { fields: `${MEDIA_FIELDS},children{media_type,media_url}` })),
  );

  server.registerTool(
    "ig_get_media_insights",
    {
      title: "Métricas de um post",
      description: "Alcance, visualizações, curtidas, comentários, compartilhamentos e salvamentos de um post.",
      inputSchema: z.object({
        media_id: z.string(),
        metrics: z.array(z.string()).default(["reach", "views", "likes", "comments", "shares", "saved", "total_interactions"]),
      }),
    },
    safe(async ({ media_id, metrics }) => instagram().get(`${media_id}/insights`, { metric: metrics.join(",") })),
  );

  server.registerTool(
    "ig_delete_media",
    {
      title: "Apagar post",
      description: "Apaga um post publicado. Não tem volta: confirme com o usuário antes.",
      inputSchema: z.object({ media_id: z.string() }),
      annotations: { destructiveHint: true },
    },
    safe(async ({ media_id }) => instagram().delete(media_id)),
  );
}
