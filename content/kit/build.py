"""Gera o PDF do Kit Claude no Trabalho a partir de kit.json.

Uso: python3 build.py   (gera kit.html e, com o Playwright, Kit-Claude-no-Trabalho.pdf)
"""
import html as H
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
kit = json.loads((HERE / "kit.json").read_text())

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');
@page { size: A4; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter Tight', sans-serif; color: #121211; background: #F3F1EC; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; overflow: hidden; padding: 22mm 20mm; page-break-after: always; position: relative; }
.logo { font: 800 18pt 'Bricolage Grotesque', sans-serif; letter-spacing: -0.5pt; display: flex; align-items: center; gap: 6pt; }
.logo i { width: 7pt; height: 7pt; background: #FF5F1F; border-radius: 1.5pt; transform: rotate(45deg); display: inline-block; }
.cover { background: #121211; color: #F3F1EC; display: flex; flex-direction: column; justify-content: space-between; }
.cover h1 { font: 400 64pt/0.95 'Instrument Serif', serif; letter-spacing: -1pt; margin: 40mm 0 10mm; }
.cover h1 em { font-style: italic; color: #FF5F1F; }
.cover p { font: 500 14pt/1.4 'Inter Tight', sans-serif; color: rgba(243,241,236,.8); max-width: 140mm; }
.tag { display: inline-block; background: #FF5F1F; color: #fff; border-radius: 20pt; padding: 5pt 12pt; font: 700 9pt 'Inter Tight', sans-serif; letter-spacing: 3pt; }
.small { font: 500 9pt 'Inter Tight', sans-serif; opacity: .6; }
h2 { font: 400 34pt/1 'Instrument Serif', serif; margin: 8mm 0 6mm; }
h2 em { font-style: italic; color: #FF5F1F; }
.kicker { font: 700 9pt 'Inter Tight', sans-serif; letter-spacing: 3pt; text-transform: uppercase; color: #FF5F1F; margin-top: 12mm; }
ol.how { padding-left: 14pt; font: 500 11.5pt/1.55 'Inter Tight', sans-serif; color: #3B3936; }
ol.how li { margin-bottom: 4pt; }
.toc div { display: flex; justify-content: space-between; border-bottom: 1px solid rgba(18,18,17,.15); padding: 7pt 0; font: 500 12pt 'Inter Tight', sans-serif; }
.toc b { font: 400 16pt 'Instrument Serif', serif; color: #FF5F1F; }
.item { break-inside: avoid; margin-bottom: 5mm; }
.item h3 { font: 700 11.5pt 'Inter Tight', sans-serif; margin-bottom: 2.5pt; display: flex; gap: 6pt; align-items: baseline; }
.item h3 span { font: 400 15pt 'Instrument Serif', serif; color: #FF5F1F; }
.item pre { white-space: pre-wrap; word-break: break-word; background: #121211; color: #F3F1EC; border-radius: 8pt; padding: 9pt 11pt; font: 500 9pt/1.5 'JetBrains Mono', monospace; }
.compact .item { margin-bottom: 3.2mm; } .compact h2 { margin: 6mm 0 4mm; } .compact .kicker { margin-top: 8mm; }
.foot { position: absolute; left: 20mm; right: 20mm; bottom: 10mm; display: flex; justify-content: space-between; font: 500 8pt 'Inter Tight', sans-serif; opacity: .5; }
.end { background: #121211; color: #F3F1EC; }
.end h2 { font-size: 44pt; margin-top: 60mm; }
.end p { font: 500 13pt/1.5 'Inter Tight', sans-serif; color: rgba(243,241,236,.8); max-width: 140mm; margin-top: 6mm; }
"""


def esc(s):
    return H.escape(s)


def foot(label):
    return f'<div class="foot"><span>Kit Claude no Trabalho · Pattiners</span><span>{label}</span></div>'


pages = []
pages.append(f'''<section class="page cover">
  <div class="logo"><i></i>pattiners</div>
  <div><span class="tag">KIT</span><h1>Claude <em>no trabalho</em></h1><p>{esc(kit["subtitle"])}</p></div>
  <div class="small">Uso pessoal. Proibida a revenda ou distribuição.</div>
</section>''')

how = "".join(f"<li>{esc(h)}</li>" for h in kit["how"])
toc = "".join(f'<div><span>{esc(a["name"])}</span><b>{len(a["prompts"])}</b></div>' for a in kit["areas"])
toc += f'<div><span>Assistentes configurados</span><b>{len(kit["assistants"])}</b></div><div><span>Bônus</span><b>{len(kit["bonus"])}</b></div>'
pages.append(f'''<section class="page"><div class="logo"><i></i>pattiners</div>
  <div class="kicker">Antes de começar</div><h2>Como usar <em>este kit</em></h2><ol class="how">{how}</ol>
  <div class="kicker">Conteúdo</div><h2>O que tem <em>aqui</em></h2><div class="toc">{toc}</div>{foot("Introdução")}</section>''')

n = 0
PER_PAGE = 5  # 10 prompts por área não cabem numa página A4
for i, area in enumerate(kit["areas"], 1):
    for start in range(0, len(area["prompts"]), PER_PAGE):
        items = ""
        for title, prompt in area["prompts"][start:start + PER_PAGE]:
            n += 1
            items += f'<div class="item"><h3><span>{n:02d}</span>{esc(title)}</h3><pre>{esc(prompt)}</pre></div>'
        head = f'<div class="kicker">Parte {i:02d}</div><h2>{esc(area["name"])}</h2>' if start == 0 else f'<div class="kicker">Parte {i:02d} · continuação</div><h2 style="font-size:24pt">{esc(area["name"])}</h2>'
        pages.append(f'''<section class="page"><div class="logo"><i></i>pattiners</div>
  {head}{items}{foot(area["name"])}</section>''')

items = "".join(f'<div class="item"><h3><span>{i:02d}</span>{esc(t)}</h3><pre>{esc(p)}</pre></div>' for i, (t, p) in enumerate(kit["assistants"], 1))
pages.append(f'''<section class="page compact"><div class="logo"><i></i>pattiners</div>
  <div class="kicker">Assistentes</div><h2>5 assistentes <em>configurados</em></h2>
  <ol class="how" style="margin-bottom:6mm"><li>No Claude, crie um Projeto e cole o texto no campo de instruções. Toda conversa dentro dele segue essas regras.</li><li>No ChatGPT, use as instruções personalizadas ou crie um GPT.</li></ol>{items}{foot("Assistentes")}</section>''')

items = "".join(f'<div class="item"><h3>{esc(t)}</h3><pre>{esc(p)}</pre></div>' for t, p in kit["bonus"])
pages.append(f'''<section class="page"><div class="logo"><i></i>pattiners</div>
  <div class="kicker">Bônus</div><h2>Para ir <em>além</em></h2>{items}{foot("Bônus")}</section>''')

pages.append('''<section class="page end"><div class="logo"><i></i>pattiners</div>
  <h2>Bom <em>trabalho.</em></h2><p>Novos prompts e tutoriais toda semana no Instagram @pattiners.ai. Dúvidas sobre o kit: mande uma mensagem direta para @pattiners.ai.</p></section>''')

(HERE / "kit.html").write_text(f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Kit Claude no Trabalho</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>')
subprocess.run(["node", "-e", f"""
const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{HERE}/kit.html');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);
await p.pdf({{path:'{HERE}/Kit-Claude-no-Trabalho.pdf',format:'A4',printBackground:true,preferCSSPageSize:true}});await b.close();}})()"""], check=True)
print("prompts:", n)
