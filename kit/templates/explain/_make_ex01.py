"""설명형(퀴즈 없음) 화면 만들기 — 반도체 수출, 꺾였나? (2026-11-01)
퀴즈 템플릿(EP.09)에서 머리·도리·말풍선은 그대로 두고 장면·장면 JS·도리 연기 표만 바꾼다."""
from pathlib import Path
p = Path('index.html'); s = p.read_text(encoding='utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a)); s = s.replace(a, b)
def cut(start, end, new, keep_end=True):
    global s
    i = s.index(start); j = s.index(end, i); s = s[:i] + new + s[j:]

rep('<title>도리의 숫자 퀴즈 나라 예산</title>', '<title>도리의 숫자 검산 반도체 수출</title>')
rep('<i style="background:var(--mint)"></i>숫자 퀴즈</div>', '<i style="background:#5B8CFF"></i>숫자 검산</div>')

# ---------- 장면 ----------
MON = [205.4, 251.4, 328.3, 318.9, 371.6, 448.1, 410.1, 466.5, 603.0, 564.4]
GROW = [102.8, 160.6, 151.4, 173.4, 169.4, 199.5, 178.8, 209.1, 262.8, 259.4]
DDR = [('4월', 35.0), ('5월', 37.5), ('6월', 40.0), ('7월', 45.0), ('8월', 46.5), ('9월', 48.0), ('10월', 50.0)]
cut('  <!-- 1 훅 -->', '  <div id="conf"', '''  <!-- 1 질문 -->
  <div class="scene" id="s1">
    <div class="ttl" id="t1"><span>반도체 수출,</span><span>이제</span><span><em>꺾였을까?</em></span></div>
    <div class="abs" id="bottle"></div>
    <div class="card" id="c1"><div class="k">10월 반도체 수출</div><div class="v">564.4억<small> 달러</small></div><div class="k" style="margin-top:8px">9월 603.0억 달러 → <b style="color:var(--red)">6.4% 줄어듦</b></div></div>
    <div class="src" id="src1">산업통상부 · 2026년 9~10월 수출입 동향</div>
  </div>

  <!-- 2 월별 -->
  <div class="scene" id="s2">
    <div class="ttl" id="t2">달마다 보면</div>
    <div class="unit" id="t2s">산업통상부 · 2026년 월별 반도체 수출(억 달러)</div>
    <div class="card" id="cm" style="left:50px;top:450px;width:880px;height:600px"></div>
    <div id="mbars"></div>
    <div class="abs xtag" id="xt1" style="left:90px;top:478px">3·6·9월 ▲ 확 늘고</div>
    <div class="abs xtag dn" id="xt2" style="left:90px;top:540px">다음 달 ▼ 조금 줄고</div>
    <div class="abs xtag rec" id="xt3" style="left:90px;top:602px">★ 그다음엔 다시 최고</div>
  </div>

  <!-- 3 증가율 -->
  <div class="scene" id="s3">
    <div class="ttl" id="t3">작년보다 얼마나?</div>
    <div class="unit" id="t3s">산업통상부 · 전년 같은 달 대비 반도체 수출 증가율</div>
    <div class="card" id="gA" style="left:60px;top:450px;width:420px;height:380px"><div class="y">9월</div><div class="pc">+262.8%</div><div class="nt">작년의 약 3.6배</div></div>
    <div class="card" id="gB" style="left:500px;top:450px;width:420px;height:380px"><div class="y">10월</div><div class="pc" style="color:var(--mint)">+259.4%</div><div class="nt">작년의 약 3.6배</div></div>
    <svg class="abs" id="gsp" width="860" height="170" style="left:60px;top:860px;overflow:visible"></svg>
  </div>

  <!-- 4 하루 평균 -->
  <div class="scene" id="s4">
    <div class="ttl" id="t4">하루 평균으로 보면</div>
    <div class="unit" id="t4s">월 수출 ÷ 조업일수(계산) · 10월 일수는 전체 수출 ÷ 일평균 수출</div>
    <div class="card" id="cd" style="left:60px;top:450px;width:860px;height:560px"></div>
    <div class="ub" id="db0" style="left:200px;width:200px"></div><div class="ub last" id="db1" style="left:580px;width:200px"></div>
    <div class="dv" id="dv0" style="left:150px">28.0억</div><div class="dv" id="dv1" style="left:530px">약 25.7억</div>
    <div class="dy" id="dy0" style="left:150px">9월 · 21.5일</div><div class="dy" id="dy1" style="left:530px">10월 · 약 22일</div>
    <div class="abs" id="dcut">약 8% ↓</div>
  </div>

  <!-- 5 메모리 값 -->
  <div class="scene" id="s5">
    <div class="ttl" id="t5">메모리 값은?</div>
    <div class="unit" id="t5s">산업통상부 인용 · D램(DDR5 16Gb) 고정가격(달러)</div>
    <div class="card" id="cp" style="left:60px;top:450px;width:860px;height:560px"></div>
    <div id="pbars"></div>
  </div>

  <!-- 6 정리 -->
  <div class="scene" id="s6">
    <div class="card" id="c8" style="height:720px;padding-top:44px"><div class="stk">정리</div>
      <div class="sum" style="margin-top:30px">꺾였다고 보긴 <b>아직 일러</b></div>
      <div class="chk" id="k1">✔ 3·6·9월 뒤엔 늘 조금 줄었다가 다시 최고</div>
      <div class="chk" id="k2">✔ 증가율 9월 262.8% → 10월 259.4%</div>
      <div class="chk" id="k3">✔ D램 값 10월에도 올라 50달러</div>
      <div class="chk warn" id="k4">△ 하루 평균은 9월보다 약 8% 줄어듦</div>
      <div class="per" style="margin-top:22px">11월 수출입 동향 발표: 12월 1일</div></div>
    <div class="abs" id="stamp8" style="top:900px">검산 끝!</div>
  </div>

  <!-- 7 질문 -->
  <div class="scene" id="s9">
    <div class="ttl" id="e1">너는 다음 달에<br>늘 것 같아, 줄 것 같아?</div>
  </div>

''')
rep('/* EP.09 증가율 막대 */', '''/* 설명형 */
.xtag{font-family:Jua;font-size:38px;color:var(--mint);background:#EAF7F2;border-radius:14px;padding:4px 16px}
.xtag.dn{color:var(--red);background:#FDECEA}
.xtag.rec{color:#B7791F;background:#FFF4D6}
.mb{position:absolute;width:62px;border-radius:14px 14px 6px 6px;background:linear-gradient(180deg,#CFEDE3,#9BD9C6)}
.mb.pk{background:linear-gradient(180deg,#7FD3BC,var(--mint))}
.mb.dp{background:linear-gradient(180deg,#F8C9C2,#EE8C7F)}
.mv{position:absolute;width:90px;text-align:center;font-size:24px;font-weight:800;color:var(--ink)}
.mm{position:absolute;width:90px;text-align:center;font-size:26px;font-weight:700;color:var(--sub)}
.star{position:absolute;font-size:34px;color:#E5A823;width:62px;text-align:center}
#gA .y,#gB .y{font-family:Jua;font-size:50px;text-align:center;margin-top:40px;color:var(--sub)}
#gA .pc,#gB .pc{font-size:100px;font-weight:900;text-align:center;margin-top:30px;letter-spacing:-3px}
#gA .nt,#gB .nt{font-size:34px;font-weight:700;text-align:center;margin-top:24px;color:var(--sub)}
.dv{position:absolute;width:300px;text-align:center;font-size:52px;font-weight:900}
.dy{position:absolute;width:300px;text-align:center;font-size:30px;font-weight:700;color:var(--sub)}
#dcut{left:640px;top:520px;font-family:Jua;font-size:64px;color:var(--red)}
.pb{position:absolute;width:76px;border-radius:14px 14px 6px 6px;background:linear-gradient(180deg,#D8E4FF,#9DB6F2)}
.pb.last{background:linear-gradient(180deg,#8FAAF0,#5B7FE0)}
.pv{position:absolute;width:110px;text-align:center;font-size:30px;font-weight:900}
.pm{position:absolute;width:110px;text-align:center;font-size:28px;font-weight:700;color:var(--sub)}
#c8 .sum{font-family:Jua;font-size:66px}
#c8 .sum b{color:var(--mint);font-weight:400}
#c8 .chk{margin-top:22px;font-size:35px;font-weight:800;color:var(--ink);align-self:flex-start;margin-left:56px}
#c8 .chk.warn{color:#C0563F}
/* EP.09 증가율 막대 */''')

# ---------- 초기화 JS ----------
i = s.index("$('bottle').innerHTML=JAR(200"); j = s.index("$('fly').innerHTML=COIN(60);")
s = s[:i] + f'''$('bottle').innerHTML=CHIP(250);
const MON={MON}, GROW={GROW}, DDR={[[a, b] for a, b in DDR]};
const MX=95, MW=86, MBASE=990, MH=v=>380*v/603;
$('mbars').innerHTML=MON.map((v,i)=>{{const c=[2,5,8].includes(i)?' pk':[3,6,9].includes(i)?' dp':'';
  return `<div class="mb${{c}}" id="mb${{i}}" style="left:${{MX+i*MW}}px"></div><div class="mv" id="mv${{i}}" style="left:${{MX+i*MW-14}}px">${{Math.round(v)}}</div><div class="mm" style="left:${{MX+i*MW-14}}px;top:${{MBASE+8}}px">${{i+1}}월</div>`;}}).join('')
  +[4,7].map(i=>`<div class="star" id="st${{i}}" style="left:${{MX+i*MW}}px;top:${{MBASE-MH(MON[i])-92}}px">★</div>`).join('');
const PX=150, PW=105, PBASE=960, PH=v=>360*v/50;
$('pbars').innerHTML=DDR.map(([m,v],i)=>`<div class="pb${{i===DDR.length-1?' last':''}}" id="pb${{i}}" style="left:${{PX+i*PW}}px"></div><div class="pv" id="pv${{i}}" style="left:${{PX+i*PW-17}}px">${{v}}</div><div class="pm" style="left:${{PX+i*PW-17}}px;top:${{PBASE+10}}px">${{m}}</div>`).join('');
{{ const W=860,H=150, xs=GROW.map((v,i)=>40+i*(W-80)/9), ys=GROW.map(v=>H-10-(v-90)/(270-90)*(H-30));
  $('gsp').innerHTML=`<text x="0" y="-8" font-size="24" font-weight="700" fill="#7E6B5C">1~10월 증가율 흐름</text><polyline id="gpl" points="${{xs.map((x,i)=>x+','+ys[i]).join(' ')}}" fill="none" stroke="#2E9C83" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>`
   +xs.map((x,i)=>`<circle cx="${{x}}" cy="${{ys[i]}}" r="${{i>=8?11:7}}" fill="${{i>=8?'#E2483A':'#2E9C83'}}" stroke="#fff" stroke-width="3"/><text x="${{x}}" y="${{H+26}}" text-anchor="middle" font-size="22" font-weight="700" fill="#7E6B5C">${{i+1}}월</text>`).join(''); }}
''' + s[j:]
rep("$('fly').innerHTML=COIN(60);", "$('fly').innerHTML=CHIP(60);")
i = s.index('// 도리 픽 동그라미'); j = s.index("$('pre').textContent")
s = s[:i] + s[j:]

# ---------- 도리 연기 표 ----------
i = s.index('const EX='); j = s.index('function renderDori(t){')
s = s[:i] + '''const EX=[[0,{think:.6}],[A('L01',.9),{think:0}],[T.wdrop,{sad:.7}],[A('L02',.98),{sad:0}],
 [T.L03,{think:.4}],[T.wpeak,{think:0,happy:.8}],[T.wdip,{happy:0,surprise:.5}],[A('L04',.97),{surprise:0}],[T.wrec,{happy:1}],[A('L05',.97),{happy:0}],
 [T.L06,{think:.3}],[T.wsame,{think:0,happy:.8}],[A('L07',.97),{happy:0}],
 [T.wday,{think:.7}],[T.w8,{think:0,sad:.8}],[A('L08',.97),{sad:0}],[T.wmore,{surprise:.6}],[A('L09',.97),{surprise:0}],
 [T.wmem,{happy:1}],[A('L10',.97),{happy:0}],
 [T.L11,{think:.4}],[T.wearly,{think:0,squint:1}],[A('L11',.97),{squint:0}],[T.wnov,{surprise:.5}],[A('L12',.97),{surprise:0}],
 [T.L14b,{squint:1}],[T.L15-.47,{squint:0,happy:1}],[T.L15+.03,{happy:0}],[T.L16+.04,{happy:1,pouch:1}]];
const EXS=[];{let cur={happy:0,squint:0,surprise:0,sad:0,think:0,pouch:0};for(const [t,o] of EX){cur={...cur,...o};EXS.push([t,{...cur}]);}}
function expr(t){let res={...EXS[0][1]};for(let i=0;i<EXS.length;i++){const [tt,o]=EXS[i];if(t<tt)break;const k=eIO(P(t,tt,tt>=T.L16?.45:.28));const from=i?EXS[i-1][1]:o;res={};K.forEach(n=>res[n]=lerp(from[n],o[n],k));}return res;}
const GZ=[[0,0,0],[T.L03,.7,-.6],[A('L05',.98),0,0],[T.L06+.1,.7,-.6],[A('L07',.98),0,0],[T.L08+.1,.7,-.5],[A('L09',.98),0,0],[T.L10+.1,.7,-.6],[A('L10',.98),0,0],[T.L11+.08,.5,-.8],[A('L12',.98),0,0]];
function gaze(t){let g=[0,0];for(let i=0;i<GZ.length;i++){if(t<GZ[i][0])break;const k=eIO(P(t,GZ[i][0],.22));const f=i?GZ[i-1]:GZ[i];g=[lerp(f[1],GZ[i][1],k),lerp(f[2],GZ[i][2],k)];}return [g[0]+Math.sin(t*2.1)*.05,g[1]+Math.cos(t*1.7)*.04];}
const BL=[];{const r=rng(23);let t=1.4;while(t<DUR){BL.push(t);if(r()<.2)BL.push(t+.32);t+=2.0+r()*2.6;}}
function blink(t){let v=0;for(const b of BL){const d=t-b;if(d>=0&&d<.2)v=Math.max(v,d<.07?d/.07:d<.11?1:1-(d-.11)/.09);}return v;}
const EF=[];{const r=rng(7);let t=2.8;while(t<DUR){EF.push([t,r()<.5?'L':'R']);t+=3.2+r()*4;}}
function flick(t,side){let v=0;for(const [b,s] of EF){if(s!==side)continue;const d=t-b;if(d>=0&&d<.4)v=Math.max(v,d<.1?d/.1:1-(d-.1)/.3);}return v;}
const HOPS=[[T.wrec,40],[T.wsame,24],[T.wmem,34],[T.L14b,70],[T.L16+.04,30]];
function hop(t){let h=0,sq=0;for(const [s,H] of HOPS){const d=t-s;
  if(d>=-.1&&d<0)sq=Math.max(sq,(d+.1)/.1*.55); else if(d>=0&&d<.42){const k=d/.42;h=Math.max(h,Math.sin(k*Math.PI)*H);sq=Math.min(sq,-.3*Math.sin(k*Math.PI));} else if(d>=.42&&d<.58)sq=Math.max(sq,.45*(1-(d-.42)/.16));}
  return [h,sq];}
const ARMR=[[0,0],[A('L01',.2),.35],[A('L01',.6),0],[T.L03+.1,.6],[A('L05',.9),0],[T.L06+.1,.4],[A('L07',.9),0],[T.L08+.1,.5],[A('L09',.9),0],[T.wmem,.8],[T.wmem+1.0,0],[T.L11+.1,.4],[A('L12',.9),0],[T.L14b,.95],[T.L14b+1.17,0],[T.L15+.13,.5],[T.L15+1.43,0],[A('L16',.4),.9]];
const ARML=[[0,0],[T.wrec,.7],[T.wrec+.9,0],[T.wmem,.55],[T.wmem+.9,0],[T.L14b,.95],[T.L14b+1.17,0],[T.L16+.04,.55],[T.L16+.89,0]];
function arm(Kf,t){let v=0;for(let i=0;i<Kf.length;i++){if(t<Kf[i][0])break;const k=eIO(P(t,Kf[i][0],.24));v=lerp(i?Kf[i-1][1]:0,Kf[i][1],k);}return v;}
function marks(t){const on=(a,b)=>clamp(P(t,a,.16))*(1-P(t,b-.22,.22));let m=null,o=0;
  for(const [a,b] of [[T.wrec,T.wrec+1.1],[T.wnov,T.wnov+1.1]]){const v=on(a,b);if(v>o){o=v;m='!';}}
  for(const [a,b] of [[.2,A('L01',.95)],[T.wday-.1,T.w8]]){const v=on(a,b);if(v>o){o=v;m='?';}}
  return [m,o];}
''' + s[j:]
rep("const sweat=clamp(P(t,T.i2,.3))*(1-P(t,T.L12-.27,.3));", "const sweat=clamp(P(t,T.w8,.3))*(1-P(t,T.L10-.27,.3));")
rep("const spark=Math.max(clamp(P(t,T.best,.2))*(1-P(t,T.best+1.4,.3)),clamp(P(t,T.w95,.2))*(1-P(t,T.w95+1.2,.3)),", "const spark=Math.max(clamp(P(t,T.wrec,.2))*(1-P(t,T.wrec+1.4,.3)),clamp(P(t,T.wmem,.2))*(1-P(t,T.wmem+1.2,.3)),")
rep("*(1-P(t,T.L10,1));", "*(1-P(t,T.wnov,1));")

# ---------- 장면 JS ----------
i = s.index('  // 1\n'); j = s.index('  // 9\n')
s = s[:i] + '''  // 1 질문
  sv('s1',0,T.s2+.4); const o1=T.s2-.1;
  document.querySelectorAll('#t1 span').forEach((el,i)=>fx(el,t,[.2,.7,1.2][i],.45,o1,.4,46));
  const gk=P(t,.5,.6), gb=eIO(P(t,o1,.4)); $('bottle').style.opacity=clamp(gk*3)*(1-gb);
  $('bottle').style.transform=`translateY(${-gb*30}px) scale(${gk<=0?.6:.6+.4*eBack(gk)}) rotate(${Math.sin(t*1.3)*2.5}deg)`;
  fx('c1',t,T.L02,.45,o1,.4,40); fx('src1',t,T.L02+.3,.4,o1,.4,20);

  // 2 월별
  sv('s2',T.s2,T.s3+.3); const o2=T.s3-.1;
  fx('t2',t,T.s2+.05,.45,o2,.35,40); fx('t2s',t,T.s2+.2,.4,o2,.35,20); fx('cm',t,T.s2+.15,.5,o2,.35,40);
  MON.forEach((v,i)=>{const s0=T.L03+.2+i*.16, g=spring(P(t,s0,.8)), b=eIO(P(t,o2,.35)), h=MH(v)*clamp(g,0,1.06), el=$('mb'+i);
    el.style.height=Math.max(0,h)+'px'; el.style.top=(MBASE-h)+'px'; el.style.opacity=(t>=s0?1:0)*(1-b);
    const hi=[2,5,8].includes(i)?P(t,T.wpeak+[0,.35,.7][[2,5,8].indexOf(i)],.4):[3,6,9].includes(i)?P(t,T.wdip,.4):0;
    el.style.transform=`scaleX(${1+.12*Math.sin(clamp(hi)*Math.PI)})`;
    const mv=$('mv'+i); mv.style.top=(MBASE-h-34)+'px'; mv.style.opacity=clamp((P(t,s0,.8)-.4)*2)*(1-b);});
  [4,7].forEach(i=>pop('st'+i,t,T.wrec+(i===7?.25:0),o2,.35,0,.4));
  pop('xt1',t,T.wpeak,o2,.35,-2,.6); pop('xt2',t,T.wdip,o2,.35,-2,.6); pop('xt3',t,T.wrec,o2,.35,-2,.6);

  // 3 증가율
  sv('s3',T.s3,T.s4+.3); const o3=T.s4-.1;
  fx('t3',t,T.s3+.05,.45,o3,.35,40); fx('t3s',t,T.s3+.2,.4,o3,.35,20);
  fx('gA',t,T.L06+.1,.45,o3,.35,40); fx('gB',t,T.L06+.5,.45,o3,.35,40);
  fx('gsp',t,T.L07,.45,o3,.35,30);
  { const pl=$('gpl'), L=pl.getTotalLength(); pl.style.strokeDasharray=L; pl.style.strokeDashoffset=L*(1-eOut(P(t,T.L07,1.2))); }

  // 4 하루 평균
  sv('s4',T.s4,T.s5+.3); const o4=T.s5-.1;
  fx('t4',t,T.s4+.05,.45,o4,.35,40); fx('t4s',t,T.s4+.2,.4,o4,.35,20); fx('cd',t,T.s4+.15,.5,o4,.35,40);
  [[28.0,T.wday],[25.65,T.wday+.5]].forEach(([v,s0],i)=>{const g=spring(P(t,s0,.9)), b=eIO(P(t,o4,.35)), h=380*v/28*clamp(g,0,1.06);
    $('db'+i).style.height=Math.max(0,h)+'px'; $('db'+i).style.top=(960-h)+'px'; $('db'+i).style.opacity=(t>=s0?1:0)*(1-b);
    $('dv'+i).style.top=(960-h-70)+'px'; $('dv'+i).style.opacity=clamp((P(t,s0,.9)-.3)*2)*(1-b);
    $('dy'+i).style.top='975px'; $('dy'+i).style.opacity=clamp(P(t,s0,.4))*(1-b);});
  pop('dcut',t,T.w8,o4,.35,-6,.5);

  // 5 메모리 값
  sv('s5',T.s5,T.s6+.3); const o5=T.s6-.1;
  fx('t5',t,T.s5+.05,.45,o5,.35,40); fx('t5s',t,T.s5+.2,.4,o5,.35,20); fx('cp',t,T.s5+.15,.5,o5,.35,40);
  DDR.forEach(([m,v],i)=>{const s0=T.L10+.1+i*.18, g=spring(P(t,s0,.8)), b=eIO(P(t,o5,.35)), h=PH(v)*clamp(g,0,1.06), el=$('pb'+i);
    el.style.height=Math.max(0,h)+'px'; el.style.top=(PBASE-h)+'px'; el.style.opacity=(t>=s0?1:0)*(1-b);
    const pv=$('pv'+i); pv.style.top=(PBASE-h-42)+'px'; pv.style.opacity=clamp((P(t,s0,.8)-.4)*2)*(1-b);});

  // 6 정리
  sv('s6',T.s6,T.s9+.3); const o6=T.s9-.1;
  fx('c8',t,T.s6+.05,.5,o6,.35,50);
  ['k1','k2','k3','k4'].forEach((id,i)=>fx(id,t,T.wearly+.1+i*.35,.4,null,0,20,-30));
  const sk=P(t,T.stamp-.12,.3), sb=eIO(P(t,o6,.35)); $('stamp8').style.opacity=clamp(sk*5)*(1-sb);
  $('stamp8').style.transform=`rotate(-10deg) scale(${sk<=0?2.2:2.2-1.2*eOut(sk)})`;

''' + s[j:]
s = s.replace("  // 9\n  sv('s9',T.s9,99);", "  // 7 질문\n  sv('s9',T.s9,99);")
p.write_text(s, encoding='utf-8'); print('ok')
