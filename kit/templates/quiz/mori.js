// 모리(고양이, 도리의 상대역 — 의심 많은 검산 담당) — 도리(dori.js)와 같은 그림체.
// 외곽선 #4A3A33 · 몸은 한 덩어리 · 같은 눈(검은 타원 + 하이라이트 둘, ∩ 웃는 눈, 감은 선) · 같은 팔·발 구조.
// 다른 점: 뾰족 귀, 긴 꼬리(끝 색 다름), 반쯤 감은 눈꺼풀(lid), 긴 수염, 라벤더 목줄 + "?" 명찰, 도리보다 키 크고 날씬.
// 시안 1판(2026-11-09). const m = Mori.mount(el,{variant:'cream'|'patch'|'cheese'}); m.draw(st)
// st: {blink, happy, surprise, open, smile, w, lid, lidL, lidR, browL, browR, gx, gy, armL, armR, hop, squash, tilt, tail, sweat, mark, markO}
(function(){
const INK='#4A3A33';
const BODY='M200,40 C270,40 312,86 316,152 C318,192 312,226 304,252 C322,300 320,392 254,402 L146,402 C80,392 78,300 96,252 C88,226 82,192 84,152 C88,86 130,40 200,40 Z';
const ARM='M-21,0 L-21,36 A21,21 0 0 0 21,36 L21,0 A21,21 0 0 0 -21,0 Z';
const EAR=['M98,104 C94,62 100,22 112,0 C117,-8 126,-8 132,-2 C152,20 170,42 182,64 Z',
           'M302,104 C306,62 300,22 288,0 C283,-8 274,-8 268,-2 C248,20 230,42 218,64 Z'];
const EARIN=['M110,90 C108,64 112,40 119,24 C133,42 147,60 156,78 Z',
             'M290,90 C292,64 288,40 281,24 C267,42 253,60 244,78 Z'];
const TAIL='M246,398 C330,404 352,338 334,300 C324,278 300,284 306,302';
const TAILTIP='M334,300 C324,278 300,284 306,302';
const EX=[156,244], EY=196;
const V={
  cream:{fur:['#F6E9D2','#E9D6B5','#DCC49E'],mid:'#E9D6B5',tip:'#C9A97E',paw:'#FFFDFB',earIn:'#F7A8AE',nose:'#EF9AA6',belly:['#FFFDFB','#F4EDE4'],stripe:null,patch:null},
  patch:{fur:['#F7F1EA','#EDE4DA','#E3D8CC'],mid:'#EDE4DA',tip:'#B98F65',paw:'#FFFDFB',earIn:'#F7A8AE',nose:'#EF9AA6',belly:['#FFFFFF','#F8F2EC'],stripe:null,patch:['#CDA77F','#B98F65']},
  cheese:{fur:['#F7CF98','#EEB977','#E2A560'],mid:'#EEB977',tip:'#D08A47',paw:'#FFF4E0',earIn:'#F7A8AE',nose:'#E98A8F',belly:['#FFF6E6','#FBE9CF'],stripe:'#D08A47',patch:null}
};
const COLLAR='#B9A3E3', TAG='#FFCF4A';
let uid=0;
const eye=(x,id)=>`<g id="${id}" transform="translate(${x},${EY})">
  <g class="open"><g class="ball"><ellipse rx="16" ry="18" fill="#271B17"/><circle cx="-5" cy="-6.5" r="6.2" fill="#fff"/><circle cx="5.5" cy="6" r="2.8" fill="#fff"/></g></g>
  <path class="shut" d="M-15,2 Q0,10 15,2" stroke="${INK}" stroke-width="6.5" stroke-linecap="round" fill="none" opacity="0"/>
  <path class="happy" d="M-15,5 Q0,-13 15,5" stroke="${INK}" stroke-width="7" stroke-linecap="round" fill="none" opacity="0"/>
</g>`;
function svg(v,p){
  const g=id=>`${id}${p}`;
  const stripes=v.stripe?`<g stroke="${v.stripe}" stroke-width="9" stroke-linecap="round" fill="none"><path d="M172,132 L162,98"/><path d="M200,126 L200,90"/><path d="M228,132 L238,98"/></g>`:'';
  const tailStripes=v.stripe?`<path d="${TAIL}" stroke="${v.stripe}" stroke-width="27" fill="none" stroke-dasharray="16 44" stroke-dashoffset="22"/>`:'';
  const patch=v.patch?`<ellipse cx="252" cy="186" rx="44" ry="52" transform="rotate(14 252 186)" fill="url(#${g('mPatch')})"/>`:'';
  return `<svg viewBox="-70 -70 540 560" width="100%" height="100%" overflow="visible" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="${g('mFur')}" x1="0" y1="40" x2="0" y2="402" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="${v.fur[0]}"/><stop offset=".55" stop-color="${v.fur[1]}"/><stop offset="1" stop-color="${v.fur[2]}"/></linearGradient>
  <radialGradient id="${g('mWh')}" cx="200" cy="300" r="160" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="${v.belly[0]}"/><stop offset=".78" stop-color="${v.belly[0]}"/><stop offset="1" stop-color="${v.belly[1]}"/></radialGradient>
  ${v.patch?`<linearGradient id="${g('mPatch')}" x1="0" y1="130" x2="0" y2="240" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="${v.patch[0]}"/><stop offset="1" stop-color="${v.patch[1]}"/></linearGradient>`:''}
  <clipPath id="${g('mClip')}"><path d="${BODY}"/></clipPath>
  <clipPath id="${g('mArmC')}"><path d="${ARM}"/></clipPath>
  <clipPath id="${g('mMouthC')}"><path class="mMouthCP"/></clipPath>
</defs>
<ellipse class="mSh" cx="200" cy="414" rx="118" ry="13" fill="#E6DFDA"/>
<g class="mRoot">
 <g class="mTail">
  <path d="${TAIL}" stroke="${INK}" stroke-width="40" stroke-linecap="round" fill="none"/>
  <path d="${TAIL}" stroke="${v.mid}" stroke-width="27" stroke-linecap="round" fill="none"/>
  ${tailStripes}
  <path d="${TAILTIP}" stroke="${v.tip}" stroke-width="27" stroke-linecap="round" fill="none"/>
 </g>
 <g class="mEarL"><path d="${EAR[0]}" fill="${v.patch?v.patch[0]:v.fur[0]}" stroke="${INK}" stroke-width="6.5" stroke-linejoin="round"/><path d="${EARIN[0]}" fill="${v.earIn}"/></g>
 <g class="mEarR"><path d="${EAR[1]}" fill="${v.fur[0]}" stroke="${INK}" stroke-width="6.5" stroke-linejoin="round"/><path d="${EARIN[1]}" fill="${v.earIn}"/></g>
 <path d="${BODY}" fill="${INK}" stroke="${INK}" stroke-width="13" stroke-linejoin="round"/>
 <path d="${BODY}" fill="url(#${g('mFur')})"/>
 <g clip-path="url(#${g('mClip')})">
  ${patch}
  <ellipse cx="200" cy="244" rx="74" ry="42" fill="url(#${g('mWh')})"/>
  <ellipse cx="200" cy="332" rx="92" ry="76" fill="url(#${g('mWh')})"/>
  ${stripes}
 </g>
 <ellipse cx="146" cy="84" rx="30" ry="12" fill="#fff" opacity=".18" transform="rotate(-26 146 84)"/>
 <ellipse class="mBlL" cx="138" cy="236" rx="20" ry="11" fill="#F6B3B8" opacity=".7"/>
 <ellipse class="mBlR" cx="262" cy="236" rx="20" ry="11" fill="#F6B3B8" opacity=".7"/>
 <g stroke="#9A8F88" stroke-width="2.8" stroke-linecap="round" fill="none">
  <path d="M118,226 L52,216 M116,238 L46,238 M118,250 L54,262"/>
  <path d="M282,226 L348,216 M284,238 L354,238 M282,250 L346,262"/>
 </g>
 ${eye(EX[0],g('mEyeL'))}${eye(EX[1],g('mEyeR'))}
 <path class="mLidL" fill="url(#${g('mFur')})"/><path class="mLidLn" stroke="${INK}" stroke-width="5.5" stroke-linecap="round" fill="none"/>
 <path class="mLidR" fill="url(#${v.patch?g('mPatch'):g('mFur')})"/><path class="mLidRn" stroke="${INK}" stroke-width="5.5" stroke-linecap="round" fill="none"/>
 <g class="mBrows" stroke="${INK}" stroke-width="4.8" stroke-linecap="round" fill="none"><path class="mBrL" opacity="0"/><path class="mBrR" opacity="0"/></g>
 <path d="M191,224 Q200,219 209,224 Q206,234 200,237 Q194,234 191,224 Z" fill="${v.nose}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>
 <path d="M200,236 L200,243" fill="none" stroke="${INK}" stroke-width="4" stroke-linecap="round"/>
 <g class="mMouthOpen" opacity="0"><path class="mMouthO" fill="#E5657A" stroke="${INK}" stroke-width="4.2" stroke-linejoin="round"/>
   <g clip-path="url(#${g('mMouthC')})"><ellipse class="mTongue" cx="200" rx="7" ry="4.5" fill="#F99DAB"/></g></g>
 <path class="mMouthC2" fill="none" stroke="${INK}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
 <g class="mCollar"><path d="M112,262 Q200,290 288,262" stroke="${INK}" stroke-width="18" stroke-linecap="round" fill="none"/>
  <path d="M112,262 Q200,290 288,262" stroke="${COLLAR}" stroke-width="11" stroke-linecap="round" fill="none"/>
  <circle cx="200" cy="287" r="15" fill="${TAG}" stroke="${INK}" stroke-width="4.5"/>
  <text x="200" y="296" text-anchor="middle" font-family="Jua,'Noto Sans CJK KR',sans-serif" font-size="23" fill="${INK}">?</text></g>
 <g class="mArmR"><path d="${ARM}" fill="${v.mid}"/><g clip-path="url(#${g('mArmC')})"><rect x="-25" y="30" width="50" height="36" fill="${v.paw}"/></g><path d="${ARM}" fill="none" stroke="${INK}" stroke-width="6.5" stroke-linejoin="round"/></g>
 <g class="mArmL"><path d="${ARM}" fill="${v.mid}"/><g clip-path="url(#${g('mArmC')})"><rect x="-25" y="30" width="50" height="36" fill="${v.paw}"/></g><path d="${ARM}" fill="none" stroke="${INK}" stroke-width="6.5" stroke-linejoin="round"/></g>
 <ellipse cx="156" cy="404" rx="26" ry="13" fill="${v.paw}" stroke="${INK}" stroke-width="5"/>
 <ellipse cx="244" cy="404" rx="26" ry="13" fill="${v.paw}" stroke="${INK}" stroke-width="5"/>
 <path class="mSweat" d="M322,112 Q336,136 322,149 Q308,136 322,112 Z" fill="#9AD8FF" stroke="#5FA9D8" stroke-width="2.5" opacity="0"/>
 <g class="mMark" opacity="0"><text class="mMarkT" x="330" y="40" font-family="Jua" font-size="92" fill="#E2483A" stroke="#fff" stroke-width="7" paint-order="stroke">?</text></g>
</g>
</svg>`;
}
const DEF={blink:0,happy:0,surprise:0,open:0,smile:0,w:0,lid:.45,browL:0,browR:0,gx:0,gy:0,armL:0,armR:0,hop:0,squash:0,tilt:0,tail:0,sweat:0,mark:'',markO:0};
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
function mount(el,opt={}){
  const v=V[opt.variant||'cream']; if(!v) throw new Error('없는 모리 변형: '+opt.variant+' (있는 것: '+Object.keys(V).join(', ')+')');
  const p='_'+(uid++);
  el.innerHTML=svg(v,p);
  const q=s=>el.querySelector(s);
  function eyeDraw(side,st){
    const ex=EX[side], g=q(side?'#mEyeR'+p:'#mEyeL'+p);
    const hp=cl(st.happy), bl=cl(st.blink);
    const lid=cl(side?(st.lidR!=null?st.lidR:st.lid):(st.lidL!=null?st.lidL:st.lid))*(1-cl(st.surprise))*(1-hp);
    const o=g.querySelector('.open'), sh=g.querySelector('.shut'), hy=g.querySelector('.happy');
    const showHappy=hp>=.5, showShut=!showHappy&&bl>=.85, showOpen=!showHappy&&!showShut;
    o.setAttribute('opacity',showOpen?1:0);
    const sy=(1-bl*.9)*(1+st.surprise*.18), sx=1+st.surprise*.12;
    o.setAttribute('transform',`translate(${st.gx*4} ${st.gy*3}) scale(${sx} ${sy})`);
    sh.setAttribute('opacity',showShut?1:0);
    hy.setAttribute('opacity',showHappy?1:0); hy.setAttribute('transform',`scale(1 ${Math.max(.2,(hp-.5)*2)})`);
    // 눈꺼풀(반쯤 감은 눈) — 털색으로 눈 위를 덮고 아래 가장자리에 선 하나
    const L=EY-18*sy+36*sy*lid;
    const lidP=q(side?'.mLidR':'.mLidL'), lnP=q(side?'.mLidRn':'.mLidLn');
    const on=showOpen&&lid>.05;
    lidP.setAttribute('opacity',on?1:0); lnP.setAttribute('opacity',on?1:0);
    lidP.setAttribute('d',`M${ex-25},${EY-30} L${ex+25},${EY-30} L${ex+25},${L} Q${ex},${L+6} ${ex-25},${L} Z`);
    lnP.setAttribute('d',`M${ex-16},${L-1} Q${ex},${L+5} ${ex+16},${L-1}`);
  }
  function draw(s){
    const st={...DEF,...s};
    const sx=1+st.squash*.10, sy=1-st.squash*.10;
    q('.mRoot').setAttribute('transform',`translate(0 ${-st.hop}) translate(200 410) scale(${sx} ${sy}) translate(-200 -410) rotate(${st.tilt} 200 300)`);
    q('.mSh').setAttribute('rx',118-st.hop*.4); q('.mSh').setAttribute('opacity',1-st.hop/200);
    q('.mTail').setAttribute('transform',`rotate(${st.tail*10} 246 398)`);
    eyeDraw(0,st); eyeDraw(1,st);
    // 눈썹: 치켜뜬 눈썹(의심) · 깜짝일 때 둘 다
    [['.mBrL',st.browL,136,166],['.mBrR',st.browR,266,234]].forEach(([c,b,x0,x1])=>{
      const e=q(c); const bb=cl(b); e.setAttribute('opacity',cl(bb*1.5));
      const y=170-bb*14, m=(x0+x1)/2; e.setAttribute('d',`M${x0},${y+3} Q${m},${y-7} ${x1},${y+1}`);
    });
    // 입: 열림 > 웃음 > ω > 기본(시큰둥한 일자)
    const o=cl(st.open+st.surprise*.5);
    const mo=q('.mMouthOpen'), mc=q('.mMouthC2');
    if(o>.08){
      const d=5+20*o, mw=12+3*o;
      const pth=`M${200-mw},246 Q${200-mw/2+.5},251 200,247 Q${200+mw/2-.5},251 ${200+mw},246 Q${200+mw-1},${246+d} 200,${248+d} Q${200-mw+1},${246+d} ${200-mw},246 Z`;
      q('.mMouthO').setAttribute('d',pth); q('.mMouthCP').setAttribute('d',pth);
      const tg=q('.mTongue'); tg.setAttribute('cy',246+d*.75); tg.setAttribute('ry',2+2.6*o);
      mo.setAttribute('opacity',1); mc.setAttribute('opacity',0);
    } else {
      mo.setAttribute('opacity',0); mc.setAttribute('opacity',1);
      mc.setAttribute('d',st.smile>.5?'M186,244 Q200,257 214,244':st.w>.5?'M186,244 Q193,251 200,245 Q207,251 214,244':'M188,247 Q200,251 213,245');
    }
    const aR=32+126*cl(st.armR,-.2,1.1), aL=-(32+126*cl(st.armL,-.2,1.1));
    q('.mArmR').setAttribute('transform',`translate(300,290) rotate(${aR})`);
    q('.mArmL').setAttribute('transform',`translate(100,290) rotate(${aL})`);
    q('.mSweat').setAttribute('opacity',st.sweat||0);
    q('.mMark').setAttribute('opacity',st.markO||0); if(st.mark) q('.mMarkT').textContent=st.mark;
    q('.mBlL').setAttribute('opacity',.7+.3*cl(st.happy)); q('.mBlR').setAttribute('opacity',.7+.3*cl(st.happy));
  }
  draw({});
  return {el,draw,variant:opt.variant||'cream'};
}
window.Mori={mount,variants:Object.keys(V),DEF};
})();
