// Leitura das variáveis de ambiente. Tudo é lido sob demanda para que
// ferramentas que não dependem de uma variável funcionem sem ela.

export function env(name: string): string | undefined {
  const value = process.env[name];
  return value && value.trim() !== "" ? value.trim() : undefined;
}

export function requireEnv(name: string): string {
  const value = env(name);
  if (!value) throw new Error(`Variável de ambiente ${name} não configurada.`);
  return value;
}

export const igApiVersion = () => env("IG_API_VERSION") ?? "v25.0";
export const mediaBucket = () => env("SUPABASE_MEDIA_BUCKET") ?? "media";
