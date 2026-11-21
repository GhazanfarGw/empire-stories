import os, sys
sys.argv = ["x", "q"]
import ep02 as X, numpy as np
from PIL import Image
picks = [("hook",0),("hook",1),("hook",3),("hook",7),("hook",9),("hook",11),("hook",12),("y0",0),("y0",1),("y0",2)]
ts = []
for b, i in picks:
    m = [x for x in X.META if x["beat"] == b][i]; ts.append(m["t"] + m["dur"] * 0.97)
ts += [X.IDENT_T + 6.5]
out = sys.argv_out if hasattr(sys, "argv_out") else "/home/claude/es/ep02/qc"
os.makedirs(out, exist_ok=True)
for k in range(0, len(ts), 9):
    grp = ts[k:k + 9]; c = Image.new("RGB", (640 * 3, 360 * ((len(grp) + 2) // 3)))
    for j, t in enumerate(grp):
        for tw in np.arange(max(0, t - 1.5), t, 0.3): X.frame_rgba(tw)
        c.paste(Image.fromarray(X.frame(t)).resize((640, 360)), ((j % 3) * 640, (j // 3) * 360))
    c.save(f"{out}/qc_{k // 9}.jpg", quality=82); print("saved", k // 9, flush=True)
