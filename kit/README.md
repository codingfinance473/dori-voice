# 도리 쇼츠 키트 (dori-shorts)

「도리의 정보주머니」 쇼츠를 만드는 공용 키트. 스킬 `dori-shorts` 가 이 폴더를 쓴다.

```
kit/
├─ docs/                  지침 — common_guide.md(공통, 먼저) · number_quiz.md · shopping_price_check.md · examples/(EP.02 소주)
├─ templates/quiz/        화면 템플릿 index.html(render(t)) · dori.js(도리 그림·표정) · thumb.html(안 잘리는 썸네일)
├─ scripts/
│  ├─ setup.sh            파이썬 패키지 · 한국어 받아쓰기 모델 · 글꼴(Jua, Pretendard) → ~/.cache/dori-shorts
│  ├─ new_episode.sh      새 편 폴더 만들기
│  ├─ voice/              voice_job.py(목소리 작업 올리기·기다리기) · select_takes.py(받아쓰기로 고르기) · tighten.py · make_ending.py · asr.py · spell.py
│  └─ episode/            build_voice.py(시간표) · mix.py(배경음·효과음) · render.py · check_final.py · shoot_thumb.py
└─ voice_common/          매 편 같은 소리: 삼·이·일 / 정답은… / 미국! / 이걸로 검산 끝! / 댓글 요청 / 볼주머니에 쏙!
```

## 한 편 만드는 순서(숫자 퀴즈)

```bash
bash kit/scripts/setup.sh
bash kit/scripts/new_episode.sh ~/ep03
cd ~/ep03
# voice/lines.json 에 대사 · 자막 · 핵심어(keys) 쓰기 (공용 소리는 "reuse": "count3" 처럼)
python3 voice/voice_job.py make ep03-01 L01 L02 L03 … --note "EP.03 화장품"
python3 voice/voice_job.py wait ep03-01          # 백그라운드로, 8~15분
python3 voice/select_takes.py                     # 확인할 줄은 말을 바꿔 다시 만든다
python3 voice/make_ending.py L16 L16b
python3 build_voice.py                            # order · WORD 고치기
python3 render.py stills 3 12 20 …                # index.html 고치며 정지 화면 확인
python3 mix.py && python3 check_final.py mix.wav
python3 render.py video EP03.mp4 mix.wav          # 백그라운드로, 약 7분
python3 check_final.py EP03.mp4
python3 shoot_thumb.py                            # thumbnail.jpg + thumb_check.png
```

산출물은 영상 1개 · 제목 1개 · 설명 1개 · 썸네일 1개(공통 지침 1절).
