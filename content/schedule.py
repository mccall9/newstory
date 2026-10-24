"""Sobe os slides para o Supabase Storage, agenda cada post e cria a regra de comente-e-ganhe."""
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
SP = HERE.parent
ENV = dict(l.split("=", 1) for l in (SP / "vercel-env.txt").read_text().splitlines() if "=" in l and not l.startswith("#"))
MCP_TOKEN = ENV["MCP_AUTH_TOKEN"]
SERVICE_KEY = sys.argv[2]
STORAGE = "https://lmiyawgqqnunfjmjqvxd.supabase.co/storage/v1/object"
SITE = "https://newstory-two.vercel.app"


def mcp(tool, args):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": args}}).encode()
    req = urllib.request.Request(f"{SITE}/api/mcp", data=body, method="POST", headers={
        "Authorization": f"Bearer {MCP_TOKEN}", "content-type": "application/json",
        "accept": "application/json, text/event-stream", "mcp-protocol-version": "2025-06-18"})
    raw = urllib.request.urlopen(req, timeout=120).read().decode()
    line = next(l[5:].strip() if l.startswith("data:") else l for l in raw.splitlines() if l.startswith("data:") or l.startswith("{"))
    res = json.loads(line)["result"]
    if res.get("isError"):
        raise RuntimeError(f"{tool}: {res['content'][0]['text']}")
    return json.loads(res["content"][0]["text"])


def upload(local, remote):
    req = urllib.request.Request(f"{STORAGE}/media/{remote}", data=Path(local).read_bytes(), method="POST", headers={
        "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "image/jpeg", "x-upsert": "true"})
    urllib.request.urlopen(req, timeout=60).read()
    return f"{STORAGE}/public/media/{remote}"


plan = json.loads(Path(sys.argv[1]).read_text())
for item in plan:
    slug, prefix, hour = item["slug"], item["prefix"], item["at"]
    files = sorted(HERE.glob(f"{prefix}-[0-9]*.jpg"), key=lambda p: int(re.search(r"-(\d+)\.jpg$", p.name).group(1)))
    urls = [upload(f, f"posts/{slug}/slide-{i}.jpg") for i, f in enumerate(files, 1)]
    post = mcp("ig_schedule_post", {"post_type": "carousel", "media_urls": urls,
                                    "caption": (HERE / f"caption-{slug}.txt").read_text(), "publish_at": hour})
    line = f"{hour}  {slug:<11} {len(urls)} slides  post={post['id'][:8]}"
    if item.get("keyword"):
        rule = mcp("ig_create_keyword_rule", {
            "name": item["name"], "keywords": [item["keyword"]],
            "dm_message": f"Oi {{username}}! {item['dm']}\n\n{{link}}",
            "link": f"{SITE}/{item['page']}", "public_reply": "Te mandei no direct!"})
        line += f"  regra={item['keyword']} ({rule['id'][:8]})"
    print(line, flush=True)
