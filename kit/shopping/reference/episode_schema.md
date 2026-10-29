# episode.json 형식 (3판)

에피소드 폴더 = `episode.json` + `evidence/`(증거 기록) (+ 사용자 사진·영상이 있으면 `media/`). 스크립트가 `facts.json`·`facts.md`·`build/`·`out/` 을 만든다.
웹 조사 편(`mode: "web"`, 기본)과 영수증 편(`mode: "receipt"`)을 같은 형식으로 쓴다. 실제 예: `examples/ep01_uniqlo/`.

```jsonc
{
  "mode": "web",                          // web: 공식몰·판매처 가격 / receipt: 사용자가 산 영수증
  "verify": "strict",                     // strict(웹 기본): 증거 검사 통과해야 계산 / draft: 연습용(화면에 '검증 전') / receipt
  "max_age_h": 24,                        // 증거 유효 시간(마지막 확인 후)
  "round_krw": 1,                         // 원화 환산 반올림 단위(1원 기본, 10도 가능)
  "series": "도리의 가격 검산", "ep": 1,
  "title": "유니클로 겨울템, 일본이 쌀까?",   // 화면 제목(길면 자동으로 글자를 줄인다)
  "place": "일본", "store": "유니클로",     // store 로 시작하는 출처 이름은 화면 칸에서 store 를 빼고 짧게 쓴다
  "currency": "JPY", "currency_sym": "¥", "currency_ko": "엔",
  "fx": { "official": "ecos" },           // 웹 편: evidence.py fx 의 ECOS 매매기준율을 쓴다. "rate" 를 적으면 ECOS 값과 같은지 대조만
  //  영수증 편: { "card_krw": 26480, "local_total": 2924, "date": "…" } (카드 실결제 환율)
  "local_rule": { "tax_rate": 10, "tax_included": true, "refund_min_pretax": 5000, "source": "tax" },
  "literals": [                           // 화면·대사에 쓰는 제도 숫자·문장 — 원문 기록(capture.js quote)에서 찾은 문구가 있어야 한다
    { "text": "2026년 11월 1일", "source": "tax", "needle": "2026年11月1日購入分から" },
    { "text": "90일", "source": "tax", "needle": "90日以内" },
    { "text": "5,000", "source": "tax", "needle": "5,000円以上" },
    { "text": "계산은 세금 포함 가격으로", "source": "tax_claims", "needle": "税込価格(課税)で免税対象物品を購入" }
  ],
  "thresholds": { "local_win": -15, "kr_win": 5 },
  "hook": { "kicker": "11월부터 일본 면세가 바뀐다", "sticker": "한국보다<br>진짜 쌀까?", "note": "가격은 …" },  // 모두 선택
  "voice": { "preset": "E", "accept": [] },   // preset: E(기본, 발랄 귀여움)·E1·E3·B — assets/voices.json. accept: 받아쓰기에 숫자가 안 들렸지만 사람이 듣고 맞다고 한 줄 번호
  "music": { "style": "fresh" },               // fresh(기본, 「도리 산책」)·lofi(2판)·none. seed·bpm, level(쉬는 동안 목소리 대비 dB, 기본 -11)·duck(말하는 동안 더 낮출 dB, 기본 8)·hi_duck(1.2kHz 위, 4)·num_duck(숫자 줄, 2)·check(배경음 위 숫자 받아쓰기, true)도 줄 수 있다
  "items": [
    {
      "id": "a", "role": "best",          // best | twist | regret
      "name": "히트텍 크루넥 T(9부)", "code": "E461003",   // code 는 화면 오른쪽 위에 작게, 증거의 상품번호와 같아야 한다
      "allow_sale": false,                // 할인가를 쓸 때만 true(+ 기간을 note 에)
      "size": { "q": 18, "unit": "매" },   // 용량이 다를 때만
      "local": { "price": 1290, "source": "유니클로 일본 공식몰", "url": "https://…" },   // price 는 생략 가능(증거에서), 적으면 대조
      "kr": { "price": 16900, "seller": "유니클로 한국 공식몰", "url": "https://…",
              "taggable": false, "shipping": 0, "size": { "q": 18, "unit": "매" } },   // 한국 판매처가 없으면 "kr": null + evidence.py absent
      "media": { "type": "none", "icon": "longtee", "color": "#8E9AAF" }
      //  사용자 사진: { "type": "photo", "path": "media/a.jpg" } / 영상: { "type": "video", "path": "media/a.mp4", "start": 1.0, "dur": 6 }
    }
  ],
  "notes": {                              // 알아 둘 점 카드(선택) — 장면 이름 "note:tax"
    "tax": { "sticker": "반전", "title": "11월부터 일본 면세가 바뀌어요",
             "items": [ { "text": "계산은 세금 포함 가격으로", "small": "2026년 11월 1일 구매분부터" },
                        { "text": "한 가게에서 하루 세전 {total.refund_min_card} 이상", "small": "히트텍 하나({a.local_card})만으로는 대상이 아니에요" } ],
             "source": "일본 관광청 면세점 사이트(여행자용 안내)" }
  },
  "summary": { "refund": true },          // 합계 화면에 면세 환급(약) 줄 보태기 — 경계값이면 자동으로 뺀다
  "outro": { "ask": "다음엔 어떤 브랜드를 검산할까?", "small": "댓글로 알려 줘!", "hold": 4.0 },   // hold: 마지막 대사 뒤 끝 화면 시간(기본 2.2초)
  "sources": [ { "kind": "면세 제도", "name": "일본 관광청 면세점 사이트(여행자용 안내)", "url": "https://…" } ],  // 원문 기록이 있으면 확인 시각이 붙는다
  "lines": [ { "id": "L01", "scene": "hook", "say": "…", "sub": "… | …", "expr": "focus", "arms": "hold", "cues": { "receipt": "^", "total": "진짜" } } ]
}
```

## 그림 아이콘(`media.icon`, `media.color`)

옷: tee · longtee · down · fleece · pants · socks · cap · shoe · bag · backpack
화장품·생활: tube · bottle · pump · jar · mask · lipstick · compact · patch
먹거리: snack · box · cup · can · food · pack(기본)
색은 `#RRGGBB`. 브랜드 로고·실제 포장 디자인은 그리지 않는다.

## 자리표시 (facts.json 에서 채운다)

품목 `{id.필드}` — 말(say)과 자막(sub)이 짝, 화면 카드는 `_card`:

| 말 | 예 | 자막 / 화면 |
|---|---|---|
| local_say | 천이백구십 엔 | local_sub (1290엔) / local_card (¥1,290) |
| krw_say | 만 구백십오 원 | krw_sub (1만 915원) / krw_card (₩10,915) |
| kr_say | 만 육천구백 원 | kr_sub / kr_card |
| save_say | 오천구백팔십오 원 (차이의 크기) | save_sub / diff_card (-₩5,985) |
| pct_say | 삼십오 퍼센트 | pct_sub (35%) / pct_card (-35%) |

품목 정보: local_time·kr_time(마지막 확인 시각 01:43), local_time_label(10/24 01:33~01:43), local_src_short(일본 공식몰), krw_exact(정확한 환산값).

합계 `{total.필드}`: saved_say/_sub/_card, saved_pct_say, local_sum_say/_card, kr_sum_say/_card, local_sum_local_say/_sub/_card(현지 통화 합계),
refund_min_say/_sub/_card(세전 기준 금액), tax_incl_local_card(세금 포함 합계), tax_approx_local_card(약 ¥1,250), refund_approx_krw_card(약 ₩10,590),
receipt_total_say/_sub·receipt_krw_say/_sub(영수증 편). 어림수로 자동 바꾸는 기능은 없다(3판).

facts 의 시각·환율: price_time.label(10/24 01:33~01:46)·local_label·kr_label, rate_card(¥100 = ₩846.12), rate_date(2026-10-23)·rate_date_md(10/23), rate_basis(매매기준율), rate_source.

## 장면과 단계(`cues`)

| scene | 단계(순서) | 화면 |
|---|---|---|
| hook | receipt → total | 검산 영수증(확인 시각·환율 포함) 출력 → 질문 스티커(영수증 아래 빈자리, 없으면 생략) |
| item:<id> | card → local → krw → kr → diff → stamp | 제목·그림 → 검산표 줄(출처·확인 시각) → 싼 쪽 동그라미 → 판정 도장 |
| note:<key> | title → b1 → b2 → b3 | 알아 둘 점 카드(최대 3줄) |
| summary | bars → result | 현지 vs 한국 막대 → 아낀 돈(+면세 환급 약) |
| outro | ask → source | 다음 주제 질문 → 검산 기준(환율 고시일·가격 확인 시각·주의)·출처·AI 목소리 표시 |

값: 그 줄 대사 속 낱말(숫자 말고), `^` 줄 시작, `$` 줄 끝. 빠진 단계는 앞뒤 사이에 자동으로 놓인다.

## 판정

| 판정 | 조건(원화 환산 현지가 vs 한국가, 용량 맞춤) | 도장 색 |
|---|---|---|
| 현지 이득 | 차이 ≤ local_win(기본 -15%) | 주홍 |
| 비슷해요 | 그 사이 | 회색 |
| 그냥 한국에서 | 차이 ≥ kr_win(기본 +5%) | 파랑 |
| 현지에서만 | 한국 판매처 없음 | 보라 |

계산은 Decimal(부동소수 오차 없음). 원화는 `round_krw`(기본 1원) 단위로 반올림(0.5 올림)하고, 차이·%는 반올림한 값끼리 계산한다(화면 숫자끼리 맞아떨어진다). %는 정수 반올림.
