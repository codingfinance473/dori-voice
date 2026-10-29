#!/usr/bin/env bash
# 새 편 작업 폴더를 만든다: 화면 템플릿 · 편 스크립트 · 목소리 스크립트 · 공용 목소리 조각 · 글꼴.
# 사용: bash kit/scripts/new_episode.sh <작업 폴더>      (먼저 setup.sh)
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="${DORI_CACHE:-$HOME/.cache/dori-shorts}"
D="${1:?작업 폴더를 주세요}"
mkdir -p "$D/voice" "$D/fonts"
cp "$KIT"/templates/quiz/index.html "$KIT"/templates/quiz/dori.js "$KIT"/templates/quiz/thumb.html "$D/"
cp "$KIT"/scripts/episode/*.py "$D/"
cp "$KIT"/scripts/voice/*.py "$D/voice/"
cp "$KIT"/voice_common/*.wav "$KIT"/voice_common/voice_common.json "$D/voice/"
[ -f "$D/voice/lines.json" ] || cp "$KIT"/docs/examples/EP02_soju_lines.json "$D/voice/lines.json"
[ -f "$D/voice/c_index.json" ] || echo '{}' > "$D/voice/c_index.json"
[ -f "$D/voice/spell.json" ] || echo '{"alt": {}, "num_form": {}}' > "$D/voice/spell.json"
rm -rf "$D/jua" && cp -r "$CACHE/fonts/jua" "$D/jua"
cp "$CACHE"/fonts/pretendard/*.otf "$D/fonts/"
echo "새 편 폴더: $D"
echo "다음: voice/lines.json 대사 쓰기 → python3 voice/voice_job.py make … → select_takes.py → build_voice.py → index.html·mix.py 고치기"
