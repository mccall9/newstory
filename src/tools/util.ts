import { GraphApiError } from "../instagram/client.js";

export type ToolResult = { content: { type: "text"; text: string }[]; isError?: boolean };

export function ok(data: unknown): ToolResult {
  return { content: [{ type: "text", text: typeof data === "string" ? data : JSON.stringify(data, null, 2) }] };
}

export function fail(err: unknown): ToolResult {
  let text = err instanceof Error ? err.message : String(err);
  if (err instanceof GraphApiError) {
    text = `Erro da API do Instagram (HTTP ${err.status}${err.code ? `, código ${err.code}` : ""}): ${err.message}`;
    if (err.code === 190) text += "\nO token expirou ou é inválido: gere um novo e atualize IG_ACCESS_TOKEN.";
    if (err.code === 4 || err.code === 17 || err.code === 32) text += "\nLimite de chamadas atingido: tente mais tarde.";
  }
  return { content: [{ type: "text", text }], isError: true };
}

/** Envolve o handler de uma ferramenta convertendo exceções em resultado de erro. */
export function safe<A>(fn: (args: A) => Promise<unknown>) {
  return async (args: A): Promise<ToolResult> => {
    try {
      return ok(await fn(args));
    } catch (err) {
      return fail(err);
    }
  };
}
