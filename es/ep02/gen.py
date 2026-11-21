"""Generate the Episode 01 narration, one wav per sentence, with the approved British voice blend."""
import soundfile as sf, json, os, sys
import numpy as np
from kokoro_onnx import Kokoro
D = "/home/claude/es/ep02"; os.makedirs(f"{D}/voice", exist_ok=True); sys.path.insert(0, D)
from script import S
k = Kokoro("/home/claude/kok/kokoro-v1.0.int8.onnx", "/home/claude/kok/voices-v1.0.bin")
VOICE = np.load("/home/claude/es/vt/lewis_blend.npy")
meta = []
for i, (b, s, cap, p, sp) in enumerate(S):
    f = f"{D}/voice/s{i:03d}.wav"
    if not os.path.exists(f):
        a, sr = k.create(s, voice=VOICE, speed=sp + 0.07, lang="en-gb"); sf.write(f, a, sr)
    else: a, sr = sf.read(f)
    meta.append({"i": i, "beat": b, "text": s, "cap": cap or s, "dur": len(a) / sr, "pause": p})
    print(i, round(len(a) / sr, 2), flush=True)
json.dump(meta, open(f"{D}/voice/meta.json", "w"), indent=1)
print("TOTAL", round(sum(m["dur"] + m["pause"] for m in meta), 1))
