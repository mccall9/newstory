import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { env, requireEnv } from "./config.js";

let client: SupabaseClient | undefined;

export function db(): SupabaseClient {
  client ??= createClient(requireEnv("SUPABASE_URL"), requireEnv("SUPABASE_SERVICE_ROLE_KEY"), {
    auth: { persistSession: false },
  });
  return client;
}

export const hasDb = () => Boolean(env("SUPABASE_URL") && env("SUPABASE_SERVICE_ROLE_KEY"));

export type PostType = "photo" | "carousel" | "reel" | "story";

export interface ScheduledPost {
  id: string;
  post_type: PostType;
  caption: string | null;
  media_urls: string[];
  publish_at: string;
  status: "scheduled" | "publishing" | "published" | "failed" | "cancelled";
  ig_media_id: string | null;
  error: string | null;
}

export interface KeywordRule {
  id: string;
  name: string;
  ig_media_id: string | null;
  keywords: string[];
  dm_message: string;
  link: string | null;
  public_reply: string | null;
  active: boolean;
}

// O token renovado pelo cron fica no banco; o da variável de ambiente é o ponto de partida.
export async function getStoredToken(): Promise<string | undefined> {
  if (!hasDb()) return undefined;
  const { data } = await db().from("ig_tokens").select("access_token").eq("id", "main").maybeSingle();
  return data?.access_token ?? undefined;
}

export async function saveToken(accessToken: string, expiresInSeconds: number): Promise<void> {
  const expires_at = new Date(Date.now() + expiresInSeconds * 1000).toISOString();
  const { error } = await db()
    .from("ig_tokens")
    .upsert({ id: "main", access_token: accessToken, expires_at, updated_at: new Date().toISOString() });
  if (error) throw new Error(`Falha ao salvar token: ${error.message}`);
}
