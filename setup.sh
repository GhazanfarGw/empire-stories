#!/usr/bin/env bash
# EMPIRE STORIES — rebuild the production workspace in a fresh session.
# Usage:  bash setup.sh            (from the repo root)
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /home/claude
ln -sfn "$REPO/es" /home/claude/es
ln -sfn "$REPO/v3" /home/claude/v3
mkdir -p "$REPO/es/out" "$REPO/es/assets/people"

# Python deps (most are preinstalled in the Claude workspace)
python3 - <<'EOF'
import importlib
for m in ["numpy", "scipy", "PIL", "soundfile"]:
    try: importlib.import_module(m)
    except ImportError: print("MISSING python package:", m)
EOF
command -v ffmpeg >/dev/null || echo "MISSING: ffmpeg"

# Voice engine (Kokoro TTS). Model files are too large for git:
#   kokoro-v1.0.int8.onnx + voices-v1.0.bin  ->  /home/claude/kok/
#   source copies live on the PC in  E:\Empire Stories\_tools\
if [ ! -f /home/claude/kok/kokoro-v1.0.int8.onnx ]; then
  echo "NOTE: Kokoro model not found in /home/claude/kok — stage it from E:\\Empire Stories\\_tools (or pip install kokoro-onnx and download the model)."
fi
echo "Workspace ready: /home/claude/es -> $REPO/es"
