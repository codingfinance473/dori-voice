"""퀴즈 쇼츠 렌더러: index.html 의 render(t) 를 프레임마다 호출해 캡처하고 ffmpeg 로 MP4 를 만든다.

사용:
  python3 render.py stills 1.2 3.8 ...        # 지정 시각 PNG 를 stills/ 에 저장
  python3 render.py video out.mp4 mix.wav     # 전체(두 구간 병렬 렌더 후 이어 붙임). 길이는 timeline.js 의 T.END
  python3 render.py eyes                      # 도리 눈 점검: 모든 프레임에서 눈 모양이 하나만·반투명 없이 보이는지, 표정 값이 튀지 않는지
                                              #   + 표정이 바뀌는 순간 앞뒤 프레임을 stills/eyes_sheet.png 로 모아 눈으로 확인
"""
import json, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FPS, W, H = 30, 1080, 1920
_tl = (HERE / "timeline.js").read_text(encoding="utf-8")
DUR = json.loads(_tl[_tl.index("{"):_tl.rindex("}") + 1])["T"]["END"]   # 영상 길이 = 마지막 대사 뒤 1.1초


def open_page(p):
    b = p.chromium.launch(args=["--font-render-hinting=none"])
    pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    pg.goto((HERE / "index.html").as_uri())
    pg.wait_for_function("window.__ready === true")
    return b, pg


def stills(times):
    out = HERE / "stills"
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b, pg = open_page(p)
        for t in times:
            pg.evaluate(f"render({float(t)})")
            pg.screenshot(path=str(out / f"t{float(t):05.2f}.png"))
        b.close()
    print("saved", len(times), "stills")


def segment(args):
    i0, i1, dst = args
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
         "-c:v", "png", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-profile:v", "high", "-g", "60", "-r", str(FPS), dst],
        stdin=subprocess.PIPE)
    t0 = time.time()
    with sync_playwright() as p:
        b, pg = open_page(p)
        for i in range(i0, i1):
            pg.evaluate(f"render({i / FPS})")
            ff.stdin.write(pg.screenshot(type="png"))
            if (i - i0) % 300 == 0:
                print(f"[{i0}-{i1}] frame {i}  {time.time() - t0:.0f}s", flush=True)
        b.close()
    ff.stdin.close()
    ff.wait()
    return dst


def video(dst, music):
    n = int(FPS * DUR)
    half = n // 2
    segs = [(0, half, str(HERE / "_seg0.mp4")), (half, n, str(HERE / "_seg1.mp4"))]
    t0 = time.time()
    with ProcessPoolExecutor(2) as ex:
        list(ex.map(segment, segs))
    lst = HERE / "_segs.txt"
    lst.write_text("".join(f"file '{s[2]}'\n" for s in segs))
    silent = HERE / "_video_only.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(silent)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(music),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(dst)], check=True)
    for s in segs:
        Path(s[2]).unlink()
    silent.unlink(); lst.unlink()
    print("done", dst, f"{time.time() - t0:.0f}s")


EYE_JS = """(t)=>{render(t);const r=[];document.querySelectorAll('#dori [id^=dEye]').forEach(g=>{
  const vis=[...g.querySelectorAll('.open,.shut,.happy,.sq')].map(e=>+(e.getAttribute('opacity')??1));
  r.push(vis);});const e=typeof expr==='function'?expr(t):{};return {eyes:r,e};}"""


def eyes():
    """프레임마다 (1) 한 눈에 보이는 모양이 하나뿐이고 0/1 로만 보이는지 (2) 표정 값이 한 프레임에 0.35 넘게 튀지 않는지 본다."""
    n = int(FPS * DUR); bad, jumps, prev = [], [], None
    with sync_playwright() as p:
        b, pg = open_page(p)
        for i in range(n):
            t = i / FPS; r = pg.evaluate(EYE_JS, t)
            for vis in r["eyes"]:
                on = [v for v in vis if v > 0.001]
                if len(on) != 1 or any(0.001 < v < 0.999 for v in vis): bad.append(round(t, 2)); break
            if prev:
                d = max((abs(r["e"].get(k, 0) - prev.get(k, 0)) for k in ("happy", "squint", "surprise", "sad")), default=0)
                if d > 0.35: jumps.append((round(t, 2), round(d, 2)))
            prev = r["e"]
        # 표정이 바뀌는 시각 앞뒤를 모아 본다
        keys = sorted({round(k, 2) for k in pg.evaluate("typeof EX!=='undefined'?EX.map(k=>k[0]).filter(x=>isFinite(x)):[]") if 0 < k < DUR})
        box = pg.evaluate("(()=>{const r=document.getElementById('dori').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
        out = HERE / "stills" / "eyes"; out.mkdir(parents=True, exist_ok=True)
        shots = []
        for k in keys[:24]:
            row = []
            for j in range(-2, 8):
                t = max(0, k + j / FPS); pg.evaluate(f"render({t})")
                x, y, w, h = box; f = out / f"k{k:06.2f}_{j+2:02d}.png"
                pg.screenshot(path=str(f), clip={"x": x + w * .15, "y": y + h * .28, "width": w * .7, "height": h * .3}); row.append((t, f))
            shots.append(row)
        b.close()
    try:
        from PIL import Image, ImageDraw
        if shots:
            w0, h0 = Image.open(shots[0][0][1]).size; S = Image.new("RGB", (w0 * 10, (h0 + 16) * len(shots)), "white"); d = ImageDraw.Draw(S)
            for ri, row in enumerate(shots):
                for ci, (t, f) in enumerate(row):
                    S.paste(Image.open(f), (ci * w0, ri * (h0 + 16) + 16)); d.text((ci * w0 + 3, ri * (h0 + 16) + 2), f"{t:.2f}s", fill="black")
            S.save(HERE / "stills" / "eyes_sheet.png")
    except ImportError:
        pass
    print(f"눈 점검: {n}프레임 — 겹침·반투명 {len(bad)}프레임, 표정 튐 {len(jumps)}곳")
    if bad: print("  겹침·반투명 시각:", bad[:20])
    if jumps: print("  튐(시각, 크기):", jumps[:20])
    print("  표정 전환 모음: stills/eyes_sheet.png (행마다 전환 직전 2프레임 ~ 직후 7프레임)")
    print("통과" if not bad and not jumps else "확인 — 위 시각의 EX·BL 을 고친다")
    return 0 if not bad and not jumps else 1


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2:])
    elif sys.argv[1] == "eyes":
        sys.exit(eyes())
    else:
        video(sys.argv[2], sys.argv[3])
