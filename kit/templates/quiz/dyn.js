/* dyn.js — 원래 그림체에 '아주 살짝' 역동감 (2026-11-11 사용자: "원래 그림체에서 아주 살짝 역동적인 느낌만")
   index.html 맨 끝(<script src="dyn.js"></script>)에서 render(t) 를 감싼다. 모두 render 시각으로 정해진다(결정적).
   ① 장면 들어올 때: 장면 판이 1.03배에서 1배로 0.4초에 내려앉음(카메라가 툭 다가갔다 자리 잡는 느낌)
   ② 장면 동안: 판이 위로 아주 천천히 흐름(최대 8px) — 정지 화면처럼 굳어 있지 않게
   ③ 핵심 단어(숫자·판정) 때: 판이 1.6% 짧게 '쿵'(0.07초 올라갔다 0.35초에 돌아옴)
   ④ 말하는 캐릭터는 배경음 박(BPM)에 맞춰 3px 가볍게 들썩, 듣는 쪽은 1px
   크기는 일부러 작다 — 글자 안전 영역(아래 420·오른쪽 160)을 넘지 않게. */
(function () {
  const TLx = window.TL || {}; const T = TLx.T || {}; const L = TLx.lines || [];
  const BEAT = 60 / (TLx.BPM || 100);
  const KEY = ['wUse', 'wVoid', 'wNext', 'wRefuse', 'wOne', 'w55', 'wSubmit', 'stamp'].filter(k => T[k] != null).map(k => T[k]);
  const SC = Object.keys(T).filter(k => /^s\d$/.test(k)).map(k => [k, T[k]]).sort((a, b) => a[1] - b[1]);
  const eo = x => 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3);
  const who = t => { for (const l of L) if (t >= l.t - .05 && t < l.t + l.d) return l.who; return null; };
  const r0 = window.render;
  window.render = function (t) {
    r0(t);
    // 지금 장면과 그 시작·끝
    let i = -1; for (let k = 0; k < SC.length; k++) if (t >= SC[k][1]) i = k;
    const st = i >= 0 ? SC[i][1] : 0, en = i + 1 < SC.length ? SC[i + 1][1] : (T.END || t + 1);
    let s = 1 + .03 * (1 - eo((t - st) / .4));
    const dy = -8 * Math.max(0, Math.min(1, (t - st) / Math.max(1, en - st)));
    for (const k of KEY) { const d = t - k; if (d > -.07 && d < .35) s += .016 * (d < 0 ? (d + .07) / .07 : 1 - eo(d / .35)); }
    document.querySelectorAll('#stage>.scene').forEach(el => {
      if (getComputedStyle(el).visibility === 'hidden') return;
      el.style.transformOrigin = '540px 700px';
      el.style.transform = `translateY(${dy.toFixed(2)}px) scale(${s.toFixed(4)})`;
    });
    // 박에 맞춘 들썩임
    const ph = ((t % BEAT) + BEAT) % BEAT / BEAT, hop = Math.pow(Math.sin(Math.PI * ph), 2);
    const w = who(t);
    for (const [id, c] of [['dori', 'D'], ['mori', 'M']]) {
      const el = document.getElementById(id); if (!el) continue;
      const a = w === c ? 3 : 1;
      if (!/translateY\(-?[\d.]+px\)\s*$/.test(el.style.transform || '')) el.style.transform = (el.style.transform || '') + ` translateY(${(-a * hop).toFixed(2)}px)`;
    }
  };
})();
