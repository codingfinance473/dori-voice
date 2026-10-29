#!/usr/bin/env python3
"""render.py — 화면 만들기·정지 화면·영상 렌더.

  python3 render.py <에피소드 폴더> prep              재료 정리 + 페이지(build/web) 만들기
  python3 render.py <에피소드 폴더> stills [초 ...]    정지 화면 PNG(build/stills) — 초를 안 주면 단계마다 자동
  python3 render.py <에피소드 폴더> video             build/frames 없이 바로 MP4(build/video_noaudio.mp4)
  python3 render.py <에피소드 폴더> mux               build/mix.wav 와 합쳐 out/<제목>.mp4
  python3 render.py <에피소드 폴더> boxes             글자 칸이 쇼츠 가림 영역에 걸리는지 점검
  python3 render.py <에피소드 폴더> audit             화면 숫자 점검 — 0.2초마다 보이는 글자의 숫자가 모두 facts·선언된 제도 숫자에서
                                                     왔는지, 품목 카드 값이 facts 와 글자 그대로 같은지 → build/audit.json
영상(video)은 audit 통과 + (strict) 증거가 아직 유효(기본 24시간)할 때만 만든다.
"""
import hashlib, json, os, re, shutil, subprocess, sys, math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

SKILL = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "receipt-shorts"
W, H, FPS = 1080, 1920, 30
SAFE = {"top": 150, "bottom": 1500, "right": 920}


def media_prep(ep_dir, ep, web):
    md = web / "media"; md.mkdir(parents=True, exist_ok=True)
    out = {"items": {}, "receipt": None}

    def photo(src, dst):
        from PIL import Image, ImageOps
        try:
            import pillow_heif; pillow_heif.register_heif_opener()
        except Exception:
            pass
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.thumbnail((1600, 1600)); im.save(dst, quality=90)
    rc = (ep.get("receipt") or {}).get("path")
    if rc:
        photo(ep_dir / rc, md / "receipt.jpg"); out["receipt"] = "media/receipt.jpg"
        from PIL import Image
        out["receipt_wh"] = list(Image.open(md / "receipt.jpg").size)
    for it in ep["items"]:
        m = it.get("media") or {"type": "none"}
        if m.get("type") == "photo":
            dst = md / f"{it['id']}.jpg"; photo(ep_dir / m["path"], dst)
            out["items"][it["id"]] = {"type": "photo", "src": f"media/{it['id']}.jpg"}
        elif m.get("type") == "video":
            fd = md / it["id"]; shutil.rmtree(fd, ignore_errors=True); fd.mkdir()
            dur = m.get("dur", 6)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(m.get("start", 0)), "-t", str(dur), "-i", str(ep_dir / m["path"]),
                            "-vf", f"fps={FPS},scale=1080:-2", "-q:v", "4", str(fd / "%04d.jpg")], check=True)
            frames = sorted(p.name for p in fd.glob("*.jpg"))
            out["items"][it["id"]] = {"type": "video", "frames": [f"media/{it['id']}/{f}" for f in frames]}
        else:
            out["items"][it["id"]] = {"type": "none"}
    return out


def prep(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    web = ep_dir / "build" / "web"; web.mkdir(parents=True, exist_ok=True)
    for f in ("engine.html", "dori.js"):
        shutil.copy(SKILL / "assets" / f, web / f)
    fdir = web / "fonts"
    if not fdir.exists():
        src = SKILL / "assets" / "fonts" if (SKILL / "assets" / "fonts" / "Pretendard-Bold.woff2").exists() else CACHE / "fonts"
        shutil.copytree(src, fdir, ignore=shutil.ignore_patterns("*.txt"))
    media = media_prep(ep_dir, ep, web)
    lean = {**tl, "lines": [{k: v for k, v in l.items() if k != "wav"} for l in tl["lines"]]}
    # '알아 둘 점' 카드: 글 속 {id.필드} 자리를 facts 값으로 채운다
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from voice import fill
    notes = {}
    for key, n in (ep.get("notes") or {}).items():
        notes[key] = {**n, "title": fill(n.get("title", ""), facts), "sticker": n.get("sticker", "알아 둘 점"),
                      "items": [{"text": fill(i.get("text", ""), facts), "small": fill(i.get("small", ""), facts)} for i in n.get("items", [])]}
    (web / "data.js").write_text("window.DATA=" + json.dumps({"episode": ep, "facts": facts, "timeline": lean, "media": media, "notes": notes},
                                                            ensure_ascii=False) + ";", encoding="utf-8")
    (web / "prep.json").write_text(json.dumps({"facts_sha": _sha(ep_dir / "facts.json"), "timeline_sha": _sha(ep_dir / "build" / "timeline.json"),
                                               "episode_sha": _sha(ep_dir / "episode.json")}), encoding="utf-8")
    print(f"페이지 준비: {web/'engine.html'}")
    return web, tl


def _page(pw):
    b = pw.chromium.launch(args=["--disable-gpu", "--font-render-hinting=none"])
    pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    return b, pg


def _open(pg, web):
    pg.goto((web / "engine.html").as_uri())
    pg.wait_for_function("window.render && window.__ready")
    pg.evaluate("window.__ready()")
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    return errs


def stills(ep_dir, times=None):
    from playwright.sync_api import sync_playwright
    ep_dir = Path(ep_dir).resolve(); web = ep_dir / "build" / "web"
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    if not times:
        times = [0.3, 2.0]
        for sc in tl["scenes"]:
            ss = tl["steps"].get(sc["id"], {})
            last = max(ss.values()) if ss else sc["t0"] + 1
            times.append(round(min(sc["t1"] - .35, last + 1.0), 2))
        times.append(round(tl["duration"] - .4, 2))
    out = ep_dir / "build" / "stills"; shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
    with sync_playwright() as pw:
        b, pg = _page(pw); errs = _open(pg, web)
        for t in times:
            pg.evaluate(f"render({t})"); pg.evaluate("window.__ready()")
            pg.screenshot(path=str(out / f"t{t:06.2f}.png"))
        b.close()
    # 한 장에 모아 보기
    from PIL import Image
    ims = [Image.open(p) for p in sorted(out.glob("t*.png"))]
    cols = 4; rows = math.ceil(len(ims) / cols); s = 0.25
    sheet = Image.new("RGB", (int(W * s) * cols + 10 * (cols + 1), int(H * s) * rows + 10 * (rows + 1)), "white")
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        sheet.paste(im.resize((int(W * s), int(H * s))), (10 + c * (int(W * s) + 10), 10 + r * (int(H * s) + 10)))
    sheet.save(out / "sheet.png")
    print(f"정지 화면 {len(ims)}장: {out}/sheet.png", "· 페이지 오류: " + "; ".join(errs) if errs else "")


def _chunk(args):
    web, f0, f1, path = args
    from playwright.sync_api import sync_playwright
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), path], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        b, pg = _page(pw); _open(pg, Path(web))
        for f in range(f0, f1):
            pg.evaluate(f"render({f / FPS:.5f})")
            if f % 15 == 0:
                pg.evaluate("window.__ready()")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
        b.close()
    ff.stdin.close(); ff.wait()
    return path


def video(ep_dir, workers=None):
    gate(ep_dir)
    ep_dir = Path(ep_dir).resolve(); web = ep_dir / "build" / "web"
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    n = int(math.ceil(tl["duration"] * FPS)); workers = workers or max(1, os.cpu_count() or 1)
    step = math.ceil(n / workers); parts = []
    for i in range(workers):
        a, b_ = i * step, min(n, (i + 1) * step)
        if a < b_:
            parts.append((str(web), a, b_, str(ep_dir / "build" / f"part{i}.mp4")))
    with ProcessPoolExecutor(len(parts)) as ex:
        done = list(ex.map(_chunk, parts))
    lst = ep_dir / "build" / "parts.txt"; lst.write_text("".join(f"file '{Path(p).name}'\n" for p in done))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(ep_dir / "build" / "video_noaudio.mp4")], check=True)
    for p in done:
        os.remove(p)
    print(f"영상 {n}프레임: {ep_dir/'build'/'video_noaudio.mp4'}")


NUM = re.compile(r"\d+(?:[.,:/]\d+)*")


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def allowed_tokens(ep, facts):
    ok = set()
    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            ok.add(str(v))
        elif isinstance(v, str):
            ok.update(NUM.findall(v))
    walk(facts)
    for l in facts.get("literals") or []:          # strict: 원문 기록으로 확인된 제도 숫자만
        ok.update(NUM.findall(l["text"]))
    if facts.get("verify") != "strict":              # draft·영수증 편: 선언만 된 숫자도 허용(화면에 '검증 전' 표시)
        for l in ep.get("literals") or []:
            ok.update(NUM.findall(l.get("text", "")))
    ok.add(f"{int(ep.get('ep', 0)):02d}"); ok.add(str(ep.get("ep", "")))
    ok.update(str(i) for i in range(1, 11))   # 검산 1·2·3 스티커, 알아 둘 점 번호, '4개' 같은 개수
    return ok


def audit(ep_dir, step=0.2):
    """화면에 보이는 모든 숫자가 facts(또는 선언된 제도 숫자)에서 왔는지, 품목 카드가 facts 와 같은지 본다."""
    from playwright.sync_api import sync_playwright
    ep_dir = Path(ep_dir).resolve(); web = ep_dir / "build" / "web"
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    pj = json.loads((web / "prep.json").read_text(encoding="utf-8")) if (web / "prep.json").exists() else {}
    if pj.get("facts_sha") != _sha(ep_dir / "facts.json") or pj.get("timeline_sha") != _sha(ep_dir / "build" / "timeline.json") \
            or pj.get("episode_sha") != _sha(ep_dir / "episode.json"):
        sys.exit("페이지가 지금 facts·시간표·episode 로 만든 것이 아니다 — render.py prep 부터 다시")
    ok_tok = allowed_tokens(ep, facts)
    stray, rows_bad, seen, covered = {}, [], 0, {}
    want = {f["id"]: {"local": f["local_card"], "krw": f["krw_card"], "kr": f.get("kr_card"), "diff": (f.get("diff_card") or "") + (f.get("pct_card") or "")}
            for f in facts["items"] if f.get("kr_equiv") is not None}
    with sync_playwright() as pw:
        b, pg = _page(pw); errs = _open(pg, web)
        t = 0.0
        while t < tl["duration"]:
            pg.evaluate(f"render({t:.3f})")
            for tx in pg.evaluate("window.__texts()"):
                for tok in NUM.findall(tx["text"]):
                    seen += 1
                    if tok not in ok_tok:
                        stray.setdefault(tok, (round(t, 2), tx["text"][:60]))
            for cv in pg.evaluate("window.__covers()"):
                covered.setdefault((cv["text"], cv["by"]), round(t, 2))
            t += step
        for sc in tl["scenes"]:
            k, _, iid = sc["id"].partition(":")
            if k != "item" or iid not in want:
                continue
            pg.evaluate(f"render({sc['t1'] - 0.35:.3f})")
            got = dict(pg.evaluate("window.__vals()")[sc["id"]])
            for key, exp in want[iid].items():
                if got.get(key, "").replace(" ", "") != (exp or "").replace(" ", ""):
                    rows_bad.append(f"{iid}.{key}: 화면 '{got.get(key)}' ≠ facts '{exp}'")
        b.close()
    res = {"ok": not stray and not rows_bad and not errs and not covered,
           "covered": [{"text": k[0], "by": k[1], "t": v} for k, v in covered.items()], "facts_sha": _sha(ep_dir / "facts.json"), "timeline_sha": _sha(ep_dir / "build" / "timeline.json"),
           "engine_sha": _sha(web / "engine.html"), "numbers_seen": seen, "stray": [{"token": k, "t": v[0], "text": v[1]} for k, v in stray.items()],
           "rows_bad": rows_bad, "page_errors": errs, "verified": facts.get("verified")}
    (ep_dir / "build" / "audit.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if res["ok"]:
        print(f"화면 숫자 점검: 통과 (숫자 {seen}개 확인, 품목 카드 {len(want)}개 facts 와 일치)")
    else:
        print("화면 숫자 점검: 실패")
        for x in res["stray"]:
            print(f"- 근거 없는 숫자 '{x['token']}' ({x['t']}s): {x['text']}")
        for x in rows_bad:
            print("- " + x)
        for x in res["covered"]:
            print(f"- 숫자가 가려짐 ({x['t']}s): '{x['text']}' ← {x['by']}")
        for x in errs:
            print("- 페이지 오류: " + x)
    return res["ok"]


def gate(ep_dir):
    """영상 렌더 전 관문: 화면 숫자 점검 통과, 같은 facts·시간표, (strict) 증거가 아직 유효."""
    ep_dir = Path(ep_dir).resolve()
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    ap = ep_dir / "build" / "audit.json"
    if not ap.exists():
        sys.exit("영상 전에 화면 숫자 점검(render.py audit)을 먼저 한다")
    a = json.loads(ap.read_text(encoding="utf-8"))
    if not a["ok"]:
        sys.exit("화면 숫자 점검이 실패한 상태다 — build/audit.json")
    if a["facts_sha"] != _sha(ep_dir / "facts.json") or a["timeline_sha"] != _sha(ep_dir / "build" / "timeline.json") \
            or a["engine_sha"] != _sha(ep_dir / "build" / "web" / "engine.html"):
        sys.exit("점검 뒤에 facts·시간표·페이지가 바뀌었다 — prep·audit 를 다시 한다")
    if facts.get("verify") == "strict":
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import evidence
        ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
        v = evidence.verify(ep_dir, float(ep.get("max_age_h", 24)), write=False)
        if not v["ok"]:
            sys.exit("증거가 더는 유효하지 않다(시간 초과 등) — 다시 읽고 calc 부터:\n - " + "\n - ".join(v["errors"]))
        if v["digest"] != facts.get("evidence_digest"):
            sys.exit("계산 뒤에 증거 기록이 바뀌었다 — calc 부터 다시 한다")
    elif facts.get("verified") is False:
        print("주의: 검증 전(draft) 영상 — 화면에 '검증 전 · 올리지 마세요'가 찍힌다")


def mux(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    od = ep_dir / "out"; od.mkdir(exist_ok=True)
    name = f"EP{int(ep.get('ep', 0)):02d}_{ep.get('place', '')}_{ep.get('store', '')}".replace(" ", "_").replace("/", "_") + ("_예시" if ep.get("sample") else "") + ".mp4"
    out = od / name
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(ep_dir / "build" / "video_noaudio.mp4"), "-i", str(ep_dir / "build" / "mix.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print(f"완성: {out}")


def boxes(ep_dir):
    from playwright.sync_api import sync_playwright
    ep_dir = Path(ep_dir).resolve(); web = ep_dir / "build" / "web"
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    bad = {}
    with sync_playwright() as pw:
        b, pg = _page(pw); _open(pg, web)
        t = 0.0
        while t < tl["duration"]:
            pg.evaluate(f"render({t})")
            for bx in pg.evaluate("window.__boxes()"):
                why = []
                if bx["y0"] < SAFE["top"]:
                    why.append("위")
                if bx["y1"] > SAFE["bottom"] + 2:
                    why.append("아래")
                if bx["x1"] > SAFE["right"] + 2:
                    why.append("오른쪽")
                if why:
                    bad.setdefault((bx["text"], "·".join(why)), t)
            t += 0.2
        b.close()
    if bad:
        print("가림 영역에 걸린 글자:")
        for (txt, w), t in bad.items():
            print(f"- {t:5.1f}s {w}: {txt}")
    else:
        print("가림 영역 점검: 통과")
    return not bad


if __name__ == "__main__":
    d, cmd = sys.argv[1], sys.argv[2]
    if cmd == "prep":
        prep(d)
    elif cmd == "stills":
        stills(d, [float(x) for x in sys.argv[3:]])
    elif cmd == "video":
        video(d)
    elif cmd == "mux":
        mux(d)
    elif cmd == "boxes":
        sys.exit(0 if boxes(d) else 1)
    elif cmd == "audit":
        sys.exit(0 if audit(d) else 1)
    elif cmd == "gate":
        gate(d); print("관문 통과")
