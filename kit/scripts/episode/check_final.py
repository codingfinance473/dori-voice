"""완성 영상(또는 mix.wav)에서 줄마다 소리를 잘라 받아쓰고, 숫자·핵심어가 배경음 위에서도 들리는지 본다.
  python3 check_final.py 완성.mp4|mix.wav
받아쓰기는 자르는 창에 따라 한 덩어리를 통째로 빼먹을 때가 있어 창 셋으로 보고 둘 이상 통과하면 통과.
같은 말 표기는 voice/spell.py + voice/spell.json."""
import json, subprocess, sys
from scipy.io import wavfile
sys.path.insert(0, "voice")
from asr import transcribe
from spell import load, ok

ALT, _ = load("voice")
src = sys.argv[1]
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "16000", "_chk.wav"], check=True)
sr, x = wavfile.read("_chk.wav")
s = open("timeline.js", encoding="utf-8").read()
TL = json.loads(s[s.index("{"):s.rindex("}") + 1])
L = {l["id"]: l for l in json.load(open("voice/lines.json", encoding="utf-8"))}
bad = []
for ln in TL["lines"]:
    keys = L.get(ln["id"], {}).get("keys", [])
    outs = []
    for pa, pb in ((.05, .12), (.0, .0), (.2, .3)):
        a, b = int((ln["t"] - pa) * sr), int((ln["t"] + ln["d"] + pb) * sr)
        wavfile.write("_seg.wav", sr, x[max(0, a):b]); outs.append(transcribe("_seg.wav"))
    hits = [ok(o, keys, ALT) if keys else True for o in outs]
    good = sum(hits) >= 2
    if not good: bad.append(ln["id"])
    print(f'{ln["id"]:5s} {"통과" if good else "확인"}  {max(zip(hits, outs))[1]}  ({sum(hits)}/3)')
print("확인할 줄:", bad)
