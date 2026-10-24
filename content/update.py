"""Sobe slides novos (caminho versionado) e troca as mídias dos posts agendados, casando pelo horário."""
import json, re, sys
from pathlib import Path
PLANFILE = sys.argv[3]; sys.argv = [sys.argv[0], "plan.json", sys.argv[1], sys.argv[2], PLANFILE]
import importlib.util
spec = importlib.util.spec_from_file_location("sch", Path(__file__).with_name("schedule.py"))
src = Path(__file__).with_name("schedule.py").read_text().split("plan = json.loads")[0]
ns = {"__file__": str(Path(__file__).with_name("schedule.py"))}
exec(src, ns)
mcp, upload, HERE = ns["mcp"], ns["upload"], ns["HERE"]
version = sys.argv[3]
plan = json.loads((HERE / sys.argv[4]).read_text())
scheduled = mcp("ig_list_scheduled", {"status": "scheduled", "limit": 50})
by_time = {}
for p in scheduled:
    by_time[p["publish_at"][:16]] = p
from datetime import datetime, timezone
for item in plan:
    t = datetime.fromisoformat(item["at"]).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    post = by_time.get(t)
    if not post:
        print("sem agendamento para", item["slug"], t); continue
    files = sorted(HERE.glob(f"{item['prefix']}-[0-9]*.jpg"), key=lambda p: int(re.search(r"-(\d+)\.jpg$", p.name).group(1)))
    urls = [upload(f, f"posts-{version}/{item['slug']}/slide-{i}.jpg") for i, f in enumerate(files, 1)]
    res = mcp("ig_update_scheduled", {"id": post["id"], "media_urls": urls, "caption": (HERE / f"caption-{item['slug']}.txt").read_text()})
    print(item["slug"], t, len(urls), res["status"], flush=True)
