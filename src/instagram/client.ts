import { env, igApiVersion, requireEnv } from "../config.js";
import { getStoredToken } from "../db.js";

export class GraphApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: number,
  ) {
    super(message);
  }
}

type Params = Record<string, string | number | boolean | undefined>;

export interface GraphClient {
  userId: string;
  get<T = any>(path: string, params?: Params): Promise<T>;
  post<T = any>(path: string, body?: Record<string, unknown>): Promise<T>;
  delete<T = any>(path: string): Promise<T>;
}

function makeClient(baseUrl: string, userId: string, token: () => Promise<string>): GraphClient {
  async function request<T>(method: string, path: string, params: Params = {}, body?: Record<string, unknown>) {
    const url = new URL(`${baseUrl}/${igApiVersion()}/${path.replace(/^\//, "")}`);
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
    const res = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${await token()}`,
        ...(body ? { "Content-Type": "application/json" } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    const json: any = await res.json().catch(() => ({}));
    if (!res.ok || json.error) {
      const err = json.error ?? {};
      throw new GraphApiError(err.message ?? `HTTP ${res.status}`, res.status, err.code);
    }
    return json as T;
  }

  return {
    userId,
    get: (path, params) => request("GET", path, params),
    post: (path, body) => request("POST", path, {}, body ?? {}),
    delete: (path) => request("DELETE", path),
  };
}

/** Conta conectada via Business Login for Instagram (graph.instagram.com). */
export function instagram(): GraphClient {
  return makeClient("https://graph.instagram.com", requireEnv("IG_USER_ID"), async () => {
    return (await getStoredToken()) ?? requireEnv("IG_ACCESS_TOKEN");
  });
}

/**
 * Business Discovery e busca de hashtags só existem na API com Facebook Login
 * (graph.facebook.com), com token de Página e o ID da conta IG ligada a ela.
 */
export function facebookGraph(): GraphClient {
  const token = env("FB_PAGE_ACCESS_TOKEN");
  const userId = env("FB_IG_USER_ID");
  if (!token || !userId) {
    throw new Error(
      "Pesquisa indisponível: configure FB_PAGE_ACCESS_TOKEN e FB_IG_USER_ID (Business Discovery e hashtags exigem Facebook Login).",
    );
  }
  return makeClient("https://graph.facebook.com", userId, async () => token);
}

/** Renova o token de longa duração (válido por ~60 dias). */
export async function refreshLongLivedToken(currentToken: string) {
  const url = new URL("https://graph.instagram.com/refresh_access_token");
  url.searchParams.set("grant_type", "ig_refresh_token");
  url.searchParams.set("access_token", currentToken);
  const res = await fetch(url);
  const json: any = await res.json().catch(() => ({}));
  if (!res.ok || json.error) {
    throw new GraphApiError(json.error?.message ?? `HTTP ${res.status}`, res.status, json.error?.code);
  }
  return { accessToken: json.access_token as string, expiresIn: json.expires_in as number };
}
