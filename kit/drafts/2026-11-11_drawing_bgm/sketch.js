/* sketch.js — 도리 쇼츠 '손그림(드로잉) 느낌' 층 (시안 2026-11-11)
   index.html 맨 끝에 <script>window.SKETCH={style:'A'}</script><script src="sketch.js"></script>
   style: '0' 지금 그대로 · 'A' 연필 스케치 · 'B' 색연필(크레용) · 'C' 그림책 수채
   하는 일
   ① 선 흔들림 + 선 끓임(boil): 외곽선이 손으로 그린 것처럼 살짝 울퉁불퉁하고, 초당 8번 미세하게 바뀐다(손그림 애니메이션 특유의 살아 있는 선).
   ② 겹선: 같은 그림을 다른 흔들림으로 한 번 더 옅게 — 연필로 두세 번 그은 선.
   ③ 종이: 화면 전체에 종이 결(곱하기) — 벽·카드·캐릭터가 한 장의 종이 위에 그려진 것처럼 묶인다.
   ④ 낙서: 벽 여백에 연필 별·소용돌이·반짝이, 마루에 연필 결 — 빈 곳을 '그린 것'으로 채운다.
   글자(말풍선·자막·숫자)는 흔들림을 아주 작게만 — 읽기가 먼저다. */
(function () {
  const S = (window.SKETCH && window.SKETCH.style) || 'A';
  if (S === '0') return;
  const CFG = {
    A: { hatch: .6, hw: 1.6, line: 4.2, freq: .032, dbl: .38, txt: 1.6, grain: 0, wash: 0, paper: .55, paperF: .85, doodle: .42, sat: 1 },
    B: { hatch: .55, hw: 2.6, line: 4.6, freq: .036, dbl: .30, txt: 1.8, grain: .34, wash: 0, paper: .70, paperF: .62, doodle: .45, sat: .96 },
    C: { hatch: 0, pig: 1, line: 3.6, freq: .028, dbl: .22, txt: 1.4, grain: 0, wash: .42, paper: .80, paperF: .45, doodle: .30, sat: .92 },
  }[S];
  const turb = (id, f, seed, oct = 2) => `<feTurbulence class="skb" data-s0="${seed}" type="fractalNoise" baseFrequency="${f}" numOctaves="${oct}" seed="${seed}" result="${id}"/>`;
  const build = (fid, H) => {
  let art = `<filter id="${fid}" x="-6%" y="-6%" width="112%" height="112%" color-interpolation-filters="sRGB">
    ${turb('n1', CFG.freq, 1)}
    <feDisplacementMap in="SourceGraphic" in2="n1" scale="${CFG.line}" xChannelSelector="R" yChannelSelector="G" result="d1"/>
    ${turb('n2', CFG.freq * 1.3, 7)}
    <feDisplacementMap in="SourceGraphic" in2="n2" scale="${CFG.line * 1.5}" xChannelSelector="G" yChannelSelector="R" result="d2"/>
    <feOffset in="d2" dx="1.4" dy="1.1" result="d2o"/>
    <feComponentTransfer in="d2o" result="d2f"><feFuncA type="linear" slope="${CFG.dbl}"/></feComponentTransfer>`;
  if (CFG.wash) art += `
    ${turb('n3', .012, 4, 3)}
    <feGaussianBlur in="SourceGraphic" stdDeviation="2.4" result="bl"/>
    <feDisplacementMap in="bl" in2="n3" scale="16" xChannelSelector="R" yChannelSelector="B" result="wsh"/>
    <feOffset in="wsh" dx="-5" dy="4" result="wsho"/>
    <feColorMatrix in="wsho" type="saturate" values="1.25" result="wshs"/>
    <feComponentTransfer in="wshs" result="wshf"><feFuncA type="linear" slope="${CFG.wash}"/></feComponentTransfer>`;
  const hsvg = `<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14'><path d='M-2 16 L16 -2 M-9 9 L9 -9 M5 23 L23 5' stroke='#5A4638' stroke-width='${CFG.hw || 1.6}' stroke-linecap='round'/></svg>`;
  if (H && CFG.hatch) art += `
    <feOffset in="SourceAlpha" dx="-20" dy="-15" result="sa"/>
    <feComposite in="SourceAlpha" in2="sa" operator="out" result="band0"/>
    <feGaussianBlur in="band0" stdDeviation="3" result="band1"/>
    <feComposite in="band1" in2="SourceAlpha" operator="in" result="band"/>
    <feTurbulence type="turbulence" baseFrequency="0.006 ${CFG.hw > 2 ? .16 : .22}" numOctaves="1" seed="9" result="hr"/>
    <feColorMatrix in="hr" type="matrix" values="0 0 0 0 .35  0 0 0 0 .27  0 0 0 0 .22  22 0 0 0 -2.4" result="ht"/>
    <feDisplacementMap in="ht" in2="n2" scale="7" xChannelSelector="R" yChannelSelector="G" result="htw"/>
    <feComposite in="htw" in2="band" operator="in" result="hb"/>
    <feComponentTransfer in="hb" result="hf"><feFuncA type="linear" slope="${CFG.hatch}"/></feComponentTransfer>
    <feDisplacementMap in="hf" in2="n1" scale="${CFG.line}" xChannelSelector="R" yChannelSelector="G" result="hfd"/>`;
  art += `<feMerge result="m">${CFG.wash ? '<feMergeNode in="wshf"/>' : ''}<feMergeNode in="d2f"/><feMergeNode in="d1"/>${H && CFG.hatch ? '<feMergeNode in="hfd"/>' : ''}</feMerge>`;
  if (CFG.grain) art += `
    <feTurbulence type="fractalNoise" baseFrequency="1.1 .55" numOctaves="1" seed="3" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 1.55" result="ga"/>
    <feComposite in="m" in2="ga" operator="in" result="gm"/>
    <feComponentTransfer in="m" result="mt"><feFuncA type="linear" slope="${1 - CFG.grain}"/></feComponentTransfer>
    <feMerge result="m2"><feMergeNode in="mt"/><feMergeNode in="gm"/></feMerge>`;
  if (CFG.pig) art += `
    <feTurbulence type="fractalNoise" baseFrequency=".011" numOctaves="3" seed="21" result="pg"/>
    <feColorMatrix in="pg" type="matrix" values=".12 0 0 0 .9  .12 0 0 0 .9  .12 0 0 0 .91  0 0 0 0 1" result="pgl"/>
    <feBlend in="m" in2="pgl" mode="multiply" result="pm0"/>
    <feComposite in="pm0" in2="m" operator="in" result="pm"/>`;
  art += `<feColorMatrix in="${CFG.pig ? 'pm' : CFG.grain ? 'm2' : 'm'}" type="saturate" values="${CFG.sat}"/></filter>`;
  return art; };
  const art = build('skArt', true) + build('skCard', false);
  // 글자 들어간 카드·말풍선·제목용(아주 작게)
  const txt = `<filter id="skTxt" x="-4%" y="-8%" width="108%" height="116%">
    ${turb('t1', .04, 2, 1)}<feDisplacementMap in="SourceGraphic" in2="t1" scale="${CFG.txt}" xChannelSelector="R" yChannelSelector="G"/></filter>`;
  const D = document.createElement('div');
  D.innerHTML = `<svg width="0" height="0" style="position:absolute"><defs>${art}${txt}</defs></svg>`;
  document.body.prepend(D.firstChild);

  const st = document.createElement('style');
  st.textContent = `
    #dori>svg,#mori>svg,#dori svg,#mori svg{filter:url(#skArt)}
    .scene .card,.scene [id$="Art"],.scene .res,.scene #st3a,.scene #st3b,.scene #tray5,.scene .yr,.scene #gl2,.scene #use2,.scene #stamp8{filter:url(#skCard)}
    .ttl,.bub,.chip,#hdr,.scene #c5 .r,.scene .tot{filter:url(#skTxt)}
    #skPaper{position:absolute;inset:0;z-index:60;pointer-events:none;mix-blend-mode:multiply}
    #skDoodle{position:absolute;inset:0;z-index:1;pointer-events:none}
    .card,.res{box-shadow:6px 9px 0 rgba(74,58,51,.18)!important}
  `;
  document.head.appendChild(st);

  // ③ 종이 — 결(고주파) + 얼룩(저주파). 정적(종이는 끓지 않는다)
  const paperSvg = `<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='1920'>
    <filter id='p'><feTurbulence type='fractalNoise' baseFrequency='${CFG.paperF}' numOctaves='3' seed='11'/>
    <feColorMatrix values='0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .36  0 0 0 -1.1 .62'/></filter>
    <filter id='q'><feTurbulence type='fractalNoise' baseFrequency='.006' numOctaves='3' seed='5'/>
    <feColorMatrix values='0 0 0 0 .78  0 0 0 0 .62  0 0 0 0 .45  0 0 0 -1.4 .78'/></filter>
    <rect width='1080' height='1920' filter='url(#q)' opacity='.55'/>
    <rect width='1080' height='1920' filter='url(#p)'/></svg>`;
  const paper = document.createElement('div');
  paper.id = 'skPaper';
  paper.style.background = `url("data:image/svg+xml;utf8,${encodeURIComponent(paperSvg)}")`;
  paper.style.opacity = CFG.paper;
  const stage = document.getElementById('stage');
  stage.appendChild(paper);

  // ④ 낙서 — 연필 선(갈색 회색, 끝이 가늘게), 벽 여백과 마루
  const P = 'stroke="#6B5A4E" stroke-linecap="round" stroke-linejoin="round" fill="none"';
  const star = (x, y, r, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot})"><path d="M0 ${-r} L${r * .28} ${-r * .3} L${r} ${-r * .2} L${r * .42} ${r * .22} L${r * .6} ${r} L0 ${r * .55} L${-r * .6} ${r} L${-r * .42} ${r * .22} L${-r} ${-r * .2} L${-r * .28} ${-r * .3} Z" ${P} stroke-width="3.2"/><path d="M${-r * .1} ${-r * .75} L${r * .2} ${-r * .35}" ${P} stroke-width="2" opacity=".6"/></g>`;
  const spark = (x, y, r) => `<g transform="translate(${x} ${y})"><path d="M0 ${-r} V${r} M${-r} 0 H${r} M${-r * .55} ${-r * .55} L${r * .55} ${r * .55} M${r * .55} ${-r * .55} L${-r * .55} ${r * .55}" ${P} stroke-width="3"/></g>`;
  const swirl = (x, y, s) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0 0 c10 -14 30 -6 26 10 c-4 18 -32 18 -36 -4 c-4 -26 30 -40 52 -22 c18 16 12 46 -8 58" ${P} stroke-width="${3 / s}"/>`;
  const dash = (x, y, a, n = 3) => { let s = ''; for (let i = 0; i < n; i++) s += `<path d="M${x + i * 14} ${y - i * 4} l${18 * Math.cos(a)} ${18 * Math.sin(a)}" ${P} stroke-width="3.4"/>`; return s; };
  const cloud = (x, y, s) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0 30 c-18 0 -22 -24 -4 -28 c2 -18 26 -24 36 -10 c8 -14 34 -10 34 8 c18 0 20 30 0 30 Z" ${P} stroke-width="${3 / s}"/>`;
  // 마루(나무) 연필 결 — 짧은 해칭과 나무결 곡선
  let floor = '';
  for (let i = 0; i < 9; i++) { const x = 40 + i * 118 + (i % 2) * 30, y = 1520 + (i * 53) % 330; floor += `<path d="M${x} ${y} q40 -8 80 0 t80 0" ${P} stroke-width="2.6" opacity=".55"/>`; }
  for (let i = 0; i < 14; i++) { const x = 30 + i * 76, y = 1490 + (i * 97) % 380; for (let k = 0; k < 4; k++) floor += `<path d="M${x + k * 9} ${y} l-14 22" ${P} stroke-width="2.2" opacity=".42"/>`; }
  const doodle = document.createElement('div');
  doodle.id = 'skDoodle';
  doodle.style.opacity = CFG.doodle;
  doodle.innerHTML = `<svg width="1080" height="1920" viewBox="0 0 1080 1920">
    ${star(980, 120, 26, 12)}${spark(930, 196, 12)}${swirl(1000, 300, .9)}
    ${spark(40, 268, 10)}${star(34, 1010, 20, -10)}${dash(12, 1080, -.6)}
    ${cloud(450, 1150, 1.1)}${spark(560, 1090, 13)}${star(610, 1240, 18, 18)}
    ${swirl(1010, 1000, .7)}${spark(1040, 1380, 10)}
    ${floor}</svg>`;
  stage.querySelector('.sk-wall') ? stage.querySelector('.sk-wall').after(doodle) : stage.prepend(doodle);

  // ① 선 끓임 — 초당 8번, 세 장 돌려 쓰기(같은 시각은 늘 같은 그림 — 렌더가 결정적)
  const tb = [...document.querySelectorAll('feTurbulence.skb')];
  const r0 = window.render;
  window.render = function (t) {
    const k = Math.floor(t * 8) % 3;
    for (const e of tb) e.setAttribute('seed', +e.dataset.s0 + k * 13);
    return r0(t);
  };
})();
