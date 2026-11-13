"""손으로 테이크를 고른다: python3 voice/force_take.py <줄> <out 안 경로(예: ex12-01/t11/00_2.wav)> — 다듬어 voice/<줄>.wav, 메타 keep:true."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
sys.path.insert(0, str(Path(__file__).parent))
from voice_job import repo
def proc(x, sr):
    a = np.abs(x); th = 10 ** (-42 / 20) * a.max(); i = np.where(a > th)[0]
    x = x[max(0, i[0] - int(.03 * sr)):min(len(x), i[-1] + int(.1 * sr))]
    x = resample_poly(x, 44100, sr).astype(np.float32); return x / np.max(np.abs(x)) * 0.89
lid, rel = sys.argv[1], sys.argv[2]
sr, x = wavfile.read(repo() / "out" / rel); x = x.astype(np.float32); x = x / 32768 if np.abs(x).max() > 2 else x
y = proc(x, sr); wavfile.write(f"voice/{lid}.wav", 44100, (y * 32767).astype(np.int16))
L = {l["id"]: l for l in json.load(open("voice/lines.json", encoding="utf-8"))}
M = json.load(open("voice/voice_meta.json", encoding="utf-8"))
ent = {"id": lid, "dur": round(len(y) / 44100, 3), "sr": 44100, "text": L[lid]["sub"], "spoken": L[lid]["say"], "pass": True, "take": rel, "voice": "C", "keep": True}
M = [m for m in M if m["id"] != lid]; M.append(ent)
json.dump(M, open("voice/voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for l in json.load(open("voice/lines.json", encoding="utf-8")):
    pass
print(lid, rel, ent["dur"])
