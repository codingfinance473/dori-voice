#!/usr/bin/env python3
"""audio.py — 목소리(다듬기) + 배경음 + 효과음을 섞어 build/mix.wav 를 만든다(배경음·효과음은 numpy로 직접 합성).

  python3 audio.py <에피소드 폴더>

- 배경음: 기본은 산뜻한 원곡 「도리 산책」(music.py — 우쿨렐레·마림바·글로켄, 마지막 대사 뒤에 끝 화음).
  episode.json "music": {"style": "fresh" | "lofi" | "none", "seed": 5, "bpm": 118} 로 바꿀 수 있다(lofi = 2판 배경음).
- 배경음은 쉬는 동안 목소리보다 11dB 작게, 말하는 동안 8dB 더 낮춘다(덕킹, "level"·"duck" 으로 조절).
  줄 사이 짧은 쉼에서는 다시 올라오지 않게 붙잡아 두어 출렁이지 않는다. 말하는 동안 1.2kHz 위쪽은 4dB 더("hi_duck"),
  숫자가 든 줄은 2dB 더("num_duck") 낮추고, 완성 믹스를 다시 받아써서 숫자가 덜 들린 줄은 그 줄만 더 낮춰 다시 섞는다.
- 통합 음량 -15 LUFS, 최대 -1 dBFS.
"""
import json, re, sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voicefx import voice_chain, limiter  # noqa: E402
import music as MUSIC  # noqa: E402

SR = 44100
rng = np.random.default_rng(7)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def lp_fast(x, fc):
    # 1차 저역통과를 scipy 없이 빠르게(lfilter 사용 가능하면 사용)
    try:
        from scipy.signal import lfilter
        a = np.exp(-2 * np.pi * fc / SR)
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        return lp(x, fc)


def hp_fast(x, fc):
    return x - lp_fast(x, fc)


def note(f, dur, kind="ep", amp=0.2):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "ep":  # 전자피아노: 사인 + 약한 FM, 지수 감쇠
        mod = np.sin(2 * np.pi * f * 2 * t) * 0.6 * np.exp(-t * 3)
        y = np.sin(2 * np.pi * f * t + mod) * env_exp(n, 0.9) + 0.25 * np.sin(2 * np.pi * f * 2 * t) * env_exp(n, 0.35)
    elif kind == "bass":
        y = np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.01) * env_exp(n, 0.6)
    else:
        y = np.sin(2 * np.pi * f * t) * env_exp(n, 0.3)
    att = np.minimum(1, t / 0.006)
    return y * att * amp


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def lofi(dur, bpm=84):
    n = int(dur * SR) + SR; out = np.zeros(n)
    beat = 60 / bpm; bar = beat * 4
    chords = [[65, 69, 72, 76], [64, 67, 71, 74], [62, 65, 69, 72], [60, 64, 67, 71]]  # Fmaj7 Em7 Dm7 Cmaj7
    roots = [41, 40, 38, 36]
    t = 0.0; bi = 0
    while t < dur + bar:
        ch = chords[bi % 4]
        for k, off in enumerate([0, beat * 1.5, beat * 2.5]):
            s = int((t + off) * SR)
            if s >= n:
                continue
            for j, m in enumerate(ch):
                y = note(mtof(m), 2.2, "ep", 0.045 if k == 0 else 0.03)
                st = s + int(j * 0.012 * SR); e = min(n, st + len(y)); out[st:e] += y[: e - st]
        for k, off in enumerate([0, beat * 2.5]):
            s = int((t + off) * SR); y = note(mtof(roots[bi % 4]), beat * 1.4, "bass", 0.11); e = min(n, s + len(y))
            if s < n:
                out[s:e] += y[: e - s]
        for b in range(4):  # 부드러운 킥(1·3박), 셰이커(8분)
            s = int((t + b * beat) * SR)
            if b in (0, 2) and s < n:
                kn = int(0.25 * SR); tt = np.arange(kn) / SR
                k_ = np.sin(2 * np.pi * (50 + 70 * np.exp(-tt * 25)) * tt) * env_exp(kn, 0.09) * 0.16
                e = min(n, s + kn); out[s:e] += k_[: e - s]
            for h in (0, 0.5):
                s2 = int((t + (b + h) * beat) * SR)
                if s2 < n:
                    hn = int(0.06 * SR); nz = hp_fast(rng.standard_normal(hn), 5000) * env_exp(hn, 0.018) * (0.035 if h else 0.025)
                    e = min(n, s2 + hn); out[s2:e] += nz[: e - s2]
        t += bar; bi += 1
    out = lp_fast(out, 6500)
    crack = (rng.random(n) < 0.0004) * rng.standard_normal(n) * 0.02
    out = out + lp_fast(crack, 3000) + lp_fast(rng.standard_normal(n), 900) * 0.002
    out = out[: int(dur * SR)]
    fi, fo = int(0.6 * SR), int(1.6 * SR)
    out[:fi] *= np.linspace(0, 1, fi); out[-fo:] *= np.linspace(1, 0, fo)
    return out


def sfx(name):
    def tone(f0, f1, d, tau, amp):
        n = int(d * SR); t = np.arange(n) / SR; f = f0 * (f1 / f0) ** (t / d)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, tau) * amp * np.minimum(1, t / 0.003)
    if name == "pop":
        return tone(520, 980, 0.09, 0.03, 0.35)
    if name == "tick":
        n = int(0.05 * SR); c = lp_fast(hp_fast(rng.standard_normal(n), 2000), 5000) * env_exp(n, 0.004) * 0.2
        return c + tone(1200, 1200, 0.05, 0.012, 0.11)
    if name == "tick2":
        a = tone(1047, 1047, 0.18, 0.06, 0.16); b = tone(1319, 1319, 0.22, 0.07, 0.16)
        y = np.zeros(int(0.32 * SR)); y[: len(a)] += a; s = int(0.08 * SR); y[s:s + len(b)] += b; return y
    if name == "print":
        d = 0.9; n = int(d * SR); y = np.zeros(n)
        for k in range(int(d * 28)):
            s = int(k / 28 * SR); m = int(0.018 * SR)
            y[s:s + m] += hp_fast(rng.standard_normal(m), 2500)[: len(y[s:s + m])] * env_exp(m, 0.006)[: len(y[s:s + m])] * 0.16
        t = np.arange(n) / SR; y += np.sin(2 * np.pi * 180 * t) * 0.02 * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.08)
        return y
    if name == "whoosh":
        n = int(0.42 * SR); t = np.arange(n) / SR; w = np.sin(np.pi * t / 0.42) ** 2
        return lp_fast(hp_fast(rng.standard_normal(n), 600), 3500) * w * 0.12
    if name == "stamp":
        n = int(0.35 * SR); t = np.arange(n) / SR
        th = np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 30)) * t) * env_exp(n, 0.07) * 0.55
        sl = lp_fast(rng.standard_normal(n), 2500) * env_exp(n, 0.025) * 0.35
        return th + sl
    if name == "puff":
        return tone(280, 760, 0.16, 0.08, 0.3)
    if name == "boing":
        n = int(0.5 * SR); t = np.arange(n) / SR; f = 520 * (0.42 ** (t / 0.5)) * (1 + 0.05 * np.sin(2 * np.pi * 14 * t))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.25) * 0.25
    if name == "sparkle":
        y = np.zeros(int(0.6 * SR))
        for k, f in enumerate([2093, 2637, 3136, 4186]):
            a = tone(f, f, 0.3, 0.08, 0.08); s = int(k * 0.07 * SR); y[s:s + len(a)] += a
        return y
    if name == "ching":
        n = int(1.0 * SR); t = np.arange(n) / SR
        y = sum(np.sin(2 * np.pi * f * t) * env_exp(n, d) * a for f, d, a in ((2093, .5, .14), (3390, .35, .09), (5240, .2, .05)))
        cn = hp_fast(rng.standard_normal(n), 4000) * env_exp(n, 0.05) * 0.08
        return y + cn
    raise KeyError(name)


def duck_curve(voice, depth_db=10.0, hold=0.32, att=0.06, rel=0.45):
    """목소리가 있는 동안 배경음을 depth_db 낮춘다. 앞뒤 hold 초를 붙잡아 줄 사이 쉼(0.42초)에서 출렁이지 않게 하고,
    장면 사이처럼 긴 쉼에서만 천천히 올라온다."""
    from scipy.ndimage import maximum_filter1d
    env = lp_fast(np.abs(voice), 8)
    ref = np.percentile(env[env > 1e-4], 50) if (env > 1e-4).any() else 1.0
    on = np.clip(env / ref, 0, 1)
    on = maximum_filter1d(on, size=max(1, int(2 * hold * SR)))
    hop = 64; o = on[::hop]
    ca, cr = np.exp(-hop / (SR * att)), np.exp(-hop / (SR * rel))
    out = np.empty_like(o); s = 0.0
    for i, v in enumerate(o):
        c = ca if v > s else cr
        s = c * s + (1 - c) * v; out[i] = s
    sm = np.interp(np.arange(len(voice)) / hop, np.arange(len(out)), out)
    return 10 ** (-depth_db * sm / 20)


def line_duck(tl, extra, n, att=0.05, rel=0.25):
    """줄별 추가 덕킹(dB) 곡선 — 숫자가 든 줄 앞뒤 0.15초까지, 부드럽게 들어가고 나온다."""
    m = np.zeros(n)
    for l in tl["lines"]:
        e = extra.get(l["id"], 0.0)
        if e:
            a, b = int(max(0.0, l["t0"] - 0.15) * SR), int(min(n / SR, l["t1"] + 0.15) * SR)
            m[a:b] = np.maximum(m[a:b], e)
    hop = 64; o = m[::hop]
    ca, cr = np.exp(-hop / (SR * att)), np.exp(-hop / (SR * rel))
    out = np.empty_like(o); s = 0.0
    for i, v in enumerate(o):
        c = ca if v > s else cr
        s = c * s + (1 - c) * v; out[i] = s
    return 10 ** (-np.interp(np.arange(n) / hop, np.arange(len(out)), out) / 20)


def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x)


def main(epdir):
    ep_dir = Path(epdir).resolve()
    tl = json.loads((ep_dir / "build" / "timeline.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    ep_path = ep_dir / "episode.json"
    ep = json.loads(ep_path.read_text(encoding="utf-8")) if ep_path.exists() else {}
    mus = ep.get("music") or {}
    num_ids = {L["id"] for L in ep.get("lines", []) if re.search(r"\{[a-z0-9_]+\.[a-z0-9_]+_say\}", L.get("say", ""))}
    dur = tl["duration"]; n = int(dur * SR)
    voice = np.zeros(n)
    for l in tl["lines"]:
        x, sr = sf.read(ep_dir / l["wav"], dtype="float64")
        if x.ndim > 1:
            x = x.mean(1)
        if sr != SR:
            from scipy.signal import resample_poly
            x = resample_poly(x, SR, sr)
        s = int(l["t0"] * SR); e = min(n, s + len(x)); voice[s:e] += x[: e - s]
    # 효과음: 시간표 + 도장(판정별)
    ev = list(tl["sfx"])
    items = {f["id"]: f for f in facts["items"]}
    for sid, st in tl["steps"].items():
        k = sid.split(":")
        if k[0] == "item" and "stamp" in st:
            ev.append({"t": st["stamp"], "name": "stamp"})
            extra = {"local": "puff", "korea": "boing", "only": "sparkle"}.get(items[k[1]]["verdict"])
            if extra:
                ev.append({"t": st["stamp"] + 0.12, "name": extra})
    fx = np.zeros(n)
    for e in ev:
        y = sfx(e["name"]); s = int(max(0, e["t"]) * SR); end = min(n, s + len(y)); fx[s:end] += y[: end - s]
    # 목소리: 편하게 들리도록 다듬기(저역 정리·치찰음·지글거림 줄이기·크기 고르게·옅은 방 울림) 후 -16 LUFS
    vc = tl.get("voice", {})
    if vc.get("chain", True) and voice.any():
        voice = voice_chain(voice, SR, bright=vc.get("bright", 0.0))
    if voice.any():
        voice *= 10 ** ((-16 - lufs(voice)) / 20)
        voice = limiter(voice, SR, -3.0, look_ms=3.0, release_ms=40.0)   # 합성음의 순간 튐(파열음)만 살짝 눌러 둔다
    lv = lufs(voice) if voice.any() else -16
    # 배경음: 쉬는 동안은 목소리보다 11dB 작게(멜로디가 들리게), 말하는 동안은 8dB 더 낮춰 약 19~20dB 아래(숫자가 또렷하게).
    # episode.music.level / duck 으로 조절. 끝 화음은 마지막 대사 바로 뒤에.
    style = mus.get("style", "fresh")
    last = max((l["t1"] for l in tl["lines"]), default=dur - 2.0)
    ring = max(1.5, dur - last - 0.1)
    if style == "none":
        music = np.zeros(n); bpm = 0
    elif style == "lofi":
        music = lofi(dur); bpm = 84
    else:
        music, bpm = MUSIC.fresh(dur, ring=ring, bpm=mus.get("bpm"), seed=int(mus.get("seed", 5)))
        music = np.pad(music, (0, max(0, n - len(music))))[:n]
    level, depth = float(mus.get("level", -11 if style == "fresh" else -14)), float(mus.get("duck", 8 if style == "fresh" else 10))
    if music.any():
        music *= 10 ** ((lv + level - lufs(music)) / 20)
    # 말하는 동안: 전체 depth dB + 자음이 사는 1.2kHz 위쪽은 hi_duck(4) dB 더(숫자 받침·끝소리가 묻히지 않게),
    # 숫자가 든 줄은 num_duck(2) dB 더. 완성 믹스를 다시 받아써서 숫자가 덜 들린 줄은 그 줄만 5dB씩 더 낮춰 다시 섞는다(최대 2번).
    from scipy.signal import butter, sosfiltfilt
    lo = sosfiltfilt(butter(2, 1200, btype="low", fs=SR, output="sos"), music); hi = music - lo
    dk = duck_curve(voice, depth_db=depth) if voice.any() else np.ones(n)
    hk = duck_curve(voice, depth_db=float(mus.get("hi_duck", 4))) if voice.any() else np.ones(n)
    extra = {lid: float(mus.get("num_duck", 2)) for lid in num_ids}
    note = ""
    for it in range(3):
        ld = line_duck(tl, extra, n)
        music_d = (lo + hi * hk) * dk * ld
        mix = voice + music_d + fx * 0.7                      # 효과음: 1판보다 3dB 작게
        # 통합 음량 -15 LUFS, 미리 보고 누르는 리미터로 최대 -1.2 dBFS(찌그러뜨려 자르지 않는다)
        g = 10 ** ((-15 - lufs(mix)) / 20); mix *= g
        pre_pk = 20 * np.log10(np.max(np.abs(mix)) + 1e-12)
        mix = limiter(mix, SR, -1.2)
        sf.write(ep_dir / "build" / "mix.wav", mix.astype(np.float32), SR)
        if not (music.any() and num_ids and mus.get("check", True)):
            break
        import voice as VOICE
        bad = VOICE.mix_number_check(ep_dir)
        if not bad:
            note = " · 배경음 위에서도 숫자 받아쓰기 통과" + (f"({it}번 더 낮춤)" if it else "")
            break
        if it == 2:
            note = " · 배경음 위에서 숫자가 덜 들리는 줄: " + ", ".join(b[0] for b in bad) + " (qa에서 확인)"
            break
        for lid, miss, txt in bad:
            extra[lid] = extra.get(lid, 0.0) + 5.0
        print("배경음 위에서 숫자가 덜 들린 줄 " + ", ".join(f"{b[0]}({'·'.join(b[1])} → '{b[2]}')" for b in bad) + " → 그 줄 배경음을 5dB 더 낮춰 다시 섞는다")
    vi = lufs(voice * g); mu = lufs(music_d * g) if music_d.any() else float("-inf")
    tune = {"fresh": f"도리 산책 {bpm:.0f} BPM", "lofi": "로파이(2판)", "none": "없음"}.get(style, style)
    print(f"통합 음량 {lufs(mix):.1f} LUFS · 최대 {20*np.log10(np.max(np.abs(mix))):.1f} dBFS(리미터 전 {pre_pk:.1f}) · "
          f"목소리 {vi:.1f} / 배경음 {mu:.1f} LUFS (차이 {vi-mu:.1f}dB) · 목소리 {vc.get('preset', '-')} · 배경음 {tune}{note}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
