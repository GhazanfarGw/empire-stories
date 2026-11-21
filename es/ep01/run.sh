#!/bin/bash
# EMPIRE STORIES Ep01: render video parts in parallel, join, mix sound, final encode (<100MB for staging).
set -e
cd /home/claude/es/ep01
mkdir -p parts
END=$(python3 ep01.py info | sed -E 's/^END ([0-9.]+).*/\1/')
echo "END=$END"
# split into 2 workers x N chunks (balanced: interleave chunks of ~60s)
python3 - "$END" > chunks.txt <<'EOF'
import sys; e = float(sys.argv[1]); step = 60.0; a = 0.0
while a < e - 1e-6: b = min(e, a + step); print(f"{a:.3f} {b:.3f}"); a = b
EOF
cat chunks.txt | xargs -P 2 -L 1 bash -c 'f=parts/p_$(printf "%05d" $(python3 -c "print(int(float(\"$0\")*10))")).mp4; [ -f "$f" ] || python3 ep01.py part $0 $1'
ls parts/p_*.mp4 | sort | sed "s/^/file '/; s/$/'/" > concat.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i concat.txt -c copy video.mp4
python3 audio.py
ffmpeg -y -loglevel error -i video.mp4 -i voice.wav -i music.wav -filter_complex "\
[1:a]asetrate=24000*0.96,aresample=48000,atempo=1.0417,highpass=f=50,lowshelf=f=120:g=4.5,equalizer=f=260:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,asplit[v1][v2];\
[2:a][v1]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=300[m];\
[m][v2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
 -map 0:v -map "[a]" -vf hqdn3d=1.5:1.5:6:6 -c:v libx264 -preset slow -crf 24 -tune animation -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart \
 EMPIRE_STORIES_Ep01_Apple_Was_Almost_Finished.mp4
python3 ep01.py srt
ls -la EMPIRE_STORIES_Ep01_Apple_Was_Almost_Finished.mp4
