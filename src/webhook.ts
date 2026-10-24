import { createHmac, timingSafeEqual } from "node:crypto";
import { db, type KeywordRule } from "./db.js";
import type { GraphClient } from "./instagram/client.js";

export function verifySignature(rawBody: string, header: string | null, appSecret: string): boolean {
  if (!header?.startsWith("sha256=")) return false;
  const expected = createHmac("sha256", appSecret).update(rawBody, "utf8").digest("hex");
  const given = header.slice("sha256=".length);
  if (given.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(given, "hex"), Buffer.from(expected, "hex"));
}

export interface CommentEvent {
  commentId: string;
  text: string;
  mediaId: string;
  fromId: string;
  fromUsername?: string;
  parentId?: string;
}

/** Extrai os comentários novos do payload de webhook do Instagram. */
export function parseCommentEvents(payload: any): CommentEvent[] {
  if (payload?.object !== "instagram") return [];
  const events: CommentEvent[] = [];
  for (const entry of payload.entry ?? []) {
    for (const change of entry.changes ?? []) {
      if (change.field !== "comments" && change.field !== "live_comments") continue;
      const v = change.value ?? {};
      if (!v.id || !v.media?.id || !v.from?.id) continue;
      events.push({
        commentId: v.id,
        text: v.text ?? "",
        mediaId: v.media.id,
        fromId: v.from.id,
        fromUsername: v.from.username,
        parentId: v.parent_id,
      });
    }
  }
  return events;
}

const normalize = (s: string) =>
  s
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();

/** A palavra-chave precisa aparecer como palavra inteira (sem acento/maiúscula). */
export function matchesKeyword(text: string, keywords: string[]): boolean {
  const words = new Set(normalize(text).split(/[^\p{L}\p{N}]+/u).filter(Boolean));
  const normalized = normalize(text);
  return keywords.some((k) => {
    const key = normalize(k).trim();
    if (!key) return false;
    return key.includes(" ") ? normalized.includes(key) : words.has(key);
  });
}

/** Regra específica do post tem prioridade sobre regra geral (ig_media_id nulo). */
export function pickRule(rules: KeywordRule[], event: CommentEvent): KeywordRule | undefined {
  const candidates = rules.filter((r) => r.active && (r.ig_media_id === null || r.ig_media_id === event.mediaId));
  candidates.sort((a, b) => Number(b.ig_media_id !== null) - Number(a.ig_media_id !== null));
  return candidates.find((r) => matchesKeyword(event.text, r.keywords));
}

export function buildDm(rule: KeywordRule, username?: string): string {
  let text = rule.dm_message.replaceAll("{username}", username ? `@${username}` : "");
  if (rule.link) text = text.includes("{link}") ? text.replaceAll("{link}", rule.link) : `${text}\n\n${rule.link}`;
  return text.trim();
}

export type CommentOutcome = "sent" | "duplicate" | "no_rule" | "ignored" | "error";

export async function handleComment(ig: GraphClient, event: CommentEvent): Promise<CommentOutcome> {
  // Ignora comentários da própria conta (inclusive as nossas respostas públicas).
  if (event.fromId === ig.userId) return "ignored";

  const { data: rules, error } = await db().from("keyword_rules").select("*").eq("active", true);
  if (error) throw new Error(error.message);
  const rule = pickRule((rules ?? []) as KeywordRule[], event);
  if (!rule) return "no_rule";

  // comment_id é único: o insert falha se esse comentário já foi atendido.
  const { error: insertError } = await db().from("leads").insert({
    comment_id: event.commentId,
    rule_id: rule.id,
    ig_media_id: event.mediaId,
    ig_user_id: event.fromId,
    username: event.fromUsername ?? null,
    comment_text: event.text,
    status: "pending",
  });
  if (insertError) {
    if (insertError.code === "23505") return "duplicate";
    throw new Error(insertError.message);
  }

  try {
    await ig.post(`${ig.userId}/messages`, {
      recipient: { comment_id: event.commentId },
      message: { text: buildDm(rule, event.fromUsername) },
    });
    if (rule.public_reply) {
      await ig.post(`${event.commentId}/replies`, { message: rule.public_reply }).catch(() => undefined);
    }
    await db().from("leads").update({ status: "sent", sent_at: new Date().toISOString() }).eq("comment_id", event.commentId);
    return "sent";
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await db().from("leads").update({ status: "failed", error: message }).eq("comment_id", event.commentId);
    return "error";
  }
}
