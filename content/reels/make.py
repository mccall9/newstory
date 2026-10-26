"""Gera um Reels de 14 s (HyperFrames) a partir de uma pauta curta.

Uso: python3 make.py reels.json   (cria reels/<slug>/ com index.html; depois
     `npx hyperframes@0.8.198 render -o renders/<slug>.mp4 <slug>` em cada pasta)

Cenas: gancho (0 a 2,8 s), lista de passos (2,8 a 10,4 s) e chamada para comentar (10,4 a 14 s).
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
BASE = HERE / "skills"  # projeto de referência: fontes e configuração

CSS = """
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-normal-400.woff2") format("woff2"); font-style: normal; font-weight: 400; }
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-italic-400.woff2") format("woff2"); font-style: italic; font-weight: 400; }
@font-face { font-family: "Bricolage Grotesque"; src: url("assets/fonts/BricolageGrotesque-normal-800.woff2") format("woff2"); font-weight: 800; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #121211; }
#root { position: relative; width: 100%; height: 100%; color: #f3f1ec; font-family: "Inter", sans-serif; overflow: hidden; }
#grid { position: absolute; inset: -200px; background-image: linear-gradient(rgba(243,241,236,.06) 2px, transparent 2px), linear-gradient(90deg, rgba(243,241,236,.06) 2px, transparent 2px); background-size: 120px 120px; }
#glow { position: absolute; width: 1400px; height: 1400px; left: -160px; top: -300px; border-radius: 50%; background: radial-gradient(circle, rgba(255,95,31,.32), transparent 62%); }
.logo { position: absolute; top: 220px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 14px; font: 800 52px/1 "Bricolage Grotesque", sans-serif; letter-spacing: -2px; }
.logo i { width: 20px; height: 20px; background: #ff5f1f; border-radius: 4px; transform: rotate(45deg); }
.scene { position: absolute; left: 90px; right: 90px; top: 420px; height: 960px; display: flex; flex-direction: column; justify-content: center; gap: 44px; }
.chip { align-self: flex-start; background: #ff5f1f; color: #fff; border-radius: 60px; padding: 18px 36px; font: 700 34px "Inter", sans-serif; letter-spacing: 6px; }
.big { font: 400 140px/0.95 "Instrument Serif", serif; letter-spacing: -3px; }
.big em, .row em { font-style: italic; color: #ff5f1f; }
.sub { font: 500 46px/1.3 "Inter", sans-serif; color: #a8a29b; }
.mid { font: 400 104px/1 "Instrument Serif", serif; letter-spacing: -2px; }
.list { display: flex; flex-direction: column; border-top: 3px solid rgba(243,241,236,.18); }
.row { display: flex; gap: 30px; align-items: baseline; padding: 24px 0; border-bottom: 3px solid rgba(243,241,236,.18); font: 400 62px/1.05 "Instrument Serif", serif; }
.row b { flex-shrink: 0; width: 70px; font: 700 34px "Inter", sans-serif; color: #ff5f1f; }
.gem { width: 200px; height: 200px; border-radius: 40px; background: #ff5f1f; align-self: center; }
.cta { align-self: stretch; background: #f3f1ec; color: #121211; border-radius: 40px; padding: 46px 50px; text-align: center; }
.cta small { display: block; font: 700 32px "Inter", sans-serif; letter-spacing: 8px; color: #d9480f; margin-bottom: 10px; }
.cta strong { display: block; font: 800 130px/1 "Bricolage Grotesque", sans-serif; letter-spacing: -5px; }
.cta span { display: block; margin-top: 14px; font: 500 40px "Inter", sans-serif; }
"""


def page(r):
    rows = "".join(f'<div class="row"><b>{i:02d}</b><span>{t}</span></div>' for i, t in enumerate(r["steps"], 1))
    n = len(r["steps"])
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="14" data-width="1080" data-height="1920">
  <div id="bg" class="clip" data-start="0" data-duration="14" data-track-index="0"><div id="grid"></div><div id="glow"></div><div class="logo"><i></i>pattiners</div></div>
  <div id="s1" class="clip scene" data-start="0" data-duration="2.8" data-track-index="1">
    <div id="s1-chip" class="chip">{r["chip"]}</div>
    <div id="s1-title" class="big">{r["hook"]}</div>
    <div id="s1-sub" class="sub">{r["sub"]}</div>
  </div>
  <div id="s2" class="clip scene" data-start="2.8" data-duration="7.6" data-track-index="1">
    <div id="s2-title" class="mid">{r["list_title"]}</div>
    <div class="list">{rows}</div>
  </div>
  <div id="s3" class="clip scene" data-start="10.4" data-duration="3.6" data-track-index="1">
    <div id="s3-gem" class="gem"></div>
    <div id="s3-cta" class="cta"><small>COMENTE</small><strong>{r["keyword"]}</strong><span>{r["promise"]}</span></div>
  </div>
</div>
<script>
  const tl = gsap.timeline({{ paused: true }});
  const e = "power3.out";
  tl.fromTo("#grid", {{ x: 0, y: 0 }}, {{ x: -120, y: -120, duration: 14, ease: "none" }}, 0);
  tl.fromTo("#glow", {{ scale: 0.9, opacity: 0.7 }}, {{ scale: 1.1, opacity: 1, duration: 14, ease: "sine.inOut" }}, 0);
  // Gancho já visível no quadro 0 (capa do Reels)
  tl.fromTo("#s1-title", {{ y: 30 }}, {{ y: 0, duration: 0.8, ease: e }}, 0);
  tl.fromTo("#s1-sub", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: e }}, 0.5);
  tl.to(["#s1-chip", "#s1-title", "#s1-sub"], {{ y: -60, opacity: 0, duration: 0.35, ease: "power2.in" }}, 2.4);
  tl.fromTo("#s2-title", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: e }}, 2.85);
  tl.fromTo("#s2 .row", {{ x: 120, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.45, ease: e, stagger: {round(4.6 / n, 2)} }}, 3.3);
  tl.to(["#s2-title", "#s2 .row"], {{ y: -50, opacity: 0, duration: 0.3, ease: "power2.in" }}, 10.05);
  tl.fromTo("#s3-gem", {{ scale: 0, rotation: -180 }}, {{ scale: 1, rotation: 45, duration: 0.7, ease: "back.out(1.8)" }}, 10.45);
  tl.fromTo("#s3-cta", {{ y: 120, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: e }}, 10.8);
  tl.fromTo("#s3-cta strong", {{ scale: 0.85 }}, {{ scale: 1, duration: 0.5, ease: "back.out(2)" }}, 11.0);
  window.__timelines["main"] = tl;
  tl.seek(0);
</script>
</body></html>
"""


if __name__ == "__main__":
    for r in json.loads(Path(sys.argv[1]).read_text()):
        out = HERE / r["slug"]
        out.mkdir(exist_ok=True)
        for f in ("hyperframes.json", "package.json"):
            shutil.copy(BASE / f, out / f)
        shutil.copytree(BASE / "assets", out / "assets", dirs_exist_ok=True)
        (out / "meta.json").write_text(json.dumps({"id": r["slug"], "name": r["slug"]}))
        (out / "index.html").write_text(page(r))
        print("ok", r["slug"])
