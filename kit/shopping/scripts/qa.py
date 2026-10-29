#!/usr/bin/env python3
"""qa.py — 완성 영상 점검 + 업로드 꾸러미.

  python3 qa.py <에피소드 폴더>

1) 완성 MP4에서 단계마다 프레임을 다시 뽑아 한 장(build/qa/sheet.png)으로 모은다 — 화면 숫자를 facts.md 와 눈으로 대조
2) 길이·해상도·음량(통합 LUFS, 최대 dBFS) 확인
3) 참고 프레임(build/qa/thumb.png): 첫 '현지 이득' 도장 직후 — 올릴 썸네일은 키트 thumb.html(칩 '가격 검산')로 안 잘리게 1장 만든다
4) 정확성: 가격 검증(strict 증거), 화면 숫자 점검(build/audit.json), 증거 유효 시간(확인 후 24시간), 받아쓰기 숫자(목소리만 + 배경음을 깐 완성 믹스)
5) out/upload.md: 제목 앞 광고 표시, 설명 첫 줄 광고 문구, 상품 태그 목록, 검산 기준(확인 시각·환율 고시일) — 제목 1개·설명 요약·해시태그는 Claude가 채운다
"""
import datetime as dt
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def ff_frame(src, t, dst):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", str(dst)], check=True)


def main(epdir):
    ep_dir = Path(epdir).resolve()
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    mp4 = sorted((ep_dir / "out").glob("*.mp4"))[-1]
    qd = ep_dir / "build" / "qa"; qd.mkdir(parents=True, exist_ok=True)
    for p in qd.glob("f_*.png"):
        p.unlink()
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate,codec_name",
                                       "-of", "json", str(mp4)], capture_output=True, text=True).stdout)
    dur = float(probe["format"]["duration"]); v = [s for s in probe["streams"] if s.get("width")][0]
    times = [1.5]
    for sc in tl["scenes"]:
        ss = tl["steps"].get(sc["id"], {})
        last = max(ss.values()) if ss else sc["t0"] + 1
        times.append(min(sc["t1"] - 0.3, last + 0.7))
    times.append(dur - 0.5)
    for t in times:
        ff_frame(mp4, t, qd / f"f_{t:06.2f}.png")
    from PIL import Image
    fs = sorted(qd.glob("f_*.png")); s = 0.3; W, H = int(1080 * s), int(1920 * s); cols = 4; rows = (len(fs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W + (cols + 1) * 12, rows * H + (rows + 1) * 12), "white")
    for i, f in enumerate(fs):
        r, c = divmod(i, cols); sheet.paste(Image.open(f).resize((W, H)), (12 + c * (W + 12), 12 + r * (H + 12)))
    sheet.save(qd / "sheet.png")
    # 썸네일 후보
    th = None
    for f in facts["items"]:
        st = tl["steps"].get("item:" + f["id"], {}).get("stamp")
        if st and f["verdict"] == "local":
            th = st + 0.55; break
    th = th or times[min(2, len(times) - 1)]
    ff_frame(mp4, th, qd / "thumb.png")
    # 음량
    import numpy as np, soundfile as sf, pyloudnorm as pyln
    x, sr = sf.read(ep_dir / "build" / "mix.wav")
    lu = pyln.Meter(sr).integrated_loudness(x); pk = 20 * np.log10(np.max(np.abs(x)) + 1e-9)
    ok = []
    ok.append(("길이 60초 이하", dur <= 60.5, f"{dur:.1f}s"))
    ok.append(("1080×1920 · 30fps", v["width"] == 1080 and v["height"] == 1920 and v["r_frame_rate"] == "30/1", f"{v['width']}×{v['height']} {v['r_frame_rate']}"))
    ok.append(("통합 음량 -16~-14 LUFS", -16.2 <= lu <= -13.8, f"{lu:.1f} LUFS"))
    ok.append(("최대 -1 dBFS 이하", pk <= -0.9, f"{pk:.1f} dBFS"))
    ok.append(("예시 데이터 아님", not facts.get("sample"), "예시 데이터 — 올리지 않는다" if facts.get("sample") else "실데이터"))
    ok.append(("facts 경고 없음", not facts["warnings"], "; ".join(facts["warnings"]) or "-"))
    vc = (ep_dir / "build" / "voice_check.md").read_text(encoding="utf-8")
    unheard = [l for l in vc.splitlines() if "안 들림" in l and "승인" not in l]
    ok.append(("받아쓰기 숫자 확인", not unheard, "voice_check.md 참고" + (f" — {len(unheard)}줄" if unheard else "")))
    try:   # 완성 믹스(배경음·효과음을 깐 소리)에서도 숫자가 들리는지 — 안 들리면 사람이 듣고 voice.accept
        import voice as VOICE
        mixbad = VOICE.mix_number_check(ep_dir)
    except Exception as e:  # noqa: BLE001
        mixbad = [("?", [f"검사 실패: {e}"[:80]], "")]
    ok.append(("배경음 위 숫자 받아쓰기", not mixbad,
               "숫자 든 줄 모두 들림" if not mixbad else "; ".join(f"{b[0]} '{'·'.join(b[1])}' 안 들림('{b[2]}')" for b in mixbad)
               + " — 들어 보고 맞으면 episode.json voice.accept 에 줄 번호, 아니면 문장·속도를 바꿔 다시"))
    au = ep_dir / "build" / "audit.json"
    a = json.loads(au.read_text(encoding="utf-8")) if au.exists() else {"ok": False, "numbers_seen": 0}
    ok.append(("화면 숫자 점검(근거 없는 숫자 0개·카드=facts)", a["ok"], f"숫자 {a.get('numbers_seen', 0)}개 확인" if a["ok"] else "build/audit.json 참고"))
    left_h = None
    if facts.get("verify") == "strict":
        import evidence
        v = evidence.verify(ep_dir, float(ep.get("max_age_h", 24)), write=False)
        if v.get("time_basis"):
            first_item_last = min(x[s_]["last"] for x in v["items"].values() for s_ in ("local", "kr") if s_ in x)
            left_h = float(ep.get("max_age_h", 24)) - (dt.datetime.now(dt.timezone.utc) - evidence.parse_t(first_item_last)).total_seconds() / 3600
        ok.append(("가격 검증(증거 규칙 통과)", v["ok"] and v["digest"] == facts.get("evidence_digest"),
                   f"증거 {facts.get('evidence_digest')} · 남은 시간 {left_h:.1f}시간" if v["ok"] and left_h is not None else "; ".join(v["errors"])[:200]))
    elif facts.get("mode", "web") == "web":
        ok.append(("가격 검증(증거 규칙 통과)", False, "검증 전(draft) — 올리지 않는다"))
    print("점검 결과")
    for name, good, val in ok:
        print(f"- [{'통과' if good else '확인'}] {name}: {val}")
    print(f"프레임 모음: {qd/'sheet.png'} · 참고 프레임: {qd/'thumb.png'} ({th:.1f}s) — 썸네일은 키트 thumb.html 로 1장")
    # 업로드 꾸러미(뼈대) — 제목 1개·요약·해시태그는 Claude가 채운다. 다시 렌더해도 같은 증거(같은 숫자)면 채운 칸을 그대로 둔다
    import hashlib, re
    dig = facts.get("evidence_digest") or hashlib.md5(json.dumps(facts["items"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    keep = {}
    old = ep_dir / "out" / "upload.md"
    if old.exists():
        prev = old.read_text(encoding="utf-8"); L_ = prev.splitlines()
        m = re.search(r"<!-- facts (\S+) -->", prev)
        if m and m.group(1) == dig:
            ti = next((k for k, l in enumerate(L_) if l.startswith("## 제목")), None)
            if ti is not None:
                t1 = L_[ti + 1].strip() if ti + 1 < len(L_) else ""
                if t1 and t1 != "[광고]":
                    keep["title"] = t1
            di = next((k for k, l in enumerate(L_) if l == "## 설명"), None); bi = next((k for k, l in enumerate(L_) if l == "검산 기준"), None)
            if di is not None and bi is not None:
                body = [l for l in L_[di + 1:bi] if l.strip() and not l.startswith("광고 · ")]
                if body and body != ["(검산 요약 2~3줄)"]:
                    keep["summary"] = body
            hi = next((k for k, l in enumerate(L_) if l.startswith("## 해시태그")), None)
            if hi is not None and hi + 1 < len(L_) and L_[hi + 1].strip() not in ("", "#"):
                keep["tags"] = L_[hi + 1].strip()
    tags = [f for f in facts["items"] if f.get("kr_taggable")]
    ad = bool(tags)
    web = facts.get("mode", "web") == "web"
    pre = "[광고] " if ad else ""
    loc = sorted({s_["name"] for s_ in facts["sources"] if s_["kind"] == "현지 가격"})
    krs = sorted({s_["name"] for s_ in facts["sources"] if s_["kind"] == "한국 가격"})
    up = [f"# 업로드 꾸러미 — {facts['title']}", "",
          f"## 제목 (1개{', 맨 앞 [광고] 유지' if ad else ''} — 답·판정은 쓰지 않는다)", keep.get("title") or pre, "",
          "## 설명"]
    if ad:
        up += ["광고 · 이 영상의 상품 태그로 구매하면 채널이 판매 수수료를 받습니다.", ""]
    pt = facts.get("price_time") or {}
    when = (f"{pt['first_kst']}~{pt['last_kst'][11:]}" if pt.get("first_kst") and pt["first_kst"][:10] == pt["last_kst"][:10]
            else f"{pt.get('first_kst', '')}~{pt.get('last_kst', '')}") if pt.get("first_kst") else facts.get("check_date", "")
    up += [*(keep.get("summary") or ["(검산 요약 2~3줄)"]), "",
           "검산 기준",
           "- 가격: " + " · ".join((loc if web else []) + krs) + f" · 정가(세금 포함, 쿠폰·할인 제외) · {when} (한국 시간) 확인",
           f"- 환율: {facts['rate_card']} ({facts.get('rate_source') or facts['rate_basis']}, {facts['rate_date']} 고시) — 원화는 이 환율로 {facts.get('round_krw', 1)}원 단위 환산, 카드 결제액은 카드사 환율·수수료로 달라요",
           f"- 판정: 한국 가격 대비 {facts['thresholds']['local_win']}% 이하 현지 이득, +{facts['thresholds']['kr_win']}% 이상 그냥 한국에서",
           "가격은 확인 시각 기준이며 이후 바뀔 수 있어요.",
           "영상 속 목소리는 AI로 만들었어요. 캐릭터 도리는 그림이에요.", "",
           "출처"]
    up += [f"- {s_['kind']}: {s_['name']} ({s_['date']}) {s_['url']}" for s_ in facts["sources"]]
    up += ["", "## 해시태그 (5개)", keep.get("tags", "#"), "",
           "## 상품 태그 (유튜브 스튜디오 → 수익 창출 → 쇼핑에서 직접 연결)"]
    for f in facts["items"]:
        if f.get("kr_taggable"):
            up.append(f"- {f['name']} — {f['kr_seller']} ({f['kr_checked']} 확인가 {f.get('kr_card', '')}) · 판정 {f['stamp']}")
        else:
            up.append(f"- {f['name']} — 태그 없음 ({f['stamp']})")
    if not ad:
        up.append("  (태그가 없으면 광고 표시도 넣지 않는다. 나중에 태그를 붙이면 제목 앞 [광고]·설명 첫 줄·화면 표시가 필요하다 → 다시 렌더)")
    up += ["", "## 올리기 전 확인",
           "- [ ] 화면의 숫자가 facts.md 와 같다(프레임 모음으로 확인)",
           "- [ ] 올리기 직전 qa 결과 '가격 검증'이 통과이고 남은 시간이 있다(24시간이 지났으면 증거를 다시 읽고 calc부터)",
           "- [ ] 화면 숫자 점검·받아쓰기 숫자 확인이 통과다",
           "- [ ] 설명란에 AI 목소리 문구와 출처 주소가 있다",
           "- [ ] 썸네일 1장을 키트 thumb.html 로 만들고 thumb_check.png(4:5·1:1·3:2)에서 제목·핵심 그림이 다 보인다",
           "- [ ] 지난 편과 주제·가게·반전이 다르다",
           "- [ ] 업로드 화면의 '변경·합성 콘텐츠' 표시 기준을 확인했다(만화 캐릭터·합성 음성)"]
    if ad:
        up += ["- [ ] 제목 맨 앞 [광고], 설명 첫 줄 광고 문구가 있다",
               "- [ ] 태그한 상품이 영상 속 품목과 같은 제품·용량이다"]
    if not web:
        up += ["- [ ] 영수증 사진의 카드번호·승인번호·회원번호를 가렸다"]
    up += ["", f"<!-- facts {dig} -->"]
    (ep_dir / "out" / "upload.md").write_text("\n".join(up) + "\n", encoding="utf-8")
    print(f"업로드 꾸러미: {ep_dir/'out'/'upload.md'}" + (" (같은 증거라 채운 제목·요약·해시태그를 유지)" if keep else ""))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
