"""Personagens da novelinha em SVG: a Bia (estagiária) e a Gema (a IA, nascida do losango da marca).

Cada função devolve um <svg> com a expressão pedida. Uso: python3 mascotes.py  (salva brand/mascote/*.svg)
"""
from pathlib import Path

INK, PAPER, ORANGE, OD = "#121211", "#F3F1EC", "#FF5F1F", "#D9480F"
SKIN, HAIR, HOOD = "#F2C4A0", "#2B1E17", "#FF5F1F"


def bia(expr="neutral", size=300):
    """Bia: coque no alto, óculos redondos e moletom laranja com crachá."""
    eyes = {
        "neutral": '<circle cx="122" cy="150" r="7" fill="#121211"/><circle cx="178" cy="150" r="7" fill="#121211"/>',
        "panic": '<circle cx="122" cy="150" r="13" fill="#fff" stroke="#121211" stroke-width="4"/><circle cx="122" cy="150" r="4" fill="#121211"/>'
                 '<circle cx="178" cy="150" r="13" fill="#fff" stroke="#121211" stroke-width="4"/><circle cx="178" cy="150" r="4" fill="#121211"/>',
        "happy": '<path d="M112 152 q10 -12 20 0" stroke="#121211" stroke-width="6" fill="none" stroke-linecap="round"/>'
                 '<path d="M168 152 q10 -12 20 0" stroke="#121211" stroke-width="6" fill="none" stroke-linecap="round"/>',
        "focus": '<path d="M112 148 h20" stroke="#121211" stroke-width="7" stroke-linecap="round"/><path d="M168 148 h20" stroke="#121211" stroke-width="7" stroke-linecap="round"/>',
        "shock": '<circle cx="122" cy="150" r="5" fill="#121211"/><circle cx="178" cy="150" r="5" fill="#121211"/>'
                 '<path d="M106 126 l28 6" stroke="#121211" stroke-width="5" stroke-linecap="round"/><path d="M194 126 l-28 6" stroke="#121211" stroke-width="5" stroke-linecap="round"/>',
        "fake": '<circle cx="122" cy="150" r="7" fill="#121211"/><circle cx="178" cy="150" r="7" fill="#121211"/>',
    }[expr]
    mouth = {
        "neutral": '<path d="M135 188 q15 10 30 0" stroke="#121211" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "panic": '<ellipse cx="150" cy="194" rx="14" ry="18" fill="#121211"/>',
        "happy": '<path d="M128 182 q22 26 44 0 z" fill="#121211"/>',
        "focus": '<path d="M140 190 h20" stroke="#121211" stroke-width="5" stroke-linecap="round"/>',
        "shock": '<path d="M134 196 q16 -10 32 0" stroke="#121211" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "fake": '<path d="M124 184 q26 18 52 0" stroke="#121211" stroke-width="6" fill="#fff" stroke-linecap="round"/>',
    }[expr]
    extra = ""
    if expr in ("panic", "fake"):
        extra += '<path d="M214 108 q10 18 0 26 q-10 -8 0 -26z" fill="#7CC4F2"/>'  # gota de suor
    if expr == "shock":
        extra += '<path d="M230 70 l8 -22 M246 84 l20 -12 M222 60 l-2 -22" stroke="#121211" stroke-width="5" stroke-linecap="round"/>'
    if expr == "happy":
        extra += '<circle cx="104" cy="178" r="11" fill="#F59A83" opacity=".7"/><circle cx="196" cy="178" r="11" fill="#F59A83" opacity=".7"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 330" width="{size}" height="{size*1.1:.0f}">
  <path d="M50 330 q0 -92 100 -92 q100 0 100 92z" fill="{HOOD}"/>
  <path d="M118 244 q32 22 64 0" stroke="{OD}" stroke-width="6" fill="none"/>
  <rect x="166" y="266" width="50" height="34" rx="6" fill="#fff"/><rect x="174" y="276" width="34" height="5" rx="2" fill="#C9C1B6"/><rect x="174" y="286" width="22" height="5" rx="2" fill="#C9C1B6"/>
  <rect x="136" y="212" width="28" height="32" fill="{SKIN}"/>
  <circle cx="150" cy="44" r="34" fill="{HAIR}"/>
  <ellipse cx="150" cy="150" rx="82" ry="88" fill="{SKIN}"/>
  <path d="M68 146 q-4 -86 82 -88 q86 2 82 88 q-18 -50 -82 -52 q-64 2 -82 52z" fill="{HAIR}"/>
  <ellipse cx="70" cy="160" rx="10" ry="16" fill="{SKIN}"/><ellipse cx="230" cy="160" rx="10" ry="16" fill="{SKIN}"/>
  <circle cx="122" cy="150" r="24" fill="none" stroke="{INK}" stroke-width="5"/><circle cx="178" cy="150" r="24" fill="none" stroke="{INK}" stroke-width="5"/>
  <path d="M146 150 h8" stroke="{INK}" stroke-width="5"/>
  {eyes}{mouth}{extra}
</svg>'''


def gema(expr="happy", size=260):
    """Gema: o losango laranja da marca, com olhos grandes e um brilho."""
    eyes = {
        "happy": '<ellipse cx="108" cy="128" rx="16" ry="20" fill="#fff"/><ellipse cx="152" cy="128" rx="16" ry="20" fill="#fff"/>'
                 '<circle cx="111" cy="132" r="8" fill="#121211"/><circle cx="155" cy="132" r="8" fill="#121211"/>',
        "explain": '<ellipse cx="108" cy="128" rx="16" ry="20" fill="#fff"/><ellipse cx="152" cy="128" rx="16" ry="20" fill="#fff"/>'
                   '<circle cx="113" cy="126" r="8" fill="#121211"/><circle cx="157" cy="126" r="8" fill="#121211"/>'
                   '<path d="M138 98 l26 -8" stroke="#121211" stroke-width="5" stroke-linecap="round"/>',
        "wink": '<ellipse cx="108" cy="128" rx="16" ry="20" fill="#fff"/><circle cx="111" cy="132" r="8" fill="#121211"/>'
                '<path d="M138 130 q14 -12 28 0" stroke="#121211" stroke-width="6" fill="none" stroke-linecap="round"/>',
    }[expr]
    mouth = {
        "happy": '<path d="M114 160 q16 14 32 0" stroke="#121211" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "explain": '<ellipse cx="130" cy="164" rx="10" ry="8" fill="#121211"/>',
        "wink": '<path d="M112 158 q18 20 36 0 z" fill="#121211"/>',
    }[expr]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260" width="{size}" height="{size}">
  <ellipse cx="130" cy="246" rx="58" ry="9" fill="#121211" opacity=".14"/>
  <rect x="48" y="48" width="164" height="164" rx="44" transform="rotate(45 130 130)" fill="{ORANGE}"/>
  <path d="M130 28 L182 80" stroke="#FF8A57" stroke-width="10" stroke-linecap="round" opacity=".9"/>
  {eyes}{mouth}
  <circle cx="84" cy="150" r="9" fill="#FF9B73"/><circle cx="176" cy="150" r="9" fill="#FF9B73"/>
  <path d="M214 50 l6 -16 l6 16 l16 6 l-16 6 l-6 16 l-6 -16 l-16 -6z" fill="{ORANGE}"/>
</svg>'''


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[3] / "brand" / "mascote"
    out.mkdir(parents=True, exist_ok=True)
    for e in ("neutral", "panic", "fake", "focus", "happy", "shock"):
        (out / f"bia-{e}.svg").write_text(bia(e))
    for e in ("happy", "explain", "wink"):
        (out / f"gema-{e}.svg").write_text(gema(e))
    print("ok", out)
