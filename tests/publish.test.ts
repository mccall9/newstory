import { describe, expect, it } from "vitest";
import type { GraphClient } from "../src/instagram/client.js";
import { publishPost, validatePost } from "../src/instagram/publish.js";

function fakeClient(statuses: string[] = ["FINISHED"]) {
  const calls: { method: string; path: string; body?: any }[] = [];
  let n = 0;
  const client: GraphClient = {
    userId: "IG1",
    async get(path) {
      calls.push({ method: "GET", path });
      return { status_code: statuses[Math.min(n++, statuses.length - 1)] } as any;
    },
    async post(path, body) {
      calls.push({ method: "POST", path, body });
      return { id: path.endsWith("media_publish") ? "MEDIA1" : `C${calls.length}` } as any;
    },
    async delete() {
      return {} as any;
    },
  };
  return { client, calls };
}

describe("validatePost", () => {
  it("carrossel precisa de 2 a 10 mídias", () => {
    expect(() => validatePost({ post_type: "carousel", media_urls: ["a.jpg"] })).toThrow();
  });
  it("reel precisa de vídeo", () => {
    expect(() => validatePost({ post_type: "reel", media_urls: ["https://x/a.jpg"] })).toThrow();
  });
});

describe("publishPost", () => {
  it("publica foto em duas etapas", async () => {
    const { client, calls } = fakeClient();
    const res = await publishPost(client, { post_type: "photo", media_urls: ["https://x/a.jpg"], caption: "oi" });
    expect(res).toEqual({ status: "published", mediaId: "MEDIA1", containerId: "C1" });
    expect(calls[0]).toEqual({ method: "POST", path: "IG1/media", body: { image_url: "https://x/a.jpg", caption: "oi" } });
    expect(calls.at(-1)).toMatchObject({ path: "IG1/media_publish", body: { creation_id: "C1" } });
  });

  it("monta carrossel com itens filhos", async () => {
    const { client, calls } = fakeClient();
    await publishPost(client, { post_type: "carousel", media_urls: ["https://x/1.jpg", "https://x/2.mp4"] });
    const posts = calls.filter((c) => c.method === "POST");
    expect(posts[0].body).toEqual({ is_carousel_item: true, image_url: "https://x/1.jpg" });
    expect(posts[1].body).toEqual({ is_carousel_item: true, media_type: "VIDEO", video_url: "https://x/2.mp4" });
    expect(posts[2].body).toMatchObject({ media_type: "CAROUSEL", children: "C1,C2" });
  });

  it("devolve processing quando o vídeo não fica pronto a tempo", async () => {
    const { client } = fakeClient(["IN_PROGRESS"]);
    const res = await publishPost(client, { post_type: "reel", media_urls: ["https://x/v.mp4"] }, { timeoutMs: 0 });
    expect(res).toEqual({ status: "processing", containerId: "C1" });
  });

  it("falha quando o container dá erro", async () => {
    const { client } = fakeClient(["ERROR"]);
    await expect(publishPost(client, { post_type: "story", media_urls: ["https://x/a.jpg"] })).rejects.toThrow(/ERROR/);
  });
});
