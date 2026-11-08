"""대사 wav 를 시간표대로 한 트랙(voice.wav)으로 합치고 timeline.js(대사 시각·자막·입모양 곡선·단어 시각)를 만든다.
편마다 고치는 곳 두 군데:
  order — (줄, 앞 쉼, 장면 시작) 순서. 장면 s1~s9 는 index.html 의 장면 id 와 같다.
  WORD  — 화면·효과음을 맞출 단어 시각. 고른 소리를 받아써서 그 글자가 시작하는 순간을 찾고, 못 찾으면 줄 길이의 비율로 둔다.
아래 값은 EX.07 해외직구(2026-11-08)."""
import json
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

SR, FPS = 44100, 30
meta = {m["id"]: m for m in json.load(open("voice/voice_meta.json", encoding="utf-8"))}
GAP, SCENE = 0.35, 0.55
order = [  # (줄, 앞 쉼, 장면 시작 표시) — EX.07 해외직구(설명형)
    ("L01", 0.30, "s1"), ("L02", GAP, None),
    ("L03", SCENE + .15, "s2"), ("L04", GAP, None), ("L05", 0.45, None),
    ("L06", SCENE + .15, "s3"), ("L07", GAP, None),
    ("L08", SCENE + .15, "s4"),
    ("L09", SCENE + .15, "s5"),
    ("L10", SCENE + .15, "s6"), ("L11", GAP, None), ("L12", 0.45, None),
    ("L13", SCENE + .15, "s8"), ("L13b", 0.3, None),
    ("L14b", 0.35, None), ("L15", 0.2, None),
]
T, lines, t = {}, [], 0.0
for lid, gap, scene in order:
    t += gap
    if scene: T[scene] = round(t - (0.25 if scene != "s1" else 0.3), 3)
    T[lid] = round(t, 3)
    lines.append({"id": lid, "t": T[lid], "d": meta[lid]["dur"], "text": meta[lid]["text"]})
    t += meta[lid]["dur"]
T["END"] = round(t + 1.1, 3)
import sys
sys.path.insert(0, "voice")
from asr import rec
from scipy.signal import resample_poly as _rs
def words(lid):
    sr, x = wavfile.read(f"voice/{lid}.wav"); x = x.astype(np.float32) / 32768
    x = _rs(x, 16000, sr).astype(np.float32)
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s)
    return list(zip(s.result.tokens, s.result.timestamps))
WORD = {  # 이름: (줄, 찾을 글자 후보, 몇 번째, 못 찾을 때 비율)
    "wQ": ("L02", ["정말", "정"], 1, .10),
    "wSum": ("L03", ["이조", "2조", "조", "미쳤"], 1, .62),
    "wDrop": ("L04", ["6.3", "육점", "육"], 1, .42),
    "wTwo": ("L05", ["두", "연속"], 1, .02), "wFirst": ("L05", ["처음"], 1, .84),
    "wCN": ("L06", ["9.1", "구점", "구"], 1, .55),
    "wUS": ("L07", ["11.1", "십일"], 1, .30),
    "wCloth": ("L08", ["옷"], 1, .30), "wC15": ("L08", ["15", "십오"], 1, .60),
    "wJP": ("L09", ["32", "삼십"], 1, .55),
    "wFX": ("L10", ["위안", "위"], 1, .48), "wUp": ("L10", ["비싸"], 1, .82),
    "wYen": ("L11", ["5", "오"], 1, .40),
    "wLess": ("L12", ["덜"], 1, .30), "wMore": ("L12", ["더샀", "더"], 1, .80),
    "stamp": ("L13b", "끝", 1, .45), "pouch": ("L15", "볼", 1, .03)}
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
loud = [e for e in env if e > 0.01]
mx = np.percentile(loud, 95) if loud else 1.0
env = [round(min(1.0, e / mx), 3) for e in env]
open("timeline.js", "w", encoding="utf-8").write("window.TL=" + json.dumps({"T": T, "lines": lines, "env": env}, ensure_ascii=False) + ";")
print("END", T["END"])
for l in lines: print(f'{l["t"]:6.2f}-{l["t"] + l["d"]:6.2f} {l["id"]}')
print({k: T[k] for k in ["s2", "s3", "s4", "s5", "s6", "s8", "stamp"]})
