"""배경음을 사운드폰트(General MIDI, TimGM6mb.sf2)로 연주한다 — 직접 합성한 우쿨렐레 대신 실제 악기 소리.
필요: libfluidsynth(이미 깔려 있음) + `pip install pyfluidsynth --break-system-packages`.

make(style, start, end, dur, sr, thin, quiet) -> (N, 2) float 배열
  style  A 피아노 발라드 · B 로파이 일렉피아노 · C 첼레스타 + 패드
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
