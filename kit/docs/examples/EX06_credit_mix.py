"""배경음(밝은 우쿨렐레·마림바, 사장조, 직접 합성) + 효과음 + 목소리 → mix.wav
목소리가 나오는 동안 배경음을 자동으로 낮춘다(덕킹). 시각은 timeline.js 의 T(줄 시작·단어 시각)·E(줄 끝)를 쓴다.
편마다 고치는 곳: '효과음' 절(장면별 소리 위치), thin·quiet(받아쓰기가 약한 줄의 편곡 비우기), NUM_LINES·WEAK.
배경음은 잔잔하게 '들리게'(2026-11-05) — 크기는 bedmix.py 가 자동으로 맞춘다.
규칙: 효과음은 단어 위에 겹치지 않게 줄 끝이나 단어 직전에 작게. 배경음은 훅 두 줄 뒤에 들어온다.
점검: NOBED=1(배경음 끔)·NOSFX=1(효과음 끔)로 섞어 check_final.py 를 돌려 무엇이 덮는지 가른다.
아래 값은 EX.06 신용융자 담보비율(2026-11-06) 값이다."""
import json, os, re
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
T = json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["T"]
DUR = T["END"]; N = int(SR * DUR)
E = {l["id"]: l["t"] + l["d"] for l in json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["lines"]}   # 줄 끝 시각
rng = np.random.default_rng(5)
bed = np.zeros((N, 2)); sfx = np.zeros((N, 2))
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def put(buf, sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0 or i >= N: return
    sig = sig[: N - i] * g
    buf[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2) * 1.414
    buf[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2) * 1.414
def tone(f, L, a=.004, dec=.35, harm=(1, .3, .1), bend=0.0):
    n = int(L * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * (1 + bend * np.exp(-t * 16))) / SR
    return sum(h * np.sin(ph * (k + 1)) for k, h in enumerate(harm)) * np.minimum(1, t / a) * np.exp(-t / dec)
def noise(L, dec): n = int(L * SR); return rng.standard_normal(n) * np.exp(-np.arange(n) / SR / dec)
def pluck(f, L=.9, damp=.996):           # 카플러스-스트롱 현
    n = int(L * SR); p = max(2, int(SR / f)); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = damp * .5 * (buf[i % p] + buf[(i + 1) % p])
    return lp(out, 5000)
def marimba(f, L=.6):
    n = int(L * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)) * np.exp(-t * 7) * np.minimum(1, t / .002)

# ---------- 배경음 ----------
# EX.06: 사용자 "원래 도리 쇼츠 브금으로"(2026-11-06 23:46) → 키트 기본 합성 우쿨렐레·마림바(사장조 116 BPM)로 되돌림(gmbed 안 씀).
BPM = 116; BEAT = 60 / BPM; BAR = BEAT * 4
chords = [[55, 59, 62, 67], [50, 57, 62, 66], [52, 55, 59, 64], [48, 55, 60, 64]]   # G D Em C (우쿨렐레 보이싱)
bass = [43, 38, 40, 36]
mel = [[71, 74, 76, 74, 71, 69, 67, 69], [69, 66, 69, 74, 72, 71, 69, 66], [67, 71, 74, 76, 74, 71, 67, 71], [72, 71, 69, 67, 64, 67, 69, 67]]
pluck_cache = {}
def strum(ch, at, g, down=True):
    for j, m in enumerate(ch if down else ch[::-1]):
        key = m
        if key not in pluck_cache: pluck_cache[key] = pluck(hz(m), .8)
        put(bed, pluck_cache[key], at + j * .012, g, pan=-.2 + j * .12)
quiet = [(T["L14"] - .4, E["L14"] + .05), (T["L12"] - .1, E["L12"] + .05)]   # 정리 줄·L12 동안 새 음 쉬기
def q(t): return any(a <= t < b for a, b in quiet)
thin = [(T[i] - .15, E[i] + .1) for i in ("L01", "L04", "L07", "L08", "L09", "L11", "L12", "L13", "L14", "L16")]   # 숫자·핵심어 줄: 멜로디·박수·킥을 빼고 현·베이스만
def th(t): return any(a <= t < b for a, b in thin)
b = 0.0; k = 0
while b < DUR - 1.2:
    ci = k % 4
    for s8 in range(8):
        tt = b + s8 * BEAT / 2
        if tt >= DUR - 1.2 or q(tt) or tt < E["L02"] + .1: continue   # 배경음은 훅 두 줄(질문·숫자) 뒤에 들어온다
        if s8 in (0, 3, 4, 6): strum(chords[ci], tt, .05 if s8 in (0, 4) else .035, down=s8 != 3)
        if s8 in (0, 4): put(bed, lp(tone(hz(bass[ci]), .5, a=.01, dec=.25, harm=(1, .25)), 500), tt, .16)
        if s8 in (0, 4) and tt > 3.0 and not th(tt):
            n = int(.25 * SR); x = np.arange(n) / SR
            put(bed, np.sin(2 * np.pi * np.cumsum(55 + 70 * np.exp(-x * 30)) / SR) * np.exp(-x * 12), tt, .14)
        if s8 in (2, 6) and tt > 3.0 and not th(tt): put(bed, bp(noise(.12, .03), 900, 3500), tt, .05, pan=-.1)     # 박수
        put(bed, hp(noise(.05, .015), 7000), tt + BEAT / 4, .018, pan=.3)                       # 셰이커
        if k % 2 == 1 and tt > 3.0 and not th(tt): put(bed, marimba(hz(mel[ci][s8])), tt, .05, pan=.15)          # 마림바(짝수 마디만 쉼)
    if k % 4 == 0: put(bed, tone(hz(86), 1.2, dec=.5, harm=(1, .2)), b, .02, pan=.4)            # 글로켄 반짝
    b += BAR; k += 1
end = DUR - 1.15                                               # 끝 화음
strum(chords[0], end, .07); put(bed, tone(hz(79), 1.4, dec=.6), end + .05, .04)
bed[-int(.4 * SR):] *= np.linspace(1, 0, int(.4 * SR))[:, None]

# ---------- 효과음 ----------
def pop(at, g=.10, m=79): put(sfx, tone(hz(m), .16, a=.002, dec=.04, harm=(1, .2), bend=-.5), at, g)
def whoosh(at, g=.06):
    n = int(.4 * SR); t = np.arange(n) / SR
    put(sfx, bp(rng.standard_normal(n), 500, 3500) * np.sin(np.pi * t / .4) ** 2, at - .3, g, pan=.3)
def chime(at, notes, g=.07, gap=.07):
    for i, m in enumerate(notes): put(sfx, tone(hz(m), 1.3, dec=.45, harm=(1, .25, .1, .15)), at + i * gap, g)
def boing(at, g=.07):
    n = int(.5 * SR); t = np.arange(n) / SR
    f = 300 + 300 * np.exp(-t * 7) * np.cos(2 * np.pi * 8 * t) ** 2
    put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6), at, g)
def thump(at, g=.2):
    n = int(.35 * SR); t = np.arange(n) / SR
    put(sfx, np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 25)) / SR) * np.exp(-t * 12) + .25 * lp(noise(.35, .04), 1500), at, g)
def sad(at, g=.06):
    for i, m in enumerate((67, 65, 62)): put(sfx, tone(hz(m), .5, dec=.25, harm=(1, .5, .2), bend=-.02), at + i * .16, g)

for s in ("s2", "s3", "s4", "s5", "s8"): whoosh(T[s], .04)
pop(E["L01"] + .04, .06, 76)                                                    # 면제 카드(훅 줄 끝)
pop(E["L04"] + .04, .05, 79)                                                    # 140% 선(줄 끝)
boing(E["L06"] + .05, .045)                                                     # 반대매매 칩(줄 끝)
for i in range(2): put(sfx, marimba(hz([72, 67][i])), E["L09"] + .03 + i * .14, .04)   # 잔고 막대 2개(줄 끝)
pop(E["L12"] + .04, .05, 74)                                                    # 증권사 카드
thump(T["stamp"] + .1, .12); chime(T["stamp"] + .6, [76, 79, 83], .04, .08)
n = int(.16 * SR); t = np.arange(n) / SR                                          # 볼주머니 '뽀옹'
put(sfx, np.sin(2 * np.pi * np.cumsum(500 + 900 * t / .16) / SR) * np.sin(np.pi * t / .16), T["L16"] - .42, .07)
chime(E["L16"] + .07, [86, 91], .04, .1)

# ---------- 목소리 + 덕킹 ----------
sr, v = wavfile.read("voice.wav"); v = v.astype(np.float32) / 32768
v = v[:N] if len(v) >= N else np.pad(v, (0, N - len(v)))
v = hp(v, 90)
env = np.convolve(np.abs(v), np.ones(int(.05 * SR)) / int(.05 * SR), mode="same")
att, rel = np.exp(-1 / (.03 * SR)), np.exp(-1 / (.25 * SR)); sm = np.zeros_like(env); g = 0.0
for i in range(0, N, 64):
    e = env[i]; g = att * g + (1 - att) * e if e > g else rel * g + (1 - rel) * e; sm[i:i + 64] = g
duck = 1 - .45 * np.clip(sm / (np.percentile(sm[sm > 1e-4], 90) + 1e-9), 0, 1)   # 말하는 동안 약 5dB만 낮춘다(2026-11-05: 예전 .62 + 줄별 lv 로 배경음이 거의 안 들렸다)
# 숫자·짧은 정답 줄만 그 줄 동안 배경음을 조금 더 낮춘다 — 기본 0.7(-3dB), 완성 믹스 받아쓰기에서 실제로 덜 들린 줄만 0.5(-6dB)까지.
# 0.5 아래로 내리지 않는다: 그래도 덜 들리면 thin(멜로디·박수·킥 빼기)·quiet(그 줄 동안 새 음 쉬기)로 편곡을 비운다.
TLL = json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["lines"]
NUM_LINES = ("L01", "L04", "L07", "L09", "L13", "L14", "L14b", "L16")   # 이 편의 숫자·정답 줄(편마다 고친다)
WEAK = {"L14": .5, "L06": .6, "L12": .6}                                                       # 예: {"L03": .5} — 완성 믹스에서 덜 들린 줄만
extra = np.ones(N)
for l in TLL:
    if l["id"] in NUM_LINES:
        a, b2 = int((l["t"] - .15) * SR), int((l["t"] + l["d"] + .1) * SR)
        lv = max(.5, WEAK.get(l["id"], .7))
        ramp = int(.12 * SR); w = np.ones(b2 - a) * lv; w[:ramp] = np.linspace(1, lv, ramp); w[-ramp:] = np.linspace(lv, 1, ramp)
        extra[a:b2] = np.minimum(extra[a:b2], w[: len(extra[a:b2])])
duck = duck * extra

# ---------- 배경음 크기 맞추기 + mix.wav (bedmix.py — 잔잔하게 들리게, 2026-11-05) ----------
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bedmix import finish
finish(bed, sfx, v, env, sm, duck, E["L02"] + .1, DUR - 1.2, SR)
