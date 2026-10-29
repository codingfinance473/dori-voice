"""퀴즈 쇼츠 렌더러: index.html 의 render(t) 를 프레임마다 호출해 캡처하고 ffmpeg 로 MP4 를 만든다.

사용:
  python3 render.py stills 1.2 3.8 ...        # 지정 시각 PNG 를 stills/ 에 저장
  python3 render.py video out.mp4 mix.wav     # 전체(두 구간 병렬 렌더 후 이어 붙임). 길이는 timeline.js 의 T.END
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


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2:])
    else:
        video(sys.argv[2], sys.argv[3])
