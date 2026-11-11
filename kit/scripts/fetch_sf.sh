#!/usr/bin/env bash
# music.py 가 쓰는 악기 샘플(MusyngKite 사운드폰트, gleitz/midi-js-soundfonts) 내려받기 → $SFDIR (기본 /home/claude/sf), 약 17MB · 1분
set -euo pipefail
SF="${SFDIR:-/home/claude/sf}"; mkdir -p "$SF"; cd "$SF"
N="C Db D Eb E F Gb G Ab A Bb B"
for i in pizzicato_strings glockenspiel acoustic_bass bassoon electric_piano_1 electric_bass_finger vibraphone marimba kalimba celesta; do
  mkdir -p $i; for o in 1 2 3 4 5 6 7; do for n in $N; do echo "$i $n$o"; done; done
done | xargs -P 24 -n 2 sh -c 'curl -s -f -o "$0/$1.mp3" "https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/MusyngKite/$0-mp3/$1.mp3" || true'
find . -name "*.mp3" | sed 's/\.mp3$//' | xargs -P 16 -I{} ffmpeg -loglevel error -y -i {}.mp3 -ac 1 -ar 44100 {}.wav
echo "샘플 준비 끝: $SF"
