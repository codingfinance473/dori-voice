// 도리 옷장(주제별 옷) — 숫자 퀴즈·생활 정보·해설(templates/quiz/dori.js)과 가격 검산(shopping/assets/dori.js)이 같이 쓴다.
// 이 파일 하나가 정본이다. new_episode.sh 와 shopping render.py 가 복사해 간다.
//   DoriOutfit.list()                       → 옷 이름들
//   DoriOutfit.apply(slots, name)           → slots={body,top,head,gloves:[g,g],hands:{R,L},bag} 에 옷을 넣는다(옷을 입으면 크로스백은 숨긴다). handR = 오른팔(화면 오른쪽)에 든 소품
//   DoriOutfit.anim(root, st)               → 매 프레임: 볼주머니 마스크 + 매듭·방울·넥타이·목도리 끝 흔들림 + 손 소품 똑바로  st={t,hop,squash,ckL:[cx,cy,r],ckR:[…],armRdeg,armLdeg}
//   DoriOutfit.check(root)                  → 렌더 전 점검: 옷이 눈·코·입을 가리는지, 장갑이 두 팔에 다 있는지, 가방이 숨었는지 → 문제 목록
// 자연스럽게 보이게: ① 몸 옷은 몸 윤곽으로 잘라 몸을 감싸고(볼주머니가 부풀면 볼 뒤로) ② 둥근 몸을 따라 가장자리가 어두워지는 명암
// ③ 모자·목도리 아래 털에 떨어지는 부드러운 그림자 ④ 천 주름·짜임·광택 ⑤ 매듭·방울·넥타이·목도리 끝은 숨·점프에 살짝 늦게 흔들린다.
// 새 옷을 더할 때 규칙(SKILL 9절): 머리 옷은 y 186 위(눈 위)에서 끝나고, 몸 옷은 y 262 아래(입 아래)에서 시작한다. 얼굴에 닿는 것은 face(안경 같은 투명한 것)만.
(function(){
const BODY='M200,86 C282,86 338,134 346,200 C350,236 346,262 338,288 C352,330 342,398 262,402 L138,402 C58,398 48,330 62,288 C54,262 50,236 54,200 C62,134 118,86 200,86 Z';
const DEFS=`<defs>
  <mask id="dBodyM" maskUnits="userSpaceOnUse" x="-70" y="-70" width="540" height="560"><path d="${BODY}" fill="#fff"/><circle class="omkL" cx="84" cy="262" r="0" fill="#000"/><circle class="omkR" cx="316" cy="262" r="0" fill="#000"/></mask>
  <radialGradient id="dRound" cx="200" cy="320" r="175" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#2A1A10" stop-opacity="0"/><stop offset=".62" stop-color="#2A1A10" stop-opacity="0"/><stop offset="1" stop-color="#2A1A10" stop-opacity=".18"/></radialGradient>
  <radialGradient id="dDome" cx="160" cy="70" r="200" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#2A1A10" stop-opacity=".22"/></radialGradient>
  <clipPath id="dHeadC"><path d="${BODY}"/></clipPath>
  <filter id="dSoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.5"/></filter></defs>`;
const OL='#4A3A33';
// 옷 조각: 자기 모양으로 잘라 바탕 · 무늬 · 둥근 명암을 칠하고 외곽선
function G(id,d,fill,extra='',sw=4.6,round=true){return `<clipPath id="dG${id}"><path d="${d}"/></clipPath>
 <g clip-path="url(#dG${id})"><path d="${d}" fill="${fill}"/>${extra}${round?'<rect x="-70" y="-70" width="540" height="560" fill="url(#dRound)"/>':''}</g>
 <path class="oo" d="${d}" fill="none" stroke="${OL}" stroke-width="${sw}" stroke-linejoin="round" stroke-linecap="round"/>`;}
// 털에 떨어지는 그림자(옷 가장자리 아래)
const SH=(d,dy=7,o=.16)=>`<path d="${d}" transform="translate(0 ${dy})" fill="#2A1A10" opacity="${o}" filter="url(#dSoft)"/>`;
// 손에 드는 소품은 쓰지 않는다(2026-11-04 사용자 의견: 쥔 모습이 어색함, 머리에 꽂는 것도 어색함). 주제 표시는 입거나 거는 것(모자·옷·목걸이·주머니)으로 한다.
// (hands 자리와 handR/handL 은 남겨 두지만 옷장에서는 비워 둔다.)
// 목선: 옷 윗단은 일직선으로 몸을 가르지 않고, 하얀 주둥이(턱) 아래를 따라 둥글게 돈다(2026-11-04 — 직선이 몸을 긋는 것처럼 보였음).
//   NY(x) = 그 x 에서 목선 높이(몸 옆 y 262 → 가운데 y 316). NK(x0,x1,dy) = x0→x1 목선을 따라가는 "L x,y …" 조각.
const NY=x=>262+54*Math.sqrt(Math.max(0,1-((x-200)/148)**2));
const NK=(x0,x1,dy=0)=>{let o='';const n=Math.max(2,Math.round(Math.abs(x1-x0)/6));for(let i=0;i<=n;i++){const x=x0+(x1-x0)*i/n;o+=` L${x.toFixed(1)},${(NY(x)+dy).toFixed(1)}`;}return o;};
// 몸 전체를 덮는 옷(티·셔츠·후드): 목선 아래만
const FULL=`M10,230 L52,262${NK(52,348)} L390,230 L390,440 L10,440 Z`;
// 앞이 V로 트인 옷(재킷·조끼·카디건·코트·셔츠): 왼판·오른판. vx = 목선에서 V가 시작하는 x, vy = V 바닥
const PL=(vx=176,vy=360)=>`M10,230 L52,262${NK(52,vx)} L200,${vy} L203,440 L10,440 Z`;
const PR=(vx=224,vy=360)=>`M390,230 L348,262${NK(348,vx)} L200,${vy} L197,440 L390,440 Z`;
// 턱 아래 그림자: 둥근 얼굴이 옷 위에 드리우는 초승달 그림자(옷이 얼굴 '뒤·아래'에 있게 보인다)
const CHIN=()=>`<path d="M64,${NY(64)} Q200,350 336,${NY(336)} Q200,330 64,${NY(64)} Z" fill="#2A1A10" opacity=".13" filter="url(#dSoft)"/>`;
// 셔츠 깃(V 꼭대기 양쪽)
const COLLAR=(c='#FFFFFF',vx=176,vy=340)=>G('cL'+c.slice(1),`M${vx+2},${NY(vx+2)-2} L200,${vy} L${vx+8},${vy+6} L${vx-10},${NY(vx-10)+8} Z`,c,'',4,false)+G('cR'+c.slice(1),`M${398-vx},${NY(398-vx)-2} L200,${vy} L${392-vx},${vy+6} L${410-vx},${NY(410-vx)+8} Z`,c,'',4,false);

// ---- 옷장 도우미(3판에서 만듦, 4판도 씀): 귀엽게, 유치하지 않게 ----
// 원칙: ① 하얀 배는 보이게(앞이 트이거나 짧은 옷) ② 모자는 작게·살짝 기울여 귀가 보이게 ③ 채도 낮춘 차분한 색
//      ④ 무늬·선은 최소(외곽선 4px, 안쪽은 같은 계열 색 선) ⑤ 둥근 끝(뾰족한 삼각형 대신)
const OW=4;
// 앞이 트인 옷(재킷·카디건·가운·셔츠): 목선 xn 에서 시작한 앞섶이 둥글게 내려와 xb(아래 끝 x)에서 끝난다. yb 가 440 이면 끝까지, 작으면 짧은 옷.
const OPEN_L=(xn,xb,yb=440)=>`M10,230 L52,262${NK(52,xn)} C${xn},${(NY(xn)+46).toFixed(1)} ${xb+6},${yb-70} ${xb},${yb}`+(yb<430?` Q${((xb+10)/2).toFixed(0)},${yb+8} 10,${yb-8} Z`:` L10,${yb} Z`);
const OPEN_R=(xn,xb,yb=440)=>`M390,230 L348,262${NK(348,400-xn)} C${400-xn},${(NY(400-xn)+46).toFixed(1)} ${400-xb-6},${yb-70} ${400-xb},${yb}`+(yb<430?` Q${((790-xb)/2).toFixed(0)},${yb+8} 390,${yb-8} Z`:` L390,${yb} Z`);
// 앞섶 가장자리 띠(안감·파이핑): 옷 조각 안쪽에만 보이게 G 의 무늬로 넣는다
const EDGE_L=(xn,xb,yb,c,w=18)=>`<path d="M${xn},${NY(xn).toFixed(1)} C${xn},${(NY(xn)+46).toFixed(1)} ${xb+6},${yb-70} ${xb},${yb}" stroke="${c}" stroke-width="${w}" fill="none"/>`;
const EDGE_R=(xn,xb,yb,c,w=18)=>`<path d="M${400-xn},${NY(400-xn).toFixed(1)} C${400-xn},${(NY(400-xn)+46).toFixed(1)} ${400-xb-6},${yb-70} ${400-xb},${yb}" stroke="${c}" stroke-width="${w}" fill="none"/>`;
// 둥근 셔츠 깃(목선 가운데 양쪽 꽃잎 모양)
const RCOL=(c='#FFFFFF')=>G('rcL'+c.slice(1),`M200,${NY(200)-1} Q186,${NY(186)-3} 174,${(NY(174)+2).toFixed(1)} Q172,336 188,338 Q198,334 200,${NY(200)+4} Z`,c,'',3.6,false)+G('rcR'+c.slice(1),`M200,${NY(200)-1} Q214,${NY(214)-3} 226,${(NY(226)+2).toFixed(1)} Q228,336 212,338 Q202,334 200,${NY(200)+4} Z`,c,'',3.6,false);
// 머리에 맞춰 쓰는 것(두건·고글 끈): 머리 윤곽 안에서만 보이게 — 귀는 밖으로 나온다
const FIT=inner=>`<g clip-path="url(#dHeadC)">${inner}</g>`;
// 작은 모자는 정수리 가운데에 살짝 기울여 얹는다
const TILT=(a,inner)=>`<g transform="rotate(${a} 200 96)">${inner}</g>`;

// V 앞섶을 따라 내려오는 띠(옷깃·라펠): 그 옷 조각 안쪽에만 보이게 G 의 무늬로 넣는다
const VEDGE_L=(vx,vy,c,w=28)=>`<path d="M${vx},${NY(vx).toFixed(1)} L200,${vy}" stroke="${c}" stroke-width="${w}" fill="none"/>`;
const VEDGE_R=(vx,vy,c,w=28)=>`<path d="M${400-vx},${NY(400-vx).toFixed(1)} L200,${vy}" stroke="${c}" stroke-width="${w}" fill="none"/>`;

// ---- 옷장 4판(2026-11-04): 한눈에 주제가 보이고, 몸에 맞게 '입은' 옷 ----
// 3판(가볍고 작은 옷)은 "모자·옷이 작아 입은 느낌이 안 난다"는 의견 → 모자는 머리에 맞는 크기(챙 폭 210~260, 머리 위를 덮음),
// 옷은 어깨부터 끝까지 덮는 제 크기. 3판의 차분한 색·둥근 깃·적은 선은 그대로. 주제마다 대표 아이템 하나는 분명하게.
const OUTFIT={
 // 1) 경제 뉴스·해설 — 남색 정장 재킷(라펠) + 둥근 흰 깃 + 민트 넥타이 + 행커치프
 news:{bag:false,
  body:`${G('nbl',PL(172,372),'#5B6E9A',VEDGE_L(172,372,'#7184B0',30)+'<path d="M64,322 Q88,380 82,440" stroke="#52648E" stroke-width="4" fill="none"/>',OW)}
   ${G('nbr',PR(228,372),'#5B6E9A',VEDGE_R(228,372,'#7184B0',30)+'<path d="M336,322 Q312,380 318,440" stroke="#52648E" stroke-width="4" fill="none"/>',OW)}
   <path d="M72,350 h32" stroke="#4A5B84" stroke-width="3.5" stroke-linecap="round"/><path d="M79,349 q4,-13 9,-13 q5,0 9,13 z" fill="#A8DCCB" stroke="${OL}" stroke-width="2.6" stroke-linejoin="round"/>
   <circle cx="200" cy="388" r="5.5" fill="#4A5B84" stroke="${OL}" stroke-width="2.6"/>${CHIN()}`,
  top:`${RCOL('#FFFFFF')}
   <g data-sw="1.4,2.2,200,326,0">${SH('M193,334 L207,334 L212,374 Q200,388 188,374 Z',4,.12)}
    ${G('tie','M193,333 L207,333 L212,372 Q200,388 188,372 Z','#3FA88F','<path d="M184,354 L216,342 M184,370 L216,358" stroke="#6CC2AC" stroke-width="4"/>',3.4,false)}
    <rect x="192.5" y="319" width="15" height="15" rx="5" fill="#2E9C83" stroke="${OL}" stroke-width="3.4"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="54" fill="#5B6E9A"/><rect x="-27" y="22" width="54" height="9" fill="#FFFDF8"/><path d="M-27,22 H27 M-27,31 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 2) 세금·연말정산·연금 — 초록 차양 바이저 + 동그란 안경 + 오트밀 니트 조끼(흰 셔츠 소매) + 남색 나비넥타이
 tax:{bag:false,
  head:`${FIT(`<path d="M20,146 Q200,112 380,146" stroke="${OL}" stroke-width="13" fill="none"/><path d="M20,146 Q200,112 380,146" stroke="#5FA77F" stroke-width="7" fill="none"/>`)}
   ${SH('M110,134 Q200,116 290,134 Q284,160 200,162 Q116,160 110,134 Z',5,.16)}
   ${G('vb','M108,132 Q200,114 292,132 Q286,160 200,163 Q114,160 108,132 Z','#86C9A3','<path d="M120,140 Q200,124 280,140" stroke="#B9E3CB" stroke-width="4" fill="none"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',OW,false).replace('fill="#86C9A3"/>','fill="#86C9A3" opacity=".92"/>')}`,
  face:`<g fill="#fff" fill-opacity=".1" stroke="#8A6B4E" stroke-width="3.6"><circle cx="148" cy="214" r="28"/><circle cx="252" cy="214" r="28"/></g>
   <path d="M176,211 Q200,201 224,211" fill="none" stroke="#8A6B4E" stroke-width="3.6" stroke-linecap="round"/>
   <path d="M120,208 L94,200 M280,208 L306,200" stroke="#8A6B4E" stroke-width="3.6" stroke-linecap="round"/>
   <path d="M131,199 Q138,192 146,191 M235,199 Q242,192 250,191" stroke="#fff" stroke-width="3.5" stroke-linecap="round" opacity=".8" fill="none"/>`,
  body:`${G('tvl',PL(182,354),'#E8D7BC','<path d="M10,398 H200" stroke="#D6BF9B" stroke-width="18"/><path d="M24,392 v12 M40,392 v12 M56,392 v12 M72,392 v12 M88,392 v12 M104,392 v12 M120,392 v12 M136,392 v12 M152,392 v12 M168,392 v12 M184,392 v12" stroke="#C9AF87" stroke-width="2.2"/><path d="M112,316 q9,12 0,24 q-9,12 0,24 q9,12 0,24" stroke="#DCC7A6" stroke-width="4" fill="none"/>',OW)}
   ${G('tvr',PR(218,354),'#E8D7BC','<path d="M200,398 H390" stroke="#D6BF9B" stroke-width="18"/><path d="M216,392 v12 M232,392 v12 M248,392 v12 M264,392 v12 M280,392 v12 M296,392 v12 M312,392 v12 M328,392 v12 M344,392 v12 M360,392 v12 M376,392 v12" stroke="#C9AF87" stroke-width="2.2"/><path d="M288,316 q-9,12 0,24 q9,12 0,24 q-9,12 0,24" stroke="#DCC7A6" stroke-width="4" fill="none"/>',OW)}${CHIN()}`,
  top:`${RCOL('#FFFFFF')}
   <g data-sw="1.2,2.0,200,334,1"><path d="M200,334 Q184,321 176,328 Q173,336 176,344 Q184,350 200,338 Z" fill="#5B6E9A" stroke="${OL}" stroke-width="3.2" stroke-linejoin="round"/>
    <path d="M200,334 Q216,321 224,328 Q227,336 224,344 Q216,350 200,338 Z" fill="#5B6E9A" stroke="${OL}" stroke-width="3.2" stroke-linejoin="round"/>
    <rect x="194.5" y="330" width="11" height="11" rx="3.5" fill="#4A5B84" stroke="${OL}" stroke-width="3"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#FFFDF8"/><rect x="-27" y="16" width="54" height="10" fill="#EEE8DE"/><path d="M-27,16 H27 M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 3) 수출·산업·무역 — 노란 안전모 + 주황 안전 조끼(반사띠) + 데님 작업 셔츠
 export:{bag:false,
  head:`${TILT(-4,`${SH('M92,128 Q200,112 308,128 Q311,140 296,144 Q200,128 104,144 Q89,140 92,128 Z',6,.2)}
   ${G('hh','M108,128 C110,74 150,50 200,50 C250,50 290,74 292,128 Z','#F4D47A','<path d="M200,50 V128" stroke="#FAE6A8" stroke-width="18"/><path d="M186,52 V128 M214,52 V128" stroke="#E6C060" stroke-width="3"/><path d="M134,92 Q144,68 170,60" stroke="#fff" stroke-width="6" stroke-linecap="round" fill="none" opacity=".7"/>',OW,false)}
   ${G('hb','M90,128 Q200,110 310,128 Q313,140 298,145 Q200,128 102,145 Q87,140 90,128 Z','#E9C25C','<path d="M104,134 Q200,118 296,134" stroke="#F4D47A" stroke-width="4" fill="none"/>',OW,false)}`)}`,
  body:`${G('wsh',FULL,'#8DA8CC','<path d="M200,330 V440" stroke="#7D97BC" stroke-width="3"/><circle cx="206" cy="350" r="3" fill="#E9EEF2"/><circle cx="206" cy="374" r="3" fill="#E9EEF2"/><circle cx="206" cy="398" r="3" fill="#E9EEF2"/>')}
   ${G('svl',`M10,230 L52,262${NK(52,180)} L186,440 L10,440 Z`,'#F0A35E','<path d="M10,352 H200 M10,388 H200" stroke="#E9EEF2" stroke-width="14"/><path d="M10,347 H200 M10,383 H200" stroke="#fff" stroke-width="3" opacity=".85"/><path d="M110,300 V440" stroke="#E08E48" stroke-width="2.6" stroke-dasharray="7 7"/>',OW)}
   ${G('svr',`M390,230 L348,262${NK(348,220)} L214,440 L390,440 Z`,'#F0A35E','<path d="M200,352 H390 M200,388 H390" stroke="#E9EEF2" stroke-width="14"/><path d="M200,347 H390 M200,383 H390" stroke="#fff" stroke-width="3" opacity=".85"/><path d="M290,300 V440" stroke="#E08E48" stroke-width="2.6" stroke-dasharray="7 7"/>',OW)}
   <rect x="242" y="316" width="30" height="22" rx="5" fill="#FFFDF8" stroke="${OL}" stroke-width="3"/><path d="M248,323 h18 M248,330 h12" stroke="#C9D0D6" stroke-width="2.6" stroke-linecap="round"/>${CHIN()}`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#8DA8CC"/><rect x="-27" y="16" width="54" height="10" fill="#7D97BC"/><path d="M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 4) 겨울 생활비 — 방울 털모자(귀는 밖으로) + 크림 니트 스웨터 + 로즈 목도리 + 벙어리장갑
 winter:{bag:false,
  head:`${FIT(`<path d="M0,0 H400 V146 Q200,110 0,146 Z" fill="#E3A1AA"/>
    <path d="M120,60 Q114,100 116,140 M160,50 Q156,90 158,132 M200,46 V128 M240,50 Q244,90 242,132 M280,60 Q286,100 284,140" stroke="#D88E98" stroke-width="3" fill="none"/>
    <path d="M0,0 H400 V146 Q200,110 0,146 Z" fill="url(#dDome)"/>
    ${SH('M10,150 Q200,114 390,150 L390,168 Q200,132 10,168 Z',4,.2)}
    <path d="M10,142 Q200,106 390,142 L390,166 Q200,130 10,166 Z" fill="#D88E98"/>
    <path d="M60,138 v20 M84,133 v20 M108,128 v20 M132,124 v20 M156,121 v20 M180,120 v20 M204,120 v20 M228,121 v20 M252,124 v20 M276,128 v20 M300,133 v20 M324,138 v20" stroke="#C97A85" stroke-width="2.4"/>
    <path d="M10,166 Q200,130 390,166" stroke="${OL}" stroke-width="${OW}" fill="none"/>`)}
   <g data-bob="1.2">${SH('M200,62 m-24,0 a24,24 0 1,0 48,0 a24,24 0 1,0 -48,0',4,.14)}
    <path d="M200,38 C213,38 219,45 222,51 C230,53 228,64 225,68 C230,76 221,85 214,83 C210,89 190,89 186,83 C179,85 170,76 175,68 C172,64 170,53 178,51 C181,45 187,38 200,38 Z" fill="#FBF3E6" stroke="${OL}" stroke-width="${OW}" stroke-linejoin="round"/>
    <path d="M189,52 Q195,46 203,46" stroke="#fff" stroke-width="4" stroke-linecap="round" fill="none"/></g>`,
  body:`${G('swt',FULL,'#EFE3CF','<path d="M118,322 q10,12 0,24 q-10,12 0,24 q10,12 0,24 M282,322 q-10,12 0,24 q10,12 0,24 q-10,12 0,24" stroke="#E0D0B4" stroke-width="5" fill="none"/><path d="M10,400 H390" stroke="#E2D2B8" stroke-width="18"/>')}${CHIN()}`,
  top:`<g mask="url(#dBodyM)">${SH(`M50,254${NK(50,350,-6)} L352,${(NY(350)+32).toFixed(1)}${NK(350,50,32)} Z`,6,.18)}
   ${G('scf',`M46,250${NK(48,352,-10)} L354,${(NY(352)+28).toFixed(1)}${NK(352,48,28)} Z`,'#E3A1AA',`<path d="M60,${NY(60)+4}${NK(60,340,4)}" stroke="#ECB7BE" stroke-width="5" fill="none"/><path d="M60,${NY(60)+17}${NK(60,340,17)}" stroke="#D88E98" stroke-width="3" fill="none" opacity=".6"/>`,OW)}</g>
   <g data-sw="2.2,2.3,252,334,0">${SH('M238,330 L274,328 L282,402 L246,406 Z',5,.14)}
    ${G('stl','M236,328 L274,326 L282,400 L244,404 Z','#E3A1AA','<path d="M232,356 L286,352 M234,380 L288,376" stroke="#D88E98" stroke-width="3" opacity=".6"/>',OW,false)}
    <path d="M249,406 l-1,11 M257,405 l0,12 M265,404 l1,12 M273,403 l1,11" stroke="#D88E98" stroke-width="4" stroke-linecap="round"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="50" fill="#EFE3CF"/><rect x="-27" y="18" width="54" height="50" fill="#E3A1AA"/><rect x="-27" y="16" width="54" height="8" fill="#D88E98"/><path d="M-27,16 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 5) 장보기·먹거리·김장 — 물방울 두건(매듭) + 크림 앞치마(세이지 끈·배추 주머니) + 로즈 고무장갑
 kimjang:{bag:false,
  head:`<defs><pattern id="dDot" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)"><circle cx="6" cy="6" r="2.8" fill="#FFF4F2"/><circle cx="17" cy="17" r="2.8" fill="#FFF4F2"/></pattern></defs>
   ${FIT(`<path d="M0,0 H400 V154 Q200,114 0,154 Z" fill="#E59BA4"/><path d="M0,0 H400 V154 Q200,114 0,154 Z" fill="url(#dDot)"/><path d="M0,0 H400 V154 Q200,114 0,154 Z" fill="url(#dDome)"/>
    ${SH('M20,156 Q200,116 380,156 L380,166 Q200,126 20,166 Z',3,.2)}<path d="M20,156 Q200,116 380,156" stroke="#D3848E" stroke-width="12" fill="none"/><path d="M20,154 Q200,114 380,154" stroke="${OL}" stroke-width="${OW}" fill="none"/>`)}
   <g transform="translate(320,146)"><g data-sw="5,2.8,0,0,0"><path d="M0,0 L32,-16 Q40,0 26,10 Z" fill="#E59BA4" stroke="${OL}" stroke-width="3.8" stroke-linejoin="round"/></g>
    <g data-sw="-6,2.4,0,0,1.1"><path d="M0,0 L28,24 Q14,34 3,22 Z" fill="#D3848E" stroke="${OL}" stroke-width="3.8" stroke-linejoin="round"/></g>
    <circle r="11" fill="#D3848E" stroke="${OL}" stroke-width="3.8"/></g>`,
  body:`${G('apr','M138,330 Q200,320 262,330 L268,358 C314,366 346,392 352,440 L48,440 C54,392 86,366 132,358 Z','#FBF5EA','<path d="M48,420 Q200,404 352,420" stroke="#A9C3A0" stroke-width="10" fill="none"/><path d="M96,392 Q106,416 100,440 M304,392 Q294,416 300,440" stroke="#EFE5D3" stroke-width="5" fill="none"/>',OW)}
   <path d="M140,332${NK(140,62,10)}" stroke="${OL}" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M140,332${NK(140,62,10)}" stroke="#A9C3A0" stroke-width="7" stroke-linecap="round" fill="none"/>
   <path d="M260,332${NK(260,338,10)}" stroke="${OL}" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M260,332${NK(260,338,10)}" stroke="#A9C3A0" stroke-width="7" stroke-linecap="round" fill="none"/>
   ${SH('M164,368 h72 v38 h-72 z',3,.12)}${G('apk','M168,366 h64 a9,9 0 0 1 9,9 v24 a9,9 0 0 1 -9,9 h-64 a9,9 0 0 1 -9,-9 v-24 a9,9 0 0 1 9,-9 z','#F3EAD8','<path d="M159,374 H241" stroke="#A9C3A0" stroke-width="4"/>',3.4,false)}
   <g transform="translate(200,378) scale(.78)"><path d="M0,30 C-16,26 -18,6 -6,-4 C-2,6 0,14 0,30 Z" fill="#A9C3A0" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/>
    <path d="M0,30 C16,26 18,6 6,-4 C2,6 0,14 0,30 Z" fill="#93B58A" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/><path d="M0,30 C-7,22 -6,8 0,0 C6,8 7,22 0,30 Z" fill="#F4F7E2" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/></g>${CHIN()}`,
  glove:`<rect x="-27" y="6" width="54" height="62" fill="#E59BA4"/><rect x="-27" y="4" width="54" height="13" rx="3" fill="#F1B9C0"/><path d="M-27,4 H27 M-27,17 H27" stroke="${OL}" stroke-width="2.8"/><path d="M-9,36 Q-5,52 -10,60" stroke="#F1B9C0" stroke-width="3.5" fill="none" stroke-linecap="round" opacity=".8"/>`},

 // 6) 과학·기술·우주·AI — 이마 위 보안경 + 흰 실험 가운(라펠·주머니 펜 두 자루) + 민트 티셔츠
 science:{bag:false,
  head:`${FIT(`<path d="M20,144 Q200,112 380,144" stroke="${OL}" stroke-width="14" fill="none"/><path d="M20,144 Q200,112 380,144" stroke="#8FB9B4" stroke-width="8" fill="none"/>`)}
   ${SH('M136,116 h60 v38 h-60 z M204,116 h60 v38 h-60 z',5,.18)}
   ${G('gl','M146,114 h44 a14,14 0 0 1 14,14 v10 a14,14 0 0 1 -14,14 h-44 a14,14 0 0 1 -14,-14 v-10 a14,14 0 0 1 14,-14 z','#CFEEF3','<path d="M138,124 L166,152 M156,116 L186,148" stroke="#fff" stroke-width="5" opacity=".75"/>',OW,false)}
   ${G('gr','M210,114 h44 a14,14 0 0 1 14,14 v10 a14,14 0 0 1 -14,14 h-44 a14,14 0 0 1 -14,-14 v-10 a14,14 0 0 1 14,-14 z','#CFEEF3','<path d="M202,124 L230,152 M220,116 L250,148" stroke="#fff" stroke-width="5" opacity=".75"/>',OW,false)}
   <path d="M194,132 Q200,126 206,132" stroke="${OL}" stroke-width="6" fill="none" stroke-linecap="round"/>`,
  body:`${G('tee',FULL,'#7CC9B5',`<path d="M70,${NY(70)+6}${NK(70,330,8)}" stroke="#5FB39D" stroke-width="7" fill="none"/>`)}
   ${G('lcl',PL(168,392),'#F4F7FA',VEDGE_L(168,392,'#E3EAF0',30)+'<path d="M66,322 Q92,384 86,440" stroke="#E3EAF0" stroke-width="5" fill="none"/>',OW)}
   ${G('lcr',PR(232,392),'#F4F7FA',VEDGE_R(232,392,'#E3EAF0',30)+'<path d="M334,322 Q308,384 314,440" stroke="#E3EAF0" stroke-width="5" fill="none"/>',OW)}
   <rect x="92" y="328" width="9" height="32" rx="3" fill="#5B8FD9" stroke="${OL}" stroke-width="2.6"/><rect x="105" y="324" width="9" height="36" rx="3" fill="#E58C8C" stroke="${OL}" stroke-width="2.6"/>
   ${G('lpk','M80,340 h46 v28 a7,7 0 0 1 -7,7 h-32 a7,7 0 0 1 -7,-7 z','#EAF0F4','',3.2,false)}
   <circle cx="214" cy="404" r="4.5" fill="#DDE5EC" stroke="${OL}" stroke-width="2.4"/>${CHIN()}`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#F4F7FA"/><path d="M-27,21 H27" stroke="#E3EAF0" stroke-width="7"/><path d="M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 7) 상식·교육·수능 — 졸업식 세트(사용자 선택 A): 학사모(술) + 남색 졸업 가운 + 금색 숄 + 별 배지 + 둥근 흰 깃
 trivia:{bag:false,
  head:`${TILT(-6,`${SH('M118,124 Q200,110 282,124 L282,132 Q200,118 118,132 Z',5,.2)}
   ${G('mc','M118,126 C120,90 156,74 200,74 C244,74 280,90 282,126 Q200,112 118,126 Z','#4E5C86','<rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',OW,false)}
   <path d="M98,58 L98,66 L200,96 L302,66 L302,58" fill="#3F4C74" stroke="${OL}" stroke-width="${OW}" stroke-linejoin="round"/>
   ${G('mb','M200,28 L302,58 L200,88 L98,58 Z','#5A6996','<path d="M142,58 L200,41 L258,58" stroke="#6E7DAA" stroke-width="5" fill="none"/>',OW,false)}
   <g data-sw="4,2.3,298,62,0"><path d="M200,58 Q252,58 298,62 L302,116" fill="none" stroke="#E7BE5E" stroke-width="5" stroke-linecap="round"/>
    <path d="M295,112 h14 l4,22 h-22 z" fill="#E7BE5E" stroke="${OL}" stroke-width="3.2" stroke-linejoin="round"/><path d="M298,120 v12 M302,120 v12 M306,120 v12" stroke="#D4A84A" stroke-width="2"/></g>
   <circle cx="200" cy="58" r="6.5" fill="#E7BE5E" stroke="${OL}" stroke-width="3.2"/>`)}`,
  body:`${G('gwl',PL(176,360),'#4A5880','<path d="M64,322 Q88,382 82,440" stroke="#425078" stroke-width="5" fill="none"/>',OW)}
   ${G('gwr',PR(224,360),'#4A5880','<path d="M336,322 Q312,382 318,440" stroke="#425078" stroke-width="5" fill="none"/>',OW)}
   ${SH(`M144,${NY(144).toFixed(1)} L176,${NY(176).toFixed(1)} L170,440 L134,440 Z`,4,.16)}${SH(`M256,${NY(256).toFixed(1)} L224,${NY(224).toFixed(1)} L230,440 L266,440 Z`,4,.16)}
   ${G('stl',`M142,${(NY(142)-2).toFixed(1)} L176,${(NY(176)-2).toFixed(1)} L170,440 L132,440 Z`,'#E7BE5E','<path d="M160,330 L152,440" stroke="#D4A84A" stroke-width="2.5"/>',OW,false)}
   ${G('str',`M258,${(NY(258)-2).toFixed(1)} L224,${(NY(224)-2).toFixed(1)} L230,440 L268,440 Z`,'#E7BE5E','<path d="M240,330 L248,440" stroke="#D4A84A" stroke-width="2.5"/>',OW,false)}
   <g data-bob="0.6">${SH('M248,366 l6,12 13,2 -9,9 2,13 -12,-6 -12,6 2,-13 -9,-9 13,-2 z',3,.16)}<path d="M246,364 l6,12 13,2 -9,9 2,13 -12,-6 -12,6 2,-13 -9,-9 13,-2 z" fill="#FFF3C4" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/></g>${CHIN()}`,
  top:`${RCOL('#FFFFFF')}`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#4A5880"/><rect x="-27" y="15" width="54" height="11" fill="#E7BE5E"/><path d="M-27,15 H27 M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 8) 팩트체크·"진짜일까?" — 사냥모자 + 낙타색 코트(어깨 망토·벨트) + 돋보기 목걸이
 detective:{bag:false,
  head:`${TILT(5,`${SH('M138,126 Q200,114 262,126 Q256,148 200,150 Q144,148 138,126 Z',5,.2)}
   ${G('dc','M112,128 C114,76 152,52 200,52 C248,52 286,76 288,128 Q200,114 112,128 Z','#C9A77C','<path d="M200,52 V126 M160,62 Q146,94 144,124 M240,62 Q254,94 256,124" stroke="#B4925F" stroke-width="3" fill="none"/><path d="M112,86 H288 M112,106 H288" stroke="#D8BC94" stroke-width="3"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',OW,false)}
   ${G('db','M138,124 Q200,112 262,124 Q256,146 200,148 Q144,146 138,124 Z','#B9966A','<path d="M150,130 Q200,120 250,130" stroke="#C9A77C" stroke-width="3.5" fill="none"/>',OW,false)}
   <circle cx="200" cy="52" r="6.5" fill="#9C7A4F" stroke="${OL}" stroke-width="3.2"/>`)}`,
  body:`${G('tcl',PL(176,356),'#D2B183','<path d="M10,392 H200" stroke="#B99257" stroke-width="16"/><path d="M76,330 Q98,384 92,440" stroke="#C7A473" stroke-width="5" fill="none"/>',OW)}
   ${G('tcr',PR(224,356),'#D2B183','<path d="M200,392 H390" stroke="#B99257" stroke-width="16"/><path d="M324,330 Q302,384 308,440" stroke="#C7A473" stroke-width="5" fill="none"/>',OW)}
   <rect x="186" y="382" width="28" height="20" rx="5" fill="none" stroke="#7A5A2A" stroke-width="4.2"/><path d="M200,392 h14" stroke="#7A5A2A" stroke-width="3.6"/>
   ${SH(`M10,262 L52,262${NK(52,182)} L186,${(NY(186)+18).toFixed(1)} Q120,356 24,348 L10,348 Z`,5,.16)}${SH(`M390,262 L348,262${NK(348,218)} L214,${(NY(214)+18).toFixed(1)} Q280,356 376,348 L390,348 Z`,5,.16)}
   ${G('cpl',`M10,230 L52,262${NK(52,182)} L186,${(NY(186)+18).toFixed(1)} Q120,352 24,344 L10,344 Z`,'#BE9A69','<path d="M24,338 Q120,346 186,330" stroke="#A9864F" stroke-width="7" fill="none"/>',OW)}
   ${G('cpr',`M390,230 L348,262${NK(348,218)} L214,${(NY(214)+18).toFixed(1)} Q280,352 376,344 L390,344 Z`,'#BE9A69','<path d="M376,338 Q280,346 214,330" stroke="#A9864F" stroke-width="7" fill="none"/>',OW)}
   <g fill="#8C6A38" stroke="${OL}" stroke-width="2.2"><circle cx="188" cy="368" r="4"/><circle cx="212" cy="368" r="4"/><circle cx="188" cy="414" r="4"/><circle cx="212" cy="414" r="4"/></g>${CHIN()}`,
  top:`<g data-sw="2,2.1,200,322,0.4"><path d="M184,${(NY(184)+3).toFixed(1)} Q192,344 200,354 Q208,344 216,${(NY(216)+3).toFixed(1)}" fill="none" stroke="#7A5A2A" stroke-width="2.6"/>
    ${SH('M200,372 m-16,0 a16,16 0 1,0 32,0 a16,16 0 1,0 -32,0',3,.16)}
    <circle cx="200" cy="370" r="16" fill="#DDF3FA" fill-opacity=".85" stroke="${OL}" stroke-width="7.5"/><circle cx="200" cy="370" r="16" fill="none" stroke="#9C7A4F" stroke-width="3"/>
    <path d="M200,354 v-1" stroke="${OL}" stroke-width="5" stroke-linecap="round"/><path d="M200,387 L200,404" stroke="${OL}" stroke-width="9" stroke-linecap="round"/><path d="M200,387 L200,404" stroke="#8C5A32" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M191,363 Q195,358 203,358" stroke="#fff" stroke-width="3.4" stroke-linecap="round" fill="none"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#D2B183"/><rect x="-27" y="14" width="54" height="9" fill="#B99257"/><path d="M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 9) 해외여행·환율·면세 — 밀짚모자(민트 리본·선글라스) + 하늘색 꽃무늬 셔츠(열린 깃)
 travel:{bag:false,
  head:`${TILT(-5,`${SH('M70,124 Q200,100 330,124 Q336,140 312,146 Q200,126 88,146 Q64,140 70,124 Z',7,.2)}
   ${G('bb','M68,124 Q200,98 332,124 Q338,140 314,147 Q200,126 86,147 Q62,140 68,124 Z','#F3E2B2','<path d="M84,132 Q200,110 316,132 M96,140 Q200,120 304,140" stroke="#E2CB8E" stroke-width="2.6" fill="none"/>',OW,false)}
   ${G('bc','M126,122 C128,80 158,62 200,62 C242,62 272,80 274,122 Q200,108 126,122 Z','#EED9A0','<path d="M140,110 Q146,84 170,70 M200,64 V110 M260,110 Q254,84 230,70" stroke="#DCC27F" stroke-width="2.8" fill="none"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',OW,false)}
   ${G('br','M128,106 Q200,94 272,106 L274,122 Q200,108 126,122 Z','#7FC8B2','<path d="M132,110 Q200,98 270,110" stroke="#A5DCCB" stroke-width="3" fill="none"/>',3.6,false)}
   <g transform="translate(200,86)"><path d="M-38,-5 h28 a5,5 0 0 1 5,5 v3 a13,13 0 0 1 -13,13 h-8 a13,13 0 0 1 -13,-13 v-3 a5,5 0 0 1 5,-5 z" fill="#3E4652" stroke="${OL}" stroke-width="3"/><path d="M10,-5 h28 a5,5 0 0 1 5,5 v3 a13,13 0 0 1 -13,13 h-8 a13,13 0 0 1 -13,-13 v-3 a5,5 0 0 1 5,-5 z" fill="#3E4652" stroke="${OL}" stroke-width="3"/>
    <path d="M-5,0 Q0,-4 5,0" stroke="${OL}" stroke-width="3" fill="none"/><path d="M-33,0 l8,8 M15,0 l8,8" stroke="#8FA3B8" stroke-width="2.6" stroke-linecap="round"/></g>`)}`,
  body:`<defs><pattern id="dFlo" width="64" height="60" patternUnits="userSpaceOnUse"><g transform="translate(16,16)"><g fill="#FFFDF8"><circle cx="0" cy="-6" r="5"/><circle cx="6" cy="-2" r="5"/><circle cx="4" cy="5" r="5"/><circle cx="-4" cy="5" r="5"/><circle cx="-6" cy="-2" r="5"/></g><circle r="2.6" fill="#F2C46B"/></g>
    <g transform="translate(48,44)"><g fill="#FBDDE2"><circle cx="0" cy="-5" r="4"/><circle cx="5" cy="-1.5" r="4"/><circle cx="3" cy="4" r="4"/><circle cx="-3" cy="4" r="4"/><circle cx="-5" cy="-1.5" r="4"/></g><circle r="2.2" fill="#FFFDF8"/></g></pattern></defs>
   ${G('shl',PL(174,350),'#A9D4EC','<rect x="-70" y="-70" width="540" height="560" fill="url(#dFlo)"/>',OW)}
   ${G('shr',PR(226,350),'#A9D4EC','<rect x="-70" y="-70" width="540" height="560" fill="url(#dFlo)"/>',OW)}
   <path d="M200,350 V440" stroke="${OL}" stroke-width="3.6"/><g fill="#FFFDF8" stroke="${OL}" stroke-width="2.2"><circle cx="207" cy="368" r="3.6"/><circle cx="207" cy="394" r="3.6"/></g>${CHIN()}`,
  top:`${G('acl',`M174,${NY(174).toFixed(1)} L200,350 L178,344 L136,${(NY(136)+10).toFixed(1)} Z`,'#C3E3F3','',3.6,false)}${G('acr',`M226,${NY(226).toFixed(1)} L200,350 L222,344 L264,${(NY(264)+10).toFixed(1)} Z`,'#C3E3F3','',3.6,false)}`,
  glove:`<rect x="-27" y="-30" width="54" height="42" fill="#A9D4EC"/><rect x="-27" y="-30" width="54" height="42" fill="url(#dFlo)"/><path d="M-27,12 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 10) 월급·연봉·고용·직장 — 하늘색 셔츠(소매 걷음·주머니 펜) + 민트 끈 사원증
 office:{bag:false,
  body:`${G('osh',FULL,'#D3E4F5','<path d="M200,322 V440" stroke="#BCD1EA" stroke-width="8"/><path d="M64,322 Q86,380 80,440 M336,322 Q314,380 320,440" stroke="#C3D7EE" stroke-width="4" fill="none"/>',OW)}
   <path d="M200,324 V440" stroke="${OL}" stroke-width="2.6"/><g fill="#FFFDF8" stroke="${OL}" stroke-width="2"><circle cx="206" cy="344" r="3.2"/><circle cx="206" cy="370" r="3.2"/><circle cx="206" cy="396" r="3.2"/></g>
   <rect x="254" y="324" width="8" height="26" rx="3" fill="#3FA88F" stroke="${OL}" stroke-width="2.4"/>
   ${G('opk','M240,336 h36 v26 a6,6 0 0 1 -6,6 h-24 a6,6 0 0 1 -6,-6 z','#C6DAF0','',3,false)}${CHIN()}`,
  top:`${RCOL('#E3EEF9')}
   <g data-sw="1.6,2.0,200,320,0.6"><path d="M168,${(NY(168)+4).toFixed(1)} Q176,344 192,356 M232,${(NY(232)+4).toFixed(1)} Q224,344 208,356" fill="none" stroke="${OL}" stroke-width="7" stroke-linecap="round"/><path d="M168,${(NY(168)+4).toFixed(1)} Q176,344 192,356 M232,${(NY(232)+4).toFixed(1)} Q224,344 208,356" fill="none" stroke="#3FA88F" stroke-width="3.4" stroke-linecap="round"/>
    ${SH('M180,358 h40 v48 h-40 z',4,.14)}${G('bdg','M184,356 h32 a6,6 0 0 1 6,6 v40 a6,6 0 0 1 -6,6 h-32 a6,6 0 0 1 -6,-6 v-40 a6,6 0 0 1 6,-6 z','#FFFDF8','<rect x="178" y="356" width="44" height="8" fill="#3FA88F"/><circle cx="200" cy="378" r="7" fill="#BFE6DA"/><path d="M189,394 h22 M192,401 h16" stroke="#C9D0D6" stroke-width="3" stroke-linecap="round"/>',3.2,false)}</g>`,
  glove:`<rect x="-27" y="-30" width="54" height="42" fill="#D3E4F5"/><rect x="-27" y="8" width="54" height="13" rx="4" fill="#E6F0FA"/><path d="M-27,8 H27 M-27,21 H27" stroke="${OL}" stroke-width="2.8"/>`}
};


// 주제 → 옷 추천(편을 만들 때 고르는 기준). 맞는 게 없으면 ''(기본: 민트 크로스백)
const TOPIC={news:'금리·환율·경제 지표·경제 해설',tax:'연말정산·세금·연금·건강보험료·지원금 신청',export:'수출입·반도체·조선·자동차·산업 통계',
  winter:'난방비·전기·가스요금·겨울 물가·한파',kimjang:'김장·장바구니 물가·농수산물·먹거리 수출',
  science:'과학·기술·우주·날씨·AI 원리',trivia:'상식·역사·지리·숫자 퀴즈 일반·교육·수능·입시·학자금',detective:'팩트체크·"진짜일까?"·오해 바로잡기·반전 숫자',
  travel:'해외여행·환율·면세·항공·관광',office:'월급·연봉·고용·직장인·최저임금'};
let UID=0;
function apply(sl,name){
  const o=OUTFIT[name]; if(!o) return false;
  const sfx='_'+(++UID), fix=s=>(s||'').replace(/\b(dBodyM|dHeadC|dRound|dDome|dSoft|dDot|dChk|dHib|dLeaf|dFlo|dG[A-Za-z0-9]+)\b/g,m=>m+sfx);
  sl.body.innerHTML=fix(DEFS+`<g class="oBody" mask="url(#dBodyM)">${o.body||''}</g>`);
  sl.top.innerHTML=fix(`<g class="oTop">${o.top||''}</g>`);
  sl.head.innerHTML=fix(`<g class="oFace">${o.face||''}</g><g class="oHead">${o.head||''}</g>`);
  (sl.gloves||[]).forEach(g=>g.innerHTML=fix(o.glove||''));
  if(sl.hands){if(sl.hands.R)sl.hands.R.innerHTML=fix(o.handR||'');if(sl.hands.L)sl.hands.L.innerHTML=fix(o.handL||'');}
  if(o.bag===false&&sl.bag) sl.bag.setAttribute('display','none');
  sl.body.ownerSVGElement&&(sl.body.ownerSVGElement.__outfit={name,o,sl});
  return true;
}
function anim(root,st){
  const t=st.t||0,hop=st.hop||0,sq=st.squash||0;
  root.querySelectorAll('.omkL,.omkR').forEach(c=>{const k=c.classList.contains('omkL')?st.ckL:st.ckR;if(!k)return;c.setAttribute('cx',k[0]);c.setAttribute('cy',k[1]);c.setAttribute('r',k[2]>0?k[2]+4:0);});
  root.querySelectorAll('[data-sw]').forEach(el=>{const [a,f,px,py,ph]=el.dataset.sw.split(',').map(Number);
    el.setAttribute('transform',`rotate(${(a*Math.sin(t*f+(ph||0))+hop*.05*Math.sign(a)).toFixed(2)} ${px} ${py})`);});
  root.querySelectorAll('.hold').forEach(el=>{const R=!!el.closest('#dArmR,.armR');const a=R?st.armRdeg:st.armLdeg;if(a==null)return;el.setAttribute('transform',`rotate(${(-a).toFixed(2)})`);});
  root.querySelectorAll('[data-bob]').forEach(el=>{const a=+el.dataset.bob;el.setAttribute('transform',`translate(0 ${(a*Math.sin(t*3.1)+hop*.09+sq*6).toFixed(2)})`);});
}
// 렌더 전 점검(도형의 자기 좌표 기준 — 기울기·점프와 상관없이 같은 판정)
const EYE=[[117,188,179,240],[221,188,283,240]], MOUTH=[180,226,220,262];
const hit=(b,r)=>b.x<r[2]&&b.x+b.width>r[0]&&b.y<r[3]&&b.y+b.height>r[1];
function check(root){
  const svg=root.ownerSVGElement||root, info=svg.__outfit, out=[];
  if(!info) return out;
  const {name,o,sl}=info;
  // 보이는 도형만: 숨은 정의·그림자(흐림 필터)·옅은 것·자르기 그룹 안의 무늬는 빼고(그 그룹은 같은 모양의 외곽선 .oo 로 본다)
  const solid=g=>[...g.querySelectorAll('path,rect,circle,ellipse,polygon')].filter(e=>{
    if(e.closest('defs,clipPath,mask,pattern')) return false;
    if(e.getAttribute('filter')) return false;
    for(let p=e.parentElement;p&&p!==g;p=p.parentElement) if(p.getAttribute('clip-path')) return false;
    return +(e.getAttribute('opacity')??1)>.3;});
  // 눈·코·입 상자 안의 점들이 실제 도형(면·선) 안에 들어가는지 — 둥근 목선처럼 상자만 큰 모양은 통과
  const pts=r=>{const a=[];for(let i=0;i<=6;i++)for(let j=0;j<=6;j++)a.push([r[0]+(r[2]-r[0])*i/6,r[1]+(r[3]-r[1])*j/6]);return a;};
  const ZONES=[['눈',pts(EYE[0])],['눈',pts(EYE[1])],['코·입',pts(MOUTH)]];
  // 하얀 주둥이(턱) 안쪽: 몸·목 옷이 여기를 덮으면 옷 윗단이 얼굴을 가로지르는 '선'처럼 보인다(2026-11-04 사용자 지적)
  const JAW=[];for(let x=90;x<=310;x+=20){const yb=260+52*Math.sqrt(Math.max(0,1-((x-200)/124)**2));for(const f of [.35,.6])JAW.push([x,262+(yb-262)*f]);}
  for(const [lab,g,ref] of [['머리',sl.head.querySelector('.oHead'),sl.head],['몸',sl.body.querySelector('.oBody'),sl.body],['목',sl.top.querySelector('.oTop'),sl.top]]){
    const zones=lab==='머리'?ZONES:[...ZONES,['턱(얼굴 아래쪽)',JAW]];
    if(!g) continue; const R=ref.getCTM(); if(!R) continue;
    let hitMsg=null;
    for(const e of solid(g)){const M=e.getCTM();if(!M)continue;const toE=M.inverse().multiply(R);
      const filled=e.classList.contains('oo')||(e.getAttribute('fill')||'')!=='none';
      for(const [zl,ps] of zones){if(ps.some(([x,y])=>{const q=new DOMPoint(x,y).matrixTransform(toE);return (filled&&e.isPointInFill(q))||e.isPointInStroke(q);})){hitMsg=`${name}: ${lab} 옷이 ${zl}을 가림 (${e.tagName}${e.getAttribute('class')?'.'+e.getAttribute('class'):''})`;break;}}
      if(hitMsg) break;}
    if(hitMsg) out.push(hitMsg);
  }
  if(o.glove){const n=(sl.gloves||[]).filter(g=>g.childElementCount>0).length;if(n!==2) out.push(`${name}: 장갑·소매가 두 팔 중 ${n}개에만 있음`);}
  if(o.bag===false&&sl.bag&&sl.bag.getAttribute('display')!=='none') out.push(`${name}: 크로스백이 숨겨지지 않음`);
  return out;
}
window.DoriOutfit={list:()=>Object.keys(OUTFIT),topics:()=>({...TOPIC}),apply,anim,check};
})();