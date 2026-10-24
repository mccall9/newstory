import { beforeEach, describe, expect, it } from "vitest";
import { GET, POST } from "../api/mcp.js";

const rpc = (body: unknown, auth = "Bearer teste") =>
  new Request("https://exemplo.com/api/mcp", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/json, text/event-stream",
      "mcp-protocol-version": "2025-06-18",
      authorization: auth,
    },
    body: JSON.stringify(body),
  });

async function readJson(res: Response) {
  const text = await res.text();
  const data = text.startsWith("{") ? text : text.split("\n").find((l) => l.startsWith("data:"))?.slice(5);
  return JSON.parse(data ?? "{}");
}

describe("endpoint MCP", () => {
  beforeEach(() => {
    process.env.MCP_AUTH_TOKEN = "teste";
  });

  it("recusa sem token", async () => {
    const res = await POST(rpc({ jsonrpc: "2.0", id: 1, method: "tools/list" }, "Bearer errado"));
    expect(res.status).toBe(401);
    expect((await GET(new Request("https://exemplo.com/api/mcp"))).status).toBe(401);
  });

  it("lista as ferramentas", async () => {
    const res = await POST(rpc({ jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }));
    expect(res.status).toBe(200);
    const json = await readJson(res);
    const names = json.result.tools.map((t: { name: string }) => t.name);
    expect(names).toEqual(
      expect.arrayContaining(["ig_get_profile", "ig_publish_now", "ig_schedule_post", "ig_create_keyword_rule", "ig_business_discovery"]),
    );
  });
});
