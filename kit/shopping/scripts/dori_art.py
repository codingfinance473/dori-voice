#!/usr/bin/env python3
"""dori_art.py — 도리 2판 그림(캐릭터 시트·스티커·썸네일용 투명 PNG·SVG)을 만든다.

영상 속 도리(assets/dori.js)와 같은 모양·색이다. 한쪽을 고치면 다른 쪽도 같이 고친다.

  python3 dori_art.py list                               자세 이름 보기
  python3 dori_art.py sheet <폴더>                        캐릭터 시트 PNG + 자세별 투명 PNG(1200px)·SVG
  python3 dori_art.py pose <번호|이름> <파일.png|.svg> [--width 1200]   한 자세만

figure(i) → SVG 문자열(viewBox -70 -70 540 560, 캐릭터 기본 좌표 400×430, 발 바닥 y≈404).
모든 선은 같은 굵기·같은 색이라 어떤 크기로 키워도 또렷하다. 글자(구독·Z·?)는 Jua 글꼴 윤곽선으로 넣는다(fontTools).
재생 버튼은 특정 서비스 로고가 아닌 일반 원형 아이콘이다.
"""
import math, shutil, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SKILL = Path(__file__).resolve().parent.parent
FONT_DIR = SKILL / "assets" / "fonts" if (SKILL / "assets" / "fonts" / "Jua-Regular.ttf").exists() else Path.home() / ".cache" / "receipt-shorts" / "fonts"
FONT = str(FONT_DIR / "Jua-Regular.ttf")
# ---- 색 ----
OUT = "#4A3A33"; SW = 6.5
FUR_T, FUR, FUR_B = "#C2BBB6", "#AEA6A1", "#9D958F"
STRIPE = "#8B817B"
WHITE, WHITE_S = "#FFFDFB", "#F1ECE8"
EAR_IN = "#F7A8AE"; BLUSH = "#FAA3AB"; NOSE = "#EF8794"
MOUTH = "#E5657A"; TONGUE = "#F99DAB"; FEET = "#F8C4C7"
BAG, BAG_D, STRAP, BTN = "#80D0BA", "#63BCA5", "#5DB6A0", "#FFF4D4"
EYE = "#271B17"; SHADOW = "#E6DFDA"
CORAL, YELLOW, PINK, BLUE = "#FF6B5E", "#FFCF4A", "#FF8FA6", "#6E9CE8"
VB = (-70, -70, 540, 560)

BODY = ("M200,86 C282,86 338,134 346,200 C350,236 346,262 338,288 "
        "C352,330 342,398 262,402 L138,402 C58,398 48,330 62,288 "
        "C54,262 50,236 54,200 C62,134 118,86 200,86 Z")

_font = None


def text_path(txt, size, x, y, anchor="middle"):
    """Jua 글꼴 윤곽을 path 로(어디서 열어도 같은 글자)."""
    global _font
    _font = _font or TTFont(FONT)
    gs, cmap, upm = _font.getGlyphSet(), _font.getBestCmap(), _font["head"].unitsPerEm
    k = size / upm
    names = [cmap[ord(c)] for c in txt]
    width = sum(gs[n].width for n in names) * k
    x0 = x - (width / 2 if anchor == "middle" else 0)
    d, cx = [], x0
    for n in names:
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        d.append(pen.getCommands()); cx += gs[n].width * k
    return " ".join(d), width


def defs(p):
    return f"""<defs>
  <linearGradient id="{p}fur" x1="0" y1="86" x2="0" y2="402" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{FUR_T}"/><stop offset=".55" stop-color="{FUR}"/><stop offset="1" stop-color="{FUR_B}"/></linearGradient>
  <radialGradient id="{p}wh" cx="200" cy="300" r="170" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{WHITE}"/><stop offset=".78" stop-color="{WHITE}"/><stop offset="1" stop-color="{WHITE_S}"/></radialGradient>
  <clipPath id="{p}body"><path d="{BODY}"/></clipPath>
</defs>"""


# ---- 부품 ----
def ears(sad=False):
    s = ""
    for cx, sx in ((122, 1), (278, -1)):
        rot = (-14 * sx) if sad else 0
        s += (f'<g transform="rotate({rot},{cx},{150})"><circle cx="{cx}" cy="118" r="38" fill="{FUR_T}" stroke="{OUT}" stroke-width="{SW}"/>'
              f'<circle cx="{cx + 5 * sx}" cy="124" r="23" fill="{EAR_IN}"/></g>')
    return s


def body(p):
    return (f'<path d="{BODY}" fill="url(#{p}fur)"/>'
            f'<g clip-path="url(#{p}body)"><ellipse cx="200" cy="260" rx="124" ry="52" fill="url(#{p}wh)"/>'
            f'<ellipse cx="200" cy="340" rx="104" ry="82" fill="url(#{p}wh)"/></g>'
            f'<g stroke="{STRIPE}" stroke-linecap="round" fill="none" opacity=".85">'
            f'<path d="M198,96 C192,118 192,138 196,160" stroke-width="7.5"/><path d="M220,100 C216,113 216,125 219,137" stroke-width="5.5"/></g>'
            f'<ellipse cx="150" cy="124" rx="34" ry="14" fill="#fff" opacity=".16" transform="rotate(-22,150,124)"/>'
            f'<path d="{BODY}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')


CHEEKS = ((84, 262, 58), (316, 262, 58))


def body_stuffed(p):
    """볼주머니: 몸과 부푼 두 볼을 한 덩어리 윤곽으로(겹친 안쪽 선은 지운다)."""
    circ = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in CHEEKS)
    return (f'<g stroke="{OUT}" stroke-width="{SW * 2}" stroke-linejoin="round" fill="{OUT}"><path d="{BODY}"/>{circ}</g>'
            f'<path d="{BODY}" fill="url(#{p}fur)"/>' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{WHITE}"/>' for x, y, r in CHEEKS)
            + f'<clipPath id="{p}stb"><path d="{BODY}"/>{circ}</clipPath>'
            f'<g clip-path="url(#{p}stb)"><ellipse cx="200" cy="262" rx="176" ry="62" fill="{WHITE}"/>'
            f'<ellipse cx="200" cy="340" rx="104" ry="82" fill="url(#{p}wh)"/></g>'
            f'<g stroke="{STRIPE}" stroke-linecap="round" fill="none" opacity=".85">'
            f'<path d="M198,96 C192,118 192,138 196,160" stroke-width="7.5"/><path d="M220,100 C216,113 216,125 219,137" stroke-width="5.5"/></g>')


def eye(cx, cy, kind, side):
    o = f'stroke="{OUT}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    if kind in ("open", "big"):
        k = 1.12 if kind == "big" else 1.0
        return (f'<g transform="translate({cx},{cy}) scale({k})"><ellipse rx="17" ry="19" fill="{EYE}"/>'
                f'<circle cx="-5.5" cy="-6.5" r="6.8" fill="#fff"/><circle cx="6" cy="6.5" r="3" fill="#fff"/></g>')
    if kind == "happy":      # ∩ 웃는 눈
        return f'<path d="M{cx - 15},{cy + 5} Q{cx},{cy - 13} {cx + 15},{cy + 5}" {o}/>'
    if kind == "sleep":      # ‿ 감은 눈 + 속눈썹
        return (f'<path d="M{cx - 16},{cy - 1} Q{cx},{cy + 12} {cx + 16},{cy - 1}" {o}/>')
    if kind == "squeeze":    # > <
        d = 1 if side == "L" else -1
        return f'<path d="M{cx - 13 * d},{cy - 12} L{cx + 11 * d},{cy} L{cx - 13 * d},{cy + 12}" {o}/>'
    if kind == "focus":      # 반쯤 감은 눈
        return (f'<g transform="translate({cx},{cy + 3})"><clipPath id="fc{side}{cx}"><rect x="-20" y="-4" width="40" height="30"/></clipPath>'
                f'<g clip-path="url(#fc{side}{cx})"><ellipse rx="15.5" ry="16" fill="{EYE}"/><circle cx="-5" cy="1" r="5" fill="#fff"/></g>'
                f'<path d="M-18,-4 L18,-4" stroke="{OUT}" stroke-width="6" stroke-linecap="round"/></g>')
    raise ValueError(kind)


def mouth(kind):
    o = f'stroke="{OUT}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"'
    lip = f'<path d="M184,247 Q192,255 200,248 Q208,255 216,247" fill="none" {o}/>'
    if kind == "w":
        return f'<path d="M200,242 L200,248" fill="none" {o}/>' + lip
    if kind == "open":
        return (f'<path d="M185,248 Q193,254 200,249 Q207,254 215,248 Q214,276 200,278 Q186,276 185,248 Z" fill="{MOUTH}" {o}/>'
                f'<ellipse cx="200" cy="270" rx="8.5" ry="5.2" fill="{TONGUE}"/><path d="M200,242 L200,249" fill="none" {o}/>')
    if kind == "o":
        return (f'<path d="M200,242 L200,248" fill="none" {o}/>'
                f'<ellipse cx="200" cy="263" rx="9.5" ry="12.5" fill="{MOUTH}" {o}/><ellipse cx="200" cy="269" rx="5.5" ry="4" fill="{TONGUE}"/>')
    if kind == "cat":
        return f'<path d="M189,248 Q194.5,255 200,248 Q205.5,255 211,248" fill="none" {o}/>'
    if kind == "flat":
        return f'<path d="M200,242 L200,248" fill="none" {o}/><path d="M190,256 L210,256" fill="none" {o}/>'
    if kind == "sad":
        return f'<path d="M200,242 L200,248" fill="none" {o}/><path d="M187,262 Q200,248 213,262" fill="none" {o}/>'
    if kind == "full":   # 볼주머니 — 오므린 입
        return f'<path d="M200,242 L200,247" fill="none" {o}/><path d="M193,252 Q200,258 207,252" fill="none" {o}/>'
    raise ValueError(kind)


def face(expr):
    e = {"neutral": ("open", "open", "w"), "smile": ("open", "open", "open"), "happy": ("happy", "happy", "open"),
         "happyc": ("happy", "happy", "cat"), "squeeze": ("squeeze", "squeeze", "open"), "wink": ("open", "happy", "open"),
         "surprise": ("big", "big", "o"), "small_o": ("open", "open", "o"), "sleep": ("sleep", "sleep", "cat"),
         "focus": ("focus", "focus", "flat"), "sad": ("open", "open", "sad"), "stuff": ("happy", "happy", "full")}[expr]
    s = ""
    bx = 36 if expr == "stuff" else 0
    s += (f'<ellipse cx="{134 - bx}" cy="254" rx="{24 + bx / 3:.0f}" ry="15" fill="{BLUSH}" opacity=".9"/>'
          f'<ellipse cx="{266 + bx}" cy="254" rx="{24 + bx / 3:.0f}" ry="15" fill="{BLUSH}" opacity=".9"/>')
    w = f'stroke="{STRIPE}" stroke-width="2.6" stroke-linecap="round"'
    s += (f'<path d="M{104 - bx},242 L{142 - bx},247 M{102 - bx},256 L{140 - bx},256" {w}/>'
          f'<path d="M{296 + bx},242 L{258 + bx},247 M{298 + bx},256 L{260 + bx},256" {w}/>')
    s += eye(148, 214, e[0], "L") + eye(252, 214, e[1], "R")
    if expr in ("focus", "sad"):
        t = .6 if expr == "focus" else -1   # focus: 안쪽이 조금 내려감(집중) / sad: 안쪽이 올라감
        s += (f'<g stroke="{OUT}" stroke-width="4.8" stroke-linecap="round" fill="none">'
              f'<path d="M134,{184 - 5 * t:.1f} Q149,{180:.1f} 164,{184 + 5 * t:.1f}"/><path d="M266,{184 - 5 * t:.1f} Q251,{180:.1f} 236,{184 + 5 * t:.1f}"/></g>')
    s += (f'<path d="M191,233 Q200,228 209,233 Q208,240 200,243 Q192,240 191,233 Z" fill="{NOSE}" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>')
    s += mouth(e[2])
    return s


def bag():
    return (f'<path d="M84,304 Q190,318 290,346" stroke="{OUT}" stroke-width="13" stroke-linecap="round" fill="none"/>'
            f'<path d="M84,304 Q190,318 290,346" stroke="{STRAP}" stroke-width="7.5" stroke-linecap="round" fill="none"/>'
            f'<rect x="266" y="334" width="70" height="52" rx="13" fill="{BAG}" stroke="{OUT}" stroke-width="5"/>'
            f'<path d="M266,348 Q266,334 279,334 L323,334 Q336,334 336,348 L336,355 Q301,368 266,355 Z" fill="{BAG_D}" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/>'
            f'<circle cx="301" cy="361" r="5" fill="{BTN}" stroke="{OUT}" stroke-width="2.5"/>')


def arm(p, name, sx, sy, ang, length=58, width=46):
    """어깨(sx,sy)에서 ang 도(0=아래, +는 시계 방향)로 뻗은 짧은 콩 모양 팔, 끝은 흰 발."""
    r = width / 2; L = length
    d = f"M{-r},0 L{-r},{L - r} A{r},{r} 0 0 0 {r},{L - r} L{r},0 A{r},{r} 0 0 0 {-r},0 Z"
    cid = f"{p}a{name}"
    return (f'<g transform="translate({sx},{sy}) rotate({ang})">'
            f'<clipPath id="{cid}"><path d="{d}"/></clipPath><path d="{d}" fill="{FUR}"/>'
            f'<g clip-path="url(#{cid})"><rect x="{-r - 4}" y="{L - r - 4}" width="{width + 8}" height="{r + 12}" fill="{WHITE}"/></g>'
            f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/></g>')


def paw(x, y, rot=0):
    """물건을 잡은 앞발(흰 장갑 모양 + 발가락 두 줄)."""
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale(.88)">'
            f'<path d="M-25,12 L-25,0 A25,25 0 0 1 25,0 L25,12 Q25,22 15,22 L-15,22 Q-25,22 -25,12 Z" fill="{WHITE}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M-7,-14 L-7,-4 M7,-14 L7,-4" stroke="{STRIPE}" stroke-width="3.2" stroke-linecap="round"/></g>')


def paws_on(x, y):
    return paw(x, y, 0)


def feet():
    return (f'<ellipse cx="158" cy="404" rx="28" ry="13.5" fill="{FEET}" stroke="{OUT}" stroke-width="5"/>'
            f'<ellipse cx="242" cy="404" rx="28" ry="13.5" fill="{FEET}" stroke="{OUT}" stroke-width="5"/>')


def shadow():
    return f'<ellipse cx="200" cy="414" rx="132" ry="14" fill="{SHADOW}"/>'


# ---- 소품·효과 ----
def sparkle(x, y, r, c=YELLOW):
    return (f'<path d="M{x},{y - r} Q{x + r * .18},{y - r * .18} {x + r},{y} Q{x + r * .18},{y + r * .18} {x},{y + r} '
            f'Q{x - r * .18},{y + r * .18} {x - r},{y} Q{x - r * .18},{y - r * .18} {x},{y - r} Z" fill="{c}"/>')


def burst(x, y, ang, n=3, c=YELLOW, length=26, gap=30, width=10, r0=30):
    """(x,y) 둘레에서 바깥으로 뻗는 짧은 강조선 n개."""
    out = ""
    for i in range(n):
        a = math.radians(ang + (i - (n - 1) / 2) * gap)
        x1, y1 = x + math.cos(a) * r0, y + math.sin(a) * r0
        x2, y2 = x + math.cos(a) * (r0 + length), y + math.sin(a) * (r0 + length)
        out += f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="{c}" stroke-width="{width}" stroke-linecap="round"/>'
    return out


def heart(x, y, r, c=PINK):
    return (f'<path d="M{x},{y + r * .9} C{x - r * 1.5},{y - r * .1} {x - r * .9},{y - r * 1.25} {x},{y - r * .45} '
            f'C{x + r * .9},{y - r * 1.25} {x + r * 1.5},{y - r * .1} {x},{y + r * .9} Z" fill="{c}"/>')


def play_button(x, y, r):
    """일반 재생 버튼(원형) — 특정 서비스 로고 모양을 쓰지 않는다."""
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{CORAL}" stroke="{OUT}" stroke-width="{SW}"/>'
            f'<path d="M{x - r * .28},{y - r * .38} L{x + r * .42},{y} L{x - r * .28},{y + r * .38} Z" fill="#fff" stroke="#fff" stroke-width="{r * .12:.1f}" stroke-linejoin="round"/>'
            f'<path d="M{x - r * .62},{y - r * .5} A{r * .78},{r * .78} 0 0 1 {x - r * .1},{y - r * .76}" stroke="#fff" stroke-width="{r * .1:.1f}" stroke-linecap="round" fill="none" opacity=".55"/>')


def bell(x, y, s):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-16,10 Q-14,-14 0,-16 Q14,-14 16,10 L20,14 L-20,14 Z" fill="#fff"/>'
            f'<circle cx="0" cy="19" r="5" fill="#fff"/><circle cx="0" cy="-18" r="3.5" fill="#fff"/></g>')


def sub_sign():
    d, w = text_path("구독", 64, 180, 322)
    return (f'<rect x="62" y="300" width="276" height="100" rx="24" fill="{CORAL}" stroke="{OUT}" stroke-width="{SW}"/>'
            f'<path d="M80,312 L320,312" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".35"/>'
            f'<g transform="translate(0,40)"><path d="{d}" fill="#fff"/></g>' + bell(180 + w / 2 + 34, 346, 1.25))


def boba(x, y):
    return (f'<g transform="translate({x},{y})">'
            f'<path d="M8,-92 L28,-128" stroke="{OUT}" stroke-width="14" stroke-linecap="round"/><path d="M8,-92 L28,-128" stroke="{PINK}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M-40,-86 L40,-86 L32,6 Q30,18 18,18 L-18,18 Q-30,18 -32,6 Z" fill="#F3E7D7" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M-37,-56 L37,-56 L32,6 Q30,18 18,18 L-18,18 Q-30,18 -32,6 Z" fill="#DDB585"/>'
            + "".join(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#4A332B"/>' for cx, cy in ((-18, -2), (0, 4), (18, -2), (-9, -16), (10, -18), (-22, -26), (22, -30), (0, -34)))
            + f'<path d="M-40,-86 L40,-86 L32,6 Q30,18 18,18 L-18,18 Q-30,18 -32,6 Z" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<rect x="-46" y="-98" width="92" height="16" rx="8" fill="#fff" stroke="{OUT}" stroke-width="5"/></g>')


def laptop():
    return (f'<rect x="88" y="296" width="224" height="106" rx="14" fill="#DCD7D3" stroke="{OUT}" stroke-width="{SW}"/>'
            f'<rect x="100" y="306" width="200" height="8" rx="4" fill="#fff" opacity=".6"/>'
            + play_button(200, 352, 26)
            + f'<path d="M56,402 L344,402 L358,420 L42,420 Z" fill="#C9C3BE" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')


def pompom(x, y, r=42):
    pts = [(x + math.cos(math.radians(i * 30)) * r * .6, y + math.sin(math.radians(i * 30)) * r * .6) for i in range(12)]
    circ = "".join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{r * .42:.1f}"/>' for a, b in pts) + f'<circle cx="{x}" cy="{y}" r="{r * .7:.1f}"/>'
    s = f'<g fill="{OUT}" stroke="{OUT}" stroke-width="10">{circ}</g><g fill="{YELLOW}">{circ}</g>'
    for i in range(5):
        a = math.radians(i * 72 + 20)
        s += (f'<path d="M{x + math.cos(a) * r * .25:.1f},{y + math.sin(a) * r * .25:.1f} Q{x + math.cos(a + .4) * r * .55:.1f},{y + math.sin(a + .4) * r * .55:.1f} '
              f'{x + math.cos(a) * r * .8:.1f},{y + math.sin(a) * r * .8:.1f}" stroke="#EDB12C" stroke-width="4" stroke-linecap="round" fill="none"/>')
    return s


def confetti(seed=3):
    import random
    rnd = random.Random(seed)
    cols = [CORAL, YELLOW, "#7FD0BA", BLUE, PINK, "#B79BF2"]
    s = ""
    for _ in range(18):
        x, y = rnd.uniform(-40, 440), rnd.uniform(-40, 140)
        if 110 < x < 290 and y > 40:
            continue
        s += f'<rect x="{x:.0f}" y="{y:.0f}" width="16" height="9" rx="2" fill="{rnd.choice(cols)}" transform="rotate({rnd.uniform(0, 180):.0f},{x + 8:.0f},{y + 4:.0f})"/>'
    return s


def receipt():
    zz = " ".join(f"L{150 + i * 12.5},{372 + (6 if i % 2 else 0)}" for i in range(9))
    return (f'<path d="M150,262 L250,262 L250,372 {zz} Z" fill="#fff" stroke="{OUT}" stroke-width="5" stroke-linejoin="round" transform="rotate(-6,200,320)"/>'
            f'<g transform="rotate(-6,200,320)" stroke="#BDB3AA" stroke-width="5" stroke-linecap="round">'
            f'<path d="M166,286 L234,286"/><path d="M166,304 L222,304"/><path d="M166,322 L234,322"/><path d="M166,344 L210,344" stroke="{CORAL}"/></g>')


def excl(x, y):
    return (f'<g transform="translate({x},{y}) rotate(-10)"><rect x="-9" y="-34" width="18" height="44" rx="9" fill="#FF5A5A"/><circle cx="0" cy="24" r="9" fill="#FF5A5A"/></g>'
            f'<g transform="translate({x + 34},{y - 4}) rotate(-4)"><rect x="-9" y="-34" width="18" height="44" rx="9" fill="#FF5A5A"/><circle cx="0" cy="24" r="9" fill="#FF5A5A"/></g>')


def motion(x, y, ang, c="#9C938E"):
    return burst(x, y, ang, 3, c, 30, 24, 8)


def sweat(x, y):
    return f'<path d="M{x},{y - 18} Q{x + 14},{y} {x},{y + 10} Q{x - 14},{y} {x},{y - 18} Z" fill="#9FD6F5" stroke="{OUT}" stroke-width="3.5"/>'


def note(x, y):
    return (f'<g fill="{OUT}"><ellipse cx="{x}" cy="{y}" rx="11" ry="8.5" transform="rotate(-20,{x},{y})"/>'
            f'<rect x="{x + 7}" y="{y - 40}" width="5" height="40"/><path d="M{x + 12},{y - 40} Q{x + 30},{y - 30} {x + 26},{y - 16} Q{x + 22},{y - 26} {x + 12},{y - 26} Z"/></g>')


def question(x, y):
    d, _ = text_path("?", 64, x, y)
    return f'<path d="{d}" fill="{BLUE}"/>'


def zzz(x, y):
    s = ""
    for i, (dx, dy, sz) in enumerate(((0, 0, 40), (34, -34, 32), (62, -62, 24))):
        dd, _ = text_path("Z", sz, x + dx, y + dy)
        s += f'<path d="{dd}" fill="{BLUE}"/>'
    return s


# ---- 자세 ----
L_SH, R_SH = (72, 292), (328, 292)


def standing(p, expr, la, ra, bag_on=True, sad_ears=False, before_arms="", front="", cheeks=False, arms_behind=False, paws=()):
    """la·ra: 팔 각도(None=안 그림). before_arms: 팔과 발 사이에 그릴 물건, paws: 물건 위 앞발 [(x,y,회전)]."""
    s = shadow() + ears(sad_ears)
    s += body_stuffed(p) if cheeks else body(p)
    s += face(expr)
    if ra is not None and abs(ra) < 60:      # 내린 오른팔은 가방 뒤
        s += arm(p, "R", *R_SH, ra)
    if bag_on:
        s += bag()
    if ra is not None and abs(ra) >= 60:
        s += arm(p, "R", *R_SH, ra)
    if la is not None:
        s += arm(p, "L", *L_SH, la)
    s += before_arms + "".join(paw(*pw) for pw in paws)
    s += feet() + front
    return s


def sleeping(p):
    blanket = ("M150,300 C210,262 300,262 356,286 C392,304 398,370 384,402 L136,402 C128,360 132,322 150,300 Z")
    checks = ""
    for i in range(-2, 9):
        checks += f'<rect x="{110 + i * 36}" y="250" width="18" height="170" fill="#FFFFFF" opacity=".55"/>'
        checks += f'<rect x="100" y="{262 + i * 36}" width="320" height="18" fill="#FFFFFF" opacity=".55"/>'
    head = ("M168,124 C236,118 292,160 298,222 C304,282 252,318 186,318 C120,318 74,282 76,228 C78,170 112,128 168,124 Z")
    s = (f'<ellipse cx="236" cy="414" rx="176" ry="14" fill="{SHADOW}"/>'
         f'<path d="M40,300 C40,268 66,256 98,258 L300,262 C330,264 344,290 340,330 L336,384 C334,404 316,410 296,410 L74,408 C52,406 40,392 40,370 Z" fill="#FFFFFF" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
         f'<path d="M66,282 Q84,272 104,276" stroke="#E7E0DA" stroke-width="5" fill="none" stroke-linecap="round"/>')
    # 머리(베개 위, 살짝 기울임)
    s += f'<g transform="rotate(-10,190,230)">'
    s += (f'<circle cx="104" cy="148" r="34" fill="{FUR_T}" stroke="{OUT}" stroke-width="{SW}"/><circle cx="108" cy="153" r="20" fill="{EAR_IN}"/>')
    s += (f'<clipPath id="{p}head"><path d="{head}"/></clipPath><path d="{head}" fill="url(#{p}fur)"/>'
          f'<g clip-path="url(#{p}head)"><ellipse cx="186" cy="262" rx="120" ry="56" fill="url(#{p}wh)"/></g>'
          f'<path d="M186,130 C180,148 180,164 184,180" stroke="{STRIPE}" stroke-width="7" stroke-linecap="round" fill="none" opacity=".85"/>'
          f'<path d="{head}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    # 얼굴
    w = f'stroke="{STRIPE}" stroke-width="2.6" stroke-linecap="round"'
    s += (f'<ellipse cx="122" cy="258" rx="21" ry="13" fill="{BLUSH}" opacity=".9"/><ellipse cx="246" cy="258" rx="21" ry="13" fill="{BLUSH}" opacity=".9"/>'
          f'<path d="M92,250 L128,254 M90,264 L126,264" {w}/><path d="M280,250 L244,254 M282,264 L246,264" {w}/>'
          + eye(140, 226, "sleep", "L") + eye(230, 226, "sleep", "R")
          + f'<path d="M176,244 Q185,239 194,244 Q193,251 185,254 Q177,251 176,244 Z" fill="{NOSE}" stroke="{OUT}" stroke-width="3"/>'
          f'<path d="M185,253 L185,258 M174,259 Q179.5,266 185,259 Q190.5,266 196,259" fill="none" stroke="{OUT}" stroke-width="4.2" stroke-linecap="round"/>')
    # 수면 모자(머리 위를 덮고 끝이 오른쪽으로 늘어진 원뿔)
    s += (f'<path d="M100,176 C108,118 182,90 250,100 C300,108 338,128 362,160 C348,166 332,168 318,166 C304,160 292,158 282,160 C226,140 158,148 100,176 Z" '
          f'fill="{PINK}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
          f'<path d="M140,128 C176,108 220,104 254,110" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none" opacity=".45"/>'
          f'<path d="M100,176 C158,148 226,140 284,160" stroke="{OUT}" stroke-width="{SW + 16}" stroke-linecap="round" fill="none"/>'
          f'<path d="M100,176 C158,148 226,140 284,160" stroke="#fff" stroke-width="16" stroke-linecap="round" fill="none"/>'
          f'<circle cx="366" cy="170" r="19" fill="#fff" stroke="{OUT}" stroke-width="{SW}"/></g>')
    # 이불
    s += (f'<clipPath id="{p}bl"><path d="{blanket}"/></clipPath><path d="{blanket}" fill="#FFB3BF"/>'
          f'<g clip-path="url(#{p}bl)">{checks}</g><path d="{blanket}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')
    # 이불 위 손
    s += (f'<g transform="translate(178,300) rotate(-28)"><path d="M-20,-30 L-20,14 A20,20 0 0 0 20,14 L20,-30 Z" fill="{FUR}"/>'
          f'<clipPath id="{p}hp"><path d="M-20,-30 L-20,14 A20,20 0 0 0 20,14 L20,-30 Z"/></clipPath><g clip-path="url(#{p}hp)"><rect x="-24" y="6" width="48" height="40" fill="{WHITE}"/></g>'
          f'<path d="M-20,-30 L-20,14 A20,20 0 0 0 20,14 L20,-30" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linecap="round"/></g>')
    s += zzz(330, 70) + (f'<circle cx="312" cy="204" r="24" fill="#DDF1FF" stroke="#8CC4EC" stroke-width="4"/><circle cx="304" cy="196" r="6" fill="#fff"/>')
    return s


POSES = [
    # (파일 이름, 시트 이름, 설명, 그리는 함수)
    ("01_인사", "인사", "손 흔들기", lambda p: play_button(36, 44, 44) + burst(150, 70, -95, 3, YELLOW, 24, 26)
     + burst(40, 214, 200, 3, YELLOW, 24, 28) + standing(p, "smile", 140, None)),
    ("02_재생버튼", "재생 버튼 꼭", "윙크 · 안기", lambda p: sparkle(356, 92, 22) + sparkle(24, 206, 15)
     + standing(p, "wink", None, None, before_arms=play_button(200, 342, 58), paws=((146, 334, -90), (254, 334, 90)))),
    ("03_구독", "구독 부탁해", "팻말 들기", lambda p: burst(96, 150, -140, 3, PINK, 26, 26)
     + standing(p, "small_o", None, None, bag_on=False, front=sub_sign() + paw(124, 300) + paw(276, 300))),
    ("04_신남", "신남", "만세 · > <", lambda p: sparkle(20, 74, 24) + sparkle(382, 150, 20) + sparkle(352, 62, 13)
     + standing(p, "squeeze", 146, -146)),
    ("05_버블티", "버블티 한 모금", "행복 · 하트", lambda p: heart(352, 120, 26)
     + standing(p, "happyc", None, None, before_arms=boba(200, 376), paws=((160, 332, -90), (240, 332, 90)))),
    ("06_깜짝", "깜짝", "! !", lambda p: excl(46, 112) + motion(320, 150, -45) + motion(70, 320, 180)
     + standing(p, "surprise", -52, None)),
    ("07_노트북", "편집 중", "노트북 · 콧노래", lambda p: note(334, 104)
     + standing(p, "happy", None, None, bag_on=False, front=laptop() + paw(150, 298) + paw(250, 298))),
    ("08_응원", "응원", "폼폼 · 축하", lambda p: confetti()
     + standing(p, "squeeze", 146, -146, front=pompom(28, 232) + pompom(372, 232))),
    ("09_잠", "꿀잠", "수면 모자 · 이불", sleeping),
    ("10_기본", "기본", "영상 기본 자세", lambda p: standing(p, "neutral", -32, 32)),
    ("11_계산중", "계산 중", "영수증 들기", lambda p: standing(p, "focus", None, None, before_arms=receipt(), paws=((150, 306, -84), (250, 300, 84)))),
    ("12_볼주머니", "볼주머니", "현지가 싸면 빵빵", lambda p: sparkle(36, 120, 18) + sparkle(366, 120, 18)
     + standing(p, "stuff", -158, 158, cheeks=True)),
    ("13_가리키기", "가리키기", "저기 봐", lambda p: sparkle(372, 160, 14) + standing(p, "smile", -32, -132)),
    ("14_생각", "생각", "볼 괴기", lambda p: question(360, 120) + standing(p, "focus", -32, 122)),
    ("15_시무룩", "시무룩", "한국이 더 쌀 때", lambda p: sweat(356, 196) + standing(p, "sad", -18, 18, sad_ears=True)),
]


def figure(idx, w=None, h=None):
    name, title, desc, fn = POSES[idx]
    p = f"p{idx}"
    size = f' width="{w}" height="{h}"' if w else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(map(str, VB))}"{size}>'
            f'{defs(p)}<g>{fn(p)}</g></svg>')


FACES = [("기본", "neutral"), ("웃음", "smile"), ("행복", "happy"), ("신남", "squeeze"), ("윙크", "wink"),
         ("깜짝", "surprise"), ("집중", "focus"), ("시무룩", "sad"), ("볼주머니", "stuff"), ("잠", "sleep")]


def face_figure(i, w=None, h=None):
    """표정 차트용: 머리만 잘라 보여 준다."""
    name, expr = FACES[i]
    p = f"f{i}"
    size = f' width="{w}" height="{h}"' if w else ""
    inner = standing(p, expr, None, None, bag_on=False, cheeks=(expr == "stuff"), sad_ears=(expr == "sad"))
    vb = "16 60 368 262" if expr == "stuff" else "40 62 320 256"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{size}>{defs(p)}<g>{inner}</g></svg>'


# ---- 내보내기 ----
STICKERS = list(range(0, 9))           # 포즈 9
VIDEO = [9, 10, 11, 12, 13, 14]        # 영상에서 쓰는 동작 6
PALETTE = [("털 위", FUR_T), ("털", FUR), ("털 아래", FUR_B), ("이마 줄무늬", STRIPE), ("선", OUT), ("흰 털", WHITE),
           ("귀 안", EAR_IN), ("볼", BLUSH), ("코", NOSE), ("입 안", MOUTH), ("발", FEET), ("가방", BAG),
           ("가방 덮개", BAG_D), ("가방 끈", STRAP), ("포인트 코랄", CORAL), ("포인트 노랑", YELLOW)]


def find(key):
    for i, (name, title, *_ ) in enumerate(POSES):
        if key in (str(i + 1), f"{i + 1:02d}", name, title, name.split("_", 1)[-1]):
            return i
    sys.exit(f"자세를 찾지 못함: {key} — list 로 이름을 본다")


def export_pose(i, out, width=1200):
    from playwright.sync_api import sync_playwright
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    W, H = width, round(width * VB[3] / VB[2])
    svg = figure(i, W, H)
    if out.suffix.lower() == ".svg":
        out.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8"); return out
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
        pg.locator("svg").screenshot(path=str(out), omit_background=True); b.close()
    return out


def sheet(out_dir):
    from playwright.sync_api import sync_playwright
    out = Path(out_dir); shutil.rmtree(out / "png", ignore_errors=True); shutil.rmtree(out / "svg", ignore_errors=True)
    (out / "png").mkdir(parents=True); (out / "svg").mkdir()
    W, H = 1200, round(1200 * VB[3] / VB[2])
    fonts = FONT_DIR.as_uri()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, (name, *_ ) in enumerate(POSES):
            svg = figure(i, W, H)
            (out / "svg" / f"도리_{name}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
            pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
            pg.locator("svg").screenshot(path=str(out / "png" / f"도리_{name}.png"), omit_background=True)
        card = lambda i, cls="": (f'<div class="card {cls}"><div class="art">{figure(i, "100%", "100%")}</div>'
                                  f'<div class="nm">{POSES[i][1]}</div><div class="ds">{POSES[i][2]}</div></div>')
        faces = "".join(f'<div class="face"><div class="fa">{face_figure(i, "100%", "100%")}</div><div class="fn">{n}</div></div>'
                        for i, (n, _) in enumerate(FACES))
        sw = "".join(f'<div class="sw"><i style="background:{c}"></i><b>{n}</b><span>{c}</span></div>' for n, c in PALETTE)
        html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Jua;src:url({fonts}/Jua-Regular.ttf)}}
@font-face{{font-family:Pre;font-weight:600;src:url({fonts}/Pretendard-SemiBold.woff2)}}
@font-face{{font-family:Pre;font-weight:800;src:url({fonts}/Pretendard-ExtraBold.woff2)}}
*{{box-sizing:border-box}}
body{{margin:0;background:#FFF7EF;font-family:Pre,sans-serif;color:#3E2F25}}
.wrap{{width:2400px;padding:130px 140px 150px}}
h1{{font-family:Jua;font-size:118px;margin:0;letter-spacing:-2px;line-height:1}}
.sub{{font-size:36px;font-weight:600;color:#8A776A;margin-top:30px;line-height:1.6}}
h2{{font-family:Jua;font-size:64px;margin:130px 0 0;letter-spacing:-1px}}
h2 small{{font-family:Pre;font-weight:600;font-size:30px;color:#9C8B7C;margin-left:22px;letter-spacing:0}}
.hero{{display:grid;grid-template-columns:960px 1fr;gap:90px;margin-top:90px;align-items:center}}
.hero .big{{background:#fff;border-radius:60px;height:960px;padding:40px;box-shadow:0 18px 44px rgba(120,80,40,.10)}}
.who .name{{font-family:Jua;font-size:150px;line-height:1;letter-spacing:-3px}}
.who .role{{font-size:38px;font-weight:800;color:#C4502F;margin-top:26px}}
.who ul{{list-style:none;padding:0;margin:56px 0 0}}
.who li{{font-size:38px;font-weight:600;line-height:1.5;margin:0 0 30px;padding-left:46px;position:relative;color:#4A3B30}}
.who li:before{{content:"";position:absolute;left:4px;top:20px;width:18px;height:18px;border-radius:50%;background:{BAG}}}
.faces{{display:grid;grid-template-columns:repeat(5,1fr);gap:44px 40px;margin-top:56px}}
.face{{background:#fff;border-radius:44px;padding:30px 24px 30px;box-shadow:0 12px 30px rgba(120,80,40,.08);text-align:center}}
.fa{{height:250px}} .fn{{font-family:Jua;font-size:42px;margin-top:16px}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:56px 50px;margin-top:56px}}
.card{{background:#fff;border-radius:52px;padding:40px 34px 44px;box-shadow:0 14px 36px rgba(120,80,40,.09);text-align:center}}
.card .art{{height:600px}}
.card.s .art{{height:430px}}
.nm{{font-family:Jua;font-size:52px;margin-top:20px}}
.ds{{font-size:30px;font-weight:600;color:#9C8B7C;margin-top:12px}}
.pal{{display:grid;grid-template-columns:repeat(8,1fr);gap:40px 32px;margin-top:56px}}
.sw{{display:flex;flex-direction:column;gap:12px}}
.sw i{{display:block;height:130px;border-radius:30px;box-shadow:inset 0 0 0 3px rgba(0,0,0,.06)}}
.sw b{{font-size:30px;font-weight:800}} .sw span{{font-size:27px;font-weight:600;color:#9C8B7C}}
.foot{{margin-top:110px;font-size:30px;font-weight:600;color:#A89786;line-height:1.8}}
</style></head><body><div class="wrap">
<h1>도리 캐릭터 시트</h1>
<div class="sub">「도리의 가격 검산」 진행자 · 2판 — 영상 속 도리와 같은 벡터 그림</div>
<div class="hero"><div class="big">{figure(0, "100%", "100%")}</div>
<div class="who"><div class="name">도리</div><div class="role">가격 검산 담당 햄스터</div><ul>
<li>통통한 회색 햄스터 — 머리와 몸이 한 덩어리</li>
<li>크고 촉촉한 눈, 분홍 볼, 이마 줄무늬 두 줄</li>
<li>민트색 크로스백을 늘 메고 다닌다</li>
<li>표식: 현지가 싸면 볼주머니가 빵빵</li>
<li>말투: 짧은 반말, 신나게 검산</li></ul></div></div>
<h2>표정<small>얼굴만 바꿔 끼우는 10가지</small></h2><div class="faces">{faces}</div>
<h2>포즈<small>쇼츠·커뮤니티·썸네일용</small></h2><div class="grid3">{"".join(card(i) for i in STICKERS)}</div>
<h2>영상에서 쓰는 동작<small>검산 장면의 기본 자세</small></h2><div class="grid3">{"".join(card(i, "s") for i in VIDEO)}</div>
<h2>색</h2><div class="pal">{sw}</div>
<div class="foot">모든 그림은 벡터(SVG)라 어떤 크기로 키워도 선이 또렷해요 · 재생 버튼은 특정 서비스 로고가 아닌 일반 원형 아이콘</div>
</div></body></html>"""
        tmp = out / "_sheet.html"; tmp.write_text(html, encoding="utf-8")
        sp = b.new_page(viewport={"width": 2400, "height": 1200})
        sp.goto(tmp.resolve().as_uri()); sp.evaluate("document.fonts.ready"); sp.wait_for_timeout(400)
        sp.screenshot(path=str(out / "도리_캐릭터_시트.png"), full_page=True)
        b.close(); tmp.unlink()
    print(f"캐릭터 시트: {out / '도리_캐릭터_시트.png'} · 자세 {len(POSES)}개(png/·svg/)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("list", "sheet", "pose"):
        sys.exit(__doc__)
    if a[0] == "list":
        for i, (name, title, desc, _) in enumerate(POSES):
            print(f"{i + 1:2d}  {name:12s} {title} — {desc}")
    elif a[0] == "sheet":
        sheet(a[1] if len(a) > 1 else "도리_그림")
    else:
        w = int(a[a.index("--width") + 1]) if "--width" in a else 1200
        print(export_pose(find(a[1]), a[2], w))
