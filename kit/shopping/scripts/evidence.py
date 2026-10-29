#!/usr/bin/env python3
"""evidence.py — 가격·환율·제도 '증거 기록'을 모으고, 영상에 써도 되는지 검사한다.

가격은 사람이 옮겨 적지 않는다. 브라우저에서 capture.js 로 읽은 기록(주소·시각·서명)이나 공식 API 응답만 쓴다.

  python3 evidence.py add    <에피소드> <파일|->     capture.js 결과(JSON 한 줄씩 또는 목록)를 서명 확인 후 저장
                                                     (읽기 실패·서명 불일치 기록은 건너뛰고 알려 준다, 같은 기록은 한 번만)
  python3 evidence.py fx     <에피소드> [--date YYYYMMDD] [--keys 키파일]
                                                     한국은행 ECOS 731Y001(서울외국환중개 매매기준율)을 받아 저장.
                                                     수출입은행 키가 있으면 같은 날 값을 받아 교차 확인한다.
  python3 evidence.py absent <에피소드> <품목id> <확인한 곳·방법> [주소]   한국 판매처가 없다는 확인 기록(현지에서만)
  python3 evidence.py check  <에피소드> [--max-age-h 24] [--now ISO시각]
                                                     규칙 검사 → evidence/verified.json (통과해야 calc.py 가 숫자를 쓴다)
  python3 evidence.py show   <에피소드>

검사 규칙(하나라도 어기면 실패):
  1. 서명이 맞는다(기록이 읽은 그대로다). 제도 원문 기록은 문맥 해시도 맞아야 한다.
  2. 품목의 현지·한국 가격마다 '읽는 방식(kind)'이 다른 기록이 2개 이상이고, 값·통화·상품번호가 모두 같다.
     (product_page 화면 + server_state 서버 원본 + search_list 검색 목록 중 둘 이상. 하나라도 값이 다르면 실패)
  3. 할인 표시가 보이면 실패 — 화면 문구(할인·기간 한정 등), 서버 데이터의 promo·가격 표시 플래그.
     할인가를 쓰려면 품목에 "allow_sale": true 와 기간을 적고 할인가로 다시 읽는다.
  4. 서버 원본의 통화(price_currency)가 기록의 통화와 같다. 세금 포함 여부(tax_policy)가 기록끼리 같고,
     현지 세율을 쓰는 편이면 INCLUSIVE(세금 포함) 여야 한다.
  5. 가장 늦게 읽은 시각이 기준 시각에서 --max-age-h(기본 24시간) 안이다.
  6. 환율은 공식 API 기록(ECOS, 선택: 수출입은행)이 있고, 가격 확인일보다 6일 넘게 앞서지 않으며,
     받은 지 --max-age-h 안이다. 두 곳 다 있으면 값이 같아야 한다.
  7. episode.json 에 가격·환율이 적혀 있으면 증거 값과 같아야 한다(사람이 조사한 값 ↔ 기계로 읽은 값 대조).
  8. episode.json 의 literals(화면에 쓰는 제도 숫자)는 출처 원문 기록에서 찾은 문구가 있어야 한다.
"""
import datetime as dt
import hashlib, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

KST = dt.timezone(dt.timedelta(hours=9))
ECOS_ITEM = {  # 731Y001 주요국 통화의 대원화환율(서울외국환중개 매매기준율)
    "USD": ("0000001", 1), "JPY": ("0000002", 100), "EUR": ("0000003", 1), "GBP": ("0000012", 1), "CAD": ("0000013", 1),
    "CHF": ("0000014", 1), "HKD": ("0000015", 1), "AUD": ("0000017", 1), "SGD": ("0000024", 1), "MYR": ("0000025", 1),
    "NZD": ("0000026", 1), "THB": ("0000028", 1), "IDR": ("0000029", 100), "TWD": ("0000031", 1), "PHP": ("0000034", 1),
    "VND": ("0000035", 100), "CNY": ("0000053", 1),
}
SIG_FIELDS = ("item", "side", "kind", "url", "code", "price", "currency", "captured_at")
SIG_FIELDS_V2 = SIG_FIELDS + ("sale_flag", "promo", "tax_policy", "price_flags")   # v2: 할인·세금 판정 칸도 서명에
PRICE_KINDS = ("product_page", "server_state", "search_list", "selector", "api")
MIN_KINDS = 2
FX_MAX_LAG_DAYS = 6   # 주말·연휴를 넘기는 정도까지만 허용


def sig_of(r):
    def s(v):  # 브라우저 JS 의 Array.join 문자열 변환과 같게(정수는 소수점 없이, null 은 빈칸, true/false, 배열은 쉼표)
        if v is None:
            return ""
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return ",".join(s(x) for x in v)
        return str(v)
    fields = SIG_FIELDS_V2 if (r.get("v") or 1) >= 2 else SIG_FIELDS
    canon = "|".join(s(r.get(k)) for k in fields)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def quotes_hash(quotes):
    return hashlib.sha256("\u0002".join(q["needle"] + "\u0001" + q["context"] for q in quotes).encode("utf-8")).hexdigest()[:16]


def parse_t(s):
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def kst(s):
    return (s if isinstance(s, dt.datetime) else parse_t(s)).astimezone(KST)


def time_label(a, b):
    """'10/24 01:33~01:46' (날짜가 다르면 '10/23 23:50~10/24 00:10')."""
    a, b = kst(a), kst(b)
    left = f"{a.month}/{a.day} {a:%H:%M}"
    if a.date() == b.date():
        return left if a.strftime("%H:%M") == b.strftime("%H:%M") else f"{left}~{b:%H:%M}"
    return f"{left}~{b.month}/{b.day} {b:%H:%M}"


def edir(ep):
    d = Path(ep) / "evidence"; d.mkdir(parents=True, exist_ok=True); return d


def load_keys(path=None):
    keys = dict(os.environ)
    for p in [path, os.environ.get("RS_KEYS")]:
        if p and Path(p).exists():
            for line in Path(p).read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys


def _stored(d):
    out = []
    for p in sorted(d.glob("*.json")):
        if p.name.startswith(("fx.", "verified")):
            continue
        try:
            out.append((p.name, json.loads(p.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            out.append((p.name, {"_broken": True}))
    return out


def cmd_add(ep, src):
    raw = (sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")).strip()
    recs = json.loads(raw) if raw.startswith("[") else [json.loads(l) for l in raw.splitlines() if l.strip()]
    d = edir(ep)
    have = {r.get("sig") for _, r in _stored(d) if r.get("sig")}
    ok = skip = bad = 0
    for r in recs:
        if isinstance(r, str):
            r = json.loads(r)
        rule = r.get("kind") == "rule_quote"
        need = [k for k in (("item", "kind", "url", "captured_at", "sig", "code") if rule
                            else ("item", "side", "kind", "url", "price", "currency", "captured_at", "sig")) if r.get(k) in (None, "")]
        tag = f"{r.get('item')}.{r.get('side')} {r.get('kind')} {r.get('url', '')}"
        if need:
            print(f"받지 않음(읽기 실패 — 빈 칸 {need}): {tag}"); bad += 1; continue
        if sig_of(r) != r["sig"]:
            print(f"받지 않음(서명 불일치 — 기록이 바뀜): {tag} {r.get('price')}"); bad += 1; continue
        if rule:
            if quotes_hash(r.get("quotes") or []) != r["code"]:
                print(f"받지 않음(원문 문맥이 바뀜): {tag}"); bad += 1; continue
            if not all(q.get("found") for q in r["quotes"]):
                print(f"받지 않음(원문에서 못 찾은 문구 있음): {[q['needle'] for q in r['quotes'] if not q.get('found')]}"); bad += 1; continue
        if r["sig"] in have:
            skip += 1; continue
        stamp = kst(r["captured_at"]).strftime("%Y%m%d-%H%M%S")
        name = f"rule.{r['item']}.{stamp}.json" if rule else f"{r['item']}.{r['side']}.{r['kind']}.{stamp}.json"
        (d / name).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        have.add(r["sig"]); ok += 1
        what = f"문구 {len(r['quotes'])}개" if rule else f"{r['currency']} {r['price']}"
        print(f"저장: {name}  {what}  ({kst(r['captured_at']).strftime('%m/%d %H:%M:%S')} KST)"
              + ("  ← 할인 표시 보임" if r.get("sale_flag") else ""))
    print(f"{ok}건 저장 · 이미 있음 {skip}건 · 거부 {bad}건")
    return bad


def http_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "receipt-shorts"}), timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def cmd_fx(ep, date=None, keyfile=None):
    epj = json.loads((Path(ep) / "episode.json").read_text(encoding="utf-8"))
    cur = epj["currency"]
    if cur not in ECOS_ITEM:
        sys.exit(f"ECOS 항목표에 없는 통화: {cur} — ECOS_ITEM 에 추가")
    code, per = ECOS_ITEM[cur]
    keys = load_keys(keyfile)
    key = next((keys[k] for k in ("ECOS_API_KEY", "ECOS_KEY", "BOK_ECOS_KEY", "BOK_API_KEY") if keys.get(k)), "sample")
    end = date or dt.datetime.now(KST).strftime("%Y%m%d")
    start = (dt.datetime.strptime(end, "%Y%m%d") - dt.timedelta(days=12)).strftime("%Y%m%d")
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/10/731Y001/D/{start}/{end}/{code}"
    fetched = dt.datetime.now(dt.timezone.utc).isoformat()
    js = http_json(url)
    if "StatisticSearch" not in js:
        sys.exit(f"ECOS 응답 오류: {json.dumps(js, ensure_ascii=False)[:200]}")
    total = int(js["StatisticSearch"].get("list_total_count") or len(js["StatisticSearch"]["row"]))
    if total > len(js["StatisticSearch"]["row"]):   # 한 번에 10건까지 — 기간 안 영업일이 더 많으면 최근 값이 빠지므로 마지막 쪽을 받는다
        a = max(1, total - 9)
        url = url.replace("/json/kr/1/10/", f"/json/kr/{a}/{total}/")
        js = http_json(url)
        if "StatisticSearch" not in js:
            sys.exit(f"ECOS 응답 오류(마지막 쪽): {json.dumps(js, ensure_ascii=False)[:200]}")
    rows = sorted(js["StatisticSearch"]["row"], key=lambda r: r["TIME"])
    if any(r["TIME"] > end for r in rows):
        sys.exit("ECOS 응답에 요청 기준일보다 늦은 날짜가 있다 — 다시 확인")
    row = rows[-1]
    rec = {"v": 1, "kind": "ecos_api", "source": "한국은행 ECOS 731Y001 주요국 통화의 대원화환율(서울외국환중개 매매기준율)",
           "item_name": row["ITEM_NAME1"], "date": row["TIME"], "rate": float(row["DATA_VALUE"]), "per": per, "currency": cur,
           "url": "https://ecos.bok.or.kr/ (통계표 731Y001, 항목 " + code + ")", "api": url.replace(key, "{KEY}"),
           "key_used": "sample" if key == "sample" else "개인 키", "fetched_at": fetched, "requested_end": end,
           "list_total_count": total, "raw_rows": rows}
    d = edir(ep)
    (d / "fx.ecos.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ECOS 매매기준율 {row['TIME']} {row['ITEM_NAME1']} = {row['DATA_VALUE']}원 (요청 기준일 {end}, 키: {rec['key_used']})")
    ek = next((keys[k] for k in ("EXIM_API_KEY", "KOREAEXIM_API_KEY", "KOREAEXIM_KEY") if keys.get(k)), None)
    if ek:
        try:
            q = urllib.parse.urlencode({"authkey": ek, "searchdate": row["TIME"], "data": "AP01"})
            lst = http_json(f"https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON?{q}")
            want = f"{cur}(100)" if per == 100 else cur
            hit = next((x for x in lst if x.get("cur_unit") == want), None)
            if hit:
                v = float(str(hit["deal_bas_r"]).replace(",", ""))
                (d / "fx.exim.json").write_text(json.dumps({"v": 1, "kind": "exim_api", "source": "한국수출입은행 현재환율 API(매매기준율)",
                    "date": row["TIME"], "rate": v, "per": per, "currency": cur, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat()},
                    ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"수출입은행 매매기준율 {row['TIME']} {want} = {v}원 → {'일치' if abs(v - rec['rate']) < 1e-9 else '불일치!'}")
            else:
                print("수출입은행 응답에 해당 통화가 없다(휴일이면 빈 응답)")
        except Exception as e:  # 교차 확인은 선택
            print(f"수출입은행 교차 확인 실패: {e}")


def cmd_absent(ep, item, how, url=""):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    rec = {"v": 1, "item": item, "side": "kr", "kind": "absent_check", "how": how, "url": url, "captured_at": now}
    (edir(ep) / f"{item}.kr.absent.{kst(now).strftime('%Y%m%d-%H%M%S')}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"한국 판매처 없음 확인 기록: {item} — {how}")


def digest_of(recs, fx):
    h = hashlib.sha256()
    for name, r in sorted(recs, key=lambda x: x[0]):
        h.update(f"{name}|{r.get('sig') or r.get('captured_at')}\n".encode("utf-8"))
    if fx:
        h.update(f"fx|{fx['date']}|{fx['rate']}|{fx['per']}|{fx['currency']}\n".encode("utf-8"))
    return h.hexdigest()[:16]


def verify(ep, max_age_h=24.0, now=None, write=True):
    """규칙 검사 결과(dict)를 돌려준다. 실패해도 예외 없이 ok=False 와 errors 를 담는다."""
    ep = Path(ep)
    epj = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    now_t = parse_t(now) if isinstance(now, str) else (now or dt.datetime.now(dt.timezone.utc))
    recs = _stored(edir(ep))
    errs, warns, items_out, times = [], [], {}, []
    for name, r in recs:
        if r.get("_broken"):
            errs.append(f"{name}: 파일이 깨졌다"); continue
        if r.get("kind") == "absent_check":
            continue
        if sig_of(r) != r.get("sig"):
            errs.append(f"{name}: 서명 불일치(기록이 바뀜)")
        if r.get("kind") == "rule_quote" and quotes_hash(r.get("quotes") or []) != r.get("code"):
            errs.append(f"{name}: 원문 문맥 해시 불일치")
    rule = epj.get("local_rule") or {}
    want_incl = bool(rule.get("tax_rate")) and rule.get("tax_included", True)
    used = []
    for it in epj["items"]:
        iid = it["id"]; items_out[iid] = {}
        sides = ["local"] + (["kr"] if it.get("kr") else [])
        for side in sides:
            rs = [(n, r) for n, r in recs if r.get("item") == iid and r.get("side") == side and r.get("kind") in PRICE_KINDS]
            tag = f"{iid}.{side}"
            if len(rs) < 2:
                errs.append(f"{tag}: 기록 {len(rs)}개 — 읽는 방식이 다른 기록 2개 이상(상품 페이지 + 서버 원본 등) 필요"); continue
            used += rs
            rs = [r for _, r in rs]
            prices = {(r["price"], r["currency"]) for r in rs}
            if len(prices) > 1:
                errs.append(f"{tag}: 기록끼리 값이 다르다 {sorted(prices, key=str)} — 색·사이즈·할인 여부를 확인하고 다시 읽는다"); continue
            kinds = {r["kind"] for r in rs}
            if len(kinds) < MIN_KINDS:
                errs.append(f"{tag}: 읽는 방식이 한 가지({', '.join(kinds)})뿐 — 서버 원본(state)이나 검색 목록(list)으로 한 번 더 읽는다")
            codes = {r.get("code") for r in rs}
            want_code = it.get("code", "")
            if want_code and codes != {want_code}:
                errs.append(f"{tag}: 상품번호가 다르다 {codes} vs {want_code}")
            if any(r.get("code_in_url") is False for r in rs):
                errs.append(f"{tag}: 주소·카드에서 상품번호를 확인하지 못한 기록이 있다")
            if any(r.get("sale_flag") for r in rs) and not it.get("allow_sale"):
                errs.append(f"{tag}: 할인·기간 한정 표시가 보인다 — 정가 비교면 정가 상품으로 다시 읽고, 할인가를 쓰려면 allow_sale 과 기간을 적는다")
            for r in rs:
                if r.get("kind") == "server_state":
                    if r.get("http_status") not in (None, 200):
                        errs.append(f"{tag}: 서버 원본 응답 {r.get('http_status')}")
                    if r.get("price_currency") and r["price_currency"] != r["currency"]:
                        errs.append(f"{tag}: 서버 원본 통화 {r['price_currency']} ≠ 기록 통화 {r['currency']}")
                    if (r.get("n_matches") or 0) != 1:
                        warns.append(f"{tag}: 서버 원본에서 같은 상품 노드 {r.get('n_matches')}개 — 값은 모두 같았다")
                elif (r.get("n_matches") or 1) > 1:
                    warns.append(f"{tag}: 가격 요소가 여러 개 보였다 — 첫 번째를 읽음(다른 방식 기록과 값이 같아 통과)")
            taxp = {r["tax_policy"] for r in rs if r.get("tax_policy")}
            if len(taxp) > 1:
                errs.append(f"{tag}: 세금 포함 여부가 기록끼리 다르다 {taxp}")
            elif taxp and taxp != {"INCLUSIVE"} and (side == "kr" or want_incl):
                errs.append(f"{tag}: 세금 별도 가격({taxp}) — 세금 포함 가격으로 비교해야 한다")
            price, cur = next(iter(prices))
            exp_cur = epj["currency"] if side == "local" else "KRW"
            if cur != exp_cur:
                errs.append(f"{tag}: 통화가 {cur} — {exp_cur} 이어야 한다")
            given = (it.get("local") or {}).get("price") if side == "local" else (it.get("kr") or {}).get("price")
            if given not in (None, "") and float(given) != float(price):
                errs.append(f"{tag}: episode.json 가격 {given} ≠ 증거 {price} — episode.json 의 숫자를 지우거나 증거 값으로 맞춘다")
            ts = sorted(parse_t(r["captured_at"]) for r in rs)
            age_h = (now_t - ts[-1]).total_seconds() / 3600
            if age_h > max_age_h:
                errs.append(f"{tag}: 마지막 확인이 {age_h:.1f}시간 전 — {max_age_h:g}시간 안에 다시 읽는다")
            times += ts
            names = []
            for r in rs:
                h = (r.get("heading") or "").strip()
                if h and h not in names:
                    names.append(h)
            items_out[iid][side] = {"price": price, "currency": cur, "first": ts[0].isoformat(), "last": ts[-1].isoformat(),
                                    "last_kst": kst(ts[-1]).strftime("%Y-%m-%d %H:%M"), "label": time_label(ts[0], ts[-1]),
                                    "urls": sorted({r["url"] for r in rs if r.get("kind") != "search_list"} or {r["url"] for r in rs}),
                                    "kinds": sorted(kinds), "n": len(rs), "tax_policy": next(iter(taxp)) if taxp else None, "names": names[:4]}
        if not it.get("kr"):
            ab = [r for _, r in recs if r.get("item") == iid and r.get("kind") == "absent_check"]
            if not ab:
                errs.append(f"{iid}.kr: 한국 판매처가 없다는 확인 기록이 없다 — evidence.py absent 로 남긴다")
            else:
                items_out[iid]["kr_absent"] = {"how": ab[-1]["how"], "url": ab[-1].get("url", ""), "at": ab[-1]["captured_at"]}
    # 제도 원문(literals)
    rules = {}
    for name, r in recs:
        if r.get("kind") == "rule_quote":
            rules.setdefault(r["item"], []).append(r)
    lit_out = []
    for lit in epj.get("literals") or []:
        rid, needle = lit.get("source"), lit.get("needle")
        cand = rules.get(rid) or []
        if not cand:
            errs.append(f"literal '{lit.get('text')}': 출처 원문 기록 '{rid}' 이 없다 — capture.js quote 로 읽는다"); continue
        r = sorted(cand, key=lambda x: x["captured_at"])[-1]
        q = next((q for q in r["quotes"] if needle and q["needle"] == needle and q["found"]), None)
        if not q:
            errs.append(f"literal '{lit.get('text')}': 원문 기록에 문구 '{needle}' 이 없다"); continue
        lit_out.append({"text": lit["text"], "source": rid, "url": r["url"], "needle": needle, "context": q["context"],
                        "captured_at": r["captured_at"], "captured_kst": kst(r["captured_at"]).strftime("%Y-%m-%d %H:%M")})
    # 환율
    fx = None
    fe = edir(ep) / "fx.ecos.json"
    if not fe.exists():
        errs.append("환율: 공식 기록이 없다 — evidence.py fx 로 한국은행 ECOS 매매기준율을 받는다")
    else:
        fx = json.loads(fe.read_text(encoding="utf-8"))
        if fx["currency"] != epj["currency"]:
            errs.append(f"환율: 통화 {fx['currency']} ≠ 에피소드 {epj['currency']}")
        fxx = edir(ep) / "fx.exim.json"
        if fxx.exists():
            ex = json.loads(fxx.read_text(encoding="utf-8"))
            if ex["date"] == fx["date"] and abs(ex["rate"] - fx["rate"]) > 1e-9:
                errs.append(f"환율: ECOS {fx['rate']} ≠ 수출입은행 {ex['rate']} ({fx['date']}) — 다시 받는다")
            fx["cross_check"] = {"source": ex["source"], "rate": ex["rate"], "match": abs(ex["rate"] - fx["rate"]) < 1e-9}
        fx_age_h = (now_t - parse_t(fx["fetched_at"])).total_seconds() / 3600
        if fx_age_h > max_age_h:
            errs.append(f"환율: 받은 지 {fx_age_h:.1f}시간 — 새 고시가 있을 수 있어 다시 받는다(evidence.py fx)")
        if times:
            d_fx = dt.datetime.strptime(fx["date"], "%Y%m%d").date()
            d_min, d_max = kst(min(times)).date(), kst(max(times)).date()
            if d_fx > d_max:
                warns.append(f"환율 기준일 {fx['date']} 이 가격 확인일보다 늦다 — 같은 날로 맞추면 깔끔하다")
            if (d_min - d_fx).days > FX_MAX_LAG_DAYS:
                errs.append(f"환율 기준일 {fx['date']} 이 가격 확인일보다 {(d_min - d_fx).days}일 앞선다 — 다시 받는다")
        fe_rate = (epj.get("fx") or {}).get("rate")
        if fe_rate not in (None, "") and abs(float(fe_rate) - fx["rate"]) > 1e-9:
            errs.append(f"환율: episode.json {fe_rate} ≠ ECOS {fx['rate']} — episode.json 의 환율을 지우거나 맞춘다")
    if times and (max(times) - min(times)).total_seconds() > 6 * 3600:
        warns.append("가격을 읽은 시각이 6시간 넘게 퍼져 있다 — 한 번에 다시 읽으면 기준 시각이 깔끔해진다")
    fx_out = None
    if fx:
        fx_out = {k: fx[k] for k in ("kind", "source", "date", "rate", "per", "currency", "fetched_at", "url", "key_used") if k in fx}
        if "cross_check" in fx:
            fx_out["cross_check"] = fx["cross_check"]
    out = {"checked_at": now_t.isoformat(), "max_age_h": max_age_h, "ok": not errs, "errors": errs, "warnings": warns,
           "items": items_out, "fx": fx_out, "literals": lit_out,
           "time_basis": ({"first": min(times).isoformat(), "last": max(times).isoformat(),
                           "first_kst": kst(min(times)).strftime("%Y-%m-%d %H:%M"), "last_kst": kst(max(times)).strftime("%Y-%m-%d %H:%M"),
                           "label": time_label(min(times), max(times))} if times else None),
           "digest": digest_of(used + [(n, r) for n, r in recs if r.get("kind") in ("rule_quote", "absent_check")], fx)}
    if write:
        (edir(ep) / "verified.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def cmd_check(ep, max_age_h=24.0, now=None):
    out = verify(ep, max_age_h, now)
    for w in out["warnings"]:
        print("주의:", w)
    if not out["ok"]:
        print("검사 실패:"); [print(" -", e) for e in out["errors"]]
        sys.exit(1)
    tb, fx = out["time_basis"], out["fx"]
    print(f"검사 통과 · 가격 {tb['label']} KST 확인 · 환율 {fx['date']} 매매기준율 {fx['per']}{fx['currency']}={fx['rate']}원"
          + (f" · 제도 원문 {len(out['literals'])}개" if out["literals"] else "") + f" · 증거 {out['digest']}")


def cmd_show(ep):
    for name, r in _stored(edir(ep)):
        if r.get("kind") == "rule_quote":
            print(f"{name:60s} 원문 문구 {len(r.get('quotes', []))}개"); continue
        print(f"{name:60s} {r.get('currency', ''):4s} {r.get('price', '')!s:>8} {'할인표시' if r.get('sale_flag') else ''}")
    for f in ("fx.ecos.json", "fx.exim.json"):
        p = edir(ep) / f
        if p.exists():
            x = json.loads(p.read_text(encoding="utf-8")); print(f"{f}: {x['date']} {x['per']}{x['currency']} = {x['rate']}원")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, ep = a[0], a[1]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if cmd == "add":
        sys.exit(1 if cmd_add(ep, a[2]) else 0)
    elif cmd == "fx":
        cmd_fx(ep, opt("--date"), opt("--keys"))
    elif cmd == "absent":
        cmd_absent(ep, a[2], a[3], a[4] if len(a) > 4 else "")
    elif cmd == "check":
        cmd_check(ep, float(opt("--max-age-h", 24)), opt("--now"))
    elif cmd == "show":
        cmd_show(ep)
    else:
        sys.exit(__doc__)
