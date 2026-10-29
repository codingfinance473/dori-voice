#!/usr/bin/env python3
"""run.py — 한 편을 처음부터 끝까지.

  python3 run.py <에피소드 폴더> preview   (증거 검사) → 계산 → 목소리 → 정지 화면 → 화면 숫자 점검(먼저 눈으로 확인)
  python3 run.py <에피소드 폴더> all       계산 → 목소리 → 정지 화면 → 화면 숫자 점검 → 가림 영역 → 소리 → 영상 → 합치기 → 점검
  python3 run.py <에피소드 폴더> video     (목소리·시간표는 그대로) 정지 화면 → 화면 숫자 점검 → … → 점검

웹 조사 편(verify strict)은 증거 검사를 통과하지 못하면 계산부터 멈춘다. 영상 렌더는 화면 숫자 점검을 통과하고
증거가 아직 유효(확인 후 24시간 안)할 때만 한다.
"""
import json, subprocess, sys, time
from pathlib import Path

S = Path(__file__).resolve().parent


def step(name, *args, must=True):
    t = time.time(); print(f"\n== {name} ==", flush=True)
    r = subprocess.run([sys.executable, *map(str, args)])
    if r.returncode and must:
        sys.exit(f"{name} 실패(코드 {r.returncode}) — 위 메시지를 보고 고친 뒤 다시")
    print(f"({time.time() - t:.0f}초)", flush=True)
    return r.returncode == 0


def main(ep, mode):
    ep = Path(ep).resolve()
    e = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    strict = (e.get("verify") or ("strict" if e.get("mode", "web") == "web" else "receipt")) == "strict"
    if mode in ("preview", "all"):
        if strict:
            step("증거 검사", S / "evidence.py", "check", ep)
        step("검산 계산", S / "calc.py", ep / "episode.json")
        step("목소리·시간표", S / "voice.py", ep)
    step("페이지 준비", S / "render.py", ep, "prep")
    step("정지 화면", S / "render.py", ep, "stills")
    ok = step("화면 숫자 점검", S / "render.py", ep, "audit", must=(mode != "preview"))
    if mode == "preview":
        print(f"\n정지 화면: {ep/'build'/'stills'/'sheet.png'} · 받아쓰기: {ep/'build'/'voice_check.md'} · 대조표: {ep/'facts.md'}"
              + ("" if ok else " · 화면 숫자 점검 실패 — build/audit.json"))
        return
    step("가림 영역 점검", S / "render.py", ep, "boxes")
    step("소리", S / "audio.py", ep)
    step("영상 렌더", S / "render.py", ep, "video")
    step("합치기", S / "render.py", ep, "mux")
    step("점검·업로드 꾸러미", S / "qa.py", ep)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "all")
