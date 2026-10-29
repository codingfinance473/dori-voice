"""배경음(밝은 우쿨렐레·마림바, 사장조, 직접 합성) + 효과음 + 목소리 → mix.wav
목소리가 나오는 동안 배경음을 자동으로 낮춘다(덕킹). 시각은 timeline.js 의 T(줄 시작·단어 시각)·E(줄 끝)를 쓴다.
편마다 고치는 곳: '효과음' 절(장면별 소리 위치), thin·lv(받아쓰기가 약한 줄의 배경음 더 낮추기), extra 목록.
규칙: 효과음은 단어 위에 겹치지 않게 줄 끝이나 단어 직전에 작게. 배경음은 훅 두 줄 뒤에 들어온다.
점검: NOBED=1(배경음 끔)·NOSFX=1(효과음 끔)로 섞어 check_final.py 를 돌려 무엇이 덮는지 가른다.
아래 값은 EP.02 소주(2026-10-29) 예시다."""
import json, re
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
quiet = [(T["drum"] - .05, T["L10"] + .05)]
def q(t): return any(a <= t < b for a, b in quiet)
thin = [(T[i] - .15, E[i] + .1) for i in ("L03", "L07", "L12", "L12b", "L13", "L16")]   # 받아쓰기가 약한 줄: 멜로디·박수·킥을 빼고 현·베이스만
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

for s in ("s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"): whoosh(T[s])
for i, s in enumerate(("cJP", "cCN", "cUS", "cVN")): pop(T[s] - .14, .06, 74 + 3 * i)   # 단어 직전에 작게
for s in ("C3", "C2", "C1"):
    for kk in range(4): put(sfx, bp(noise(.04, .008), 2200 if kk % 2 else 3000, 6000), T[s] + kk * .25, .09)
n = int(.6 * SR); t = np.arange(n) / SR
put(sfx, bp(rng.standard_normal(n), 1500, 6000) * np.sin(np.pi * t / .6) ** 2, T["pick"], .05, pan=.2); pop(T["pick"] + .4, .09, 84)
pop(E["L02"] + .04, .08, 81)                                             # 숫자 카드
put(sfx, bp(rng.standard_normal(int(.8 * SR)), 900, 4000) * np.sin(np.pi * np.arange(int(.8 * SR)) / SR / .8) ** 2, T["L06"] + .5, .04)  # 도넛 그려짐
put(sfx, marimba(hz(79)), T["w30"] + .5, .07)
pop(T["wfruit"] - .15, .05, 83); put(sfx, marimba(hz(81)), E["L07"] + .03, .09)
n = int((T["L10"] - T["drum"]) * SR); t = np.arange(n) / SR                       # 드럼롤
put(sfx, bp(rng.standard_normal(n), 150, 2500) * (.45 + .55 * (np.sin(2 * np.pi * 17 * t) > 0)) * (.25 + .75 * t / t[-1]), T["drum"], .12)
chime(E["L10"] - .04, [74, 78, 81, 86], .08); put(sfx, hp(noise(1.5, .4), 5000), E["L10"] - .04, .05); thump(E["L10"] + .04, .14)
for i, k2 in enumerate(("L11", "jp2", "cn2")): put(sfx, marimba(hz([79, 76, 72][i])), T[k2] + .1, .06)
sad(E["L11b"] + .04, .06)
for i in range(5): put(sfx, marimba(hz([84, 81, 76, 72, 71][i])), T["w2010"] + .1 + i * .26, .07)   # 일본 비중 점 5개(내려감)
boing(E["L12"] + .03, .06)
for i in range(10): put(sfx, tone(hz(91 if i < 8 else 84), .25, dec=.07, harm=(1, .3)), T["L12b"] + .2 + i * .12, .018)  # 병 10개
for i in range(4): put(sfx, marimba(hz([72, 74, 76, 79][i])), T["L13"] + .3 + i * .28, .035)   # 미국 비중 막대 4개(올라감)
chime(E["L13"] + .03, [79, 83, 86], .06, .06)
thump(T["stamp"] + .1, .16); chime(T["stamp"] + .6, [79, 83, 86, 91], .06, .06)
pop(T["cmt"], .09, 81)
n = int(.16 * SR); t = np.arange(n) / SR                                          # 볼주머니 '뽀옹'
put(sfx, np.sin(2 * np.pi * np.cumsum(500 + 900 * t / .16) / SR) * np.sin(np.pi * t / .16), T["L16"] - .42, .07)
chime(E["L16"] + .07, [86, 91], .04, .1)

# ---------- 목소리 + 덕킹 ----------
sr, v = wavfile.read("voice.wav"); v = v.astype(np.float32) / 32768
v = v[:N] if len(v) >= N else np.pad(v, (0, N - len(v)))
v = hp(v, 90)
env = np.convolve(np.abs(v), np.ones(int(.05 * SR)) / int(.05 * SR), mode="same")
att, rel = np.exp(-1 / (.03 * SR)), np.exp(-1 / (.35 * SR)); sm = np.zeros_like(env); g = 0.0
for i in range(0, N, 64):
    e = env[i]; g = att * g + (1 - att) * e if e > g else rel * g + (1 - rel) * e; sm[i:i + 64] = g
duck = 1 - .62 * np.clip(sm / (np.percentile(sm[sm > 1e-4], 90) + 1e-9), 0, 1)
# 배경음 위에서 덜 들린 줄은 그 줄 동안 배경음을 6dB 더 낮춘다
TLL = json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["lines"]
extra = np.ones(N)
for l in TLL:
    if l["id"] in ("L02", "L03", "L07", "L09", "L10", "L11", "L11b", "L12", "L12b", "L13", "L14b", "L16"):
        a, b2 = int((l["t"] - .15) * SR), int((l["t"] + l["d"] + .1) * SR)
        lv = {"L03": .22, "L16": .3, "L07": .35, "L13": .28, "L12b": .3}.get(l["id"], .5)   # 받아쓰기가 배경음에 가장 약했던 줄은 더 낮춘다
        ramp = int(.12 * SR); w = np.ones(b2 - a) * lv; w[:ramp] = np.linspace(1, lv, ramp); w[-ramp:] = np.linspace(lv, 1, ramp)
        extra[a:b2] = np.minimum(extra[a:b2], w[: len(extra[a:b2])])
duck = duck * extra
import os
if os.environ.get("NOSFX"): sfx[:] = 0
if os.environ.get("NOBED"): bed[:] = 0
mix = bed * duck[:, None] * 1.9 + sfx + np.stack([v, v], 1)
mix /= np.max(np.abs(mix)) / 10 ** (-1 / 20)
wavfile.write("mix.wav", SR, (mix * 32767).astype(np.int16))
sp = np.abs(v) > .02
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
print("voice in speech", round(db(v[sp]), 1), "| music under speech", round(db((bed[:, 0] * duck * 1.9)[sp]), 1), "| music in gaps", round(db((bed[:, 0] * duck * 1.9)[~sp]), 1))
