"""다시 만든 줄(L01c 등)을 원래 줄 id(L01)로 바꿔 끼운다 — 화면·시간표가 원래 id를 쓰기 때문(EX.06)."""
import json, shutil, sys
M = json.load(open("voice/voice_meta.json", encoding="utf-8")); by = {m["id"]: m for m in M}
for pair in sys.argv[1:]:
    dst, src = pair.split("=")
    shutil.copy(f"voice/{src}.wav", f"voice/{dst}.wav")
    d = dict(by[src]); d["id"] = dst; d["keep"] = True; d["from"] = src
    by[dst].clear(); by[dst].update(d); print(dst, "<-", src, d["dur"], d["asr"])
json.dump(M, open("voice/voice_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
