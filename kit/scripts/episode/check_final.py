"""완성 영상(또는 mix.wav)에서 줄마다 소리를 잘라 받아쓰고, 숫자·핵심어가 배경음 위에서도 들리는지 본다.
  python3 check_final.py 완성.mp4|mix.wav
끝으로 줄 안 빈틈(목소리만, 0.7초 넘게)과 조용한 구간(-38dBFS 아래 0.4초 이상, 맨 끝 0.15초 제외)을 찾는다 — 2026-11-11 사용자: "영상 말미에 뜬금없이 침묵하는 부분".
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

# 조용한 구간 — 말이 끝난 뒤 음악·효과음이 먼저 꺼져 화면만 남는 곳(특히 끝)
import numpy as np
y = x.astype(np.float32) / 32768; h = int(.05 * sr)
db = 20 * np.log10(np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) for i in range(0, len(y) - h, h)]) + 1e-9)
quiet, run = [], None
for i, d in enumerate(list(db) + [0]):
    if d < -38 and i * .05 < len(y) / sr - .15:
        run = i if run is None else run
    elif run is not None:
        if (i - run) * .05 >= .4: quiet.append((round(run * .05, 2), round(i * .05, 2)))
        run = None
end_voice = max(l["t"] + l["d"] for l in TL["lines"]); tail = len(y) / sr - end_voice
print("조용한 구간:", quiet or "없음", f"· 마지막 말 뒤 {tail:.2f}초")
if quiet or tail > .9:
    print("확인 — 조용한 구간/끝 꼬리: build_voice.py 의 END(마지막 줄 + 0.6초 안팎)와 music.py 끝맺음(마지막 화음이 끝까지 울리게)을 고친다")

# 줄 안 빈틈 — 한 줄 소리 안에 말이 끊긴 채 0.7초 넘게 비거나, 말이 끝난 뒤 군소리·무음이 길게 붙은 곳(목소리만 든 voice.wav 로 잰다)
# 2026-11-11 사용자: "'1교시 전에 내야 한대' 하고 시차를 두는 이유가 뭐야?" — EX.09 L07 테이크 끝에 3.9초 무음·군소리가 붙어 있었다.
try:
    vsr, vv = wavfile.read("voice.wav"); vv = vv.astype(np.float32) / 32768
    if vv.ndim > 1: vv = vv.mean(1)
    hv = int(.05 * vsr); gaps = []
    for ln in TL["lines"]:
        a, b = int(ln["t"] * vsr), int((ln["t"] + ln["d"]) * vsr)
        e = [20 * np.log10(np.sqrt(np.mean(vv[i:i + hv] ** 2)) + 1e-9) for i in range(a, max(a, b - hv), hv)]
        sp = [i for i, d in enumerate(e) if d > -28]
        if not sp: continue
        runs = [(sp[k + 1] - sp[k]) * .05 for k in range(len(sp) - 1)] + [(len(e) - 1 - sp[-1]) * .05]
        if max(runs) > .7: gaps.append((ln["id"], round(max(runs), 2)))
    print("줄 안 빈틈:", gaps or "없음")
    if gaps: print("확인 — 그 줄 테이크를 잘라(끝 군소리) 또는 tighten.py 로 줄이고 build_voice.py 부터 다시")
except FileNotFoundError:
    print("줄 안 빈틈: voice.wav 가 없어 건너뜀")
