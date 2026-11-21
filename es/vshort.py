"""EMPIRE STORIES — native vertical Shorts (owner rule, 21 Nov 2026).
Full-screen 1080x1920 on the paper background. No letterboxing, no subtitles. Every scene of the episode is re-laid out for
mobile: each panel's elements are stacked top-to-bottom (picture first, its text underneath), scaled up to fill the width.
Same timing as the episode, so the episode's voice + sound line up exactly.
Usage: python3 vshort.py <episode_dir> <module> "<EPISODE NN>" [stills t1,t2,...]"""
import os, sys, json, subprocess, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
EP_DIR, MOD, LABEL = sys.argv[1], sys.argv[2], sys.argv[3]; EXTRA = sys.argv[4:]
sys.argv = ["x", "q"]; sys.path.insert(0, EP_DIR); sys.path.insert(0, "/home/claude/es/tl3")
import importlib; X = importlib.import_module(MOD)
from tl3 import font, txt, place, NAVY_US, RED_US, IVORY, INK, MUTE, V, r, eo, eio
SW, SH = 1080, 1920
TOP, BOTTOM = 300, 1600            # story area (YouTube's own buttons sit over the bottom/right edges)
GAP = 44
MAXS = {"person": 1.9, "photo": 1.7, "cut": 1.8, "lab": 1.55, "big": 1.25, "count": 1.2, "words": 1.4, "quote": 1.45, "bars": 1.15,
        "stamp": 1.4, "note": 1.5, "grid": 1.25, "chain": 0.95, "screen": 1.45, "chart": 1.3, "focus": 1.1}

@functools.lru_cache(None)
def paper():
    p = V.bg().convert("RGB").rotate(90, expand=True).resize((SW, SH))
    yy, xx = np.mgrid[0:SH, 0:SW]; vig = 1 - 0.12 * (((xx - SW / 2) / (SW / 1.1)) ** 2 + ((yy - SH / 2) / (SH / 1.0)) ** 2)
    return Image.fromarray((np.asarray(p, np.float32) * vig[..., None]).clip(0, 255).astype(np.uint8)).convert("RGBA")

def solo(e, t, a):
    """draw one episode element alone on a transparent 1920x1080 layer (no hero move, no credit)"""
    lay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); e2 = dict(e, hero=None)
    if e["kind"] == "quote": e2["mw"] = 640                                    # rewrap for a phone screen
    if e["kind"] == "words": p = list(e["pay"]); p[5] = min(p[5], 720); e2["pay"] = tuple(p)
    X.el_draw(lay, e2, t, a); return lay

BBOX = {}
def bbox(e):
    k = id(e)
    if k not in BBOX:
        tb = max(e["tin"] + 2.5, min(e["tout"] - 0.6, e["tin"] + 30)) if e["kind"] in ("grid", "bars", "chain", "chart") else e["tin"] + 2.5
        lay = solo(e, tb, 1.0); al = np.array(lay.getchannel("A"))
        al[:90, 1000:] = 0                                   # ignore the photo-credit line in the corner
        ys, xs = np.where(al > 8)
        BBOX[k] = (max(0, xs.min() - 14), max(0, ys.min() - 14), min(1920, xs.max() + 15), min(1080, ys.max() + 15)) if len(xs) else (0, 0, 1, 1)
    return BBOX[k]

# ---- live mobile stack: whatever is on screen is stacked top-to-bottom (picture first, its text below);
#      arrivals/departures push the others smoothly (per-element smoothed position + scale)
STATE = {}; STATE_T = {}
TINS = sorted(e["tin"] for e in X.EL)
for e in X.EL:
    nxt = [x for x in TINS if x >= e["tout"] - 0.05]
    if nxt and 0 < nxt[0] - e["tout"] <= 6.0: e["tout_v"] = nxt[0] - 0.05
def stack(vis_w):
    els = sorted(vis_w, key=lambda ew: (round(ew[0]["x"] / 320), ew[0]["y"]))
    rows = []
    for e, w_ in els:
        x0, y0, x1, y1 = bbox(e); bw, bh = x1 - x0, y1 - y0
        s_ = min(MAXS.get(e["kind"], 1.3), 980 / max(bw, 1)); rows.append((e, bh * s_, s_, w_))
    tot = sum(h * w_ for _, h, _, w_ in rows) + GAP * max(0, sum(w_ for *_, w_ in rows) - 1)
    k = min(1.0, (BOTTOM - TOP) / max(tot, 1)); y = TOP + ((BOTTOM - TOP) - tot * k) / 2; out = {}
    for e, h, s_, w_ in rows:
        out[id(e)] = (y + h * k / 2, s_ * k); y += (h + GAP) * k * w_
    return out
def credit_for(t, vis):
    for e in vis:
        if e["kind"] in ("photo", "cut") and len(e["pay"]) > 2: return e["pay"][2]
    return None

def frame(t, title):
    im = paper().copy(); d = ImageDraw.Draw(im)
    # brand strip + title
    em = X.emblem_us(60); im.alpha_composite(em, (SW // 2 - 150, 70))
    d.text((SW // 2 - 78, 100), "EMPIRE STORIES", font=font("cardo", 34), fill=NAVY_US, anchor="lm")
    d.text((SW // 2, 190), title, font=font("disp", 54), fill=NAVY_US, anchor="mm")
    beat = None; vis = []; items = []
    for e in X.EL:
        to = e.get("tout_v", e["tout"])
        if not (e["tin"] - 0.05 <= t <= to + 0.05): continue
        ain = eio(r(t, e["tin"], e["tin"] + 0.4)); aout = 1 - r(t, to - 0.45, to); a = ain * aout
        if a <= 0: continue
        items.append((e, a)); vis.append(e); beat = e["b"]
    target = stack([(e, min(1.0, a * 1.4)) for e, a in items]); kk = 1 - math.exp(-1 / 30 / 0.22)
    for e, a in items:
        ty, ts_ = target[id(e)]; cy, cs = STATE.get(id(e), (ty, ts_))
        if id(e) not in STATE or t - STATE_T.get(id(e), -9) > 0.2: cy, cs = ty, ts_
        cy += (ty - cy) * kk; cs += (ts_ - cs) * kk; STATE[id(e)] = (cy, cs); STATE_T[id(e)] = t
        x0, y0, x1, y1 = bbox(e)
        piece = solo(e, t, 1.0).crop((x0, y0, x1, y1))
        piece = piece.resize((max(1, int(piece.width * cs)), max(1, int(piece.height * cs))), Image.LANCZOS)
        if a < 1: piece.putalpha(piece.getchannel("A").point(lambda v, a=a: int(v * a)))
        im.alpha_composite(piece, (int(SW / 2 - piece.width / 2), int(cy - piece.height / 2)))
    if X.TR["map"] <= t < X.TR["deal"] + X.XF:
        ma = eio(r(t, X.TR["map"], X.TR["map"] + X.XF)) * (1 - eio(r(t, X.TR["deal"], X.TR["deal"] + X.XF)))
        mp = X.scene_map(t).convert("RGB").crop((200, 0, 1720, 1080)).resize((SW, int(1080 * SW / 1520)), Image.LANCZOS).convert("RGBA")
        if ma < 1: mp.putalpha(int(255 * ma))
        im.alpha_composite(mp, (0, int((TOP + BOTTOM) / 2 - mp.height / 2)))
    pin = X.PIN_OF.get(beat) if beat else None
    if pin is not None and t >= X.PIN_T.get(pin, 1e9) - 0.2:
        lb = X.label_box(str(X.YEARS[pin]), 34, RED_US, IVORY); im.alpha_composite(lb, (SW // 2 - lb.width // 2, 238))
    c = credit_for(t, vis)
    if c: d.text((SW // 2, 1650), c, font=font("sansm", 20), fill=MUTE, anchor="mm")
    d.text((SW // 2, 1700), f"FULL STORY · {LABEL} ON THE CHANNEL", font=font("sansb", 26), fill=RED_US, anchor="mm")
    return im.convert("RGB")

if EXTRA and EXTRA[0] == "stills":
    ts = [float(x) for x in EXTRA[1].split(",")]; title = EXTRA[2] if len(EXTRA) > 2 else "Preview"
    c = Image.new("RGB", (360 * len(ts), 640))
    for j, t in enumerate(ts): c.paste(frame(t, title).resize((360, 640)), (j * 360, 0))
    c.save(f"{EP_DIR}/qc/vshort_stills.jpg", quality=85); print("stills ok"); sys.exit()

OUT = f"{EP_DIR}/vshorts"; os.makedirs(OUT, exist_ok=True)
for sh in json.load(open(f"{EP_DIR}/shorts_v2.json")):
    a, b, name = sh["a"], sh["b"], sh["name"]; dur = b - a; tmp = f"{OUT}/{name}.v.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", "30", "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fi in range(int(round(dur * 30))): enc.stdin.write(frame(a + fi / 30, sh["title"]).tobytes())
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", sh["audio"],
                    "-filter_complex", f"[1:a]afade=t=in:d=0.3,afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]", "-map", "0:v", "-map", "[au]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/{name}.mp4"], check=True)
    os.remove(tmp); print(name, round(dur, 1), "s", flush=True)
