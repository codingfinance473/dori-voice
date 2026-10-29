#!/usr/bin/env python3
"""calc.py — 가격 검산 계산기.

episode.json 의 품목마다 현지 가격을 원화로 바꾸고, 용량을 맞춘 한국 가격과 비교해 차이·판정을 낸다.
화면·대사에 쓰는 숫자는 모두 여기서 만든 facts.json 에서만 가져온다.

  python3 calc.py episode.json            → facts.json · facts.md (같은 폴더)

검증 단계(verify):
  strict (웹 조사 편 기본) — evidence/ 의 증거 기록이 evidence.py 규칙을 모두 통과해야 계산한다.
          가격·환율·확인 시각은 증거에서만 가져오고, episode.json 에 적힌 값은 증거와 같은지 대조만 한다.
  draft  — 증거 없이 episode.json 값으로 계산한다(구성 연습용). 화면에 '검증 전 · 올리지 마세요'가 크게 찍힌다.
  receipt (영수증 편 기본) — 영수증·카드 결제액(사진 확인)을 쓴다. 환율 증거가 있으면 함께 표시한다.

돈 계산은 Decimal 로 한다(부동소수 오차 없음). 원화 환산은 round_krw(기본 1원) 단위 반올림(0.5 올림),
퍼센트는 정수 반올림(0.5 올림). 세금·환급처럼 가게 계산 방식·수수료에 따라 달라지는 값은 '약'을 붙이고 10 단위로 둥근다.
"""
import datetime as dt
import json, sys
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

VERDICT = {
    "local": ("현지 이득", "현지에서 사는 게 쌌다"),
    "same": ("비슷해요", "차이가 작아 짐만 늘어난다"),
    "korea": ("그냥 한국에서", "한국에서 사는 게 쌌다"),
    "only": ("현지에서만", "한국 판매처를 찾지 못했다"),
}
DIG = "영일이삼사오육칠팔구"


def _four(n):  # 0~9999 한자어 읽기
    out = ""
    for unit, v in (("천", 1000), ("백", 100), ("십", 10)):
        d = n // v
        n %= v
        if d:
            out += ("" if d == 1 else DIG[d]) + unit
    if n:
        out += DIG[n]
    return out


def ko_num(n):
    """정수를 한글 읽기로: 14900 → '만 사천구백', 1280 → '천이백팔십'."""
    n = int(n)
    if n == 0:
        return "영"
    neg = n < 0
    n = abs(n)
    parts = []
    eok, rest = divmod(n, 100_000_000)
    man, rest = divmod(rest, 10_000)
    if eok:
        parts.append(_four(eok) + "억")
    if man:
        parts.append(("" if man == 1 else _four(man)) + "만")
    if rest:
        parts.append(_four(rest))
    return ("마이너스 " if neg else "") + " ".join(parts)


def sub_num(n):
    """자막용(둥근 글꼴은 쉼표가 마침표처럼 보여 쉼표를 쓰지 않는다): 14900 → '1만 4900', 1280 → '1280'."""
    n = int(n)
    neg = n < 0
    n = abs(n)
    eok, rest = divmod(n, 100_000_000)
    man, rest = divmod(rest, 10_000)
    p = []
    if eok:
        p.append(f"{eok}억")
    if man:
        p.append(f"{man}만")
    if rest or not p:
        p.append(str(rest))
    return ("-" if neg else "") + " ".join(p)


def card_num(n):
    return f"{int(n):,}"


def dec(x):
    return x if isinstance(x, Decimal) else Decimal(str(x))


def rnd(x, unit=1):
    """unit 단위 반올림(0.5 올림, 음수는 절댓값 기준)."""
    u, v = dec(unit), dec(x)
    q = (abs(v) / u).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * u
    return int(q if v >= 0 else -q)


def pct_of(diff, base):
    return rnd(dec(diff) * 100 / dec(base)) if base else 0


def rate_text(sym, rate_per, per):
    """화면용 환율 표기: per 단위 고시값을 그대로(¥100 = ₩846.12)."""
    v = rate_per * per
    s = f"{v:,.2f}" if v < 10000 else f"{v:,.0f}"
    return f"{sym}{per} = ₩{s}"


def mmdd(d):
    try:
        x = dt.date.fromisoformat(str(d)[:10])
        return f"{x.month}/{x.day}"
    except Exception:
        return d or ""


def money(obj, key, n, unit_say, unit_sub, sym="₩"):
    """같은 숫자의 세 가지 표기를 한 번에: key_card(화면) · key_say(읽기) · key_sub(자막)."""
    n = int(n)
    obj[key] = n
    obj[key + "_card"] = f"{sym}{card_num(n)}"
    obj[key + "_say"] = f"{ko_num(abs(n))} {unit_say}".strip()
    obj[key + "_sub"] = f"{sub_num(abs(n))}{unit_sub}"


def load_evidence(ep_dir, ep):
    import evidence
    res = evidence.verify(ep_dir, float(ep.get("max_age_h", 24)))
    for w in res["warnings"]:
        print("증거 주의:", w)
    if not res["ok"]:
        print("증거 검사 실패 — 숫자를 만들지 않는다:")
        for e in res["errors"]:
            print(" -", e)
        print("고친 뒤 다시: python3 scripts/evidence.py check <에피소드>  (구성 연습만 하려면 episode.json 에 \"verify\": \"draft\")")
        sys.exit(1)
    return res


def main(path):
    p = Path(path).resolve()
    ep = json.loads(p.read_text(encoding="utf-8"))
    ep_dir = p.parent
    mode = ep.get("mode", "web")
    vmode = ep.get("verify") or ("strict" if mode == "web" else "receipt")
    if vmode not in ("strict", "draft", "receipt"):
        sys.exit(f"verify 는 strict·draft·receipt 중 하나: {vmode}")
    ev = load_evidence(ep_dir, ep) if vmode == "strict" else None
    if vmode == "receipt" and (ep_dir / "evidence" / "fx.ecos.json").exists() and not (ep.get("fx") or {}).get("card_krw"):
        import evidence
        ev = evidence.verify(ep_dir, float(ep.get("max_age_h", 24 * 30)), write=False)  # 환율만 쓴다
    th = {"local_win": -15, "kr_win": 5, **ep.get("thresholds", {})}
    sym, cko = ep.get("currency_sym", ""), ep.get("currency_ko", "")
    unit = int(ep.get("round_krw", 1))
    rule = ep.get("local_rule") or {}
    tax = rule.get("tax_rate")
    warn = []
    # ---- 환율 ----
    fx_in = ep.get("fx") or {}
    if ev and ev.get("fx"):
        fx = ev["fx"]; per = int(fx["per"]); rate_per = dec(fx["rate"])
        rate = rate_per / per
        basis, rate_date = "매매기준율", f"{fx['date'][:4]}-{fx['date'][4:6]}-{fx['date'][6:]}"
        rate_source, rate_url = "한국은행 ECOS · 서울외국환중개 매매기준율", "https://ecos.bok.or.kr/"
    elif fx_in.get("card_krw") and fx_in.get("local_total"):
        rate = dec(fx_in["card_krw"]) / dec(fx_in["local_total"]); per, rate_per = 1, rate
        basis, rate_date, rate_source, rate_url = "카드 실결제 환율", fx_in.get("date", ep.get("trip_date", "")), "카드 결제 내역", ""
    elif vmode != "strict" and fx_in.get("rate"):
        per = int(fx_in.get("per", 1)); rate_per = dec(fx_in["rate"]); rate = rate_per / per
        basis, rate_date = fx_in.get("basis", "매매기준율"), fx_in.get("date", "")
        rate_source, rate_url = fx_in.get("source", ""), fx_in.get("url", "")
        warn.append("환율이 공식 API 기록이 아니다(draft) — evidence.py fx 로 받는다")
    else:
        sys.exit("환율이 없다 — evidence.py fx 로 공식 환율을 받거나(웹 조사 편), fx.card_krw+local_total(영수증 편)을 적는다")
    tb = (ev or {}).get("time_basis") if vmode == "strict" else None
    today = (tb["last_kst"][:10] if tb else None) or ep.get("check_date") or dt.date.today().isoformat()
    store = ep.get("store", "")

    def short(name):  # 화면 칸이 좁아 가게 이름을 뺀다: '유니클로 일본 공식몰' → '일본 공식몰'
        return name[len(store):].strip() if store and name.startswith(store + " ") else name
    items = []
    for it in ep["items"]:
        loc = it["local"]
        evi = ((ev or {}).get("items") or {}).get(it["id"], {}) if vmode == "strict" else {}
        lp = evi["local"]["price"] if evi else loc["price"]
        f = {"id": it["id"], "role": it.get("role", "best"), "name": it["name"], "code": it.get("code", ""),
             "local_src": loc.get("source", ""), "local_url": loc.get("url", ""), "tax_free": bool(loc.get("tax_free")),
             "tax_incl": (evi["local"].get("tax_policy") == "INCLUSIVE") if evi and evi["local"].get("tax_policy") else loc.get("tax_incl", True)}
        if evi:
            e = evi["local"]
            f.update({"local_checked": e["last_kst"][:10], "local_time": e["last_kst"][11:], "local_time_label": e["label"],
                      "local_kinds": e["kinds"], "local_n": e["n"], "local_names": e["names"], "local_urls": e["urls"]})
            f["local_url"] = f["local_url"] or e["urls"][0]
        else:
            f.update({"local_checked": loc.get("checked", ""), "local_time": "", "local_time_label": mmdd(loc.get("checked", ""))})
        f["local_checked_md"] = mmdd(f["local_checked"])
        f["local_src_short"] = short(f["local_src"])
        f["local"] = int(lp)
        f["local_card"] = f"{sym}{card_num(lp)}"
        f["local_say"] = f"{ko_num(lp)} {cko}".strip()
        f["local_sub"] = f"{sub_num(lp)}{cko}"
        krw_exact = dec(lp) * rate
        f["krw_exact"] = str(krw_exact.quantize(Decimal("0.001")).normalize())
        money(f, "krw", rnd(krw_exact, unit), "원", "원")
        if mode == "web" and vmode != "strict" and (not loc.get("url") or not loc.get("checked")):
            warn.append(f"{it['id']}: 현지 가격의 출처 주소·확인일이 없다")
        kr = it.get("kr")
        if kr and (kr.get("price") or (evi and evi.get("kr"))):
            kp = evi["kr"]["price"] if evi else kr["price"]
            scale, size_note = Decimal(1), ""
            ls, ks = it.get("size"), kr.get("size")
            if ls and ks and ls.get("q") and ks.get("q"):
                if ls.get("unit") != ks.get("unit"):
                    warn.append(f"{it['id']}: 용량 단위가 다르다({ls.get('unit')} vs {ks.get('unit')}) — 같은 단위로 바꿔 적는다")
                elif ls["q"] != ks["q"]:
                    scale = dec(ls["q"]) / dec(ks["q"])
                    size_note = f"{ks['q']}{ks['unit']}→{ls['q']}{ls['unit']} 환산"
            eq = (dec(kp) + dec(kr.get("shipping", 0))) * scale
            f.update({"kr_price": int(kp), "kr_seller": kr.get("seller", ""), "kr_url": kr.get("url", ""),
                      "kr_taggable": bool(kr.get("taggable")), "size_note": size_note, "kr_shipping": kr.get("shipping", 0)})
            if evi:
                e = evi["kr"]
                f.update({"kr_checked": e["last_kst"][:10], "kr_time": e["last_kst"][11:], "kr_time_label": e["label"],
                          "kr_kinds": e["kinds"], "kr_n": e["n"], "kr_names": e["names"], "kr_urls": e["urls"]})
                f["kr_url"] = f["kr_url"] or e["urls"][0]
                if e.get("tax_policy") not in (None, "INCLUSIVE"):
                    warn.append(f"{it['id']}: 한국 가격이 세금 별도로 표시됐다")
            else:
                f.update({"kr_checked": kr.get("checked", ""), "kr_time": "", "kr_time_label": mmdd(kr.get("checked", ""))})
            f["kr_checked_md"] = mmdd(f["kr_checked"])
            f["kr_seller_short"] = short(f["kr_seller"])
            money(f, "kr_equiv", rnd(eq, unit), "원", "원")
            f["kr_card"], f["kr_say"], f["kr_sub"] = f["kr_equiv_card"], f["kr_equiv_say"], f["kr_equiv_sub"]
            if vmode != "strict" and (not kr.get("checked") or not kr.get("seller")):
                warn.append(f"{it['id']}: 한국 가격의 판매처·확인일이 없다")
            if mode == "web" and not f["kr_url"]:
                warn.append(f"{it['id']}: 한국 가격의 출처 주소가 없다")
            diff = f["krw"] - f["kr_equiv"]
            pct = pct_of(diff, f["kr_equiv"])
            f.update({"diff": diff, "pct": pct})
            f["diff_card"] = ("-" if diff < 0 else "+") + f"₩{card_num(abs(diff))}"
            f["save_say"] = f"{ko_num(abs(diff))} 원"
            f["save_sub"] = f"{sub_num(abs(diff))}원"
            f["pct_card"] = f"{pct:+d}%"
            f["pct_say"] = f"{ko_num(abs(pct))} 퍼센트"
            f["pct_sub"] = f"{abs(pct)}%"
            f["verdict"] = "local" if pct <= th["local_win"] else "korea" if pct >= th["kr_win"] else "same"
        else:
            f.update({"kr_price": None, "kr_equiv": None, "diff": None, "pct": None, "verdict": "only", "kr_taggable": False})
        if vmode != "strict":
            for d_ in (f.get("local_checked"), f.get("kr_checked")):
                try:
                    if d_ and (dt.date.fromisoformat(today) - dt.date.fromisoformat(d_)).days > 7:
                        warn.append(f"{it['id']}: 확인일 {d_} 이 기준일 {today} 보다 7일 넘게 지났다 — 다시 확인")
                except ValueError:
                    pass
        f["stamp"], f["verdict_text"] = VERDICT[f["verdict"]]
        items.append(f)
    comp = [f for f in items if f["kr_equiv"] is not None]
    tl, tk = sum(f["krw"] for f in comp), sum(f["kr_equiv"] for f in comp)
    tot = {"n": len(items), "n_comp": len(comp), "saved_pct": pct_of(tk - tl, tk)}
    money(tot, "local_sum", tl, "원", "원")
    money(tot, "kr_sum", tk, "원", "원")
    money(tot, "saved", tk - tl, "원", "원")
    tot["saved_card"] = ("" if tk >= tl else "-") + f"₩{card_num(abs(tk - tl))}"
    tot["saved_pct_say"] = f"{ko_num(abs(tot['saved_pct']))} 퍼센트"
    loc_sum = sum(f["local"] for f in comp)
    tot["local_sum_local"] = loc_sum
    tot["local_sum_local_card"] = f"{sym}{card_num(loc_sum)}"
    tot["local_sum_local_say"] = f"{ko_num(loc_sum)} {cko}".strip()
    tot["local_sum_local_sub"] = f"{sub_num(loc_sum)}{cko}"
    if tax:
        incl = sum(f["local"] for f in items)
        t_exact = dec(incl) * dec(tax) / (100 + dec(tax))
        pre_lo = int((dec(incl) - t_exact - 1).quantize(Decimal("1"), rounding=ROUND_FLOOR))  # 가게 끝수 처리와 상관없이 이 값 이상
        mn = int(rule.get("refund_min_pretax", 0))
        eligible = pre_lo >= mn
        border = (not eligible) and (dec(incl) - t_exact + 1) >= mn
        if border:
            warn.append(f"면세 기준 경계값(세전 약 {pre_lo}) — 영수증 끝수 처리에 따라 대상 여부가 달라질 수 있어 화면에서 환급 말을 빼거나 품목을 바꾼다")
        tot.update({"tax_incl_local": incl, "tax_incl_local_card": f"{sym}{card_num(incl)}",
                    "tax_approx_local": rnd(t_exact, 10), "tax_approx_local_card": f"약 {sym}{card_num(rnd(t_exact, 10))}",
                    "tax_approx_local_sub": f"약 {sub_num(rnd(t_exact, 10))}{cko}", "tax_approx_local_say": f"약 {ko_num(rnd(t_exact, 10))} {cko}".strip(),
                    "refund_eligible": eligible, "refund_border": border, "refund_min_pretax": mn,
                    "refund_min_card": f"{sym}{card_num(mn)}", "refund_min_sub": f"{sub_num(mn)}{cko}", "refund_min_say": f"{ko_num(mn)} {cko}".strip()})
        ak = rnd(t_exact * rate, 10)
        tot.update({"refund_approx_krw": ak, "refund_approx_krw_card": f"약 ₩{card_num(ak)}",
                    "refund_approx_krw_sub": f"약 {sub_num(ak)}원", "refund_approx_krw_say": f"약 {ko_num(ak)} 원"})
    rc = ep.get("receipt") or {}
    if rc.get("total_local"):
        t = rc["total_local"]
        tot.update({"receipt_total": t, "receipt_total_card": f"{sym}{card_num(t)}",
                    "receipt_total_say": f"{ko_num(t)} {cko}".strip(), "receipt_total_sub": f"{sub_num(t)}{cko}"})
        money(tot, "receipt_krw", rnd(dec(t) * rate, unit), "원", "원")
    # ---- 확인 시각(기준 시각) ----
    if tb:
        loc_t = [f for f in items if f.get("local_kinds")]
        kr_t = [f for f in items if f.get("kr_kinds")]
        import evidence as E_
        def span(fs, side):
            a = min(ev["items"][f["id"]][side]["first"] for f in fs); b = max(ev["items"][f["id"]][side]["last"] for f in fs)
            return E_.time_label(a, b)
        price_time = {"label": tb["label"], "first_kst": tb["first_kst"], "last_kst": tb["last_kst"], "date": tb["last_kst"][:10],
                      "local_label": span(loc_t, "local") if loc_t else "", "kr_label": span(kr_t, "kr") if kr_t else ""}
    elif vmode == "receipt":
        td = ep.get("trip_date", "")
        price_time = {"label": f"{mmdd(td)} 영수증" if td else "", "date": td, "local_label": "", "kr_label": ""}
    else:
        price_time = {"label": f"{mmdd(today)} 확인일(검증 전)", "date": today, "local_label": "", "kr_label": ""}
    # ---- 출처 목록(끝 화면·설명란) ----
    src = []

    def add(kind, name, url, date):
        key = (kind, name, url)
        if name and key not in {(s["kind"], s["name"], s["url"]) for s in src}:
            src.append({"kind": kind, "name": name, "url": url or "", "date": date or ""})
    add("환율", rate_source or basis, rate_url, rate_date)
    for f in items:
        add("현지 가격", f["local_src"], f.get("local_url"), f.get("local_time_label") or f.get("local_checked"))
        if f.get("kr_seller"):
            add("한국 가격", f["kr_seller"], f.get("kr_url"), f.get("kr_time_label") or f.get("kr_checked"))
    lits = (ev or {}).get("literals") or []
    for s_ in (ep.get("sources") or []):
        cap = next((l for l in lits if l["url"] == s_.get("url")), None)
        add(s_.get("kind", "참고"), s_.get("name"), s_.get("url"),
            f"{mmdd(cap['captured_kst'][:10])} {cap['captured_kst'][11:]} 원문 확인" if cap else s_.get("date"))
    facts = {
        "mode": mode, "verify": vmode, "verified": True if vmode == "strict" else ("receipt" if vmode == "receipt" else False),
        "evidence_digest": (ev or {}).get("digest") if vmode == "strict" else None,
        "evidence_checked_at": (ev or {}).get("checked_at") if vmode == "strict" else None,
        "title": ep.get("title", ""), "place": ep.get("place", ""), "store": ep.get("store", ""),
        "check_date": today, "trip_date": ep.get("trip_date", ""), "currency": ep.get("currency", ""), "sym": sym, "cko": cko,
        "round_krw": unit, "rate": str(rate.normalize()), "rate_per": str(rate_per.normalize()), "rate_unit": per,
        "rate_basis": basis, "rate_date": rate_date, "rate_date_md": mmdd(rate_date), "rate_source": rate_source,
        "rate_card": rate_text(sym, rate_per / per, per), "price_time": price_time, "literals": lits,
        "thresholds": th, "items": items, "total": tot, "warnings": warn, "sample": bool(ep.get("sample")),
        "has_tags": any(f.get("kr_taggable") for f in items), "sources": src, "local_rule": rule,
    }
    p.with_name("facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")
    # ---- 대조표 ----
    vtxt = {"strict": "검증 통과(증거 " + str(facts["evidence_digest"]) + ")", "draft": "검증 전(draft) — 올리지 않는다", "receipt": "영수증 편"}[vmode]
    md = [f"# 검산 대조표 — {facts['title']}", "",
          f"- 상태: {vtxt}",
          (f"- 가격 확인: {price_time['label']} (한국 시간) · {facts['place']} {price_time['local_label']} · 한국 {price_time['kr_label']}" if tb
           else f"- 가격 기준: {price_time['label'] or '-'}"),
          f"- 환율: {facts['rate_card']} ({basis}, {rate_date}{', ' + rate_source if rate_source else ''}) · 원화 환산 {unit}원 단위 반올림",
          f"- 판정: 한국가 대비 {th['local_win']}% 이하 현지 이득 · +{th['kr_win']}% 이상 그냥 한국에서 · 그 사이 비슷해요 · 한국 판매처 없음 현지에서만", "",
          "| 품목 | 현지가 | 원화(정확값) | 한국가(용량 맞춤) | 차이 | 판정 |", "|---|---|---|---|---|---|"]
    for f in items:
        md.append(f"| {f['name']} ({f['code']}) | {f['local_card']} | {f['krw_card']} ({f['krw_exact']}) | {f.get('kr_card', '-')} {f.get('size_note', '')} | "
                  f"{f.get('diff_card', '-')} ({f.get('pct_card', '-')}) | {f['stamp']} |")
    md += ["", f"- 비교 가능 {tot['n_comp']}개 합계: 현지 {tot['local_sum_card']}({tot['local_sum_local_card']}) vs 한국 {tot['kr_sum_card']} → {tot['saved_card']} ({tot['saved_pct']}%)"]
    if tax:
        md.append(f"- 면세: 세금 포함 합계 {tot['tax_incl_local_card']} → 세전 {tot['refund_min_card']} 이상 {'대상' if tot['refund_eligible'] else '대상 아님'}"
                  f" · 소비세 {tot['tax_approx_local_card']}({tot['refund_approx_krw_card']}) — 가게 끝수 처리·환급 수수료에 따라 달라 '약'으로 표시")
    if vmode == "strict":
        md += ["", "## 증거(기계로 읽은 기록)", "", "| 품목 | 쪽 | 값 | 읽은 방식 | 기록 수 | 확인 시각(KST) | 주소 |", "|---|---|---|---|---|---|---|"]
        for f in items:
            for side, lab in (("local", facts["place"] or "현지"), ("kr", "한국")):
                e = ev["items"][f["id"]].get(side)
                if e:
                    md.append(f"| {f['name']} | {lab} | {e['currency']} {e['price']:,} | {'·'.join(e['kinds'])} | {e['n']} | {e['label']} | {' '.join(e['urls'])} |")
        fxr = ev["fx"]
        md += ["", f"- 환율 기록: {fxr['source']} · {fxr['date']} · {fxr['per']}{fxr['currency']} = {fxr['rate']}원 · 받은 시각 {fxr['fetched_at'][:19]}Z"
               + (f" · 교차 확인 {fxr['cross_check']['source']} {'일치' if fxr['cross_check']['match'] else '불일치'}" if fxr.get("cross_check") else " · 교차 확인 없음(수출입은행 키 없음)")]
        for l in lits:
            md.append(f"- 제도 숫자 '{l['text']}': {l['url']} ({l['captured_kst']} 원문) — 「{l['context']}」")
        md.append(f"- 검사 시각 {ev['checked_at'][:19]}Z · 기준: 가격은 확인 후 {ev['max_age_h']:g}시간 안에만 영상에 쓴다")
    md += ["", "## 출처"] + [f"- {s_['kind']}: {s_['name']} {s_['date']} {s_['url']}" for s_ in src]
    if warn:
        md += ["", "## 경고"] + [f"- {w}" for w in warn]
    p.with_name("facts.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "episode.json")
