import { hasSecret } from "../../src/auth.js";
import { env } from "../../src/config.js";
import { instagram } from "../../src/instagram/client.js";
import { pollComments } from "../../src/poller.js";
import { runDuePosts } from "../../src/scheduler.js";

// Chamado a cada minuto pelo pg_cron do Supabase (o cron da Vercel no plano grátis é só diário).
// Publica os agendados e, a cada COMMENT_POLL_MINUTES, lê comentários para o comente-e-ganhe.
export async function POST(req: Request): Promise<Response> {
  if (!hasSecret(req, env("CRON_SECRET"))) return new Response("Unauthorized", { status: 401 });
  const ig = instagram();
  const posts = await runDuePosts(ig);

  const every = Math.max(1, Number(env("COMMENT_POLL_MINUTES") ?? 2));
  let comments: unknown = "skipped";
  if (new Date().getUTCMinutes() % every === 0) {
    const recentLimit = Math.max(1, Number(env("COMMENT_POLL_RECENT") ?? 8));
    comments = await pollComments(ig, { recentLimit }).catch((err) => ({ error: err instanceof Error ? err.message : String(err) }));
  }
  return Response.json({ posts, comments });
}

export { POST as GET };
