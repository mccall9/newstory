import { hasSecret } from "../../src/auth.js";
import { env } from "../../src/config.js";
import { instagram } from "../../src/instagram/client.js";
import { runDuePosts } from "../../src/scheduler.js";

// Chamado a cada minuto pelo pg_cron do Supabase (o cron da Vercel no plano grátis é só diário).
export async function POST(req: Request): Promise<Response> {
  if (!hasSecret(req, env("CRON_SECRET"))) return new Response("Unauthorized", { status: 401 });
  const summary = await runDuePosts(instagram());
  return Response.json(summary);
}

export { POST as GET };
