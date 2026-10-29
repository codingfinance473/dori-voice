#!/usr/bin/env python3
"""music.py — 산뜻한 배경음 「도리 산책」(직접 작곡·합성한 원곡, 매 편 길이에 맞춰 새로 만든다).

  python3 music.py <초> <출력.wav> [--bpm 118] [--ring 2.0] [--seed 5]

- 사장조, 116~120 BPM 안팎. 우쿨렐레 스트럼(현 합성) + 통통 튀는 베이스 + 마림바 멜로디(후렴처럼 귀에 붙는 2마디 동기)
  + 글로켄슈필 반짝임 + 가벼운 킥·박수·셰이커. 로파이 잡음(지지직)은 넣지 않는다.
- 구성: 도입 1마디 → A(8마디, I–V–vi–IV) → B(8마디, IV–V–iii–vi 왕도 진행) → A'·B'(글로켄 겹침) … 길이에 맞춰 자르고,
  끝 두 마디는 IV–V, 마지막 I 화음이 마지막 대사 바로 뒤에 울리도록 템포를 108~128 사이에서 고른다(ring = 끝 화음이 울리는 시간).
- 멜로디·화성 모두 이 파일에서 새로 쓴 것이다(기존 곡을 옮기지 않는다). 진행(I–V–vi–IV 등)은 흔한 화성 진행이라 누구의 것도 아니다.
"""
import argparse
import numpy as np
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR = 44100
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def nm(s):
    """'F#5' → 78"""
    acc = 1 if "#" in s else (-1 if "b" in s[1:] else 0)
    return 12 * (int(s[-1]) + 1) + NAMES[s[0]] + acc


def mel(s):
    """'D5 0 1 | G5 1 1' → [(시작 8분, 길이 8분, 음)]"""
    out = []
    for tok in s.split("|"):
        p, a, b = tok.split()
        out.append((float(a), float(b), nm(p)))
    return out


# ── 화음: 우쿨렐레(G4 C4 E4 A4, 위 현이 높은 G) 잡는 모양 그대로 · 베이스 근음 ──
UKE = {"G": [67, 62, 67, 71], "D": [69, 62, 66, 69], "Em": [67, 64, 67, 71], "C": [67, 60, 64, 72],
       "Bm": [71, 62, 66, 71], "Am": [69, 60, 64, 69], "D7": [69, 62, 66, 72]}
ROOT = {"G": 43, "D": 38, "Em": 40, "C": 36, "Bm": 47, "Am": 45, "D7": 38}

# ── 멜로디(마림바). 강박에는 화음 구성음, 약박에 지나는 음 ──
A_CH = ["G", "D", "Em", "C", "G", "D", "C", "D"]
A_MEL = [
    "D5 0 1 | G5 1 1 | B5 2 2 | A5 4 1 | B5 5 1 | G5 6 2",
    "F#5 0 1 | A5 1 1 | D6 2 2 | E6 4 1 | D6 5 1 | A5 6 2",
    "G5 0 1 | B5 1 1 | E6 2 2 | F#6 4 1 | E6 5 1 | B5 6 2",
    "E6 0 2 | D6 2 1 | C6 3 1 | B5 4 1 | A5 5 1 | G5 6 1 | A5 7 1",
    "D5 0 1 | G5 1 1 | B5 2 2 | A5 4 1 | B5 5 1 | G5 6 2",
    "F#5 0 1 | A5 1 1 | D6 2 2 | E6 4 1 | D6 5 1 | A5 6 2",
    "E6 0 1 | D6 1 1 | C6 2 2 | E6 4 1 | D6 5 1 | C6 6 1 | B5 7 1",
    "A5 0 2 | F#5 2 1 | A5 3 1 | D6 4 3",
]
B_CH = ["C", "D", "Bm", "Em", "C", "D", "G", "G"]
B_MEL = [
    "G5 0 1 | C6 1 1 | E6 2 3 | D6 5 1 | C6 6 2",
    "A5 0 1 | D6 1 1 | F#6 2 3 | E6 5 1 | D6 6 2",
    "F#6 0 2 | E6 2 1 | D6 3 1 | B5 4 2 | D6 6 1 | E6 7 1",
    "E6 0 3 | B5 3 1 | G5 4 2",
    "E6 0 1 | G6 1 1 | E6 2 2 | C6 4 1 | E6 5 1 | G6 6 2",
    "F#6 0 1 | E6 1 1 | D6 2 2 | A5 4 1 | D6 5 1 | E6 6 2",
    "D6 0 1 | B5 1 1 | G5 2 1 | B5 3 1 | D6 4 4",
    "B5 0 2 | A5 2 1 | G5 3 1",
]
B_FILL = "D6 4 1 | G6 5 1 | B6 6 2"          # B 마지막 마디 빈자리에 글로켄 반짝
CAD_CH = ["C", "D"]
CAD_MEL = ["E6 0 1 | D6 1 1 | C6 2 2 | E6 4 1 | D6 5 1 | C6 6 1 | B5 7 1",
           "A5 0 1 | D6 1 1 | F#6 2 2 | E6 4 1 | D6 5 1 | C6 6 1 | A5 7 1"]
INTRO_GLOCK = "B5 6 1 | D6 7 1"
STRUM = [(0, "D", 1.0), (2, "D", 0.8), (3, "U", 0.55), (5, "U", 0.6), (6, "D", 0.8), (7, "U", 0.5)]   # 섬 스트럼
BASS = [(0, 1.6, 0), (3, 0.9, 7), (4, 1.6, 0), (6, 0.9, 12), (7, 0.9, 7)]                              # (위치, 길이, 근음에서)


# ── 악기 ──
def ks(f, dur, t60=1.4, bright=0.35, pick=0.2, rng=None):
    """카플러스-스트롱 현(전대역 통과 필터로 미세 조율 — 화음이 맞게)."""
    P = SR / f
    N = int(np.floor(P - 0.6)); d = P - 0.5 - N; C = (1 - d) / (1 + d)
    n = int(dur * SR)
    exc = rng.uniform(-1, 1, N + 2)
    a = np.exp(-2 * np.pi * (700 + 7000 * bright) / SR)
    exc = lfilter([1 - a], [1, -a], exc)
    M = max(1, int(pick * N)); exc[M:] = exc[M:] - exc[:-M]; exc -= exc.mean()
    x = np.zeros(max(n, len(exc))); x[:len(exc)] = exc
    g = 10 ** (-3 / (f * t60))
    den = np.zeros(N + 3); den[0] = 1; den[1] = C
    den[N] -= 0.5 * g * C; den[N + 1] -= 0.5 * g * (1 + C); den[N + 2] -= 0.5 * g
    y = lfilter([1.0, C], den, x)[:n]
    return y / (np.max(np.abs(y[: int(0.05 * SR)])) + 1e-9)


def marimba(f, dur, rng):
    n = int(dur * SR); t = np.arange(n) / SR
    k = (f / 440) ** 0.6
    y = np.zeros(n)
    for r, amp, tau in ((1.0, 1.0, 0.75), (3.93, 0.30, 0.16), (9.2, 0.07, 0.05)):
        if f * r < SR * 0.45:
            y += amp * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 0.3)) * np.exp(-t * k / tau)
    m = int(0.005 * SR); click = rng.standard_normal(m) * np.hanning(m) * 0.12
    y[:m] += lfilter([0.3], [1, -0.7], click)
    return y * np.minimum(1, t / 0.0015)


def glock(f, dur, rng):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for r, amp, tau in ((1.0, 1.0, 1.1), (2.756, 0.42, 0.40), (5.404, 0.18, 0.15), (8.933, 0.06, 0.07)):
        if f * r < SR * 0.45:
            y += amp * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 0.5)) * np.exp(-t / tau)
    return y * np.minimum(1, t / 0.001)


def kick():
    n = int(0.32 * SR); t = np.arange(n) / SR
    f = 50 + 95 * np.exp(-t * 30)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    return y * np.minimum(1, t / 0.002)


def clap(rng):
    n = int(0.3 * SR); t = np.arange(n) / SR
    nb = sosfilt(butter(2, [950, 2700], btype="band", fs=SR, output="sos"), rng.standard_normal(n))
    env = np.zeros(n)
    for d, a in ((0.0, 0.8), (0.008, 0.7), (0.017, 0.9)):
        env += a * np.exp(-np.maximum(0, t - d) / 0.005) * (t >= d)
    env += 0.5 * np.exp(-np.maximum(0, t - 0.022) / 0.07) * (t >= 0.022)
    return nb * env


def shaker(rng, acc):
    n = int(0.08 * SR); t = np.arange(n) / SR
    nb = sosfilt(butter(2, 5500, btype="high", fs=SR, output="sos"), rng.standard_normal(n))
    env = np.minimum(1, t / (0.012 if acc else 0.006)) * np.exp(-t / (0.03 if acc else 0.018))
    return nb * env


def add(buf, y, s):
    s = int(s)
    if s >= len(buf) or s + len(y) <= 0:
        return
    a = max(0, -s); e = min(len(buf), s + len(y))
    buf[max(0, s):e] += y[a:a + e - max(0, s)]


def plan(dur, ring, bpm=None):
    """마디 순서와 템포. 마지막 I 화음은 dur-ring 초에 친다."""
    t_end = dur - ring
    if bpm:
        n = max(6, int(round(t_end * bpm / 240)))
    else:
        cands = [n for n in range(6, 200) if 108 <= 240 * n / t_end <= 128]
        n = min(cands, key=lambda n: abs(240 * n / t_end - 118)) if cands else max(6, int(round(t_end * 118 / 240)))
    bpm = 240 * n / t_end
    bars = [("G", None, "intro")]
    k = 0
    while len(bars) < n:
        sec = ["A", "B", "A2", "B2"][k % 4]; k += 1
        ch, ml = (A_CH, A_MEL) if sec.startswith("A") else (B_CH, B_MEL)
        for i in range(8):
            bars.append((ch[i], ml[i], sec + (":last" if i == 7 else "")))
    bars = bars[:n]
    if n >= 4:
        bars[-2] = (CAD_CH[0], CAD_MEL[0], "cad"); bars[-1] = (CAD_CH[1], CAD_MEL[1], "cad")
    return bars, bpm


LEVELS = dict(uke=0.36, bass=0.56, lead=0.18, gl=0.09, drums=0.58, wet=0.10)


def fresh(dur, ring=2.0, bpm=None, seed=5, levels=None, stems=False):
    rng = np.random.default_rng(seed)
    bars, bpm = plan(dur, ring, bpm)
    e8 = 60 / bpm / 2; bar = e8 * 8
    n = int(dur * SR) + SR
    uke, bass, lead, gl, drums, send = (np.zeros(n) for _ in range(6))
    hum = lambda: rng.normal(0, 0.004)          # 사람 손 같은 미세한 박자 흔들림
    for bi, (ch, ml, sec) in enumerate(bars):
        t0 = bi * bar
        intro = sec == "intro"
        # 우쿨렐레 스트럼: 다음 스트럼에서 줄이 다시 울리므로 그때까지만 울린다
        for si, (pos, way, vel) in enumerate(STRUM):
            nxt = STRUM[si + 1][0] if si + 1 < len(STRUM) else 8
            strings = UKE[ch] if way == "D" else UKE[ch][::-1]
            st = t0 + pos * e8 + hum()
            ln = (nxt - pos) * e8 + 0.05
            for j, m in enumerate(strings):
                y = ks(mtof(m), ln + 0.03, t60=1.2, bright=0.32 if way == "D" else 0.42, rng=rng)
                fo = int(0.03 * SR); y[-fo:] *= np.linspace(1, 0, fo)
                add(uke, y * vel * (0.85 + 0.3 * rng.random()) * (0.75 if intro else 1.0), (st + j * (0.011 if way == "D" else 0.008)) * SR)
        # 베이스
        if not intro:
            for pos, ln, iv in BASS:
                y = ks(mtof(ROOT[ch] + iv), ln * e8 + 0.04, t60=2.2, bright=0.12, pick=0.3, rng=rng)
                fo = int(0.04 * SR); y[-fo:] *= np.linspace(1, 0, fo)
                add(bass, y * (1.0 if pos in (0, 4) else 0.75), (t0 + pos * e8 + hum()) * SR)
        # 멜로디
        if ml:
            for a, ln, m in mel(ml):
                v = 0.9 + 0.2 * rng.random()
                y = marimba(mtof(m), max(0.6, ln * e8 + 0.5), rng) * v
                s = (t0 + a * e8 + hum()) * SR
                add(lead, y, s)
                if sec.startswith(("A2", "B2")) or sec == "cad":
                    add(gl, glock(mtof(m), 1.6, rng) * 0.45 * v, s)
        if sec.startswith("B") and sec.endswith(":last"):
            for a, ln, m in mel(B_FILL):
                add(gl, glock(mtof(m), 1.6, rng) * 0.8, (t0 + a * e8) * SR)
        if intro:
            for a, ln, m in mel(INTRO_GLOCK):
                add(gl, glock(mtof(m), 1.6, rng) * 0.8, (t0 + a * e8) * SR)
        # 타악기: 도입은 셰이커만
        for k16 in range(16):
            acc = k16 % 4 == 2
            add(drums, shaker(rng, acc) * (0.26 if acc else 0.14) * (0.9 + 0.2 * rng.random()), (t0 + k16 * e8 / 2 + hum()) * SR)
        if not intro:
            kicks = [0, 4] + ([3] if sec.startswith("B") else [])
            for p in kicks:
                add(drums, kick() * (0.9 if p in (0, 4) else 0.55), (t0 + p * e8) * SR)
            for p in (2, 6):
                c = clap(rng) * 0.45
                add(drums, c, (t0 + p * e8 + hum()) * SR); add(send, c * 0.8, (t0 + p * e8) * SR)
    # 마지막 I 화음: 한 번 쓸어내리는 스트럼 + 베이스 + 마림바 짧은 굴림 + 글로켄 딩
    tf = len(bars) * bar
    for j, m in enumerate(UKE["G"]):
        add(uke, ks(mtof(m), ring + 0.5, t60=2.5, bright=0.3, rng=rng) * 0.9, (tf + j * 0.018) * SR)
    add(bass, ks(mtof(ROOT["G"]), ring + 0.5, t60=3.0, bright=0.12, pick=0.3, rng=rng), tf * SR)
    add(drums, kick() * 0.9, tf * SR)
    for r in range(4):
        for m in (nm("G5"), nm("B5"), nm("D6")):
            add(lead, marimba(mtof(m), ring + 0.5, rng) * (0.55 - 0.1 * r), (tf + r * 0.035) * SR)
    add(gl, glock(mtof(nm("G6")), ring + 0.5, rng) * 0.7, (tf + 0.02) * SR)
    # 섞기: 스트럼은 목소리 대역을 덜 차지하게 저역·고역 정리, 멜로디·반짝임·박수는 잔향을 조금
    hp = lambda x, f: sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)
    lp = lambda x, f: sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)
    uke = lp(hp(uke, 170), 6500)
    bass = lp(bass, 1800)
    send = send + lead * 0.25 + gl * 0.4 + uke * 0.12
    nir = int(1.1 * SR); tt = np.arange(nir) / SR
    ir = lp(rng.standard_normal(nir) * np.exp(-6.91 * tt / 0.9), 4500); ir /= np.sqrt((ir ** 2).sum())
    ir = np.concatenate([np.zeros(int(0.018 * SR)), ir])
    wet = fftconvolve(send, ir)[:n]
    L = {**LEVELS, **(levels or {})}
    parts = dict(uke=uke * L["uke"], bass=bass * L["bass"], lead=lead * L["lead"], gl=gl * L["gl"], drums=drums * L["drums"], wet=wet * L["wet"])
    mix = sum(parts.values())
    mix = hp(mix, 35)
    mix = mix[: int(dur * SR)]
    fi = int(0.15 * SR); mix[:fi] *= np.linspace(0, 1, fi)
    fo = int(min(1.2, ring * 0.6) * SR); mix[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    pk = np.max(np.abs(mix)) + 1e-9
    if stems:
        return {k: v[: int(dur * SR)] / pk * 0.8 for k, v in parts.items()}, bpm
    return mix / pk * 0.8, bpm


if __name__ == "__main__":
    import soundfile as sf
    ap = argparse.ArgumentParser()
    ap.add_argument("dur", type=float); ap.add_argument("out")
    ap.add_argument("--bpm", type=float); ap.add_argument("--ring", type=float, default=2.0); ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()
    y, bpm = fresh(a.dur, a.ring, a.bpm, a.seed)
    sf.write(a.out, y.astype(np.float32), SR)
    print(f"배경음 {a.dur:.1f}초 · {bpm:.1f} BPM → {a.out}")
