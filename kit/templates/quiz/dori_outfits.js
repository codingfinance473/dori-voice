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

// ---- 옷장 3판(2026-11-04): 귀엽게, 유치하지 않게 ----
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

const OUTFIT={
 // 1) 경제 뉴스·해설 — 앞이 트인 짧은 남색 재킷 + 둥근 흰 깃 + 민트 넥타이 + 가슴 행커치프
 news:{bag:false,
  body:`${G('nbl',OPEN_L(166,126,404),'#5B6E9A',EDGE_L(166,126,404,'#7184B0',20)+'<path d="M64,330 Q86,370 82,404" stroke="#52648E" stroke-width="4" fill="none"/>',OW)}
   ${G('nbr',OPEN_R(166,126,404),'#5B6E9A',EDGE_R(166,126,404,'#7184B0',20)+'<path d="M336,330 Q314,370 318,404" stroke="#52648E" stroke-width="4" fill="none"/>',OW)}
   <path d="M70,350 h28" stroke="#4A5B84" stroke-width="3.5" stroke-linecap="round"/><path d="M76,349 q4,-12 9,-12 q5,0 9,12 z" fill="#A8DCCB" stroke="${OL}" stroke-width="2.6" stroke-linejoin="round"/>${CHIN()}`,
  top:`${RCOL('#FFFFFF')}
   <g data-sw="1.4,2.2,200,326,0">${SH('M194,334 L206,334 L210,372 Q200,384 190,372 Z',4,.12)}
    ${G('tie','M194,333 L206,333 L210,370 Q200,384 190,370 Z','#3FA88F','<path d="M186,352 L214,342" stroke="#6CC2AC" stroke-width="4"/>',3.4,false)}
    <rect x="193" y="320" width="14" height="14" rx="4.5" fill="#2E9C83" stroke="${OL}" stroke-width="3.4"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="54" fill="#5B6E9A"/><rect x="-27" y="22" width="54" height="9" fill="#FFFDF8"/><path d="M-27,22 H27 M-27,31 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 2) 세금·연말정산·연금 — 동그란 안경 + 짧은 오트밀 니트 조끼 + 남색 나비넥타이
 tax:{bag:false,
  body:`${G('tvl',`M10,230 L52,262${NK(52,182)} L200,352 L200,390 Q120,400 10,378 Z`,'#E8D7BC','<path d="M10,372 Q120,394 200,384" stroke="#D6BF9B" stroke-width="16" fill="none"/><path d="M112,318 q8,11 0,22 q-8,11 0,22 q8,11 0,22" stroke="#DCC7A6" stroke-width="4" fill="none"/>',OW)}
   ${G('tvr',`M390,230 L348,262${NK(348,218)} L200,352 L200,390 Q280,400 390,378 Z`,'#E8D7BC','<path d="M390,372 Q280,394 200,384" stroke="#D6BF9B" stroke-width="16" fill="none"/><path d="M288,318 q-8,11 0,22 q8,11 0,22 q-8,11 0,22" stroke="#DCC7A6" stroke-width="4" fill="none"/>',OW)}${CHIN()}`,
  top:`${RCOL('#FFFFFF')}
   <g data-sw="1.2,2.0,200,334,1"><path d="M200,334 Q186,322 179,328 Q176,336 179,343 Q186,349 200,338 Z" fill="#5B6E9A" stroke="${OL}" stroke-width="3.2" stroke-linejoin="round"/>
    <path d="M200,334 Q214,322 221,328 Q224,336 221,343 Q214,349 200,338 Z" fill="#5B6E9A" stroke="${OL}" stroke-width="3.2" stroke-linejoin="round"/>
    <rect x="195" y="330" width="10" height="10" rx="3.5" fill="#4A5B84" stroke="${OL}" stroke-width="3"/></g>`,
  face:`<g fill="#fff" fill-opacity=".1" stroke="#8A6B4E" stroke-width="3.4"><circle cx="148" cy="214" r="28"/><circle cx="252" cy="214" r="28"/></g>
   <path d="M176,211 Q200,201 224,211" fill="none" stroke="#8A6B4E" stroke-width="3.4" stroke-linecap="round"/>
   <path d="M120,208 L94,200 M280,208 L306,200" stroke="#8A6B4E" stroke-width="3.4" stroke-linecap="round"/>
   <path d="M131,199 Q138,192 146,191 M235,199 Q242,192 250,191" stroke="#fff" stroke-width="3.5" stroke-linecap="round" opacity=".8" fill="none"/>`},

 // 3) 수출·산업·무역 — 작은 노란 안전모(살짝 기울임) + 데님 멜빵바지
 export:{bag:false,
  head:`${TILT(-9,`${SH('M132,98 Q200,88 268,98 Q270,108 258,110 Q200,102 142,110 Q130,108 132,98 Z',5,.18)}
   ${G('hh','M146,98 C148,62 172,46 200,46 C228,46 252,62 254,98 Z','#F4D47A','<path d="M200,46 V98" stroke="#FAE6A8" stroke-width="12"/><path d="M166,72 Q172,58 186,54" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none" opacity=".7"/>',OW,false)}
   ${G('hb','M130,98 Q200,88 270,98 Q272,108 260,110 Q200,102 140,110 Q128,108 130,98 Z','#E9C25C','',OW,false)}`)}`,
  body:`${G('ovp','M10,368 Q200,358 390,368 L390,440 L10,440 Z','#8DA8CC','<path d="M10,378 Q200,368 390,378" stroke="#B4C8E2" stroke-width="2.6" stroke-dasharray="7 6" fill="none"/><path d="M200,368 V440" stroke="#7D97BC" stroke-width="3"/>',OW)}
   ${G('ovb','M154,334 Q154,324 164,324 L236,324 Q246,324 246,334 L246,372 L154,372 Z','#8DA8CC','<rect x="160" y="330" width="80" height="38" rx="6" fill="none" stroke="#B4C8E2" stroke-width="2.4" stroke-dasharray="6 5"/><rect x="184" y="338" width="32" height="20" rx="5" fill="none" stroke="#7D97BC" stroke-width="3"/>',OW,false)}
   <path d="M160,328 Q122,${NY(122)+4} 86,${NY(86)+6} M240,328 Q278,${NY(278)+4} 314,${NY(314)+6}" stroke="${OL}" stroke-width="13" stroke-linecap="round" fill="none"/>
   <path d="M160,328 Q122,${NY(122)+4} 86,${NY(86)+6} M240,328 Q278,${NY(278)+4} 314,${NY(314)+6}" stroke="#8DA8CC" stroke-width="7" stroke-linecap="round" fill="none"/>
   <circle cx="161" cy="330" r="5" fill="#F4D47A" stroke="${OL}" stroke-width="2.6"/><circle cx="239" cy="330" r="5" fill="#F4D47A" stroke="${OL}" stroke-width="2.6"/>${CHIN()}`},

 // 4) 겨울 생활비 — 폭신한 귀마개 + 두툼한 로즈 목도리
 winter:{bag:false,
  head:`<path d="M112,96 Q200,64 288,96" fill="none" stroke="${OL}" stroke-width="14" stroke-linecap="round"/><path d="M112,96 Q200,64 288,96" fill="none" stroke="#E3A1AA" stroke-width="8" stroke-linecap="round"/>
   ${[[118,116],[282,116]].map(([x,y])=>`${SH(`M${x},${y} m-30,0 a30,30 0 1,0 60,0 a30,30 0 1,0 -60,0`,5,.16)}
   <path d="M${x-30},${y} a30,30 0 1,0 60,0 a30,30 0 1,0 -60,0" fill="#FBF3E6" stroke="${OL}" stroke-width="${OW}"/>
   <path d="M${x-22},${y-6} q4,-2 6,2 M${x-6},${y-22} q4,-2 6,2 M${x+12},${y-14} q4,-2 6,2 M${x-14},${y+12} q4,-2 6,2 M${x+8},${y+10} q4,-2 6,2" stroke="#E9DCC6" stroke-width="3" fill="none" stroke-linecap="round"/>
   <path d="M${x-14},${y-18} q8,-6 18,-4" stroke="#fff" stroke-width="4" stroke-linecap="round" fill="none"/>`).join('')}`,
  top:`<g mask="url(#dBodyM)">${SH(`M50,254${NK(50,350,-4)} L352,${(NY(350)+30).toFixed(1)}${NK(350,50,30)} Z`,6,.18)}
   ${G('scf',`M46,250${NK(48,352,-8)} L354,${(NY(352)+26).toFixed(1)}${NK(352,48,26)} Z`,'#E3A1AA',`<path d="M60,${NY(60)+4}${NK(60,340,4)}" stroke="#ECB7BE" stroke-width="5" fill="none"/><path d="M60,${NY(60)+16}${NK(60,340,16)}" stroke="#D88E98" stroke-width="3" fill="none" opacity=".6"/>`,OW)}</g>
   <g data-sw="2.2,2.3,252,330,0">${SH('M238,326 L272,324 L280,392 L246,396 Z',5,.14)}
    ${G('stl','M236,324 L272,322 L280,390 L244,394 Z','#E3A1AA','<path d="M232,350 L284,346 M234,372 L286,368" stroke="#D88E98" stroke-width="3" opacity=".6"/>',OW,false)}
    <path d="M249,396 l-1,10 M257,395 l0,11 M265,394 l1,11 M273,393 l1,10" stroke="#D88E98" stroke-width="4" stroke-linecap="round"/></g>`},

 // 5) 장보기·먹거리·김장 — 머리에 맞춘 로즈 두건(작은 매듭) + 크림색 허리 앞치마(배추 자수)
 kimjang:{bag:false,
  head:`<defs><pattern id="dDot" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)"><circle cx="6" cy="6" r="2.6" fill="#FFF4F2"/><circle cx="17" cy="17" r="2.6" fill="#FFF4F2"/></pattern></defs>
   ${FIT(`<path d="M0,0 H400 V152 Q200,116 0,152 Z" fill="#E59BA4"/><path d="M0,0 H400 V152 Q200,116 0,152 Z" fill="url(#dDot)"/><path d="M0,0 H400 V152 Q200,116 0,152 Z" fill="url(#dDome)"/>
    <path d="M30,154 Q200,118 370,154" stroke="#D3848E" stroke-width="10" fill="none"/>
    ${SH('M30,154 Q200,118 370,154 L370,162 Q200,126 30,162 Z',3,.2)}<path d="M30,152 Q200,116 370,152" stroke="${OL}" stroke-width="${OW}" fill="none"/>`)}
   <g transform="translate(318,142)"><g data-sw="5,2.8,0,0,0"><path d="M0,0 L24,-12 Q30,0 20,8 Z" fill="#E59BA4" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/></g>
    <g data-sw="-6,2.4,0,0,1.1"><path d="M0,0 L20,18 Q10,26 2,16 Z" fill="#D3848E" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/></g>
    <circle r="8" fill="#D3848E" stroke="${OL}" stroke-width="3.6"/></g>`,
  body:`${G('apr','M66,352 Q200,342 334,352 L342,440 L58,440 Z','#FBF5EA','<path d="M80,372 Q90,410 84,440 M320,372 Q310,410 316,440" stroke="#EFE5D3" stroke-width="5" fill="none"/>',OW)}
   <path d="M66,352 Q200,342 334,352" stroke="${OL}" stroke-width="15" fill="none" stroke-linecap="round"/><path d="M66,352 Q200,342 334,352" stroke="#A9C3A0" stroke-width="9" fill="none" stroke-linecap="round"/>
   ${G('apk','M170,368 h60 a8,8 0 0 1 8,8 v20 a8,8 0 0 1 -8,8 h-60 a8,8 0 0 1 -8,-8 v-20 a8,8 0 0 1 8,-8 z','#F3EAD8','<path d="M162,375 H238" stroke="#A9C3A0" stroke-width="4"/>',3.4,false)}
   <g transform="translate(200,382) scale(.62)"><path d="M0,30 C-16,26 -18,6 -6,-4 C-2,6 0,14 0,30 Z" fill="#A9C3A0" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/>
    <path d="M0,30 C16,26 18,6 6,-4 C2,6 0,14 0,30 Z" fill="#93B58A" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/><path d="M0,30 C-7,22 -6,8 0,0 C6,8 7,22 0,30 Z" fill="#F4F7E2" stroke="${OL}" stroke-width="3.6" stroke-linejoin="round"/></g>
   <g data-sw="5,2.5,76,352,0.5"><path d="M76,352 q-16,-10 -20,0 q4,10 20,0 M76,352 q-10,12 -6,22 M76,352 q-2,14 6,22" stroke="${OL}" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M76,352 q-16,-10 -20,0 q4,10 20,0 M76,352 q-10,12 -6,22 M76,352 q-2,14 6,22" stroke="#A9C3A0" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>${CHIN()}`},

 // 6) 과학·기술·우주·AI — 이마 위 작은 보안경 + 앞이 트인 흰 가운(민트 펜 하나)
 science:{bag:false,
  head:`${FIT(`<path d="M30,150 Q200,124 370,150" stroke="${OL}" stroke-width="12" fill="none"/><path d="M30,150 Q200,124 370,150" stroke="#8FB9B4" stroke-width="6" fill="none"/>`)}
   ${SH('M146,128 h48 v28 h-48 z M206,128 h48 v28 h-48 z',4,.16)}
   ${G('gl','M152,126 h36 a12,12 0 0 1 12,12 v6 a12,12 0 0 1 -12,12 h-36 a12,12 0 0 1 -12,-12 v-6 a12,12 0 0 1 12,-12 z','#CFEEF3','<path d="M150,134 L170,154 M164,128 L186,152" stroke="#fff" stroke-width="4" opacity=".75"/>',3.6,false)}
   ${G('gr','M212,126 h36 a12,12 0 0 1 12,12 v6 a12,12 0 0 1 -12,12 h-36 a12,12 0 0 1 -12,-12 v-6 a12,12 0 0 1 12,-12 z','#CFEEF3','<path d="M210,134 L230,154 M224,128 L246,152" stroke="#fff" stroke-width="4" opacity=".75"/>',3.6,false)}
   <path d="M196,140 Q200,136 204,140" stroke="${OL}" stroke-width="5" fill="none" stroke-linecap="round"/>`,
  body:`${G('lcl',OPEN_L(168,118),'#F4F7FA',EDGE_L(168,118,440,'#E3EAF0',20)+'<path d="M66,330 Q92,390 86,440" stroke="#E3EAF0" stroke-width="5" fill="none"/>',OW)}
   ${G('lcr',OPEN_R(168,118),'#F4F7FA',EDGE_R(168,118,440,'#E3EAF0',20)+'<path d="M334,330 Q308,390 314,440" stroke="#E3EAF0" stroke-width="5" fill="none"/>',OW)}
   <rect x="96" y="332" width="9" height="30" rx="3" fill="#7CC9B5" stroke="${OL}" stroke-width="2.6"/>
   ${G('lpk','M84,344 h42 v26 a7,7 0 0 1 -7,7 h-28 a7,7 0 0 1 -7,-7 z','#EAF0F4','',3.2,false)}${CHIN()}`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#F4F7FA"/><path d="M-27,22 H27" stroke="#E3EAF0" stroke-width="6"/><path d="M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 7) 상식·교육·수능·입시 — 졸업식 세트(2026-11-04 사용자 선택 A — 카디건은 구식, 교복은 학사모와 안 맞음)를 3판 모양으로:
 //    작은 학사모(살짝 기울임, 술이 흔들림) + 앞이 트인 남색 졸업 가운 + 앞섶을 따라 내려오는 금색 숄 + 작은 별 배지 + 둥근 흰 깃
 trivia:{bag:false,
  head:`${TILT(-8,`${SH('M152,98 Q200,90 248,98 L248,104 Q200,96 152,104 Z',4,.2)}
   ${G('mc','M152,98 C154,76 174,66 200,66 C226,66 246,76 248,98 Q200,90 152,98 Z','#4E5C86','<rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',OW,false)}
   <path d="M130,62 L130,68 L200,88 L270,68 L270,62" fill="#3F4C74" stroke="${OL}" stroke-width="${OW}" stroke-linejoin="round"/>
   ${G('mb','M200,42 L270,62 L200,82 L130,62 Z','#5A6996','<path d="M160,62 L200,51 L240,62" stroke="#6E7DAA" stroke-width="4" fill="none"/>',OW,false)}
   <g data-sw="4,2.3,256,66,0"><path d="M200,62 Q236,62 256,66 L259,98" fill="none" stroke="#E7BE5E" stroke-width="4" stroke-linecap="round"/>
    <path d="M253,96 h12 l3,16 h-18 z" fill="#E7BE5E" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/></g>
   <circle cx="200" cy="62" r="5" fill="#E7BE5E" stroke="${OL}" stroke-width="3"/>`)}`,
  body:`${G('gwl',OPEN_L(166,124),'#4A5880',EDGE_L(166,124,440,'#E7BE5E',30)+EDGE_L(166,124,440,'#D4A84A',3)+'<path d="M62,330 Q86,390 80,440" stroke="#425078" stroke-width="5" fill="none"/>',OW)}
   ${G('gwr',OPEN_R(166,124),'#4A5880',EDGE_R(166,124,440,'#E7BE5E',30)+EDGE_R(166,124,440,'#D4A84A',3)+'<path d="M338,330 Q314,390 320,440" stroke="#425078" stroke-width="5" fill="none"/>',OW)}
   <g data-bob="0.6">${SH('M266,346 l5,10 11,1.5 -8,7.5 2,11 -10,-5 -10,5 2,-11 -8,-7.5 11,-1.5 z',3,.16)}<path d="M264,344 l5,10 11,1.5 -8,7.5 2,11 -10,-5 -10,5 2,-11 -8,-7.5 11,-1.5 z" fill="#FFF3C4" stroke="${OL}" stroke-width="2.8" stroke-linejoin="round"/></g>${CHIN()}`,
  top:`${RCOL('#FFFFFF')}`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#4A5880"/><rect x="-27" y="16" width="54" height="10" fill="#E7BE5E"/><path d="M-27,16 H27 M-27,26 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 8) 팩트체크·"진짜일까?" — 작은 사냥모자 + 낙타색 망토 + 목에 건 작은 돋보기
 detective:{bag:false,
  head:`${TILT(7,`${SH('M164,98 Q200,92 236,98 Q232,112 200,114 Q168,112 164,98 Z',4,.2)}
   ${G('dc','M150,100 C152,64 174,48 200,48 C226,48 248,64 250,100 Q200,92 150,100 Z','#C9A77C','<path d="M200,48 V98 M176,54 Q166,74 164,98 M224,54 Q234,74 236,98" stroke="#B4925F" stroke-width="3" fill="none"/><path d="M150,70 H250 M150,84 H250" stroke="#D8BC94" stroke-width="2.5"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',OW,false)}
   ${G('db','M164,96 Q200,90 236,96 Q232,110 200,112 Q168,110 164,96 Z','#B9966A','',OW,false)}
   <circle cx="200" cy="48" r="5" fill="#9C7A4F" stroke="${OL}" stroke-width="3"/>`)}`,
  body:`${G('cpl',`M10,230 L52,262${NK(52,188)} L192,342 Q120,370 24,352 L10,352 Z`,'#C9A77C','<path d="M24,344 Q120,362 192,336" stroke="#B4925F" stroke-width="10" fill="none"/>',OW)}
   ${G('cpr',`M390,230 L348,262${NK(348,212)} L208,342 Q280,370 376,352 L390,352 Z`,'#C9A77C','<path d="M376,344 Q280,362 208,336" stroke="#B4925F" stroke-width="10" fill="none"/>',OW)}
   <g fill="#8C6A38" stroke="${OL}" stroke-width="2.2"><circle cx="182" cy="322" r="4"/><circle cx="218" cy="322" r="4"/></g>${CHIN()}`,
  top:`<g data-sw="2,2.1,200,322,0.4"><path d="M186,${(NY(186)+3).toFixed(1)} Q194,340 200,352 Q206,340 214,${(NY(214)+3).toFixed(1)}" fill="none" stroke="#7A5A2A" stroke-width="2.4"/>
    <circle cx="200" cy="368" r="13" fill="#DDF3FA" fill-opacity=".8" stroke="${OL}" stroke-width="6.5"/><circle cx="200" cy="368" r="13" fill="none" stroke="#9C7A4F" stroke-width="2.6"/>
    <path d="M200,352 v3" stroke="${OL}" stroke-width="5" stroke-linecap="round"/><path d="M200,383 L200,396" stroke="${OL}" stroke-width="8" stroke-linecap="round"/><path d="M200,383 L200,396" stroke="#8C5A32" stroke-width="4" stroke-linecap="round"/>
    <path d="M193,362 Q196,358 202,358" stroke="#fff" stroke-width="3" stroke-linecap="round" fill="none"/></g>`},

 // 9) 해외여행·환율·면세 — 작은 밀짚 보터(민트 리본) + 앞이 트인 하늘색 셔츠(작은 잎 무늬)
 travel:{bag:false,
  head:`${TILT(-8,`${SH('M116,98 Q200,86 284,98 Q286,108 274,110 Q200,100 126,110 Q114,108 116,98 Z',5,.2)}
   ${G('bc','M152,98 L156,62 Q200,54 244,62 L248,98 Z','#EED9A0','<path d="M154,72 Q200,64 246,72 M153,84 Q200,76 247,84" stroke="#DCC27F" stroke-width="2.6" fill="none"/>',OW,false)}
   ${G('br','M152,84 Q200,78 248,84 L248,96 Q200,90 152,96 Z','#7FC8B2','',3.4,false)}
   ${G('bb','M116,98 Q200,86 284,98 Q286,108 274,110 Q200,100 126,110 Q114,108 116,98 Z','#F3E2B2','<path d="M126,102 Q200,92 274,102" stroke="#E2CB8E" stroke-width="2.6" fill="none"/>',OW,false)}
   <g data-sw="5,2.6,248,90,0"><path d="M248,90 q12,4 14,16 M248,92 q6,8 4,18" stroke="${OL}" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M248,90 q12,4 14,16 M248,92 q6,8 4,18" stroke="#7FC8B2" stroke-width="4" fill="none" stroke-linecap="round"/></g>`)}`,
  body:`<defs><pattern id="dLeaf" width="56" height="56" patternUnits="userSpaceOnUse"><path d="M14,18 q8,-10 16,0 q-8,10 -16,0 z" fill="#E7F4FB"/><path d="M38,44 q8,-10 16,0 q-8,10 -16,0 z" fill="#E7F4FB" opacity=".8"/></pattern></defs>
   ${G('shl',OPEN_L(172,138),'#A9D4EC','<rect x="-70" y="-70" width="540" height="560" fill="url(#dLeaf)"/>'+EDGE_L(172,138,440,'#BEDFF1',12),OW)}
   ${G('shr',OPEN_R(172,138),'#A9D4EC','<rect x="-70" y="-70" width="540" height="560" fill="url(#dLeaf)"/>'+EDGE_R(172,138,440,'#BEDFF1',12),OW)}
   <g fill="#FFFDF8" stroke="${OL}" stroke-width="2.2"><circle cx="266" cy="356" r="3.6"/><circle cx="263" cy="382" r="3.6"/></g>${CHIN()}`,
  top:`${G('tcl',`M174,${NY(174).toFixed(1)} Q156,${(NY(156)+12).toFixed(1)} 146,${(NY(146)+22).toFixed(1)} Q166,${(NY(166)+30).toFixed(1)} 184,${(NY(184)+20).toFixed(1)} Z`,'#C3E3F3','',3.4,false)}${G('tcr',`M226,${NY(226).toFixed(1)} Q244,${(NY(244)+12).toFixed(1)} 254,${(NY(254)+22).toFixed(1)} Q234,${(NY(234)+30).toFixed(1)} 216,${(NY(216)+20).toFixed(1)} Z`,'#C3E3F3','',3.4,false)}`,
  glove:`<rect x="-27" y="-30" width="54" height="40" fill="#A9D4EC"/><path d="M-27,10 H27" stroke="${OL}" stroke-width="2.8"/>`},

 // 10) 월급·연봉·고용·직장 — 짧은 하늘색 셔츠(소매 걷음) + 민트 끈 사원증
 office:{bag:false,
  body:`${G('osh',`M10,230 L52,262${NK(52,348)} L390,230 L390,378 Q200,402 10,378 Z`,'#D3E4F5','<path d="M200,322 V400" stroke="#BCD1EA" stroke-width="8"/><path d="M64,320 Q84,360 80,390 M336,320 Q316,360 320,390" stroke="#C3D7EE" stroke-width="4" fill="none"/>',OW)}
   <g fill="#FFFDF8" stroke="${OL}" stroke-width="2"><circle cx="205" cy="344" r="3.2"/><circle cx="205" cy="368" r="3.2"/></g>
   ${G('opk','M238,340 h32 v22 a6,6 0 0 1 -6,6 h-20 a6,6 0 0 1 -6,-6 z','#C6DAF0','',3,false)}${CHIN()}`,
  top:`${RCOL('#E3EEF9')}
   <g data-sw="1.6,2.0,200,320,0.6"><path d="M172,${(NY(172)+4).toFixed(1)} Q178,340 194,352 M228,${(NY(228)+4).toFixed(1)} Q222,340 206,352" fill="none" stroke="${OL}" stroke-width="7" stroke-linecap="round"/><path d="M172,${(NY(172)+4).toFixed(1)} Q178,340 194,352 M228,${(NY(228)+4).toFixed(1)} Q222,340 206,352" fill="none" stroke="#3FA88F" stroke-width="3.4" stroke-linecap="round"/>
    ${SH('M184,354 h32 v36 h-32 z',4,.14)}${G('bdg','M188,352 h24 a6,6 0 0 1 6,6 v30 a6,6 0 0 1 -6,6 h-24 a6,6 0 0 1 -6,-6 v-30 a6,6 0 0 1 6,-6 z','#FFFDF8','<rect x="182" y="352" width="36" height="7" fill="#3FA88F"/><circle cx="200" cy="371" r="6" fill="#BFE6DA"/><path d="M191,385 h18" stroke="#C9D0D6" stroke-width="3" stroke-linecap="round"/>',3.2,false)}</g>`,
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
  const sfx='_'+(++UID), fix=s=>(s||'').replace(/\b(dBodyM|dHeadC|dRound|dDome|dSoft|dDot|dChk|dHib|dLeaf|dG[A-Za-z0-9]+)\b/g,m=>m+sfx);
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