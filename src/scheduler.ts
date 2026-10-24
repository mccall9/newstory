import { db, type ScheduledPost } from "./db.js";
import type { GraphClient } from "./instagram/client.js";
import { publishPost } from "./instagram/publish.js";

export interface RunSummary {
  published: string[];
  processing: string[];
  failed: { id: string; error: string }[];
}

/**
 * Publica os posts agendados cujo horário já passou. Chamado a cada minuto
 * pelo pg_cron do Supabase. Vídeos que ainda estão processando ficam com o
 * container salvo e são retomados na próxima execução.
 */
export async function runDuePosts(ig: GraphClient, now = new Date(), limit = 5): Promise<RunSummary> {
  const summary: RunSummary = { published: [], processing: [], failed: [] };

  const { data, error } = await db()
    .from("scheduled_posts")
    .select("*")
    .eq("status", "scheduled")
    .lte("publish_at", now.toISOString())
    .order("publish_at")
    .limit(limit);
  if (error) throw new Error(error.message);

  for (const post of (data ?? []) as (ScheduledPost & { container_id: string | null })[]) {
    // Trava otimista: só segue quem conseguir mudar scheduled -> publishing.
    const { data: claimed } = await db()
      .from("scheduled_posts")
      .update({ status: "publishing" })
      .eq("id", post.id)
      .eq("status", "scheduled")
      .select("id");
    if (!claimed?.length) continue;

    try {
      const result = await publishPost(ig, post, { containerId: post.container_id, timeoutMs: 40_000 });
      if (result.status === "published") {
        await db()
          .from("scheduled_posts")
          .update({
            status: "published",
            ig_media_id: result.mediaId,
            container_id: result.containerId,
            published_at: new Date().toISOString(),
            error: null,
          })
          .eq("id", post.id);
        await db().from("keyword_rules").update({ ig_media_id: result.mediaId }).eq("scheduled_post_id", post.id);
        summary.published.push(post.id);
      } else {
        await db()
          .from("scheduled_posts")
          .update({ status: "scheduled", container_id: result.containerId })
          .eq("id", post.id);
        summary.processing.push(post.id);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      await db().from("scheduled_posts").update({ status: "failed", error: message }).eq("id", post.id);
      summary.failed.push({ id: post.id, error: message });
    }
  }

  return summary;
}
