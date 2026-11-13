"""대사 wav 를 시간표대로 한 트랙(voice.wav)으로 합치고 timeline.js 를 만든다 — 2인 형식(도리·모리).
편마다 고치는 곳: order(줄·앞 쉼·장면), WORD(화면·효과음 단어 시각). 아래 값은 EX.12 일본 쌀값(2026-11-13).
timeline.js: T(줄·장면·단어 시각), lines(id·t·d·text·who), env(둘 합침), envD(도리 입), envM(모리 입)."""
import json, sys, os
ALT = os.environ.get("MORI_ALT", "0") == "1"   # 기본 1: 사용자가 3번 목소리를 골랐다(2026-11-10)
#   # 1이면 모리 줄을 비교용 3번 목소리(…x)로 — 같은 id 로 시간표를 만든다
def SRC(lid): return lid + "x" if ALT and lid[0] == "M" and (lid + "x") in meta else lid
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

SR, FPS = 44100, 30
meta = {m["id"]: m for m in json.load(open("voice/voice_meta.json", encoding="utf-8"))}
WHO = {l["id"]: l.get("who", "D") for l in json.load(open("voice/lines.json", encoding="utf-8"))}

from scipy.signal import butter, sosfilt
def _f(x, f, kind): return sosfilt(butter(2, f, kind, fs=SR, output="sos"), x)
def _act(x): a = x[np.abs(x) > .02 * np.max(np.abs(x))]; return float(np.sqrt(np.mean(a ** 2)))
DORI_RMS = 10 ** (-13.1 / 20)   # 도리 줄의 말하는 구간 평균 음량(EX.08 실측)
def mori_fx(x):
    """모리(낮은 목소리)를 도리와 같은 크기·또렷함으로(2026-11-10): 실측 — 모리 줄이 평균 2.6dB 작고 에너지의 43%가 300Hz 아래(도리 6%)라
    베이스에 묻히고 폰 스피커에선 얇아졌다. 110Hz 아래를 자르고 300Hz 아래를 덜고(-5dB) 2~5kHz 를 올린(+4dB) 뒤 도리 음량에 맞춘다."""
    x = _f(x, 110, "high"); low = _f(x, 300, "low"); x = x - .6 * low
    x = x + .6 * _f(x, [2000, 5000], "band")
    x = x * (DORI_RMS / (_act(x) + 1e-9))
    x = np.tanh(x * 1.1) / 1.1; x = x * (DORI_RMS / (_act(x) + 1e-9))
    return np.clip(x, -.97, .97).astype(np.float32)   # 올린 만큼 넘치는 봉우리만 부드럽게 누른다
GAP, SCENE = 0.30, 0.32   # 배경음 없는 판(2026-11-10): 쉼이 그대로 무음이라 조금 더 촘촘하게
order = [  # (줄, 앞 쉼, 장면 시작 표시) — EX.12 일본 쌀값(2026-11-13)
    ("L01", 0.30, "s1"), ("M01", 0.18, None), ("M00", 0.15, None),
    ("L02", SCENE, "s2"), ("M02", 0.18, None),
    ("L03", SCENE, "s3"), ("M03", 0.18, None),
    ("L04", SCENE, "s4"), ("L05", GAP, None), ("M04", 0.18, None),
    ("L06", SCENE, "s5"),
    ("M05", 0.25, None), ("L08", 0.40, "s8"), ("L09", 0.30, None),
    ("L10", 0.35, None), ("L11", 0.20, None),
]
T, lines, t = {}, [], 0.0
import math
QUANT = float(os.environ.get("BPM", "100"))   # 박자 맞춤(2026-11-11 시안): 줄 시작을 8분음표 격자에, 장면 시작을 박에 맞춘다
for lid, gap, scene in order:
    t += gap
    if QUANT:
        g = 60 / QUANT * .5
        t = math.ceil((t - .08) / g - 1e-9) * g
    if scene: T[scene] = round(t - (0.25 if scene != "s1" else 0.3), 3)
    T[lid] = round(t, 3)
    lines.append({"id": lid, "t": T[lid], "d": meta[SRC(lid)]["dur"], "text": meta[SRC(lid)]["text"], "who": WHO.get(lid, "D")})
    t += meta[SRC(lid)]["dur"]
T["END"] = round(t + .6, 3)   # 마지막 말 뒤 0.6초 — 1.1초는 끝에 화면만 남는 침묵이 됐다(2026-11-11 사용자)
sys.path.insert(0, "voice")
from asr import rec
def words(lid):
    sr, x = wavfile.read(f"voice/{SRC(lid)}.wav"); x = x.astype(np.float32) / 32768
    x = resample_poly(x, 16000, sr).astype(np.float32)
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s)
    return list(zip(s.result.tokens, s.result.timestamps))
WORD = {  # 이름: (줄, 찾을 글자 후보, 몇 번째, 못 찾을 때 비율)
    "w15": ("L01", ["일점오", "1.5", "일 점", "점오"], 1, .45),
    "wMori": ("M00", ["모리", "머리", "몰이"], 1, .12),
    "w2800": ("L02", ["이천", "2800", "2천"], 1, .55),
    "w23": ("L03", ["이만", "2만"], 1, .45),
    "w63": ("L04", ["육만", "6만"], 1, .55),
    "w16": ("L05", ["만육", "육천", "1만", "만"], 1, .55),
    "wPeak": ("L06", ["최고"], 1, .45), "w36": ("L06", ["삼십육", "36", "삼십"], 1, .70),
    "stamp": ("L08", "끝", 1, .45), "pouch": ("L11", "볼", 1, .03)}
cache = {}
for k, (lid, tgt, nth, frac) in WORD.items():
    if lid not in cache: cache[lid] = words(lid)
    toks = cache[lid]; txt = ""; starts = []
    for tok, ts in toks:
        for ch in tok.replace(" ", ""): txt += ch; starts.append(ts)
    pos, at = -1, None
    for tg in (tgt if isinstance(tgt, list) else [tgt]):
        pos = -1
        for _ in range(nth):
            pos = txt.find(tg, pos + 1)
            if pos < 0: break
        if pos >= 0: break
    if pos >= 0: at = starts[pos]
    T[k] = round(T[lid] + (at if at is not None else frac * meta[SRC(lid)]["dur"]), 3)
    print(f"{k:8s} {lid:5s} {str(tgt)[:14]:14s} -> {'찾음' if at is not None else '비율'} {T[k]-T[lid]:.2f}s")

n = int(T["END"] * SR)
track = np.zeros(n, dtype=np.float32); trD = np.zeros(n, dtype=np.float32); trM = np.zeros(n, dtype=np.float32)
for l in lines:
    sr, x = wavfile.read(f"voice/{SRC(l['id'])}.wav")
    x = x.astype(np.float32) / 32768
    if sr != SR: x = resample_poly(x, SR, sr).astype(np.float32)
    if l["who"] == "M": x = mori_fx(x)
    i = int(l["t"] * SR); seg = x[: n - i]
    track[i:i + len(seg)] += seg
    (trM if l["who"] == "M" else trD)[i:i + len(seg)] += seg
wavfile.write("voice.wav", SR, (np.clip(track, -1, 1) * 32767).astype(np.int16))
hop = SR // FPS
def envelope(tr):
    env = [float(np.sqrt(np.mean(tr[i:i + hop] ** 2))) for i in range(0, n, hop)]
    loud = [e for e in env if e > 0.01]
    mx = np.percentile(loud, 95) if loud else 1.0
    return [round(min(1.0, e / mx), 3) for e in env]
env, envD, envM = envelope(track), envelope(trD), envelope(trM)
open("timeline.js", "w", encoding="utf-8").write("window.TL=" + json.dumps({"BPM": QUANT, "T": T, "lines": lines, "env": env, "envD": envD, "envM": envM}, ensure_ascii=False) + ";")
print("END", T["END"])
for l in lines: print(f'{l["t"]:6.2f}-{l["t"] + l["d"]:6.2f} {l["who"]} {l["id"]}')
print({k: T[k] for k in ["s2", "s3", "s4", "s5", "s8", "stamp"]})
