// 도리(회색 햄스터, 민트 크로스백) — 채널 시안의 벡터 그림(2판)을 그대로 쓰고 표정·팔·볼주머니만 움직이게 나눴다.
// Dori.mount(el) → Dori.draw(st)
// st: {t, blink, happy, squint, surprise, sad, open, gx, gy, pouch, armL, armR, earL, earR, hop, squash, breath, tilt, sweat, sweatY, mark, markO, spark}
(function(){
const INK='#4A3A33';
const BODY='M200,86 C282,86 338,134 346,200 C350,236 346,262 338,288 C352,330 342,398 262,402 L138,402 C58,398 48,330 62,288 C54,262 50,236 54,200 C62,134 118,86 200,86 Z';
const ARM='M-23.0,0 L-23.0,35.0 A23.0,23.0 0 0 0 23.0,35.0 L23.0,0 A23.0,23.0 0 0 0 -23.0,0 Z';
const eye=(x,id)=>`<g id="${id}" transform="translate(${x},214)">
  <g class="open"><g class="ball"><ellipse rx="17" ry="19" fill="#271B17"/><circle class="h1" cx="-5.5" cy="-6.5" r="6.8" fill="#fff"/><circle class="h2" cx="6" cy="6.5" r="3" fill="#fff"/></g></g>
  <path class="shut" d="M-15,2 Q0,10 15,2" stroke="${INK}" stroke-width="6.5" stroke-linecap="round" fill="none" opacity="0"/>
  <path class="happy" d="M-15,5 Q0,-13 15,5" stroke="${INK}" stroke-width="7" stroke-linecap="round" fill="none" opacity="0"/>
  <path class="sq" d="${x<200?'M-13,-12 L11,0 L-13,12':'M13,-12 L-11,0 L13,12'}" stroke="${INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0"/>
</g>`;
const svg=`<svg viewBox="-70 -70 540 560" width="100%" height="100%" overflow="visible" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="dFur" x1="0" y1="86" x2="0" y2="402" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#C2BBB6"/><stop offset=".55" stop-color="#AEA6A1"/><stop offset="1" stop-color="#9D958F"/></linearGradient>
  <radialGradient id="dWh" cx="200" cy="300" r="170" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FFFDFB"/><stop offset=".78" stop-color="#FFFDFB"/><stop offset="1" stop-color="#F1ECE8"/></radialGradient>
  <clipPath id="dClip"><path d="${BODY}"/><circle id="dPcL" cx="84" cy="262" r="0"/><circle id="dPcR" cx="316" cy="262" r="0"/></clipPath>
  <clipPath id="dArmC"><path d="${ARM}"/></clipPath>
  <clipPath id="dMouthC"><path id="dMouthCP"/></clipPath>
</defs>
<ellipse id="dSh" cx="200" cy="414" rx="132" ry="14" fill="#E6DFDA"/>
<g id="dRoot">
 <g id="dSpark" opacity="0" fill="#FFCF4A">
  <path d="M36,102 Q39.24,116.76 54,120 Q39.24,123.24 36,138 Q32.76,123.24 18,120 Q32.76,116.76 36,102 Z"/>
  <path d="M366,92 Q369.24,106.76 384,110 Q369.24,113.24 366,128 Q362.76,113.24 348,110 Q362.76,106.76 366,92 Z"/>
  <path d="M352,30 Q354,39 363,41 Q354,43 352,52 Q350,43 341,41 Q350,39 352,30 Z"/>
 </g>
 <g id="dHeadAll">
  <g id="dEarL"><circle cx="122" cy="118" r="38" fill="#C2BBB6" stroke="${INK}" stroke-width="6.5"/><circle cx="127" cy="124" r="23" fill="#F7A8AE"/></g>
  <g id="dEarR"><circle cx="278" cy="118" r="38" fill="#C2BBB6" stroke="${INK}" stroke-width="6.5"/><circle cx="273" cy="124" r="23" fill="#F7A8AE"/></g>
  <g id="dPouchStroke" stroke="${INK}" stroke-width="13" stroke-linejoin="round" fill="${INK}"><path d="${BODY}"/><circle id="dPsL" cx="84" cy="262" r="0"/><circle id="dPsR" cx="316" cy="262" r="0"/></g>
  <path d="${BODY}" fill="url(#dFur)"/>
  <circle id="dPwL" cx="84" cy="262" r="0" fill="#FFFDFB"/><circle id="dPwR" cx="316" cy="262" r="0" fill="#FFFDFB"/>
  <g clip-path="url(#dClip)"><ellipse id="dCheekW" cx="200" cy="260" rx="124" ry="52" fill="url(#dWh)"/><ellipse cx="200" cy="340" rx="104" ry="82" fill="url(#dWh)"/></g>
  <g stroke="#8B817B" stroke-linecap="round" fill="none" opacity=".85"><path d="M198,96 C192,118 192,138 196,160" stroke-width="7.5"/><path d="M220,100 C216,113 216,125 219,137" stroke-width="5.5"/></g>
  <ellipse cx="150" cy="124" rx="34" ry="14" fill="#fff" opacity=".16" transform="rotate(-22,150,124)"/>
  <ellipse id="dBlL" cx="134" cy="254" rx="24" ry="15" fill="#FAA3AB" opacity=".9"/>
  <ellipse id="dBlR" cx="266" cy="254" rx="24" ry="15" fill="#FAA3AB" opacity=".9"/>
  <path id="dWhL" d="M104,242 L142,247 M102,256 L140,256" stroke="#8B817B" stroke-width="2.6" stroke-linecap="round"/>
  <path id="dWhR" d="M296,242 L258,247 M298,256 L260,256" stroke="#8B817B" stroke-width="2.6" stroke-linecap="round"/>
  ${eye(148,'dEyeL')}${eye(252,'dEyeR')}
  <g id="dBrows" stroke="${INK}" stroke-width="4.8" stroke-linecap="round" fill="none" opacity="0"><path id="dBrL"/><path id="dBrR"/></g>
  <path d="M191,233 Q200,228 209,233 Q208,240 200,243 Q192,240 191,233 Z" fill="#EF8794" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M200,242 L200,248" fill="none" stroke="${INK}" stroke-width="4.2" stroke-linecap="round"/>
  <g id="dMouthOpen" opacity="0"><path id="dMouthO" fill="#E5657A" stroke="${INK}" stroke-width="4.2" stroke-linejoin="round"/>
    <g clip-path="url(#dMouthC)"><ellipse id="dTongue" cx="200" rx="8.5" ry="5.2" fill="#F99DAB"/></g></g>
  <path id="dMouthC2" fill="none" stroke="${INK}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
 </g>
 <path d="M84,304 Q190,318 290,346" stroke="${INK}" stroke-width="13" stroke-linecap="round" fill="none"/>
 <path d="M84,304 Q190,318 290,346" stroke="#5DB6A0" stroke-width="7.5" stroke-linecap="round" fill="none"/>
 <rect x="266" y="334" width="70" height="52" rx="13" fill="#80D0BA" stroke="${INK}" stroke-width="5"/>
 <path d="M266,348 Q266,334 279,334 L323,334 Q336,334 336,348 L336,355 Q301,368 266,355 Z" fill="#63BCA5" stroke="${INK}" stroke-width="4.5" stroke-linejoin="round"/>
 <circle cx="301" cy="361" r="5" fill="#FFF4D4" stroke="${INK}" stroke-width="2.5"/>
 <g id="dArmR"><path d="${ARM}" fill="#AEA6A1"/><g clip-path="url(#dArmC)"><rect x="-27" y="31" width="54" height="35" fill="#FFFDFB"/></g><path d="${ARM}" fill="none" stroke="${INK}" stroke-width="6.5" stroke-linejoin="round"/></g>
 <g id="dArmL"><path d="${ARM}" fill="#AEA6A1"/><g clip-path="url(#dArmC)"><rect x="-27" y="31" width="54" height="35" fill="#FFFDFB"/></g><path d="${ARM}" fill="none" stroke="${INK}" stroke-width="6.5" stroke-linejoin="round"/></g>
 <ellipse cx="158" cy="404" rx="28" ry="13.5" fill="#F8C4C7" stroke="${INK}" stroke-width="5"/>
 <ellipse cx="242" cy="404" rx="28" ry="13.5" fill="#F8C4C7" stroke="${INK}" stroke-width="5"/>
 <path id="dSweat" d="M352,120 Q366,144 352,157 Q338,144 352,120 Z" fill="#9AD8FF" stroke="#5FA9D8" stroke-width="2.5" opacity="0"/>
 <g id="dMark" opacity="0"><text id="dMarkT" x="350" y="70" font-family="Jua" font-size="92" fill="#E2483A" stroke="#fff" stroke-width="7" paint-order="stroke">!</text></g>
</g>
</svg>`;
let q;
function mount(el){el.innerHTML=svg;q=s=>el.querySelector(s);}
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
function eyeDraw(g,st){
  const happy=cl(st.happy), sq=cl(st.squint), shut=cl(st.blink);
  const openVis=1-Math.max(happy,sq);
  const sy=Math.max(.06,1-shut)*(1+st.surprise*.14), sx=1+st.surprise*.12;
  const o=g.querySelector('.open');
  o.setAttribute('opacity',openVis*(shut>.85?0:1));
  o.setAttribute('transform',`translate(${st.gx*4} ${st.gy*3}) scale(${sx} ${sy})`);
  g.querySelector('.shut').setAttribute('opacity',openVis*(shut>.85?1:0));
  g.querySelector('.happy').setAttribute('opacity',happy*(1-sq));
  g.querySelector('.sq').setAttribute('opacity',sq);
}
function draw(st){
  const pouch=cl(st.pouch);
  // 몸: 점프·찌그러짐·숨
  const sx=1+st.squash*.10, sy=1-st.squash*.10+st.breath*.012;
  q('#dRoot').setAttribute('transform',`translate(0 ${-st.hop}) translate(200 410) scale(${sx} ${sy}) translate(-200 -410)`);
  q('#dSh').setAttribute('rx',132-st.hop*.4); q('#dSh').setAttribute('opacity',1-st.hop/200);
  q('#dHeadAll').setAttribute('transform',`rotate(${st.tilt} 200 300)`);
  q('#dEarL').setAttribute('transform',`rotate(${st.earL} 122 150)`);
  q('#dEarR').setAttribute('transform',`rotate(${-st.earR} 278 150)`);
  // 볼주머니: 0이면 몸 안쪽에 숨고, 1이면 시안처럼 양옆으로 빵빵
  const r=58*pouch, cxL=lerp(124,84,pouch), cxR=lerp(276,316,pouch);
  [['#dPsL',cxL],['#dPsR',cxR],['#dPwL',cxL],['#dPwR',cxR],['#dPcL',cxL],['#dPcR',cxR]].forEach(([id,x])=>{q(id).setAttribute('cx',x);q(id).setAttribute('r',r);});
  const cw=q('#dCheekW'); cw.setAttribute('rx',124+52*pouch); cw.setAttribute('ry',52+10*pouch); cw.setAttribute('cy',260+2*pouch);
  q('#dBlL').setAttribute('cx',134-36*pouch); q('#dBlR').setAttribute('cx',266+36*pouch);
  q('#dBlL').setAttribute('rx',24+12*pouch); q('#dBlR').setAttribute('rx',24+12*pouch);
  q('#dWhL').setAttribute('transform',`translate(${-36*pouch} 0)`); q('#dWhR').setAttribute('transform',`translate(${36*pouch} 0)`);
  // 눈
  eyeDraw(q('#dEyeL'),st); eyeDraw(q('#dEyeR'),{...st});
  // 눈썹: 시무룩·깜짝일 때만
  const br=Math.max(st.sad,st.surprise);
  q('#dBrows').setAttribute('opacity',cl(br*1.5));
  const by=184-st.surprise*10;
  q('#dBrL').setAttribute('d',st.sad>st.surprise?`M134,${by-2} Q149,${by-6} 164,${by+4}`:`M134,${by+2} Q149,${by-6} 164,${by+2}`);
  q('#dBrR').setAttribute('d',st.sad>st.surprise?`M266,${by-2} Q251,${by-6} 236,${by+4}`:`M266,${by+2} Q251,${by-6} 236,${by+2}`);
  // 입
  const o=cl(st.open+st.surprise*.55), sad=cl(st.sad);
  const d=6+24*o, mw=15+3*o;
  const mo=q('#dMouthOpen'), mc=q('#dMouthC2');
  if(o>.08){
    const p=`M${200-mw},248 Q${200-mw/2+.5},254 200,249 Q${200+mw/2-.5},254 ${200+mw},248 Q${200+mw-1},${248+d} 200,${250+d} Q${200-mw+1},${248+d} ${200-mw},248 Z`;
    q('#dMouthO').setAttribute('d',p); q('#dMouthCP').setAttribute('d',p);
    const tg=q('#dTongue'); tg.setAttribute('cy',248+d*.75); tg.setAttribute('ry',2+3.2*o);
    mo.setAttribute('opacity',1); mc.setAttribute('opacity',0);
  } else {
    mo.setAttribute('opacity',0); mc.setAttribute('opacity',1);
    mc.setAttribute('d',sad>.4?`M189,257 Q200,${250} 211,257`:(pouch>.5?'M193,252 Q200,258 207,252':'M184,247 Q192,255 200,248 Q208,255 216,247'));
  }
  // 팔: 0 = 내림(32°), 1 = 번쩍(158°)
  const aR=32+126*cl(st.armR,-.2,1.1), aL=-(32+126*cl(st.armL,-.2,1.1));
  q('#dArmR').setAttribute('transform',`translate(328,292) rotate(${aR})`);
  q('#dArmL').setAttribute('transform',`translate(72,292) rotate(${aL})`);
  q('#dSweat').setAttribute('opacity',st.sweat||0); q('#dSweat').setAttribute('transform',`translate(0 ${st.sweatY||0})`);
  q('#dMark').setAttribute('opacity',st.markO||0); if(st.mark) q('#dMarkT').textContent=st.mark;
  q('#dMark').setAttribute('transform',`translate(0 ${-(st.markY||0)})`);
  q('#dSpark').setAttribute('opacity',st.spark||0);
}
function lerp(a,b,k){return a+(b-a)*k;}
window.Dori={mount,draw};
})();
