#!/usr/bin/env python3
"""voice.py — 대사 합성 → 받아쓰기 확인 → 시간표(timeline.json).

  python3 voice.py <에피소드 폴더>

- 대사의 {id.필드} 자리는 facts.json 값으로 바꾼다(숫자를 손으로 쓰지 않는다).
- 목소리 기본은 C(확정 도리 목소리, 깃허브 액션 Qwen3-TTS) — 이 컴퓨터에서 합성하지 않는다. 고른 소리가 없으면
  build/voice_c/voice/lines.json(채운 대사·자막·숫자)을 내보내고 멈춘다(코드 5) → 키트 voice_job.py·select_takes.py 로
  만들어 고른 뒤 다시 실행하면, 그 소리로 받아쓰기 확인·시간표를 만든다.
- 예비 프리셋 E(발랄하고 귀여운 도리 톤, assets/voices.json). Supertonic-3 기본 화자를 섞은 스타일을
  실행할 때 ~/.cache/receipt-shorts/voices/ 에 만들어 쓰고(모델 파일을 스킬에 담지 않는다), 프리셋의 fx 로
  음높이·성도 길이·억양 폭을 바꾼다(voicefx.character). 받아쓰기 확인은 톤을 바꾼 소리로 한다.
- 숫자가 든 줄은 num_speed(E 0.92)만큼 천천히 또박또박 읽고, 숫자는 합성 소리와 다듬은 소리 두 번 다 받아써져야 통과한다.
- 줄마다 합성하고, 한국어 음성인식으로 받아써서 원문과 비교한다. 비슷한 정도가 낮거나 숫자가 안 들리면
  속도·스텝을 바꿔 다시 합성한다. 숫자를 어림수로 바꾸지 않는다 — 끝내 안 들리면 멈추고(코드 3) 알려 준다.
  들어 보고 숫자가 맞으면 episode.json voice.accept 에 그 줄 번호를 넣고 다시 실행한다.
- 합성 전에 자막(sub)에 보이는 숫자가 대사(say)에서 같은 숫자로 읽히는지 대조한다(어긋나면 코드 4).
  대사 틀에 아라비아 숫자를 직접 쓰지 않는다 — 숫자는 {id.필드_say} 로만 넣는다.
- 받아쓰기 단어 시각으로 화면 단계(카드·현지가·원화·한국가·차이·도장)를 대사에 맞춘다.
"""
import difflib, json, re, struct, sys
from pathlib import Path

import numpy as np
import soundfile as sf

CACHE = Path.home() / ".cache" / "receipt-shorts"
HOME = CACHE / "models"
SKILL = Path(__file__).resolve().parent.parent
KIT = SKILL.parent                                   # dori-shorts 키트(kit/) — 목소리 C 스크립트·공용 소리
TTS_DIR = HOME / "sherpa-onnx-supertonic-3-tts-int8-2026-05-11"
ASR_NAME = "sherpa-onnx-zipformer-korean-2024-06-24"
ASR_DIR = next((p for p in (HOME / ASR_NAME, Path(__import__("os").environ.get("DORI_CACHE", Path.home() / ".cache" / "dori-shorts")) / ASR_NAME)
                if (p / "tokens.txt").exists()), HOME / ASR_NAME)
FPS = 30
SCENE_STEPS = {"item": ["card", "local", "krw", "kr", "diff", "stamp"], "hook": ["receipt", "total"],
               "note": ["title", "b1", "b2", "b3"], "summary": ["bars", "result"], "outro": ["ask", "source"]}
HOLD = {"hook": 0.15, "item": 0.45, "note": 0.7, "summary": 1.1, "outro": 0}  # 장면이 끝나기 전 머무는 시간(도장·합계를 볼 틈)
SFX_OF = {"card": "pop", "local": "tick", "krw": "tick", "kr": "tick", "diff": "tick2", "receipt": "print",
          "total": "tick2", "title": "pop", "b1": "tick", "b2": "tick", "b3": "tick",
          "bars": "pop", "result": "ching", "ask": "pop", "source": "tick"}
LEAD, GAP, SCENE_GAP, TAIL = 0.6, 0.42, 0.75, 2.2   # 앞 여백, 줄 사이 쉼, 장면 사이 쉼, 끝 여백(초)
MAX_LEN = 58.0
sys.path.insert(0, str(Path(__file__).parent))
from calc import ko_num  # noqa: E402
from voicefx import character, voice_chain  # noqa: E402


def presets():
    return json.loads((SKILL / "assets" / "voices.json").read_text(encoding="utf-8"))


def build_style(key):
    """프리셋의 화자 비율대로 스타일 벡터를 섞어 한 사람짜리 voice 파일을 만든다(행 크기는 원래대로 유지)."""
    P = presets(); key = key or P["default"]; pr = P[key]
    import hashlib
    out = CACHE / "voices" / f"{key}-{hashlib.md5(json.dumps(pr['mix']).encode()).hexdigest()[:8]}.bin"
    if out.exists():
        return out, pr
    b = (TTS_DIR / "voice.bin").read_bytes()
    n, a, c, n2, d, e = struct.unpack("<6q", b[:48])
    x = np.frombuffer(b[48:], dtype="<f4")
    ttl = x[: n * a * c].reshape(n, a, c); dp = x[n * a * c:].reshape(n2, d, e)

    def mix(arr):
        m = sum(w * arr[i] for i, w in pr["mix"])
        norm = sum(w * np.linalg.norm(arr[i], axis=1, keepdims=True) for i, w in pr["mix"])
        return m / np.linalg.norm(m, axis=1, keepdims=True) * norm
    t, q = mix(ttl), mix(dp)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<6q", 1, a, c, 1, d, e)); f.write(t.astype("<f4").tobytes()); f.write(q.astype("<f4").tobytes())
    return out, pr


def load_asr():
    import sherpa_onnx as s
    A = str(ASR_DIR) + "/"
    return s.OfflineRecognizer.from_transducer(
        encoder=A + "encoder-epoch-99-avg-1.int8.onnx", decoder=A + "decoder-epoch-99-avg-1.onnx",
        joiner=A + "joiner-epoch-99-avg-1.int8.onnx", tokens=A + "tokens.txt", num_threads=2,
        decoding_method="greedy_search")


def mix_number_check(ep_dir, mix_path=None, asr=None):
    """완성 믹스(배경음·효과음을 깐 소리)에서 줄마다 다시 받아써서 숫자가 여전히 들리는지 본다.
    돌려주는 값: [(줄 번호, 빠진 숫자들, 받아쓰기)] — voice.accept 에 넣은 줄은 건너뛴다."""
    ep_dir = Path(ep_dir)
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    x, sr = sf.read(mix_path or (ep_dir / "build" / "mix.wav"), dtype="float32")
    if x.ndim > 1:
        x = x.mean(1)
    asr = asr or load_asr()
    accept = set((ep.get("voice") or {}).get("accept") or [])
    byid = {L["id"]: L for L in ep["lines"]}
    bad = []
    for l in tl["lines"]:
        L = byid.get(l["id"])
        if not L or l["id"] in accept:
            continue
        nums = []
        fill(L["say"], facts, nums)
        need = [v for v in (strip_unit(e) for e, _ in nums) if len(v) >= 2]
        if not need:
            continue
        seg = np.ascontiguousarray(x[int(max(0.0, l["t0"] - 0.05) * sr): int((l["t1"] + 0.1) * sr)])
        txt, _, _ = transcribe(asr, seg, sr)
        miss = [v for v in need if v not in compact(txt)]
        if miss:
            bad.append((l["id"], miss, txt))
    return bad


def load_models(style_path):
    import sherpa_onnx as s
    M = str(TTS_DIR) + "/"
    sc = s.OfflineTtsSupertonicModelConfig(
        duration_predictor=M + "duration_predictor.int8.onnx", text_encoder=M + "text_encoder.int8.onnx",
        vector_estimator=M + "vector_estimator.int8.onnx", vocoder=M + "vocoder.int8.onnx",
        tts_json=M + "tts.json", unicode_indexer=M + "unicode_indexer.bin", voice_style=str(style_path))
    tts = s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(supertonic=sc, num_threads=2)))
    return s, tts, load_asr()


def fill(text, facts, used=None):
    items = {f["id"]: f for f in facts["items"]}

    def rep(m):
        a, b = m.group(1), m.group(2)
        src = facts["total"] if a == "total" else facts if a == "fx" else items.get(a)
        if src is None or b not in src or src[b] in (None, ""):
            raise SystemExit(f"대사 자리 {{{a}.{b}}} 를 facts.json 에서 찾지 못했다")
        if used is not None and b.endswith("_say"):
            used.append((str(src[b]), str(src.get(b + "_r", src[b]))))
        return str(src[b])
    return re.sub(r"\{([a-z0-9_]+)\.([a-z0-9_]+)\}", rep, text)


def compact(t):
    t = t.replace("%", "퍼센트")                    # 받아쓰기가 '37%'처럼 기호로 적어도 같은 말로 본다
    t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", t)   # 천 단위 쉼표(1,290)는 한 숫자로, '59,8' 같은 건 끊어 읽는다
    t = re.sub(r"\d+", lambda m: ko_num(int(m.group())), t)
    return re.sub(r"[^가-힣a-zA-Z]", "", t)


def strip_unit(n):
    """숫자 읽기에서 단위(원·엔·퍼센트)를 뺀 숫자 부분 — 받아쓰기에 그대로 있어야 한다."""
    return compact(re.sub(r"^약\s*", "", re.sub(r"\s*(원|엔|퍼센트|달러|위안|바트|동|유로|파운드)$", "", n)))


NAT_U = {1: ("한", "하나"), 2: ("두", "둘"), 3: ("세", "셋"), 4: ("네", "넷"), 5: ("다섯",), 6: ("여섯",), 7: ("일곱",), 8: ("여덟",), 9: ("아홉",)}
NAT_T = {1: ("열",), 2: ("스물", "스무"), 3: ("서른",), 4: ("마흔",), 5: ("쉰",), 6: ("예순",), 7: ("일흔",), 8: ("여든",), 9: ("아흔",)}
SINO = "영일이삼사오육칠팔구십백천만억"


def native_forms(v):
    """1~99 고유어 수: 4 → 네·넷, 18 → 열여덟, 20 → 스물·스무."""
    if not 1 <= v <= 99:
        return ()
    t, u = divmod(v, 10)
    if t == 0:
        return NAT_U[u]
    if u == 0:
        return NAT_T[t]
    return tuple(a + b for a in NAT_T[t] if a != "스무" for b in NAT_U[u])


def sub_values(text):
    """자막에 보이는 숫자들: '1만 915원' → 10915, '5,000' → 5000, '37%' → 37 (소수는 읽지 않는 값이라 뺀다)."""
    out = []
    for m in re.finditer(r"(?:(\d+)억\s*)?(?:(\d+)만\s*)?(\d[\d,]*(?:\.\d+)?)?", text):
        e, mn, r = m.groups()
        if not (e or mn or r) or (r and "." in r):
            continue
        out.append(int(e or 0) * 10 ** 8 + int(mn or 0) * 10 ** 4 + int((r or "0").replace(",", "")))
    return out


def say_runs(say):
    """대사 속 한자어 숫자 읽기 덩어리: '한국이 이천오백구십이 원' → ['이천오백구십이'] (조사 '이'가 붙지 않게 낱말 단위로 본다)."""
    runs, cur = [], ""
    for raw in say.split():
        t = re.sub(r"[^가-힣a-zA-Z0-9]", "", raw)
        lead = re.match(f"[{SINO}]*", t).group(0)
        if lead and lead == t:
            cur += t
            continue
        if lead:
            runs.append(cur + lead); cur = ""
        elif cur:
            runs.append(cur); cur = ""
    if cur:
        runs.append(cur)
    return runs


def say_has(v, say):
    """자막 숫자 v 가 대사에서 같은 숫자로 읽히는가 — 덩어리가 정확히 같아야 한다('만구백십'이 '만구백십오'에 묻혀 통과하지 않게)."""
    if compact(ko_num(v)) in say_runs(say):
        return True
    toks = [re.sub(r"[^가-힣]", "", t) for t in say.split()]
    return any(t.startswith(f) and len(t) <= len(f) + 2 for f in native_forms(v) for t in toks)


def check_numbers(lines_filled):
    """자막 숫자 ↔ 대사 읽기 대조, 대사에 아라비아 숫자가 남았는지."""
    errs = []
    for lid, say, sub in lines_filled:
        if re.search(r"\d", say):
            errs.append(f"{lid}: 대사에 아라비아 숫자가 있다 — '{say}' (숫자는 {{id.필드_say}} 로 넣거나 한글로 쓴다)")
        for v in sub_values(sub):
            if not say_has(v, say):
                errs.append(f"{lid}: 자막 숫자 {v:,} 가 대사에서 읽히지 않는다 — 자막: '{sub}' / 대사: '{say}'")
    return errs


def trim(x, sr, thr_db=-42, pad=0.04):
    env = np.abs(x)
    thr = 10 ** (thr_db / 20) * max(1e-6, env.max())
    idx = np.where(env > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(pad * sr)); b = min(len(x), idx[-1] + int(pad * 1.5 * sr))
    y = x[a:b].copy()
    f = int(0.008 * sr)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y


def transcribe(asr, x, sr):
    st = asr.create_stream(); st.accept_waveform(sr, x); asr.decode_stream(st)
    r = st.result
    return r.text, list(r.tokens), list(r.timestamps)


def cue_time(key, say_c, asr_text, toks, ts, dur):
    """키워드가 받아쓰기에 있으면 그 토큰 시각, 없으면 원문 글자 위치 비율로."""
    k = compact(key)
    acc, pos = "", []
    for tk in toks:
        pos.append(len(acc)); acc += compact(tk)
    i = acc.find(k)
    if i >= 0 and toks:
        j = max(n for n, p in enumerate(pos) if p <= i)
        return max(0.0, ts[j] - 0.05), "word"
    i = say_c.find(k)
    if i >= 0 and say_c:
        return dur * i / len(say_c), "ratio"
    return None, "miss"


def export_c(ep, facts, vdir, todo):
    """목소리 C 로 만들 대사를 키트 형식(voice/lines.json)으로 내보낸다. 숫자는 keys 로 — 받아쓰기에 꼭 들려야 한다."""
    import shutil
    vdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for L in ep["lines"]:
        nums = []
        say, sub = fill(L["say"], facts, nums), fill(L.get("sub", L["say"]), facts)
        keys = [v for v in (strip_unit(e) for e, _ in nums) if len(v) >= 2]
        rows.append({"id": L["id"], "say": say, "sub": sub.replace("|", "<br>"), "keys": keys})
    (vdir / "lines.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for f in ("voice_common.json",):
        if (KIT / "voice_common" / f).exists() and not (vdir / f).exists(): shutil.copy(KIT / "voice_common" / f, vdir / f)
    if not (vdir / "c_index.json").exists(): (vdir / "c_index.json").write_text("{}", encoding="utf-8")
    cdir = vdir.parent; vs = KIT / "scripts" / "voice"
    print("도리 목소리 C 가 아직 없는 줄: " + ", ".join(todo))
    print(f"  cd {cdir}")
    print(f"  python3 {vs}/voice_job.py make <작업id> {' '.join(todo)} --note \"가격 검산 EP.xx\"")
    print(f"  python3 {vs}/voice_job.py wait <작업id>      # Bash 백그라운드로, 8~15분")
    print(f"  python3 {vs}/select_takes.py                 # 줄마다 가장 또렷한 테이크 → voice/<줄>.wav")
    print("그다음 voice.py(또는 run.py preview)를 다시 실행한다.")


def main(epdir):
    ep_dir = Path(epdir).resolve()
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    out = ep_dir / "build" / "voice"; out.mkdir(parents=True, exist_ok=True)
    vin = ep.get("voice", {})
    key = vin.get("preset") or presets()["default"]
    use_c = key == "C"
    if use_c:
        pr = presets()["C"]; style = None
        vc = {"preset": "C", "name": pr["name"], "sid": 0, "speed": 1.0, "steps": 0, "chain": True, "bright": 0.0,
              "min_sim": 0.82, "num_speed": 1.0, "fx": None, **{k: v for k, v in vin.items() if k in ("min_sim",)}}
    else:
        style, pr = build_style(key)
        vc = {"preset": key, "name": pr["name"], "sid": 0, "speed": pr["speed"],
              "steps": pr["steps"], "chain": pr.get("chain", True), "bright": pr.get("bright", 0.0), "min_sim": 0.82,
              "num_speed": pr.get("num_speed", 1.0), "fx": pr.get("fx"),
              **{k: v for k, v in vin.items() if k in ("speed", "steps", "min_sim", "num_speed")}}
    strict = facts.get("verify") == "strict"
    accept = set(vin.get("accept") or [])
    pre = check_numbers([(L["id"], fill(L["say"], facts), fill(L.get("sub", L["say"]), facts)) for L in ep["lines"]])
    if pre:
        print("자막·대사 숫자 대조 실패:"); [print(" -", e) for e in pre]
        sys.exit(4)
    if use_c:
        vdir = ep_dir / "build" / "voice_c" / "voice"
        todo = [L["id"] for L in ep["lines"] if not (vdir / f"{L['id']}.wav").exists()]
        if todo:
            export_c(ep, facts, vdir, todo)
            sys.exit(5)
        s, tts, asr = None, None, load_asr()
    else:
        s, tts, asr = load_models(style)
    lead, gap, scene_gap = LEAD, GAP, SCENE_GAP
    tail = float((ep.get("outro") or {}).get("hold", TAIL))   # 끝 화면(검산 기준)을 읽을 시간
    t = lead
    lines, report, sfx, steps, scenes, num_bad = [], [], [], {}, [], []
    prev_scene = None
    for L in ep["lines"]:
        nums = []
        say, sub = fill(L["say"], facts, nums), fill(L.get("sub", L["say"]), facts)
        # 숫자 읽기에서 단위(원·엔·퍼센트)를 뺀 숫자 부분은 받아쓰기에 그대로 있어야 한다(strip_unit)
        need = {ex: strip_unit(ex) for ex, _ in nums}
        need = {k: v for k, v in need.items() if len(v) >= 2}
        sp0 = vc["speed"] * (vc["num_speed"] if need else 1.0)    # 숫자가 든 줄은 조금 천천히
        tries = [(sp0, vc["steps"]), (sp0 * 0.96, vc["steps"] + 6), (sp0 * 1.03, vc["steps"] + 10),
                 (sp0 * 0.92, vc["steps"] + 12), (sp0 * 1.0, vc["steps"] + 20)]
        best = None
        if use_c:                                                # 깃허브 액션에서 만들어 고른 소리를 그대로 쓴다
            x, sr = sf.read(vdir / f"{L['id']}.wav", dtype="float32")
            if x.ndim > 1: x = x.mean(1)
            txt, toks, ts = transcribe(asr, x, sr)
            sim = difflib.SequenceMatcher(None, compact(say), compact(txt)).ratio()
            miss = [k for k, v in need.items() if v not in compact(txt)]
            if need and not miss:
                t2, _, _ = transcribe(asr, voice_chain(x, sr).astype(np.float32), sr)
                miss = [k for k, v in need.items() if v not in compact(t2)]
            best = (sim - 0.5 * len(miss), sim, miss, x, sr, txt, toks, ts, 1.0, 0)
            tries = []
        for sp, nst in tries:
            g = s.GenerationConfig(); g.sid = vc["sid"]; g.speed = sp; g.num_steps = nst; g.extra = {"lang": "ko"}
            a = tts.generate(say, g); sr = a.sample_rate
            x = trim(np.array(a.samples, dtype=np.float32), sr)
            x = character(x, sr, vc["fx"])                      # 도리 톤으로 바꾼 뒤에 받아쓰기로 확인한다
            txt, toks, ts = transcribe(asr, x, sr)
            sim = difflib.SequenceMatcher(None, compact(say), compact(txt)).ratio()
            miss = [k for k, v in need.items() if v not in compact(txt)]
            if need and not miss:
                # 다듬기(압축·울림)를 거친, 실제로 들릴 소리로 한 번 더 받아쓴다 — 아슬아슬하게 들리는 숫자는 다시 합성
                t2, _, _ = transcribe(asr, voice_chain(x, sr).astype(np.float32), sr)
                miss = [k for k, v in need.items() if v not in compact(t2)]
            score = sim - 0.5 * len(miss)
            if best is None or score > best[0]:
                best = (score, sim, miss, x, sr, txt, toks, ts, sp, nst)
            if sim >= vc["min_sim"] and not miss:
                break
        _, sim, miss, x, sr, txt, toks, ts, sp, nst = best
        wav = out / f"{L['id']}.wav"; sf.write(wav, x, sr)
        dur = len(x) / sr
        scene = L["scene"]
        if prev_scene is not None and scene != prev_scene:
            t += scene_gap - gap + HOLD.get(prev_scene.split(":")[0], 0)
        if scene != prev_scene:
            scenes.append({"id": scene, "t0": round(t - (0.25 if prev_scene else lead), 3)})
            if prev_scene is not None:
                sfx.append({"t": round(t - 0.28, 3), "name": "whoosh"})
        prev_scene = scene
        kind = scene.split(":")[0]
        say_c = compact(say)
        cues = {}
        for step, key in (L.get("cues") or {}).items():
            if key in ("^", "$"):
                cues[step] = round(t + (0.02 if key == "^" else dur - 0.1), 3); continue
            c, how = cue_time(key, say_c, txt, toks, ts, dur)
            if c is None:
                report.append(f"- {L['id']}: 신호 '{step}'의 단어 '{key}'를 대사에서 찾지 못해 자동 배치")
                continue
            cues[step] = round(t + c, 3)
            if how == "ratio":
                report.append(f"- {L['id']}: '{key}' 받아쓰기에 없어 글자 위치로 맞춤")
        steps.setdefault(scene, {}).update(cues)
        react = None
        if L.get("react"):
            r = L["react"]; rt = t
            if r.get("on"):
                c, _ = cue_time(r["on"], say_c, txt, toks, ts, dur); rt = t + (c or 0)
            react = {**r, "t": round(rt, 3)}
        chunks = [c.strip() for c in sub.split("|")]
        w = [max(1, len(compact(c))) for c in chunks]; acc = 0; sc = []
        for c, wi in zip(chunks, w):
            sc.append({"t0": round(t + dur * acc / sum(w), 3), "t1": round(t + dur * (acc + wi) / sum(w), 3), "text": c}); acc += wi
        env = []
        hop = sr // FPS
        for i in range(0, len(x), hop):
            env.append(float(np.sqrt(np.mean(x[i:i + hop] ** 2))))
        lines.append({"id": L["id"], "scene": scene, "t0": round(t, 3), "t1": round(t + dur, 3), "wav": str(wav.relative_to(ep_dir)),
                      "say": say, "sub": sc, "expr": L.get("expr"), "arms": L.get("arms"), "react": react, "env": env})
        flag = (" ← 일치 낮음" if sim < vc["min_sim"] else "") + (f" ← 숫자 '{', '.join(miss)}' 안 들림" if miss else "") + (" · 사람이 듣고 승인(voice.accept)" if miss and L["id"] in accept else "")
        if miss:
            num_bad.append(L["id"])
        report.append(f"- {L['id']} ({dur:.2f}s, 일치 {sim:.2f}{flag}) 원문: {say} / 받아쓰기: {txt}")
        t += dur + gap
    duration = round(t - gap + tail, 3)
    for i, sc_ in enumerate(scenes):
        sc_["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else duration
    # 신호가 없는 단계는 장면 안에서 순서대로 고르게 배치한다
    for sc_ in scenes:
        kind = sc_["id"].split(":")[0]
        want = SCENE_STEPS.get(kind, [])
        have = steps.setdefault(sc_["id"], {})
        sl = [l for l in lines if l["scene"] == sc_["id"]]
        a, b = (sl[0]["t0"], sl[-1]["t1"]) if sl else (sc_["t0"], sc_["t1"])
        last = a - 0.15
        for n, st in enumerate(want):
            if st not in have:
                nxt = next((have[w] for w in want[n + 1:] if w in have), None)
                guess = a + (b - a) * (n + 0.5) / len(want)
                if nxt is not None:
                    guess = min(guess, (last + nxt) / 2) if nxt > last else last + 0.12
                have[st] = round(max(guess, last + 0.12), 3)
            last = max(last, have[st])
        for st, tt in have.items():
            if st in SFX_OF:
                sfx.append({"t": tt, "name": SFX_OF[st]})
    # 입 모양: 30fps 음량 곡선
    nfr = int(np.ceil(duration * FPS)); mouth = np.zeros(nfr)
    for l in lines:
        e = np.array(l["env"]);
        if not len(e):
            continue
        e = e / max(1e-6, np.percentile(e, 92)); e = np.clip((e - 0.12) / 0.88, 0, 1)
        f0 = int(round(l["t0"] * FPS)); mouth[f0:f0 + len(e)] = np.maximum(mouth[f0:f0 + len(e)], e[: max(0, nfr - f0)])
        del l["env"]
    mouth = np.convolve(mouth, [0.25, 0.5, 0.25], "same")
    tl = {"fps": FPS, "duration": duration, "lines": lines, "scenes": scenes, "steps": steps,
          "sfx": sorted(sfx, key=lambda e: e["t"]), "mouth": [round(float(v), 3) for v in mouth], "voice": vc}
    (ep_dir / "build" / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (ep_dir / "build" / "voice_check.md").write_text("# 받아쓰기 대조\n\n" + "\n".join(report) + "\n", encoding="utf-8")
    print(f"길이 {duration:.1f}s, 대사 {len(lines)}줄 · 목소리 {vc['preset']}({vc['name']})")
    print("\n".join(report))
    if duration > MAX_LEN:
        print(f"길이 초과: {duration:.1f}s > {MAX_LEN}s — 대사를 줄여 다시 실행(쇼츠는 60초 이하, 여유 2초)")
    bad = [x for x in num_bad if x not in accept]
    if bad:
        print(f"숫자 확인 필요: {', '.join(bad)} — build/voice/<줄>.wav 를 들어 보고, 숫자가 맞게 들리면 episode.json voice.accept 에"
              " 줄 번호를 넣고, 틀리면 문장을 바꿔 다시 실행")
        if strict:
            sys.exit(3)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
