/*
  scenekit.js — 도리 화면 그림 키트 (2026-11-07, 사용자 의견 "영상 이미지가 너무 단순하고 붙여 넣은 느낌")
  원칙
   1. 무대가 있다: 벽(잔무늬) · 위 차양 · 아래 탁자(식탁보) — 도리와 소품이 '어딘가에 놓여' 있게.
   2. 빛은 왼쪽 위에서: 모든 소품은 왼쪽 위 밝게·오른쪽 아래 어둡게(그라데이션), 하이라이트 한 줄, 바닥 그림자(타원).
   3. 도리와 같은 그림체: 외곽선 #4A3A33 6~7px, 둥근 끝. 카드도 같은 외곽선 + 아래로 떨어지는 단색 그림자(스티커 느낌).
   4. 소품은 크게, 결·주름·무늬로 '사물'로 보이게(배추 잎맥, 무 잔뿌리, 대파 묶음 끈, 젓갈 새우 마디).
  쓰는 법: <script src="scenekit.js"></script> 뒤에 SK.defs(); SK.stage(document.getElementById('stage'), {awning:true, table:'gingham'})
          소품: SK.cabbage(w) · SK.half(w) · SK.radish(w) · SK.pa(w) · SK.jar(w) · SK.basin(w) · SK.crate(w,'cabbage'|'radish') · SK.scale(w) · SK.house(w,fill,id) · SK.tub(w) · SK.cocoaBean(w,face,rot) · SK.cocoaBowl(w)
          바닥 그림자: SK.ground(w) — 소품 아래에 깔 타원 SVG
*/
const SK = (() => {
  const K = '#4A3A33';
  const defs = () => {
    if (document.getElementById('skDefs')) return;
    const d = document.createElement('div');
    d.innerHTML = `<svg id="skDefs" width="0" height="0" style="position:absolute"><defs>
      <linearGradient id="skCabLeaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#C3EA94"/><stop offset=".55" stop-color="#8FCB60"/><stop offset="1" stop-color="#5E9E3E"/></linearGradient>
      <linearGradient id="skCabLeafL" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E2F6BF"/><stop offset="1" stop-color="#A9DA7A"/></linearGradient>
      <linearGradient id="skCabWhite" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#FBF6E2"/><stop offset="1" stop-color="#E6DDBB"/></linearGradient>
      <radialGradient id="skCabCore" cx=".62" cy=".5" r=".6"><stop offset="0" stop-color="#F7D768"/><stop offset=".55" stop-color="#FBE8A6"/><stop offset="1" stop-color="#FFF6D6"/></radialGradient>
      <linearGradient id="skRad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#F8F6EE"/><stop offset="1" stop-color="#DCD7C6"/></linearGradient>
      <linearGradient id="skRadTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B7DE8A"/><stop offset="1" stop-color="#B7DE8A" stop-opacity="0"/></linearGradient>
      <linearGradient id="skLeaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9AD77A"/><stop offset="1" stop-color="#4E9E44"/></linearGradient>
      <linearGradient id="skPa" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".42" stop-color="#F1F6E4"/><stop offset=".5" stop-color="#A7DB83"/><stop offset="1" stop-color="#4F9E45"/></linearGradient>
      <linearGradient id="skGlass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F4FBFC"/><stop offset=".5" stop-color="#E3F1F4"/><stop offset="1" stop-color="#C9DFE4"/></linearGradient>
      <linearGradient id="skShrimpBed" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBD9CB"/><stop offset="1" stop-color="#EE9F86"/></linearGradient>
      <linearGradient id="skLid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FC1A5"/><stop offset="1" stop-color="#23826C"/></linearGradient>
      <linearGradient id="skBasin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F26E5F"/><stop offset="1" stop-color="#C5352A"/></linearGradient>
      <linearGradient id="skWood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E2B27C"/><stop offset="1" stop-color="#BC814B"/></linearGradient>
      <linearGradient id="skMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#ECE6DE"/><stop offset="1" stop-color="#CFC6BB"/></linearGradient>
      <linearGradient id="skRoof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0816F"/><stop offset="1" stop-color="#C9493A"/></linearGradient>
      <linearGradient id="skRoofOff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D8CFC6"/><stop offset="1" stop-color="#B9AEA3"/></linearGradient>
      <linearGradient id="skKimchi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F49A78"/><stop offset="1" stop-color="#D9573F"/></linearGradient>
      <linearGradient id="skCocoa" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#C07A4E"/><stop offset=".55" stop-color="#94532F"/><stop offset="1" stop-color="#6E3B22"/></linearGradient>
      <radialGradient id="skShadow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#5A3A28" stop-opacity=".32"/><stop offset="1" stop-color="#5A3A28" stop-opacity="0"/></radialGradient>
    </defs></svg>`;
    document.body.prepend(d.firstElementChild);
  };
  const ground = (w, op = 1) => `<svg width="${w}" height="${w * .2}" viewBox="0 0 100 20" style="display:block;opacity:${op}"><ellipse cx="50" cy="10" rx="50" ry="10" fill="url(#skShadow)"/></svg>`;

  // ---------- 무대 ----------
  function stage(root, o = {}) {
    defs();
    const wall = document.createElement('div');
    wall.className = 'sk-wall';
    wall.style.cssText = `position:absolute;inset:0;z-index:0;pointer-events:none;
      background:
        radial-gradient(circle at 18px 18px, rgba(226,72,58,.07) 4px, transparent 5px) 0 0/48px 48px,
        radial-gradient(circle at 42px 42px, rgba(46,156,131,.06) 4px, transparent 5px) 0 0/48px 48px,
        linear-gradient(180deg,#FFF4E6 0%,#FFF8F0 55%,#FFEFE2 100%)`;
    root.prepend(wall);
    if (o.awning) {
      let st = '', sc = '';
      for (let i = 0; i < 13; i++) st += `<rect x="${i * 90}" y="0" width="45" height="96" fill="#E2483A"/>`;
      for (let i = 0; i < 13; i++) sc += `<path d="M${i * 90} 96 q22.5 34 45 0" fill="#E2483A" stroke="${K}" stroke-width="5"/><path d="M${i * 90 + 45} 96 q22.5 34 45 0" fill="#FFF6EC" stroke="${K}" stroke-width="5"/>`;
      const a = document.createElement('div');
      a.style.cssText = 'position:absolute;left:0;top:0;width:1080px;height:140px;z-index:1;pointer-events:none';
      a.innerHTML = `<svg width="1080" height="140" viewBox="0 0 1080 140"><rect width="1080" height="96" fill="#FFF6EC"/>${st}${sc}
        <rect x="0" y="0" width="1080" height="96" fill="url(#skAwShade)"/><defs><linearGradient id="skAwShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".18"/></linearGradient></defs></svg>`;
      root.prepend(a); a.style.zIndex = 1; wall.after(a);
    }
    if (o.table) {
      const top = o.tableTop || 1468;
      const t = document.createElement('div');
      t.className = 'sk-table';
      const cloth = o.table === 'gingham'
        ? `repeating-linear-gradient(90deg,rgba(226,72,58,.20) 0 40px,transparent 40px 80px),repeating-linear-gradient(0deg,rgba(226,72,58,.20) 0 40px,transparent 40px 80px),#FFF8F0`
        : `repeating-linear-gradient(90deg,rgba(120,70,30,.10) 0 2px,transparent 2px 180px),linear-gradient(180deg,#E7BE8B,#C99257)`;
      t.style.cssText = `position:absolute;left:0;top:${top}px;width:1080px;height:${1920 - top}px;z-index:0;pointer-events:none;background:${cloth};
        border-top:7px solid ${K};box-shadow:inset 0 26px 30px -18px rgba(90,50,30,.28)`;
      wall.after(t);
      // 탁자 윗면 하이라이트
      const hl = document.createElement('div');
      hl.style.cssText = `position:absolute;left:0;top:${top + 7}px;width:1080px;height:16px;z-index:0;pointer-events:none;background:linear-gradient(180deg,rgba(255,255,255,.55),rgba(255,255,255,0))`;
      t.after(hl);
    }
  }

  // ---------- 소품 ----------
  const cabbage = w => `<svg viewBox="0 0 200 300" width="${w}" height="${w * 1.5}" style="overflow:visible">
    <path d="M100 14 C142 14 178 54 180 114 C182 184 156 250 100 290 C44 250 18 184 20 114 C22 54 58 14 100 14Z" fill="url(#skCabLeaf)" stroke="${K}" stroke-width="7"/>
    <path d="M30 96 C36 74 50 80 56 60 C64 40 78 56 88 36 C96 22 104 22 112 36 C122 56 136 40 144 60 C150 80 164 74 170 96" fill="none" stroke="#5E9E3E" stroke-width="5" stroke-linecap="round"/>
    <path d="M100 112 C134 120 152 174 148 230 C144 264 124 286 100 290 C76 286 56 264 52 230 C48 174 66 120 100 112Z" fill="url(#skCabWhite)" stroke="${K}" stroke-width="6"/>
    <path d="M100 176 V280 M82 180 C77 216 79 248 88 276 M118 180 C123 216 121 248 112 276" fill="none" stroke="#E2D7B0" stroke-width="5" stroke-linecap="round"/>
    <path d="M100 34 C130 44 142 86 136 126 C130 150 116 162 100 166 C84 162 70 150 64 126 C58 86 70 44 100 34Z" fill="url(#skCabLeafL)" stroke="${K}" stroke-width="5"/>
    <path d="M100 50 V160 M100 88 L84 72 M100 88 L116 72 M100 118 L80 100 M100 118 L120 100 M100 144 L84 130 M100 144 L116 130" fill="none" stroke="#8BC867" stroke-width="4" stroke-linecap="round"/>
    <path d="M52 76 C44 106 42 138 48 168" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".45"/>
    <path d="M150 200 C156 230 152 256 140 274" fill="none" stroke="#B8AE8C" stroke-width="6" stroke-linecap="round" opacity=".5"/></svg>`;

  const half = w => `<svg viewBox="0 0 320 160" width="${w}" height="${w * .5}" style="overflow:visible">
    <path d="M12 84 C8 40 70 8 162 8 C252 8 312 38 314 80 C312 122 252 152 162 152 C70 152 16 128 12 84Z" fill="url(#skCabLeaf)" stroke="${K}" stroke-width="7"/>
    <path d="M12 84 C4 64 14 40 30 30 C28 44 36 50 44 42 C48 26 62 16 78 16 C70 30 78 38 90 30 C96 18 110 12 122 12" fill="none" stroke="#5E9E3E" stroke-width="6" stroke-linecap="round"/>
    <path d="M34 82 C36 46 92 24 166 24 C238 24 292 48 296 80 C292 112 238 136 166 136 C92 136 36 118 34 82Z" fill="url(#skCabCore)" stroke="${K}" stroke-width="5"/>
    <path d="M72 80 C74 54 120 40 178 40 C232 40 272 58 276 80 C272 102 232 120 178 120 C120 120 74 106 72 80Z" fill="none" stroke="#EAD27E" stroke-width="6"/>
    <path d="M112 80 C114 62 148 52 188 52 C228 52 256 66 258 80 C256 94 228 108 188 108 C148 108 114 98 112 80Z" fill="none" stroke="#E2C25C" stroke-width="5"/>
    <path d="M34 82 C36 54 58 34 94 28 C80 48 82 66 98 80 C82 94 80 114 94 132 C58 126 36 110 34 82Z" fill="url(#skCabLeafL)" stroke="${K}" stroke-width="4"/>
    <path d="M50 64 C58 50 70 44 80 42 M50 100 C58 112 70 118 80 120 M48 82 H84" stroke="#8BC867" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M296 80 C294 60 282 46 264 36 C278 56 280 68 278 80 C280 92 278 104 264 124 C282 114 294 100 296 80Z" fill="#fff" opacity=".85"/>
    <path d="M120 32 C150 26 190 26 220 30" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".7" fill="none"/></svg>`;

  const radish = w => `<svg viewBox="0 0 200 300" width="${w}" height="${w * 1.5}" style="overflow:visible">
    <path d="M94 96 C76 62 52 36 42 12 C62 8 86 32 102 86 Z" fill="url(#skLeaf)" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M106 90 C116 52 136 22 156 8 C164 26 142 58 116 94 Z" fill="url(#skLeaf)" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M98 92 C96 54 100 26 106 6 C118 30 116 64 108 92 Z" fill="#5DB85A" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M70 46 L84 60 M136 36 L124 54 M104 24 V48" stroke="#3E8A3A" stroke-width="3" stroke-linecap="round"/>
    <path d="M60 104 C60 84 140 84 140 104 L146 214 C148 258 126 286 100 290 C74 286 52 258 54 214 Z" fill="url(#skRad)" stroke="${K}" stroke-width="7"/>
    <path d="M62 104 C62 88 138 88 138 104 L141 158 C114 172 86 172 59 158 Z" fill="url(#skRadTop)"/>
    <path d="M60 104 C60 84 140 84 140 104 L146 214 C148 258 126 286 100 290 C74 286 52 258 54 214 Z" fill="none" stroke="${K}" stroke-width="7"/>
    <path d="M78 190 h14 M108 226 h14 M82 252 h10 M112 168 h10" stroke="#D3CCB8" stroke-width="5" stroke-linecap="round"/>
    <path d="M144 200 l14 6 M56 236 l-12 6 M120 270 l10 10" stroke="${K}" stroke-width="3" stroke-linecap="round"/>
    <path d="M100 290 L100 306" stroke="${K}" stroke-width="5" stroke-linecap="round"/>
    <path d="M70 122 C66 160 66 196 72 230" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".7" fill="none"/></svg>`;

  const pa = w => `<svg viewBox="0 0 200 300" width="${w}" height="${w * 1.5}" style="overflow:visible">
    <path d="M72 168 L52 22 C50 10 66 8 68 18 L92 168 Z" fill="url(#skLeaf)" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M110 168 L146 28 C150 16 166 20 162 32 L126 170 Z" fill="url(#skLeaf)" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M90 168 L96 14 C98 2 114 2 114 14 L108 168 Z" fill="#4FA94F" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    ${[66, 92, 118].map((x, i) => `<rect x="${x}" y="${136 + (i % 2) * 6}" width="30" height="${140 - (i % 2) * 6}" rx="15" fill="url(#skPa)" stroke="${K}" stroke-width="5"/>`).join('')}
    <path d="M72 158 V250 M98 162 V254 M124 158 V250" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/>
    <rect x="60" y="214" width="96" height="16" rx="8" fill="#E2483A" stroke="${K}" stroke-width="4"/>
    <path d="M74 276 L66 296 M84 278 L84 300 M108 280 L104 300 M118 280 L124 298 M136 276 L144 294" stroke="${K}" stroke-width="3.5" stroke-linecap="round"/></svg>`;

  const jar = w => `<svg viewBox="0 0 200 280" width="${w}" height="${w * 1.4}" style="overflow:visible">
    <rect x="50" y="18" width="100" height="42" rx="12" fill="url(#skLid)" stroke="${K}" stroke-width="6"/>
    <path d="M58 30 H142" stroke="#8FE0CB" stroke-width="5" stroke-linecap="round"/>
    <path d="M60 60 H140 C160 66 170 84 170 110 V236 C170 256 156 268 136 268 H64 C44 268 30 256 30 236 V110 C30 84 40 66 60 60 Z" fill="url(#skGlass)" stroke="${K}" stroke-width="7"/>
    <path d="M38 128 C70 120 130 136 162 126 V234 C162 250 152 260 136 260 H64 C48 260 38 250 38 234 Z" fill="url(#skShrimpBed)"/>
    <g fill="none" stroke="#E07A62" stroke-width="7" stroke-linecap="round">
      <path d="M62 170 C48 162 54 142 74 146"/><path d="M106 158 C92 150 98 130 118 134"/><path d="M144 182 C130 174 136 154 156 158"/>
      <path d="M80 214 C66 206 72 186 92 190"/><path d="M124 228 C110 220 116 200 136 204"/><path d="M58 246 C48 240 52 226 66 228"/></g>
    <g fill="#4A3A33">${[[74, 146], [118, 134], [156, 158], [92, 190], [136, 204]].map(([x, y]) => `<circle cx="${x - 2}" cy="${y + 4}" r="2.6"/>`).join('')}</g>
    <g stroke="#F6B9A6" stroke-width="2.5">${[[60, 160], [104, 148], [142, 172], [78, 204], [122, 218]].map(([x, y]) => `<path d="M${x} ${y} l6 -4 M${x + 6} ${y + 6} l6 -4"/>`).join('')}</g>
    <path d="M60 60 H140 C160 66 170 84 170 110 V236 C170 256 156 268 136 268 H64 C44 268 30 256 30 236 V110 C30 84 40 66 60 60 Z" fill="none" stroke="${K}" stroke-width="7"/>
    <path d="M48 96 C46 84 52 76 62 74" stroke="#fff" stroke-width="9" stroke-linecap="round" fill="none"/>
    <path d="M46 116 V206" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".75"/>
    <path d="M154 120 V220" stroke="#B9D3D9" stroke-width="6" stroke-linecap="round" opacity=".8"/></svg>`;

  const basin = (w, inner = '') => `<svg viewBox="0 -240 800 520" width="${w}" height="${w * .65}" style="overflow:visible">
    <ellipse cx="400" cy="250" rx="390" ry="30" fill="url(#skShadow)"/>
    <ellipse cx="400" cy="60" rx="394" ry="62" fill="url(#skBasin)" stroke="${K}" stroke-width="8"/>
    <ellipse cx="400" cy="66" rx="354" ry="42" fill="#A3291F"/>
    ${inner}
    <path d="M6 60 A394 62 0 0 0 794 60 C780 132 744 196 690 222 Q400 258 110 222 C56 196 20 132 6 60Z" fill="url(#skBasin)" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
    <path d="M24 74 A380 52 0 0 0 776 74" stroke="#F58A7C" stroke-width="10" fill="none" stroke-linecap="round"/>
    <path d="M60 140 Q400 196 740 140" stroke="#B73226" stroke-width="7" fill="none" opacity=".6"/>
    <path d="M104 182 Q400 226 696 182" stroke="#B73226" stroke-width="7" fill="none" opacity=".45"/>
    <path d="M70 116 C86 160 110 192 136 208" stroke="#fff" stroke-width="14" stroke-linecap="round" fill="none" opacity=".35"/></svg>`;
  const at = (svg, x, y, rot = 0, s = 1) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">${svg}</g>`;

  // 나무 상자(가을걷이) — 위로 배추·무가 소복이
  const crate = (w, kind = 'cabbage') => {
    const top = kind === 'cabbage'
      ? [at(cabbage(110), 18, -112, -16), at(cabbage(116), 112, -132, 4), at(cabbage(110), 206, -108, 18)].join('')
      : [at(radish(100), 28, -132, -24), at(radish(104), 120, -150, 0), at(radish(100), 212, -128, 22)].join('');
    return `<svg viewBox="0 -170 340 380" width="${w}" height="${w * 380 / 340}" style="overflow:visible">
      <ellipse cx="170" cy="200" rx="170" ry="16" fill="url(#skShadow)"/>
      ${top}
      <path d="M14 40 H326 L314 190 H26 Z" fill="url(#skWood)" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
      <path d="M18 88 H322 M22 138 H318" stroke="${K}" stroke-width="5" opacity=".55"/>
      <path d="M30 52 H310" stroke="#F3CFA0" stroke-width="6" stroke-linecap="round"/>
      <path d="M60 46 V186 M280 46 V186" stroke="#A86E3C" stroke-width="10" opacity=".45"/>
      <circle cx="40" cy="64" r="5" fill="${K}"/><circle cx="300" cy="64" r="5" fill="${K}"/><circle cx="40" cy="168" r="5" fill="${K}"/><circle cx="300" cy="168" r="5" fill="${K}"/>
    </svg>`;
  };

  // 부엌 저울 + 보자기 덮인 '?' 재료
  const scale = w => `<svg viewBox="0 0 360 420" width="${w}" height="${w * 420 / 360}" style="overflow:visible">
    <ellipse cx="180" cy="404" rx="170" ry="14" fill="url(#skShadow)"/>
    <path d="M58 164 H302 L282 374 C280 392 268 400 252 400 H108 C92 400 80 392 78 374 Z" fill="url(#skMetal)" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
    <path d="M86 186 C84 260 90 330 100 380" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".8"/>
    <circle cx="180" cy="284" r="72" fill="#FFFDF7" stroke="${K}" stroke-width="7"/>
    ${Array.from({ length: 11 }, (_, i) => { const a = (-210 + i * 24) * Math.PI / 180; return `<path d="M${180 + Math.cos(a) * 58} ${284 + Math.sin(a) * 58} L${180 + Math.cos(a) * 66} ${284 + Math.sin(a) * 66}" stroke="${K}" stroke-width="${i % 5 ? 3 : 5}" stroke-linecap="round"/>`; }).join('')}
    <path d="M180 284 L216 246" stroke="#E2483A" stroke-width="8" stroke-linecap="round"/><circle cx="180" cy="284" r="8" fill="${K}"/>
    <text x="180" y="334" text-anchor="middle" font-family="Jua" font-size="30" fill="${K}">kg</text>
    <rect x="34" y="140" width="292" height="28" rx="14" fill="#E9DED3" stroke="${K}" stroke-width="7"/>
    <path d="M96 140 C80 100 104 52 180 50 C256 52 280 100 264 140 Z" fill="#F7C9A8" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M96 140 C110 128 124 140 138 128 C152 140 166 128 180 140 C194 128 208 140 222 128 C236 140 250 128 264 140" fill="none" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M150 52 C160 36 200 36 210 52" fill="#F7C9A8" stroke="${K}" stroke-width="6"/>
    <path d="M118 86 C130 70 150 62 168 60" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".6" fill="none"/>
    <circle cx="180" cy="98" r="30" fill="#E2483A" stroke="${K}" stroke-width="6"/>
    <text x="180" y="113" text-anchor="middle" font-family="Jua" font-size="42" fill="#fff">?</text></svg>`;

  // 집(58.6% 그림) — fill: 0~1 칠한 몫(따뜻한 불빛 + 빨간 지붕), 나머지는 회색
  const house = (w, f, id) => `<svg viewBox="0 0 90 92" width="${w}" height="${w * 92 / 90}" style="overflow:visible">
    <defs><clipPath id="${id}"><rect x="0" y="0" width="${90 * f}" height="92"/></clipPath></defs>
    <ellipse cx="45" cy="88" rx="40" ry="5" fill="url(#skShadow)"/>
    <g><path d="M16 44 H74 V84 H16 Z" fill="#EFE7DE" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
      <path d="M6 46 L45 12 L84 46 Z" fill="url(#skRoofOff)" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
      <rect x="24" y="52" width="16" height="14" rx="3" fill="#D6CEC4" stroke="${K}" stroke-width="3.5"/><rect x="48" y="56" width="16" height="28" rx="4" fill="#D6CEC4" stroke="${K}" stroke-width="3.5"/></g>
    <g clip-path="url(#${id})"><path d="M16 44 H74 V84 H16 Z" fill="#FFF6E6" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
      <path d="M6 46 L45 12 L84 46 Z" fill="url(#skRoof)" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
      <path d="M22 38 L45 18 M34 40 L52 24" stroke="#F7A596" stroke-width="3" stroke-linecap="round"/>
      <rect x="24" y="52" width="16" height="14" rx="3" fill="#FFD45C" stroke="${K}" stroke-width="3.5"/><rect x="48" y="56" width="16" height="28" rx="4" fill="#C98E5C" stroke="${K}" stroke-width="3.5"/>
      <circle cx="60" cy="70" r="2" fill="${K}"/></g></svg>`;

  // 김치통
  const tub = w => `<svg viewBox="0 0 200 170" width="${w}" height="${w * .85}" style="overflow:visible">
    <ellipse cx="100" cy="162" rx="90" ry="8" fill="url(#skShadow)"/>
    <rect x="22" y="30" width="156" height="32" rx="12" fill="#E2483A" stroke="${K}" stroke-width="6"/>
    <path d="M32 40 H168" stroke="#F58A7C" stroke-width="5" stroke-linecap="round"/>
    <rect x="86" y="16" width="28" height="16" rx="6" fill="#E2483A" stroke="${K}" stroke-width="5"/>
    <rect x="32" y="58" width="136" height="98" rx="16" fill="#FFF7F0" stroke="${K}" stroke-width="6"/>
    <path d="M40 74 C70 66 130 80 160 70 V140 C160 146 154 150 148 150 H52 C46 150 40 146 40 140 Z" fill="url(#skKimchi)"/>
    <path d="M52 92 C66 84 80 96 94 88 M104 108 C118 100 132 112 146 104 M60 128 C74 120 88 132 102 124" stroke="#FCE2D2" stroke-width="5" fill="none" stroke-linecap="round"/>
    <rect x="32" y="58" width="136" height="98" rx="16" fill="none" stroke="${K}" stroke-width="6"/>
    <path d="M42 76 V138" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".6"/></svg>`;

  // 코코아 콩(EP.15, 2026-11-08 사용자 의견: 열매 그림이 커서 코코넛 같음 → 작은 콩 여러 개, 귀엽게).
  // 커피콩과 다르게: 아몬드처럼 통통, 붉은 갈색, 가운데 진한 홈 대신 옅은 결. face=true 면 웃는 얼굴·볼터치.
  const beanG = (x, y, rot = 0, s = 1, face = false) => `<g transform="translate(${x},${y}) rotate(${rot}) scale(${s})">
    <path d="M-31 2 C-27 -14 -9 -20 6 -19 C22 -17 32 -7 31 2 C29 14 13 21 -2 20 C-18 19 -33 13 -31 2Z" fill="url(#skCocoa)" stroke="${K}" stroke-width="4.5"/>
    <path d="M-24 5 C-10 1 10 1 25 3" stroke="#D59A6E" stroke-width="2.6" fill="none" stroke-linecap="round" opacity=".75"/>
    <ellipse cx="-12" cy="-10" rx="8" ry="3.4" fill="#fff" opacity=".4" transform="rotate(-14 -12 -10)"/>
    ${face ? `<circle cx="-8" cy="3" r="3.8" fill="#271B17"/><circle cx="8" cy="3" r="3.8" fill="#271B17"/><circle cx="-6.8" cy="1.6" r="1.3" fill="#fff"/><circle cx="9.2" cy="1.6" r="1.3" fill="#fff"/><path d="M-4 9.5 Q0 13 4 9.5" stroke="#271B17" stroke-width="2.2" fill="none" stroke-linecap="round"/><ellipse cx="-16" cy="8" rx="4.4" ry="2.8" fill="#FF9EB0" opacity=".8"/><ellipse cx="16" cy="8" rx="4.4" ry="2.8" fill="#FF9EB0" opacity=".8"/>` : ''}</g>`;
  const cocoaBean = (w, face = false, rot = 0) => `<svg viewBox="-34 -26 68 52" width="${w}" height="${w * 52 / 68}" style="overflow:visible">${beanG(0, 0, rot, 1, face)}</svg>`;
  // 나무 그릇에 담긴 코코아 콩 무더기 + 초록 잎(위 두 콩은 웃는 얼굴)
  const cocoaBowl = w => `<svg viewBox="0 0 260 180" width="${w}" height="${w * 180 / 260}" style="overflow:visible">
    <ellipse cx="130" cy="172" rx="104" ry="9" fill="${K}" opacity=".14"/>
    <path d="M168 66 C196 30 238 22 254 34 C240 64 204 82 168 66Z" fill="#6DBE7E" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <path d="M170 65 C198 50 224 40 252 35" stroke="#3E8F55" stroke-width="3.2" fill="none" stroke-linecap="round"/>
    <ellipse cx="130" cy="96" rx="112" ry="17" fill="#8A5A34" stroke="${K}" stroke-width="5"/>
    ${[[70, 84, -16, 1.1, 0], [192, 84, 14, 1.1, 0], [100, 62, 18, 1.15, 1], [160, 64, -14, 1.15, 0], [130, 40, -4, 1.2, 1], [96, 98, -6, 1.1, 0], [164, 98, 8, 1.1, 0], [130, 82, 0, 1.15, 0]].map(([x, y, r, sc, f]) => beanG(x, y, r, sc, !!f)).join('')}
    <path d="M18 96 C24 146 70 172 130 172 C190 172 236 146 242 96 C214 112 46 112 18 96Z" fill="url(#skWood)" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>
    <path d="M40 120 C70 140 190 140 220 120" stroke="#9C6838" stroke-width="4" fill="none" opacity=".55" stroke-linecap="round"/>
    <path d="M34 108 C40 128 52 140 66 148" stroke="#fff" stroke-width="7" fill="none" opacity=".35" stroke-linecap="round"/></svg>`;
  return { K, defs, stage, ground, cabbage, half, radish, pa, jar, basin, crate, scale, house, tub, cocoaBean, cocoaBowl, at };
})();
