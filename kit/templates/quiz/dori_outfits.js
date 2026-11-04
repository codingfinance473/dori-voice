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
  <radialGradient id="dRound" cx="200" cy="320" r="175" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#2A1A10" stop-opacity="0"/><stop offset=".62" stop-color="#2A1A10" stop-opacity="0"/><stop offset="1" stop-color="#2A1A10" stop-opacity=".26"/></radialGradient>
  <radialGradient id="dDome" cx="160" cy="70" r="200" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#2A1A10" stop-opacity=".22"/></radialGradient>
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

const OUTFIT={
 // 1) 경제 뉴스·해설 — 남색 재킷 + 흰 셔츠 깃 + 민트 넥타이(채널 색)
 news:{bag:false,
  body:`${G('nl',PL(176,368),'#3E5A8C','<path d="M64,310 Q90,370 84,440" stroke="#33507F" stroke-width="5" fill="none" opacity=".7"/>')}
   ${G('nr',PR(224,368),'#3E5A8C','<path d="M336,310 Q310,370 316,440" stroke="#33507F" stroke-width="5" fill="none" opacity=".7"/>')}
   ${G('lal',`M176,${NY(176)} L200,368 L182,352 L146,${NY(146)+4} Z`,'#2F4874','',4.2,false)}
   ${G('lar',`M224,${NY(224)} L200,368 L218,352 L254,${NY(254)+4} Z`,'#2F4874','',4.2,false)}
   <path d="M246,346 L274,342" stroke="${OL}" stroke-width="4" stroke-linecap="round"/><path d="M249,343 L256,330 L264,342 Z" fill="#80D0BA" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/>
   <circle cx="200" cy="386" r="5.5" fill="#25385C" stroke="${OL}" stroke-width="2.5"/>${CHIN()}`,
  top:`${COLLAR('#FFFFFF',176,338)}
   <g data-sw="1.6,2.2,200,336,0">${SH('M193,346 L207,346 L213,394 L200,408 L187,394 Z',5,.14)}
    ${G('tie','M193,346 L207,346 L214,394 L200,410 L186,394 Z','#2E9C83','<path d="M180,362 L224,344 M180,378 L224,360 M180,394 L224,376" stroke="#5FC2A9" stroke-width="5"/>',4.2,false)}
    ${G('kn','M191,332 L209,332 L206,348 L194,348 Z','#268A73','',4.2,false)}</g>`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#3E5A8C"/><rect x="-27" y="22" width="54" height="9" fill="#FFFFFF"/><path d="M-27,22 H27" stroke="${OL}" stroke-width="3"/><path d="M-27,31 H27" stroke="${OL}" stroke-width="3"/>`},

 // 2) 세금·연말정산·연금 — 초록 차양 바이저 + 동그란 안경 + 낙타색 니트 조끼 + 나비넥타이
 tax:{bag:false,
  body:`${G('vl',PL(178,352),'#C99A6B','<path d="M44,322 l24,24 -24,24 -24,-24z M92,346 l24,24 -24,24 -24,-24z M140,322 l24,24 -24,24 -24,-24z" fill="none" stroke="#E2BE93" stroke-width="3.5"/><path d="M10,390 H220" stroke="#B5845A" stroke-width="22"/><path d="M30,382 v18 M44,382 v18 M58,382 v18 M72,382 v18 M86,382 v18 M100,382 v18 M114,382 v18 M128,382 v18 M142,382 v18 M156,382 v18 M170,382 v18 M184,382 v18 M198,382 v18" stroke="#A3744C" stroke-width="2.5"/>')}
   ${G('vr',PR(222,352),'#C99A6B','<path d="M356,322 l-24,24 24,24 24,-24z M308,346 l-24,24 24,24 24,-24z M260,322 l-24,24 24,24 24,-24z" fill="none" stroke="#E2BE93" stroke-width="3.5"/><path d="M180,390 H390" stroke="#B5845A" stroke-width="22"/><path d="M202,382 v18 M216,382 v18 M230,382 v18 M244,382 v18 M258,382 v18 M272,382 v18 M286,382 v18 M300,382 v18 M314,382 v18 M328,382 v18 M342,382 v18 M356,382 v18 M370,382 v18" stroke="#A3744C" stroke-width="2.5"/>')}${CHIN()}`,
  top:`${COLLAR('#FFFFFF',178,336)}
   <g data-sw="1.2,2.0,200,338,1">${G('bwl','M200,338 L176,326 L174,352 Z','#2E6E5E','<path d="M178,330 L184,348" stroke="#3F8A77" stroke-width="3"/>',4,false)}${G('bwr','M200,338 L224,326 L226,352 Z','#2E6E5E','<path d="M222,330 L216,348" stroke="#3F8A77" stroke-width="3"/>',4,false)}
   <rect x="193" y="331" width="14" height="14" rx="4" fill="#25594B" stroke="${OL}" stroke-width="3.5"/></g>`,
  head:`${SH('M96,150 Q200,128 304,150 Q296,180 200,182 Q104,180 96,150 Z',8,.14)}
   <path d="M60,156 Q200,118 340,156" fill="none" stroke="#2F7D52" stroke-width="12" stroke-linecap="round"/>
   <path d="M60,156 Q200,118 340,156" fill="none" stroke="#3FA36B" stroke-width="6" stroke-linecap="round"/>
   ${G('bill','M96,150 Q200,126 304,150 Q298,182 200,184 Q102,182 96,150 Z','#3FA36B','<path d="M106,156 Q200,138 294,156" stroke="#9EE0B8" stroke-width="5" fill="none" opacity=".8"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',4.4,false).replace('fill="#3FA36B"/>','fill="#3FA36B" opacity=".86"/>')}`,
  face:`<g fill="#fff" fill-opacity=".14" stroke="#5A4636" stroke-width="4.5"><circle cx="148" cy="214" r="31"/><circle cx="252" cy="214" r="31"/></g>
   <path d="M179,212 Q200,200 221,212" fill="none" stroke="#5A4636" stroke-width="4.5" stroke-linecap="round"/>
   <path d="M117,208 L84,198 M283,208 L316,198" stroke="#5A4636" stroke-width="4.5" stroke-linecap="round"/>
   <path d="M128,196 Q136,188 146,186 M232,196 Q240,188 250,186" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".75" fill="none"/>`,},

 // 3) 수출·산업·무역 — 노란 안전모 + 주황 형광 조끼(반사띠)
 export:{bag:false,
  body:`${G('hvl',`M10,230 L52,262${NK(52,190)} L194,440 L10,440 Z`,'#FF8A2A','<path d="M10,350 H200" stroke="#D9E2E8" stroke-width="16"/><path d="M10,345 H200" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M10,384 H200" stroke="#D9E2E8" stroke-width="16"/><path d="M10,379 H200" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M120,300 V440" stroke="#E87420" stroke-width="3" stroke-dasharray="8 8" opacity=".7"/>')}
   ${G('hvr',`M390,230 L348,262${NK(348,210)} L206,440 L390,440 Z`,'#FF8A2A','<path d="M200,350 H390" stroke="#D9E2E8" stroke-width="16"/><path d="M200,345 H390" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M200,384 H390" stroke="#D9E2E8" stroke-width="16"/><path d="M200,379 H390" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M280,300 V440" stroke="#E87420" stroke-width="3" stroke-dasharray="8 8" opacity=".7"/>')}
   <rect x="240" y="318" width="28" height="22" rx="4" fill="#FFB36B" stroke="${OL}" stroke-width="3.5"/><path d="M246,324 H262 M246,331 H258" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>${CHIN()}`,
  head:`${SH('M48,150 Q200,126 352,150 Q350,168 336,172 Q200,150 64,172 Q50,168 48,150 Z',9,.2)}
   ${G('dome','M76,152 C80,96 134,62 200,62 C266,62 320,96 324,152 Z','#FFC93C','<path d="M184,60 L184,152 M216,60 L216,152" stroke="#E5A923" stroke-width="5"/><path d="M200,60 V152" stroke="#FFE07A" stroke-width="16"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/><path d="M110,110 Q130,82 168,72" stroke="#FFF3C4" stroke-width="9" stroke-linecap="round" fill="none"/>',5.2,false)}
   ${G('brim','M48,150 Q200,126 352,150 Q350,168 336,172 Q200,150 64,172 Q50,168 48,150 Z','#F2B627','<path d="M60,158 Q200,136 340,158" stroke="#FFD866" stroke-width="5" fill="none"/>',5,false)}`},

 // 4) 겨울 생활비(난방비·전기요금·겨울 물가) — 니트 비니(방울) + 줄무늬 목도리 + 벙어리장갑
 winter:{bag:false,
  top:`<g mask="url(#dBodyM)">${SH(`M50,254${NK(50,350,-4)} L352,${NY(350)+30}${NK(350,50,30)} Z`,6,.2)}
   ${G('scf',`M46,250${NK(48,352,-8)} L354,${NY(352)+26}${NK(352,48,26)} Z`,'#F2B544','<path d="M80,250 V350 M118,250 V350 M156,250 V350 M194,250 V350 M232,250 V350 M270,250 V350 M308,250 V350" stroke="#E09C2C" stroke-width="10"/><path d="M60,300 Q200,330 340,300" stroke="#FFD27A" stroke-width="3" fill="none" opacity=".8"/>',4.8)}</g>
   <g data-sw="2.4,2.4,250,330,0">${SH('M236,326 L276,324 L286,398 L246,402 Z',6,.16)}
    ${G('tail','M234,324 L274,322 L284,398 L244,402 Z','#F2B544','<path d="M230,346 L290,342 M232,370 L292,366" stroke="#E09C2C" stroke-width="10"/>',4.6,false)}
    <path d="M248,404 l-2,12 M257,403 l-1,13 M266,402 l0,13 M275,401 l1,12 M283,400 l2,11" stroke="#E09C2C" stroke-width="5" stroke-linecap="round"/></g>`,
  head:`${SH('M56,150 Q200,126 344,150 L346,178 Q200,156 54,178 Z',8,.2)}
   ${G('bean','M66,160 C68,96 126,58 200,58 C274,58 332,96 334,160 Z','#5DB6A0','<path d="M110,150 Q118,100 150,72 M155,150 Q160,96 178,62 M200,150 V58 M245,150 Q240,96 222,62 M290,150 Q282,100 250,72" stroke="#4FA48F" stroke-width="5" fill="none"/><path d="M96,120 l8,8 8,-8 M140,110 l8,8 8,-8 M188,104 l8,8 8,-8 M236,110 l8,8 8,-8 M284,120 l8,8 8,-8 M120,86 l8,8 8,-8 M188,76 l8,8 8,-8 M256,86 l8,8 8,-8" stroke="#7FCBB6" stroke-width="3" fill="none" stroke-linejoin="round"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5,false)}
   ${G('cuff','M54,146 Q200,120 346,146 L348,178 Q200,154 52,178 Z','#4FA48F','<path d="M70,140 V182 M86,138 V180 M102,136 V178 M118,134 V176 M134,132 V174 M150,131 V172 M166,130 V171 M182,129 V170 M198,129 V170 M214,129 V170 M230,130 V171 M246,131 V172 M262,132 V174 M278,134 V176 M294,136 V178 M310,138 V180 M326,140 V182" stroke="#3F8F7B" stroke-width="3.5"/>',5,false)}
   <g data-bob="1.2">${SH('M200,30 m-24,0 a24,24 0 1,0 48,0 a24,24 0 1,0 -48,0',5,.14)}
    <path d="M200,6 C214,6 220,14 224,20 C232,22 230,34 226,38 C232,46 222,56 214,54 C210,60 190,60 186,54 C178,56 168,46 174,38 C170,34 168,22 176,20 C180,14 186,6 200,6 Z" fill="#FFF4E0" stroke="${OL}" stroke-width="4.5" stroke-linejoin="round"/>
    <path d="M188,22 Q194,16 202,16" stroke="#fff" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M186,44 Q200,50 214,44" stroke="#EAD8BC" stroke-width="4" stroke-linecap="round" fill="none"/></g>`,
  glove:`<rect x="-27" y="16" width="54" height="52" fill="#F2B544"/><rect x="-27" y="16" width="54" height="11" fill="#E09C2C"/><path d="M-20,16 v11 M-12,16 v11 M-4,16 v11 M4,16 v11 M12,16 v11 M20,16 v11" stroke="#C98722" stroke-width="2.5"/><path d="M-27,27 H27" stroke="${OL}" stroke-width="3"/>`},

 // 5) 김장·장보기·먹거리 물가 — 물방울 두건(매듭이 흔들림) + 어깨끈 앞치마(배추 주머니) + 고무장갑(접힌 소매)
 kimjang:{bag:false,
  body:`${G('apr','M140,326 Q200,316 260,326 L266,350 C312,358 344,384 350,440 L50,440 C56,384 88,358 134,350 Z','#FFD3DA','<path d="M134,352 Q200,366 266,352" stroke="#F4AEBB" stroke-width="7" fill="none"/><path d="M110,380 Q120,410 112,440 M290,380 Q280,410 288,440 M200,370 V440" stroke="#F6BFC9" stroke-width="5" fill="none"/>',4.8)}
   <path d="M142,328${NK(142,60,10).replace(/ L/g,' L')}" stroke="${OL}" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M142,328${NK(142,60,10)}" stroke="#F49BAA" stroke-width="7" stroke-linecap="round" fill="none"/>
   <path d="M258,328${NK(258,340,10)}" stroke="${OL}" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M258,328${NK(258,340,10)}" stroke="#F49BAA" stroke-width="7" stroke-linecap="round" fill="none"/>
   ${SH('M160,374 h66 v36 h-66 z',4,.14)}${G('pk','M160,372 h66 a10,10 0 0 1 10,10 v24 a10,10 0 0 1 -10,10 h-66 a10,10 0 0 1 -10,-10 v-24 a10,10 0 0 1 10,-10 z','#FFE9ED','<path d="M150,380 H236" stroke="#F4AEBB" stroke-width="4"/>',4.2,false)}
   <g transform="translate(193,372) scale(.9)"><path d="M0,34 C-18,30 -20,8 -7,-4 C-2,8 0,16 0,34 Z" fill="#9BD37A" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M0,34 C18,30 20,8 7,-4 C2,8 0,16 0,34 Z" fill="#7CC35C" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M0,34 C-8,25 -7,9 0,0 C7,9 8,25 0,34 Z" fill="#F3F8D6" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/></g>${CHIN()}`,
  head:`<defs><pattern id="dDot" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)"><circle cx="6" cy="6" r="3.8" fill="#FFF1F1"/><circle cx="18" cy="18" r="3.8" fill="#FFF1F1"/></pattern></defs>
   ${SH('M64,172 C100,150 150,142 200,142 C250,142 300,150 336,172 L336,180 C300,160 250,152 200,152 C150,152 100,160 64,180 Z',4,.24)}
   ${G('band','M64,174 C68,112 124,78 200,78 C276,78 332,112 336,174 C300,152 250,144 200,144 C150,144 100,152 64,174 Z','#E8505B','<rect x="-70" y="-70" width="540" height="560" fill="url(#dDot)"/><path d="M64,174 C100,152 150,144 200,144 C250,144 300,152 336,174" stroke="#C93F4A" stroke-width="16" fill="none"/><path d="M110,100 Q150,84 196,86" stroke="#FF8F98" stroke-width="7" stroke-linecap="round" fill="none" opacity=".8"/><path d="M150,110 Q180,128 170,144 M250,112 Q228,128 236,144" stroke="#C93F4A" stroke-width="4" fill="none" opacity=".7"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5.2,false)}
   <g transform="translate(320,146)"><g data-sw="5,2.8,0,0,0">${G('t1','M0,0 L40,-20 Q50,0 32,12 Z','#E8505B','<rect x="0" y="-30" width="60" height="50" fill="url(#dDot)"/>',4.6,false)}</g>
    <g data-sw="-6,2.4,0,0,1.2">${G('t2','M0,0 L34,28 Q18,40 4,26 Z','#D9434F','<rect x="0" y="0" width="40" height="44" fill="url(#dDot)"/>',4.6,false)}</g>
    <circle r="11" fill="#D9434F" stroke="${OL}" stroke-width="4.6"/><path d="M-5,-4 Q0,-8 5,-4" stroke="#FF8F98" stroke-width="3" fill="none" stroke-linecap="round"/></g>`,
  glove:`<rect x="-27" y="8" width="54" height="60" fill="#E8505B"/><path d="M-10,40 Q-6,58 -12,64 M8,38 Q14,56 10,64" stroke="#FF8F98" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/><rect x="-27" y="6" width="54" height="13" fill="#F7A1A9"/><path d="M-27,6 H27 M-27,19 H27" stroke="${OL}" stroke-width="3"/>`},

 // 6) 과학·기술·우주·AI — 흰 실험 가운(민트 티셔츠, 가슴 주머니 펜) + 이마에 올린 보안경
 science:{bag:false,
  body:`${G('tee',FULL,'#7CC9B5',`<path d="M70,${NY(70)+6}${NK(70,330,8)}" stroke="#5FB39D" stroke-width="8" fill="none"/>`)}
   ${G('lcl',PL(172,396),'#F4F7F9','<path d="M70,320 Q96,380 88,440" stroke="#DCE3E8" stroke-width="6" fill="none"/>',4.6)}
   ${G('lcr',PR(228,396),'#F4F7F9','<path d="M330,320 Q304,380 312,440" stroke="#DCE3E8" stroke-width="6" fill="none"/>',4.6)}
   ${G('lpl',`M172,${NY(172)} L200,396 L182,360 L140,${NY(140)+6} Z`,'#E3E9ED','',4,false)}${G('lpr',`M228,${NY(228)} L200,396 L218,360 L260,${NY(260)+6} Z`,'#E3E9ED','',4,false)}
   <rect x="96" y="334" width="10" height="34" rx="3" fill="#4F7FD9" stroke="${OL}" stroke-width="3"/><rect x="110" y="330" width="10" height="38" rx="3" fill="#E2483A" stroke="${OL}" stroke-width="3"/>
   ${G('lpk','M86,346 h48 v30 a8,8 0 0 1 -8,8 h-32 a8,8 0 0 1 -8,-8 z','#EDF2F5','',4,false)}
   <circle cx="222" cy="376" r="5" fill="#DCE3E8" stroke="${OL}" stroke-width="2.5"/><circle cx="214" cy="410" r="5" fill="#DCE3E8" stroke="${OL}" stroke-width="2.5"/>${CHIN()}`,
  head:`${SH('M118,124 h64 v34 h-64 z M218,124 h64 v34 h-64 z',6,.18)}
   <path d="M62,152 Q200,116 338,152" fill="none" stroke="${OL}" stroke-width="13" stroke-linecap="round"/><path d="M62,152 Q200,116 338,152" fill="none" stroke="#3E6B78" stroke-width="7" stroke-linecap="round"/>
   ${G('gl','M120,120 h60 a14,14 0 0 1 14,14 v8 a14,14 0 0 1 -14,14 h-60 a14,14 0 0 1 -14,-14 v-8 a14,14 0 0 1 14,-14 z','#9BD7E4','<path d="M118,126 L150,152 M136,122 L170,154" stroke="#fff" stroke-width="5" opacity=".7"/>',5,false)}
   ${G('gr','M220,120 h60 a14,14 0 0 1 14,14 v8 a14,14 0 0 1 -14,14 h-60 a14,14 0 0 1 -14,-14 v-8 a14,14 0 0 1 14,-14 z','#9BD7E4','<path d="M218,126 L250,152 M236,122 L270,154" stroke="#fff" stroke-width="5" opacity=".7"/>',5,false)}
   <path d="M194,136 Q200,130 206,136" stroke="${OL}" stroke-width="6" fill="none" stroke-linecap="round"/>`,
  glove:`<rect x="-27" y="-30" width="54" height="58" fill="#F4F7F9"/><path d="M-27,22 H27" stroke="#DCE3E8" stroke-width="6"/><path d="M-27,27 H27" stroke="${OL}" stroke-width="3"/>`,},

 // 7) 상식·교육·수능·입시 — 학사모(술이 흔들림) + 와인색 카디건(흰 셔츠 깃)
 trivia:{bag:false,
  body:`${G('cdl',PL(178,352),'#A44A5C','<path d="M40,268 V440 M60,268 V440 M80,268 V440 M100,268 V440 M120,268 V440 M140,268 V440 M160,268 V440 M180,268 V440" stroke="#953F51" stroke-width="3"/><path d="M10,396 H220" stroke="#8C3A4B" stroke-width="20"/>')}
   ${G('cdr',PR(222,352),'#A44A5C','<path d="M220,268 V440 M240,268 V440 M260,268 V440 M280,268 V440 M300,268 V440 M320,268 V440 M340,268 V440 M360,268 V440" stroke="#953F51" stroke-width="3"/><path d="M180,396 H390" stroke="#8C3A4B" stroke-width="20"/>')}
   <circle cx="200" cy="366" r="5.5" fill="#F3E3C8" stroke="${OL}" stroke-width="2.5"/><circle cx="200" cy="388" r="5.5" fill="#F3E3C8" stroke="${OL}" stroke-width="2.5"/>${CHIN()}`,
  top:`${COLLAR('#FFFFFF',178,336)}`,
  head:`${SH('M88,146 Q200,128 312,146 L312,154 Q200,136 88,154 Z',6,.22)}
   ${G('cap','M88,148 C92,110 140,94 200,94 C260,94 308,110 312,148 Q200,128 88,148 Z','#2D3550','<rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5,false)}
   <path d="M70,88 L70,96 L200,128 L330,96 L330,88" fill="#222941" stroke="${OL}" stroke-width="5" stroke-linejoin="round"/>
   ${G('board','M200,54 L330,88 L200,122 L70,88 Z','#353E5E','<path d="M120,88 L200,66 L280,88" stroke="#47517A" stroke-width="5" fill="none"/>',5,false)}
   <g data-sw="4,2.3,300,94,0"><path d="M200,88 Q260,90 300,94 L304,150" fill="none" stroke="#F2B544" stroke-width="5" stroke-linecap="round"/>
    <path d="M296,146 h16 l4,24 h-24 z" fill="#F2B544" stroke="${OL}" stroke-width="3.5" stroke-linejoin="round"/><path d="M299,154 v14 M304,154 v14 M309,154 v14" stroke="#D99A2B" stroke-width="2"/></g>
   <circle cx="200" cy="88" r="7" fill="#F2B544" stroke="${OL}" stroke-width="3.5"/>`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#A44A5C"/><rect x="-27" y="16" width="54" height="11" fill="#8C3A4B"/><path d="M-20,16 v11 M-12,16 v11 M-4,16 v11 M4,16 v11 M12,16 v11 M20,16 v11" stroke="#7A3242" stroke-width="2.2"/><path d="M-27,27 H27" stroke="${OL}" stroke-width="3"/>`,},

 // 8) 팩트체크·"진짜일까?"·오해 바로잡기 — 사냥모자(체크) + 트렌치코트(벨트) + 목에 건 돋보기(흔들림)
 detective:{bag:false,
  body:`${G('tcL',PL(176,352),'#D8B67E','<path d="M10,372 H220" stroke="#B99257" stroke-width="18"/><path d="M80,320 Q100,370 92,440" stroke="#C7A266" stroke-width="5" fill="none"/>')}
   ${G('tcR',PR(224,352),'#D8B67E','<path d="M180,372 H390" stroke="#B99257" stroke-width="18"/><path d="M320,320 Q300,370 308,440" stroke="#C7A266" stroke-width="5" fill="none"/>')}
   ${G('tlL',`M176,${NY(176)} L200,352 L172,346 L126,${NY(126)+6} Z`,'#C9A46A','',4.2,false)}${G('tlR',`M224,${NY(224)} L200,352 L228,346 L274,${NY(274)+6} Z`,'#C9A46A','',4.2,false)}
   <rect x="186" y="362" width="28" height="20" rx="4" fill="none" stroke="#7A5A2A" stroke-width="4.5"/><path d="M200,372 h14" stroke="#7A5A2A" stroke-width="4"/>
   <g fill="#8C6A38" stroke="${OL}" stroke-width="2.2"><circle cx="172" cy="356" r="4.5"/><circle cx="228" cy="356" r="4.5"/><circle cx="172" cy="398" r="4.5"/><circle cx="228" cy="398" r="4.5"/></g>${CHIN()}`,
  top:`<g data-sw="2.2,2.1,212,322,0.4"><path d="M188,${NY(188)+4} Q206,340 238,350 M212,${NY(212)+4} Q222,336 238,350" fill="none" stroke="${OL}" stroke-width="6" stroke-linecap="round"/><path d="M188,${NY(188)+4} Q206,340 238,350 M212,${NY(212)+4} Q222,336 238,350" fill="none" stroke="#7A5A2A" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M238,350 L244,362" stroke="${OL}" stroke-width="11" stroke-linecap="round"/><path d="M238,350 L244,362" stroke="#8C5A32" stroke-width="5.5" stroke-linecap="round"/>
    ${SH('M252,384 m-18,0 a18,18 0 1,0 36,0 a18,18 0 1,0 -36,0',4,.18)}
    <circle cx="252" cy="380" r="18" fill="#CFEFFF" fill-opacity=".7" stroke="${OL}" stroke-width="8"/><circle cx="252" cy="380" r="18" fill="none" stroke="#5A6470" stroke-width="3.5"/>
    <path d="M243,373 Q247,367 255,367" stroke="#fff" stroke-width="4" stroke-linecap="round" fill="none"/></g>`,
  head:`<defs><pattern id="dChk" width="22" height="22" patternUnits="userSpaceOnUse"><rect width="22" height="22" fill="#9C7A4F"/><path d="M0,5 H22 M0,16 H22" stroke="#86653E" stroke-width="3"/><path d="M5,0 V22 M16,0 V22" stroke="#B08C5E" stroke-width="2.5"/></pattern></defs>
   ${SH('M110,148 Q200,128 290,148 Q280,176 200,178 Q120,176 110,148 Z',6,.2)}
   ${G('dcr','M74,152 C78,96 132,64 200,64 C268,64 322,96 326,152 Q200,134 74,152 Z','#9C7A4F','<rect x="-70" y="-70" width="540" height="560" fill="url(#dChk)"/><path d="M200,64 V150 M140,74 Q128,110 122,150 M260,74 Q272,110 278,150" stroke="#6E5230" stroke-width="3" fill="none"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5,false)}
   ${G('dbr','M108,146 Q200,126 292,146 Q282,176 200,178 Q118,176 108,146 Z','#8A6A42','<rect x="-70" y="-70" width="540" height="560" fill="url(#dChk)" opacity=".6"/><path d="M118,152 Q200,136 282,152" stroke="#B08C5E" stroke-width="4" fill="none"/>',4.8,false)}
   <circle cx="200" cy="64" r="8" fill="#7A5A2A" stroke="${OL}" stroke-width="3.5"/>`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#D8B67E"/><rect x="-27" y="14" width="54" height="9" fill="#B99257"/><path d="M-27,26 H27" stroke="${OL}" stroke-width="3"/>`,},

 // 9) 해외여행·환율·면세·관광 — 밀짚모자(선글라스를 모자에) + 하늘색 꽃무늬 셔츠
 travel:{bag:false,
  body:`<defs><pattern id="dHib" width="64" height="58" patternUnits="userSpaceOnUse"><g transform="translate(16,16)"><g fill="#FFFFFF"><circle cx="0" cy="-8" r="6"/><circle cx="8" cy="-2" r="6"/><circle cx="5" cy="7" r="6"/><circle cx="-5" cy="7" r="6"/><circle cx="-8" cy="-2" r="6"/></g><circle r="3.5" fill="#FF8FA0"/></g>
    <g transform="translate(48,44) scale(.8)"><g fill="#FFD3DA"><circle cx="0" cy="-8" r="6"/><circle cx="8" cy="-2" r="6"/><circle cx="5" cy="7" r="6"/><circle cx="-5" cy="7" r="6"/><circle cx="-8" cy="-2" r="6"/></g><circle r="3.5" fill="#F2B544"/></g>
    <path d="M38,10 q8,4 10,14 M2,40 q10,0 14,10" stroke="#4FB09A" stroke-width="4" fill="none" stroke-linecap="round"/></pattern></defs>
   ${G('alL',PL(174,346),'#6EC3E8','<rect x="-70" y="-70" width="540" height="560" fill="url(#dHib)"/>')}
   ${G('alR',PR(226,346),'#6EC3E8','<rect x="-70" y="-70" width="540" height="560" fill="url(#dHib)"/>')}
   <path d="M200,346 V440" stroke="${OL}" stroke-width="4.5"/><g fill="#FFF6E6" stroke="${OL}" stroke-width="2.2"><circle cx="208" cy="366" r="4"/><circle cx="208" cy="392" r="4"/></g>${CHIN()}`,
  top:`${G('acL',`M174,${NY(174)} L200,346 L176,342 L134,${NY(134)+8} Z`,'#5AB4DC','',4.2,false)}${G('acR',`M226,${NY(226)} L200,346 L224,342 L266,${NY(266)+8} Z`,'#5AB4DC','',4.2,false)}`,
  head:`${SH('M24,150 Q200,112 376,150 Q380,176 340,180 Q200,160 60,180 Q20,176 24,150 Z',9,.22)}
   ${G('brm','M24,150 Q200,112 376,150 Q380,176 340,180 Q200,160 60,180 Q20,176 24,150 Z','#EBC777','<path d="M40,160 Q200,128 360,160 M50,170 Q200,140 350,170" stroke="#D6AE5C" stroke-width="3" fill="none"/>',5,false)}
   ${G('crn','M104,146 C106,94 146,68 200,68 C254,68 294,94 296,146 Q200,130 104,146 Z','#F0CF83','<path d="M120,140 Q126,96 160,78 M150,138 Q154,94 180,72 M200,136 V68 M250,138 Q246,94 220,72 M280,140 Q274,96 240,78" stroke="#D9B565" stroke-width="3" fill="none"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5,false)}
   ${G('rib','M104,128 Q200,112 296,128 L296,146 Q200,130 104,146 Z','#E8505B','<path d="M106,134 Q200,118 294,134" stroke="#FF8F98" stroke-width="3" fill="none"/>',4.2,false)}
   <g transform="translate(200,98)"><path d="M-46,-6 h36 a6,6 0 0 1 6,6 v4 a16,16 0 0 1 -16,16 h-10 a16,16 0 0 1 -16,-16 v-4 a6,6 0 0 1 6,-6 z" fill="#2E3440" stroke="${OL}" stroke-width="3.5"/><path d="M10,-6 h36 a6,6 0 0 1 6,6 v4 a16,16 0 0 1 -16,16 h-10 a16,16 0 0 1 -16,-16 v-4 a6,6 0 0 1 6,-6 z" fill="#2E3440" stroke="${OL}" stroke-width="3.5"/>
    <path d="M-4,0 Q0,-4 4,0" stroke="${OL}" stroke-width="3.5" fill="none"/><path d="M-40,0 l10,10 M16,0 l10,10" stroke="#8FA3B8" stroke-width="3" stroke-linecap="round"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="40" fill="#6EC3E8"/><rect x="-27" y="-30" width="54" height="40" fill="url(#dHib)"/><path d="M-27,10 H27" stroke="${OL}" stroke-width="3"/>`},

 // 10) 월급·연봉·고용·직장인·최저임금 — 하늘색 셔츠(소매 걷음) + 사원증 목걸이(흔들림)
 office:{bag:false,
  body:`${G('sh',FULL,'#CFE3F7','<path d="M200,330 V440" stroke="#B7D0EA" stroke-width="10"/><path d="M60,320 Q80,380 74,440 M340,320 Q320,380 326,440" stroke="#BFD6EE" stroke-width="5" fill="none"/>')}
   <path d="M200,332 V440" stroke="${OL}" stroke-width="3"/><g fill="#fff" stroke="${OL}" stroke-width="2"><circle cx="206" cy="352" r="3.5"/><circle cx="206" cy="376" r="3.5"/><circle cx="206" cy="400" r="3.5"/></g>
   ${G('spk','M234,338 h40 v28 a6,6 0 0 1 -6,6 h-28 a6,6 0 0 1 -6,-6 z','#C2DAF3','',3.6,false)}${CHIN()}`,
  top:`${COLLAR('#DCEBFA',178,334)}
   <g data-sw="1.8,2.0,200,318,0.6"><path d="M166,${NY(166)+4} Q174,346 194,360 M234,${NY(234)+4} Q226,346 206,360" fill="none" stroke="${OL}" stroke-width="8" stroke-linecap="round"/><path d="M166,${NY(166)+4} Q174,346 194,360 M234,${NY(234)+4} Q226,346 206,360" fill="none" stroke="#2E9C83" stroke-width="4" stroke-linecap="round"/>
    ${SH('M180,362 h40 v44 h-40 z',4,.16)}${G('badge','M182,360 h36 a6,6 0 0 1 6,6 v36 a6,6 0 0 1 -6,6 h-36 a6,6 0 0 1 -6,-6 v-36 a6,6 0 0 1 6,-6 z','#FFFFFF','<rect x="186" y="368" width="16" height="17" rx="3" fill="#80D0BA"/><path d="M188,392 h24 M188,399 h16" stroke="#BFC7CE" stroke-width="3.5" stroke-linecap="round"/><path d="M176,360 h48 v6 h-48 z" fill="#2E9C83"/>',3.8,false)}
    <rect x="194" y="354" width="12" height="10" rx="2" fill="#9AA6B2" stroke="${OL}" stroke-width="2.5"/></g>`,
  glove:`<rect x="-27" y="-30" width="54" height="50" fill="#CFE3F7"/><rect x="-27" y="10" width="54" height="13" rx="3" fill="#E3EFFB"/><path d="M-27,10 H27 M-27,23 H27" stroke="${OL}" stroke-width="3"/><path d="M-18,14 v6 M0,14 v6 M18,14 v6" stroke="#B7D0EA" stroke-width="2.5"/>`,},

};

// 주제 → 옷 추천(편을 만들 때 고르는 기준). 맞는 게 없으면 ''(기본: 민트 크로스백)
const TOPIC={news:'금리·환율·경제 지표·경제 해설',tax:'연말정산·세금·연금·건강보험료·지원금 신청',export:'수출입·반도체·조선·자동차·산업 통계',
  winter:'난방비·전기·가스요금·겨울 물가·한파',kimjang:'김장·장바구니 물가·농수산물·먹거리 수출',
  science:'과학·기술·우주·날씨·AI 원리',trivia:'상식·역사·지리·숫자 퀴즈 일반·교육·수능·입시·학자금',detective:'팩트체크·"진짜일까?"·오해 바로잡기·반전 숫자',
  travel:'해외여행·환율·면세·항공·관광',office:'월급·연봉·고용·직장인·최저임금'};
let UID=0;
function apply(sl,name){
  const o=OUTFIT[name]; if(!o) return false;
  const sfx='_'+(++UID), fix=s=>(s||'').replace(/\b(dBodyM|dRound|dDome|dSoft|dDot|dChk|dHib|dG[A-Za-z0-9]+)\b/g,m=>m+sfx);
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