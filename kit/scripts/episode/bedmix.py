"""배경음 크기 맞추기 + 마무리(mix.wav) — 숫자 퀴즈·생활 검산·해설 mix.py 가 같이 쓴다(2026-11-05).

사용자 지시(2026-11-05): "배경음이 전혀 안 들린다 — 도리 목소리에 집중되는 건 좋지만 잔잔하게는 들리게".
예전 믹스는 덕킹(-8dB) + 줄별 추가 낮춤(-6~-13dB) + 고정 배율이라 말하는 동안 배경음이
목소리보다 25~30dB 아래(EP.02 소주 실측)였다 — 휴대폰에서는 사실상 들리지 않았다.

지금 규칙(휴대폰 스피커 기준 — 200Hz 아래 베이스는 폰에서 거의 안 나와 빼고 잰다):
  · 말하는 동안 배경음 = 목소리보다 약 14dB 작게(12~16 통과). 배율은 자동으로 맞춘다(BED_UNDER=16 처럼 바꿀 수 있음).
  · 말하는 동안 배경음의 800Hz~4kHz(받침·자음이 사는 대역)만 약 9dB 더 비운다 — 우쿨렐레 몸통(아래)과
    셰이커·글로켄 반짝임(위)은 남아서 '들리지만 말을 덮지 않는다'.
  · 줄 사이 쉼에서는 7~12dB 작게.
  · 통합 음량 -14 LUFS, 최대 -1dBFS(리미터).
받아쓰기 시험(공용 목소리 19줄, 2026-11-05): 배경음 없음 0.815 · 예전 믹스 0.801 · 이 믹스 0.794(평균 문자 일치율) — 또렷함은 그대로.
"""
import os, re, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt


def _f(x, f, kind, sr): return sosfilt(butter(2, f, kind, fs=sr, output="sos"), x)
def _db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def lufs(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])


def finish(bed, sfx, v, env, sm, duck, music_from, music_to, SR, out="mix.wav"):
    """bed·sfx: (N,2) 배경음·효과음, v: 목소리(N), env: 50ms 평균 음량, sm: 덕킹용 매끈한 음량,
    duck: 덕킹 곡선(N, 줄별 추가 낮춤 포함), music_from/to: 배경음이 깔린 구간(초)."""
    N = len(v)
    ref = np.percentile(env[env > 1e-4], 90)
    sp = env > .1 * ref                                   # 말하는 구간
    sil = env < .02 * ref                                 # 줄 사이 쉼
    if os.environ.get("NOSFX"): sfx = sfx * 0
    nobed = bool(os.environ.get("NOBED")) or not bed.any()
    if not nobed:
        lo = np.stack([_f(bed[:, c], 800, "low", SR) for c in (0, 1)], 1)
        hi = np.stack([_f(bed[:, c], 4000, "high", SR) for c in (0, 1)], 1)
        carve = 1 - .65 * np.clip(sm / (ref + 1e-9), 0, 1)
        bed = lo + (bed - lo - hi) * carve[:, None] + hi
    bed_ph = _f(bed[:, 0] + bed[:, 1], 200, "high", SR) * .5   # 폰에서 들리는 대역
    vs = _db(v[sp])
    gain = 1.0 if nobed else float(np.clip(10 ** ((vs - float(os.environ.get("BED_UNDER", 14)) - _db((bed_ph * duck)[sp])) / 20), .5, 8))
    if nobed: bed = bed * 0
    mix = bed * duck[:, None] * gain + sfx + np.stack([v, v], 1)
    mix /= np.max(np.abs(mix)) / 10 ** (-1 / 20)
    wavfile.write(out, SR, (mix * 32767).astype(np.int16))
    lu = lufs(out)                                        # 배경음이 커지면 최대치 정규화만으로는 -16 LUFS 쪽으로 내려간다
    if abs(-14 - lu) > .3:
        tmp = out + ".tmp.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-af",
                        f"volume={-14 - lu:.2f}dB,alimiter=limit=0.891:attack=5:release=60:level=disabled",
                        "-c:a", "pcm_s16le", tmp], check=True)
        os.replace(tmp, out); lu = lufs(out)
    print(f"통합 음량 {lu:.1f} LUFS")
    if nobed:
        print("배경음 끔(NOBED)"); return
    on = np.zeros(N, bool); on[int(music_from * SR):int(music_to * SR)] = True
    under = vs - _db((bed_ph * duck * gain)[sp & on]); gap = vs - _db((bed_ph * duck * gain)[sil & on])
    ok = 12 <= under <= 16 and 7 <= gap <= 12
    print(f"배경음 {'통과' if ok else '확인'} — 목소리보다 말하는 동안 {under:.1f}dB · 쉼에서 {gap:.1f}dB 작게"
          f"(목표 12~16 · 7~12, 배율 {gain:.2f})")
