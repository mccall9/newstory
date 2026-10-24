import { timingSafeEqual } from "node:crypto";

export function safeEqual(a: string, b: string): boolean {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

/** Aceita o segredo no header Authorization (Bearer) ou, para clientes que não enviam headers, em ?key=. */
export function hasSecret(req: Request, secret: string | undefined): boolean {
  if (!secret) return false;
  const header = req.headers.get("authorization");
  const bearer = header?.startsWith("Bearer ") ? header.slice(7) : undefined;
  const key = new URL(req.url).searchParams.get("key") ?? undefined;
  return [bearer, key].some((given) => given !== undefined && safeEqual(given, secret));
}
