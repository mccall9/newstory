import { db } from "../src/db.js";

// Cadastro na lista de espera do Kit (formulário da página /kit e dos guias).
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const clean = (v: unknown, max: number) => (typeof v === "string" ? v.trim().slice(0, max) : "") || null;

export async function POST(req: Request): Promise<Response> {
  const form = req.headers.get("content-type")?.includes("application/json")
    ? await req.json().catch(() => ({}))
    : Object.fromEntries(await req.formData().catch(() => new FormData()));

  // Campo escondido: robôs preenchem, pessoas não.
  if (clean(form.website, 200)) return Response.json({ ok: true });

  const email = clean(form.email, 200)?.toLowerCase();
  if (!email || !EMAIL.test(email)) return Response.json({ ok: false, error: "E-mail inválido." }, { status: 400 });

  const { error } = await db()
    .from("waitlist")
    .upsert(
      {
        email,
        name: clean(form.name, 120),
        instagram: clean(form.instagram, 60)?.replace(/^@/, "") ?? null,
        source: clean(form.source, 60),
      },
      { onConflict: "product,email", ignoreDuplicates: true },
    );
  if (error) return Response.json({ ok: false, error: "Não foi possível salvar agora. Tente de novo." }, { status: 500 });
  return Response.json({ ok: true });
}
