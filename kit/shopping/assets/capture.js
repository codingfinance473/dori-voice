// capture.js — 브라우저(Claude in Chrome 등)에서 화면의 가격을 기계로 읽어 '증거 기록'(JSON 문자열)을 만든다.
// 사람이 숫자를 옮겨 적지 않기 위한 도구다. 기록에는 주소·읽은 시각·읽은 위치·서명(sig)이 붙고,
// evidence.py 가 서명을 다시 계산해 한 글자라도 바뀌었으면 받지 않는다.
//
// 쓰는 법: 상품 페이지(또는 검색 결과 페이지)를 연 뒤, 이 파일 전체 + 아래 호출 한 줄을 javascript_tool 로 실행한다.
//   await DoriCapture.product({item:'a', side:'local', code:'E461003', currency:'JPY'})   // 상품 페이지
//   await DoriCapture.list({item:'a', side:'kr', code:'E461003', currency:'KRW'})        // 검색 결과 목록(같은 상품번호 카드)
//   await DoriCapture.state({item:'a', side:'local', code:'E461003', currency:'JPY'})       // 같은 상품 페이지의 서버 원본 데이터
//   await DoriCapture.selector({item:'b', side:'kr', kind:'product_page', currency:'KRW', selector:'.final-price', code:'A000123'})
// 한 가격은 '읽는 방식(kind)'이 다른 기록 2개 이상이 같아야 통과한다(예: product_page + server_state, + search_list).
// 나온 문자열을 그대로(고치지 말고) evidence/inbox.jsonl 에 한 줄씩 붙이고 `evidence.py add` 로 넣는다.
(() => {
  const SALE = /(가격\s*인하|기간\s*한정|한정\s*가격|할인|세일|특가|SALE|値下げ|期間限定|限定価格|特価|セール|Clearance|\d+\s*%\s*OFF)/i;
  const num = s => { const m = String(s ?? '').replace(/[,\s]/g, '').match(/\d+(?:\.\d+)?/); return m ? Number(m[0]) : null; };
  const vis = e => !!e && e.offsetParent !== null;
  // 서명 v2: 가격 칸에 더해 할인·세금 판정에 쓰는 칸(sale_flag·promo·tax_policy·price_flags)까지 묶는다.
  async function sign(r) {
    const f = [r.item, r.side, r.kind, r.url, r.code, r.price, r.currency, r.captured_at];
    if ((r.v || 1) >= 2) f.push(r.sale_flag, r.promo, r.tax_policy, r.price_flags);
    const canon = f.join('|');
    const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canon));
    return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 16);
  }
  function base(o, kind) {
    const now = new Date();
    return { v: 2, item: o.item, side: o.side, kind, code: o.code || '', currency: o.currency,
      url: location.origin + location.pathname, page_title: document.title.slice(0, 120),
      captured_at: now.toISOString(), tz_offset_min: -now.getTimezoneOffset(), method: 'browser-dom' };
  }
  async function finish(r) { r.sig = await sign(r); return JSON.stringify(r); }
  function boxText(el) {
    if (!el) return '';
    let b = el; for (let i = 0; i < 5 && b.parentElement; i++) b = b.parentElement;
    return b.innerText.replace(/\s+/g, ' ').trim().slice(0, 300);
  }
  window.DoriCapture = {
    // 상품 페이지: 큰 가격 표시 하나를 읽는다(유니클로 기본 선택자). 보이는 가격 요소가 여러 개면 n_matches 로 남긴다.
    async product(o) {
      const sel = o.selector || '.fr-ec-price-text--large';
      const els = [...document.querySelectorAll(sel)].filter(vis);
      const el = els[0];
      const r = base(o, 'product_page');
      Object.assign(r, { selector: sel, n_matches: els.length, price_text: el ? el.innerText.trim() : null, price: el ? num(el.innerText) : null });
      r.price_box = boxText(el);
      r.sale_flag = SALE.test(r.price_box);
      r.heading = ((document.querySelector('h1') || {}).innerText || '').trim().slice(0, 80);
      r.code_in_url = o.code ? location.pathname.includes(o.code) : null;
      return finish(r);
    },
    // 검색 결과 목록: 같은 상품번호의 기본 카드(…/products/{code}-000/00)에서 가격을 읽는다.
    async list(o) {
      const want = `/products/${o.code}-000/00`;
      const a = [...document.querySelectorAll('a[href*="/products/"]')].find(x => x.getAttribute('href').split('?')[0].endsWith(want));
      const t = a ? a.innerText.replace(/\s+/g, ' ') : '';
      const m = t.match(/[¥₩$€]\s?[\d,]+(?:\.\d+)?|[\d,]+\s?원/);
      const r = base(o, 'search_list');
      Object.assign(r, { selector: `a[href$="${want}"]`, card_text: t.slice(0, 200), price_text: m ? m[0] : null, price: m ? num(m[0]) : null,
        sale_flag: SALE.test(t), code_in_url: !!a });
      return finish(r);
    },
    // 서버 원본 데이터: 지금 페이지 주소를 다시 받아(번역·화면 꾸밈 전의 HTML) 안에 든 상품 데이터(__PRELOADED_STATE__)에서
    // 정가(base)·할인가(promo)·세금 포함 여부를 읽는다. 크롬 자동 번역이 화면 글자를 바꿔도 영향을 받지 않는다.
    // 같은 상품번호 노드가 여러 개인데 값이 다르면 price 를 비워 받지 않게 한다.
    async state(o) {
      const res = await fetch(location.pathname, { credentials: 'omit', cache: 'no-store' });
      const html = await res.text();
      const r = base(o, 'server_state');
      r.method = 'page-refetch';
      let st = null, perr = null;
      const k = html.indexOf('__PRELOADED_STATE__');
      if (k >= 0) {
        const s = html.indexOf('{', k);
        let depth = 0, inStr = false, esc = false, e = -1;
        for (let i = s; i < html.length; i++) {
          const c = html.charCodeAt(i);
          if (inStr) { if (esc) esc = false; else if (c === 92) esc = true; else if (c === 34) inStr = false; continue; }
          if (c === 34) inStr = true; else if (c === 123) depth++; else if (c === 125 && --depth === 0) { e = i; break; }
        }
        try { st = JSON.parse(html.slice(s, e + 1)); } catch (x) { perr = String(x).slice(0, 80); }
      } else perr = 'no __PRELOADED_STATE__';
      const hits = [], seen = new Set();
      (function walk(n, d) {
        if (!n || typeof n !== 'object' || d > 60 || seen.has(n)) return; seen.add(n);
        if (typeof n.productId === 'string' && o.code && n.productId.startsWith(o.code) && n.prices && n.prices.base) hits.push(n);
        for (const v of Object.values(n)) walk(v, d + 1);
      })(st, 0);
      const pick = h => (o.promo && h.prices.promo ? h.prices.promo.value : h.prices.base.value);
      const vals = [...new Set(hits.map(pick))];
      const h = hits[0], p = h ? h.prices : null;
      Object.assign(r, {
        source: '__PRELOADED_STATE__', http_status: res.status, parse_error: perr, n_matches: hits.length, distinct_values: vals,
        price: vals.length === 1 ? vals[0] : null, price_basis: o.promo ? 'promo' : 'base',
        price_currency: p && p.base.currency ? p.base.currency.code : null,
        promo: p && p.promo ? (p.promo.value ?? JSON.stringify(p.promo).slice(0, 60)) : null,
        dual_price: p ? !!p.isDualPrice : null,
        tax_policy: p ? (p.taxPolicy || h.taxPolicy || null) : null,
        price_flags: h && h.flags && Array.isArray(h.flags.priceFlags) ? h.flags.priceFlags.map(f => String(f.name || f.code)).slice(0, 5) : [],
        heading: h ? String(h.name || '').slice(0, 80) : '',
        code_in_url: o.code ? location.pathname.includes(o.code) : null,
      });
      r.sale_flag = !o.promo && (r.promo !== null || r.price_flags.length > 0 || r.dual_price === true);
      return finish(r);
    },
    // 제도·규정 원문: 공식 페이지의 원본 HTML(번역 전)에서 찾을 문구(needles)를 찾아 앞뒤 문맥을 남긴다.
    // 전각·반각 차이는 NFKC 로 맞춘다. 문구·문맥은 서명에 들어가는 code 칸(문맥 해시)으로 묶인다.
    //   await DoriCapture.quote({id:'tax', needles:['2026年11月1日購入分から', '90日以内', '5,000円以上']})
    // 한 기록에 문구 3개까지(도구 출력이 길면 잘려 서명이 사라진다). 더 있으면 id 를 나눠 여러 번 읽는다.
    async quote(o) {
      const res = await fetch(location.href, { credentials: 'omit', cache: 'no-store' });
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      doc.querySelectorAll('script,style,noscript').forEach(e => e.remove());
      const text = (doc.body ? doc.body.textContent : '').normalize('NFKC').replace(/\s+/g, ' ');
      const quotes = (o.needles || []).map(n0 => {
        const n = String(n0).normalize('NFKC'), i = text.indexOf(n);
        return { needle: n, found: i >= 0, context: i >= 0 ? text.slice(Math.max(0, i - 60), i + n.length + 60).trim() : '' };
      });
      const r = base({ item: o.id, side: 'rule', code: '', currency: '' }, 'rule_quote');
      Object.assign(r, { method: 'page-refetch', http_status: res.status, quotes, price: null });
      const qb = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(quotes.map(q => q.needle + '\u0001' + q.context).join('\u0002')));
      r.code = [...new Uint8Array(qb)].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 16);
      return finish(r);
    },
    // 그 밖의 사이트: 가격이 든 요소의 CSS 선택자를 직접 준다.
    async selector(o) {
      const els = [...document.querySelectorAll(o.selector)].filter(vis);
      const el = els[0];
      const r = base(o, o.kind || 'product_page');
      Object.assign(r, { selector: o.selector, n_matches: els.length, price_text: el ? el.innerText.trim() : null, price: el ? num(el.innerText) : null });
      r.price_box = boxText(el);
      r.sale_flag = SALE.test(r.price_box);
      r.heading = ((document.querySelector('h1') || {}).innerText || '').trim().slice(0, 80);
      r.code_in_url = o.code ? (location.pathname + location.search).includes(o.code) : null;
      return finish(r);
    }
  };
})();
