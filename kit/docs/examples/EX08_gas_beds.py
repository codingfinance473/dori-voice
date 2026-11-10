"""배경음 시안(2026-11-10, 사용자: "브금이 좀 촌스럽나?") — mix.py 가 BED=A|B|C 일 때 기본 「도리 산책」 대신 쓴다.
A 로파이(78BPM, 일렉트릭 피아노·부드러운 비트) · B 미니멀 그루브(100BPM, 베이스 리프·핑거스냅, 장면마다 한 겹씩) · C 지금 곡 다듬기(기타 아르페지오·패드, 마림바·박수 없음)."""
import numpy as np

def make(style, G):
    put, bed, hz, lp, hp, bp, noise, pluck, tone = (G[k] for k in ("put", "bed", "hz", "lp", "hp", "bp", "noise", "pluck", "tone"))
    T, E, DUR, SR, q, th, mo, rng = (G[k] for k in ("T", "E", "DUR", "SR", "q", "th", "mo", "rng"))
    t0, t1 = E["M01"] + .1, DUR - 1.2
    def ep(f, L=2.4, dec=1.1):                     # 일렉트릭 피아노(FM)
        n = int(L * SR); t = np.arange(n) / SR; ph = 2 * np.pi * f * t
        x = np.sin(ph + 1.1 * np.exp(-t * 5) * np.sin(ph)) * np.exp(-t / dec) + .06 * np.sin(ph * 14) * np.exp(-t * 30)
        return lp(x * np.minimum(1, t / .004) * (1 + .08 * np.sin(2 * np.pi * 4.5 * t)), 2600)
    def sub(f, L=.55, dec=.3):
        n = int(L * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * f * t) + .2 * np.sin(4 * np.pi * f * t)) * np.minimum(1, t / .01) * np.exp(-t / dec)
    def kick():
        n = int(.3 * SR); x = np.arange(n) / SR
        return lp(np.sin(2 * np.pi * np.cumsum(48 + 60 * np.exp(-x * 35)) / SR) * np.exp(-x * 10), 220)
    def rim(): return bp(noise(.09, .022), 1200, 3200)
    def snap():
        a = bp(noise(.07, .012), 1800, 5200); out = np.zeros(len(a) + int(.014 * SR)); out[:len(a)] += .5 * a; out[int(.014 * SR):] += a
        return out
    def hat(): return hp(noise(.04, .01), 8000)
    cache = {}
    def pl(m, L, damp, cut=5000):
        k = (m, L, damp, cut)
        if k not in cache: cache[k] = lp(pluck(hz(m), L, damp), cut)
        return cache[k]

    if style == "A":                                # 로파이
        BEAT = 60 / 78; BAR = BEAT * 4; SW = .62
        ch = [[55, 59, 62, 66], [52, 55, 59, 62], [48, 52, 55, 59], [50, 55, 57, 60, 64]]; root = [43, 40, 36, 38]
        b = 0.0; k = 0
        while b < t1:
            ci = k % 4
            for i, at in enumerate((b, b + (2 + SW) * BEAT)):
                if t0 <= at < t1 and not q(at):
                    notes = ch[ci] if i == 0 else ch[ci][1:]
                    for j, m in enumerate(notes): put(bed, ep(hz(m + 12)), at + j * .016, (.034 if i == 0 else .02) * (.7 if mo(at) else 1), pan=-.3 + j * .18)
                    put(bed, sub(hz(root[ci])), at, .08 if mo(at) else .16)
                    if not th(at) and not mo(at): put(bed, kick(), at, .13)
            for bt in (1, 3):
                at = b + bt * BEAT
                if t0 <= at < t1 and not q(at): put(bed, rim(), at, .04, pan=.1)
            for e8 in range(8):
                at = b + (e8 // 2) * BEAT + (SW * BEAT if e8 % 2 else 0)
                if t0 <= at < t1: put(bed, hat(), at, .013 if e8 % 2 else .008, pan=.3)
            for _ in range(7):                       # 바이닐 잡음
                at = b + rng.uniform(0, BAR)
                if t0 <= at < t1: put(bed, hp(noise(.004, .001), 3000), at, .006, pan=rng.uniform(-.6, .6))
            b += BAR; k += 1
        for j, m in enumerate(ch[0]): put(bed, ep(hz(m + 12), 2.0), t1 + .05 + j * .03, .04, pan=-.3 + j * .18)

    elif style == "B":                              # 미니멀 그루브 — 근거 장면마다 한 겹씩
        BEAT = 60 / 100; BAR = BEAT * 4
        riffm = [{0: 40, 3: 40, 4: 43, 6: 45}, {0: 40, 3: 40, 4: 43, 6: 47, 7: 45}]
        riffM = [{0: 43, 3: 43, 4: 47, 6: 50}, {0: 43, 3: 43, 4: 50, 6: 47, 7: 45}]
        b = 0.0; k = 0
        while b < t1:
            major = b + BAR * .5 >= T["s8"]
            riff = (riffM if major else riffm)[k % 2]; stab = (67, 71, 74) if major else (64, 67, 71)
            for s8 in range(8):
                at = b + s8 * BEAT / 2
                if not (t0 <= at < t1): continue
                if s8 in riff and not q(at):
                    m = riff[s8]; g = .2   # 모리 줄에서도 그대로 — 목소리 쪽에서 낮은 대역을 비웠다(build_voice.mori_fx)
                    put(bed, pl(m, .5, .992, 700), at, g * .8); put(bed, sub(hz(m), .4, .22), at, g * .7)
                if s8 in (2, 6) and not q(at): put(bed, snap(), at, .05, pan=.15)
                if at >= T["s2"] and s8 % 2 == 1: put(bed, hat(), at, .012, pan=.35)
                if at >= T["s3"] and s8 in (3, 6) and not th(at) and not q(at):
                    for j, m in enumerate(stab): put(bed, pl(m, .25, .975), at + j * .006, .03, pan=-.25 + j * .2)
                if at >= T["s4"] and s8 == 7 and not q(at): put(bed, pl(stab[1] + 12, .22, .975), at, .022, pan=.4)
                if at >= T["s5"]: put(bed, hat(), at + BEAT / 4, .006, pan=-.3)
            b += BAR; k += 1
        put(bed, tone(hz(86), 1.2, dec=.5, harm=(1, .2)), T["s8"] + .1, .02, pan=.4)
        put(bed, pl(43, .9, .995, 700), t1 + .05, .2); put(bed, sub(hz(43), .8, .4), t1 + .05, .14)
        for j, m in enumerate((67, 71, 74)): put(bed, pl(m, .8, .994), t1 + .05 + j * .012, .04, pan=-.25 + j * .2)

    elif style == "C":                              # 지금 곡 다듬기 — 같은 코드, 기타 아르페지오 + 패드
        BEAT = 60 / 100; BAR = BEAT * 4
        ch = [[55, 59, 62, 67], [50, 57, 62, 66], [52, 55, 59, 64], [48, 55, 60, 64]]; root = [43, 38, 40, 36]; order = [0, 2, 1, 3, 2, 1, 3, 2]
        b = 0.0; k = 0
        while b < t1:
            ci = k % 4
            if t0 <= b < t1:                         # 패드
                n = int(BAR * 1.15 * SR); t = np.arange(n) / SR; envp = np.minimum(1, t / .5) * np.minimum(1, (BAR * 1.15 - t) / .5)
                put(bed, lp(sum(np.sin(2 * np.pi * hz(m + 12) * t) for m in ch[ci]) * envp, 1800), b, .011)
            for s8 in range(8):
                at = b + s8 * BEAT / 2
                if not (t0 <= at < t1) or q(at): continue
                put(bed, pl(ch[ci][order[s8]], 1.4, .9985, 4200), at, .05 * (.6 if mo(at) else 1), pan=-.25 + (s8 % 4) * .16)
                if s8 in (0, 4) and not mo(at): put(bed, sub(hz(root[ci]), .6, .35), at, .12)
                if s8 % 2 == 1: put(bed, hat(), at, .009, pan=.3)
            b += BAR; k += 1
        for j, m in enumerate(ch[0]): put(bed, pl(m, 1.4, .9985, 4200), t1 + .05 + j * .03, .06, pan=-.2 + j * .12)

    elif style == "H":                              # 훅 멜로디 그루브 — 0초부터, 귀에 남는 두 마디 멜로디(2026-11-10 사용자: "시작부터 안 나와 집중이 안 된다, 몰입되는 멜로디 라인이 없다")
        t0 = 0.0
        BEAT = 60 / 104; BAR = BEAT * 4
        riffm = [{0: 40, 3: 40, 4: 43, 6: 45}, {0: 40, 3: 40, 4: 43, 6: 47, 7: 45}]
        riffM = [{0: 43, 3: 43, 4: 47, 6: 50}, {0: 43, 3: 43, 4: 50, 6: 47, 7: 45}]
        m1 = {0: 71, 2: 74, 3: 71, 5: 76, 7: 74}; m2 = {0: 71, 2: 67, 3: 69, 5: 71}; m2b = {0: 76, 2: 74, 3: 71, 5: 69, 6: 67}
        def bell(m):
            k = ("bell", m)
            if k not in cache:
                f = hz(m); a = tone(f, .55, a=.002, dec=.17, harm=(1, .45, .2, .1)); b2 = tone(2 * f * 1.003, .3, a=.002, dec=.09, harm=(1, .2))
                a[:len(b2)] += .45 * b2; cache[k] = a
            return cache[k]
        b = 0.0; k = 0
        while b < t1:
            major = b + BAR * .5 >= T["s8"]
            riff = (riffM if major else riffm)[k % 2]; stab = (67, 71, 74) if major else (64, 67, 71)
            mot = m1 if k % 2 == 0 else (m2b if k % 8 == 7 else m2)
            for s8 in range(8):
                at = b + s8 * BEAT / 2
                if not (t0 <= at < t1): continue
                if s8 in riff and not q(at):
                    m = riff[s8]; put(bed, pl(m, .5, .992, 700), at, .16); put(bed, sub(hz(m), .4, .22), at, .14)
                if s8 in (0, 4) and not th(at): put(bed, kick(), at, .1)
                if s8 in (2, 6) and not q(at): put(bed, snap(), at, .05, pan=.15); put(bed, rim(), at, .02, pan=-.1)
                if s8 % 2 == 1: put(bed, hat(), at, .012, pan=.35)
                if s8 in mot and not q(at):              # 훅 멜로디 + 점8분 메아리
                    g = .03 if th(at) else .05
                    put(bed, bell(mot[s8]), at, g, pan=.1); put(bed, bell(mot[s8]), at + BEAT * .75, g * .32, pan=-.35)
                if at >= T["s3"] and s8 in (3, 6) and not th(at) and not q(at):
                    for j, m in enumerate(stab): put(bed, pl(m, .25, .975), at + j * .006, .026, pan=-.25 + j * .2)
                if at >= T["s5"]: put(bed, hat(), at + BEAT / 4, .006, pan=-.3)
            b += BAR; k += 1
        put(bed, pl(43, .9, .995, 700), t1 + .05, .2); put(bed, sub(hz(43), .8, .4), t1 + .05, .14)
        for j, m in enumerate((71, 74, 79)): put(bed, bell(m), t1 + .05 + j * .09, .06, pan=-.2 + j * .2)
