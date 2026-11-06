"""배경음을 사운드폰트(General MIDI, TimGM6mb.sf2)로 연주한다 — 직접 합성한 우쿨렐레 대신 실제 악기 소리.
필요: libfluidsynth(이미 깔려 있음) + `pip install pyfluidsynth --break-system-packages`.

make(style, start, end, dur, sr, thin, quiet) -> (N, 2) float 배열
  style  A 피아노 발라드 · B 로파이 일렉피아노 · C 첼레스타 + 패드 · D 어쿠스틱 기타+마림바(밝게) · E 피치카토+일렉피아노(경쾌) · F 나일론 기타 보사노바 · G 재즈 카페 피아노 · H 하프 아르페지오 미니멀 · I 기타+글로켄 밝은 팝 · K 장조 로파이 힙합 · L 플루트+피치카토 · M 소프트 피아노 팝
  start  배경음이 들어오는 시각(훅 두 줄 뒤) · end 끝 화음 시각
  thin(t)  True 면 그 박의 멜로디를 빼고 반주를 조금 여리게(숫자·핵심어 줄)
  quiet(t) True 면 그 박에 새 음을 내지 않는다
크기는 mix.py 의 bedmix.finish 가 맞추므로 여기서는 대략 -12dBFS 봉우리로만 맞춘다.
"""
import numpy as np

SF = "/usr/share/sounds/sf2/TimGM6mb.sf2"


def _render(events, programs, dur, sr, reverb=.55):
    import fluidsynth
    fs = fluidsynth.Synth(samplerate=float(sr), gain=0.5)
    sid = fs.sfload(SF)
    for ch, prog in programs.items():
        if ch == 9: fs.program_select(9, sid, 128, 0)
        else: fs.program_select(ch, sid, 0, prog)
        fs.cc(ch, 91, int(reverb * 110))   # 잔향
        fs.cc(ch, 93, 20)                  # 코러스 조금
    try: fs.set_reverb(roomsize=.75, damping=.35, width=.9, level=.7)
    except Exception: pass
    ev = []
    for t, ch, note, vel, length in events:
        if t < 0 or t >= dur: continue
        ev.append((t, 1, ch, note, vel)); ev.append((min(dur, t + length), 0, ch, note, 0))
    ev.sort(key=lambda e: (e[0], e[1]))
    out = []; now = 0
    N = int(dur * sr)
    for t, on, ch, note, vel in ev:
        n = int(t * sr) - now
        if n > 0: out.append(fs.get_samples(n)); now += n
        if on: fs.noteon(ch, note, vel)
        else: fs.noteoff(ch, note)
    if N > now: out.append(fs.get_samples(N - now))
    fs.delete()
    x = np.concatenate(out).astype(np.float32).reshape(-1, 2) / 32768
    x = x[:N] if len(x) >= N else np.pad(x, ((0, N - len(x)), (0, 0)))
    pk = np.abs(x).max()
    return x / pk * .25 if pk > 0 else x


def make(style, start, end, dur, sr, thin=lambda t: False, quiet=lambda t: False):
    ev = []
    def note(t, ch, n, v, L):
        if start <= t < end and not quiet(t): ev.append((t, ch, n, v, L))

    if style == "A":      # 피아노 발라드 — 가단조, 느린 8분 아르페지오 + 느린 현 패드
        BPM = 70; B = 60 / BPM; BAR = 4 * B
        prog = {0: 0, 1: 49, 2: 0}   # 0 피아노 반주 · 1 현 패드 · 2 피아노 멜로디
        ch_ = [(45, [57, 64, 69, 72]), (41, [53, 60, 65, 69]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]   # Am F C G
        mel = [[76, 74, 72, 71], [72, 69, 67, 69], [67, 72, 76, 74], [74, 71, 67, 71]]
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            note(b, 0, root, 52, BAR); note(b, 0, root - 12, 40, BAR)
            for i in range(8):
                t = b + i * B / 2; v = 34 if thin(t) else 42
                note(t, 0, up[[0, 1, 2, 3, 2, 1, 2, 1][i]], v + (6 if i == 0 else 0), B * 1.2)
            for n in up[:3]: note(b, 1, n - 12, 30, BAR)
            if k % 2 == 1:
                for i in range(4):
                    t = b + i * B
                    if not thin(t): note(t, 2, mel[k % 4][i], 50, B * .95)
            b += BAR; k += 1
        for n in (36, 48, 55, 60, 64, 67): ev.append((end, 0, n, 50, 2.5))   # 끝 화음 C(밝게 마무리)
        for n in (48, 55, 60): ev.append((end, 1, n, 34, 2.5))

    elif style == "B":    # 로파이 일렉피아노 — 7화음, 부드러운 브러시 드럼, 손가락 베이스
        BPM = 74; B = 60 / BPM; BAR = 4 * B
        prog = {0: 4, 1: 33, 9: 0}
        ch_ = [(45, [57, 60, 64, 67]), (41, [53, 57, 60, 64]), (48, [52, 55, 59, 64]), (43, [50, 55, 59, 62])]   # Am7 Fmaj7 Cmaj7 G6
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for tt, v in ((b, 46), (b + 1.5 * B, 36), (b + 2.5 * B, 40)):
                for j, n in enumerate(up): note(tt + j * .012, 0, n, v - (6 if thin(tt) else 0), B * (1.4 if tt == b else .9))
            note(b, 1, root - 12 + 12, 60, B * 1.6); note(b + 2.5 * B, 1, root + (7 if k % 2 else 0), 50, B * 1.2)
            for i in range(8):
                t = b + i * B / 2
                note(t, 9, 42, 22 if i % 2 else 30, .1)                     # 닫힌 하이햇(여리게)
                if i in (0, 5): note(t, 9, 36, 48, .2)                     # 킥
                if i in (2, 6): note(t, 9, 37, 34, .2)                     # 사이드스틱
            b += BAR; k += 1
        for j, n in enumerate((48, 52, 55, 59, 64)): ev.append((end + j * .02, 0, n, 48, 2.5))
        ev.append((end, 1, 36, 55, 2.2))

    elif style == "D":    # 어쿠스틱 기타 + 마림바 — 바장조, 가볍고 담백한 정보 전달용(2026-11-06 EX.06)
        BPM = 92; B = 60 / BPM; BAR = 4 * B
        prog = {0: 25, 1: 12, 2: 32, 9: 0}   # 0 스틸 기타 · 1 마림바 · 2 어쿠스틱 베이스 · 9 드럼
        ch_ = [(41, [53, 57, 60, 65]), (48, [52, 55, 60, 64]), (50, [53, 57, 62, 65]), (46, [53, 58, 62, 65])]   # F C Dm Bb
        mel = [[72, 0, 69, 0, 72, 74, 0, 0], [72, 0, 67, 0, 64, 0, 67, 0], [69, 0, 74, 0, 72, 69, 0, 0], [70, 0, 69, 67, 0, 65, 0, 0]]
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for i, tt in enumerate((b, b + B, b + 2 * B, b + 3 * B)):    # 기타 스트럼(4분)
                for j, n in enumerate(up): note(tt + j * .018, 0, n, (44 if i % 2 == 0 else 34) - (6 if thin(tt) else 0), B * .9)
            note(b, 2, root - 12, 56, B * 1.6); note(b + 2 * B, 2, root - 5, 48, B * 1.4)
            if k % 2 == 1:
                for i in range(8):
                    t = b + i * B / 2; m = mel[k % 4][i]
                    if m and not thin(t): note(t, 1, m, 40, B * .6)
            for i in range(4):
                t = b + i * B
                note(t, 9, 42, 18, .1)
                if i in (1, 3): note(t, 9, 39, 22, .15)                    # 손뼉(여리게)
            b += BAR; k += 1
        for j, n in enumerate((41, 53, 57, 60, 65)): ev.append((end + j * .02, 0, n, 46, 2.4))
        for n in (72, 77): ev.append((end + .1, 1, n, 40, 1.2))

    elif style == "E":    # 피치카토 현 + 클린 일렉피아노 — 라장조, 경쾌한 해설·브리핑 느낌(2026-11-06 EX.06)
        BPM = 100; B = 60 / BPM; BAR = 4 * B
        prog = {0: 45, 1: 4, 2: 32, 3: 48}   # 0 피치카토 · 1 일렉피아노 · 2 베이스 · 3 현 합주(아주 여리게)
        ch_ = [(50, [62, 66, 69, 74]), (45, [61, 64, 69, 73]), (47, [62, 66, 71, 74]), (43, [62, 67, 71, 74])]   # D A Bm G
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for i in range(8):                                             # 피치카토 8분
                t = b + i * B / 2; n = up[[0, 2, 1, 3, 2, 1, 3, 2][i]]
                note(t, 0, n, (40 if i % 2 == 0 else 32) - (6 if thin(t) else 0), B * .4)
            for j, n in enumerate(up[:3]): note(b + j * .01, 1, n - 12, 36, B * 1.8)
            note(b, 2, root - 12, 54, B * 1.5); note(b + 2 * B, 2, root - 12, 46, B * 1.2)
            for n in up[:3]: note(b, 3, n, 20, BAR)
            b += BAR; k += 1
        for j, n in enumerate((38, 50, 57, 62, 66, 69)): ev.append((end + j * .02, 0, n, 46, 1.2))
        for n in (50, 57, 62): ev.append((end, 3, n, 26, 2.4))

    elif style == "F":    # 나일론 기타 보사노바 + 따뜻한 패드 — 바장조 7화음, 카페처럼 편안하게(2026-11-06 EX.06)
        BPM = 84; B = 60 / BPM; BAR = 4 * B
        prog = {0: 24, 1: 89, 2: 32, 9: 0}   # 0 나일론 기타 · 1 웜 패드 · 2 어쿠스틱 베이스 · 9 쉐이커 대신 하이햇 여리게
        ch_ = [(41, [57, 60, 64, 65]), (40, [55, 59, 62, 64]), (38, [53, 57, 60, 62]), (43, [53, 55, 59, 62])]   # Fmaj7 Em7 Dm7 G7
        hits = [0, 1.5, 2.5, 3.5]                                          # 보사노바 손가락 패턴(박)
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            note(b, 2, root - 12 + 12, 54, B * 1.4); note(b + 2 * B, 2, root - 12 + 19, 44, B * 1.2)
            for h in hits:
                tt = b + h * B
                for j, n in enumerate(up[1:]): note(tt + j * .015, 0, n, (38 if h == 0 else 32) - (6 if thin(tt) else 0), B * .55)
            note(b, 0, root, 40, B * 1.4)
            for n in up[:3]: note(b, 1, n, 24, BAR + .05)
            for i in range(8): note(b + i * B / 2, 9, 70, 14 if i % 2 else 20, .08)   # 마라카스(아주 여리게)
            b += BAR; k += 1
        for j, n in enumerate((41, 53, 57, 60, 64)): ev.append((end + j * .03, 0, n, 42, 2.4))
        for n in (53, 57, 60): ev.append((end, 1, n, 26, 2.4))

    elif style == "G":    # 재즈 카페 피아노 — 다장조 7화음, 업라이트 베이스 + 브러시(2026-11-06 EX.06)
        BPM = 80; B = 60 / BPM; BAR = 4 * B
        prog = {0: 0, 2: 32, 9: 0}
        ch_ = [(48, [52, 55, 59, 64]), (45, [52, 55, 60, 64]), (50, [53, 57, 60, 64]), (43, [53, 57, 59, 62])]   # Cmaj7 Am7 Dm7 G7
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for tt, v in ((b, 38), (b + 1.5 * B, 30), (b + 3 * B, 32)):
                for j, n in enumerate(up): note(tt + j * .01, 0, n, v - (6 if thin(tt) else 0), B * (1.3 if tt == b else .8))
            for i in range(4): note(b + i * B, 2, root - 12 + [0, 4, 7, 9][i], 52 if i == 0 else 44, B * .9)   # 걷는 베이스
            for i in range(4):
                t = b + i * B; note(t, 9, 59, 18, .2)                      # 라이드(여리게)
                if i in (1, 3): note(t, 9, 42, 20, .1)
            b += BAR; k += 1
        for j, n in enumerate((36, 52, 55, 59, 62, 64)): ev.append((end + j * .03, 0, n, 40, 2.6))

    elif style == "H":    # 하프 아르페지오 + 패드 + 비브라폰 — 다장조, 미니멀 설명 영상 톤(2026-11-06 EX.06)
        BPM = 92; B = 60 / BPM; BAR = 4 * B
        prog = {0: 46, 1: 89, 2: 32, 3: 11}   # 0 하프 · 1 웜 패드 · 2 베이스 · 3 비브라폰
        ch_ = [(48, [48, 55, 60, 64]), (43, [43, 50, 55, 59]), (45, [45, 52, 57, 60]), (41, [41, 48, 53, 57])]   # C G Am F
        mel = [[67, 0, 64, 0], [67, 0, 62, 0], [64, 0, 60, 0], [65, 0, 64, 62]]
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for i in range(8):
                t = b + i * B / 2; n = up[[0, 1, 2, 3, 2, 1, 2, 3][i]] + 12
                note(t, 0, n, (34 if i % 2 == 0 else 28) - (6 if thin(t) else 0), B * .9)
            for n in up[1:]: note(b, 1, n, 22, BAR + .05)
            note(b, 2, root - 12 + 12, 50, B * 1.8); note(b + 2 * B, 2, root - 12 + 19, 40, B * 1.4)
            if k % 2 == 1:
                for i in range(4):
                    t = b + i * B; m = mel[k % 4][i]
                    if m and not thin(t): note(t, 3, m + 12, 30, B * 1.2)
            b += BAR; k += 1
        for j, n in enumerate((48, 60, 64, 67, 72)): ev.append((end + j * .06, 0, n, 38, 2.2))
        for n in (48, 55, 64): ev.append((end, 1, n, 24, 2.4))

    elif style == "I":    # 기타 + 글로켄슈필 — 사장조, 밝은 브이로그·정보 쇼츠 톤(2026-11-06 EX.06)
        BPM = 104; B = 60 / BPM; BAR = 4 * B
        prog = {0: 24, 1: 9, 2: 32, 9: 0}   # 0 나일론 기타 · 1 글로켄슈필 · 2 베이스 · 9 드럼
        ch_ = [(43, [55, 59, 62, 67]), (50, [54, 57, 62, 66]), (40, [52, 55, 59, 64]), (48, [52, 55, 60, 64])]   # G D Em C
        mel = [[79, 0, 74, 0, 76, 0, 79, 0], [78, 0, 74, 0, 0, 0, 0, 0], [76, 0, 79, 0, 83, 0, 79, 0], [76, 0, 0, 0, 74, 0, 0, 0]]
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for i in range(8):                                             # 기타 8분 뜯기(높은 줄 위주)
                t = b + i * B / 2; n = up[[0, 2, 1, 3, 2, 1, 3, 2][i]]
                note(t, 0, n, (38 if i % 2 == 0 else 30) - (6 if thin(t) else 0), B * .5)
            note(b, 2, root - 12 + 12, 52, B * 1.2); note(b + 2 * B, 2, root - 12 + 19, 44, B * 1.2)
            if k % 2 == 1:
                for i in range(8):
                    t = b + i * B / 2; m = mel[k % 4][i]
                    if m and not thin(t): note(t, 1, m, 30, B * .5)
            for i in range(4):
                t = b + i * B
                if i in (0, 2): note(t, 9, 36, 30, .2)
                if i in (1, 3): note(t, 9, 39, 20, .12)
            b += BAR; k += 1
        for j, n in enumerate((43, 55, 59, 62, 67)): ev.append((end + j * .03, 0, n, 42, 2.0))
        ev.append((end + .1, 1, 79, 34, 1.4))

    elif style == "K":    # 장조 로파이 힙합 — 라장조 7화음 로즈 + 둥근 킥·스네어, 느긋하게(2026-11-06 EX.06)
        BPM = 82; B = 60 / BPM; BAR = 4 * B
        prog = {0: 4, 1: 33, 9: 0}
        ch_ = [(50, [61, 64, 66, 69]), (47, [62, 66, 69, 73]), (43, [62, 66, 69, 71]), (45, [61, 64, 67, 71])]   # Dmaj7 Bm9 Gmaj7 A7sus
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for tt, v in ((b, 40), (b + 1.75 * B, 32), (b + 3 * B, 34)):
                for j, n in enumerate(up): note(tt + j * .02, 0, n - 12, v - (6 if thin(tt) else 0), B * (1.5 if tt == b else .9))
            note(b, 1, root - 12, 58, B * 1.5); note(b + 2.75 * B, 1, root - 12 + 7, 46, B * .9)
            for i in range(8):
                t = b + i * B / 2 + (.03 if i % 2 else 0)                  # 살짝 늘어지는 리듬
                note(t, 9, 42, 16 if i % 2 else 22, .08)
                if i in (0, 3, 5): note(t, 9, 36, 44, .2)
                if i in (2, 6): note(t, 9, 38, 26, .2)
            b += BAR; k += 1
        for j, n in enumerate((38, 49, 52, 54, 57)): ev.append((end + j * .03, 0, n, 40, 2.6))

    elif style == "L":    # 플루트 + 피치카토 — 바장조, 귀엽고 가벼운 마스코트 톤(2026-11-06 EX.06)
        BPM = 96; B = 60 / BPM; BAR = 4 * B
        prog = {0: 45, 1: 73, 2: 32, 3: 12}   # 0 피치카토 · 1 플루트 · 2 베이스 · 3 마림바
        ch_ = [(41, [53, 57, 60, 65]), (46, [53, 58, 62, 65]), (48, [52, 55, 60, 64]), (41, [53, 57, 60, 65])]   # F Bb C F
        mel = [[72, 0, 74, 72, 69, 0, 0, 0], [70, 0, 72, 70, 67, 0, 0, 0], [67, 0, 69, 70, 72, 0, 76, 0], [77, 0, 0, 0, 0, 0, 0, 0]]
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for i in range(4):
                t = b + i * B
                note(t, 0, root if i % 2 == 0 else up[0], 40, B * .4)
                for n in up[1:]: note(t + B / 2, 3, n, 24 - (6 if thin(t) else 0), B * .3)
            note(b, 2, root - 12 + 12, 46, B * 1.6)
            if k % 2 == 1:
                for i in range(8):
                    t = b + i * B / 2; m = mel[k % 4][i]
                    if m and not thin(t): note(t, 1, m, 34, B * .5)
            b += BAR; k += 1
        for j, n in enumerate((41, 53, 57, 60, 65)): ev.append((end + j * .03, 0, n, 44, 1.2))
        ev.append((end + .05, 1, 77, 34, 1.4))

    elif style == "M":    # 소프트 피아노 팝 — 내림마장조, 스타카토 4분 + 첼로 길게, 따뜻하고 단정하게(2026-11-06 EX.06)
        BPM = 90; B = 60 / BPM; BAR = 4 * B
        prog = {0: 0, 1: 42, 2: 32}   # 0 피아노 · 1 첼로 · 2 베이스
        ch_ = [(51, [55, 58, 63, 67]), (46, [53, 58, 62, 65]), (48, [55, 60, 63, 67]), (44, [56, 60, 63, 68])]   # Eb Bb Cm Ab
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for i in range(4):
                t = b + i * B
                for j, n in enumerate(up[1:]): note(t + j * .008, 0, n, (36 if i == 0 else 30) - (6 if thin(t) else 0), B * .45)
            note(b, 0, root, 40, B * 1.6)
            note(b, 1, root, 30, BAR + .05)
            note(b, 2, root - 12, 44, B * 1.8); note(b + 2 * B, 2, root - 12 + 7, 36, B * 1.5)
            b += BAR; k += 1
        for j, n in enumerate((39, 51, 55, 58, 63, 67)): ev.append((end + j * .03, 0, n, 40, 2.6))
        ev.append((end, 1, 51, 30, 2.6))

    else:                 # C 첼레스타 + 따뜻한 패드 — 작고 쓸쓸한 오르골 느낌
        BPM = 68; B = 60 / BPM; BAR = 4 * B
        prog = {0: 89, 1: 8, 2: 0}   # 0 웜 패드 · 1 첼레스타 · 2 피아노 베이스
        ch_ = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (43, [55, 59, 62])]
        mel = [[76, 0, 72, 74], [72, 0, 69, 67], [67, 72, 0, 76], [74, 0, 71, 0]]
        b = start; k = 0
        while b < end - .2:
            root, up = ch_[k % 4]
            for n in up: note(b, 0, n, 40, BAR + .1)
            note(b, 2, root, 46, BAR); note(b + 2 * B, 2, root + 7, 34, B * 2)
            for i in range(4):
                t = b + i * B; m = mel[k % 4][i]
                if m and not thin(t): note(t, 1, m + 12, 46, B * 1.5)
            b += BAR; k += 1
        for n in (48, 55, 60, 64): ev.append((end, 0, n, 40, 2.5))
        for j, n in enumerate((72, 76, 79, 84)): ev.append((end + j * .12, 1, n, 46, 1.5))

    return _render(ev, prog, dur, sr)
