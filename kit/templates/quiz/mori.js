// 모리(고양이, 도리의 상대역) 3판(2026-11-10 사용자 확정 과정): 능글맞은 고양이 — 도리(성실·귀여움)와 대비.
// 얼굴: 둥근 눈꺼풀 눈(A2 — 곡선, 일자로 깎지 않는다) · 한쪽 입꼬리 · 눈썹 점 · 고개 살짝 기울임.
// 몸: 짝다리로 서서 화면 오른쪽 손은 허리, 왼쪽 손은 늘어뜨렸다가 말할 때 도리 쪽으로 내민다.
// 색: 벽(연한 살구색)에 묻히지 않게 털색을 한 단계 진하게, 몸·머리에 도리처럼 위→아래 그라데이션. 발밑 그림자는 도리와 같은 SK.ground(화면 쪽에서 깐다).
// 선: 이어지는 곳(어깨→팔, 다리→발)은 한 줄, 겹치는 곳(몸 앞의 팔, 몸 뒤의 꼬리)은 앞쪽 선을 그린다. 화면에서 도리 키의 약 1.5배.
// const m=Mori.mount(el); m.draw(st)  viewBox 20 -20 400 570, 발바닥 y≈527
// st:{blink,open,smile,lid,lidL,lidR,browL,browR,gx,gy,armL(내미는 손 0~1),armR,hop,squash,tilt,tail,sweat}
(function(){
const K='#4A3A33',C0='#FBE3B6',C1='#EDC78C',LT='#FFF7E4',BR='#B5764A',TAN='#CFA57A';
const HEAD='M215,62 C270,62 318,96 326,150 C328,164 326,176 322,186 L342,197 L316,206 C296,238 258,252 215,252 C172,252 134,238 114,206 L88,197 L108,186 C104,176 102,164 104,150 C112,96 160,62 215,62 Z',EAR='M116,134 C104,84 110,38 124,10 C128,1 139,1 145,8 C168,34 188,58 200,78 Z',EARI='M130,116 C123,80 128,50 135,30 C152,50 168,68 178,84 Z',TAIL='M176,468 C116,482 78,442 92,392 C103,352 140,332 128,294 C120,268 92,262 80,284',TIP='M128,294 C120,268 92,262 80,284',BODY='M163.9,262 C146.6,276 144.1,300 154.0,330 C159.0,352 151.5,372 151.5,392 C151.5,428 154.0,466 151.5,502 L196.2,504 C201.1,474 208.6,446 221.0,424 C235.8,444 255.7,474 268.1,504 L310.2,496 C297.8,462 283.0,420 280.5,388 C280.5,368 273.0,350 278.0,330 C287.9,300 285.4,276 268.1,262 Z';
const wx=x=>216+(x-216)*1.24;
const HANG=[[178,288],[148,308],[138,344],[144,374]],GEST=[[180,288],[156,302],[134,300],[118,282]],HIP=[[252,286],[300,294],[304,342],[268,362]],HIP2=[[252,286],[298,296],[310,330],[284,356]];
let uid=0;
function svg(p){
  const ear=`<path d="${EAR}" fill="${C0}" stroke="${K}" stroke-width="6.5" stroke-linejoin="round"/><path d="${EARI}" fill="#F2A58E"/>`;
  const foot=(x,y,r,f)=>`<g transform="rotate(${r} ${wx(x)} ${y})"><ellipse cx="${wx(x)}" cy="${y}" rx="33" ry="15" ${f}/></g>`;
  const arm=c=>`<g class="${c}"><path class="i" stroke="${K}" stroke-width="43" stroke-linecap="round" fill="none"/><path class="f" stroke="${C0}" stroke-width="30" stroke-linecap="round" fill="none"/>
   <path class="w" pathLength="100" stroke-dasharray="18 200" stroke-dashoffset="-82" stroke="#FFFDFB" stroke-width="30" stroke-linecap="round" fill="none"/>
   <g clip-path="url(#mBC${p})"><circle class="s" r="25" fill="${C0}"/></g><path class="t" stroke="${K}" stroke-width="3" stroke-linecap="round" fill="none"/></g>`;
  const eye=i=>`<g class="mEye${i}"><clipPath id="mE${i}${p}"><path class="cp"/></clipPath><path class="wh" fill="#FFFBF2"/>
   <g clip-path="url(#mE${i}${p})"><g class="ball"><ellipse class="pu" rx="12.5" ry="15" fill="#3A2219"/><circle class="h1" r="4.3" fill="#fff"/><circle class="h2" r="2" fill="#fff" opacity=".8"/></g></g>
   <path class="bo" fill="none" stroke="${K}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path class="to" fill="none" stroke="${K}" stroke-width="6" stroke-linecap="round"/></g>`;
  return `<svg viewBox="20 -20 400 570" width="100%" height="100%" overflow="visible" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="mGB${p}" x1="0" y1="262" x2="0" y2="510" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="${C0}"/><stop offset=".45" stop-color="${C0}"/><stop offset="1" stop-color="${C1}"/></linearGradient><linearGradient id="mGH${p}" x1="0" y1="62" x2="0" y2="252" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FDEBC6"/><stop offset=".6" stop-color="${C0}"/><stop offset="1" stop-color="#F3D29E"/></linearGradient><clipPath id="mBC${p}"><path d="${BODY}"/></clipPath></defs>
<ellipse class="mSh" cx="222" cy="528" rx="112" ry="12" fill="#E6DFDA" opacity="0"/>
<g class="mRoot">
 <g transform="translate(446 0) scale(-1 1)"><g class="mTail"><path d="${TAIL}" stroke="${K}" stroke-width="42" stroke-linecap="round" fill="none"/><path d="${TAIL}" stroke="${C1}" stroke-width="30" stroke-linecap="round" fill="none"/><path d="${TIP}" stroke="${BR}" stroke-width="30" stroke-linecap="round" fill="none"/></g></g>
 <path d="${BODY}" fill="${K}" stroke="${K}" stroke-width="13" stroke-linejoin="round"/>${foot(182,512,-4,`fill="${K}" stroke="${K}" stroke-width="13"`)}${foot(278,510,10,`fill="${K}" stroke="${K}" stroke-width="13"`)}
 <path d="${BODY}" fill="url(#mGB${p})"/><g clip-path="url(#mBC${p})"><ellipse cx="216" cy="366" rx="36" ry="62" fill="${LT}"/></g>${foot(182,512,-4,'fill="#FFFDFB"')}${foot(278,510,10,'fill="#FFFDFB"')}
 ${arm('mArmL')}${arm('mArmR')}
 <path d="M172,246 Q216,262 260,246 L260,266 Q216,282 172,266 Z" fill="#B28FE0" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>
 <circle cx="222" cy="292" r="16" fill="#F2C24B" stroke="${K}" stroke-width="5"/><text x="222" y="300" text-anchor="middle" font-family="Jua,'Noto Sans CJK KR',sans-serif" font-size="22" fill="${K}">?</text>
 <g class="mHead">
  ${ear}<g transform="translate(430 0) scale(-1 1)">${ear}</g>
  <path d="${HEAD}" fill="url(#mGH${p})" stroke="${K}" stroke-width="6.5" stroke-linejoin="round"/><ellipse cx="160" cy="104" rx="30" ry="12" fill="#fff" opacity=".22" transform="rotate(-28 160 104)"/>
  <ellipse cx="217" cy="212" rx="36" ry="24" fill="${LT}"/>
  <ellipse class="mBrL" cx="168" cy="128" rx="12" ry="6" fill="${TAN}"/><ellipse class="mBrR" cx="266" cy="128" rx="12" ry="6" fill="${TAN}"/>
  <ellipse cx="128" cy="204" rx="15" ry="9" fill="#FAA3AB" opacity=".75"/><ellipse cx="306" cy="204" rx="15" ry="9" fill="#FAA3AB" opacity=".75"/>
  <g stroke="${K}" stroke-width="3" stroke-linecap="round"><path d="M112,190 L58,178 M110,200 L52,200 M114,210 L62,222 M318,190 L372,178 M320,200 L378,200 M316,210 L368,222"/></g>
  ${eye(0)}${eye(1)}
  <path d="M209,188 Q217,184 225,188 Q222,195 217,197 Q212,195 209,188 Z" fill="#F2A0A0" stroke="${K}" stroke-width="3" stroke-linejoin="round"/>
  <path class="mMo" fill="#D9566B" stroke="${K}" stroke-width="4.5" stroke-linejoin="round" opacity="0"/><path class="mTg" fill="#F7A0AC" opacity="0"/>
  <path class="mMc" fill="none" stroke="${K}" stroke-width="4.8" stroke-linecap="round" stroke-linejoin="round"/>
  <path class="mSweat" d="M334,96 Q346,118 334,130 Q322,118 334,96 Z" fill="#9AD8FF" stroke="#5FA9D8" stroke-width="2.5" opacity="0"/>
 </g>
</g></svg>`;
}
const DEF={blink:0,open:0,smile:0,lid:.42,browL:0,browR:0,gx:0,gy:0,armL:0,armR:0,hop:0,squash:0,tilt:0,tail:0,sweat:0};
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), lp=(a,b,k)=>a+(b-a)*k;
function mount(el){
  const p='_'+(uid++); el.innerHTML=svg(p); const q=s=>el.querySelector(s);
  function armDraw(c,A,B,k){
    const P=A.map((a,i)=>[wx(lp(a[0],B[i][0],k)),lp(a[1],B[i][1],k)]), g=q('.'+c);
    const d=`M${P[0][0]},${P[0][1]} C${P[1][0]},${P[1][1]} ${P[2][0]},${P[2][1]} ${P[3][0]},${P[3][1]}`;
    ['i','f','w'].forEach(n=>g.querySelector('.'+n).setAttribute('d',d));
    const s=g.querySelector('.s'); s.setAttribute('cx',P[0][0]); s.setAttribute('cy',P[0][1]);
    let ux=P[3][0]-P[2][0],uy=P[3][1]-P[2][1]; const L=Math.hypot(ux,uy)||1; ux/=L; uy/=L; const px=-uy,py=ux; let t='';
    for(const o of [-5.5,5.5]){const x0=P[3][0]+ux*13+px*o,y0=P[3][1]+uy*13+py*o; t+=`M${x0.toFixed(1)},${y0.toFixed(1)} L${(x0-ux*9).toFixed(1)},${(y0-uy*9).toFixed(1)} `;}
    g.querySelector('.t').setAttribute('d',t);
  }
  function eyeDraw(i,st,lid){
    const x=i?264:170,o=i?1:-1,y=158,g=q('.mEye'+i),b=cl(st.blink);
    const op=5+(.42-lid)*22, c0=y-15-op, c=lp(c0,y+19,b), xi=x-o*23,xo=x+o*23;
    const top=`M${xi},${y-1} Q${x},${c} ${xo},${y-1}`, bot=`Q${xo-o},${y+17} ${x},${y+17} Q${xi+o},${y+17} ${xi},${y-1}`;
    const sh=top+' '+bot+' Z', shut=b>.8;
    g.querySelector('.cp').setAttribute('d',sh); g.querySelector('.wh').setAttribute('d',sh); g.querySelector('.wh').setAttribute('opacity',shut?0:1);
    g.querySelector('.bo').setAttribute('d',`M${xo},${y-1} `+bot); g.querySelector('.bo').setAttribute('opacity',shut?0:1);
    g.querySelector('.to').setAttribute('d',top); g.querySelector('.ball').setAttribute('opacity',shut?0:1);
    const px=x+st.gx*2.6, py=y+3+st.gy*1.5;
    g.querySelector('.pu').setAttribute('cx',px); g.querySelector('.pu').setAttribute('cy',py);
    g.querySelector('.h1').setAttribute('cx',px-4.5); g.querySelector('.h1').setAttribute('cy',py-3);
    g.querySelector('.h2').setAttribute('cx',px+5); g.querySelector('.h2').setAttribute('cy',py+6);
  }
  function draw(s){
    const st={...DEF,...s};
    const sx=1+st.squash*.08, sy=1-st.squash*.08;
    q('.mRoot').setAttribute('transform',`translate(0 ${-st.hop}) translate(222 527) scale(${sx} ${sy}) translate(-222 -527)`);
    q('.mSh').setAttribute('rx',112-st.hop*.4);
    q('.mTail').setAttribute('transform',`rotate(${st.tail*6} 176 468)`);
    q('.mHead').setAttribute('transform',`rotate(${-5+st.tilt} 216 250)`);
    armDraw('mArmL',HANG,GEST,cl(st.armL)); armDraw('mArmR',HIP,HIP2,cl(st.armR));
    const lid=((st.lidL!=null?st.lidL:st.lid)+(st.lidR!=null?st.lidR:st.lid))/2;   // 두 눈은 같은 정도로(짝짝이 금지)
    eyeDraw(0,st,lid); eyeDraw(1,st,lid);
    const bl=cl(st.browL)*.5, br=.25+cl(st.browR)*.5;
    q('.mBrL').setAttribute('transform',`translate(0 ${-bl*12}) rotate(-10 168 128)`);
    q('.mBrR').setAttribute('transform',`translate(0 ${-br*14}) rotate(${14+br*12} 266 128)`);
    const o=cl(st.open), mo=q('.mMo'), tg=q('.mTg'), mc=q('.mMc');
    if(o>.1){const d=3+15*o;
      mo.setAttribute('d',`M203,203 Q218,207 238,199 Q236,${203+d} 220,${204+d} Q207,${202+d} 203,203 Z`); mo.setAttribute('opacity',1);
      tg.setAttribute('d',`M211,${200+d} Q221,${194+d} 231,${199+d} Q223,${204+d} 211,${200+d} Z`); tg.setAttribute('opacity',o>.45?1:0);
      mc.setAttribute('d','M217,196 V201');}
    else{mo.setAttribute('opacity',0); tg.setAttribute('opacity',0);
      mc.setAttribute('d',st.smile>.5?'M217,196 V203 M196,203 Q206,211 217,204 Q230,212 246,194 M243,188 Q250,193 246,201':'M217,196 V203 M200,204 Q208,211 217,204 Q227,211 239,200');}
    q('.mSweat').setAttribute('opacity',st.sweat||0);
  }
  draw({}); return {el,draw,variant:'cream'};
}
window.Mori={mount,variants:['cream'],DEF};
})();
