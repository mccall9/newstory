import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";
import type { KeywordRule } from "../src/db.js";
import { buildDm, matchesKeyword, parseCommentEvents, pickRule, verifySignature } from "../src/webhook.js";

const rule = (over: Partial<KeywordRule> = {}): KeywordRule => ({
  id: "r1",
  name: "geral",
  ig_media_id: null,
  keywords: ["quero"],
  dm_message: "Oi {username}! Aqui: {link}",
  link: "https://exemplo.com/ebook",
  public_reply: null,
  active: true,
  ...over,
});

describe("verifySignature", () => {
  const body = '{"object":"instagram"}';
  const sig = "sha256=" + createHmac("sha256", "segredo").update(body).digest("hex");
  it("aceita assinatura válida", () => expect(verifySignature(body, sig, "segredo")).toBe(true));
  it("recusa segredo errado", () => expect(verifySignature(body, sig, "outro")).toBe(false));
  it("recusa header ausente ou malformado", () => {
    expect(verifySignature(body, null, "segredo")).toBe(false);
    expect(verifySignature(body, "sha1=abc", "segredo")).toBe(false);
  });
});

describe("parseCommentEvents", () => {
  it("extrai comentários do payload da Meta", () => {
    const events = parseCommentEvents({
      object: "instagram",
      entry: [
        {
          id: "123",
          changes: [
            { field: "comments", value: { id: "c1", text: "QUERO", media: { id: "m1" }, from: { id: "u1", username: "ana" } } },
            { field: "mentions", value: { id: "x" } },
          ],
        },
      ],
    });
    expect(events).toEqual([
      { commentId: "c1", text: "QUERO", mediaId: "m1", fromId: "u1", fromUsername: "ana", parentId: undefined },
    ]);
  });
  it("ignora outros objetos", () => expect(parseCommentEvents({ object: "page", entry: [] })).toEqual([]));
});

describe("matchesKeyword", () => {
  it("ignora maiúsculas e acentos", () => expect(matchesKeyword("Quéro sim!!", ["QUERO"])).toBe(true));
  it("exige palavra inteira", () => expect(matchesKeyword("queroquero", ["quero"])).toBe(false));
  it("aceita frases", () => expect(matchesKeyword("me manda o link por favor", ["o link"])).toBe(true));
  it("não casa sem a palavra", () => expect(matchesKeyword("que lindo", ["quero"])).toBe(false));
});

describe("pickRule", () => {
  const event = { commentId: "c", text: "quero", mediaId: "m1", fromId: "u" };
  it("prefere a regra do post específico", () => {
    const specific = rule({ id: "r2", ig_media_id: "m1" });
    expect(pickRule([rule(), specific], event)?.id).toBe("r2");
  });
  it("ignora regra presa a post agendado que ainda não foi publicado", () => {
    expect(pickRule([rule({ scheduled_post_id: "agendado-1" })], event)).toBeUndefined();
  });
  it("ignora regras de outros posts e inativas", () => {
    expect(pickRule([rule({ ig_media_id: "m2" }), rule({ active: false })], event)).toBeUndefined();
  });
});

describe("buildDm", () => {
  it("substitui variáveis", () => expect(buildDm(rule(), "ana")).toBe("Oi @ana! Aqui: https://exemplo.com/ebook"));
  it("anexa o link quando a mensagem não tem {link}", () => {
    expect(buildDm(rule({ dm_message: "Segue o material" }))).toBe("Segue o material\n\nhttps://exemplo.com/ebook");
  });
});
