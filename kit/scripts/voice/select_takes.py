"""목소리 C 결과에서 줄마다 가장 또렷한 테이크를 골라 voice/<줄>.wav(44.1kHz, 앞뒤 무음 다듬음)와 voice/voice_meta.json 을 만든다.

  python3 voice/select_takes.py            모든 줄
  python3 voice/select_takes.py L02 L06    이 줄만 다시 고른다(나머지는 이전 메타 그대로)

- 후보: voice/c_index.json {줄: [[작업id, task, 대사번호], …]} 의 모든 테이크.
- 통과: lines.json 의 keys(숫자·핵심어)가 원본 소리와 다듬은 소리 두 받아쓰기에 모두 들어 있어야 한다(spell.py 의 같은 말 포함).
- 순위: 통과 > 원문과 비슷한 정도(두 받아쓰기 중 낮은 쪽).
- lines.json 에서 "reuse": "<공용 id>" 인 줄은 voice/voice_common.json 의 공용 소리를 그대로 쓴다(카운트다운·정답은·검산 끝·댓글·볼주머니에 쏙).
- "keep": true 인 줄이나 후보가 없는 줄은 이전 메타를 그대로 둔다(이미 고른 소리, 손으로 이어 붙인 소리).
"""
import difflib, glob, json, shutil, sys
from pathlib import Path
import numpy as np, parselmouth
from scipy.io import wavfile
from scipy.signal import resample_poly
sys.path.insert(0, str(Path(__file__).parent))
from asr import transcribe
from spell import load, norm, ok, num_form, ko
from voice_job import repo

V = Path("voice")
L = {l["id"]: l for l in json.load(open(V / "lines.json", encoding="utf-8"))}
IDX = json.load(open(V / "c_index.json", encoding="utf-8")) if (V / "c_index.json").exists() else {}
COMMON = {c["id"]: c for c in json.load(open(V / "voice_common.json", encoding="utf-8"))}
ALT, NF = load(V)
prev = {m["id"]: m for m in json.load(open(V / "voice_meta.json", encoding="utf-8"))} if (V / "voice_meta.json").exists() else {}


def proc(x, sr):
    a = np.abs(x); th = 10 ** (-42 / 20) * a.max(); i = np.where(a > th)[0]
    x = x[max(0, i[0] - int(.03 * sr)):min(len(x), i[-1] + int(.1 * sr))]
    x = resample_poly(x, 44100, sr).astype(np.float32); return x / np.max(np.abs(x)) * 0.89


def read(f):
    sr, x = wavfile.read(f); x = x.astype(np.float32)
    return sr, (x / 32768 if np.abs(x).max() > 2 else x)


meta, report, only = [], [], set(sys.argv[1:])
R = repo() if IDX else None
for lid, l in L.items():
    if l.get("reuse"):
        c = COMMON[l["reuse"]]; shutil.copy(V / c["file"], V / f"{lid}.wav")
        meta.append({"id": lid, "dur": c["dur"], "sr": 44100, "text": l.get("sub", c["sub"]), "spoken": c["spoken"], "pass": True, "take": f"공용:{c['id']}", "voice": "C"})
        continue
    if l.get("keep") or lid not in IDX or (only and lid not in only):
        if lid in prev: meta.append(prev[lid])
        elif lid not in IDX: print("후보 없음:", lid)
        continue
    files = []
    for job, task, ti in IDX[lid]:
        files += sorted(glob.glob(str(R / "out" / job / task / f"{ti:02d}_*.wav")))
    best = None
    for f in files:
        sr, x = read(f)
        t1 = transcribe(f)
        wavfile.write("_p.wav", 44100, (proc(x, sr) * 32767).astype(np.int16)); t2 = transcribe("_p.wav")
        ref = ko(num_form(l["say"], NF))                       # 숫자는 한글 읽기로 맞춰 비교한다
        sim = min(difflib.SequenceMatcher(None, ref, ko(norm(t1))).ratio(), difflib.SequenceMatcher(None, ref, ko(norm(t2))).ratio())
        good = ok(t1, l.get("keys", []), ALT) and ok(t2, l.get("keys", []), ALT)
        p = parselmouth.Sound(f).to_pitch(pitch_ceiling=700).selected_array["frequency"]; p = p[p > 0]
        k = "/".join(Path(f).parts[-3:])
        report.append((lid, k, "통과" if good else "확인", round(sim, 2), round(float(np.median(p)) if len(p) else 0), t1, "|", t2))
        if best is None or (good, sim) > best[:2]: best = (good, sim, k, t2, f)
    if best is None: print("소리 없음:", lid); continue
    good, sim, k, t2, f = best
    sr, x = read(f); x = proc(x, sr)
    wavfile.write(V / f"{lid}.wav", 44100, (x * 32767).astype(np.int16))
    meta.append({"id": lid, "dur": round(len(x) / 44100, 3), "sr": 44100, "text": l.get("sub", ""), "spoken": l["say"], "asr": t2, "pass": good, "take": k, "voice": "C"})
for r in report: print(*r)
json.dump(meta, open(V / "voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("고른 것:", [(m["id"], m["take"], m.get("pass")) for m in meta if not str(m["take"]).startswith("공용")])
print("확인할 줄:", [m["id"] for m in meta if not m.get("pass") and L.get(m["id"], {}).get("keys")])
