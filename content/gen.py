"""Gera carrosséis no modelo Pattiners e as páginas-guia de cada post.

Uso: python3 gen.py posts.json   (gera CARROSSEL-<slug>.html e public/<slug>.html)
"""
import html as H
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent / "carrosseis"
PUBLIC = Path("/home/user/newstory/public")
UNSPLASH = "https://images.unsplash.com/photo-{}?w=1400&q=85&auto=format"

base = (HERE / "CARROSSEL-2026-10-24-motion-com-claude.html").read_text()
CSS = base[base.index("<style>") + 7 : base.index("</style>")]
CSS = CSS.replace("url('phone-motion.png')", "var(--phone)")
CSS = CSS.replace(".phone .screen { width: 100%; height: 100%; border-radius: 60px; overflow: hidden; background: #F6F1EA var(--phone) top center / 100% auto no-repeat;",
                  ".phone .screen { width: 100%; height: 100%; border-radius: 60px; overflow: hidden; background: #F6F1EA var(--phone) top center / 100% auto no-repeat;")
CSS += """

  /* Textura de papel nos slides claros */
  .light::before { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .5; mix-blend-mode: multiply;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.5 0 0 0 0 0.45 0 0 0 0 0.4 0 0 0 .18 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
  .light > * { position: relative; }
  .light > .top, .light > .bottom, .light > .task, .light > .cta-title, .light > .cta-left, .light > .phone { position: absolute; }

  /* Prompt como caixa de mensagem de chat */
  .chatbox { border-radius: 30px; padding: 34px 36px 22px; background: #1F1E1C; color: #F4F1EC; box-shadow: 0 24px 50px rgba(0,0,0,.22); }
  .dark .chatbox { background: #242320; border: 2px solid #33312D; }
  .chatbox small { display: block; font: 700 20px 'Inter Tight', sans-serif; letter-spacing: 4px; color: var(--orange); margin-bottom: 14px; }
  .chatbox .msg { font: 500 31px/1.45 'Inter Tight', sans-serif; letter-spacing: -0.3px; }
  .chatbox .msg .k { color: var(--orange); }
  .chatbox .bar2 { display: flex; align-items: center; justify-content: space-between; margin-top: 26px; }
  .chatbox .plus { width: 46px; height: 46px; border-radius: 50%; border: 2px solid #4A4743; color: #A8A29B; display: grid; place-items: center; font: 400 32px/1 'Inter Tight', sans-serif; }
  .chatbox .right { display: flex; align-items: center; gap: 18px; font: 500 22px 'Inter Tight', sans-serif; color: #A8A29B; }
  .chatbox .send { width: 50px; height: 50px; border-radius: 14px; background: var(--orange); color: #fff; display: grid; place-items: center; font: 700 28px/1 'Inter Tight', sans-serif; }
  .roomy .chatbox .msg { font-size: 42px; line-height: 1.4; }
  .roomy .chatbox { padding: 44px 44px 26px; }

  /* Barra lateral de app com item destacado */
  .side { align-self: flex-start; width: 560px; border-radius: 28px; background: #1F1E1C; color: #F4F1EC; padding: 28px 22px; box-shadow: 0 24px 50px rgba(0,0,0,.22); }
  .dark .side { background: #242320; border: 2px solid #33312D; }
  .side .app { font: 800 34px 'Bricolage Grotesque', sans-serif; padding: 0 18px 16px; }
  .side .it { font: 500 30px 'Inter Tight', sans-serif; padding: 14px 18px; border-radius: 16px; color: rgba(244,241,236,.75); }
  .side .it.on { color: #fff; outline: 4px solid var(--orange); outline-offset: -4px; background: rgba(255,95,31,.12); }
  .row2 { display: flex; gap: 40px; align-items: center; }
  .row2 .note { font: 800 52px/1 'Bricolage Grotesque', sans-serif; letter-spacing: -1.5px; }
  .row2 .note em { font-style: normal; color: var(--orange); }

  /* Capa com tipografia mista */
  .cover-text h1 i { font: italic 400 0.82em 'Inter Tight', sans-serif; letter-spacing: -2px; }
  .task.roomy { gap: 46px; }
  .roomy .title { font-size: 104px; letter-spacing: -2.5px; }
  .roomy .code { font-size: 35px; padding: 46px 44px; }
  .roomy .body { font-size: 38px; }
  .roomy .close { font-size: 46px; }
  .roomy .fix { font-size: 36px; padding: 34px 36px; }
  .big-n { font: 800 200px/0.8 'Bricolage Grotesque', sans-serif; letter-spacing: -8px; color: var(--orange); }
  .fix { border-radius: 22px; padding: 26px 30px; font: 600 31px/1.35 'Inter Tight', sans-serif; letter-spacing: -0.4px; }
  .light .fix { background: var(--peach); color: var(--ink); }
  .dark .fix { background: #1D1C1A; color: var(--paper); }
  .fix b { color: var(--orange); }
  .light .code { background: var(--ink); }
  .dark .code { background: #1D1C1A; border: 2px solid #2A2826; }
  .cover-type { position: absolute; right: -120px; top: 110px; width: 760px; height: 760px; border-radius: 120px; background: var(--orange); transform: rotate(45deg); opacity: .95; }
  .cover-type + .top + .cover-text h1 em { color: var(--ink); background: var(--paper); padding: 0 14px; }
"""


def top(n, total):
    return f'<div class="top"><div class="logo"><i></i>pattiners</div><div class="num">{n:02d} / {total:02d}</div></div>'


def bottom(n, total):
    bars = "".join('<i class="on"></i>' if i == n else "<i></i>" for i in range(1, total + 1))
    return f'<div class="bottom"><div class="bar">{bars}</div><div class="swipe">Arraste <b>→</b></div></div>'


def block(b):
    """Converte um bloco de conteúdo em HTML."""
    kind = b["k"]
    if kind == "body":
        return '<div class="body">' + "".join(f"<p>{p}</p>" for p in b["p"]) + "</div>"
    if kind == "close":
        return f'<div class="close">{b["t"]}</div>'
    if kind == "photo":
        return f'<div class="photo" style="height:{b.get("h", 450)}px;background-image:url(\'{UNSPLASH.format(b["id"])}\')"></div>'
    if kind == "code":
        return (f'<div class="chatbox"><small>{b.get("label", "COLE NO CLAUDE")}</small><div class="msg">{b["t"]}</div>'
                '<div class="bar2"><div class="plus">+</div><div class="right">Claude<div class="send">↑</div></div></div></div>')
    if kind == "side":
        items = "".join(f'<div class="it{" on" if it == b["on"] else ""}">{it}</div>' for it in b["items"])
        note = f'<div class="note">{b["note"]}</div>' if b.get("note") else ""
        return f'<div class="row2"><div class="side"><div class="app">{b.get("app", "Claude")}</div>{items}</div>{note}</div>'
    if kind == "fix":
        return f'<div class="fix">{b["t"]}</div>'
    if kind == "chat":
        return '<div class="chat">' + "".join(
            f'<div class="bubble{" ai" if who == "ai" else ""}">{t}</div>' for who, t in b["m"]
        ) + "</div>"
    if kind == "list":
        items = "".join(f'<div class="item"><div class="n">{i:02d}</div><div><b>{t}</b><span>{d}</span></div></div>'
                        for i, (t, d) in enumerate(b["items"], 1))
        return f'<div class="list{b.get("cls", "")}">{items}</div>'
    if kind == "cards":
        return '<div class="cards">' + "".join(
            f'<div class="opt"><small>{s}</small><b>{t}</b><p>{d}</p></div>' for s, t, d in b["items"]) + "</div>"
    if kind == "bign":
        return f'<div class="big-n">{b["t"]}</div>'
    raise ValueError(kind)


def carousel(post):
    slides = post["slides"]
    total = len(slides) + 2
    out = []
    c = post["cover"]
    art = (f'<div class="cover-photo" style="background-image:url(\'{UNSPLASH.format(c["photo"])}\')"></div>'
           if c.get("photo") else '<div class="cover-type"></div>')
    out.append(f'''<div class="s dark" id="slide-1">{art}{top(1, total)}
    <div class="cover-text"><div class="chip">{c.get("chip", "TUTORIAL")}</div>
    <h1 style="font-size:{c.get("size", 104)}px">{c["title"]}</h1><p>{c["sub"]}</p></div>{bottom(1, total)}</div>''')
    for i, s in enumerate(slides, 2):
        theme = "light" if i % 2 == 0 else "dark"
        blocks = "".join(block(b) for b in s["blocks"])
        roomy = "" if any(b["k"] in ("photo", "list", "cards", "chat") for b in s["blocks"]) else " roomy"
        if theme == "light":
            blocks = blocks.replace('class="list"', 'class="list light-list"')
        out.append(f'''<div class="s {theme}" id="slide-{i}">{top(i, total)}
    <div class="task{roomy}"><div class="label">{s["label"]}</div><div class="title">{s["title"]}</div>{blocks}</div>{bottom(i, total)}</div>''')
    cta = post["cta"]
    out.append(f'''<div class="s light" id="slide-{total}" style="--phone:url('phone-{post["slug"]}.png')">{top(total, total)}
    <div class="cta-title">{cta["title"]}</div>
    <div class="cta-left"><p>{cta["text"]}</p>
    <div class="keyword"><small>COMENTE</small><strong>{post["keyword"]}</strong><span>e receba o guia na sua DM.</span></div></div>
    <div class="phone"><div class="screen"><div class="island"></div></div></div></div>''')
    return f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{post["slug"]}</title><style>{CSS}</style></head>
<body><div class="slides-wrap">{"".join(out)}</div>
<div class="caption-box"><h3>Legenda</h3>{H.escape(post["caption"])}</div></body></html>'''


GUIDE_BASE = (PUBLIC / "claude.html").read_text()
G_HEAD = GUIDE_BASE[: GUIDE_BASE.index("<main>")]
G_SCRIPT = GUIDE_BASE[GUIDE_BASE.index("<script>"):]


def guide(post):
    g = post["guide"]
    head = G_HEAD.replace("<title>Claude no Dia a Dia</title>", f"<title>{g['tab']}</title>")
    head = head.replace(
        'content="5 prompts para o Claude fazer as tarefas chatas do seu dia, prontos para copiar. Pattiners Club."',
        f'content="{H.escape(g["desc"])}"')
    steps = ""
    for i, (title, why, prompt) in enumerate(g["steps"], 1):
        steps += f'''
  <section class="step">
    <header><h2><span>{i}.</span> {title}</h2><button data-copy="p{i}">Copiar</button></header>
    <p class="why">{why}</p>
    <pre id="p{i}">{H.escape(prompt)}</pre>
  </section>
'''
    body = f'''<main>
  <div class="brand">Pattiners Club</div>
  <h1>{g["h1"]}</h1>
  <p class="lead">{g["lead"]}</p>

  <div class="how"><b>{g["how_b"]}</b> {g["how"]}</div>
{steps}
  <div class="tips">
    <h3>{g["tips_h"]}</h3>
    <p>{g["tips"]}</p>
  </div>

  <footer>Feito por <a href="https://www.instagram.com/pattiners.ai/">@pattiners.ai</a> · <a href="/privacidade">Privacidade</a></footer>
</main>
'''
    return head + body + G_SCRIPT


if __name__ == "__main__":
    posts = json.loads(Path(sys.argv[1]).read_text())
    for post in posts:
        if "guide" in post:
            (PUBLIC / f"{post['slug']}.html").write_text(guide(post))
        (HERE / f"CARROSSEL-{post['slug']}.html").write_text(carousel(post))
        (HERE / f"caption-{post['slug']}.txt").write_text(post["caption"])
        print("ok", post["slug"])
