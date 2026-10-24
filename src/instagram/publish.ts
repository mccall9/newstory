import type { PostType } from "../db.js";
import type { GraphClient } from "./client.js";

// Publicação no Instagram é em duas etapas: cria-se um "container" com a mídia
// e, quando o processamento termina (status FINISHED), publica-se o container.

export interface PostInput {
  post_type: PostType;
  media_urls: string[];
  caption?: string | null;
}

const VIDEO_EXT = /\.(mp4|mov|m4v)(\?|#|$)/i;
export const isVideoUrl = (url: string) => VIDEO_EXT.test(url);

export function validatePost(input: PostInput): void {
  const n = input.media_urls.length;
  if (n === 0) throw new Error("Informe ao menos uma URL de mídia.");
  if (input.post_type === "carousel" && (n < 2 || n > 10)) {
    throw new Error("Carrossel precisa de 2 a 10 mídias.");
  }
  if (input.post_type !== "carousel" && n !== 1) {
    throw new Error(`Post do tipo ${input.post_type} aceita exatamente 1 mídia.`);
  }
  if (input.post_type === "reel" && !isVideoUrl(input.media_urls[0])) {
    throw new Error("Reel precisa de um vídeo (.mp4 ou .mov).");
  }
  if (input.caption && input.caption.length > 2200) {
    throw new Error("Legenda passa de 2.200 caracteres.");
  }
}

function mediaField(url: string) {
  return isVideoUrl(url) ? { video_url: url } : { image_url: url };
}

export async function createContainer(ig: GraphClient, input: PostInput): Promise<string> {
  validatePost(input);
  const caption = input.caption ?? undefined;
  const [first] = input.media_urls;
  let body: Record<string, unknown>;

  switch (input.post_type) {
    case "photo":
      if (isVideoUrl(first)) throw new Error("Para vídeo no feed use o tipo reel.");
      body = { image_url: first, caption };
      break;
    case "reel":
      body = { media_type: "REELS", video_url: first, caption };
      break;
    case "story":
      body = { media_type: "STORIES", ...mediaField(first) };
      break;
    case "carousel": {
      // Os itens são criados e aguardados em paralelo: em série, um carrossel de
      // 8 imagens passava do tempo limite da função.
      const children = await Promise.all(
        input.media_urls.map(async (url) => {
          const child = await ig.post<{ id: string }>(`${ig.userId}/media`, {
            is_carousel_item: true,
            ...(isVideoUrl(url) ? { media_type: "VIDEO", video_url: url } : { image_url: url }),
          });
          return child.id;
        }),
      );
      const ready = await Promise.all(children.map((id) => waitUntilReady(ig, id)));
      if (ready.includes(false)) throw new Error("Itens do carrossel ainda processando: tente de novo em instantes.");
      body = { media_type: "CAROUSEL", children: children.join(","), caption };
      break;
    }
  }

  const container = await ig.post<{ id: string }>(`${ig.userId}/media`, body);
  return container.id;
}

export type ContainerStatus = "FINISHED" | "IN_PROGRESS" | "ERROR" | "EXPIRED" | "PUBLISHED";

export async function containerStatus(ig: GraphClient, containerId: string) {
  return ig.get<{ status_code: ContainerStatus; status?: string }>(containerId, { fields: "status_code,status" });
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Espera o container ficar pronto. Retorna false se estourar o tempo. */
export async function waitUntilReady(
  ig: GraphClient,
  containerId: string,
  { timeoutMs = 90_000, intervalMs = 3_000 } = {},
): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const { status_code, status } = await containerStatus(ig, containerId);
    if (status_code === "FINISHED" || status_code === "PUBLISHED") return true;
    if (status_code === "ERROR" || status_code === "EXPIRED") {
      throw new Error(`Container ${containerId} falhou (${status_code}): ${status ?? "sem detalhes"}`);
    }
    if (Date.now() + intervalMs > deadline) return false;
    await sleep(intervalMs);
  }
}

export async function publishContainer(ig: GraphClient, containerId: string): Promise<string> {
  const res = await ig.post<{ id: string }>(`${ig.userId}/media_publish`, { creation_id: containerId });
  return res.id;
}

export type PublishResult =
  | { status: "published"; mediaId: string; containerId: string }
  | { status: "processing"; containerId: string };

/** Cria (ou reaproveita) o container e publica se ficar pronto dentro do prazo. */
export async function publishPost(
  ig: GraphClient,
  input: PostInput,
  opts: { containerId?: string | null; timeoutMs?: number } = {},
): Promise<PublishResult> {
  const containerId = opts.containerId ?? (await createContainer(ig, input));
  const ready = await waitUntilReady(ig, containerId, { timeoutMs: opts.timeoutMs });
  if (!ready) return { status: "processing", containerId };
  const mediaId = await publishContainer(ig, containerId);
  return { status: "published", mediaId, containerId };
}
