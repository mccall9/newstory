import { hasSecret } from "../../src/auth.js";
import { env, requireEnv } from "../../src/config.js";
import { getStoredToken, saveToken } from "../../src/db.js";
import { refreshLongLivedToken } from "../../src/instagram/client.js";

// Cron diário da Vercel: renova o token de longa duração antes de expirar (~60 dias).
export async function GET(req: Request): Promise<Response> {
  if (!hasSecret(req, env("CRON_SECRET"))) return new Response("Unauthorized", { status: 401 });
  const current = (await getStoredToken()) ?? requireEnv("IG_ACCESS_TOKEN");
  const { accessToken, expiresIn } = await refreshLongLivedToken(current);
  await saveToken(accessToken, expiresIn);
  return Response.json({ refreshed: true, expires_in_days: Math.round(expiresIn / 86_400) });
}
