# 가격 검산(쇼핑) 편 — 만드는 법 (receipt-shorts 3판 → dori-shorts 키트, 2026-10-29)

"○○ 가면 꼭 사야 할 Best 3"를 숫자로 검산하는 쇼츠다. 두 나라 공식 가격·판매처 가격을 같은 상품끼리 환율·용량까지 맞춰 비교하고,
"그냥 한국에서 사"라는 결론이나 제도 변화 같은 반전도 그대로 말한다. **가격은 절대 틀리면 안 된다** — 사람이 숫자를 옮겨 적지 않고,
기계로 읽은 증거가 검사를 통과해야만 영상이 나온다.

공통 지침(`kit/docs/common_guide.md`)이 이 문서보다 앞선다: 산출물은 영상 1개 · 제목 1개 · 설명 1개 · 안 잘리는 썸네일 1개,
숫자는 지금과 가장 가까운 최신 값, 주제는 뉴스만이 아니라 검색 추이·시사 달력·커뮤니티에서.

- **웹 조사 편(기본, `mode: "web"`, `verify: "strict"`)**: 브라우저로 공식몰 가격을 읽어 증거를 남긴다.
- **영수증 편(`mode: "receipt"`)**: 사용자가 여행에서 산 영수증·사진으로 만든다.
- 구성 연습만 할 때는 `verify: "draft"` — 화면에 "검증 전 · 올리지 마세요"가 크게 찍히고 qa가 통과시키지 않는다.

## 0. 준비 (세션마다 한 번)

```bash
K=$DORI_VOICE_REPO/kit            # 저장소 codingfinance473/dori-voice 를 클론한 곳
SK=$K/shopping
bash $K/scripts/setup.sh          # 받아쓰기 모델·글꼴(키트 공용)
bash $SK/scripts/setup.sh         # 쇼핑 편 파이썬 패키지(soundfile·pyloudnorm 등). 예비 목소리 E 모델은 RS_TTS=1 일 때만
```

작업 폴더는 쓰기 가능한 곳에 만든다(예: `~/shorts/ep02`). 키트 폴더 안에서 작업하지 않는다.
실제 완성 예: `examples/ep01_uniqlo`(2026-10-24 가격 — 증거가 만료됐으므로 그대로 다시 올리지 않는다).

## 1. 주제 정하기

`reference/주제_은행.md` 와 공통 지침 5절(검색 추이·시사 달력·커뮤니티·통계 발표 일정·뉴스)에서 후보를 모은다. 고르는 기준:
- 같은 상품을 두 나라에서 공식 가격으로 확인할 수 있다(상품번호·용량이 맞는다).
- 태그 수익을 원하면 한국 가격이 유튜브 쇼핑 제휴처(올리브영·쿠팡·컬리·W컨셉 등)에 있는 품목. 브랜드 공식몰 비교는 태그 없이.
- 시의성 훅(환율 급변, 면세 제도 변경, 세일, 신제품, "○○ 반값" 같은 소문 검색 급증).
- 의약품·의약외품·건강 효능 주제는 다루지 않는다.
- 편 구성을 돌려 쓴다(4개 검산+알아 둘 점 / 3개+반전 / 먹킷리스트 / 다시 검산). 같은 틀에 이름만 바꾼 영상이 쌓이면 유튜브가 채널 단위로 수익 창출에서 뺄 수 있다.

## 2. 가격 증거 → 검사 → 대조표

`reference/리서치_가이드.md` 를 따른다.

1. **가격(브라우저)**: 상품 페이지를 열고 `assets/capture.js` 를 실행해 증거 기록(JSON 한 줄)을 받는다. 한 가격마다 읽는 방식이 다른 기록 2개 이상:
   `DoriCapture.product`(화면 가격) + `DoriCapture.state`(서버 원본 — 크롬 자동 번역의 영향을 받지 않는다) + 가능하면 `DoriCapture.list`(검색 목록).
   결과 문자열은 **고치지 말고 그대로** `evidence/inbox.jsonl` 에 붙인다(한 실행에 기록 하나). 페이지 사이 4~5초 쉬고, "Access Denied"가 뜨면 그 사이트는 멈춘다.
2. **제도 숫자·문장(브라우저)**: 정부 원문 페이지에서 `DoriCapture.quote({id, needles:[원문 문구…]})`(한 기록에 문구 3개까지), episode.json `literals` 에 화면 문구와 원문 문구를 짝지어 적는다. 원문에 없는 말은 쓰지 않는다.
3. **환율(API)**: `python3 $SK/scripts/evidence.py fx ~/shorts/ep02` — 한국은행 ECOS 매매기준율(키 없이 sample 로도 된다).
4. **넣고 검사**:
   ```bash
   python3 $SK/scripts/evidence.py add   ~/shorts/ep02 ~/shorts/ep02/evidence/inbox.jsonl
   python3 $SK/scripts/evidence.py check ~/shorts/ep02        # → evidence/verified.json
   ```
   한국 판매처가 없는 품목은 `evidence.py absent <폴더> <id> "<찾아본 곳>"`.
5. 가격 밖의 배경 숫자(방문객 수·카드 결제액·환율 추이 등)도 오늘 기준 가장 최근 발표를 쓰고 기관 + 기준 기간을 적는다.

## 3. episode.json

형식은 `reference/episode_schema.md`, 빈 틀은 `examples/template.json`. `"voice": {"preset": "C"}`(기본이라 생략 가능).

```bash
python3 $SK/scripts/calc.py ~/shorts/ep02/episode.json     # 증거 검사 → facts.json · facts.md — 실패하면 숫자를 만들지 않는다
python3 $SK/scripts/draft.py ~/shorts/ep02                 # 대사 초안(선택). 이 편에 맞게 고친다
```

구성(50초 안팎, 58초 넘으면 voice.py 가 알려 준다): 훅(`hook`) → 검산 3~4개(`item:<id>`, 첫 품목만 자세히) → 반전 1개(`role: "twist"` 또는 `notes`) → 합계(`summary`) → 마무리(`outro`).

대본 규칙:
- 숫자는 자리표시로만: 말 `{a.local_say}` `{a.krw_say}` `{a.kr_say}` `{a.save_say}` `{a.pct_say}` `{total.saved_say}` …, 자막은 `_sub`. 대사에 아라비아 숫자를 쓰지 않는다.
- 자막 숫자는 대사에서 같은 숫자로 읽혀야 한다(voice.py 가 대조). 한 줄 2~5초, 짧은 반말, 외래어는 띄어 쓰고(드럭 스토어), 알파벳 상품명은 한글로.
- "~래", "공식몰 기준으로"처럼 조사 결과를 전하는 말투. 효능·건강·금융 조언 금지. 제도는 원문과 같은 뜻으로("이상"을 "넘게"로 바꾸지 않는다).
- 화면 단계는 `cues`(낱말·`^`·`$`)로 대사에 맞춘다.

## 4. 목소리 C → 만들기

```bash
python3 $SK/scripts/run.py ~/shorts/ep02 preview
```
처음에는 목소리 단계에서 **멈춘다(코드 5)** — 도리 목소리 C 는 깃허브 액션에서 만든다. 화면에 나온 명령대로:
```bash
cd ~/shorts/ep02/build/voice_c
python3 $K/scripts/voice/voice_job.py make <작업id> L01 L02 … --note "가격 검산 EP.xx"     # 숫자는 이미 채워져 있다(voice/lines.json)
python3 $K/scripts/voice/voice_job.py wait <작업id>          # Bash 백그라운드로, 8~15분
python3 $K/scripts/voice/select_takes.py                     # 숫자가 원본·다듬은 소리 두 받아쓰기에 다 들린 테이크
```
"확인할 줄"은 문장을 바꿔 그 줄만 새 작업으로 다시 만든다(숫자를 어림수로 바꾸지 않는다). 그다음 `run.py ~/shorts/ep02 preview` 를 다시 돌리면
고른 소리로 받아쓰기 확인·시간표·정지 화면·화면 숫자 점검까지 간다. `facts.md`, `build/voice_check.md`, `build/stills/sheet.png`, `build/audit.json` 을 확인한다.

```bash
python3 $SK/scripts/run.py ~/shorts/ep02 video     # 정지 화면 → 화면 숫자 점검 → 가림 영역 → 소리 → 렌더(약 6분) → 합치기 → 점검
```
- 렌더 전 관문: 화면 숫자 점검 통과 + 같은 facts·시간표 + 증거가 아직 24시간 안 + 계산 뒤 증거가 바뀌지 않음.
- Bash 시간 제한을 10분으로 두거나 백그라운드로 돌리고, 끊기면 `render.py <폴더> video` 부터 다시.
- qa "확인" 항목은 고친다. "가격 검증" 줄의 남은 시간 안에 올리거나, 지났으면 증거를 다시 읽고 calc부터.
- 숫자가 걸린 편은 마지막에 작업을 모르는 별도 에이전트에게 원본 증거만 주고 다시 계산해 영상 프레임과 대조하게 한다.

예비 목소리: 저장소를 쓸 수 없을 때만 `"voice": {"preset": "E"}` + `RS_TTS=1 bash $SK/scripts/setup.sh`(Supertonic-3, 이 컴퓨터에서 합성).

## 5. 넘겨주기 — 네 가지

1. **영상**: `out/` 의 MP4 하나(10MB 버전 없음).
2. **제목 1개**: `out/upload.md` 의 제목 칸(태그가 있으면 맨 앞 `[광고]`). 판정을 제목에 쓰지 않는다.
3. **설명**: `out/upload.md` 의 설명(요약 1~2줄 + 검산 기준·출처·AI 목소리 문구는 그대로 + 해시태그 5개).
4. **썸네일 1장**: 키트 `templates/quiz/thumb.html` 을 작업 폴더에 복사해 `CFG`(칩 `가격 검산`, 제목, `flags` 대신 `key`에 상품 아이콘·"반값?" 같은 핵심 그림 하나, 소품)를 고치고 `python3 $K/scripts/episode/shoot_thumb.py` → `thumb_check.png` 로 4:5·1:1·3:2 잘림 확인. 판정 도장은 넣지 않는다.
   (shoot_thumb.py 는 같은 폴더의 thumb.html·dori.js·글꼴을 쓴다 — `cp $K/templates/quiz/{thumb.html,dori.js} . && cp -r ~/.cache/dori-shorts/fonts/jua jua && mkdir -p fonts && cp ~/.cache/dori-shorts/fonts/pretendard/*.otf fonts/`)

상품 태그 연결은 사용자가 유튜브 스튜디오에서 한다.

## 가격 정확성 규칙 (바꾸지 않는다)

1. 가격은 기계로 읽은 증거 기록만(주소·읽은 시각·서명 v2). 사람이 옮겨 적은 숫자, 기사·블로그 가격은 쓰지 않는다.
2. 한 가격은 읽는 방식이 다른 기록 2개 이상이 같아야 한다. 하나라도 다르면 그 품목은 멈춘다.
3. 할인·기간 한정 표시가 있으면 정가 비교에서 멈춘다(할인가는 `allow_sale` + 기간).
4. 세금 포함 여부를 서버 데이터로 확인한다(세금 포함가로 비교).
5. 환율은 한국은행 ECOS 매매기준율만. 화면에 고시일, "카드 결제액과는 달라요". 원화 1원 단위 반올림(0.5 올림), % 정수 반올림.
6. 확인 시각을 화면 위 칩·영수증·품목 줄·끝 화면·설명란에(한국 시간). 증거는 마지막 확인 후 24시간까지만.
7. 세금·환급처럼 끝수·수수료로 달라지는 값은 "약". 원문에서 확인한 제도 숫자만(`literals`).
8. 화면의 모든 숫자는 facts·literals 에서 와야 하고(0.2초마다 점검), 숫자가 스티커·도장·말풍선에 가려지면 안 된다. 세어 올라가는 연출 없음.

## 키 (모두 선택)

- 한국은행 ECOS `ECOS_API_KEY`(없으면 공개 sample 키로 최근 10건). 한국수출입은행 `EXIM_API_KEY`(교차 확인, 도메인 허용 필요).
- 키는 대화창·주소창·파일 안에 붙여 넣지 않는다. 기록에는 `{KEY}` 가 남는다.

## 정책·표시

- **AI 목소리**: 화면 위 "AI 목소리" 칩 + 설명란 "영상 속 목소리는 AI로 만들었어요." 끝 화면에는 AI 문구를 넣지 않는다(2026-10-28).
- **광고 표시**: 상품 태그를 거는 편만 — 첫 2.6초 띠, 작은 칩, 제목 맨 앞 `[광고]`, 설명 첫 줄.
- **출처·시각**: 공식몰 이름·확인 시각·환율 고시일은 화면에, 주소 목록은 설명란에. "가격은 확인 시각 기준이며 이후 바뀔 수 있어요".
- **그림**: 상품은 일반 아이콘 일러스트(로고·실제 포장·쇼핑몰 사진·캡처 금지). 사용자가 직접 찍은 사진·영상은 쓸 수 있다.
- **영수증 편**: 카드번호·승인번호·회원번호는 `receipt.blur` 로 가린다.
- **가림 영역**: 위 150px, 아래 420px, 오른쪽 160px에 글자를 두지 않는다(`render.py boxes`).
- 저작권·상표: `reference/저작권_점검.md`. 도리 그림: `reference/도리_캐릭터.md`, 시트·스티커는 `scripts/dori_art.py`.

## 파일

- `scripts/`: setup.sh · evidence.py(증거·환율·검사) · calc.py(검산) · draft.py(대사 초안) · voice.py(목소리 C 불러오기·받아쓰기·숫자 대조·시간표, 예비 E 합성) · voicefx.py · render.py(정지 화면·화면 숫자 점검·렌더 관문·가림 점검) · audio.py(효과음·덕킹·믹스) · music.py(배경음 「도리 산책」) · qa.py(점검·업로드 꾸러미) · run.py(한 번에) · dori_art.py
- `assets/`: capture.js · engine.html(화면 엔진) · dori.js · voices.json(기본 C, 예비 E·E1·E3·B) · fonts
- `reference/`: 리서치_가이드 · 주제_은행 · episode_schema · 입력양식 · 촬영_체크리스트 · 도리_캐릭터 · 저작권_점검
- `examples/`: ep01_uniqlo(웹 조사 편, 증거 포함) · sample(영수증 편) · template.json
