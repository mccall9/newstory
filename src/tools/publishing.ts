import type { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { mediaBucket } from "../config.js";
import { db } from "../db.js";
import { instagram } from "../instagram/client.js";
import { containerStatus, publishContainer, publishPost, validatePost } from "../instagram/publish.js";
import { safe } from "./util.js";

const postType = z.enum(["photo", "carousel", "reel", "story"]);
const mediaUrls = z
  .array(z.string().url())
  .min(1)
  .max(10)
  .describe("URLs públicas das mídias (use ig_upload_media para hospedar um arquivo). JPEG para imagem, MP4/MOV para vídeo.");

const EXT_BY_TYPE: Record<string, string> = {
  "image/jpeg": "jpg",
  "image/png": "png",
  "video/mp4": "mp4",
  "video/quicktime": "mov",
};

export function registerPublishingTools(server: McpServer) {
  server.registerTool(
    "ig_upload_media",
    {
      title: "Hospedar mídia",
      description:
        "Hospeda uma imagem ou vídeo no Supabase Storage e devolve a URL pública que a API do Instagram exige. Informe source_url (copia de outro lugar) ou base64.",
      inputSchema: z.object({
        source_url: z.string().url().optional(),
        base64: z.string().optional(),
        content_type: z.enum(["image/jpeg", "image/png", "video/mp4", "video/quicktime"]).optional(),
      }),
    },
    safe(async ({ source_url, base64, content_type }) => {
      let bytes: Buffer;
      let type = content_type;
      if (source_url) {
        const res = await fetch(source_url);
        if (!res.ok) throw new Error(`Não consegui baixar ${source_url} (HTTP ${res.status}).`);
        bytes = Buffer.from(await res.arrayBuffer());
        type ??= (res.headers.get("content-type")?.split(";")[0] as typeof content_type) ?? undefined;
      } else if (base64) {
        bytes = Buffer.from(base64.replace(/^data:[^,]+,/, ""), "base64");
      } else {
        throw new Error("Informe source_url ou base64.");
      }
      if (!type || !EXT_BY_TYPE[type]) throw new Error("Tipo de arquivo não suportado: use JPEG, PNG, MP4 ou MOV.");

      const path = `${new Date().toISOString().slice(0, 10)}/${crypto.randomUUID()}.${EXT_BY_TYPE[type]}`;
      const storage = db().storage.from(mediaBucket());
      const { error } = await storage.upload(path, bytes, { contentType: type });
      if (error) throw new Error(`Falha no upload: ${error.message}`);
      return { url: storage.getPublicUrl(path).data.publicUrl, content_type: type, bytes: bytes.length };
    }),
  );

  server.registerTool(
    "ig_publish_now",
    {
      title: "Publicar agora",
      description:
        "Publica imediatamente uma foto, carrossel (2-10 mídias), reel ou story. Se o vídeo ainda estiver processando, devolve o container_id para usar em ig_publish_container.",
      inputSchema: z.object({
        post_type: postType,
        media_urls: mediaUrls,
        caption: z.string().max(2200).optional(),
      }),
    },
    safe(async (input) => {
      const result = await publishPost(instagram(), input);
      return result.status === "published"
        ? { ...result, message: "Publicado!" }
        : { ...result, message: "Ainda processando. Chame ig_publish_container em alguns instantes." };
    }),
  );

  server.registerTool(
    "ig_publish_container",
    {
      title: "Publicar container pronto",
      description: "Confere o status de um container e publica se estiver pronto.",
      inputSchema: z.object({ container_id: z.string() }),
    },
    safe(async ({ container_id }) => {
      const ig = instagram();
      const status = await containerStatus(ig, container_id);
      if (status.status_code !== "FINISHED") return status;
      return { status: "published", mediaId: await publishContainer(ig, container_id) };
    }),
  );

  server.registerTool(
    "ig_publishing_limit",
    {
      title: "Cota de publicação",
      description: "Quantos posts a conta já publicou nas últimas 24h e qual é o limite.",
      inputSchema: z.object({}),
    },
    safe(async () => {
      const ig = instagram();
      return ig.get(`${ig.userId}/content_publishing_limit`, { fields: "quota_usage,config" });
    }),
  );

  server.registerTool(
    "ig_schedule_post",
    {
      title: "Agendar post",
      description:
        "Agenda um post para publicação automática. publish_at em ISO 8601 com fuso (ex.: 2026-11-01T18:00:00-03:00).",
      inputSchema: z.object({
        post_type: postType,
        media_urls: mediaUrls,
        caption: z.string().max(2200).optional(),
        publish_at: z.string().datetime({ offset: true }),
      }),
    },
    safe(async ({ post_type, media_urls, caption, publish_at }) => {
      validatePost({ post_type, media_urls, caption });
      if (new Date(publish_at).getTime() < Date.now() - 60_000) throw new Error("publish_at está no passado.");
      const { data, error } = await db()
        .from("scheduled_posts")
        .insert({ post_type, media_urls, caption: caption ?? null, publish_at })
        .select("id,post_type,publish_at,status")
        .single();
      if (error) throw new Error(error.message);
      return data;
    }),
  );

  server.registerTool(
    "ig_list_scheduled",
    {
      title: "Posts agendados",
      description: "Lista posts agendados e o histórico (publicados, com falha ou cancelados).",
      inputSchema: z.object({
        status: z.enum(["scheduled", "publishing", "published", "failed", "cancelled"]).optional(),
        limit: z.number().int().min(1).max(100).default(30),
      }),
    },
    safe(async ({ status, limit }) => {
      let query = db().from("scheduled_posts").select("*").order("publish_at").limit(limit);
      if (status) query = query.eq("status", status);
      const { data, error } = await query;
      if (error) throw new Error(error.message);
      return data;
    }),
  );

  server.registerTool(
    "ig_update_scheduled",
    {
      title: "Editar agendamento",
      description: "Altera legenda, mídias ou horário de um post que ainda não foi publicado.",
      inputSchema: z.object({
        id: z.string().uuid(),
        caption: z.string().max(2200).optional(),
        media_urls: mediaUrls.optional(),
        publish_at: z.string().datetime({ offset: true }).optional(),
      }),
    },
    safe(async ({ id, ...changes }) => {
      const { data: current, error: readError } = await db().from("scheduled_posts").select("*").eq("id", id).single();
      if (readError) throw new Error(readError.message);
      if (!["scheduled", "failed"].includes(current.status)) {
        throw new Error(`Post está "${current.status}" e não pode mais ser editado.`);
      }
      const next = { ...current, ...Object.fromEntries(Object.entries(changes).filter(([, v]) => v !== undefined)) };
      validatePost(next);
      const { data, error } = await db()
        .from("scheduled_posts")
        .update({
          caption: next.caption,
          media_urls: next.media_urls,
          publish_at: next.publish_at,
          status: "scheduled",
          container_id: null,
          error: null,
        })
        .eq("id", id)
        .select("*")
        .single();
      if (error) throw new Error(error.message);
      return data;
    }),
  );

  server.registerTool(
    "ig_cancel_scheduled",
    {
      title: "Cancelar agendamento",
      description: "Cancela um post agendado que ainda não foi publicado.",
      inputSchema: z.object({ id: z.string().uuid() }),
    },
    safe(async ({ id }) => {
      const { data, error } = await db()
        .from("scheduled_posts")
        .update({ status: "cancelled" })
        .eq("id", id)
        .in("status", ["scheduled", "failed"])
        .select("id,status");
      if (error) throw new Error(error.message);
      if (!data?.length) throw new Error("Post não encontrado ou já publicado.");
      return data[0];
    }),
  );
}
