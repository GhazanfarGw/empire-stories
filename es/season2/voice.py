import soundfile as sf, json, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro("/home/claude/kok/kokoro-v1.0.int8.onnx", "/home/claude/kok/voices-v1.0.bin")
V = np.load("/home/claude/es/vt/lewis_blend.npy")
S = [  # (text, speed, pause_after)
 ("San Bernardino, California. Nineteen forty-eight.", 1.0, 0.5),
 ("Two brothers own the busiest drive-in in town. Cars wrapped around the block. Money coming in every single night.", 1.15, 0.6),
 ("And then... they shut it down.", 0.92, 1.1),
 ("Three months. Doors locked. Parking lot empty.", 1.05, 0.5),
 ("People thought they had lost their minds.", 1.1, 0.7),
 ("But Dick and Mac McDonald had a plan.", 1.05, 0.6),
 ("When the doors opened again, the menu had just nine items. No plates. No waitresses. A hamburger for fifteen cents.", 1.15, 0.5),
 ("And the kitchen ran like a factory. Every man, one job. Your food, in seconds.", 1.15, 0.9),
 ("Six years later, in Chicago, a fifty-two-year-old milkshake-machine salesman noticed something strange.", 1.12, 0.4),
 ("One tiny restaurant in California had bought eight of his mixers.", 1.1, 0.5),
 ("Eight. Nobody needed eight.", 1.0, 0.8),
 ("So Ray Kroc got in his car, and drove west to see it for himself.", 1.08, 0.6),
 ("What he found there... would build an empire.", 0.95, 1.5),
]
meta=[]; t=0.6
for i,(s,sp,p) in enumerate(S):
    a,sr=k.create(s,voice=V,speed=sp+0.07,lang="en-gb"); sf.write(f"v{i:02d}.wav",a,sr)
    d=len(a)/sr; meta.append(dict(i=i,text=s,t0=t,dur=d)); t+=d+p
json.dump(meta,open("vmeta.json","w"),indent=1); print("TOTAL",round(t,1))
