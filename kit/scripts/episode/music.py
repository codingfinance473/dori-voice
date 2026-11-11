"""music.py — 말 박자를 따라가는 배경음 시안(2026-11-11). mix.py 가 BED=P|L|M 일 때 music.make(style, globals()) 로 부른다.

원칙(잘되는 정보 쇼츠 배경음에서 가져온 것)
  · 100 BPM(대화 속도와 같은 걸음) · 강한 주선율 없이 리듬 + 화음 바닥 — 말을 가리지 않는다.
  · 대사 시작이 8분음표 격자에 놓이도록 build_voice.py(BPM=100)가 쉼을 조금씩 맞췄다 → 말과 박이 함께 걷는다.
  · 멜로디는 '대답'만 한다: 말이 쉬는 틈에만 짧은 꾸밈(도리 줄 뒤 = 높고 반짝, 모리 줄 뒤 = 낮고 능청).
  · 모리가 말할 땐 음악을 끄지 않고 옷만 바꾼다(높은 반짝이를 빼고 낮은 '살금살금' 베이스) — 같은 박이 계속 간다.
  · 장면이 바뀌면 올라가는 꾸밈 한 번, 숫자가 나오면 작은 화음 한 번, '검산 끝'에서 으뜸화음으로 닫고 '쏙'에 마지막 한 음.
  · 악기는 실제 악기 녹음 샘플(MusyngKite 사운드폰트 음 하나하나) — 합성음의 '촌스러움'을 피한다.
"""
import os
import numpy as np
from scipy.io import wavfile

SFDIR = os.environ.get("SFDIR", "/home/claude/sf")
_cache = {}
NN = "C Db D Eb E F Gb G Ab A Bb B".split()


def smp(inst, m):
    k = (inst, m)
    if k not in _cache:
        nm = f"{NN[m % 12]}{m // 12 - 1}"
        sr, x = wavfile.read(f"{SFDIR}/{inst}/{nm}.wav")
        x = x.astype(np.float32) / 32768
        i = np.where(np.abs(x) > .01 * np.abs(x).max())[0]
        x = x[max(0, i[0] - 40):] if len(i) else x
        _cache[k] = x / (np.sqrt(np.mean(x[:4410] ** 2)) + 1e-6) * .2
    return _cache[k]


def make(style, G):
    SR, N, DUR, T, put = G["SR"], G["N"], G["DUR"], G["T"], G["put"]
    bed, rng = G["bed"], np.random.default_rng(7)
    TL = G["json"].loads(G["re"].search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), G["re"].S).group(1))
    lines = TL["lines"]
    BPM = TL.get("BPM") or 100
    BEAT = 60 / BPM; E8 = BEAT / 2; BAR = 4 * BEAT
    END = DUR - 1.05

    def speaking(t, pad=.05):
        for l in lines:
            if l["t"] - pad <= t < l["t"] + l["d"] + pad: return l["who"]
        return None

    def who_near(t):          # 지금(또는 바로 앞) 말하는 쪽
        w = None
        for l in lines:
            if l["t"] - .2 <= t: w = l["who"]
        return w or "D"

    QW = list(G.get("quiet", [])) + [(T["L09"] - .25, T["L09"] + 1.3)] if "L09" in T else list(G.get("quiet", []))
    def note(inst, m, at, g, L=1.2, pan=0.0, vel=1.0):
        if at < 0 or at >= END + 1: return
        if any(a <= at < b for a, b in QW): g *= .35          # 핵심 첫마디(quiet 구간): 새 음은 아주 작게
        x = smp(inst, m)[: int(L * SR)].copy()
        r = min(len(x), int(.09 * SR)); x[-r:] *= np.linspace(1, 0, r)
        put(bed, x, at, g * vel, pan)

    def noise(L, dec): n = int(L * SR); return rng.standard_normal(n) * np.exp(-np.arange(n) / SR / dec)
    hp, bp, lp = G["hp"], G["bp"], G["lp"]

    def shaker(at, g): put(bed, hp(noise(.07, .018), 6500), at, g, .3)
    def snap(at, g):
        x = bp(noise(.05, .008), 1500, 4500); x[:882] += .4 * hp(noise(.02, .004), 6000); put(bed, x, at, g, -.15)
    def kick(at, g):
        n = int(.22 * SR); x = np.arange(n) / SR
        put(bed, np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-x * 35)) / SR) * np.exp(-x * 14), at, g)
    def rim(at, g): put(bed, bp(noise(.04, .006), 1800, 3800) + .5 * np.sin(2 * np.pi * 820 * np.arange(int(.04 * SR)) / SR) * np.exp(-np.arange(int(.04 * SR)) / SR / .01), at, g, .1)
    def hat(at, g): put(bed, hp(noise(.04, .01), 8000), at, g, .25)

    # 화음 진행 — 마디마다
    if style == "L":   # 로파이: Fmaj7 Em7 Dm7 Cmaj7
        CH = [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (48, 52, 55, 59)]; BS = [41, 40, 38, 36]
        SCALE = [60, 62, 64, 67, 69, 72, 74, 76]
    else:              # C Am F G
        CH = [(60, 64, 67), (57, 60, 64), (53, 57, 60, 65), (55, 59, 62, 67)]; BS = [36, 33, 41, 43]
        SCALE = [60, 62, 64, 67, 69, 72, 74, 76, 79]
    INST = {"P": dict(ch="pizzicato_strings", bass="acoustic_bass", hi="glockenspiel", lo="bassoon"),
            "L": dict(ch="electric_piano_1", bass="electric_bass_finger", hi="vibraphone", lo="electric_piano_1"),
            "M": dict(ch="marimba", bass="acoustic_bass", hi="kalimba", lo="marimba")}[style]
    swing = .045 if style == "L" else 0.0

    # 마디별 화음 계획 — 기본 4마디 반복, '검산 끝'부터는 끝맺음(I → IV·V → I)으로 갈아탄다(1판: 끝이 IV에 걸린 채 끊겨 어색했음)
    SB = int(round(T["stamp"] / BAR)) if "stamp" in T else 10 ** 6
    def ci_at(bar, half=0):
        if bar < SB: return bar % 4
        r = bar - SB
        return 0 if r == 0 else (2 if half == 0 else 3) if r == 1 else 0
    def chord_at(t): b_ = int(t // BAR); return CH[ci_at(b_, int((t - b_ * BAR) >= BAR / 2))]
    S5, S8 = T.get("s5", 10 ** 6), T.get("s8", 10 ** 6)
    LASTBAR = SB + 2

    # ---------- 바닥: 리듬 + 화음(0초부터 끝까지 끊지 않는다) ----------
    k, b = 0, 0.0
    while b < END - .05:
        for s in range(8):
            ci = ci_at(k, int(s >= 4)); ch = CH[ci]
            t = b + s * E8 + (swing if s % 2 else 0)
            if t >= END - .05: break
            sp = speaking(t)
            mori = who_near(t) == "M"
            calm = S5 - .1 <= t < S8 - .3          # 긴 설명 구간: 한 겹 덜어 숨 쉬게
            if style == "P" and k >= LASTBAR:      # 마지막 마디: 으뜸화음 한 번 길게 + 베이스, 나머지는 비운다
                if s == 0:
                    for j, m in enumerate(CH[0][:3]): note(INST["ch"], m, t + j * .01, .06, 1.6, pan=.2 - .1 * j)
                    note(INST["bass"], 48, t, .16, 1.4)
                continue
            if style == "P":
                if s % 2 == 1:   # 뒷박 피치카토 화음(통통) — 긴 설명 구간도 박은 그대로(빼면 말 쉼과 겹쳐 침묵처럼 들림, 2026-11-11), 크기만 0.85배
                    for j, m in enumerate(ch[:3]): note(INST["ch"], m, t + j * .006, .05 * (.8 if sp else 1) * (.85 if calm else 1), .5, pan=.2 - .1 * j)
                if s in (0, 4): note(INST["bass"], BS[ci] + 12 + (0 if s == 0 else 7 if ci != 2 else -5), t, .16 * (.85 if calm and s == 4 else 1), .55)
                if s == 7 and k % 2 and k < SB - 1: note(INST["bass"], BS[ci_at(k + 1) ] + 12 - 1, t, .1, .25)   # 다음 마디로 걸어가는 반음
                shaker(t, .012 * (.8 if calm else 1)); shaker(t + E8 / 2, .007 * (.6 if calm else 1))
                if calm and s == 0: note("celesta", ch[-1] + 12, t, .022, 1.2, pan=.35)   # 숨 쉬는 구간: 마디 첫 박에 맑은 한 음
                if s in (2, 6): snap(t, .045)
                if mori and s in (1, 5): note("pizzicato_strings", BS[ci] + 24, t, .07, .3, pan=.35)   # 모리: 낮은 살금살금
            elif style == "L":
                if s == 0: [note(INST["ch"], m, t + j * .012, .045, BAR * .9, pan=-.1 + .07 * j) for j, m in enumerate(ch)]
                if s == 3: [note(INST["ch"], m + 12 * (0 if mori else 0), t, .028, .35, pan=.1) for m in ch[1:]]
                if s in (0, 5): note(INST["bass"], BS[ci] + 12, t, .17, .5 if s == 0 else .3)
                if s in (0, 5): kick(t, .16)
                if s in (2, 6): rim(t, .05)
                hat(t, .010 if s % 2 else .016)
                if mori and s == 6: note(INST["ch"], ch[0] - 12, t, .05, .3)
            else:  # M
                arp = [ch[0], ch[1], ch[2], ch[1] + 12 if len(ch) > 3 else ch[0] + 12, ch[2], ch[1], ch[0] + 12, ch[1]]
                mm = arp[s] - (12 if mori else 0)          # 모리: 같은 무늬를 한 옥타브 아래로
                note(INST["ch"], mm, t, (.035 if sp else .05) * (1.15 if s % 2 == 0 else .8), .45, pan=.25 if s % 2 else -.15)
                if s in (0, 3, 4): note(INST["bass"], BS[ci] + 12, t, .15, .45)
                if s in (2, 6): snap(t, .04)
                if s in (0, 4): kick(t, .09)
                shaker(t, .008)
        if k % 4 == 0 and style != "L" and k < SB: note(INST["hi"], 84 if style == "P" else 79, b, .03, 1.5, pan=.4)
        b += BAR; k += 1
    if style == "L":   # 바이닐 잡음 한 겹
        cr = (rng.random(N) < .0009) * rng.standard_normal(N) * .5
        cr = hp(cr, 2000) + lp(rng.standard_normal(N), 1200) * .006
        bed[:, 0] += cr * .25; bed[:, 1] += cr * .25



    # ---------- 대답(말 틈에만) ----------
    for i, l in enumerate(lines[:-1]):
        a = l["t"] + l["d"] + .04; z = lines[i + 1]["t"] - .06
        room = z - a
        if room < .18: continue
        ch = chord_at(a); top = sorted(set([m + 12 for m in ch] + [m + 24 for m in ch[:2]]))
        if l["who"] == "M":    # 모리 줄 뒤: 낮은 능청 두 음
            inst = INST["lo"]; ms = [ch[0] - 12, ch[0] - 5] if style == "P" else [ch[0] - 12, ch[2] - 12]
            ms = [m - 12 for m in ms] if style == "P" else ms
            ms = [m + 12 * max(0, -((m - 40) // 12)) for m in ms]      # 바순 아주 낮은 음(F1 등)은 한 옥타브 올림
            for j, m in enumerate(ms[: 1 if room < .3 else 2]): note(inst, m, a + j * .15, .07 if style == "P" else .06, .28, pan=.3)
        else:                  # 도리 줄 뒤: 높고 반짝 1~3음(올라가며)
            n = 1 if room < .3 else 2 if room < .45 else 3
            ms = top[-n - 1:-1] if n > 1 else [top[-1]]
            for j, m in enumerate(ms): note(INST["hi"], m, a + j * .1, .05, .6, pan=-.3 + .25 * j)

    # ---------- 장면이 바뀔 때: 올라가는 꾸밈 ----------
    for s_ in ("s2", "s3", "s4", "s5", "s8"):
        if s_ not in T: continue
        t0 = T[s_]; ch = chord_at(t0 + .3)
        for j, m in enumerate([ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]):
            note(INST["hi"], m, t0 - .32 + j * .075, .028, .5, pan=-.3 + .2 * j)

    # ---------- 숫자·핵심 단어: 작은 화음 한 번(16분음표 격자에) ----------
    for w in ("wUse", "wNext", "wRefuse", "wOne", "w55", "wSubmit"):
        if w not in T: continue
        t = round(T[w] / (E8 / 2)) * (E8 / 2); ch = chord_at(t)
        for j, m in enumerate(ch[:3]): note(INST["ch"] if style != "M" else "celesta", m + 12, t + j * .008, .03, .5, pan=.15)

    # ---------- 끝: 검산 끝 → 으뜸화음, 쏙 → 마지막 한 음 ----------
    ts = T.get("stamp")
    if ts is not None:
        root = CH[0] if style != "L" else (48, 52, 55, 59)
        tb = SB * BAR if abs(SB * BAR - ts) < .5 else ts
        for j, m in enumerate(root): note(INST["ch"], m + 12, tb + j * .03, .05, 1.2, pan=-.2 + .1 * j)
    tp = T.get("pouch")
    lastL = max(lines, key=lambda l: l["t"])
    te = lastL["t"] + lastL["d"] - .05   # 마지막 말 끝: 으뜸화음 한 번 더 — 끝까지 울려 침묵으로 끝나지 않게(2026-11-11)
    for j, m_ in enumerate(CH[0][:3]): note(INST["ch"], m_ + 12, te + j * .012, .05, 1.2, pan=.15 - .1 * j)
    note(INST["bass"], 48, te, .12, 1.0)
    if tp is not None:
        note(INST["hi"], 84, tp + .35, .05, 1.6); note(INST["hi"], 88, tp + .45, .04, 1.6, pan=.3); note(INST["hi"], 91, tp + .55, .04, 1.6, pan=-.2)
    f = int(.35 * SR); bed[-f:] *= np.linspace(1, 0, f)[:, None]
