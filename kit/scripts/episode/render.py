"""퀴즈 쇼츠 렌더러: index.html 의 render(t) 를 프레임마다 호출해 캡처하고 ffmpeg 로 MP4 를 만든다.

사용:
  python3 render.py stills 1.2 3.8 ...        # 지정 시각 PNG 를 stills/ 에 저장
  python3 render.py video out.mp4 mix.wav     # 전체(두 구간 병렬 렌더 후 이어 붙임). 길이는 timeline.js 의 T.END
  python3 render.py qa                        # ★ 렌더 전 자동 점검(필수): 눈·옷·손 소품·움직임·글자(안전 영역·겹침·잘림·도리와 겹침) + 훑어보기 시트
                                              #   통과 못 하면 video 를 돌리지 않는다. stills/qa_sheet.png · qa_flags.png · eyes_sheet.png 를 Claude 가 직접 열어 본다
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
                if d > 0.45: jumps.append((round(t, 2), round(d, 2)))
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


# ---------------- 렌더 전 자동 점검 ----------------
FRAME_JS = """(t)=>{render(t);const r={eyes:[]};document.querySelectorAll('#dori [id^=dEye]').forEach(g=>{
  r.eyes.push([...g.querySelectorAll('.open,.shut,.happy,.sq')].map(e=>+(e.getAttribute('opacity')??1)));});
  const eo=document.querySelector('#dori #dEyeL .open');if(eo){const m=(eo.getAttribute('transform')||'').match(/scale\\(([\\d.]+)[ ,]+([\\d.]+)\\)/);r.eyeV=(+(eo.getAttribute('opacity')??1)>.5&&m)?+m[2]:null;}
  r.e=typeof expr==='function'?expr(t):{};const d=window.__dst||{};r.d={armL:d.armL||0,armR:d.armR||0,tilt:d.tilt||0,hop:d.hop||0};
  // 손 소품이 눈을 가리는지(눈 상자와 겹친 넓이 비율)
  r.prop=0;const eb=[...document.querySelectorAll('#dori [id^=dEye]')].map(e=>e.getBoundingClientRect());
  document.querySelectorAll('#dori .hand .hold').forEach(h=>{const b=h.getBoundingClientRect();if(!b.width)return;for(const e of eb){
    const ov=Math.max(0,Math.min(b.right,e.right)-Math.max(b.left,e.left))*Math.max(0,Math.min(b.bottom,e.bottom)-Math.max(b.top,e.top));r.prop=Math.max(r.prop,ov/(e.width*e.height));}});
  return r;}"""
LAYOUT_JS = """()=>{
  const W=1080,H=1920,vis=e=>{for(let n=e;n&&n!==document.documentElement;n=n.parentElement){const cs=getComputedStyle(n);
    if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity<.5)return false;}return true;};
  const name=e=>(e.id?'#'+e.id:'')||((e.className&&typeof e.className==='string')?'.'+e.className.split(' ')[0]:e.tagName.toLowerCase());
  const txt=[];
  for(const e of document.querySelectorAll('body *')){
    if(e.closest('svg,script,style')||e.id==='pre')continue;
    if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;
    if(!vis(e))continue;
    const rg=document.createRange();rg.selectNodeContents(e);const b=rg.getBoundingClientRect();
    if(b.width<4||b.height<4)continue;
    if(b.right<0||b.left>W||b.bottom<0||b.top>H)continue;
    txt.push({e,n:name(e),t:e.textContent.trim().slice(0,14),b:{x:b.left,y:b.top,w:b.width,h:b.height}});}
  const out=[],inter=(a,b)=>Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x))*Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
  for(const a of txt){const b=a.b;
    if(b.x<-2||b.y<-2||b.x+b.w>W+2||b.y+b.h>H+2)out.push({k:'화면 밖',m:`${a.n} "${a.t}"`,b});
    else if(b.y+b.h>H-420||b.x+b.w>W-160)out.push({k:'안전 영역 밖(아래 420·오른쪽 160)',m:`${a.n} "${a.t}"`,b});
    if((a.e.scrollWidth>a.e.clientWidth+2||a.e.scrollHeight>a.e.clientHeight+2)&&getComputedStyle(a.e).overflow!=='visible'){out.push({k:'글자 잘림',m:`${a.n} "${a.t}"`,b});continue;}
    for(let p=a.e.parentElement;p&&p!==document.body;p=p.parentElement){const cs=getComputedStyle(p);
      if(cs.overflow!=='visible'||cs.overflowX!=='visible'){const r=p.getBoundingClientRect();
        if(b.x<r.left-2||b.y<r.top-2||b.x+b.w>r.right+2||b.y+b.h>r.bottom+2){out.push({k:'글자 잘림',m:`${a.n} "${a.t}"`,b});}break;}}}
  for(let i=0;i<txt.length;i++)for(let j=i+1;j<txt.length;j++){const A=txt[i],B=txt[j];
    if(A.e.contains(B.e)||B.e.contains(A.e))continue;const ov=inter(A.b,B.b);
    if(ov>.2*Math.min(A.b.w*A.b.h,B.b.w*B.b.h))out.push({k:'글자끼리 겹침',m:`${A.n} "${A.t}" ↔ ${B.n} "${B.t}"`,b:A.b,b2:B.b});}
  const dh=document.querySelector('#dori #dPouchStroke');if(dh){const r=dh.getBoundingClientRect(),D={x:r.left+r.width*.06,y:r.top+r.height*.04,w:r.width*.88,h:r.height*.92};   // 도리 몸 윤곽(옷의 자르기용 큰 사각형은 빼고)
    for(const a of txt){if(a.e.closest('#bub'))continue;const ov=inter(a.b,D);if(ov>.08*a.b.w*a.b.h)out.push({k:'도리와 글자 겹침',m:`${a.n} "${a.t}"`,b:a.b,b2:D});}}
  return out;}"""


def qa():
    """렌더 전 자동 점검. 문제가 하나라도 있으면 코드 1 — 고치고 다시 돌린다(사람이 일일이 보지 않아도 되게)."""
    import re
    n = int(FPS * DUR); probs = {}; prev = None; flat_run = 0
    def add(k, t, m, box=None):
        probs.setdefault(k, []).append((round(t, 2), m, box))
    with sync_playwright() as p:
        b, pg = open_page(p)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        # 1) 옷: 눈·코·입 가림, 장갑 두 팔, 크로스백 숨김
        for m in pg.evaluate("Dori.check?Dori.check():[]"): add("옷", 0, m)
        outfit = pg.evaluate("typeof OUTFIT!=='undefined'?OUTFIT:''")
        th = HERE / "thumb.html"
        if th.exists():
            mm = re.search(r"outfit:'([^']*)'", th.read_text(encoding="utf-8"))
            if (mm.group(1) if mm else "") != outfit: add("옷", 0, f"썸네일 CFG.outfit('{mm.group(1) if mm else ''}')이 영상 OUTFIT('{outfit}')과 다름")
        for i in range(n):
            t = i / FPS; r = pg.evaluate(FRAME_JS, t)
            # 2) 눈: 한 눈에 모양 하나, 반투명 없음
            for vis in r["eyes"]:
                if len([v for v in vis if v > .001]) != 1 or any(.001 < v < .999 for v in vis): add("눈 겹침·반투명", t, "눈 모양이 둘 이상 보이거나 반투명"); break
            # 2-1) 납작한 눈(2026-11-11): 뜬 눈이 세로로 눌린 채(.22~.85) 0.25초 넘게 머물면 — 깜빡임·전환은 짧아서 안 걸린다
            ev = r.get("eyeV"); sv = (ev / (1 + .14 * r["e"].get("surprise", 0))) if ev is not None else 1
            flat_run = (flat_run + 1) if .22 < sv < .85 else 0
            if flat_run == int(.25 * FPS): add("눈 납작", t, f"뜬 눈이 {sv:.2f}배로 눌린 채 머묾 — 그 시각 EX 의 happy·squint 중간 값(.55~.95)을 0 또는 1로")
            if r.get("prop", 0) > .25: add("소품이 눈을 가림", t, f"손 소품이 눈의 {r['prop']*100:.0f}%를 덮음 — 그 시각 팔(ARMR)을 덜 들거나 소품 없는 옷으로")
            # 3) 움직임: 표정·팔·기울기·점프가 한 프레임에 튀지 않게
            if prev:
                de = max((abs(r["e"].get(k, 0) - prev["e"].get(k, 0)) for k in ("happy", "squint", "surprise", "sad")), default=0)
                if de > .45: add("표정 튐", t, f"표정 값이 한 프레임에 {de:.2f} 바뀜")
                for k, lim in (("armL", .4), ("armR", .4), ("tilt", 3.0), ("hop", 30)):   # 정상 전환의 가장 빠른 순간보다 조금 크게 — 진짜 튐(끊김)만 잡는다
                    dv = abs(r["d"][k] - prev["d"][k])
                    if dv > lim: add("움직임 튐", t, f"{k} 가 한 프레임에 {dv:.2f} 바뀜(한도 {lim})")
            prev = r
            # 4) 글자: 화면 밖·안전 영역·잘림·겹침·도리와 겹침 (0.1초마다)
            if i % 3 == 0:
                for o in pg.evaluate(LAYOUT_JS): add(o["k"], t, o["m"], (o["b"], o.get("b2")))
        for e in errs[:5]: add("스크립트 오류", 0, e)
        keys = sorted({round(k, 2) for k in pg.evaluate("typeof EX!=='undefined'?EX.map(k=>k[0]).filter(x=>isFinite(x)):[]") if 0 < k < DUR})
        out = HERE / "stills"; out.mkdir(exist_ok=True)
        # 훑어보기: 2초마다 한 장씩
        over = []
        for k in range(0, int(DUR) + 1, 2):
            pg.evaluate(f"render({min(k, DUR - .05)})"); f = out / f"_ov{k:03d}.png"; pg.screenshot(path=str(f)); over.append((k, f))
        # 문제 프레임: 종류별 첫 시각(최대 12장) — 문제 상자를 빨갛게
        flagged = []
        for k, lst in probs.items():   # 종류마다 가운데쯤 한 장 + 마지막 한 장(도리가 다 들어온 뒤 장면이 보이게)
            pick = [lst[len(lst) // 2]] + ([lst[-1]] if len(lst) > 1 else [])
            for t, m, box in pick:
                if len(flagged) >= 12: break
                pg.evaluate(f"render({t})"); f = out / f"_fl{len(flagged):02d}.png"; pg.screenshot(path=str(f)); flagged.append((t, k, m, box, f))
        # 눈: 표정 전환 앞뒤
        box = pg.evaluate("(()=>{const r=document.getElementById('dori').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
        eyes_rows = []
        for k in keys[:24]:
            row = []
            for j in range(-2, 8):
                t = max(0, k + j / FPS); pg.evaluate(f"render({t})"); x, y, w, h = box; f = out / f"_ey{k:06.2f}_{j+2:02d}.png"
                pg.screenshot(path=str(f), clip={"x": x + w * .1, "y": y + h * .1, "width": w * .8, "height": h * .5}); row.append((t, f))
            eyes_rows.append(row)
        b.close()
    from PIL import Image, ImageDraw, ImageFont
    fp = next((str(x) for x in [HERE / "fonts" / "Pretendard-Bold.otf", Path.home() / ".cache/dori-shorts/fonts/pretendard/Pretendard-Bold.otf"] if Path(x).exists()), None)
    FONT = ImageFont.truetype(fp, 20) if fp else None
    def grid(items, cols, scale, path, label):
        ims = [Image.open(f).convert("RGB") for *_, f in items]
        if not ims: return
        w, h = int(ims[0].width * scale), int(ims[0].height * scale); pad = 36
        S = Image.new("RGB", (cols * (w + 16) + 16, ((len(ims) + cols - 1) // cols) * (h + pad + 16) + 16), "#FFF6EC"); d = ImageDraw.Draw(S)
        for i, (it, im) in enumerate(zip(items, ims)):
            x, y = 16 + (i % cols) * (w + 16), 16 + (i // cols) * (h + pad + 16)
            im2 = im.copy(); dd = ImageDraw.Draw(im2)
            for bx in (it[3] if len(it) > 4 and it[3] else []):
                if bx: dd.rectangle([bx["x"], bx["y"], bx["x"] + bx["w"], bx["y"] + bx["h"]], outline="#E2483A", width=8)
            S.paste(im2.resize((w, h)), (x, y + pad)); d.text((x, y + 6), label(it), fill="#3E2F25", font=FONT)
        S.save(path)
    grid(over, 6, .2, out / "qa_sheet.png", lambda it: f"{it[0]}s")
    grid(flagged, 3, .3, out / "qa_flags.png", lambda it: f"{it[0]}s {it[1]}")
    if eyes_rows:
        flat = [x for row in eyes_rows for x in row]; grid(flat, 10, 1, out / "eyes_sheet.png", lambda it: f"{it[0]:.2f}s")
    for f in out.glob("_*.png"): f.unlink()
    print(f"렌더 전 점검: {n}프레임 · 옷 '{outfit or '기본'}'")
    if not probs:
        print("  문제 없음 — 그래도 stills/qa_sheet.png(2초마다)와 eyes_sheet.png(표정 전환)를 직접 열어 본다"); print("통과"); return 0
    for k, lst in probs.items():
        ts = sorted({t for t, _, _ in lst}); print(f"  ✗ {k}: {len(ts)}곳 — {lst[0][1]} (시각 {', '.join(map(str, ts[:8]))}{' …' if len(ts) > 8 else ''})")
    print("  stills/qa_flags.png 에 문제 프레임을 빨간 상자로 모았다. 고치고 다시 돌린다. 일부러 그렇게 둔 것이면(예: 글자가 의도적으로 겹치는 장면) 이유를 작업 기록에 적는다.")
    print("확인"); return 1


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(sys.argv[2:])
    elif sys.argv[1] == "eyes":
        sys.exit(eyes())
    elif sys.argv[1] == "qa":
        sys.exit(qa())
    else:
        video(sys.argv[2], sys.argv[3])
