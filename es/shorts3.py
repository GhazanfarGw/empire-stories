"""EMPIRE STORIES Shorts v3 — smart reframe (owner feedback 21 Nov 2026).
Thin header + thin footer, big story window, centred captions. Each frame the window follows the elements that are on screen
(from the episode's element list): tight and big on a single portrait/photo, wider when a panel has several items, never
cutting a label. Movement is smoothed like a camera operator.
Usage: python3 shorts3.py <episode_dir> <module> "<EPISODE NN>"   (segments in <episode_dir>/shorts_v2.json)"""
import os, sys, json, subprocess, math
import numpy as np
from PIL import Image, ImageDraw
EP_DIR, MOD, LABEL = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", "q"]; sys.path.insert(0, EP_DIR); sys.path.insert(0, "/home/claude/es/tl3")
import importlib; X = importlib.import_module(MOD)
from tl3 import font, txt, NAVY_US, RED_US, IVORY, INK, V
OUT = f"{EP_DIR}/shorts_v2"; os.makedirs(OUT, exist_ok=True)
SW, SH = 1080, 1920; TOP, BOT = 158, 1846            # header bottom / footer top
WIN_Y0, WIN_H = 170, 1110                             # story window area
CAP_Y = 1470; ASPECT = SW / WIN_H                     # window aspect (w/h)

def half_w(e):
    k, p = e["kind"], e["pay"]
    if k == "person": return 160
    if k in ("cut",): return p[1] * 0.62
    if k == "photo": return p[1] / 2 + 10
    if k == "lab": return len(p[0]) * 9.5 + 30
    if k == "big": return len(str(p[0])) * p[2] * 0.3 + 20
    if k == "count": return 160
    if k == "words": return min(p[5], len(p[0]) * p[1] * 0.27) / 2 + 20
    if k == "quote": return (860 if p[2] < 50 else 1000) / 2 + 80
    if k == "bars": n = len(p["data"]); return (n * p.get("bw", 120) + (n - 1) * p.get("gap", 70)) / 2 + 40
    if k == "grid": return 760
    if k == "chain": return 860
    if k == "screen": return 320
    if k == "stamp": return 170
    if k == "note": return len(p) * 7.5
    if k == "chart": return 420
    if k == "focus": return 330
    return 200
def half_h(e):
    k, p = e["kind"], e["pay"]
    return {"person": 190, "photo": 260, "cut": (p[1] / 2 + 20) if k == "cut" else 0, "lab": 30, "big": (p[2] * 0.5) if k == "big" else 0,
            "words": 70, "quote": 150, "bars": 260, "grid": 260, "chain": 110, "screen": 260, "stamp": 50, "note": 20, "chart": 260, "focus": 110}.get(k, 80)

SPOT = ("quote", "person", "photo", "cut", "screen", "bars", "chart", "words")
def target(t):
    """bounding box of what is on screen at time t -> (cx, cy, w); a newly arrived key element gets a 2.5 s spotlight"""
    vis = [e for e in X.EL if e["tin"] - 0.2 <= t <= e["tout"] - 0.3]; allvis = list(vis)
    new = [e for e in vis if e["kind"] in SPOT and 0 <= t - e["tin"] <= 2.5]
    if new and len(vis) > 1:
        nw = max(new, key=lambda e: e["tin"]); vis = [nw] + [e for e in vis if e is not nw and abs(e["tin"] - nw["tin"]) < 0.4 and abs(e["x"] - nw["x"]) < 260]
    xs0, xs1, ys0, ys1 = [], [], [], []
    for e in vis:
        x, y = e["x"], e["y"]; hw, hh = half_w(e), half_h(e)
        he = e.get("hero")
        if e["kind"] == "person" and he and t < he + 0.6:
            m = max(0.0, min(1.0, (t - he) / 0.6)); cx, cy = 960, (470 if X.PIN_OF.get(e["b"]) is not None else 540)
            x, y = cx + (x - cx) * m, cy + (y - cy) * m; hw *= X.HERO_SCALE; hh *= X.HERO_SCALE
        if e["kind"] == "big": y -= 10
        xs0.append(x - hw); xs1.append(x + hw); ys0.append(y - hh); ys1.append(y + hh)
    if not xs0: return None
    x0, x1, y0, y1 = min(xs0), max(xs1), min(ys0), max(ys1)
    # never cut a neighbour in half: anything the window would partly cover is pulled fully inside
    others = [(e["x"] - half_w(e), e["x"] + half_w(e), e["y"] - half_h(e), e["y"] + half_h(e)) for e in allvis if e not in vis]
    for _ in range(6):
        w = min(max(x1 - x0 + 120, (y1 - y0 + 120) * ASPECT, 720), 1920); cx = min(max((x0 + x1) / 2, w / 2), 1920 - w / 2)
        wx0, wx1 = cx - w / 2, cx + w / 2; grown = False
        for ex0, ex1, ey0, ey1 in others:
            if ex1 > wx0 + 4 and ex0 < wx1 - 4 and (ex0 < wx0 or ex1 > wx1):
                x0, x1, y0, y1 = min(x0, ex0), max(x1, ex1), min(y0, ey0), max(y1, ey1); grown = True
        if not grown: break
    w = min(max(x1 - x0 + 120, (y1 - y0 + 120) * ASPECT, 720), 1920)
    return (x0 + x1) / 2, (y0 + y1) / 2, w

def wrap(text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t2 = (cur + " " + w).strip()
        if f.getlength(t2) <= maxw: cur = t2
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def bg(title):
    im = V.bg().resize((SW, SH)).convert("RGB"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SW, 150], fill=NAVY_US); d.rectangle([0, 148, SW, 156], fill=RED_US)
    em = X.emblem_us(52).convert("RGBA"); im.paste(em, (32, 14), em); d.text((96, 40), "EMPIRE STORIES", font=font("cardo", 30), fill=IVORY, anchor="lm")
    d.text((540, 108), title, font=font("disp", 50), fill=IVORY, anchor="mm")
    d.rectangle([0, BOT, SW, SH], fill=NAVY_US); d.text((540, 1883), f"FULL STORY · {LABEL} ON THE CHANNEL", font=font("sansb", 26), fill=IVORY, anchor="mm")
    return im

def caption_at(t):
    for m in X.META:
        s0, s1 = m["t"], m["t"] + m["dur"] + 0.1
        if s0 <= t < s1:
            w = m["cap"].split(); ch = [w[i:i + 6] for i in range(0, len(w), 6)]; j = min(len(ch) - 1, int((t - s0) / ((s1 - s0) / len(ch))))
            return " ".join(ch[j])
    return ""

CF = font("sansb", 70)
for sh in json.load(open(f"{EP_DIR}/shorts_v2.json")):
    a, b, name = sh["a"], sh["b"], sh["name"]; dur = b - a; nfr = int(round(dur * 30))
    base = bg(sh["title"]); src = sh["video"]; voff = sh.get("v_off", a)
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{voff:.3f}", "-i", src, "-t", f"{dur:.3f}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", "30", "-"], stdout=subprocess.PIPE)
    tmp = f"{OUT}/{name}.v.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", "30", "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    st = None
    for fi in range(nfr):
        raw = dec.stdout.read(1920 * 1080 * 3)
        if len(raw) < 1920 * 1080 * 3: break
        t = a + fi / 30; frame = Image.frombytes("RGB", (1920, 1080), raw)
        tg = target(t) or (st or (960, 450, 1500))
        if st is None: st = tg
        k = 1 - math.exp(-1 / 30 / 0.35); st = tuple(s_ + (g - s_) * k for s_, g in zip(st, tg))
        cx, cy, w = st; h = w / ASPECT
        x0 = min(max(cx - w / 2, 0), 1920 - w); y0 = cy - h / 2
        if h <= 1080: y0 = min(max(y0, 0), 1080 - h)
        else: y0 = (1080 - h) / 2
        # crop with paper padding when the window is taller than the source
        win = Image.new("RGB", (int(round(w)), int(round(h))), V.bg().convert("RGB").getpixel((960, 540)))
        sx0, sy0 = int(round(x0)), int(round(y0))
        win.paste(frame.crop((sx0, max(0, sy0), sx0 + int(round(w)), min(1080, sy0 + int(round(h))))), (0, max(0, -sy0)))
        win = win.resize((SW, WIN_H), Image.LANCZOS)
        out = base.copy(); out.paste(win, (0, WIN_Y0))
        d = ImageDraw.Draw(out); cap = caption_at(t)
        if cap:
            ls = wrap(cap, CF, 960)
            for j, ln in enumerate(ls): d.text((540, CAP_Y + 90 + (j - (len(ls) - 1) / 2) * 86), ln, font=CF, fill=NAVY_US, anchor="mm")
        enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", sh["audio"],
                    "-filter_complex", f"[1:a]afade=t=in:d=0.3,afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]", "-map", "0:v", "-map", "[au]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/{name}.mp4"], check=True)
    os.remove(tmp); print(name, round(dur, 1), "s", flush=True)
