#!/usr/bin/env python3
"""voicefx.py — 목소리를 편하게 들리게 다듬는 처리와 마스터 리미터.

voice_chain(x, sr): 저역 정리 → 먹먹한 중저역 살짝 덜기 → 또렷함 살짝 → 치찰음 줄이기(디에서) →
                    고역 거친 기 덜기 → 부드러운 압축(크기 고르게) → 아주 옅은 방 울림
limiter(x, sr, ceil_db): 미리 보고 누르는 리미터(찌그러뜨려 자르지 않는다)
character(x, sr, fx): 도리 캐릭터 톤(음높이·성도 길이·억양 폭) — 합성 직후, 받아쓰기 확인 전에 적용한다
"""
import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt, lfilter, fftconvolve
from scipy.ndimage import minimum_filter1d, uniform_filter1d


def biquad(kind, f0, sr, q=0.707, gain_db=0.0):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / sr; cw = np.cos(w0); alpha = np.sin(w0) / (2 * q)
    if kind == "peak":
        b = [1 + alpha * A, -2 * cw, 1 - alpha * A]; a = [1 + alpha / A, -2 * cw, 1 - alpha / A]
    elif kind == "hshelf":
        sq = 2 * np.sqrt(A) * alpha
        b = [A * ((A + 1) + (A - 1) * cw + sq), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sq)]
        a = [(A + 1) - (A - 1) * cw + sq, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sq]
    elif kind == "lshelf":
        sq = 2 * np.sqrt(A) * alpha
        b = [A * ((A + 1) - (A - 1) * cw + sq), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sq)]
        a = [(A + 1) + (A - 1) * cw + sq, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sq]
    else:
        raise ValueError(kind)
    return np.array(b) / a[0], np.array(a) / a[0]


def eq(x, sr, kind, f0, q=0.707, gain_db=0.0):
    b, a = biquad(kind, f0, sr, q, gain_db)
    return lfilter(b, a, x)


def env_rms(x, sr, win_ms):
    n = max(1, int(sr * win_ms / 1000))
    return np.sqrt(uniform_filter1d(x * x, n) + 1e-12)


def deess(x, sr, lo=5000, hi=9500, thresh=0.32, max_cut_db=7.0):
    """치찰음 대역이 전체 크기에 비해 튈 때만 그 대역을 줄인다."""
    sos = butter(3, [lo, min(hi, sr / 2 * 0.95)], btype="band", fs=sr, output="sos")
    band = sosfiltfilt(sos, x)   # 위상이 같아야 빼서 줄어든다
    eb, ef = env_rms(band, sr, 6), env_rms(x, sr, 6)
    ratio = eb / (ef + 1e-9)
    over = np.clip((ratio - thresh) / thresh, 0, 1)
    g = 10 ** (-max_cut_db * over / 20)
    g = uniform_filter1d(g, int(sr * 0.004))
    return x - (1 - g) * band


def compress(x, sr, below_db=7.0, ratio=2.6, knee_db=6.0, attack_ms=7.0, release_ms=150.0):
    """말소리 크기(활성 구간 상위 레벨)보다 below_db 아래부터 눌러 큰 낱말이 튀지 않게 한다. 처리 전후 말소리 크기는 같게 맞춘다."""
    hop = int(sr * 0.0025)
    e = env_rms(x, sr, 12)[::hop]
    lv = 20 * np.log10(e + 1e-9)
    act = lv[lv > lv.max() - 40]
    speech = np.percentile(act, 90) if len(act) else lv.max()
    thresh_db = speech - below_db
    over = lv - thresh_db
    gr = np.where(over <= -knee_db / 2, 0.0,
                  np.where(over >= knee_db / 2, over * (1 - 1 / ratio), (1 - 1 / ratio) * (over + knee_db / 2) ** 2 / (2 * knee_db)))
    ca, cr = np.exp(-hop / (sr * attack_ms / 1000)), np.exp(-hop / (sr * release_ms / 1000))
    sm = np.zeros_like(gr); s = 0.0
    for i, v in enumerate(gr):
        c = ca if v > s else cr
        s = c * s + (1 - c) * v; sm[i] = s
    g = 10 ** (-np.interp(np.arange(len(x)) / hop, np.arange(len(sm)), sm) / 20)
    y = x * g
    on = lv > speech - 20
    makeup = np.median(sm[on]) if on.any() else 0.0
    return y * 10 ** (makeup / 20), float(np.median(sm[on]) if on.any() else 0.0), float(np.percentile(sm[on], 95) if on.any() else 0.0)


def room(x, sr, rt60=0.28, wet_db=-23.0, predelay_ms=12.0, seed=3):
    rng = np.random.default_rng(seed)
    n = int(sr * rt60 * 1.4); t = np.arange(n) / sr
    ir = rng.standard_normal(n) * np.exp(-6.91 * t / rt60)
    for d, gdb in ((0.011, -6), (0.017, -8), (0.023, -10), (0.031, -12)):  # 이른 반사
        k = int(d * sr)
        if k < n:
            ir[k] += 10 ** (gdb / 20) * 3
    ir = lfilter(*butter(2, 4000, fs=sr), ir)       # 울림은 어둡게(고음을 더하지 않게)
    ir /= np.sqrt((ir ** 2).sum())
    pd = int(sr * predelay_ms / 1000)
    wet = fftconvolve(x, ir)[: len(x)]
    wet = np.concatenate([np.zeros(pd), wet])[: len(x)]
    wet *= np.sqrt((x ** 2).mean() / ((wet ** 2).mean() + 1e-12)) * 10 ** (wet_db / 20)
    return x + wet


def voice_chain(x, sr, bright=0.0, report=None):
    """bright: 목소리가 어두우면 +, 밝으면 − (−1~+1). 화자에 맞춘 미세 조정."""
    x = np.asarray(x, dtype=np.float64)
    x = sosfilt(butter(2, 80, btype="high", fs=sr, output="sos"), x)
    x = eq(x, sr, "peak", 300, 0.9, -1.5)            # 먹먹한 중저역 덜기
    if bright:
        x = eq(x, sr, "peak", 2300, 0.8, 1.5 * bright)  # 어두운 목소리만 또렷하게
    x = eq(x, sr, "lshelf", 150, 0.707, 0.8)         # 살짝 따뜻하게
    x, gr_med, gr_95 = compress(x, sr)                # 크기를 먼저 고르게
    x = deess(x, sr, thresh=0.30, max_cut_db=6.0)     # 압축으로 올라온 치찰음을 다시 누른다
    x = eq(x, sr, "hshelf", 7500, 0.707, -2.0)       # 합성음 특유의 지글거림 덜기
    x = room(x, sr)
    if report is not None:
        report.update(comp_med_db=round(gr_med, 1), comp_p95_db=round(gr_95, 1))
    return x


def character(x, sr, fx):
    """도리 캐릭터 톤: 음높이·성도 길이·억양 폭을 바꾼다(Praat 'Change gender', PSOLA).
    fx = {"f0": 새 음높이 중앙값 Hz(0 = 그대로), "formant": 성도 길이 비율(1.1 = 10% 짧은 성도 → 작고 어린 목소리),
          "range": 억양 폭 배수(1.15 = 15% 더 오르내림 → 발랄), "floor"/"ceil": 원래 목소리 음높이 분석 범위}"""
    if not fx:
        return x
    try:
        import parselmouth
        from parselmouth.praat import call
    except ImportError:
        raise SystemExit("목소리 톤 처리에 praat-parselmouth 가 필요하다 — scripts/setup.sh 를 다시 실행(pip install praat-parselmouth)")
    snd = parselmouth.Sound(np.asarray(x, dtype=np.float64), sampling_frequency=sr)
    out = call(snd, "Change gender", float(fx.get("floor", 100)), float(fx.get("ceil", 500)), float(fx.get("formant", 1.0)),
               float(fx.get("f0", 0.0)), float(fx.get("range", 1.0)), 1.0)
    y = np.asarray(out.values[0], dtype=np.float64)
    osr = int(round(out.sampling_frequency))
    if osr != sr:
        from scipy.signal import resample_poly
        y = resample_poly(y, sr, osr)
    pk = np.max(np.abs(y)) + 1e-9
    return (y * min(1.0, 0.95 / pk)).astype(np.float32)


def limiter(x, sr, ceil_db=-1.2, look_ms=5.0, release_ms=60.0):
    ceil = 10 ** (ceil_db / 20)
    a = np.abs(x) if x.ndim == 1 else np.max(np.abs(x), axis=1)
    need = np.minimum(1.0, ceil / (a + 1e-12))
    L = max(1, int(sr * look_ms / 1000))
    g = minimum_filter1d(need, size=2 * L + 1)        # 봉우리 앞뒤 L 표본 동안 미리 누른다
    g = uniform_filter1d(g, size=L)                    # 누르는 동작을 매끈하게
    # 놓을 때는 천천히(블록 단위 한 극 필터, 올라갈 때만 늦춘다)
    hop = 32
    nb = int(np.ceil(len(g) / hop))
    gb = np.minimum.reduceat(g, np.arange(0, len(g), hop))
    cr = np.exp(-hop / (sr * release_ms / 1000)); s = 1.0; out = np.empty(nb)
    for i, v in enumerate(gb):
        s = v if v < s else cr * s + (1 - cr) * v
        out[i] = s
    g = np.minimum(g, np.interp(np.arange(len(g)) / hop, np.arange(nb), out))
    y = x * (g if x.ndim == 1 else g[:, None])
    return np.clip(y, -ceil, ceil)
