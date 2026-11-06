"""고른 소리의 앞뒤 무음을 0.12초로 줄이고 voice_meta.json 길이를 고친다(EX.06)."""
import json, sys, numpy as np
from scipy.io import wavfile
meta = json.load(open("voice/voice_meta.json", encoding="utf-8"))
for m in meta:
    if sys.argv[1:] and m["id"] not in sys.argv[1:]: continue
    sr, x = wavfile.read(f"voice/{m['id']}.wav"); f = x.astype(np.float32) / 32768
    e = np.convolve(np.abs(f), np.ones(int(.02 * sr)) / int(.02 * sr), "same"); on = np.where(e > .01)[0]
    a = max(0, on[0] - int(.12 * sr)); b = min(len(x), on[-1] + int(.12 * sr))
    if a > 0 or b < len(x):
        y = x[a:b].astype(np.float32); n = int(.03 * sr); y[-n:] *= np.linspace(1, 0, n)
        wavfile.write(f"voice/{m['id']}.wav", sr, y.astype(np.int16)); old = m["dur"]; m["dur"] = round(len(y) / sr, 3)
        print(m["id"], old, "->", m["dur"])
json.dump(meta, open("voice/voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
