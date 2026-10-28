"""Novelinha "Diário de uma Estagiária com IA", episódio 1: O relatório das 8h.

Uso: python3 ep1.py   (escreve ep1/index.html e mixa ep1/assets/audio/mix.wav)
Tudo acontece na tela do celular, sem narração: funciona no mudo.
"""
import html
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "ep1"
SFX = Path("/root/.claude/skills/media-use/audio/assets/sfx")
DUR = 31.5


def ch(text, cls="k"):
    return "".join(f'<span class="{cls}">{html.escape(c) if c != " " else "&nbsp;"}</span>' for c in text)


def wd(text, cls="a"):
    return " ".join(f'<span class="{cls}">{html.escape(w)}</span>' for w in text.split(" "))


ASK1 = "Tenho uma planilha de vendas bagunçada e preciso de um relatório pro meu chefe até 8h. Me ajuda?"
AI1 = "Bora. Antes, me diz duas coisas: quem vai ler e o que essa pessoa precisa decidir?"
ASK2 = "Meu chefe. Ele quer saber se a campanha de setembro funcionou."
AI2 = [
    "Então o relatório tem 4 partes:",
    "<b>1.</b> A resposta em uma frase: funcionou ou não",
    "<b>2.</b> Vendas antes e depois, em gráfico",
    "<b>3.</b> O que puxou o resultado",
    "<b>4.</b> O que fazer em novembro",
]
REPLY = "Claro! Às 8h está na sua mesa."

CSS = """
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-normal-400.woff2") format("woff2"); font-style: normal; font-weight: 400; }
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-italic-400.woff2") format("woff2"); font-style: italic; font-weight: 400; }
@font-face { font-family: "Bricolage Grotesque"; src: url("assets/fonts/BricolageGrotesque-normal-800.woff2") format("woff2"); font-weight: 800; }
:root { --ink: #121211; --paper: #F3F1EC; --orange: #FF5F1F; --od: #D9480F; --muted: #8A8279; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Inter", sans-serif; color: var(--ink); }
.full { position: absolute; inset: 0; }
#ground { background: radial-gradient(110% 70% at 50% 30%, #2A1A12 0%, #151312 55%, #0E0D0C 100%); }
.series { position: absolute; top: 182px; left: 0; right: 0; display: flex; justify-content: center; z-index: 50; }
.series span { background: rgba(255,255,255,.1); color: #F3F1EC; border: 2px solid rgba(255,255,255,.18); border-radius: 40px; padding: 12px 28px; font: 800 24px "Inter", sans-serif; letter-spacing: 4px; }
.series span b { color: var(--orange); }

/* Tela bloqueada */
#lock .clock { position: absolute; top: 300px; left: 0; right: 0; text-align: center; color: #F3F1EC; font: 400 230px/1 "Inter", sans-serif; letter-spacing: -8px; }
#lock .date { position: absolute; top: 540px; left: 0; right: 0; text-align: center; color: rgba(243,241,236,.7); font: 700 36px "Inter", sans-serif; }
.notif { position: absolute; left: 70px; right: 70px; background: rgba(250,248,244,.94); border-radius: 36px; padding: 26px 30px; display: flex; gap: 22px; box-shadow: 0 20px 60px rgba(0,0,0,.35); }
.notif .ic { width: 78px; height: 78px; border-radius: 20px; background: #1F9D55; flex-shrink: 0; display: grid; place-items: center; color: #fff; font: 900 36px "Inter", sans-serif; }
.notif .tx { flex: 1; }
.notif .top { display: flex; justify-content: space-between; font: 700 30px "Inter", sans-serif; }
.notif .top i { font-style: normal; font-weight: 400; color: var(--muted); font-size: 26px; }
.notif p { margin-top: 6px; font: 400 33px/1.3 "Inter", sans-serif; color: #2B2926; }
#n1 { top: 660px; } #n2 { top: 860px; }

/* Pensamento da Bia */
.thought { position: absolute; left: 90px; right: 90px; top: 1110px; display: flex; justify-content: center; z-index: 45; }
.thought span { background: var(--paper); color: var(--ink); border-radius: 28px; padding: 18px 34px; font: italic 400 62px/1.05 "Instrument Serif", serif; box-shadow: 0 16px 50px rgba(0,0,0,.3); }
.thought span em { color: var(--od); }

/* Conversa com o chefe (tema claro) */
.panel { position: absolute; left: 50px; right: 50px; top: 260px; height: 1040px; border-radius: 52px; overflow: hidden; box-shadow: 0 40px 120px rgba(0,0,0,.5); }
.light { background: #EFEAE2; }
.light .hd { height: 130px; background: #fff; display: flex; align-items: center; gap: 22px; padding: 0 36px; border-bottom: 2px solid #E4DDD2; }
.av { width: 76px; height: 76px; border-radius: 50%; background: #3B3936; color: #fff; display: grid; place-items: center; font: 900 34px "Inter", sans-serif; flex-shrink: 0; }
.hd .nm { font: 800 36px "Inter", sans-serif; }
.hd .st { position: relative; height: 32px; margin-top: 4px; font: 400 27px "Inter", sans-serif; color: var(--muted); }
.hd .st span { position: absolute; left: 0; top: 0; white-space: nowrap; }
.hd .st .typing { color: #1F9D55; font-weight: 700; opacity: 0; }
.msgs { position: absolute; left: 30px; right: 30px; top: 160px; display: flex; flex-direction: column; gap: 16px; }
.b { max-width: 780px; border-radius: 30px; padding: 20px 26px 16px; font: 400 36px/1.32 "Inter", sans-serif; box-shadow: 0 2px 0 rgba(0,0,0,.05); }
.them { align-self: flex-start; background: #fff; border-top-left-radius: 8px; }
.mine { align-self: flex-end; background: #FFE1CF; border-top-right-radius: 8px; }
.b small { display: block; text-align: right; margin-top: 4px; font: 400 23px "Inter", sans-serif; color: var(--muted); }
.b small .tk2 { color: var(--od); font-weight: 700; }
.day { align-self: center; background: rgba(255,255,255,.8); border-radius: 20px; padding: 8px 22px; font: 700 24px "Inter", sans-serif; color: var(--muted); letter-spacing: 2px; }
.bar { position: absolute; left: 24px; right: 24px; bottom: 24px; height: 104px; background: #fff; border-radius: 52px; display: flex; align-items: center; padding: 0 34px; font: 400 34px "Inter", sans-serif; color: var(--ink); overflow: hidden; white-space: nowrap; }
.bar .ph { color: #A8A29B; position: absolute; left: 34px; }
.bar .k { opacity: 0; }
.pdf { display: flex; align-items: center; gap: 20px; }
.pdf .fi { width: 70px; height: 86px; border-radius: 12px; background: #E5484D; color: #fff; display: grid; place-items: center; font: 900 22px "Inter", sans-serif; flex-shrink: 0; }
.pdf b { display: block; font: 700 32px "Inter", sans-serif; }
.pdf span { font: 400 26px "Inter", sans-serif; color: var(--muted); }

/* Claude (tema escuro) */
.dark { background: #1C1B19; color: #F3F1EC; border: 2px solid #2E2C29; }
.dark .hd { height: 130px; display: flex; align-items: center; gap: 18px; padding: 0 40px; border-bottom: 2px solid #2E2C29; font: 800 36px "Inter", sans-serif; }
.dark .hd i { width: 22px; height: 22px; border-radius: 5px; background: var(--orange); transform: rotate(45deg); }
.dark .mine { background: #2E2C29; color: #F3F1EC; }
.ai { align-self: flex-start; max-width: 900px; font: 400 36px/1.42 "Inter", sans-serif; color: #D9D3CA; }
.ai b { color: var(--orange); }
.ai .a { opacity: 0; }
.ai .ln { opacity: 0; }
.chart { display: flex; align-items: flex-end; gap: 26px; height: 170px; margin-top: 18px; padding-left: 6px; }
.chart div { width: 90px; border-radius: 14px 14px 4px 4px; background: #3B3936; transform-origin: bottom; }
.chart .up { background: var(--orange); }
.dark .bar { background: #262522; color: #F3F1EC; }

/* Salto no tempo */
#jump .lbl { position: absolute; top: 470px; left: 0; right: 0; text-align: center; font: italic 400 72px "Instrument Serif", serif; color: rgba(243,241,236,.75); }
#jump .clk { position: absolute; top: 580px; left: 0; right: 0; height: 240px; overflow: hidden; text-align: center; color: #F3F1EC; font: 400 230px/240px "Inter", sans-serif; letter-spacing: -8px; }
#jump .clk div { position: absolute; left: 0; right: 0; }
#file { position: absolute; left: 140px; right: 140px; top: 900px; background: #fff; border-radius: 34px; padding: 28px 32px; box-shadow: 0 20px 60px rgba(0,0,0,.35); }
#file .ok { margin-left: auto; background: #1F9D55; color: #fff; border-radius: 30px; padding: 8px 20px; font: 800 24px "Inter", sans-serif; letter-spacing: 2px; }

/* Final */
#endbg { background: var(--ink); clip-path: circle(0px at 540px 900px); }
#end .c1 { position: absolute; top: 470px; left: 0; right: 0; text-align: center; font: italic 400 200px/1 "Instrument Serif", serif; color: #F3F1EC; }
#end .c2 { position: absolute; top: 720px; left: 0; right: 0; text-align: center; font: 800 44px "Inter", sans-serif; color: var(--orange); letter-spacing: 2px; }
#end .follow { position: absolute; left: 120px; right: 120px; top: 840px; background: #F3F1EC; color: var(--ink); border-radius: 40px; padding: 30px; text-align: center; font: 900 46px "Inter", sans-serif; }
#end .kw { position: absolute; left: 120px; right: 120px; top: 1010px; text-align: center; font: 400 36px/1.35 "Inter", sans-serif; color: rgba(243,241,236,.8); }
#end .kw b { color: var(--orange); font-weight: 900; }
"""


def page():
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="bg" class="clip full" data-start="0" data-duration="{DUR}" data-track-index="0"><div id="ground" class="full"></div></div>
  <div id="seriesclip" class="clip" data-start="0" data-duration="26.4" data-track-index="1"><div class="series"><span>DIÁRIO DE UMA ESTAGIÁRIA COM IA · <b>EP. 1</b></span></div></div>

  <div id="lock" class="clip" data-start="0" data-duration="3.5" data-track-index="2">
    <div class="clock" id="lclock">23:47</div><div class="date">terça-feira, 27 de outubro</div>
    <div class="notif" id="n1"><div class="ic">C</div><div class="tx"><div class="top">Chefe<i>agora</i></div><p>Bia, preciso do relatório de vendas do trimestre até amanhã às 8h.</p></div></div>
    <div class="notif" id="n2"><div class="ic">C</div><div class="tx"><div class="top">Chefe<i>agora</i></div><p>Com gráfico e análise.</p></div></div>
    <div class="thought" id="th1"><span>eu nunca fiz um relatório <em>na vida.</em></span></div>
  </div>

  <div id="chefe1" class="clip" data-start="3.3" data-duration="4.7" data-track-index="3">
    <div class="panel light" id="p1">
      <div class="hd"><div class="av">C</div><div><div class="nm">Chefe</div><div class="st"><span>online</span></div></div></div>
      <div class="msgs">
        <div class="b them">Bia, preciso do relatório de vendas do trimestre até amanhã às 8h.<small>23:47</small></div>
        <div class="b them">Com gráfico e análise.<small>23:47</small></div>
        <div class="b mine" id="r1">{html.escape(REPLY)}<small>23:49 <span class="tk2">✓✓</span></small></div>
      </div>
      <div class="bar" id="bar1"><span class="ph" id="ph1">Mensagem</span>{ch(REPLY)}</div>
    </div>
    <div class="thought" id="th2"><span>…<em>como?</em></span></div>
  </div>

  <div id="claude" class="clip" data-start="7.6" data-duration="9.4" data-track-index="4">
    <div class="panel dark" id="p2">
      <div class="hd"><i></i>Claude</div>
      <div class="msgs">
        <div class="b mine" id="q1">{html.escape(ASK1)}</div>
        <div class="ai" id="a1">{wd(AI1)}</div>
        <div class="b mine" id="q2">{html.escape(ASK2)}</div>
        <div class="ai" id="a2">{"".join(f'<div class="ln">{l}</div>' for l in AI2)}<div class="chart" id="chart"><div style="height:70px"></div><div style="height:85px"></div><div class="up" style="height:160px"></div></div></div>
      </div>
      <div class="bar" id="bar2"><span class="ph" id="ph2">Responder…</span>{ch(ASK1[:44] + "…")}</div>
    </div>
  </div>

  <div id="jump" class="clip" data-start="16.9" data-duration="2.5" data-track-index="5">
    <div class="lbl">38 minutos depois</div>
    <div class="clk"><div id="ck1">23:52</div><div id="ck2">00:31</div></div>
    <div id="file"><div class="pdf"><div class="fi">PDF</div><div><b>relatorio_vendas_set.pdf</b><span>4 páginas · 1 gráfico</span></div><div class="ok">PRONTO</div></div></div>
  </div>

  <div id="chefe2" class="clip" data-start="19.3" data-duration="7.4" data-track-index="6">
    <div class="panel light" id="p3">
      <div class="hd"><div class="av">C</div><div><div class="nm">Chefe</div><div class="st"><span class="on" id="st-on">online</span><span class="typing" id="st-ty">digitando…</span></div></div></div>
      <div class="msgs">
        <div class="b mine">{html.escape(REPLY)}<small>23:49 ✓✓</small></div>
        <div class="day">HOJE · 08:00</div>
        <div class="b mine" id="pdfb"><div class="pdf"><div class="fi">PDF</div><div><b>relatorio_vendas_set.pdf</b><span>4 páginas</span></div></div><small>08:00 <span id="tk1">✓</span><span class="tk2" id="tk2">✓✓ visto</span></small></div>
        <div class="b them" id="m1">Bia.<small>08:03</small></div>
        <div class="b them" id="m2">Vem na minha sala. Agora.<small>08:03</small></div>
      </div>
      <div class="bar"><span class="ph">Mensagem</span></div>
    </div>
  </div>

  <div id="end" class="clip" data-start="26.3" data-duration="{round(DUR - 26.3, 2)}" data-track-index="7">
    <div id="endbg" class="full"></div>
    <div class="c1" id="e1">Continua…</div>
    <div class="c2" id="e2">EP. 2 AMANHÃ, 19H</div>
    <div class="follow" id="e3">Segue @pattiners.ai pra não perder</div>
    <div class="kw" id="e4">Comenta <b>RELATÓRIO</b> que eu te mando<br>o prompt que a Bia usou</div>
  </div>

  <audio id="mix" class="clip" src="assets/audio/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const out = "expo.out";

// 1. Tela bloqueada: a primeira notificação já está lá no quadro 0
tl.fromTo("#n1", {{ y: -20 }}, {{ y: 0, duration: 0.6, ease: out }}, 0);
tl.fromTo("#n2", {{ y: -60, opacity: 0, scale: 0.96 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.45, ease: out }}, 1.3);
tl.fromTo("#th1", {{ y: 30, opacity: 0, filter: "blur(8px)" }}, {{ y: 0, opacity: 1, filter: "blur(0px)", duration: 0.35, ease: out }}, 2.0);
tl.to(["#lclock", "#n1", "#n2", "#th1", "#lock .date"], {{ y: -80, opacity: 0, duration: 0.3, ease: "power3.in", stagger: 0.02 }}, 3.15);

// 2. Responde o chefe
tl.fromTo("#p1", {{ y: 260, opacity: 0, scale: 0.94 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.5, ease: out }}, 3.3);
tl.set("#r1", {{ opacity: 0 }}, 0);
tl.to("#ph1", {{ opacity: 0, duration: 0.05 }}, 3.85);
tl.to("#bar1 .k", {{ opacity: 1, duration: 0.01, stagger: 0.034 }}, 3.9);
tl.to("#bar1 .k", {{ opacity: 0, duration: 0.05 }}, 5.0);
tl.fromTo("#r1", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)" }}, 5.05);
tl.fromTo("#th2", {{ y: 30, opacity: 0, filter: "blur(8px)" }}, {{ y: 0, opacity: 1, filter: "blur(0px)", duration: 0.35, ease: out }}, 5.9);
tl.to(["#p1", "#th2"], {{ x: -1100, rotationY: -20, duration: 0.45, ease: "power3.in" }}, 7.45);

// 3. Pede ajuda ao Claude
tl.fromTo("#p2", {{ x: 1100, rotationY: 20 }}, {{ x: 0, rotationY: 0, duration: 0.5, ease: out }}, 7.6);
tl.set(["#q1", "#q2"], {{ opacity: 0 }}, 0);
tl.to("#ph2", {{ opacity: 0, duration: 0.05 }}, 8.1);
tl.to("#bar2 .k", {{ opacity: 1, duration: 0.01, stagger: 0.03 }}, 8.15);
tl.to("#bar2 .k", {{ opacity: 0, duration: 0.05 }}, 9.6);
tl.fromTo("#q1", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.4)" }}, 9.65);
tl.to("#a1 .a", {{ opacity: 1, duration: 0.08, stagger: 0.075 }}, 10.1);
tl.fromTo("#q2", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.4)" }}, 12.4);
tl.to("#p2 .msgs", {{ y: -330, duration: 0.6, ease: "power2.inOut" }}, 12.9);
tl.to("#a2 .ln", {{ opacity: 1, duration: 0.2, stagger: 0.42 }}, 13.3);
tl.fromTo("#chart div", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.5, ease: out, stagger: 0.12 }}, 15.5);
tl.to("#p2", {{ scale: 0.9, opacity: 0, filter: "blur(12px)", duration: 0.3, ease: "power3.in" }}, 16.65);

// 4. Madrugada
tl.fromTo("#jump .lbl", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.25 }}, 16.95);
tl.fromTo("#ck1", {{ y: 0 }}, {{ y: -240, duration: 0.35, ease: "power3.inOut" }}, 17.5);
tl.fromTo("#ck2", {{ y: 240 }}, {{ y: 0, duration: 0.35, ease: "power3.inOut" }}, 17.5);
tl.fromTo("#file", {{ y: 80, opacity: 0, scale: 0.9 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.5)" }}, 18.1);
tl.to(["#jump .lbl", "#jump .clk", "#file"], {{ y: -60, opacity: 0, duration: 0.25, ease: "power3.in" }}, 19.1);

// 5. Oito da manhã
tl.fromTo("#p3", {{ y: 260, opacity: 0, scale: 0.94 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.5, ease: out }}, 19.3);
tl.set(["#pdfb", "#m1", "#m2", "#tk2"], {{ opacity: 0 }}, 0);
tl.fromTo("#pdfb", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)" }}, 19.7);
tl.to("#tk1", {{ opacity: 0, duration: 0.05 }}, 20.7);
tl.to("#tk2", {{ opacity: 1, duration: 0.1 }}, 20.7);
[[21.1, 22.3], [23.0, 24.1]].forEach(([a, b]) => {{
  tl.to("#st-on", {{ opacity: 0, duration: 0.05 }}, a); tl.to("#st-ty", {{ opacity: 1, duration: 0.05 }}, a);
  tl.to("#st-ty", {{ opacity: 0, duration: 0.05 }}, b); tl.to("#st-on", {{ opacity: 1, duration: 0.05 }}, b);
}});
tl.fromTo("#m1", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)" }}, 24.2);
tl.fromTo("#m2", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)" }}, 25.2);
tl.fromTo("#p3", {{ scale: 1 }}, {{ scale: 1.06, duration: 0.25, ease: "power2.out" }}, 25.2);

// 6. Continua
tl.to("#endbg", {{ clipPath: "circle(1500px at 540px 900px)", duration: 0.5, ease: "power2.inOut" }}, 26.3);
tl.fromTo("#e1", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.35 }}, 26.75);
tl.fromTo("#e2", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: out }}, 27.3);
tl.fromTo("#e3", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, 27.8);
tl.fromTo("#e4", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 28.5);

window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""


SFX_AT = [("notification", 0.05, 0.3), ("notification", 1.3, 0.3), ("typing", 3.9, 0.22), ("pop", 5.05, 0.3), ("whoosh-short", 7.45, 0.3),
          ("typing", 8.15, 0.22), ("pop", 9.65, 0.3), ("pop", 12.4, 0.3), ("pop", 15.5, 0.25), ("whoosh", 16.65, 0.3),
          ("click", 17.5, 0.4), ("sparkle", 18.1, 0.22), ("whoosh-short", 19.25, 0.3), ("pop", 19.7, 0.3), ("ping", 20.7, 0.2),
          ("key-press", 21.2, 0.15), ("key-press", 23.1, 0.15), ("pop", 24.2, 0.35), ("impact-bass-1", 25.2, 0.5), ("whoosh", 26.25, 0.3)]


def mix(bed):
    A = OUT / "assets" / "audio"
    ins, ch_, fx = [], [], []
    for n, (name, at, vol) in enumerate(SFX_AT):
        ins += ["-i", str(SFX / f"{name}.mp3")]
        ch_.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={int(at*1000)}:all=1[s{n}]")
        fx.append(f"[s{n}]")
    ins += ["-i", str(bed)]
    b = len(SFX_AT)
    # Trilha corta seco no "Vem na minha sala" e volta no "Continua"
    g = ";".join(ch_ + [
        f"{''.join(fx)}amix=inputs={len(fx)}:normalize=0,apad=whole_dur={DUR}[fx]",
        f"[{b}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,aloop=loop=-1:size=2e9,atrim=0:{DUR},"
        f"volume='if(between(t,25.15,26.3),0.05,0.6)':eval=frame,afade=t=out:st={DUR-1.5}:d=1.5[bm]",
        f"[bm][fx]amix=inputs=2:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.5:LRA=9[out]",
    ])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", g, "-map", "[out]", "-ar", "48000", str(A / "mix.wav")], check=True)


if __name__ == "__main__":
    import sys
    (OUT / "index.html").write_text(page())
    if len(sys.argv) > 1:
        mix(sys.argv[1])
    print("ok")
