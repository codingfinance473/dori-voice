#!/usr/bin/env bash
# 도리 쇼츠 작업 환경 준비(세션마다 한 번). 파이썬 패키지 · 한국어 받아쓰기 모델 · 글꼴(Jua, Pretendard — 둘 다 OFL)을 캐시에 받는다.
# 사용: bash kit/scripts/setup.sh        캐시 위치는 DORI_CACHE(기본 ~/.cache/dori-shorts)
set -euo pipefail
CACHE="${DORI_CACHE:-$HOME/.cache/dori-shorts}"
mkdir -p "$CACHE"

python3 -c "import sherpa_onnx, parselmouth, scipy, numpy, PIL" 2>/dev/null || \
  pip install -q --break-system-packages sherpa-onnx praat-parselmouth scipy numpy pillow 2>/dev/null || \
  pip install -q sherpa-onnx praat-parselmouth scipy numpy pillow
python3 -c "import playwright" 2>/dev/null || echo "알림: playwright 가 없어요(pip install playwright && playwright install chromium)"
command -v ffmpeg >/dev/null || echo "알림: ffmpeg 가 없어요"

M="$CACHE/sherpa-onnx-zipformer-korean-2024-06-24"
if [ ! -f "$M/tokens.txt" ]; then
  echo "받아쓰기 모델 내려받는 중…"
  curl -sSL -o "$CACHE/asr.tar.bz2" https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2
  tar -xjf "$CACHE/asr.tar.bz2" -C "$CACHE" && rm -f "$CACHE/asr.tar.bz2"
fi

F="$CACHE/fonts"
if [ ! -f "$F/jua/index.css" ] || [ ! -f "$F/pretendard/Pretendard-Bold.otf" ]; then
  echo "글꼴 내려받는 중…"
  rm -rf "$F" && mkdir -p "$F" && cd "$F"
  npm pack -q @fontsource/jua@5.3.0 >/dev/null && tar -xzf fontsource-jua-5.3.0.tgz && mv package jua && rm -f fontsource-jua-5.3.0.tgz
  npm pack -q pretendard@1.3.9 >/dev/null && tar -xzf pretendard-1.3.9.tgz && mkdir -p pretendard
  cp package/dist/public/static/Pretendard-{Regular,Medium,SemiBold,Bold,ExtraBold,Black}.otf pretendard/ && rm -rf package pretendard-1.3.9.tgz
fi
echo "준비 끝: $CACHE"
