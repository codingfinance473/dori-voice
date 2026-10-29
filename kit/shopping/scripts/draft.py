#!/usr/bin/env python3
"""draft.py — 품목·판정이 정해진 episode.json 에서 대사 초안을 만든다(숫자는 모두 자리표시).

  python3 draft.py <에피소드 폴더>        → episode.json 의 lines 를 채운다(이미 있으면 lines_draft 로 따로 둔다)

- 먼저 calc.py 를 돌려 facts.json 이 있어야 한다(판정에 맞는 말을 고른다).
- 문장은 여러 표현 중에서 에피소드 제목을 씨앗으로 골라, 편마다 말투가 조금씩 달라진다.
- 초안일 뿐이다. 훅·반전·마무리는 이 편만의 말로 고쳐 쓴다(같은 틀만 반복하면 유튜브가 대량 생산으로 본다).
- 대사 글자 수로 길이를 어림해 58초를 넘을 것 같으면 알려 준다.
"""
import hashlib, json, random, re, sys
from pathlib import Path

ORD = ["첫 번째", "두 번째", "세 번째", "네 번째", "다섯 번째"]
CIRC = "①②③④⑤"


def syl(t):
    return len(re.sub(r"[^가-힣]", "", t))


def main(epdir):
    ep_dir = Path(epdir)
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    facts = json.loads((ep_dir / "facts.json").read_text(encoding="utf-8"))
    rnd = random.Random(int(hashlib.md5(ep.get("title", "").encode()).hexdigest()[:8], 16))
    pick = lambda xs: rnd.choice(xs)
    place, store = ep.get("place", "현지"), ep.get("store", "")
    F = {f["id"]: f for f in facts["items"]}
    L = []

    def add(scene, say, sub, **kw):
        L.append({"id": f"L{len(L) + 1:02d}", "scene": scene, "say": say, "sub": sub, **kw})

    q = pick([f"{store}, {place}에서 사면 진짜 쌀까?", f"{place} {store}, 한국보다 얼마나 쌀까?", f"{store} {place} 가격, 같이 검산해 볼까?"])
    add("hook", q, q.replace(", ", " | ", 1), expr="focus", arms="hold", cues={"receipt": "^", "total": "진짜" if "진짜" in q else "$"})
    add("hook", pick(["공식몰 가격으로 검산해 볼게!", "두 나라 공식 가격으로 따져 볼게!", "확인한 가격으로 하나씩 볼게!"]),
        "공식 가격으로 검산!", expr="happy", arms="wave")
    for n, it in enumerate(ep["items"]):
        i, f = it["id"], F[it["id"]]
        name = it.get("say_name") or re.sub(r"\(.*?\)", "", it["name"]).strip()
        sc = f"item:{i}"
        v = f["verdict"]
        if n == 0:
            add(sc, f"{name}, {place}은 {{{i}.local_say}}, 원화로 {{{i}.krw_say}}.", f"{CIRC[n]} {it['name']} | {place} {{{i}.local_sub}} = {{{i}.krw_sub}}",
                arms="point", cues={"card": "^", "local": f"{place}은", "krw": "원화로"})
            if v == "local":
                add(sc, f"한국은 {{{i}.kr_say}}. {pick(['볼주머니 행!', '이건 볼주머니에 쏙!', '볼주머니 준비!'])}", f"한국 {{{i}.kr_sub}} | 볼주머니 행!",
                    expr="focus", arms="hold", cues={"kr": "^", "diff": "볼주머니", "stamp": "$"})
            elif v == "korea":
                add(sc, f"어? 한국은 {{{i}.kr_say}}. 이건 그냥 한국에서!", f"한국 {{{i}.kr_sub}} | 그냥 한국에서!", expr="surprise", arms="up",
                    cues={"kr": "한국은", "diff": "이건", "stamp": "$"})
            elif v == "same":
                add(sc, f"한국은 {{{i}.kr_say}}. 거의 비슷하네.", f"한국 {{{i}.kr_sub}} | 거의 비슷!", cues={"kr": "^", "diff": "거의", "stamp": "$"})
            else:
                add(sc, "한국에선 파는 곳을 못 찾았어. 현지에서만!", "한국 판매처 없음 | 현지에서만!", cues={"kr": "^", "stamp": "$"})
            continue
        if v == "local":
            say = pick([f"{name}도 {{{i}.pct_say}}나 싸네.", f"{name}은 {{{i}.save_say}} 차이!", f"{name}도 {{{i}.pct_say}} 싸!"])
            sub = f"{CIRC[n]} {it['name']} | " + ("{%s.pct_sub} 싸다" % i if "pct" in say else "{%s.save_sub} 차이" % i)
        elif v == "korea":
            say = f"근데 {name}은 한국이 {{{i}.save_say}} 더 싸. 그냥 한국에서!"
            sub = f"{CIRC[n]} {it['name']} | 한국이 {{{i}.save_sub}} 더 싸다"
        elif v == "same":
            say = f"{name}은 {{{i}.pct_say}} 차이라 비슷해."
            sub = f"{CIRC[n]} {it['name']} | 차이 {{{i}.pct_sub}}"
        else:
            say = f"{name}은 한국에 없어. 현지에서만!"
            sub = f"{CIRC[n]} {it['name']} | 현지에서만"
        add(sc, say, sub, arms="point", cues={"card": "^", "stamp": "$"})
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from calc import ko_num
    for key, note in (ep.get("notes") or {}).items():
        spoken = re.sub(r"\d+", lambda m: ko_num(int(m.group())), note.get("title", ""))
        add(f"note:{key}", f"근데 반전. {spoken}.", f"근데 반전! | {note.get('title', '')}", expr="surprise", arms="up",
            cues={"title": "반전"}, todo="알아 둘 점 대사를 이 편에 맞게 다시 쓴다(항목마다 b1·b2·b3 신호)")
    if facts["total"]["n_comp"] >= 2:
        if facts["total"]["saved"] >= 0:
            add("summary", f"다 사면 한국보다 {{total.saved_say}} 덜 써!", "합계 | {total.saved_sub} 덜 쓴다!", expr="happy", arms="up", cues={"bars": "^", "result": "덜"})
        else:
            add("summary", "다 합치면 오히려 한국이 {total.saved_say} 싸.", "합계 | 한국이 {total.saved_sub} 싸다", expr="sad", cues={"bars": "^", "result": "오히려"})
    ask = (ep.get("outro") or {}).get("ask") or pick(["다음엔 뭘 검산할까?", "다음엔 어디를 검산할까?", "다음 검산 주제는 뭐가 좋을까?"])
    add("outro", f"{ask} 댓글로 알려 줘!", f"{ask} | 댓글로 알려 줘!", expr="happy", arms="wave", cues={"ask": "^", "source": "댓글로"})
    # 길이 어림: 숫자 자리는 평균 7음절로 본다
    total = sum(syl(re.sub(r"\{[^}]+\}", "가" * 7, l["say"])) for l in L)
    est = total / 5.0 + 0.42 * len(L) + 0.9 * len({l["scene"] for l in L}) + 3.5
    key = "lines" if not ep.get("lines") else "lines_draft"
    ep[key] = L
    (ep_dir / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"대사 초안 {len(L)}줄 → episode.json 의 {key} · 어림 길이 {est:.0f}초" + (" — 58초를 넘을 수 있으니 줄인다" if est > 56 else ""))
    for l in L:
        print(f"  {l['id']} [{l['scene']}] {l['say']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
