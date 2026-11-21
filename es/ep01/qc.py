import os, sys
os.environ.setdefault("EP_META", "meta_test.json"); sys.argv = ["x", "q"]
import ep01 as X, numpy as np
from PIL import Image
picks = [("hook",1),("hook",4),("hook",7),("hook",8),("hook",10),("y0",1),("y1",1),("y2",2),("y2",6),("y3",2),("y3",5),("y3",8),
         ("y3",10),("y3",14),("y4",1),("y4",3),("y4",5),("map",2),("map",4),("deal",2),("deal",5),("deal",8),("y4b",3),("y4b",7),
         ("y4b",9),("y4b",12),("y4b",15),("y5",3),("y5",5),("y5",9),("y5",13),("y6",1),("y6",3),("y6",6),("y7",2),("y7",5),
         ("lesson",1),("lesson",5),("lesson",7),("lesson",9),("lesson",11)]
ts = []
for b, i in picks:
    m = [x for x in X.META if x["beat"] == b][i]; ts.append(m["t"] + m["dur"] * 0.97)
ts += [X.IDENT_T + 6.5, X.OUTRO + 5]
out = sys.argv_out if hasattr(sys, "argv_out") else "/home/claude/es/ep01/qc"
os.makedirs(out, exist_ok=True)
for k in range(0, len(ts), 9):
    grp = ts[k:k + 9]; c = Image.new("RGB", (640 * 3, 360 * ((len(grp) + 2) // 3)))
    for j, t in enumerate(grp):
        for tw in np.arange(max(0, t - 1.5), t, 0.3): X.frame_rgba(tw)
        c.paste(Image.fromarray(X.frame(t)).resize((640, 360)), ((j % 3) * 640, (j // 3) * 360))
    c.save(f"{out}/qc_{k // 9}.jpg", quality=82); print("saved", k // 9, flush=True)
