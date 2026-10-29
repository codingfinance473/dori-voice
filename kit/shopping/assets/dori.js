// dori.js — 「도리의 가격 검산」 진행자 도리 2판(원작 캐릭터: 통통한 회색 햄스터, 민트 크로스백, 볼주머니).
// 사용자 수정안을 바탕으로 다시 그린 벡터 그림. 선 굵기·색이 하나라 어떤 크기로 키워도 또렷하다.
// Dori.mount(el) 로 SVG를 붙이고, Dori.pose(d, p) 로 한 프레임의 자세를 그린다. 같은 p면 항상 같은 그림.
// p: EXPR 의 값(eye·arc·lid·brow·browOp·cheek·blush·smile·mo·ear·sweat·excl) + armL·armR(도, 0=아래·+시계) + prop(영수증)
//    + mouth(말할 때 0~1) · blink(0~1) · breath · sway · jump · squash · lookX · lookY · earTw
(function () {
  const C = {
    out: '#4A3A33', furT: '#C2BBB6', fur: '#AEA6A1', furB: '#9D958F', stripe: '#8B817B', white: '#FFFDFB', whiteS: '#F1ECE8',
    earIn: '#F7A8AE', blush: '#FAA3AB', nose: '#EF8794', mouth: '#E5657A', tongue: '#F99DAB', feet: '#F8C4C7',
    bag: '#80D0BA', bagD: '#63BCA5', strap: '#5DB6A0', btn: '#FFF4D4', eye: '#271B17', shadow: '#6B4F36', red: '#FF5A5A', sweat: '#9FD6F5'
  };
  const SW = 6.5;
  const BODY = 'M200,86 C282,86 338,134 346,200 C350,236 346,262 338,288 C352,330 342,398 262,402 L138,402 C58,398 48,330 62,288 C54,262 50,236 54,200 C62,134 118,86 200,86 Z';
  const ARM = 'M-23,0 L-23,35 A23,23 0 0 0 23,35 L23,0 A23,23 0 0 0 -23,0 Z';   // 길이 58·폭 46, 끝은 흰 발
  const SH = { L: [72, 292], R: [328, 292] };
  let uid = 0;

  function eye(u, s, cx) {
    return `<g class="eye${s}" transform="translate(${cx},214)">
      <clipPath id="${u}-ec${s}"><rect class="ecr" x="-28" y="-30" width="56" height="62"/></clipPath>
      <g class="eo" clip-path="url(#${u}-ec${s})"><g class="eos"><ellipse rx="17" ry="19" fill="${C.eye}"/>
        <circle cx="-5.5" cy="-6.5" r="6.8" fill="#fff"/><circle cx="6" cy="6.5" r="3" fill="#fff"/></g></g>
      <path class="lidl" d="M-19,0 L19,0" stroke="${C.out}" stroke-width="6" stroke-linecap="round" opacity="0"/>
      <path class="arc" d="M-15,5 Q0,-13 15,5" stroke="${C.out}" stroke-width="7" stroke-linecap="round" fill="none" opacity="0"/>
      <path class="shut" d="M-16,-1 Q0,11 16,-1" stroke="${C.out}" stroke-width="7" stroke-linecap="round" fill="none" opacity="0"/>
    </g>`;
  }
  function arm(u, s) {
    return `<g class="arm${s}"><clipPath id="${u}-ac${s}"><path d="${ARM}"/></clipPath><path d="${ARM}" fill="${C.fur}"/>
      <g clip-path="url(#${u}-ac${s})"><rect x="-27" y="31" width="54" height="36" fill="${C.white}"/></g>
      <path d="${ARM}" fill="none" stroke="${C.out}" stroke-width="${SW}" stroke-linejoin="round"/></g>`;
  }
  function paw(x, y, rot) {
    return `<g transform="translate(${x},${y}) rotate(${rot}) scale(.88)">
      <path d="M-25,12 L-25,0 A25,25 0 0 1 25,0 L25,12 Q25,22 15,22 L-15,22 Q-25,22 -25,12 Z" fill="${C.white}" stroke="${C.out}" stroke-width="${SW}" stroke-linejoin="round"/>
      <path d="M-7,-14 L-7,-4 M7,-14 L7,-4" stroke="${C.stripe}" stroke-width="3.2" stroke-linecap="round"/></g>`;
  }
  function svg(u) {
    const zz = [...Array(9)].map((_, i) => `L${150 + i * 12.5},${372 + (i % 2 ? 6 : 0)}`).join(' ');
    return `<svg viewBox="0 0 400 430" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <defs>
    <linearGradient id="${u}-fur" x1="0" y1="86" x2="0" y2="402" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="${C.furT}"/><stop offset=".55" stop-color="${C.fur}"/><stop offset="1" stop-color="${C.furB}"/></linearGradient>
    <radialGradient id="${u}-wh" cx="200" cy="300" r="170" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="${C.white}"/><stop offset=".78" stop-color="${C.white}"/><stop offset="1" stop-color="${C.whiteS}"/></radialGradient>
    <clipPath id="${u}-bc"><path d="${BODY}"/><circle class="ckLc" cx="84" cy="262" r="0"/><circle class="ckRc" cx="316" cy="262" r="0"/></clipPath>
  </defs>
  <ellipse class="shadow" cx="200" cy="414" rx="132" ry="14" fill="${C.shadow}" opacity=".15"/>
  <g class="jump"><g class="squash"><g class="sway"><g class="breath">
    <g class="earL"><circle cx="122" cy="118" r="38" fill="${C.furT}" stroke="${C.out}" stroke-width="${SW}"/><circle cx="127" cy="124" r="23" fill="${C.earIn}"/></g>
    <g class="earR"><circle cx="278" cy="118" r="38" fill="${C.furT}" stroke="${C.out}" stroke-width="${SW}"/><circle cx="273" cy="124" r="23" fill="${C.earIn}"/></g>
    <g fill="${C.out}" stroke="${C.out}" stroke-width="${SW * 2}" stroke-linejoin="round"><path d="${BODY}"/>
      <circle class="ckLo" cx="84" cy="262" r="0"/><circle class="ckRo" cx="316" cy="262" r="0"/></g>
    <path d="${BODY}" fill="url(#${u}-fur)"/>
    <circle class="ckLf" cx="84" cy="262" r="0" fill="${C.white}"/><circle class="ckRf" cx="316" cy="262" r="0" fill="${C.white}"/>
    <g clip-path="url(#${u}-bc)"><ellipse class="mz" cx="200" cy="260" rx="124" ry="52" fill="url(#${u}-wh)"/>
      <ellipse cx="200" cy="340" rx="104" ry="82" fill="url(#${u}-wh)"/></g>
    <g stroke="${C.stripe}" stroke-linecap="round" fill="none" opacity=".85">
      <path d="M198,96 C192,118 192,138 196,160" stroke-width="7.5"/><path d="M220,100 C216,113 216,125 219,137" stroke-width="5.5"/></g>
    <ellipse cx="150" cy="124" rx="34" ry="14" fill="#fff" opacity=".16" transform="rotate(-22,150,124)"/>
    <g class="face">
      <ellipse class="blL" cx="134" cy="254" rx="24" ry="15" fill="${C.blush}"/><ellipse class="blR" cx="266" cy="254" rx="24" ry="15" fill="${C.blush}"/>
      <g stroke="${C.stripe}" stroke-width="2.6" stroke-linecap="round"><path class="wL" d="M104,242 L142,247 M102,256 L140,256"/>
        <path class="wR" d="M296,242 L258,247 M298,256 L260,256"/></g>
      ${eye(u, 'L', 148)}${eye(u, 'R', 252)}
      <g stroke="${C.out}" stroke-width="4.8" stroke-linecap="round" fill="none">
        <path class="browL" d="M134,184 Q149,180 164,184" opacity="0"/><path class="browR" d="M266,184 Q251,180 236,184" opacity="0"/></g>
      <path d="M191,233 Q200,228 209,233 Q208,240 200,243 Q192,240 191,233 Z" fill="${C.nose}" stroke="${C.out}" stroke-width="3" stroke-linejoin="round"/>
      <path d="M200,242 L200,248" stroke="${C.out}" stroke-width="4.2" stroke-linecap="round"/>
      <path class="mc" d="" fill="none" stroke="${C.out}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
      <g class="mOpen" opacity="0"><path class="mo" d="" fill="${C.mouth}" stroke="${C.out}" stroke-width="4.2" stroke-linejoin="round"/>
        <ellipse class="tg" cx="200" cy="270" rx="8" ry="5" fill="${C.tongue}"/></g>
    </g>
    ${arm(u, 'R')}
    <path d="M84,304 Q190,318 290,346" stroke="${C.out}" stroke-width="13" stroke-linecap="round" fill="none"/>
    <path d="M84,304 Q190,318 290,346" stroke="${C.strap}" stroke-width="7.5" stroke-linecap="round" fill="none"/>
    <rect x="266" y="334" width="70" height="52" rx="13" fill="${C.bag}" stroke="${C.out}" stroke-width="5"/>
    <path d="M266,348 Q266,334 279,334 L323,334 Q336,334 336,348 L336,355 Q301,368 266,355 Z" fill="${C.bagD}" stroke="${C.out}" stroke-width="4.5" stroke-linejoin="round"/>
    <circle cx="301" cy="361" r="5" fill="${C.btn}" stroke="${C.out}" stroke-width="2.5"/>
    ${arm(u, 'L')}
    <g class="prop" opacity="0"><g transform="rotate(-6,200,320)">
      <path d="M150,262 L250,262 L250,372 ${zz} Z" fill="#fff" stroke="${C.out}" stroke-width="5" stroke-linejoin="round"/>
      <g stroke="#BDB3AA" stroke-width="5" stroke-linecap="round"><path d="M166,286 L234,286"/><path d="M166,304 L222,304"/><path d="M166,322 L234,322"/>
        <path d="M166,344 L210,344" stroke="#FF6B5E"/></g></g>
      ${paw(150, 306, -84)}${paw(250, 300, 84)}</g>
    <ellipse cx="158" cy="404" rx="28" ry="13.5" fill="${C.feet}" stroke="${C.out}" stroke-width="5"/>
    <ellipse cx="242" cy="404" rx="28" ry="13.5" fill="${C.feet}" stroke="${C.out}" stroke-width="5"/>
    <path class="sweat" d="M356,178 Q370,196 356,206 Q342,196 356,178 Z" fill="${C.sweat}" stroke="${C.out}" stroke-width="3.5" opacity="0"/>
    <g class="excl" opacity="0"><g transform="translate(40,104) rotate(-10)"><rect x="-9" y="-34" width="18" height="44" rx="9" fill="${C.red}"/><circle cy="24" r="9" fill="${C.red}"/></g>
      <g transform="translate(74,100) rotate(-4)"><rect x="-9" y="-34" width="18" height="44" rx="9" fill="${C.red}"/><circle cy="24" r="9" fill="${C.red}"/></g></g>
  </g></g></g></g>
</svg>`;
  }

  function mount(el) {
    const u = 'd' + (++uid);
    el.innerHTML = svg(u);
    const q = s => el.querySelector(s);
    const d = { u, el, svg: q('svg') };
    ['shadow', 'jump', 'squash', 'sway', 'breath', 'earL', 'earR', 'face', 'blL', 'blR', 'wL', 'wR', 'browL', 'browR', 'mc', 'mOpen', 'mo', 'tg',
      'mz', 'ckLc', 'ckRc', 'ckLo', 'ckRo', 'ckLf', 'ckRf', 'armL', 'armR', 'prop', 'sweat', 'excl', 'eyeL', 'eyeR'].forEach(k => d[k] = q('.' + k));
    return d;
  }

  const f = (x, n = 2) => (+x).toFixed(n);
  function setEye(g, p) {
    const k = p.eye ?? 1, arc = Math.min(1, Math.max(0, p.arc || 0)), b = Math.min(1, Math.max(0, p.blink || 0));
    const lid = Math.min(1, Math.max(0, p.lid || 0)), open = 1 - arc;
    const sy = Math.max(0.08, 1 - b * 0.92);
    const lx = (p.lookX || 0) * 2.6, ly = (p.lookY || 0) * 2;
    g.querySelector('.eos').setAttribute('transform', `translate(${f(lx)},${f(ly)}) scale(${f(k, 3)},${f(k * sy, 3)})`);
    const top = -19 * k + lid * 21 * k;                       // 집중: 위 눈꺼풀이 내려와 눈 위쪽이 잘린다
    g.querySelector('.ecr').setAttribute('y', f(top));
    g.querySelector('.eo').setAttribute('opacity', f(open * (b > 0.75 ? Math.max(0, 1 - (b - 0.75) * 4) : 1)));
    const ll = g.querySelector('.lidl');
    ll.setAttribute('transform', `translate(${f(lx)},${f(top + ly)})`); ll.setAttribute('opacity', f(open * Math.min(1, lid * 4) * (1 - b)));
    g.querySelector('.arc').setAttribute('opacity', f(arc));
    g.querySelector('.shut').setAttribute('opacity', f(open * (b > 0.6 ? Math.min(1, (b - 0.6) * 3) : 0)));
  }

  function pose(d, p) {
    const br = 1 + (p.breath || 0) * 0.014;
    d.breath.setAttribute('transform', `translate(200,412) scale(${f(2 - br, 4)},${f(br, 4)}) translate(-200,-412)`);
    d.sway.setAttribute('transform', `rotate(${f(p.sway || 0)},200,412)`);
    const j = p.jump || 0, sq = p.squash || 0;
    d.jump.setAttribute('transform', `translate(0,${f(-j, 1)})`);
    d.squash.setAttribute('transform', `translate(200,412) scale(${f(1 + sq * 0.12, 3)},${f(1 - sq * 0.12, 3)}) translate(-200,-412)`);
    d.shadow.setAttribute('rx', f(132 * (1 - Math.min(j, 120) / 300), 1));
    d.shadow.setAttribute('opacity', f(0.15 * (1 - Math.min(j, 120) / 200), 3));
    const ear = (p.ear || 0) * 16, tw = p.earTw || 0;
    d.earL.setAttribute('transform', `rotate(${f(-ear - tw, 1)},122,150)`);
    d.earR.setAttribute('transform', `rotate(${f(ear + tw * 0.6, 1)},278,150)`);
    d.face.setAttribute('transform', `translate(${f((p.lookX || 0) * 3)},${f((p.lookY || 0) * 2)})`);
    // 볼주머니: 양 볼이 부풀고 흰 주둥이·홍조·수염이 바깥으로
    const c = Math.min(1, Math.max(0, p.cheek || 0)), r = f(58 * c, 1);
    for (const k of ['ckLc', 'ckRc', 'ckLo', 'ckRo', 'ckLf', 'ckRf']) d[k].setAttribute('r', r);
    d.mz.setAttribute('rx', f(124 + 52 * c, 1)); d.mz.setAttribute('ry', f(52 + 10 * c, 1)); d.mz.setAttribute('cy', f(260 + 2 * c, 1));
    const bl = p.blush ?? 0.85;
    d.blL.setAttribute('opacity', f(bl)); d.blR.setAttribute('opacity', f(bl));
    d.blL.setAttribute('cx', f(134 - 36 * c, 1)); d.blR.setAttribute('cx', f(266 + 36 * c, 1));
    d.blL.setAttribute('rx', f(24 + 12 * c, 1)); d.blR.setAttribute('rx', f(24 + 12 * c, 1));
    d.wL.setAttribute('transform', `translate(${f(-36 * c, 1)},0)`); d.wR.setAttribute('transform', `translate(${f(36 * c, 1)},0)`);
    setEye(d.eyeL, p); setEye(d.eyeR, p);
    const bw = p.brow || 0, bo = p.browOp || 0;
    d.browL.setAttribute('opacity', f(bo)); d.browR.setAttribute('opacity', f(bo));
    d.browL.setAttribute('transform', `translate(0,${f(-Math.max(0, -bw) * 5 + Math.max(0, bw) * 2, 1)}) rotate(${f(bw * 12, 1)},149,182)`);
    d.browR.setAttribute('transform', `translate(0,${f(-Math.max(0, -bw) * 5 + Math.max(0, bw) * 2, 1)}) rotate(${f(-bw * 12, 1)},251,182)`);
    // 입: 말할 때·놀랄 때 열림, 닫힌 입은 smile(웃음 w ~ 일자 ~ 시무룩)
    const open = Math.max((p.mouth || 0) * 0.95, p.mo || 0);
    if (open > 0.06) {
      const w = 12 + open * 5, dep = 7 + open * 22, nar = (p.mo || 0) > (p.mouth || 0) ? 0.72 : 1, ww = w * nar;
      d.mo.setAttribute('d', `M${f(200 - ww, 1)},247 Q${f(200 - ww / 2, 1)},253 200,248 Q${f(200 + ww / 2, 1)},253 ${f(200 + ww, 1)},247 ` +
        `Q${f(200 + ww * 0.96, 1)},${f(247 + dep, 1)} 200,${f(249 + dep, 1)} Q${f(200 - ww * 0.96, 1)},${f(247 + dep, 1)} ${f(200 - ww, 1)},247 Z`);
      d.tg.setAttribute('cy', f(246 + dep * 0.84, 1)); d.tg.setAttribute('rx', f(ww * 0.52, 1)); d.tg.setAttribute('ry', f(Math.min(5.5, dep * 0.22), 1));
      d.tg.setAttribute('opacity', dep > 14 ? '1' : '0');
      d.mOpen.setAttribute('opacity', '1'); d.mc.setAttribute('opacity', '0');
    } else {
      const s = p.smile ?? 0.6;
      let path;
      if (s >= 0.2) { const a = (s - 0.2) / 0.8; path = `M184,${f(247 - a, 1)} Q192,${f(253 + a * 2, 1)} 200,248 Q208,${f(253 + a * 2, 1)} 216,${f(247 - a, 1)}`; }
      else if (s > -0.2) path = 'M190,256 L210,256';
      else { const a = (-s - 0.2) / 0.8; path = `M187,${f(258 + a * 4, 1)} Q200,${f(254 - a * 6, 1)} 213,${f(258 + a * 4, 1)}`; }
      d.mc.setAttribute('d', path); d.mc.setAttribute('opacity', '1'); d.mOpen.setAttribute('opacity', '0');
    }
    // 팔(어깨 기준 회전), 영수증을 들면 팔 대신 영수증 위 앞발
    const pr = Math.min(1, Math.max(0, p.prop || 0));
    d.armL.setAttribute('transform', `translate(${SH.L[0]},${SH.L[1]}) rotate(${f(p.armL ?? -32, 1)})`);
    d.armR.setAttribute('transform', `translate(${SH.R[0]},${SH.R[1]}) rotate(${f(p.armR ?? 32, 1)})`);
    d.armL.setAttribute('opacity', f(1 - pr)); d.armR.setAttribute('opacity', f(1 - pr));
    d.prop.setAttribute('opacity', f(pr));
    d.prop.setAttribute('transform', `translate(200,330) scale(${f(0.6 + pr * 0.4, 3)}) translate(-200,-330)`);
    d.sweat.setAttribute('opacity', f(p.sweat || 0));
    d.excl.setAttribute('opacity', f(p.excl || 0));
  }

  // 팔 각도: 0 = 아래, + = 시계 방향(화면 기준). prop = 영수증
  const ARMS = {
    rest: { l: -32, r: 32, prop: 0 },
    hold: { l: -64, r: 64, prop: 1 },
    point: { l: -32, r: -132, prop: 0 },
    up: { l: 146, r: -146, prop: 0 },
    wave: { l: -32, r: -140, prop: 0 },
    think: { l: -32, r: 122, prop: 0 },
    cheeks: { l: -158, r: 158, prop: 0 }
  };
  // 표정: eye(크기) arc(웃는 눈 ∩) lid(위 눈꺼풀) brow(+안쪽 내림 / -안쪽 올림) browOp cheek(볼주머니) blush smile(1 웃음 w, 0 일자, -1 시무룩) mo(놀라 벌린 입) ear(처짐) sweat excl
  const EXPR = {
    neutral:  { eye: 1.00, arc: 0, lid: 0.00, brow: 0.0, browOp: 0.0, cheek: 0, blush: 0.85, smile: 0.6, mo: 0.00, ear: 0, sweat: 0, excl: 0 },
    happy:    { eye: 1.00, arc: 1, lid: 0.00, brow: 0.0, browOp: 0.0, cheek: 0, blush: 1.00, smile: 1.0, mo: 0.00, ear: 0, sweat: 0, excl: 0 },
    focus:    { eye: 1.00, arc: 0, lid: 0.55, brow: 0.6, browOp: 1.0, cheek: 0, blush: 0.60, smile: 0.0, mo: 0.00, ear: 0, sweat: 0, excl: 0 },
    surprise: { eye: 1.12, arc: 0, lid: 0.00, brow: -0.6, browOp: 0.9, cheek: 0, blush: 0.80, smile: 0.0, mo: 0.55, ear: -0.3, sweat: 0, excl: 1 },
    sad:      { eye: 0.96, arc: 0, lid: 0.15, brow: -1.0, browOp: 1.0, cheek: 0, blush: 0.50, smile: -1.0, mo: 0.00, ear: 1, sweat: 1, excl: 0 },
    stuff:    { eye: 1.00, arc: 1, lid: 0.00, brow: 0.0, browOp: 0.0, cheek: 1, blush: 1.00, smile: 0.3, mo: 0.00, ear: 0, sweat: 0, excl: 0 }
  };
  function mix(a, b, k) { const o = {}; for (const key in a) o[key] = a[key] + ((b[key] ?? a[key]) - a[key]) * k; return o; }
  window.Dori = { mount, pose, EXPR, ARMS, mix };
})();
