// 돈 그림(상표·실제 화폐 도안 없음) — 금화·지폐·돈 묶음·돈 저금통. 2026-10-31 생활 검산 EP.02에서 만듦.
let _mid = 0;
// 금화: 금색 그라데이션 + 테두리 톱니 + ₩ 각인 + 반짝임
const COIN = (s) => { const i = 'mc' + (_mid++);
  return `<svg width="${s}" height="${s}" viewBox="0 0 60 60"><defs><radialGradient id="${i}" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFF4B8"/><stop offset=".45" stop-color="#FFD045"/><stop offset="1" stop-color="#D99A12"/></radialGradient></defs>
  <circle cx="30" cy="31.5" r="26" fill="#B97F0C"/>
  <circle cx="30" cy="29" r="26" fill="url(#${i})" stroke="#7A5208" stroke-width="2.5"/>
  <circle cx="30" cy="29" r="20.5" fill="none" stroke="#C88A0E" stroke-width="2" stroke-dasharray="2.2 2.2"/>
  <circle cx="30" cy="29" r="17" fill="none" stroke="#FFF1A8" stroke-width="1.6" opacity=".8"/>
  <text x="30" y="37.5" text-anchor="middle" font-family="P,sans-serif" font-weight="900" font-size="23" fill="#A86E07">₩</text>
  <path d="M15 19 Q20 11 29 9" stroke="#fff" stroke-width="3.5" fill="none" stroke-linecap="round" opacity=".75"/></svg>`; };
// 지폐: 연두빛 종이 + 무늬 테두리 + 가운데 ₩ 원 + 모서리 숫자(실제 화폐 도안 아님)
const BILL = (w, rot = 0, c1 = '#CDEBC4', c2 = '#9FD49A', ink = '#3C7A45') => { const i = 'mb' + (_mid++);
  return `<svg width="${w}" height="${w * .5}" viewBox="0 0 120 60" style="transform:rotate(${rot}deg);overflow:visible"><defs><linearGradient id="${i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient></defs>
  <rect x="2" y="3" width="116" height="55" rx="5" fill="#6E9F68" opacity=".45"/>
  <rect x="1" y="1" width="116" height="55" rx="5" fill="url(#${i})" stroke="${ink}" stroke-width="2.5"/>
  <rect x="7" y="6" width="104" height="45" rx="3" fill="none" stroke="${ink}" stroke-width="1.4" stroke-dasharray="3 2" opacity=".7"/>
  <ellipse cx="59" cy="28.5" rx="15" ry="15" fill="#F2FAEE" stroke="${ink}" stroke-width="2"/>
  <text x="59" y="36" text-anchor="middle" font-family="P,sans-serif" font-weight="900" font-size="21" fill="${ink}">₩</text>
  <text x="13" y="20" font-family="P,sans-serif" font-weight="900" font-size="10" fill="${ink}">10000</text>
  <text x="105" y="47" text-anchor="end" font-family="P,sans-serif" font-weight="900" font-size="10" fill="${ink}">10000</text>
  <path d="M84 16 q6 5 0 10 q-6 5 0 10 q6 5 0 10 M34 16 q-6 5 0 10 q6 5 0 10 q-6 5 0 10" stroke="${ink}" stroke-width="1.3" fill="none" opacity=".45"/></svg>`; };
// 돈 묶음: 지폐 n장 겹침 + 금화
const MONEY = (n, h = 70) => { const w = h * 1.55;
  let out = `<span style="position:relative;display:inline-block;width:${w + (n - 1) * 26 + h * .45}px;height:${h}px">`;
  for (let k = 0; k < n; k++) out += `<span style="position:absolute;left:${k * 26}px;top:${6 + (k % 2) * 4}px">${BILL(w, (k - (n - 1) / 2) * 7)}</span>`;
  out += `<span style="position:absolute;left:${(n - 1) * 26 + w * .72}px;top:${h * .3}px">${COIN(h * .62)}</span></span>`;
  return out; };
// 저금통 병: 지폐가 삐죽 + 금화 더미
const JAR = (w, c, lab) => { const i = 'mj' + (_mid++);
  const coins = [[38, 142], [70, 147], [102, 142], [52, 126], [88, 126], [70, 110]].map(([x, y]) =>
    `<g><ellipse cx="${x}" cy="${y + 2.5}" rx="17" ry="8" fill="#B97F0C"/><ellipse cx="${x}" cy="${y}" rx="17" ry="8" fill="url(#${i})" stroke="#7A5208" stroke-width="2"/><ellipse cx="${x}" cy="${y}" rx="10" ry="4.4" fill="none" stroke="#C88A0E" stroke-width="1.5"/></g>`).join('');
  return `<svg viewBox="0 0 140 170" width="${w}" height="${w * 170 / 140}"><defs><linearGradient id="${i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF0A0"/><stop offset=".5" stop-color="#FFD045"/><stop offset="1" stop-color="#D99A12"/></linearGradient></defs>
  <g transform="rotate(-14 96 92)"><rect x="70" y="70" width="52" height="28" rx="3" fill="#B8E1AE" stroke="#3C7A45" stroke-width="2.5"/><circle cx="96" cy="84" r="7" fill="#F2FAEE" stroke="#3C7A45" stroke-width="1.6"/></g>
  <g transform="rotate(10 46 98)"><rect x="22" y="80" width="52" height="28" rx="3" fill="#CDEBC4" stroke="#3C7A45" stroke-width="2.5"/><circle cx="48" cy="94" r="7" fill="#F2FAEE" stroke="#3C7A45" stroke-width="1.6"/></g>
  ${coins}
  <path d="M24 30 H116 Q132 30 132 50 V146 Q132 164 112 164 H28 Q8 164 8 146 V50 Q8 30 24 30 Z" fill="#EAF7F2" fill-opacity=".35" stroke="#4A3A33" stroke-width="5"/>
  <path d="M20 50 Q18 100 22 150" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" opacity=".7"/>
  <rect x="30" y="8" width="80" height="22" rx="8" fill="${c}" stroke="#4A3A33" stroke-width="4"/>
  ${lab ? `<rect x="26" y="40" width="88" height="30" rx="10" fill="#fff" stroke="#4A3A33" stroke-width="3"/><text x="70" y="62" text-anchor="middle" font-family="Jua" font-size="21" fill="#3E2F25">${lab}</text>` : ''}</svg>`; };
