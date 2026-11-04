// 도리 옷장(주제별 옷) — 숫자 퀴즈·생활 정보·해설(templates/quiz/dori.js)과 가격 검산(shopping/assets/dori.js)이 같이 쓴다.
// 이 파일 하나가 정본이다. new_episode.sh 와 shopping render.py 가 복사해 간다.
//   DoriOutfit.list()                       → 옷 이름들
//   DoriOutfit.apply(slots, name)           → slots={body,top,head,gloves:[g,g],bag} 에 옷을 넣는다(옷을 입으면 크로스백은 숨긴다)
//   DoriOutfit.anim(root, st)               → 매 프레임: 볼주머니 마스크 + 매듭·방울·넥타이·목도리 끝 흔들림  st={t,hop,squash,ckL:[cx,cy,r],ckR:[…]}
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
 <path d="${d}" fill="none" stroke="${OL}" stroke-width="${sw}" stroke-linejoin="round" stroke-linecap="round"/>`;}
// 털에 떨어지는 그림자(옷 가장자리 아래)
const SH=(d,dy=7,o=.16)=>`<path d="${d}" transform="translate(0 ${dy})" fill="#2A1A10" opacity="${o}" filter="url(#dSoft)"/>`;
// 몸통을 감싸는 앞판(왼·오른 판이 가운데 V에서 만난다)
const PANEL_L='M20,268 L172,268 L200,338 L203,430 L20,430 Z', PANEL_R='M380,268 L228,268 L200,338 L197,430 L380,430 Z';
const OUTFIT={
 // 1) 경제 뉴스·해설 — 남색 재킷 + 흰 셔츠 깃 + 민트 넥타이(채널 색)
 news:{bag:false,
  body:`${SH('M20,262 L172,262 L200,332 L228,262 L380,262 L380,300 L20,300 Z',4,.12)}
   ${G('nl',PANEL_L,'#3E5A8C','<path d="M60,300 Q90,360 84,420" stroke="#33507F" stroke-width="5" fill="none" opacity=".7"/>')}
   ${G('nr',PANEL_R,'#3E5A8C','<path d="M340,300 Q310,360 316,420" stroke="#33507F" stroke-width="5" fill="none" opacity=".7"/>')}
   ${G('lal','M172,268 L200,338 L178,320 L150,290 L158,268 Z','#2F4874','',4.2,false)}
   ${G('lar','M228,268 L200,338 L222,320 L250,290 L242,268 Z','#2F4874','',4.2,false)}
   <path d="M244,316 L272,312" stroke="${OL}" stroke-width="4" stroke-linecap="round"/><path d="M247,313 L254,300 L262,312 Z" fill="#80D0BA" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/>
   <circle cx="200" cy="362" r="5.5" fill="#25385C" stroke="${OL}" stroke-width="2.5"/>`,
  top:`${G('cl','M170,266 L200,300 L182,304 L160,280 Z','#FFFFFF','<path d="M170,266 L200,300" stroke="#E6E1DC" stroke-width="6"/>',4,false)}
   ${G('cr','M230,266 L200,300 L218,304 L240,280 Z','#FFFFFF','<path d="M230,266 L200,300" stroke="#E6E1DC" stroke-width="6"/>',4,false)}
   <g data-sw="1.6,2.2,200,296,0">${SH('M192,302 L208,302 L214,356 L200,372 L186,356 Z',5,.14)}
    ${G('tie','M192,302 L208,302 L215,356 L200,374 L185,356 Z','#2E9C83','<path d="M180,318 L224,300 M180,334 L224,316 M180,350 L224,332" stroke="#5FC2A9" stroke-width="5"/>',4.2,false)}
    ${G('kn','M190,288 L210,288 L207,304 L193,304 Z','#268A73','',4.2,false)}</g>`,
  glove:`<rect x="-27" y="-30" width="54" height="56" fill="#3E5A8C"/><rect x="-27" y="22" width="54" height="9" fill="#FFFFFF"/><path d="M-27,22 H27" stroke="${OL}" stroke-width="3"/><path d="M-27,31 H27" stroke="${OL}" stroke-width="3"/>`},

 // 2) 세금·연말정산·연금 — 초록 차양 바이저 + 동그란 안경 + 낙타색 니트 조끼 + 나비넥타이 + 귀에 꽂은 연필
 tax:{bag:false,
  body:`${SH('M20,264 L174,264 L200,326 L226,264 L380,264 L380,296 L20,296 Z',4,.12)}
   ${G('vl',PANEL_L.replace('L200,338','L200,330'),'#C99A6B','<path d="M40,300 l26,26 -26,26 -26,-26z M92,330 l26,26 -26,26 -26,-26z M40,360 l26,26 -26,26 -26,-26z M140,300 l26,26 -26,26 -26,-26z" fill="none" stroke="#E2BE93" stroke-width="3.5"/><path d="M20,384 H220" stroke="#B5845A" stroke-width="22"/><path d="M30,376 v18 M44,376 v18 M58,376 v18 M72,376 v18 M86,376 v18 M100,376 v18 M114,376 v18 M128,376 v18 M142,376 v18 M156,376 v18 M170,376 v18 M184,376 v18 M198,376 v18" stroke="#A3744C" stroke-width="2.5"/>')}
   ${G('vr',PANEL_R.replace('L200,338','L200,330'),'#C99A6B','<path d="M360,300 l-26,26 26,26 26,-26z M308,330 l-26,26 26,26 26,-26z M360,360 l-26,26 26,26 26,-26z M260,300 l-26,26 26,26 26,-26z" fill="none" stroke="#E2BE93" stroke-width="3.5"/><path d="M180,384 H380" stroke="#B5845A" stroke-width="22"/><path d="M202,376 v18 M216,376 v18 M230,376 v18 M244,376 v18 M258,376 v18 M272,376 v18 M286,376 v18 M300,376 v18 M314,376 v18 M328,376 v18 M342,376 v18 M356,376 v18 M370,376 v18" stroke="#A3744C" stroke-width="2.5"/>')}`,
  top:`${G('tcl','M172,266 L200,296 L182,300 L162,280 Z','#FFFFFF','',4,false)}${G('tcr','M228,266 L200,296 L218,300 L238,280 Z','#FFFFFF','',4,false)}
   <g data-sw="1.2,2.0,200,298,1">${G('bwl','M200,298 L176,286 L174,312 Z','#2E6E5E','<path d="M178,290 L184,308" stroke="#3F8A77" stroke-width="3"/>',4,false)}${G('bwr','M200,298 L224,286 L226,312 Z','#2E6E5E','<path d="M222,290 L216,308" stroke="#3F8A77" stroke-width="3"/>',4,false)}
   <rect x="193" y="291" width="14" height="14" rx="4" fill="#25594B" stroke="${OL}" stroke-width="3.5"/></g>`,
  head:`<g transform="rotate(-38 318 104)"><rect x="286" y="96" width="70" height="15" rx="3" fill="#FFCF4A" stroke="${OL}" stroke-width="3.5"/><path d="M286,96 L270,103.5 L286,111 Z" fill="#F4D7B0" stroke="${OL}" stroke-width="3.5" stroke-linejoin="round"/><path d="M270,103.5 L276,103.5" stroke="${OL}" stroke-width="4" stroke-linecap="round"/><rect x="348" y="96" width="14" height="15" rx="4" fill="#F7A1A9" stroke="${OL}" stroke-width="3.5"/><path d="M290,100 H346" stroke="#FFE38A" stroke-width="3"/></g>
   ${SH('M96,150 Q200,128 304,150 Q296,180 200,182 Q104,180 96,150 Z',8,.14)}
   <path d="M60,156 Q200,118 340,156" fill="none" stroke="#2F7D52" stroke-width="12" stroke-linecap="round"/>
   <path d="M60,156 Q200,118 340,156" fill="none" stroke="#3FA36B" stroke-width="6" stroke-linecap="round"/>
   ${G('bill','M96,150 Q200,126 304,150 Q298,182 200,184 Q102,182 96,150 Z','#3FA36B','<path d="M106,156 Q200,138 294,156" stroke="#9EE0B8" stroke-width="5" fill="none" opacity=".8"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',4.4,false).replace('fill="#3FA36B"/>','fill="#3FA36B" opacity=".86"/>')}`,
  face:`<g fill="#fff" fill-opacity=".14" stroke="#5A4636" stroke-width="4.5"><circle cx="148" cy="214" r="31"/><circle cx="252" cy="214" r="31"/></g>
   <path d="M179,212 Q200,200 221,212" fill="none" stroke="#5A4636" stroke-width="4.5" stroke-linecap="round"/>
   <path d="M117,208 L84,198 M283,208 L316,198" stroke="#5A4636" stroke-width="4.5" stroke-linecap="round"/>
   <path d="M128,196 Q136,188 146,186 M232,196 Q240,188 250,186" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".75" fill="none"/>`},

 // 3) 수출·산업·무역 — 노란 안전모 + 주황 형광 조끼(반사띠)
 export:{bag:false,
  body:`${G('hvl',PANEL_L.replace('L200,338','L192,330 L194,430').replace('L203,430',''),'#FF8A2A','<path d="M20,328 H200" stroke="#D9E2E8" stroke-width="16"/><path d="M20,323 H200" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M20,366 H200" stroke="#D9E2E8" stroke-width="16"/><path d="M20,361 H200" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M120,268 V420" stroke="#E87420" stroke-width="3" stroke-dasharray="8 8" opacity=".7"/>')}
   ${G('hvr',PANEL_R.replace('L200,338','L208,330 L206,430').replace('L197,430',''),'#FF8A2A','<path d="M200,328 H380" stroke="#D9E2E8" stroke-width="16"/><path d="M200,323 H380" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M200,366 H380" stroke="#D9E2E8" stroke-width="16"/><path d="M200,361 H380" stroke="#FFFFFF" stroke-width="4" opacity=".8"/><path d="M280,268 V420" stroke="#E87420" stroke-width="3" stroke-dasharray="8 8" opacity=".7"/>')}
   <rect x="240" y="286" width="28" height="22" rx="4" fill="#FFB36B" stroke="${OL}" stroke-width="3.5"/><path d="M246,292 H262 M246,299 H258" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>`,
  head:`${SH('M48,150 Q200,126 352,150 Q350,168 336,172 Q200,150 64,172 Q50,168 48,150 Z',9,.2)}
   ${G('dome','M76,152 C80,96 134,62 200,62 C266,62 320,96 324,152 Z','#FFC93C','<path d="M184,60 L184,152 M216,60 L216,152" stroke="#E5A923" stroke-width="5"/><path d="M200,60 V152" stroke="#FFE07A" stroke-width="16"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/><path d="M110,110 Q130,82 168,72" stroke="#FFF3C4" stroke-width="9" stroke-linecap="round" fill="none"/>',5.2,false)}
   ${G('brim','M48,150 Q200,126 352,150 Q350,168 336,172 Q200,150 64,172 Q50,168 48,150 Z','#F2B627','<path d="M60,158 Q200,136 340,158" stroke="#FFD866" stroke-width="5" fill="none"/>',5,false)}`},

 // 4) 겨울 생활비(난방비·전기요금·겨울 물가) — 니트 비니(방울) + 줄무늬 목도리 + 벙어리장갑
 winter:{bag:false,
  top:`${SH('M70,280 Q200,306 330,280 L334,304 Q200,334 66,304 Z',8,.18)}
   <g mask="url(#dBodyM)">${G('scf','M58,274 Q200,302 342,274 L346,304 Q200,336 54,304 Z','#F2B544','<path d="M80,270 V320 M118,276 V330 M156,280 V336 M194,282 V338 M232,280 V336 M270,276 V330 M308,272 V322" stroke="#E09C2C" stroke-width="10"/><path d="M60,290 Q200,318 340,290" stroke="#FFD27A" stroke-width="3" fill="none" opacity=".8"/>',4.8)}</g>
   <g data-sw="2.4,2.4,250,300,0">${SH('M236,298 L276,296 L286,372 L246,376 Z',6,.16)}
    ${G('tail','M234,296 L274,294 L284,372 L244,376 Z','#F2B544','<path d="M230,318 L290,314 M232,342 L292,338" stroke="#E09C2C" stroke-width="10"/>',4.6,false)}
    <path d="M248,378 l-2,14 M257,377 l-1,15 M266,376 l0,15 M275,375 l1,14 M283,374 l2,13" stroke="#E09C2C" stroke-width="5" stroke-linecap="round"/></g>`,
  head:`${SH('M56,150 Q200,126 344,150 L346,178 Q200,156 54,178 Z',8,.2)}
   ${G('bean','M66,160 C68,96 126,58 200,58 C274,58 332,96 334,160 Z','#5DB6A0','<path d="M110,150 Q118,100 150,72 M155,150 Q160,96 178,62 M200,150 V58 M245,150 Q240,96 222,62 M290,150 Q282,100 250,72" stroke="#4FA48F" stroke-width="5" fill="none"/><path d="M96,120 l8,8 8,-8 M140,110 l8,8 8,-8 M188,104 l8,8 8,-8 M236,110 l8,8 8,-8 M284,120 l8,8 8,-8 M120,86 l8,8 8,-8 M188,76 l8,8 8,-8 M256,86 l8,8 8,-8" stroke="#7FCBB6" stroke-width="3" fill="none" stroke-linejoin="round"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5,false)}
   ${G('cuff','M54,146 Q200,120 346,146 L348,178 Q200,154 52,178 Z','#4FA48F','<path d="M70,140 V182 M86,138 V180 M102,136 V178 M118,134 V176 M134,132 V174 M150,131 V172 M166,130 V171 M182,129 V170 M198,129 V170 M214,129 V170 M230,130 V171 M246,131 V172 M262,132 V174 M278,134 V176 M294,136 V178 M310,138 V180 M326,140 V182" stroke="#3F8F7B" stroke-width="3.5"/>',5,false)}
   <g data-bob="1.2">${SH('M200,30 m-24,0 a24,24 0 1,0 48,0 a24,24 0 1,0 -48,0',5,.14)}
    <path d="M200,6 C214,6 220,14 224,20 C232,22 230,34 226,38 C232,46 222,56 214,54 C210,60 190,60 186,54 C178,56 168,46 174,38 C170,34 168,22 176,20 C180,14 186,6 200,6 Z" fill="#FFF4E0" stroke="${OL}" stroke-width="4.5" stroke-linejoin="round"/>
    <path d="M188,22 Q194,16 202,16" stroke="#fff" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M186,44 Q200,50 214,44" stroke="#EAD8BC" stroke-width="4" stroke-linecap="round" fill="none"/></g>`,
  glove:`<rect x="-27" y="16" width="54" height="52" fill="#F2B544"/><rect x="-27" y="16" width="54" height="11" fill="#E09C2C"/><path d="M-20,16 v11 M-12,16 v11 M-4,16 v11 M4,16 v11 M12,16 v11 M20,16 v11" stroke="#C98722" stroke-width="2.5"/><path d="M-27,27 H27" stroke="${OL}" stroke-width="3"/>`},

 // 5) 김장·장보기·먹거리 물가 — 물방울 두건(매듭이 흔들림) + 어깨끈 앞치마(배추 주머니) + 고무장갑(접힌 소매)
 kimjang:{bag:false,
  body:`${G('apr','M134,280 Q200,272 266,280 L270,314 C314,322 344,354 350,420 L50,420 C56,354 86,322 130,314 Z','#FFD3DA','<path d="M128,316 Q200,330 272,316" stroke="#F4AEBB" stroke-width="7" fill="none"/><path d="M110,350 Q120,390 112,420 M290,350 Q280,390 288,420 M200,336 V420" stroke="#F6BFC9" stroke-width="5" fill="none"/>',4.8)}
   <path d="M136,284 Q104,284 64,296 M264,284 Q296,284 336,296" stroke="${OL}" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M136,284 Q104,284 64,296 M264,284 Q296,284 336,296" stroke="#F49BAA" stroke-width="7" stroke-linecap="round" fill="none"/>
   ${SH('M156,346 h70 v44 h-70 z',4,.14)}${G('pk','M156,344 h70 a10,10 0 0 1 10,10 v32 a10,10 0 0 1 -10,10 h-70 a10,10 0 0 1 -10,-10 v-32 a10,10 0 0 1 10,-10 z','#FFE9ED','<path d="M146,352 H236" stroke="#F4AEBB" stroke-width="4"/>',4.2,false)}
   <g transform="translate(190,346)"><path d="M0,34 C-18,30 -20,8 -7,-4 C-2,8 0,16 0,34 Z" fill="#9BD37A" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M0,34 C18,30 20,8 7,-4 C2,8 0,16 0,34 Z" fill="#7CC35C" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M0,34 C-8,25 -7,9 0,0 C7,9 8,25 0,34 Z" fill="#F3F8D6" stroke="${OL}" stroke-width="3" stroke-linejoin="round"/></g>`,
  head:`<defs><pattern id="dDot" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)"><circle cx="6" cy="6" r="3.8" fill="#FFF1F1"/><circle cx="18" cy="18" r="3.8" fill="#FFF1F1"/></pattern></defs>
   ${SH('M64,172 C100,150 150,142 200,142 C250,142 300,150 336,172 L336,180 C300,160 250,152 200,152 C150,152 100,160 64,180 Z',4,.24)}
   ${G('band','M64,174 C68,112 124,78 200,78 C276,78 332,112 336,174 C300,152 250,144 200,144 C150,144 100,152 64,174 Z','#E8505B','<rect x="-70" y="-70" width="540" height="560" fill="url(#dDot)"/><path d="M64,174 C100,152 150,144 200,144 C250,144 300,152 336,174" stroke="#C93F4A" stroke-width="16" fill="none"/><path d="M110,100 Q150,84 196,86" stroke="#FF8F98" stroke-width="7" stroke-linecap="round" fill="none" opacity=".8"/><path d="M150,110 Q180,128 170,144 M250,112 Q228,128 236,144" stroke="#C93F4A" stroke-width="4" fill="none" opacity=".7"/><rect x="-70" y="-70" width="540" height="560" fill="url(#dDome)"/>',5.2,false)}
   <g transform="translate(320,146)"><g data-sw="5,2.8,0,0,0">${G('t1','M0,0 L40,-20 Q50,0 32,12 Z','#E8505B','<rect x="0" y="-30" width="60" height="50" fill="url(#dDot)"/>',4.6,false)}</g>
    <g data-sw="-6,2.4,0,0,1.2">${G('t2','M0,0 L34,28 Q18,40 4,26 Z','#D9434F','<rect x="0" y="0" width="40" height="44" fill="url(#dDot)"/>',4.6,false)}</g>
    <circle r="11" fill="#D9434F" stroke="${OL}" stroke-width="4.6"/><path d="M-5,-4 Q0,-8 5,-4" stroke="#FF8F98" stroke-width="3" fill="none" stroke-linecap="round"/></g>`,
  glove:`<rect x="-27" y="8" width="54" height="60" fill="#E8505B"/><path d="M-10,40 Q-6,58 -12,64 M8,38 Q14,56 10,64" stroke="#FF8F98" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/><rect x="-27" y="6" width="54" height="13" fill="#F7A1A9"/><path d="M-27,6 H27 M-27,19 H27" stroke="${OL}" stroke-width="3"/>`}
};

// 주제 → 옷 추천(편을 만들 때 고르는 기준). 맞는 게 없으면 ''(기본: 민트 크로스백)
const TOPIC={news:'금리·환율·경제 지표·경제 해설',tax:'연말정산·세금·연금·건강보험료·지원금 신청',export:'수출입·반도체·조선·자동차·산업 통계',
  winter:'난방비·전기·가스요금·겨울 물가·한파',kimjang:'김장·장바구니 물가·농수산물·먹거리 수출'};
let UID=0;
function apply(sl,name){
  const o=OUTFIT[name]; if(!o) return false;
  const sfx='_'+(++UID), fix=s=>(s||'').replace(/\b(dBodyM|dRound|dDome|dSoft|dDot|dG[A-Za-z0-9]+)\b/g,m=>m+sfx);
  sl.body.innerHTML=fix(DEFS+`<g class="oBody" mask="url(#dBodyM)">${o.body||''}</g>`);
  sl.top.innerHTML=fix(`<g class="oTop">${o.top||''}</g>`);
  sl.head.innerHTML=fix(`<g class="oFace">${o.face||''}</g><g class="oHead">${o.head||''}</g>`);
  (sl.gloves||[]).forEach(g=>g.innerHTML=fix(o.glove||''));
  if(o.bag===false&&sl.bag) sl.bag.setAttribute('display','none');
  sl.body.ownerSVGElement&&(sl.body.ownerSVGElement.__outfit={name,o,sl});
  return true;
}
function anim(root,st){
  const t=st.t||0,hop=st.hop||0,sq=st.squash||0;
  root.querySelectorAll('.omkL,.omkR').forEach(c=>{const k=c.classList.contains('omkL')?st.ckL:st.ckR;if(!k)return;c.setAttribute('cx',k[0]);c.setAttribute('cy',k[1]);c.setAttribute('r',k[2]>0?k[2]+4:0);});
  root.querySelectorAll('[data-sw]').forEach(el=>{const [a,f,px,py,ph]=el.dataset.sw.split(',').map(Number);
    el.setAttribute('transform',`rotate(${(a*Math.sin(t*f+(ph||0))+hop*.05*Math.sign(a)).toFixed(2)} ${px} ${py})`);});
  root.querySelectorAll('[data-bob]').forEach(el=>{const a=+el.dataset.bob;el.setAttribute('transform',`translate(0 ${(a*Math.sin(t*3.1)+hop*.09+sq*6).toFixed(2)})`);});
}
// 렌더 전 점검(도형의 자기 좌표 기준 — 기울기·점프와 상관없이 같은 판정)
const EYE=[[117,188,179,240],[221,188,283,240]], MOUTH=[180,226,220,262];
const hit=(b,r)=>b.x<r[2]&&b.x+b.width>r[0]&&b.y<r[3]&&b.y+b.height>r[1];
function check(root){
  const svg=root.ownerSVGElement||root, info=svg.__outfit, out=[];
  if(!info) return out;
  const {name,o,sl}=info;
  // 보이는 도형만: 숨은 정의·그림자(흐림 필터)·옅은 것은 빼고, 자르기 그룹 안의 무늬는 그 그룹의 외곽선(같은 모양 path)으로 대신 본다
  const solid=g=>[...g.querySelectorAll('path,rect,circle,ellipse,polygon')].filter(e=>{
    if(e.closest('defs,clipPath,mask,pattern')) return false;
    if(e.getAttribute('filter')) return false;
    for(let p=e.parentElement;p&&p!==g;p=p.parentElement) if(p.getAttribute('clip-path')) return false;
    return +(e.getAttribute('opacity')??1)>.3;});
  for(const [lab,g] of [['머리',sl.head.querySelector('.oHead')],['몸',sl.body.querySelector('.oBody')],['목',sl.top.querySelector('.oTop')]]){
    if(!g) continue;
    for(const e of solid(g)){let b;try{b=e.getBBox();}catch(_){continue;}if(!b.width&&!b.height)continue;
      if(EYE.some(r=>hit(b,r))) {out.push(`${name}: ${lab} 옷이 눈을 가림 (${e.tagName} y ${b.y.toFixed(0)}~${(b.y+b.height).toFixed(0)})`);break;}
      if(hit(b,MOUTH)) {out.push(`${name}: ${lab} 옷이 코·입을 가림 (${e.tagName} y ${b.y.toFixed(0)}~${(b.y+b.height).toFixed(0)})`);break;}}
  }
  if(o.glove){const n=(sl.gloves||[]).filter(g=>g.childElementCount>0).length;if(n!==2) out.push(`${name}: 장갑·소매가 두 팔 중 ${n}개에만 있음`);}
  if(o.bag===false&&sl.bag&&sl.bag.getAttribute('display')!=='none') out.push(`${name}: 크로스백이 숨겨지지 않음`);
  return out;
}
window.DoriOutfit={list:()=>Object.keys(OUTFIT),topics:()=>({...TOPIC}),apply,anim,check};
})();
