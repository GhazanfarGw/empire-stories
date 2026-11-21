#!/bin/bash
# EMPIRE STORIES sound v3 mix: voice clear on top; bed ducked under voice; soft effects bus. usage: mix.sh <dir> <video.mp4> <out.mp4>
D=$1; cd "$D"
ffmpeg -y -loglevel error -i "$2" -i voice.wav -i sfx.wav -i bed.wav -filter_complex "\
[1:a]aresample=48000,highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=15:release=200,asplit=2[v1][v2];\
[3:a]volume=0.14[b];[b][v1]sidechaincompress=threshold=0.012:ratio=10:attack=60:release=1200[bd];\
[2:a]volume=0.12,lowpass=f=5000[s];\
[v2][bd][s]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$3.tmp.mp4" && mv "$3.tmp.mp4" "$3"
