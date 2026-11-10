// 스마트안경 A 다시 그리기(2026-11-11) — 상표 없는 뿔테 스마트안경.
// 위에서 살짝 내려다본 정면: 다리가 뒤로 뻗어 보이고, 경첩(엔드피스)은 테와 한 몸, 카메라는 테 안에 박힌 작은 렌즈.
// 렌즈는 투명(뒤 배경이 비침) + 부드러운 창문 반사, 테는 거북등 아세테이트(윗면 광택·안쪽 깎인 면·아래 그림자).
// SG3(w,{fold,led,id}) — fold: 다리를 접어 렌즈 너머로 비치게, led: 불빛 켜짐(기본 켜짐)
(function(){
let N=0;
const K='#3A2B22';
// 렌즈 모양 — 윗선은 거의 평평, 아래는 넉넉하게 둥근 부드러운 웰링턴형
function lens(x,y,w,h,rt){const r=rt||w*.16;
  return `M${x+r},${y} L${x+w-r},${y} Q${x+w},${y} ${x+w},${y+r} L${x+w},${y+h*.48}
  C${x+w},${y+h*.86} ${x+w*.86},${y+h} ${x+w*.62},${y+h} L${x+w*.38},${y+h}
  C${x+w*.14},${y+h} ${x},${y+h*.86} ${x},${y+h*.48} L${x},${y+r} Q${x},${y} ${x+r},${y} Z`;}
function SG3(w,o={}){
  const p='g3'+(o.id||N++), fold=!!o.fold, on=o.led!==false&&!fold;
  // 렌즈 안쪽(유리) / 테 바깥 — 위는 두껍게(18), 옆 15, 아래 11
  const LI=[50,68,136,96], RI=[234,68,136,96];
  const out=([x,y,ww,hh])=>lens(x-15,y-18,ww+30,hh+29,ww*.2);
  const inn=([x,y,ww,hh])=>lens(x,y,ww,hh);
  const rim=a=>out(a)+' '+inn(a);
  const tort=[[30,60,16],[70,52,12],[120,50,10],[176,58,14],[34,120,12],[60,168,14],[130,172,12],[188,140,10],
              [246,52,12],[300,50,14],[352,56,12],[392,92,14],[388,150,12],[330,172,14],[262,170,10],[232,120,9]];
  return `<svg viewBox="0 0 420 210" width="${w}" height="${w*210/420}" style="overflow:visible">
<defs>
 <linearGradient id="${p}f" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="180"><stop offset="0" stop-color="#6A4B37"/><stop offset=".35" stop-color="#4A3226"/><stop offset="1" stop-color="#24170F"/></linearGradient>
 <linearGradient id="${p}t" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="70"><stop offset="0" stop-color="#2A1C14"/><stop offset="1" stop-color="#4E3627"/></linearGradient>
 <linearGradient id="${p}gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EAF5FF" stop-opacity=".55"/><stop offset=".5" stop-color="#BFD9F0" stop-opacity=".22"/><stop offset="1" stop-color="#7FA6CC" stop-opacity=".38"/></linearGradient>
 <linearGradient id="${p}rf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <radialGradient id="${p}cl" cx=".35" cy=".32" r=".75"><stop offset="0" stop-color="#6C7FA6"/><stop offset=".4" stop-color="#1F2536"/><stop offset="1" stop-color="#07090E"/></radialGradient>
 <linearGradient id="${p}mt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F5F8"/><stop offset=".55" stop-color="#9DA2AE"/><stop offset="1" stop-color="#5E6370"/></linearGradient>
 <radialGradient id="${p}lg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#E9FCFF"/><stop offset=".35" stop-color="#7DE6FF" stop-opacity=".9"/><stop offset="1" stop-color="#7DE6FF" stop-opacity="0"/></radialGradient>
 <radialGradient id="${p}sh" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#3E2F25" stop-opacity=".32"/><stop offset="1" stop-color="#3E2F25" stop-opacity="0"/></radialGradient>
 <filter id="${p}b2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2"/></filter>
 <filter id="${p}b1" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1"/></filter>
 <clipPath id="${p}cf"><path d="${rim(LI)} ${rim(RI)}" clip-rule="evenodd"/><path d="M18,56 Q16,44 28,42 L48,40 L48,84 L30,84 Q18,84 18,72Z M402,56 Q404,44 392,42 L372,40 L372,84 L390,84 Q402,84 402,72Z"/></clipPath>
 <clipPath id="${p}cl2"><path d="${inn(LI)}"/><path d="${inn(RI)}"/></clipPath>
</defs>
<!-- 바닥 그림자 -->
<ellipse cx="210" cy="196" rx="196" ry="12" fill="url(#${p}sh)"/>
<ellipse cx="118" cy="186" rx="80" ry="6" fill="#3E2F25" opacity=".18" filter="url(#${p}b2)"/>
<ellipse cx="302" cy="186" rx="80" ry="6" fill="#3E2F25" opacity=".18" filter="url(#${p}b2)"/>
${fold?'':`<!-- 다리: 위에서 내려다봐 뒤로(위로) 뻗는다, 끝은 귀걸이 곡선 -->
<path d="M26,54 C34,32 64,16 106,10 L114,10 Q120,12 114,16 L106,18 C70,24 46,38 40,58 Z" fill="url(#${p}t)" stroke="${K}" stroke-width="3" stroke-linejoin="round"/>
<path d="M394,54 C386,32 356,16 314,10 L306,10 Q300,12 306,16 L314,18 C350,24 374,38 380,58 Z" fill="url(#${p}t)" stroke="${K}" stroke-width="3" stroke-linejoin="round"/>
<path d="M46,30 C62,20 80,16 98,13" stroke="#fff" stroke-width="2" opacity=".25" fill="none" stroke-linecap="round"/>
<path d="M374,30 C358,20 340,16 322,13" stroke="#fff" stroke-width="2" opacity=".25" fill="none" stroke-linecap="round"/>`}
<!-- 렌즈: 투명한 유리 -->
<g clip-path="url(#${p}cl2)">
 ${fold?`<path d="M30,82 C110,104 200,136 300,150" stroke="#3B281D" stroke-width="13" stroke-linecap="round" fill="none" opacity=".55"/>
 <path d="M390,82 C310,104 220,136 120,150" stroke="#3B281D" stroke-width="13" stroke-linecap="round" fill="none" opacity=".55"/>`:''}
 <path d="${inn(LI)}" fill="url(#${p}gl)"/><path d="${inn(RI)}" fill="url(#${p}gl)"/>
 ${[LI,RI].map(([x,y,ww,hh])=>`
 <path d="M${x+6},${y+hh*.62} C${x+ww*.08},${y+hh*.2} ${x+ww*.3},${y+6} ${x+ww*.62},${y+8} L${x+ww*.5},${y+hh*.34} C${x+ww*.3},${y+hh*.32} ${x+ww*.16},${y+hh*.44} ${x+12},${y+hh*.7}Z" fill="url(#${p}rf)" opacity=".75" filter="url(#${p}b1)"/>
 <path d="M${x+ww*.7},${y+hh*.98} C${x+ww*.86},${y+hh*.9} ${x+ww*.96},${y+hh*.72} ${x+ww*.98},${y+hh*.5}" stroke="#fff" stroke-width="3.5" fill="none" opacity=".55" stroke-linecap="round"/>
 <path d="M${x+ww*.08},${y+12} Q${x+ww*.16},${y+5} ${x+ww*.3},${y+4}" stroke="#fff" stroke-width="4" fill="none" opacity=".9" stroke-linecap="round"/>`).join('')}
 <!-- 안쪽 깎인 면이 렌즈에 드리우는 그림자 -->
 <path d="${inn(LI)}" fill="none" stroke="#1B110B" stroke-width="7" opacity=".28"/><path d="${inn(RI)}" fill="none" stroke="#1B110B" stroke-width="7" opacity=".28"/>
</g>
<!-- 브리지(키홀) -->
<path d="M196,76 C202,62 218,62 224,76 L224,90 C218,80 202,80 196,90Z" fill="url(#${p}f)" stroke="${K}" stroke-width="3.5" stroke-linejoin="round"/>
<path d="M201,70 C206,66 214,66 219,70" stroke="#fff" stroke-width="2.4" opacity=".4" fill="none" stroke-linecap="round"/>
<!-- 엔드피스(테와 한 몸 — 테보다 먼저 같은 색으로) -->
<path d="M18,56 Q16,44 28,42 L48,40 L48,84 L30,84 Q18,84 18,72Z" fill="url(#${p}f)" stroke="${K}" stroke-width="3.5"/>
<path d="M402,56 Q404,44 392,42 L372,40 L372,84 L390,84 Q402,84 402,72Z" fill="url(#${p}f)" stroke="${K}" stroke-width="3.5"/>
<!-- 테 -->
<path d="${rim(LI)} ${rim(RI)}" fill="url(#${p}f)" fill-rule="evenodd"/>
<path d="M34,52 L50,52 L50,80 L34,80Z M370,52 L386,52 L386,80 L370,80Z" fill="url(#${p}f)"/>
<!-- 거북등 무늬(테 안에만, 흐리게 번진 호박색·검은 반점) -->
<g clip-path="url(#${p}cf)">
 ${tort.map(([x,y,r],i)=>`<ellipse cx="${x}" cy="${y}" rx="${r}" ry="${r*.62}" transform="rotate(${(i*37)%60-30} ${x} ${y})" fill="${i%3?'#B5763A':'#140C07'}" opacity="${i%3?.42:.35}" filter="url(#${p}b2)"/>`).join('')}
 <!-- 안쪽 깎인 면(밝은 띠) -->
 <path d="${inn(LI)}" fill="none" stroke="#C99A6E" stroke-width="3" opacity=".55" transform="translate(0,-1.5)"/>
 <path d="${inn(RI)}" fill="none" stroke="#C99A6E" stroke-width="3" opacity=".55" transform="translate(0,-1.5)"/>
 <!-- 윗면 광택(왼쪽 위 빛) -->
 <path d="M52,54 C86,48 150,48 186,54" stroke="#fff" stroke-width="5" opacity=".42" fill="none" stroke-linecap="round" filter="url(#${p}b1)"/>
 <path d="M234,54 C268,48 332,48 368,54" stroke="#fff" stroke-width="5" opacity=".3" fill="none" stroke-linecap="round" filter="url(#${p}b1)"/>
 <path d="M24,50 Q26,46 34,45" stroke="#fff" stroke-width="3" opacity=".45" fill="none" stroke-linecap="round"/>
 <!-- 아래쪽 어두움 -->
 <path d="M56,176 C92,184 150,184 182,170 M238,170 C270,184 328,184 364,176" stroke="#0E0805" stroke-width="6" opacity=".35" fill="none" stroke-linecap="round" filter="url(#${p}b1)"/>
</g>
<!-- 테 외곽선(한 줄) -->
<path d="${rim(LI)} ${rim(RI)}" fill="none" stroke="${K}" stroke-width="3.5"/>
<!-- 카메라: 왼쪽 엔드피스에 박힌 작은 렌즈 -->
<g transform="translate(32 62)">
 <circle r="10.5" fill="#120C08" opacity=".55"/>
 <circle r="9" fill="url(#${p}mt)" stroke="${K}" stroke-width="1.6"/>
 <circle r="6.6" fill="url(#${p}cl)"/>
 <circle r="2.6" fill="#05070B"/>
 <path d="M-4.6,-1.8 A5,5 0 0 1 -1.2,-4.8" stroke="#A9C1FF" stroke-width="1.3" fill="none" stroke-linecap="round"/>
 <circle cx="-2.4" cy="-2.6" r="1.3" fill="#fff"/>
</g>
<!-- 불빛: 오른쪽 엔드피스 -->
<g class="sgLed"><circle cx="388" cy="62" r="12" fill="url(#${p}lg)" opacity="${on?.85:0}"/>
 <circle cx="388" cy="62" r="3.4" fill="${on?'#D9FAFF':'#6E6258'}" stroke="${K}" stroke-width="1.2"/></g>
</svg>`;}
window.SG3=SG3;
})();
