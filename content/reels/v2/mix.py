"""Mixa narração, trilha e efeitos de um Reels v2 em assets/audio/mix.wav.

Uso: python3 mix.py formula
Espera em v2/<slug>/assets/audio/: voice/l1.wav..., bed.wav. Os efeitos vêm da biblioteca do HyperFrames.
A trilha abaixa sozinha quando a voz entra (sidechain) e o resultado é normalizado em -14 LUFS.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SFX = Path("/root/.claude/skills/media-use/audio/assets/sfx")
SFX_VOL = {"typing": 0.25, "pop": 0.35, "click": 0.5, "error": 0.3, "sparkle": 0.3, "impact-bass-1": 0.45, "notification": 0.35}

slug = sys.argv[1]
p = json.loads((HERE / "pautas.json").read_text())[slug]
A = HERE / slug / "assets" / "audio"
D = p["duration"]

inputs, chains, voice, fx = [], [], [], []
for i, (lid, at) in enumerate(p["voice"].items()):
    inputs += ["-i", str(A / "voice" / f"{lid}.wav")]
    chains.append(f"[{len(inputs)//2 - 1}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={int(at*1000)}:all=1[v{i}]")
    voice.append(f"[v{i}]")
for j, (name, at) in enumerate(p["sfx"]):
    inputs += ["-i", str(SFX / f"{name}.mp3")]
    vol = SFX_VOL.get(name, 0.4)
    chains.append(f"[{len(inputs)//2 - 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={int(at*1000)}:all=1[s{j}]")
    fx.append(f"[s{j}]")
inputs += ["-i", str(A / "bed.wav")]
bed = len(inputs) // 2 - 1

graph = ";".join(chains + [
    f"{''.join(voice)}amix=inputs={len(voice)}:normalize=0,apad=whole_dur={D}[vo]",
    "[vo]asplit=2[vo1][vokey]",
    f"[{bed}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,aloop=loop=-1:size=2e9,atrim=0:{D},volume=0.5,afade=t=in:d=0.3,afade=t=out:st={D-1.5}:d=1.5[bm]",
    "[bm][vokey]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck]",
    f"{''.join(fx)}amix=inputs={len(fx)}:normalize=0[fx]",
    f"[vo1][duck][fx]amix=inputs=3:normalize=0,atrim=0:{D},loudnorm=I=-14:TP=-1.5:LRA=9[out]",
])
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[out]", "-ar", "48000", str(A / "mix.wav")], check=True)
print("ok", A / "mix.wav")
