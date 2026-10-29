"""고른 C 소리에서 0.45초보다 긴 쉼을 0.38초로 줄인다(앞뒤 0.05초 페이드). voice_meta.json 길이도 고친다."""
import json, sys, numpy as np
from scipy.io import wavfile
ids = sys.argv[1:]
meta = json.load(open("voice_meta.json", encoding="utf-8"))
for m in meta:
    if ids and m["id"] not in ids: continue
    sr, x = wavfile.read(f"{m['id']}.wav"); x = x.astype(np.float32) / 32768
    hop = int(.02 * sr); n = len(x) // hop
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) + 1e-9) for i in range(n)])
    quiet = db < -38
    keep = np.ones(len(x), bool); i = 0; cut = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            L = (j - i) * hop / sr
            if L > .45 and i > 0 and j < n:
                a = i * hop + int(.19 * sr); b = j * hop - int(.19 * sr)
                keep[a:b] = False; cut += (b - a) / sr
            i = j
        else: i += 1
    y = x[keep]
    if cut:
        y = y.copy()
        wavfile.write(f"{m['id']}.wav", sr, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    m["dur"] = round(len(y) / sr, 3)
    if cut: print(m["id"], f"-{cut:.2f}s ->", m["dur"])
json.dump(meta, open("voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
