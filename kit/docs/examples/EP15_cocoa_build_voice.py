"""대사 wav 를 시간표대로 한 트랙(voice.wav)으로 합치고 timeline.js(대사 시각·자막·입모양 곡선·단어 시각)를 만든다.
편마다 고치는 곳 두 군데:
  order — (줄, 앞 쉼, 장면 시작) 순서. 장면 s1~s9 는 index.html 의 장면 id 와 같다.
  WORD  — 화면·효과음을 맞출 단어 시각. 고른 소리를 받아써서 그 글자가 시작하는 순간을 찾고, 못 찾으면 줄 길이의 비율로 둔다.
         받아쓰기 표기(숫자는 아라비아 숫자, '일억'→'이럭' 등)를 후보 목록으로 여러 개 적는다.
아래 값은 EP.15 코코아 값 vs 빼빼로 값(2026-11-07)."""
import json
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

SR, FPS = 44100, 30
meta = {m["id"]: m for m in json.load(open("voice/voice_meta.json", encoding="utf-8"))}
GAP, SCENE = 0.35, 0.55
order = [  # (줄, 앞 쉼, 장면 시작 표시) — EP.15 코코아 값 vs 빼빼로 값
    ("L01", 0.30, "s1"), ("L02", GAP, None),
    ("L03", SCENE + .15, "s2"), ("L03b", 0.30, None), ("C3", 0.45, None), ("C2", 0.45, None), ("C1", 0.45, None), ("L05", 0.40, None),
    ("L06", SCENE + .45, "s3"), ("L07", SCENE + .6, "s4"),   # 힌트 1 선 그래프를 다 그린 뒤
    ("L09", SCENE + 2.0, "s5"), ("L10", 1.6, None), ("L11", 0.40, None),   # 힌트 2 뒤 셈할 틈 + 드럼롤
    ("L12", SCENE + .45, "s6"), ("L12b", 0.25, None), ("L12c", GAP, None),   # 정답 막대에서 '올봄 70% 내림'(도리 픽) 한 박자 → 반전 1: 왜 내렸나(ICCO)
    ("L13", SCENE + .1, "s7"), ("L13b", GAP, None),                         # 반전 2: 빼빼로는 2000원 그대로 + 비쌀 때 사 둔 원료(+ 아직 2022년의 2.5배 칩)
    ("L14", SCENE + .1, "s8"), ("L14b", 0.25, None),
    ("L15", SCENE + .1, "s9"), ("L15b", 0.35, None), ("L16", 0.20, None),
]
T, lines, t = {}, [], 0.0
for lid, gap, scene in order:
    t += gap
    if scene: T[scene] = round(t - (0.25 if scene != "s1" else 0.3), 3)
    T[lid] = round(t, 3)
    lines.append({"id": lid, "t": T[lid], "d": meta[lid]["dur"], "text": meta[lid]["text"]})
    t += meta[lid]["dur"]
T["END"] = round(t + 1.1, 3)
# 대사 속 단어 시각 — 고른 소리를 받아써서 단어가 시작하는 순간을 찾는다(못 찾으면 줄 길이의 비율로 둔다)
import sys
sys.path.insert(0, "voice")
from asr import rec
from scipy.signal import resample_poly as _rs
def words(lid):
    sr, x = wavfile.read(f"voice/{lid}.wav"); x = x.astype(np.float32) / 32768
    x = _rs(x, 16000, sr).astype(np.float32)
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s)
    return list(zip(s.result.tokens, s.result.timestamps))
WORD = {  # 이름: (줄, 찾을 글자, 몇 번째, 못 찾을 때 비율) — EP.15 코코아
    "wPep": ("L02", ["빼빼로", "빼배로", "빼빼"], 1, .05),
    "cA": ("L03", ["15", "십오"], 1, .03), "cB": ("L03", ["45", "사십오"], 1, .30), "cC": ("L03", ["75", "칠십오"], 1, .58),
    "pick": ("L05", ["75", "칠십오"], 1, .12), "wUp": ("L06", ["올랐", "올라"], 1, .75),
    "wMan": ("L07", ["만", "1만"], 1, .30), "w6k": ("L07", ["6천", "육천", "6000"], 1, .65),
    "wHalf": ("L11", ["반값", "반"], 1, .25),
    "wProd": ("L12", ["8.5", "8", "팔"], 1, .62), "wUse": ("L12b", ["3.3", "3", "삼"], 1, .55), "wLeft": ("L12c", ["남기", "남"], 1, .55),
    "w2000": ("L13", ["2000", "이천", "2천"], 1, .62), "wRaw": ("L13b", ["원료", "원뇨"], 1, .62),
    "wSame8": ("L14", ["빼빼로", "빼배로", "빼빼"], 1, .60),
    "stamp": ("L14b", "끝", 1, .45), "pouch": ("L16", "볼", 1, .03)}
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
    T[k] = round(T[lid] + (at if at is not None else frac * meta[lid]["dur"]), 3)
    print(f"{k:7s} {lid:5s} {str(tgt)[:12]:12s} -> {'찾음' if at is not None else '비율'} {T[k]-T[lid]:.2f}s")
T["drum"] = round(T["L09"] + meta["L09"]["dur"] + 0.05, 3)
T["san"] = round(T["L11"] + meta["L11"]["dur"] + 0.1, 3)   # 올봄 바닥(70% 내림) 꼬리표 — 도리 픽이 틀린 순간

n = int(T["END"] * SR)
track = np.zeros(n, dtype=np.float32)
for l in lines:
    sr, x = wavfile.read(f"voice/{l['id']}.wav")
    x = x.astype(np.float32) / 32768
    if sr != SR: x = resample_poly(x, SR, sr).astype(np.float32)
    i = int(l["t"] * SR)
    track[i:i + len(x)] += x[: n - i]
wavfile.write("voice.wav", SR, (np.clip(track, -1, 1) * 32767).astype(np.int16))
hop = SR // FPS
env = [float(np.sqrt(np.mean(track[i:i + hop] ** 2))) for i in range(0, n, hop)]
mx = np.percentile([e for e in env if e > 0.01], 95)
env = [round(min(1.0, e / mx), 3) for e in env]
open("timeline.js", "w", encoding="utf-8").write("window.TL=" + json.dumps({"T": T, "lines": lines, "env": env}, ensure_ascii=False) + ";")
print("END", T["END"])
for l in lines: print(f'{l["t"]:6.2f}-{l["t"] + l["d"]:6.2f} {l["id"]}')
print({k: T[k] for k in ["s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "drum", "L10", "stamp", "wHalf", "san"]}, "정답 위치", round(T["L10"] / T["END"] * 100, 1), "%")
