"""손으로 고른 테이크를 그 줄 소리로 쓴다 — python3 pin.py L03=ep14-01/t02/00_1.wav … (EP.14)"""
import json, sys, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
OUT = "/home/claude/dori-voice/out"
def proc(x, sr):
    a = np.abs(x); th = 10 ** (-42 / 20) * a.max(); i = np.where(a > th)[0]
    x = x[max(0, i[0] - int(.03 * sr)):min(len(x), i[-1] + int(.1 * sr))]
    x = resample_poly(x, 44100, sr).astype(np.float32); return x / np.max(np.abs(x)) * 0.89
M = json.load(open("voice/voice_meta.json", encoding="utf-8")); by = {m["id"]: m for m in M}
for arg in sys.argv[1:]:
    lid, take = arg.split("=")
    sr, x = wavfile.read(f"{OUT}/{take}"); x = x.astype(np.float32); x = x / 32768 if np.abs(x).max() > 2 else x
    y = proc(x, sr); wavfile.write(f"voice/{lid}.wav", 44100, (y * 32767).astype(np.int16))
    by[lid].update(dur=round(len(y) / 44100, 3), take=take, keep=True); print(lid, take, by[lid]["dur"])
json.dump(M, open("voice/voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
