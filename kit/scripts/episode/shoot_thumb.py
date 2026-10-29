"""썸네일 1장(thumbnail.jpg, 1080×1920)과 잘림 점검 그림(thumb_check.png)을 만든다.
  python3 shoot_thumb.py [이름.jpg]
점검 그림: UI 가림 표시판 + 가운데 4:5 · 1:1 · 3:2 자르기 — 세 장 모두에서 제목과 핵심 그림이 다 보여야 통과."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

H = Path(__file__).resolve().parent
name = sys.argv[1] if len(sys.argv) > 1 else "thumbnail.jpg"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--font-render-hinting=none"])
    for g, out in (("0", H / name), ("1", H / "_thumb_guide.png")):
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto((H / "thumb.html").as_uri() + f"?guide={g}"); pg.wait_for_function("window.__ready===true")
        pg.screenshot(path=str(out), type="jpeg" if out.suffix == ".jpg" else "png", **({"quality": 92} if out.suffix == ".jpg" else {}))
        pg.close()
    b.close()
im = Image.open(H / name)
crops = {"4:5": (0, 285, 1080, 1635), "1:1": (0, 420, 1080, 1500), "3:2": (0, 600, 1080, 1320)}
row = [Image.open(H / "_thumb_guide.png").resize((270, 480))] + [im.crop(c).resize((270, int(270 * (c[3] - c[1]) / 1080))) for c in crops.values()]
W = Image.new("RGB", (270 * 4 + 60, 480), "white"); x = 0
for r in row: W.paste(r, (x, (480 - r.height) // 2)); x += r.width + 20
W.save(H / "thumb_check.png")
print("썸네일:", H / name, f"{(H / name).stat().st_size // 1024}KB", "| 점검:", H / "thumb_check.png")
