import type { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { db } from "../db.js";
import { instagram } from "../instagram/client.js";
import { safe } from "./util.js";

export function registerEngagementTools(server: McpServer) {
  server.registerTool(
    "ig_get_comments",
    {
      title: "Comentários de um post",
      description: "Lista os comentários (e respostas) de um post.",
      inputSchema: z.object({
        media_id: z.string(),
        limit: z.number().int().min(1).max(100).default(50),
        after: z.string().optional(),
      }),
    },
    safe(async ({ media_id, limit, after }) =>
      instagram().get(`${media_id}/comments`, {
        fields: "id,text,username,timestamp,like_count,hidden,replies{id,text,username,timestamp}",
        limit,
        after,
      }),
    ),
  );

  server.registerTool(
    "ig_reply_comment",
    {
      title: "Responder comentário",
      description: "Responde publicamente a um comentário.",
      inputSchema: z.object({ comment_id: z.string(), message: z.string().min(1).max(2200) }),
    },
    safe(async ({ comment_id, message }) => instagram().post(`${comment_id}/replies`, { message })),
  );

  server.registerTool(
    "ig_hide_comment",
    {
      title: "Ocultar comentário",
      description: "Oculta (ou volta a mostrar) um comentário.",
      inputSchema: z.object({ comment_id: z.string(), hide: z.boolean().default(true) }),
    },
    safe(async ({ comment_id, hide }) => instagram().post(comment_id, { hide })),
  );

  server.registerTool(
    "ig_delete_comment",
    {
      title: "Apagar comentário",
      description: "Apaga um comentário. Não tem volta: confirme com o usuário antes.",
      inputSchema: z.object({ comment_id: z.string() }),
      annotations: { destructiveHint: true },
    },
    safe(async ({ comment_id }) => instagram().delete(comment_id)),
  );

  server.registerTool(
    "ig_create_keyword_rule",
    {
      title: "Criar regra comente-e-ganhe",
      description:
        "Quando alguém comentar uma das palavras-chave, envia automaticamente uma DM (private reply) com a mensagem e o link. " +
        "Sem media_id, a regra vale para todos os posts. Na mensagem, use {username} e {link} como variáveis.",
      inputSchema: z.object({
        name: z.string().min(1).describe("Nome interno da regra, ex.: 'E-book março'"),
        keywords: z.array(z.string().min(1)).min(1).describe("Ex.: ['QUERO', 'link']. Não diferencia maiúsculas nem acentos."),
        dm_message: z.string().min(1).max(1000).describe("Ex.: 'Oi {username}! Aqui está o seu acesso: {link}'"),
        link: z.string().url().optional(),
        media_id: z.string().optional().describe("Post já publicado. Omitir (e sem scheduled_post_id) = todos os posts."),
        scheduled_post_id: z
          .string()
          .uuid()
          .optional()
          .describe("Post agendado (id de ig_schedule_post): a regra passa a valer quando ele for publicado."),
        public_reply: z.string().max(300).optional().describe("Resposta pública no comentário, ex.: 'Te mandei no direct! 📩'"),
      }),
    },
    safe(async ({ name, keywords, dm_message, link, media_id, scheduled_post_id, public_reply }) => {
      const { data, error } = await db()
        .from("keyword_rules")
        .insert({
          name,
          keywords,
          dm_message,
          link: link ?? null,
          ig_media_id: media_id ?? null,
          ...(scheduled_post_id ? { scheduled_post_id } : {}),
          public_reply: public_reply ?? null,
        })
        .select("*")
        .single();
      if (error) throw new Error(error.message);
      return data;
    }),
  );

  server.registerTool(
    "ig_list_rules",
    {
      title: "Regras comente-e-ganhe",
      description: "Lista as regras com o total de DMs enviadas por cada uma.",
      inputSchema: z.object({}),
    },
    safe(async () => {
      const { data, error } = await db().from("keyword_rules_stats").select("*").order("created_at", { ascending: false });
      if (error) throw new Error(error.message);
      return data;
    }),
  );

  server.registerTool(
    "ig_update_rule",
    {
      title: "Editar regra",
      description: "Ativa/desativa ou altera uma regra comente-e-ganhe.",
      inputSchema: z.object({
        id: z.string().uuid(),
        active: z.boolean().optional(),
        keywords: z.array(z.string().min(1)).min(1).optional(),
        dm_message: z.string().min(1).max(1000).optional(),
        link: z.string().url().nullable().optional(),
        public_reply: z.string().max(300).nullable().optional(),
      }),
    },
    safe(async ({ id, ...changes }) => {
      const update = Object.fromEntries(Object.entries(changes).filter(([, v]) => v !== undefined));
      const { data, error } = await db().from("keyword_rules").update(update).eq("id", id).select("*").single();
      if (error) throw new Error(error.message);
      return data;
    }),
  );

  server.registerTool(
    "ig_list_leads",
    {
      title: "Leads",
      description: "Pessoas que comentaram a palavra-chave e o status da DM enviada.",
      inputSchema: z.object({
        rule_id: z.string().uuid().optional(),
        status: z.enum(["pending", "sent", "failed"]).optional(),
        limit: z.number().int().min(1).max(500).default(50),
      }),
    },
    safe(async ({ rule_id, status, limit }) => {
      let query = db().from("leads").select("*").order("created_at", { ascending: false }).limit(limit);
      if (rule_id) query = query.eq("rule_id", rule_id);
      if (status) query = query.eq("status", status);
      const { data, error } = await query;
      if (error) throw new Error(error.message);
      return data;
    }),
  );
}
