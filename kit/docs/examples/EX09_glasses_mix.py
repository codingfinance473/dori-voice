"""배경음(밝은 우쿨렐레·마림바, 사장조, 직접 합성) + 효과음 + 목소리 → mix.wav
목소리가 나오는 동안 배경음을 자동으로 낮춘다(덕킹). 시각은 timeline.js 의 T(줄 시작·단어 시각)·E(줄 끝)를 쓴다.
편마다 고치는 곳: '효과음' 절(장면별 소리 위치), thin·quiet(받아쓰기가 약한 줄의 편곡 비우기), NUM_LINES·WEAK.
배경음은 잔잔하게 '들리게'(2026-11-05) — 크기는 bedmix.py 가 자동으로 맞춘다.
규칙: 효과음은 단어 위에 겹치지 않게 줄 끝이나 단어 직전에 작게. 배경음은 훅 두 줄 뒤에 들어온다.
점검: NOBED=1(배경음 끔)·NOSFX=1(효과음 끔)로 섞어 check_final.py 를 돌려 무엇이 덮는지 가른다.
아래 값은 EX.08 도시가스(2026-11-09, 도리·모리 2인 형식) 값이다. 배경음은 콜드오픈 두 줄(도리 주장·모리 의심) 뒤에 들어온다."""
import json, os, re
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
T = json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["T"]
DUR = T["END"]; N = int(SR * DUR)
E = {l["id"]: l["t"] + l["d"] for l in json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["lines"]}   # 줄 끝 시각
rng = np.random.default_rng(5)
TLL0 = json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["lines"]
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
# 키트 기본 합성 우쿨렐레·마림바(사장조 116 BPM) — 「도리 산책」
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
quiet = [(T["wMori"] - .2, T["wMori"] + .5), (T["L02"] - .2, T["L02"] + .7), (T["wVoid"] - .15, T["wVoid"] + .6), (T["L04"] - .2, T["L04"] + .7), (T["w55"] - .15, T["w55"] + .7), (T["M05"] - .2, E["M05"] + .05)]   # 핵심 단어 0.5~0.7초만 새 음을 쉰다
def q(t): return any(a <= t < b for a, b in quiet)
thin = [(T[i] - .15, E[i] + .1) for i in ("L02", "L03", "L04", "L05", "L06", "L07", "L09", "M05", "L11")]   # 숫자·핵심어 줄
def th(t): return any(a <= t < b for a, b in thin)
MORI = [(T[i] - .25, E[i] + .15) for i in ("M01", "M00", "M02", "M03", "M04", "M05")]   # 모리 줄
def mo(t): return any(a <= t < b for a, b in MORI)
b = 0.0; k = 0
while b < DUR - 1.2:
    ci = k % 4
    for s8 in range(8):
        tt = b + s8 * BEAT / 2
        if tt >= DUR - 1.2 or q(tt) or tt < E["M01"] + .1: continue   # 배경음은 콜드오픈 두 줄 뒤에 들어온다
        if s8 in (0, 3, 4, 6): strum(chords[ci], tt, (.05 if s8 in (0, 4) else .035) * (.55 if mo(tt) else 1), down=s8 != 3)
        if s8 in (0, 4) and not mo(tt): put(bed, lp(tone(hz(bass[ci]), .5, a=.01, dec=.25, harm=(1, .25)), 500), tt, .16)
        if s8 in (0, 4) and tt > 3.0 and not th(tt) and not mo(tt):
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

BED_STYLE = os.environ.get("BED", "N")   # N = 배경음 없음 + 징글·효과음(2026-11-10 사용자 확정) · B 그루브 · H 훅 · OLD 도리 산책
_old_default = os.environ.get("BED_OLD_DEFAULT", "B")   # 2026-11-10 사용자 선택: B 미니멀 그루브. BED= 로 비우면 예전 「도리 산책」
BED_STYLE = "" if BED_STYLE == "OLD" else BED_STYLE
#   # A·B·C 시안(beds.py), 비우면 「도리 산책」
if BED_STYLE:
    bed[:] = 0
    import beds; beds.make(BED_STYLE, globals())
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
pop(E["M01"] + .05, .06, 74)                                                    # 모리 의심 끝 → 근거 장면
pop(E["L03"] + .05, .04, 72)                                                    # "무효" 줄 끝 — 줄 안에는 소리를 두지 않는다
pop(E["M02"] + .05, .05, 76)                                                    # 모리 질문 끝 → 그냥 안경 장면
chime(T["wOff"] + .6, [76, 79], .035, .08)                                      # 벗어서 ✔
pop(E["M03"] + .05, .05, 76)                                                    # 모리 "3년?" 끝 → 3년 장면
pop(E["M04"] + .05, .05, 76)                                                    # 모리 "무슨 상관" 끝 → 계산 장면
chime(E["M05"] + .06, [76, 79], .04, .09)                                      # "인정" 뒤 두 음
thump(T["stamp"] + .1, .12); chime(T["stamp"] + .6, [76, 79, 83], .04, .08)
n = int(.16 * SR); t = np.arange(n) / SR                                          # 볼주머니 '뽀옹'
put(sfx, np.sin(2 * np.pi * np.cumsum(500 + 900 * t / .16) / SR) * np.sin(np.pi * t / .16), T["L11"] - .42, .07)
chime(E["L11"] + .07, [86, 91], .04, .1)

if BED_STYLE == "N":
    # 배경음 없이 빈틈없게(2026-11-10): 대화가 리듬을 만든다 — 음악 대신 ① 시작·끝 징글 ② 말하는 쪽이 바뀔 때 작은 신호 ③ 숫자마다 한 번씩 ④ 아주 낮은 공간 소리
    def bell(m, at, g, pan=0.0):
        f = hz(m); a = tone(f, .55, a=.002, dec=.17, harm=(1, .45, .2, .1)); b2 = tone(2 * f * 1.003, .3, a=.002, dec=.09, harm=(1, .2)); a[:len(b2)] += .45 * b2
        put(sfx, a, at, g, pan)
    for i, m in enumerate((71, 76)): bell(m, .02 + i * .1, .07, -.2 + i * .4)                      # 시작 징글 "띠링"(첫 말 앞 0.3초)
    for i, l in enumerate(TLL0):                                                                # 말하는 쪽이 바뀌는 순간: 모리 = 낮은 톡, 도리 = 높은 톡
        if i and l["who"] != TLL0[i - 1]["who"]:
            put(sfx, tone(hz(55 if l["who"] == "M" else 79), .12, a=.002, dec=.035, harm=(1, .2), bend=-.3), l["t"] - .17, .026 if l["who"] == "M" else .02, pan=.35 if l["who"] == "M" else -.35)
    for s_ in ("s2", "s3", "s4", "s5", "s8"): whoosh(T[s_], .03); put(sfx, bp(noise(.06, .012), 1800, 5200), T[s_] + .02, .03)   # 장면 전환을 또렷하게
    bell(83, T["wUse"] + .55, .03, .3)                                                           # "사용한 걸로" 상자가 뜰 때
    for i, m in enumerate((79, 86)): bell(m, T["w55"] + .9 + i * .08, .035, .2)                 # 지원자 수 "띵"
    pop(T["wSubmit"] + .5, .05, 83)                                                              # 제출 바구니
    for i, m in enumerate((71, 74, 79)): bell(m, E["L11"] + .22 + i * .1, .06, -.2 + i * .2)     # 끝 징글(시작과 같은 음에서 올라가며 닫는다)
    put(sfx, lp(tone(hz(43), .9, a=.005, dec=.4, harm=(1, .3)), 600), E["L11"] + .22, .1)
    room = lp(rng.standard_normal(N), 900) * .0016; room[:int(.2 * SR)] *= np.linspace(0, 1, int(.2 * SR)); room[-int(.3 * SR):] *= np.linspace(1, 0, int(.3 * SR))
    sfx[:, 0] += room; sfx[:, 1] += room                                                         # 줄 사이가 디지털 무음으로 뚝 끊기지 않게

# ---------- 목소리 + 덕킹 ----------
sr, v = wavfile.read("voice.wav"); v = v.astype(np.float32) / 32768
v = v[:N] if len(v) >= N else np.pad(v, (0, N - len(v)))
v = hp(v, 90)
env = np.convolve(np.abs(v), np.ones(int(.05 * SR)) / int(.05 * SR), mode="same")
att, rel = np.exp(-1 / (.03 * SR)), np.exp(-1 / (.14 * SR)); sm = np.zeros_like(env); g = 0.0
for i in range(0, N, 64):
    e = env[i]; g = att * g + (1 - att) * e if e > g else rel * g + (1 - rel) * e; sm[i:i + 64] = g
duck = 1 - .62 * np.clip(sm / (np.percentile(sm[sm > 1e-4], 90) + 1e-9), 0, 1)   # 말하는 동안 약 5dB만 낮춘다(2026-11-05: 예전 .62 + 줄별 lv 로 배경음이 거의 안 들렸다)
# 숫자·짧은 정답 줄만 그 줄 동안 배경음을 조금 더 낮춘다 — 기본 0.7(-3dB), 완성 믹스 받아쓰기에서 실제로 덜 들린 줄만 0.5(-6dB)까지.
# 0.5 아래로 내리지 않는다: 그래도 덜 들리면 thin(멜로디·박수·킥 빼기)·quiet(그 줄 동안 새 음 쉬기)로 편곡을 비운다.
TLL = json.loads(re.search(r"window.TL=(.*);$", open("timeline.js", encoding="utf-8").read(), re.S).group(1))["lines"]
NUM_LINES = ("L02", "L03", "L04", "L05", "L06", "L07", "L08", "L11", "M00", "M01", "M02", "M03", "M04", "M05")   # 이 편의 숫자·결론 줄
WEAK = {}   # 모리 줄은 도리 줄과 같은 깊이(.7)로만 — 모리 때만 음악이 꺼지는 느낌이 없게                                          # 완성 믹스 받아쓰기에서 덜 들린 줄(첫마디가 덮임)
extra = np.ones(N)
for l in TLL:
    if l["id"] in NUM_LINES:
        a, b2 = int((l["t"] - .12) * SR), int((l["t"] + l["d"] + .1) * SR)   # 첫마디가 덮이지 않게 .35초 앞서 내린다
        lv = max(.5, WEAK.get(l["id"], .7))
        ramp = int(.12 * SR); w = np.ones(b2 - a) * lv; w[:ramp] = np.linspace(1, lv, ramp); w[-ramp:] = np.linspace(lv, 1, ramp)
        extra[a:b2] = np.minimum(extra[a:b2], w[: len(extra[a:b2])])
duck = duck * extra

# ---------- 배경음 크기 맞추기 + mix.wav (bedmix.py — 잔잔하게 들리게, 2026-11-05) ----------
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os
os.environ.setdefault("BED_UNDER", "12.7")   # 2인 형식은 쉼이 짧아(0.2초) 쉼에서만 키우기 어렵다 → 전체를 조금 크게, 고르게 깐다
from bedmix import finish
bed *= 2.6   # 2판: 모리 줄에서 베이스·킥을 빼 전체가 얇아져 자동 배율(최대 8)로는 쉼이 너무 조용 → 원 소리를 키워 맞춘다
finish(bed, sfx, v, env, sm, duck, (.05 if BED_STYLE == "H" else E["M01"] + .1), DUR - 1.2, SR)
