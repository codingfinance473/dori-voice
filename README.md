# dori-voice

「도리의 가격 검산」 도리 목소리를 무료로 만드는 저장소.
깃허브 액션이 오픈소스 Qwen3-TTS(Apache-2.0, 상업적 이용 가능)를 CPU로 돌린다. API 키·결제 없음.

- `jobs/*.json` 을 올리면(push) 액션이 돈다 → 결과는 `out/<작업 id>/` 에 커밋된다.
- 작업 종류
  - `design`: 설명문으로 목소리를 새로 디자인(Qwen3-TTS-12Hz-1.7B-VoiceDesign)
  - `custom`: 미리 있는 목소리(Sohee 등)에 말투 지시(Qwen3-TTS-12Hz-1.7B-CustomVoice)
  - `clone`: `voices/<이름>/ref.wav`+`ref.txt` 로 고정한 도리 목소리로 대사 생성(Qwen3-TTS-12Hz-0.6B/1.7B-Base)
- 여러 작업은 동시에(매트릭스) 돈다. 비공개 저장소 무료 한도는 매달 2,000분.

receipt-shorts 스킬이 이 저장소에 작업을 올리고 결과를 받아 숫자 받아쓰기 확인·시간표·영상까지 이어서 만든다.
