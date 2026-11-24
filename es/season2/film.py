"""EMPIRE STORIES Season 2 'cinematic' demo renderer: full-screen painted scenes, eased camera with 2.5D row parallax,
film grade, clean title text that fades in/out. usage: python3 film.py <t0> <t1> <out.mp4>"""
import sys, json, math, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
D = "/home/claude/demo2"
VM = json.load(open(f"{D}/vmeta.json"))
def T(i, f=0.0): return VM[i]["t0"] + f * VM[i]["dur"]
END = VM[-1]["t0"] + VM[-1]["dur"] + 3.2
MONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
DMS = "/usr/share/fonts/truetype/google-fonts/ofl/dmsans/DMSans[opsz,wght].ttf"
def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try: f.set_variation_by_axes([wght] if "Montserrat" in path else [14, wght])
    except Exception: pass
    return f
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eio(x): x = min(1, max(0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)

# ---------- film grade (applied once per source image) ----------
def grade(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1)                                  # contrast
    a = a * a * (3 - 2 * a) * 0.35 + a * 0.65                                    # soft S-curve
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[..., None]
    sh = np.clip(1 - lum * 2, 0, 1); hi = np.clip(lum * 2 - 1, 0, 1)
    a = a + sh * np.array([-0.025, 0.01, 0.035]) + hi * np.array([0.035, 0.012, -0.03])   # teal shadows, warm highlights
    a = lum + (a - lum) * 1.08                                                   # a touch more colour
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
@functools.lru_cache(maxsize=16)
def SRC(name):
    im = Image.open(f"{D}/img/{name}").convert("RGB")
    im = im.resize((2880, int(2880 * im.height / im.width)), Image.LANCZOS)     # work at 1.5x for crisp zooms
    return np.asarray(grade(im))
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.42 * np.clip((np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - 0.55) / 0.8, 0, 1) ** 1.5)[..., None].astype(np.float32)
rng = np.random.default_rng(5)
GRAIN = [(rng.standard_normal((H // 2, W // 2)) * 7).astype(np.float32) for _ in range(6)]

def view(name, cx, cy, z, par=0.0):
    """crop of source at centre (cx,cy) in 0..1, zoom z (1 = whole width), with row parallax 'par' px (near rows move more)"""
    s = SRC(name); sh, sw = s.shape[:2]
    cw = sw / z; ch = cw * H / W
    if ch > sh: ch = sh; cw = ch * W / H
    x0 = np.clip(cx * sw - cw / 2, 0, sw - cw); y0 = np.clip(cy * sh - ch / 2, 0, sh - ch)
    ys = (y0 + (np.arange(H) + 0.5) * ch / H).astype(np.int32).clip(0, sh - 1)
    depth = (np.arange(H) / H) ** 1.6                                            # bottom of frame = nearer = moves more
    xs = x0 + (np.arange(W)[None, :] + 0.5) * cw / W + (par * depth * sw / W / z)[:, None]
    xs = np.clip(xs, 0, sw - 1).astype(np.int32)
    return s[ys[:, None], xs]

# ---------- shots: (t_start, image, (cx0,cy0,z0) -> (cx1,cy1,z1), parallax px over the shot) ----------
SHOTS = [
    (0.0, "s1_busy.png", (0.5, 0.55, 1.0), (0.5, 0.52, 1.14), 0),
    (T(1), "s1_busy.png", (0.30, 0.62, 1.55), (0.62, 0.60, 1.6), 70),
    (T(2), "s2_closed.png", (0.5, 0.5, 1.0), (0.5, 0.52, 1.07), 0),
    (T(3), "s2_closed.png", (0.5, 0.66, 1.9), (0.5, 0.66, 2.1), 0),
    (T(4), "s2_closed.png", (0.5, 0.55, 1.25), (0.5, 0.5, 1.02), 0),
    (T(5), "s4_kitchen.png", (0.62, 0.45, 1.6), (0.55, 0.45, 1.4), -40),
    (T(6), "s3_burger.png", (0.45, 0.5, 1.15), (0.5, 0.52, 1.3), 0),
    (T(6, 0.62), "s3_burger.png", (0.72, 0.72, 1.9), (0.7, 0.72, 2.1), 0),
    (T(7), "s4_kitchen.png", (0.30, 0.55, 1.35), (0.65, 0.55, 1.35), 90),
    (T(8), "s5_kroc_office.png", (0.45, 0.5, 1.05), (0.5, 0.5, 1.2), 0),
    (T(9), "s5_kroc_office.png", (0.47, 0.5, 1.5), (0.58, 0.5, 1.75), 30),
    (T(10), "s5_kroc_office.png", (0.64, 0.5, 2.4), (0.64, 0.5, 2.7), 0),
    (T(11), "s6_road.png", (0.35, 0.55, 1.25), (0.42, 0.55, 1.1), 80),
    (T(12), "s7_queue.png", (0.4, 0.5, 1.15), (0.55, 0.5, 1.02), 40),
]
XF = 0.55                                                                        # crossfade seconds
BLACK_AT = T(2)                                                                  # dip to black before "And then... they shut it down."
def shot_frame(k, t):
    t0, name, a, b, par = SHOTS[k]; t1 = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else END
    u = eio((t - t0) / max(0.1, t1 + XF - t0))
    cx, cy, z = [a[i] + (b[i] - a[i]) * u for i in range(3)]
    return view(name, cx, cy, z, par * (u - 0.5)).astype(np.float32)

# ---------- titles ----------
def title_layer(top, big, sub, align="left", big_size=120):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ft = font(DMS, 34, 700); fb = font(MONT, big_size, 800); fs = font(DMS, 36, 500)
    x = 140 if align == "left" else W // 2; anc = "l" if align == "left" else "m"
    y = H - 300 if align == "left" else H // 2 + int(0.3 * big_size)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    def put(dd, yy_, s, f, col, sp=0):
        if sp:
            s = " ".join(s)
        dd.text((x, yy_), s, font=f, fill=col, anchor=anc + "s")
    if top:
        ty = y - int(0.74 * big_size) - 34; put(ds, ty, top, ft, (0, 0, 0, 200), 1); put(d, ty, top, ft, (212, 175, 55, 255), 1)
    put(ds, y + 4, big, fb, (0, 0, 0, 210)); put(d, y, big, fb, (255, 255, 255, 255))
    if sub: put(ds, y + 70, sub, fs, (0, 0, 0, 200)); put(d, y + 64, sub, fs, (236, 232, 222, 255))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); db = ImageDraw.Draw(bg)
    if align == "left": db.rectangle([0, y - big_size - 120, 1150, y + 130], fill=(5, 8, 18, 120))
    else: db.ellipse([W // 2 - 760, y - big_size - 150, W // 2 + 760, y + 170], fill=(5, 8, 18, 135))
    bg = bg.filter(ImageFilter.GaussianBlur(90))
    return Image.alpha_composite(Image.alpha_composite(bg, sh), lay)
TITLES = [  # (t_in, t_out, top, big, sub, align, size)
    (1.0, T(1, 0.55), "EMPIRE STORIES", "SAN BERNARDINO", "California · 1948", "left", 120),
    (T(3, 0.05), T(4, 0.9), None, "CLOSED", "for three months", "left", 150),
    (T(6, 0.42), T(6, 0.62), "THE NEW MENU", "9 ITEMS", "no plates · no waitresses", "left", 150),
    (T(6, 0.82), T(7, 0.2), "A HAMBURGER", "15¢", None, "center", 240),
    (T(7, 0.25), T(7, 1.0) + 0.6, None, "THE SPEEDEE SYSTEM", "every man, one job", "left", 104),
    (T(8, 0.12), T(8, 0.95), None, "CHICAGO", "1954", "left", 130),
    (T(10, 0.0), T(10, 1.0) + 0.5, "MULTIMIXERS ORDERED", "8", "by one small restaurant", "center", 300),
    (T(11, 0.15), T(11, 1.0), None, "RAY KROC", "milkshake-machine salesman · age 52", "left", 130),
    (T(12, 0.6), END - 0.4, "THE STORY OF", "McDONALD'S", "1940 – 2026", "center", 150),
]
@functools.lru_cache(maxsize=16)
def TL(i):
    _, _, top, big, sub, al, sz = TITLES[i]; return np.asarray(title_layer(top, big, sub, al, sz)).astype(np.float32) / 255

def frame(t):
    k = max(i for i, s in enumerate(SHOTS) if s[0] <= t)
    img = shot_frame(k, t)
    if k > 0 and t - SHOTS[k][0] < XF and SHOTS[k][0] != BLACK_AT:
        f = eio((t - SHOTS[k][0]) / XF); img = shot_frame(k - 1, t) * (1 - f) + img * f
    # dip to black around the 'shut it down' moment, and fade in/out of the whole film
    b = 1.0
    if BLACK_AT - 0.45 < t < BLACK_AT + 0.6: b = min(1, abs(t - BLACK_AT) / 0.45) if t < BLACK_AT else min(1, (t - BLACK_AT) / 0.6)
    b *= min(1, t / 0.8) * min(1, (END - t) / 1.0)
    img = img * b
    for i, (ti, to, *_r) in enumerate(TITLES):
        if ti - 0.01 <= t <= to + 0.01:
            a = eio((t - ti) / 0.7) * eio((to - t) / 0.7)
            if a <= 0: continue
            L = TL(i); dy = int((1 - a) * 18)
            if dy: L = np.roll(L, dy, axis=0)
            al = L[..., 3:4] * a; img = img * (1 - al) + L[..., :3] * 255 * al
    img = img * VIG
    g = GRAIN[int(t * FPS) % len(GRAIN)]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    return np.clip(img + g, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for t in sys.argv[2].split(","): Image.fromarray(frame(float(t))).save(f"{D}/still_{t}.jpg", quality=88)
        sys.exit()
    a, b, out = float(sys.argv[1]), min(float(sys.argv[2]), END), sys.argv[3]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out + ".tmp.mp4"], stdin=subprocess.PIPE)
    for n in range(int(round((b - a) * FPS))): p.stdin.write(frame(a + n / FPS).tobytes())
    p.stdin.close(); p.wait(); import os; os.replace(out + ".tmp.mp4", out); print("done", a, b, END)
