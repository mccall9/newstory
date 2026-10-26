"""Reels v2 da Pattiners: a interface do chat em ação, com narração, trilha e efeitos.

Uso: python3 build.py formula   (gera v2/<slug>/index.html a partir de PAUTAS[slug])
A mixagem do áudio fica em mix.py; os tempos daqui e de lá vêm da mesma pauta.
"""
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
PAUTAS = json.loads((HERE / "pautas.json").read_text())


def chars(text, cls):
    """Cada caractere vira um span, para a digitação ser animada no timeline."""
    return "".join(f'<span class="{cls}">{html.escape(c) if c != " " else "&nbsp;"}</span>' for c in text)


def words(text, cls):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split(" "))


CSS = """
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-normal-400.woff2") format("woff2"); font-style: normal; font-weight: 400; }
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-italic-400.woff2") format("woff2"); font-style: italic; font-weight: 400; }
@font-face { font-family: "Bricolage Grotesque"; src: url("assets/fonts/BricolageGrotesque-normal-800.woff2") format("woff2"); font-weight: 800; }
:root { --ink: #121211; --paper: #F3F1EC; --orange: #FF5F1F; --orange-d: #D9480F; --muted: #8E877F; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Inter", sans-serif; color: var(--paper); }
.full { position: absolute; inset: 0; }
#ground { background: var(--ink); }
#glow { position: absolute; width: 1500px; height: 1500px; left: -210px; top: -520px; border-radius: 50%; background: radial-gradient(circle, rgba(255,95,31,.30), transparent 60%); }
#flood { background: var(--paper); clip-path: circle(0px at 540px 1010px); }
.logo { position: absolute; top: 200px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 14px; font: 800 46px/1 "Bricolage Grotesque", sans-serif; letter-spacing: -1.6px; z-index: 30; }
.logo i { width: 18px; height: 18px; background: var(--orange); border-radius: 4px; transform: rotate(45deg); }
.logo span { color: var(--paper); }

/* Títulos */
.title { position: absolute; left: 80px; right: 80px; top: 560px; font: 400 150px/0.96 "Instrument Serif", serif; letter-spacing: -3px; z-index: 20; }
.title em { font-style: italic; color: var(--orange); }
.title .w { display: inline-block; }
#t9 { color: var(--ink); top: 300px; font-size: 104px; }
#t9 em, #build .head em { color: var(--orange-d); }

/* Janela do chat */
#chat { position: absolute; left: 60px; right: 60px; top: 380px; height: 760px; border-radius: 44px; background: #1C1B19; border: 2px solid #2E2C29; overflow: hidden; z-index: 10; box-shadow: 0 40px 120px rgba(0,0,0,.45); }
#chat .bar { height: 96px; display: flex; align-items: center; gap: 16px; padding: 0 40px; border-bottom: 2px solid #2E2C29; font: 600 32px "Inter", sans-serif; color: #CFC9C1; }
#chat .bar i { width: 18px; height: 18px; border-radius: 4px; background: var(--orange); transform: rotate(45deg); }
.msgs { position: absolute; left: 40px; right: 40px; top: 130px; display: flex; flex-direction: column; gap: 28px; }
.me { align-self: flex-end; max-width: 760px; background: #2E2C29; border-radius: 34px 34px 8px 34px; padding: 26px 32px; font: 500 38px/1.35 "Inter", sans-serif; color: var(--paper); }
.ai { max-width: 900px; font: 400 38px/1.45 "Inter", sans-serif; color: #A8A29B; }
.ai .w { opacity: 0; }
#stamp { position: absolute; right: 110px; top: 860px; transform: rotate(-8deg); border: 6px solid #E5484D; color: #E5484D; border-radius: 18px; padding: 10px 26px; font: 800 64px "Bricolage Grotesque", sans-serif; letter-spacing: 2px; z-index: 12; }
.input { position: absolute; left: 30px; right: 30px; bottom: 30px; height: 112px; border-radius: 30px; background: #262522; display: flex; align-items: center; padding: 0 30px; font: 500 36px "Inter", sans-serif; color: var(--muted); }
.send { position: absolute; right: 22px; top: 22px; width: 68px; height: 68px; border-radius: 20px; background: var(--orange); display: grid; place-items: center; color: #fff; font: 700 38px "Inter", sans-serif; }

/* Pedido montado com a fórmula (fundo claro) */
#build { position: absolute; left: 60px; right: 60px; top: 330px; display: flex; flex-direction: column; gap: 22px; z-index: 15; }
#build .head { font: 400 104px/1 "Instrument Serif", serif; color: var(--ink); letter-spacing: -2px; margin-bottom: 14px; }
#build .head em { font-style: italic; color: var(--orange); }
.part { display: flex; flex-direction: column; gap: 10px; background: #fff; border-radius: 30px; padding: 24px 30px; box-shadow: 0 10px 40px rgba(18,18,17,.08); }
.part small { align-self: flex-start; background: var(--orange-d); color: #fff; border-radius: 40px; padding: 8px 22px; font: 700 30px "Inter", sans-serif; letter-spacing: 4px; }
.part span { font: 500 38px/1.3 "Inter", sans-serif; color: var(--ink); }

/* Resposta boa */
#good { position: absolute; left: 60px; right: 60px; top: 520px; border-radius: 44px; background: #fff; padding: 44px 44px 40px; z-index: 16; box-shadow: 0 30px 90px rgba(18,18,17,.14); }
#good .lbl { display: flex; align-items: center; gap: 14px; font: 600 30px "Inter", sans-serif; color: var(--muted); margin-bottom: 26px; }
#good .lbl i { width: 16px; height: 16px; border-radius: 4px; background: var(--orange); transform: rotate(45deg); }
.cap { display: flex; gap: 22px; padding: 22px 0; border-top: 2px solid #ECE6DD; font: 500 38px/1.35 "Inter", sans-serif; color: var(--ink); }
.cap b { font: 400 54px/1 "Instrument Serif", serif; color: var(--orange-d); flex-shrink: 0; width: 46px; }
#ok { position: absolute; right: 60px; top: 470px; z-index: 17; background: var(--ink); color: var(--paper); border-radius: 40px; padding: 14px 26px; font: 700 28px "Inter", sans-serif; letter-spacing: 4px; }

/* Chamada final */
#cta { position: absolute; left: 70px; right: 70px; top: 360px; display: flex; flex-direction: column; align-items: center; gap: 40px; z-index: 25; }
#cta .c1 { font: 400 140px/1 "Instrument Serif", serif; color: var(--ink); letter-spacing: -3px; }
#cta .kw { background: var(--orange-d); color: #fff; border-radius: 40px; padding: 30px 60px; font: 800 150px/1 "Bricolage Grotesque", sans-serif; letter-spacing: -5px; }
#cta .c2 { font: 500 44px/1.3 "Inter", sans-serif; color: #3B3936; text-align: center; }
#dm { align-self: stretch; display: flex; gap: 22px; align-items: center; background: #fff; border-radius: 34px; padding: 26px 30px; box-shadow: 0 20px 60px rgba(18,18,17,.12); }
#dm .av { width: 84px; height: 84px; border-radius: 50%; background: var(--ink); display: grid; place-items: center; flex-shrink: 0; }
#dm .av i { width: 26px; height: 26px; border-radius: 6px; background: var(--orange); transform: rotate(45deg); }
#dm b { display: block; font: 700 32px "Inter", sans-serif; color: var(--ink); }
#dm span { font: 400 32px/1.3 "Inter", sans-serif; color: #5C564F; }

/* Legendas da narração */
.capt { position: absolute; left: 90px; right: 90px; top: 1190px; display: flex; justify-content: center; z-index: 40; }
.capt span { background: rgba(18,18,17,.88); color: #fff; border-radius: 22px; padding: 16px 28px; font: 600 42px/1.25 "Inter", sans-serif; text-align: center; }
.capt span em { font-style: normal; color: var(--orange); }
"""


def page(p):
    L = p["lines"]  # {id: [inicio, duracao, legenda]}
    cap_html = "".join(
        f'<div id="c{i}" class="clip capt" data-start="{a}" data-duration="{d}" data-track-index="9"><span>{t}</span></div>'
        for i, (a, d, t) in L.items()
    )
    bad = p["bad"]
    good = "".join(f'<div class="cap"><b>{n}</b><span>{t}</span></div>' for n, t in enumerate(p["good"], 1))
    parts = "".join(f'<div class="part" id="p{i}"><small>{k}</small><span>{v}</span></div>' for i, (k, v) in enumerate(p["parts"], 1))
    T = p["t"]
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{p['duration']}" data-width="1080" data-height="1920">
  <div id="bg" class="clip full" data-start="0" data-duration="{p['duration']}" data-track-index="0">
    <div id="ground" class="full"></div><div id="glow"></div><div id="flood" class="full"></div>
    <div class="logo"><i></i><span id="logotxt">pattiners</span></div>
  </div>

  <div id="hook" class="clip" data-start="0" data-duration="{T['chat_in']}" data-track-index="1">
    <div id="t1" class="title">{words(p['hook'], 'w')}</div>
    <div id="t2" class="title">{words(p['hook2'], 'w')}</div>
  </div>

  <div id="chatclip" class="clip" data-start="{T['chat_in'] - 0.2}" data-duration="{T['flood'] - T['chat_in'] + 0.8}" data-track-index="2">
    <div id="chat">
      <div class="bar"><i></i>Claude</div>
      <div class="msgs">
        <div class="me" id="bme">{chars(bad['ask'], 'k')}</div>
        <div class="ai" id="bai">{words(bad['answer'], 'w')}</div>
      </div>
      <div class="input"><span>Responder…</span><div class="send">↑</div></div>
    </div>
    <div id="stamp">GENÉRICO</div>
  </div>

  <div id="buildclip" class="clip" data-start="{T['flood']}" data-duration="{T['send2'] - T['flood'] + 0.6}" data-track-index="3">
    <div id="build"><div class="head">{p['build_head']}</div>{parts}</div>
  </div>

  <div id="goodclip" class="clip" data-start="{T['send2']}" data-duration="{T['cta'] - T['send2'] + 0.4}" data-track-index="4">
    <div id="t9" class="title">{words(p['same'], 'w')}</div>
    <div id="ok">PRONTO PARA POSTAR</div>
    <div id="good"><div class="lbl"><i></i>Claude</div>{good}</div>
  </div>

  <div id="ctaclip" class="clip" data-start="{T['cta']}" data-duration="{p['duration'] - T['cta']}" data-track-index="5">
    <div id="cta">
      <div class="c1">Comente</div>
      <div class="kw" id="kw">{p['keyword']}</div>
      <div class="c2">{p['promise']}</div>
      <div id="dm"><div class="av"><i></i></div><div><b>pattiners.ai</b><span>{p['dm']}</span></div></div>
    </div>
  </div>

  {cap_html}
  <audio id="mix" class="clip" src="assets/audio/mix.wav" data-start="0" data-duration="{p['duration']}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
const T = {json.dumps(T)};
const tl = gsap.timeline({{ paused: true }});
const out4 = "expo.out", io = "power2.inOut";

// Fundo: brilho respira devagar só no lado escuro; inundação de papel na virada
tl.fromTo("#glow", {{ x: 0 }}, {{ x: 120, duration: T.flood, ease: "none" }}, 0);
tl.to("#flood", {{ clipPath: "circle(2300px at 540px 1010px)", duration: 0.55, ease: io }}, T.flood);
tl.to("#logotxt", {{ color: "#121211", duration: 0.3 }}, T.flood + 0.15);

// 1. Gancho: visível no quadro 0, cada palavra assenta com desfoque
tl.fromTo("#t1 .w", {{ y: 18 }}, {{ y: 0, duration: 0.7, stagger: 0.06, ease: out4 }}, 0);
tl.to("#t1 .w", {{ filter: "blur(8px)", opacity: 0, duration: 0.16, stagger: 0.03 }}, T.hook2 - 0.2);
tl.fromTo("#t2 .w", {{ filter: "blur(10px)", opacity: 0 }}, {{ filter: "blur(0px)", opacity: 1, duration: 0.16, stagger: 0.12, ease: "none" }}, T.hook2);
tl.to("#t2", {{ y: -40, opacity: 0, filter: "blur(10px)", duration: 0.25, ease: "power3.in" }}, T.chat_in - 0.3);

// 2. O pedido ruim: a janela cresce a partir da caixa de texto
tl.fromTo("#chat", {{ scale: 0.55, y: 360, opacity: 0, filter: "blur(14px)" }}, {{ scale: 1, y: 0, opacity: 1, filter: "blur(0px)", duration: 0.65, ease: io }}, T.chat_in - 0.2);
tl.fromTo("#bme", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, T.type1);
tl.fromTo("#bme .k", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, stagger: {p['type_step']} }}, T.type1);
tl.to("#bai .w", {{ opacity: 1, duration: 0.12, stagger: 0.07 }}, T.answer1);
tl.fromTo("#stamp", {{ scale: 2.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.28, ease: "back.out(1.6)" }}, T.stamp);
tl.to(["#chat", "#stamp"], {{ scale: 0.9, opacity: 0, filter: "blur(12px)", duration: 0.3, ease: "power3.in" }}, T.flood - 0.05);

// 3. A fórmula: cada parte entra na palavra que a narra
tl.fromTo("#build .head", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: out4 }}, T.flood + 0.3);
{chr(10).join(f'tl.fromTo("#p{i}", {{ x: 140, opacity: 0, filter: "blur(8px)" }}, {{ x: 0, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: out4 }}, T.part{i});' for i in range(1, len(p['parts']) + 1))}
tl.to("#build", {{ y: -160, scale: 0.7, opacity: 0, filter: "blur(10px)", duration: 0.4, ease: "power3.in" }}, T.send2 - 0.05);

// 4. Mesma IA, outra resposta
tl.fromTo("#good", {{ y: 260, opacity: 0, scale: 0.92 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.6, ease: out4 }}, T.send2 + 0.15);
tl.fromTo("#good .cap", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.35, stagger: 0.32, ease: out4 }}, T.send2 + 0.55);
tl.fromTo("#t9 .w", {{ filter: "blur(10px)", opacity: 0 }}, {{ filter: "blur(0px)", opacity: 1, duration: 0.16, stagger: 0.09, ease: "none" }}, T.same);
tl.fromTo("#ok", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }}, T.ok);
tl.to(["#good", "#t9", "#ok"], {{ y: -120, opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power3.in" }}, T.cta - 0.1);

// 5. Chamada
tl.fromTo("#cta .c1", {{ filter: "blur(10px)", opacity: 0 }}, {{ filter: "blur(0px)", opacity: 1, duration: 0.2 }}, T.cta + 0.05);
tl.fromTo("#kw", {{ scale: 0.3, opacity: 0, rotation: -6 }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.5, ease: "back.out(1.5)" }}, T.kw);
tl.fromTo("#cta .c2", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: out4 }}, T.kw + 0.35);
tl.fromTo("#dm", {{ y: 160, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.55, ease: out4 }}, T.dm);

window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""


if __name__ == "__main__":
    for slug in sys.argv[1:]:
        (HERE / slug / "index.html").write_text(page(PAUTAS[slug]))
        print("ok", slug)
