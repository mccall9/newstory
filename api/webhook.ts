import { waitUntil } from "@vercel/functions";
import { safeEqual } from "../src/auth.js";
import { env, requireEnv } from "../src/config.js";
import { instagram } from "../src/instagram/client.js";
import { handleComment, parseCommentEvents, verifySignature } from "../src/webhook.js";

// Verificação da assinatura do webhook pela Meta (feita uma vez, ao cadastrar a URL).
export function GET(req: Request): Response {
  const params = new URL(req.url).searchParams;
  const token = params.get("hub.verify_token") ?? "";
  const expected = env("META_WEBHOOK_VERIFY_TOKEN");
  if (params.get("hub.mode") === "subscribe" && expected && safeEqual(token, expected)) {
    return new Response(params.get("hub.challenge") ?? "", { status: 200 });
  }
  return new Response("Forbidden", { status: 403 });
}

export async function POST(req: Request): Promise<Response> {
  const raw = await req.text();
  if (!verifySignature(raw, req.headers.get("x-hub-signature-256"), requireEnv("META_APP_SECRET"))) {
    return new Response("Invalid signature", { status: 401 });
  }

  let payload: unknown;
  try {
    payload = JSON.parse(raw);
  } catch {
    return new Response("Bad JSON", { status: 400 });
  }

  // A Meta espera 200 rápido; o envio das DMs continua depois da resposta.
  const events = parseCommentEvents(payload);
  if (events.length) {
    const ig = instagram();
    waitUntil(
      Promise.allSettled(events.map((e) => handleComment(ig, e))).then((results) => {
        for (const r of results) if (r.status === "rejected") console.error("webhook:", r.reason);
      }),
    );
  }
  return new Response("OK", { status: 200 });
}
