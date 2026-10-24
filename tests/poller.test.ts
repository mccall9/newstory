import { describe, expect, it } from "vitest";
import type { KeywordRule } from "../src/db.js";
import type { GraphClient } from "../src/instagram/client.js";
import { mediaToWatch, toEvents } from "../src/poller.js";

const now = Date.parse("2026-10-24T12:00:00Z");
const rule = (ig_media_id: string | null) => ({ ig_media_id }) as KeywordRule;

describe("toEvents", () => {
  const comments = [
    { id: "c1", text: "QUERO", timestamp: "2026-10-24T11:00:00+0000", from: { id: "u1", username: "ana" } },
    { id: "c2", text: "QUERO", timestamp: "2026-10-10T11:00:00+0000", from: { id: "u2" } },
    { id: "c3", text: "QUERO", timestamp: "2026-10-24T11:00:00+0000", from: { id: "u3" } },
    { id: "c4", text: "sem autor", timestamp: "2026-10-24T11:00:00+0000" },
  ];

  it("ignora comentários já atendidos, sem autor ou fora da janela de 7 dias", () => {
    const events = toEvents("m1", comments, now, new Set(["c3"]));
    expect(events).toEqual([{ commentId: "c1", text: "QUERO", mediaId: "m1", fromId: "u1", fromUsername: "ana" }]);
  });
});

describe("mediaToWatch", () => {
  const ig = {
    userId: "IG1",
    get: async () => ({ data: [{ id: "r1" }, { id: "m1" }] }),
  } as unknown as GraphClient;

  it("só vigia os posts das regras específicas", async () => {
    expect(await mediaToWatch(ig, [rule("m1")], 3)).toEqual(["m1"]);
  });
  it("com regra geral, inclui os posts recentes sem duplicar", async () => {
    expect(await mediaToWatch(ig, [rule("m1"), rule(null)], 3)).toEqual(["m1", "r1"]);
  });
});
