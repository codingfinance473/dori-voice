#!/usr/bin/env bash
# setup.sh — 가격 검산(쇼핑) 편 준비(세션마다 한 번): 파이썬 패키지, 받아쓰기 모델, 글꼴을 ~/.cache/receipt-shorts 에. 예비 목소리 E 모델은 RS_TTS=1 일 때만.
set -e
C="$HOME/.cache/receipt-shorts"; mkdir -p "$C/models" "$C/fonts"
pip install -q sherpa-onnx soundfile pyloudnorm playwright pillow pillow-heif scipy numpy fonttools praat-parselmouth --break-system-packages 2>/dev/null || \
  pip install -q sherpa-onnx soundfile pyloudnorm playwright pillow pillow-heif scipy numpy fonttools praat-parselmouth || true
python3 -c "from playwright.sync_api import sync_playwright as s; p=s().start(); b=p.chromium.launch(); b.close(); p.stop()" 2>/dev/null || python3 -m playwright install chromium
R=https://github.com/k2-fsa/sherpa-onnx/releases/download
cd "$C/models"
# 기본 목소리 C 는 깃허브 액션에서 만든다 — 예비 목소리 E(Supertonic-3)를 쓸 때만 RS_TTS=1 로 받는다(약 400MB)
if [ "${RS_TTS:-0}" = 1 ]; then
  [ -f sherpa-onnx-supertonic-3-tts-int8-2026-05-11/tts.json ] || { curl -sSL -o tts.tar.bz2 "$R/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2" && tar xjf tts.tar.bz2 && rm tts.tar.bz2; }
fi
# 받아쓰기 모델은 dori-shorts 키트 캐시에 있으면 그걸 쓴다
DK="${DORI_CACHE:-$HOME/.cache/dori-shorts}/sherpa-onnx-zipformer-korean-2024-06-24"
if [ ! -f sherpa-onnx-zipformer-korean-2024-06-24/tokens.txt ] && [ -f "$DK/tokens.txt" ]; then ln -s "$DK" sherpa-onnx-zipformer-korean-2024-06-24; fi
[ -f sherpa-onnx-zipformer-korean-2024-06-24/tokens.txt ] || { curl -sSL -o asr.tar.bz2 "$R/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2" && tar xjf asr.tar.bz2 && rm asr.tar.bz2; }
SK="$(cd "$(dirname "$0")/.." && pwd)"
if [ -s "$SK/assets/fonts/Pretendard-Bold.woff2" ]; then echo "글꼴: 스킬에 들어 있음"; ls "$C/models"; echo "준비 끝"; exit 0; fi
cd "$C/fonts"
if [ ! -s Jua-Regular.ttf ] || ! head -c 4 Jua-Regular.ttf | od -An -tx1 | grep -q "00 01 00 00"; then
  curl -sSL -o Jua-Regular.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/jua/Jua-Regular.ttf" || true
fi
if ! head -c 4 Jua-Regular.ttf 2>/dev/null | od -An -tx1 | grep -q "00 01 00 00"; then
  rm -f Jua-Regular.ttf; echo "주아(Jua) 글꼴을 받지 못함 — 말풍선·제목은 기본 한글 글꼴로 그린다(재료를 직접 올려도 된다: Jua-Regular.ttf)"
fi
for w in Medium SemiBold Bold ExtraBold; do
  [ -s "Pretendard-$w.woff2" ] || NEED=1
done
if [ -n "$NEED" ]; then T=$(mktemp -d); (cd "$T" && npm pack pretendard@1.3.9 --silent >/dev/null && tar xzf pretendard-1.3.9.tgz \
  && cp package/dist/web/static/woff2/Pretendard-{Medium,SemiBold,Bold,ExtraBold}.woff2 "$C/fonts/"); fi
ls "$C/models" "$C/fonts"
echo "준비 끝"
