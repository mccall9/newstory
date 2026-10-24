import { db, isGlobalRule, type KeywordRule } from "./db.js";
import type { GraphClient } from "./instagram/client.js";
import { handleComment, type CommentEvent, type CommentOutcome } from "./webhook.js";

// Alternativa ao webhook: a Meta só envia webhooks de comentário para apps
// publicados com Advanced Access (exige empresa verificada). Aqui o próprio
// cron lê os comentários dos posts com regra ativa e dispara a mesma lógica.

const PRIVATE_REPLY_WINDOW_MS = 7 * 24 * 60 * 60 * 1000;

export interface PollSummary {
  media: number;
  checked: number;
  outcomes: Partial<Record<CommentOutcome, number>>;
}

/** Posts a vigiar: os ligados a regras específicas e, se houver regra geral, os mais recentes. */
export async function mediaToWatch(ig: GraphClient, rules: KeywordRule[], recentLimit: number): Promise<string[]> {
  const ids = new Set(rules.filter((r) => r.ig_media_id).map((r) => r.ig_media_id as string));
  if (rules.some(isGlobalRule)) {
    const recent = await ig.get<{ data: { id: string }[] }>(`${ig.userId}/media`, { fields: "id", limit: recentLimit });
    for (const m of recent.data) ids.add(m.id);
  }
  return [...ids];
}

interface ApiComment {
  id: string;
  text?: string;
  timestamp: string;
  from?: { id: string; username?: string };
  username?: string;
}

export function toEvents(mediaId: string, comments: ApiComment[], now: number, known: Set<string>): CommentEvent[] {
  return comments
    .filter((c) => c.from?.id && !known.has(c.id) && now - Date.parse(c.timestamp) < PRIVATE_REPLY_WINDOW_MS)
    .map((c) => ({
      commentId: c.id,
      text: c.text ?? "",
      mediaId,
      fromId: c.from!.id,
      fromUsername: c.from!.username ?? c.username,
    }));
}

export async function pollComments(ig: GraphClient, { recentLimit = 3, now = Date.now() } = {}): Promise<PollSummary> {
  const summary: PollSummary = { media: 0, checked: 0, outcomes: {} };

  const { data: rules, error } = await db().from("keyword_rules").select("*").eq("active", true);
  if (error) throw new Error(error.message);
  if (!rules?.length) return summary;

  const mediaIds = await mediaToWatch(ig, rules as KeywordRule[], recentLimit);
  summary.media = mediaIds.length;

  for (const mediaId of mediaIds) {
    const res = await ig.get<{ data: ApiComment[] }>(`${mediaId}/comments`, {
      fields: "id,text,timestamp,username,from",
      limit: 50,
    });
    const ids = res.data.map((c) => c.id);
    if (!ids.length) continue;

    // Comentários que já viraram lead (DM enviada ou com falha) não são reprocessados.
    const { data: seen } = await db().from("leads").select("comment_id").in("comment_id", ids);
    const known = new Set((seen ?? []).map((l) => l.comment_id as string));

    for (const event of toEvents(mediaId, res.data, now, known)) {
      summary.checked++;
      const outcome = await handleComment(ig, event);
      summary.outcomes[outcome] = (summary.outcomes[outcome] ?? 0) + 1;
    }
  }
  return summary;
}
