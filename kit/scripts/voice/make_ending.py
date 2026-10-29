"""끝인사 = 공용 "볼주머니에 쏙!"(매 편 같은 소리) + 0.28초 쉼 + 이번 편 예고 한 줄.
  python3 voice/make_ending.py L16 L16b      → voice/L16.wav 를 만들고 voice_meta.json 의 L16 을 바꾼다
  (L16b = lines.json 의 예고 줄, 예: "다음엔 화장품 퀴즈로 올게." — 먼저 select_takes.py 로 골라 둔다.)
  L16 의 sub 는 "볼주머니에 쏙!<br>다음엔 ○○ 퀴즈로 올게" 처럼 lines.json 에 적어 둔다.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, str(Path(__file__).parent))
from asr import transcribe

out_id, tail_id = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("L16", "L16b")
V = Path("voice")
sr, a = wavfile.read(V / "bolju_ssok.wav"); a = a.astype(np.float32) / 32768
sr2, b = wavfile.read(V / f"{tail_id}.wav"); b = b.astype(np.float32) / 32768
assert sr == sr2 == 44100
x = np.concatenate([a, np.zeros(int(.28 * sr), np.float32), b])
wavfile.write(V / f"{out_id}.wav", sr, (x * 32767).astype(np.int16))
meta = json.load(open(V / "voice_meta.json", encoding="utf-8"))
L = {l["id"]: l for l in json.load(open(V / "lines.json", encoding="utf-8"))}
mb = next(m for m in meta if m["id"] == tail_id)
meta = [m for m in meta if m["id"] != out_id]
meta.append({"id": out_id, "dur": round(len(x) / sr, 3), "sr": sr, "text": L.get(out_id, {}).get("sub", ""), "spoken": "볼주머니에 쏙! " + mb.get("spoken", ""),
             "asr": transcribe(str(V / f"{out_id}.wav")), "pass": mb.get("pass", True), "take": f"공용:bolju_ssok + {tail_id}({mb['take']})", "voice": "C", "keep": True})
json.dump(meta, open(V / "voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(meta[-1])
