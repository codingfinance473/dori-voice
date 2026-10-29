"""도리 목소리 C 작업 올리기·기다리기 — 사용자 비공개 저장소 codingfinance473/dori-voice 의 깃허브 액션(Qwen3-TTS 0.6B Base, voices/dori).

  python3 voice/voice_job.py make <작업id> L02 L06 … [--takes 4] [--note "EP.03 화장품"] [--trailer "커밋 끝줄"] [--dry]
      voice/lines.json 의 say 를 줄마다 작업(task) 하나로 jobs/<작업id>.json 에 쓰고 push 한다.
      voice/c_index.json 에 그 줄의 후보로 [작업id, task, 0] 을 더한다(이전 후보는 남겨 둔다).
  python3 voice/voice_job.py wait <작업id>
      out/<작업id>/done.json 이 커밋될 때까지 20초마다 확인하고 받아 온다(Bash 백그라운드로 돌린다, 보통 8~15분).

저장소 위치: DORI_VOICE_REPO, 없으면 ~/dori-voice, /home/claude/dori-voice 순서로 찾는다.
"""
import json, os, subprocess, sys, time, zlib
from pathlib import Path


def repo():
    for p in (os.environ.get("DORI_VOICE_REPO"), Path.home() / "dori-voice", "/home/claude/dori-voice"):
        if p and (Path(p) / "jobs").is_dir(): return Path(p)
    sys.exit("dori-voice 저장소를 찾지 못했어요 — 클론하고 DORI_VOICE_REPO 를 지정하세요")


def git(R, *a):
    r = subprocess.run(["git", "-C", str(R), *a], capture_output=True, text=True)
    if r.returncode: sys.exit(f"git {' '.join(a)} 실패: {r.stderr.strip()}")
    return r.stdout


def make(jid, ids, takes=4, note="", trailer="", dry=False):
    R = repo(); L = {l["id"]: l for l in json.load(open("voice/lines.json", encoding="utf-8"))}
    if not dry: git(R, "pull", "-q", "--rebase", "--autostash", "origin", "main")
    if (R / "jobs" / f"{jid}.json").exists(): sys.exit(f"{jid} 는 이미 있어요 — 새 작업 id 를 쓰세요")
    tasks, seed0 = [], zlib.crc32(jid.encode()) % 900 + 100
    for i, lid in enumerate(ids):
        say = L[lid]["say"]
        tasks.append({"id": f"t{i:02d}", "mode": "clone", "model": "Qwen/Qwen3-TTS-12Hz-0.6B-Base", "voice": "voices/dori",
                      "seed": seed0 + i, "takes": takes, "texts": [say], "dtype": "auto"})
    job = {"id": jid, "note": note or f"대사 {len(ids)}줄", "tasks": tasks, "lines": ids}
    if dry: print(json.dumps(job, ensure_ascii=False, indent=1)); return
    (R / "jobs" / f"{jid}.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    git(R, "add", f"jobs/{jid}.json")
    msg = f"작업: {job['note']}" + (f"\n\n{trailer}" if trailer else "")
    git(R, "commit", "-q", "-m", msg); git(R, "push", "-q", "origin", "main")
    idx = json.load(open("voice/c_index.json", encoding="utf-8")) if Path("voice/c_index.json").exists() else {}
    for i, lid in enumerate(ids):
        cands = idx.get(lid, [])
        if cands and isinstance(cands[0], str): cands = [["?", *cands]]
        idx[lid] = cands + [[jid, f"t{i:02d}", 0]]
    json.dump(idx, open("voice/c_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"올림: {jid} — {len(ids)}줄 × {takes}테이크. 기다리기: python3 voice/voice_job.py wait {jid}")


def wait(jid, every=20, limit=3600):
    R = repo(); t0 = time.time()
    while time.time() - t0 < limit:
        subprocess.run(["git", "-C", str(R), "fetch", "-q", "origin"], capture_output=True)
        if subprocess.run(["git", "-C", str(R), "cat-file", "-e", f"origin/main:out/{jid}/done.json"], capture_output=True).returncode == 0:
            git(R, "pull", "-q", "--rebase", "--autostash", "origin", "main")
            n = len(list((R / "out" / jid).glob("*/*.wav")))
            print(f"끝: {jid} — 소리 {n}개 (done.json 의 status 가 failure 여도 Post 캐시 단계만 실패한 경우가 많다 — 파일 수로 확인)")
            return
        time.sleep(every)
    sys.exit(f"{limit}초 안에 안 끝났어요 — gh run list -R codingfinance473/dori-voice 로 확인")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "make":
        takes, note, trailer, ids, i, dry = 4, "", "", [], 2, False
        while i < len(a):
            if a[i] == "--takes": takes = int(a[i + 1]); i += 2
            elif a[i] == "--note": note = a[i + 1]; i += 2
            elif a[i] == "--trailer": trailer = a[i + 1]; i += 2
            elif a[i] == "--dry": dry = True; i += 1
            else: ids.append(a[i]); i += 1
        make(a[1], ids, takes, note, trailer, dry)
    elif a[0] == "wait": wait(a[1])
    else: sys.exit(__doc__)
