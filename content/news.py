"""Modelo editorial da Pattiners (notícias e histórias de IA).

Uso: python3 news.py noticias.json   (gera CARROSSEL-<slug>.html e, se houver guia, public/<slug>.html)
"""
import html as H
import json
import sys
from pathlib import Path

import gen  # reaproveita o gerador das páginas-guia

HERE = Path(__file__).parent / "carrosseis"
UNSPLASH = "https://images.unsplash.com/photo-{}?w=1400&q=85&auto=format"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Inter+Tight:wght@400;500;600;700&display=swap');
:root { --paper: #F3F1EC; --ink: #121211; --orange: #FF5F1F; --peach: #FFD9C5; --muted: #3B3936; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a10; font-family: 'Inter Tight', sans-serif; display: flex; flex-direction: column; align-items: center; padding: 30px 15px; }
.slides-wrap { display: flex; flex-wrap: wrap; gap: 18px; justify-content: center; max-width: 1400px; }
.s { width: 1080px; height: 1350px; position: relative; overflow: hidden; flex-shrink: 0; transform: scale(0.30); transform-origin: top left; margin-bottom: -945px; margin-right: -756px; }
.light { background: var(--paper); color: var(--ink); }
.dark { background: var(--ink); color: var(--paper); }
.light::before { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .55; mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.5 0 0 0 0 0.45 0 0 0 0 0.4 0 0 0 .18 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }

.logo { position: absolute; top: 64px; left: 60px; z-index: 5; font: 800 40px/1 'Bricolage Grotesque', sans-serif; letter-spacing: -1.4px; display: flex; align-items: center; gap: 10px; }
.logo i { width: 14px; height: 14px; background: var(--orange); border-radius: 3px; transform: rotate(45deg); }
.count { position: absolute; top: 52px; right: 52px; z-index: 5; padding: 12px 24px; border-radius: 40px; font: 500 28px 'Inter Tight', sans-serif; }
.light .count { background: rgba(18,18,17,.55); color: #fff; }
.dark .count, .cover .count { background: rgba(255,255,255,.16); color: #fff; }
.foot { position: absolute; left: 60px; right: 60px; bottom: 58px; z-index: 5; }
.foot hr { border: 0; height: 2px; background: currentColor; opacity: .85; }
.foot span { display: block; margin-top: 16px; font: 500 23px 'Inter Tight', sans-serif; letter-spacing: 3px; text-transform: uppercase; }

.page { position: absolute; inset: 160px 60px 140px; display: flex; flex-direction: column; justify-content: center; gap: 34px; }
.head { font: 400 88px/0.98 'Instrument Serif', serif; letter-spacing: -1.5px; }
.head em { font-style: italic; color: var(--orange); }
.head, .cover h1, .end-head, .stat { -webkit-text-stroke: 1.2px currentColor; }
.page.roomy .head { font-size: 112px; }
.page.roomy .text { font-size: 40px; }
.page.roomy .pill { font-size: 42px; }
.photo { width: 100%; height: 470px; border-radius: 30px; background-size: cover; background-position: center; flex-shrink: 0; }
.text { display: flex; flex-direction: column; gap: 22px; font: 500 33px/1.32 'Inter Tight', sans-serif; letter-spacing: -0.5px; }
.light .text { color: var(--muted); }
.dark .text { color: rgba(243,241,236,.85); }
.text b { color: inherit; font-weight: 700; }
.pill { align-self: flex-start; padding: 10px 18px; font: 600 36px 'Inter Tight', sans-serif; letter-spacing: -0.6px; background: var(--orange); color: #fff; }
.light .pill.soft { background: var(--peach); color: var(--ink); }
.src { font: 500 22px/1.4 'Inter Tight', sans-serif; opacity: .6; }
.stat { font: 400 300px/0.8 'Instrument Serif', serif; letter-spacing: -8px; color: var(--orange); }

.rows { display: flex; flex-direction: column; border-top: 2px solid rgba(243,241,236,.18); }
.r { display: flex; justify-content: space-between; align-items: baseline; padding: 22px 0; border-bottom: 2px solid rgba(243,241,236,.18); font: 500 34px 'Inter Tight', sans-serif; }
.r b { font: 400 64px/1 'Instrument Serif', serif; color: var(--orange); }

/* Capa */
.cover { background: var(--ink); color: #fff; }
.cover .bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
.cover .bg::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(18,18,17,.45) 0%, rgba(18,18,17,0) 22%, rgba(18,18,17,0) 40%, rgba(18,18,17,.9) 66%, #121211 100%); }
.cover .brand { position: absolute; top: 66px; left: 0; right: 0; z-index: 5; display: flex; align-items: center; justify-content: center; gap: 26px; font: 800 44px 'Bricolage Grotesque', sans-serif; letter-spacing: -1.5px; }
.cover .brand i { width: 200px; height: 2px; background: rgba(255,255,255,.7); }
.cover .txt { position: absolute; left: 60px; right: 60px; bottom: 120px; z-index: 5; display: flex; flex-direction: column; gap: 28px; }
.tag { align-self: flex-start; background: #fff; color: var(--ink); border-radius: 40px; padding: 12px 28px; font: 600 28px 'Inter Tight', sans-serif; letter-spacing: 6px; }
.cover h1 { font: 400 110px/0.95 'Instrument Serif', serif; letter-spacing: -2px; }
.cover h1 em { font-style: italic; color: var(--orange); }
.cover p { font: 500 32px/1.3 'Inter Tight', sans-serif; color: rgba(255,255,255,.85); }
.cover .spaced { font: 500 24px 'Inter Tight', sans-serif; letter-spacing: 14px; text-transform: uppercase; }

/* Fechamento */
.end-head { font: 400 104px/1 'Instrument Serif', serif; letter-spacing: -2px; }
.end-head span { background: var(--peach); padding: 0 12px; box-decoration-break: clone; -webkit-box-decoration-break: clone; }
.end-left { position: absolute; left: 60px; width: 470px; top: 690px; display: flex; flex-direction: column; gap: 44px; }
.end-left p { font: 500 36px/1.28 'Inter Tight', sans-serif; letter-spacing: -0.8px; }
.end-left p b { background: var(--orange); color: #fff; padding: 0 8px; }
.ask { font: 600 48px/1.18 'Inter Tight', sans-serif; letter-spacing: -1.2px; text-decoration: underline; text-decoration-thickness: 3px; text-underline-offset: 8px; }
.phone { position: absolute; left: 590px; top: 640px; width: 520px; height: 1000px; border-radius: 76px; background: var(--ink); padding: 18px; box-shadow: 0 30px 60px rgba(0,0,0,.2); }
.phone .screen { width: 100%; height: 100%; border-radius: 60px; overflow: hidden; background: #F6F1EA var(--phone) top center / 100% auto no-repeat; position: relative; }
.phone .island { position: absolute; top: 18px; left: 50%; transform: translateX(-50%); width: 150px; height: 42px; border-radius: 30px; background: var(--ink); }
.answers { display: flex; gap: 20px; }
.answers div { flex: 1; border: 3px solid var(--ink); border-radius: 24px; padding: 30px; text-align: center; font: 400 64px/1 'Instrument Serif', serif; }
.answers div:first-child { background: var(--ink); color: var(--paper); }
.caption-box { margin-top: 40px; max-width: 900px; width: 100%; background: #16151a; color: #ddd; border-radius: 12px; padding: 28px; font: 15px/1.6 'Inter Tight', sans-serif; white-space: pre-wrap; }
"""


def block(b):
    k = b["k"]
    if k == "photo":
        return f'<div class="photo" style="height:{b.get("h", 470)}px;background-image:url(\'{UNSPLASH.format(b["id"])}\')"></div>'
    if k == "text":
        return '<div class="text">' + "".join(f"<p>{p}</p>" for p in b["p"]) + "</div>"
    if k == "pill":
        return f'<div class="pill{" soft" if b.get("soft") else ""}">{b["t"]}</div>'
    if k == "src":
        return f'<div class="src">{b["t"]}</div>'
    if k == "stat":
        return f'<div class="stat">{b["t"]}</div>'
    if k == "rows":
        return '<div class="rows">' + "".join(f'<div class="r"><span>{a}</span><b>{v}</b></div>' for a, v in b["items"]) + "</div>"
    raise ValueError(k)


def carousel(post):
    total = len(post["slides"]) + 2
    c = post["cover"]
    out = [f'''<div class="s cover" id="slide-1"><div class="bg" style="background-image:url('{UNSPLASH.format(c["photo"])}')"></div>
  <div class="brand"><i></i>pattiners<i></i></div><div class="count">1/{total}</div>
  <div class="txt"><div class="tag">{c.get("tag", "NOTÍCIA")}</div><h1>{c["title"]}</h1><p>{c["sub"]}</p><div class="spaced">Arraste para o lado</div></div></div>''']
    for i, s in enumerate(post["slides"], 2):
        theme = s.get("theme") or ("light" if i % 2 == 0 else "dark")
        body = "".join(block(b) for b in s["blocks"])
        roomy = "" if any(b["k"] in ("photo", "rows", "stat") for b in s["blocks"]) else " roomy"
        out.append(f'''<div class="s {theme}" id="slide-{i}"><div class="logo"><i></i>pattiners</div><div class="count">{i}/{total}</div>
  <div class="page{roomy}"><div class="head">{s["head"]}</div>{body}</div>
  <div class="foot"><hr><span>Arraste para o lado</span></div></div>''')
    e = post["end"]
    if e.get("keyword"):
        right = f'<div class="phone"><div class="screen"><div class="island"></div></div></div>'
        left = f'<div class="end-left"><p>{e["text"]}</p><div class="ask">Comente “{e["keyword"]}” e receba na sua DM</div></div>'
    else:
        right = ""
        left = f'<div class="end-left" style="width:auto;right:60px;top:640px"><p>{e["text"]}</p><div class="answers">{"".join(f"<div>{a}</div>" for a in e["answers"])}</div><div class="src">{e.get("src", "")}</div></div>'
    out.append(f'''<div class="s light" id="slide-{total}" style="--phone:url('phone-{post["slug"]}.png')"><div class="logo"><i></i>pattiners</div><div class="count">{total}/{total}</div>
  <div style="position:absolute;left:60px;right:60px;top:190px" class="end-head">{e["head"]}</div>{left}{right}</div>''')
    return f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{post["slug"]}</title><style>{CSS}</style></head>
<body><div class="slides-wrap">{"".join(out)}</div><div class="caption-box">{H.escape(post["caption"])}</div></body></html>'''


if __name__ == "__main__":
    for post in json.loads(Path(sys.argv[1]).read_text()):
        if "guide" in post:
            (gen.PUBLIC / f"{post['slug']}.html").write_text(gen.guide(post))
        (HERE / f"CARROSSEL-{post['slug']}.html").write_text(carousel(post))
        (HERE / f"caption-{post['slug']}.txt").write_text(post["caption"])
        print("ok", post["slug"])
