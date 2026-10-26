"""Reels v3 da Pattiners: narração rápida com cada palavra aparecendo na hora em que é dita,
um objeto na tela para cada frase e um palco só, sem cortes.

Uso: python3 build.py formula [--voice pm_alex] [--speed 1.15]
  1. gera a voz de cada frase (Kokoro, local) em v3/<slug>/assets/audio/voice/
  2. mede onde a fala começa e termina e distribui as palavras nesse intervalo
  3. escreve v3/<slug>/index.html e mixa assets/audio/mix.wav (voz + trilha + efeitos)
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SFX = Path("/root/.claude/skills/media-use/audio/assets/sfx")
GAP = 0.18  # respiro entre frases


def run(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def duration(f):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)).stdout)


def speech_bounds(f):
    """Início e fim da fala, ignorando silêncio nas pontas."""
    err = subprocess.run(["ffmpeg", "-i", str(f), "-af", "silencedetect=n=-40dB:d=0.08", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    total = duration(f)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    a = ends[0] if starts and starts[0] < 0.02 and ends else 0.0
    b = starts[-1] if starts and (not ends or starts[-1] > ends[-1]) else total
    return a, b, total


def tokens(text):
    """'Mesma IA. *Outra* resposta.' -> [('Mesma', False), ('IA.', False), ('Outra', True), ...]"""
    return [(w.replace("*", ""), "*" in w) for w in text.split()]


def word_times(toks, a, b):
    """Distribui as palavras pelo tempo de fala, proporcional ao tamanho de cada uma."""
    weights = [len(re.sub(r"\W", "", w)) + 2 for w, _ in toks]
    total, acc, out = sum(weights), 0, []
    for w in weights:
        out.append(a + (b - a) * acc / total)
        acc += w
    return out


def say(text):
    """Texto que vai para a voz: sem marcações e com a palavra-chave pronunciável."""
    return text.replace("*", "")


CSS = (HERE / "style.css").read_text()


def words_html(bid, toks, cls=""):
    return " ".join(
        f'<span class="w{" hl" if hl else ""}{cls}" id="{bid}w{i}">{html.escape(w)}</span>' for i, (w, hl) in enumerate(toks)
    )


def build(slug, voice, speed):
    P = json.loads((HERE / "pautas.json").read_text())[slug]
    D = HERE / slug
    (D / "assets" / "audio" / "voice").mkdir(parents=True, exist_ok=True)
    for src in ("fonts",):
        subprocess.run(["cp", "-r", str(HERE.parent / "skills" / "assets" / src), str(D / "assets")], check=True)
    for f in ("hyperframes.json", "package.json"):
        subprocess.run(["cp", str(HERE.parent / "skills" / f), str(D / f)], check=True)
    (D / "meta.json").write_text(json.dumps({"id": f"{slug}-v3", "name": f"{slug}-v3"}))

    # 1 e 2: voz e tempos
    t, beats = 0.25, []
    for i, b in enumerate(P["beats"]):
        wav = D / "assets" / "audio" / "voice" / f"b{i}.wav"
        if not wav.exists() or "--fresh" in sys.argv:
            run("npx", "hyperframes@0.8.198", "tts", b.get("say", say(b["text"])), "-v", voice, "-l", "pt-br", "-s", str(speed), "-o", str(wav))
        a, e, total = speech_bounds(wav)
        toks = tokens(b["text"])
        times = [round(t + x, 3) for x in word_times(toks, a, e)]
        beats.append({**b, "i": i, "start": round(t, 3), "speech_end": round(t + e, 3), "toks": toks, "times": times, "wav": wav})
        t += total + GAP + b.get("hold", 0)
    dur = round(t + P.get("tail", 1.6), 2)

    # 3: página
    texts, tw = [], []
    for k, b in enumerate(beats):
        nxt = beats[k + 1]["start"] if k + 1 < len(beats) else dur
        bid = f"b{b['i']}"
        pre = f'<div class="pre">{html.escape(b["pre"])}</div>' if b.get("pre") else ""
        c0 = 0 if k == 0 else b["start"]
        texts.append(f'<div id="{bid}" class="clip line {b.get("size", "")}" data-start="{c0}" data-duration="{round(nxt - c0, 3)}" data-track-index="2">{pre}<div class="main">{words_html(bid, b["toks"])}</div></div>')
        if b.get("pre"):
            tw.append(f'tl.fromTo("#{bid} .pre", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {b["start"]});')
        for j, at in enumerate(b["times"]):
            if k == 0:
                tw.append(f'tl.fromTo("#{bid}w{j}", {{color: "#A39A8F"}}, {{color: "{'#D9480F' if b['toks'][j][1] else '#121211'}", duration: 0.12}}, {at});')
                continue
            tw.append(f'tl.fromTo("#{bid}w{j}", {{opacity: 0, y: 14, filter: "blur(8px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.14, ease: "power2.out"}}, {at});')
        if k + 1 < len(beats) and not beats[k + 1].get("keep_prev"):
            tw.append(f'tl.to("#{bid} .main, #{bid} .pre", {{opacity: 0, y: -26, filter: "blur(10px)", duration: 0.16, ease: "power2.in"}}, {round(nxt - 0.17, 3)});')
        if b.get("strike"):
            s0 = b["times"][b["strike"][0]]
            tw.append(f'tl.fromTo("#{bid} .strike", {{scaleX: 0}}, {{scaleX: 1, duration: 0.3, ease: "power2.inOut"}}, {round(b["speech_end"] + 0.05, 3)});')
    T = {b["id"]: b["start"] for b in beats if b.get("id")}
    T.update({f'{b["id"]}_end': b["speech_end"] for b in beats if b.get("id")})
    W = {}  # tempo de cada palavra marcada com "@nome" na pauta
    for b in beats:
        for name, idx in b.get("marks", {}).items():
            W[name] = b["times"][idx]
    def when(ref):
        if ref == "END":
            return dur
        name, _, off = ref.partition("+")
        name, _, neg = name.partition("~")
        base = W.get(name, T.get(name))
        return round(base + float(off or 0) - float(neg or 0), 3)
    sub = lambda txt: re.sub(r"\{\{D:([^:}]+):([^}]+)\}\}", lambda m: str(round(when(m.group(2)) - when(m.group(1)), 3)),
                             re.sub(r"\{\{T:([^}]+)\}\}", lambda m: str(when(m.group(1))), txt))
    props = sub((HERE / "props.html").read_text())
    props_js = sub((HERE / "props.js").read_text())
    for k, v in P["fill"].items():
        props = props.replace("{{" + k + "}}", v)
    page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="bg" class="clip full" data-start="0" data-duration="{dur}" data-track-index="0"><div id="paper" class="full"></div><div id="light"></div><div id="dots" class="full"></div><div class="handle">@pattiners.ai</div></div>
  {props}
  {''.join(texts)}
  <audio id="mix" class="clip" src="assets/audio/mix.wav" data-start="0" data-duration="{dur}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
const T = {json.dumps(T)};
const W = {json.dumps(W)};
const DUR = {dur};
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#light", {{ x: -60 }}, {{ x: 60, duration: DUR, ease: "sine.inOut" }}, 0);
{chr(10).join(tw)}
{props_js}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
    # A palavra riscada ganha a linha por cima
    for b in beats:
        if b.get("strike"):
            i0, i1 = b["strike"]
            ids = [f'id="b{b["i"]}w{j}"' for j in range(i0, i1 + 1)]
            first, last = ids[0], ids[-1]
            page = page.replace(f'<span class="w" {first}', f'<span class="strikewrap"><span class="strike"></span><span class="w" {first}', 1)
            m = re.search(rf'<span class="w[^"]*" {re.escape(last)}>[^<]*</span>', page)
            page = page[: m.end()] + "</span>" + page[m.end():]
    (D / "index.html").write_text(page)

    # Efeitos: tempos vêm de T (início de frase) ou W (palavra marcada), mais um deslocamento
    sfx = [(n, when(r)) for n, r in P["sfx"]]
    mix(D, beats, sfx, dur)
    (D / "timing.json").write_text(json.dumps({"dur": dur, "T": T, "W": W, "sfx": sfx}, indent=1))
    print("ok", slug, dur, "s")


SFX_VOL = {"typing": 0.22, "pop": 0.3, "click": 0.45, "error": 0.25, "sparkle": 0.25, "impact-bass-1": 0.4, "notification": 0.3, "whoosh": 0.3, "whoosh-short": 0.3, "key-press": 0.3, "ping": 0.25}


def mix(D, beats, sfx, dur):
    A = D / "assets" / "audio"
    ins, ch, vo, fx = [], [], [], []
    for b in beats:
        ins += ["-i", str(b["wav"])]
        n = len(ins) // 2 - 1
        ch.append(f"[{n}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={int(b['start']*1000)}:all=1[v{n}]")
        vo.append(f"[v{n}]")
    for name, at in sfx:
        ins += ["-i", str(SFX / f"{name}.mp3")]
        n = len(ins) // 2 - 1
        ch.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={SFX_VOL.get(name, 0.3)},adelay={int(at*1000)}:all=1[s{n}]")
        fx.append(f"[s{n}]")
    ins += ["-i", str(A / "bed.wav")]
    bed = len(ins) // 2 - 1
    g = ";".join(ch + [
        f"{''.join(vo)}amix=inputs={len(vo)}:normalize=0,apad=whole_dur={dur}[vo]",
        "[vo]asplit=2[vo1][key]",
        f"[{bed}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,aloop=loop=-1:size=2e9,atrim=0:{dur},volume=0.45,afade=t=in:d=0.2,afade=t=out:st={dur-1.4}:d=1.4[bm]",
        "[bm][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=300[duck]",
        f"{''.join(fx)}amix=inputs={len(fx)}:normalize=0[fx]",
        f"[vo1][duck][fx]amix=inputs=3:normalize=0,atrim=0:{dur},loudnorm=I=-14:TP=-1.5:LRA=9[out]",
    ])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", g, "-map", "[out]", "-ar", "48000", str(A / "mix.wav")], check=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    voice = args[args.index("--voice") + 1] if "--voice" in args else "pm_alex"
    speed = float(args[args.index("--speed") + 1]) if "--speed" in args else 1.15
    build(args[0], voice, speed)
