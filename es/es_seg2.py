"""EMPIRE STORIES Ep001 demo 2: 'The art of subtraction' -> iMac. Real licensed photos in an editorial collage."""
import sys, math, random, subprocess, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import es_demo as E
from es_demo import W, H, FPS, NAVY, GOLD, IVORY, CHAR, place, txt, wtxt, words_in, gold_line, dust, r, eo, eio, eo5, cl, font, BG

RED = (205, 70, 58)
A = "/home/claude/es/assets/"

@functools.lru_cache(None)
def collage(name, h, border=10, rot_seed=0):
    """photo cutout with ivory scissor border + soft shadow"""
    im = Image.open(A + name).convert("RGBA"); s = h / im.height; im = im.resize((int(im.width * s), h), Image.LANCZOS)
    pad = border + 40; big = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0)); big.alpha_composite(im, (pad, pad))
    a = big.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    grown = a
    for _ in range(max(1, border // 7)): grown = grown.filter(ImageFilter.MaxFilter(15))
    rng = np.random.default_rng(rot_seed)
    nz = Image.fromarray((rng.random((big.height // 5 + 1, big.width // 5 + 1)) * 255).astype(np.uint8)).resize(big.size, Image.BICUBIC)
    g = np.asarray(grown.filter(ImageFilter.GaussianBlur(2)), np.float32) + (np.asarray(nz, np.float32) - 128) * 0.35
    edge = Image.fromarray(((g > 128) * 255).astype(np.uint8))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0)); sh.putalpha(edge.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)))
    out.alpha_composite(sh, (10, 16))
    wl = Image.new("RGBA", big.size, IVORY + (255,)); wl.putalpha(edge); out.alpha_composite(wl); out.alpha_composite(big)
    return out

@functools.lru_cache(None)
def photo_card(name, w, border=14):
    im = Image.open(A + name).convert("RGB"); s = w / im.width; im = im.resize((w, int(im.height * s)), Image.LANCZOS)
    card = Image.new("RGBA", (im.width + border * 2 + 40, im.height + border * 2 + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([20, 20, card.width - 20, card.height - 20], fill=(0, 0, 0, 140))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (8, 14))
    ImageDraw.Draw(card).rectangle([20, 20, card.width - 21, card.height - 21], fill=IVORY + (255,)); card.paste(im, (20 + border, 20 + border))
    return card

def rot(im, deg): return im.rotate(deg, expand=True, resample=Image.BICUBIC)

@functools.lru_cache(None)
def stamp_img(text, size=60, color=RED, seed=3):
    f = font("sansb", size); tw = E.ImageDraw.Draw(Image.new("L", (4, 4))).textlength(text, font=f)
    w, h = int(tw + size * 1.2), int(size * 1.9); k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([6 * k, 6 * k, (w - 6) * k, (h - 6) * k], outline=color + (255,), width=6 * k)
    d.text((w * k / 2, h * k / 2), text, font=font("sansb", size * k), fill=color + (255,), anchor="mm")
    im = im.resize((w, h), Image.LANCZOS); a = np.asarray(im.getchannel("A"), np.float32)
    n = np.random.default_rng(seed).random(a.shape); a = a * (0.75 + 0.25 * (n > 0.3)) * (n > 0.05)
    im.putalpha(Image.fromarray(a.clip(0, 255).astype(np.uint8))); return im
def stamp(im, text, x, y, t, t0, size=60, deg=-8, color=RED):
    a = r(t, t0, t0 + 0.2)
    if a <= 0: return
    place(im, rot(stamp_img(text, size, color), deg), x, y, scale=1.7 - 0.7 * eo(a), alpha=min(1, a * 1.6))

def credit(im, text, alpha=1.0):
    place(im, txt(text, "sansm", 17, (150, 156, 175)), W - 30 - txt(text, "sansm", 17, (150, 156, 175)).width / 2, 30, alpha=alpha * 0.9)

def hl_label(im, text, x, y, t, t0, size=30, left=True):
    """ivory text strip with a gold highlighter swipe, editorial callout"""
    a = r(t, t0, t0 + 0.3)
    if a <= 0: return
    ti = txt(text, "sansb", size, NAVY, 2); w, h = ti.width + 28, ti.height + 14
    p = eo(r(t, t0 + 0.15, t0 + 0.6))
    lay = Image.new("RGBA", (w, h), IVORY + (255,)); d = ImageDraw.Draw(lay); d.rectangle([0, 0, int(w * p), h], fill=GOLD + (255,))
    lay.alpha_composite(ti, (14, 7)); place(im, lay, x + (w / 2 if left else -w / 2), y, alpha=eio(a))

def leader(im, x0, y0, x1, y1, prog):
    if prog <= 0: return
    d = ImageDraw.Draw(im); xe, ye = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog
    d.line([(x0, y0), (xe, ye)], fill=GOLD + (255,), width=3); d.ellipse([x0 - 7, y0 - 7, x0 + 7, y0 + 7], fill=GOLD + (255,))

CAPS = [(0.2, 7.4, "So he cut. Roughly seventy percent of Apple's products were cancelled, including the Newton handheld."),
        (7.7, 12.4, "Then, at a whiteboard, he drew a grid. Two columns: Consumer and Pro."),
        (12.4, 16.4, "Two rows: Desktop and Portable. Four boxes."),
        (16.7, 21.4, "And one box was still empty: a computer for ordinary people at home."),
        (21.9, 24.7, "On May 6th, 1998, Jobs filled it."),
        (24.9, 33.4, "The iMac looked like no other computer: an all-in-one machine in translucent blue-green plastic, with a handle on top."),
        (33.7, 39.9, "It made bold bets too. No floppy disk drive. New USB ports instead of Apple's old connectors."),
        (40.2, 46.0, "It went on sale on August 15th, 1998, for one thousand two hundred and ninety-nine dollars."),
        (46.0, 52.9, "In its first six weeks, Apple shipped two hundred and seventy-eight thousand iMacs."),
        (53.2, 60.8, "When fiscal 1998 closed, Apple reported a profit of $309 million. Its first profitable year since 1995.")]
def captions(im, t):
    for a, b, text in CAPS:
        if a <= t < b:
            ti = txt(text, "sansm", 32, IVORY); box = Image.new("RGBA", (ti.width + 40, ti.height + 18), (8, 12, 26, 175)); box.alpha_composite(ti, (20, 9))
            place(im, box, W / 2, H - 56, alpha=min(r(t, a, a + 0.2), 1 - r(t, b - 0.2, b))); return

# ---------- shots ----------
TILES = ["Performa 5260", "Performa 6400", "Power Mac 4400", "Power Mac 7300", "PowerBook 1400", "PowerBook 3400", "eMate 300", "Newton MP2100",
         "Performa 6360", "Power Mac 8600", "Power Mac 9600", "PowerBook 2400", "Performa 5400", "Power Mac 6500", "Twentieth Anniv. Mac", "QuickTake 200",
         "Performa 6320", "Power Mac 5500", "StyleWriter 4500", "LaserWriter 8500", "Apple Studio Display", "Pippin", "Power Mac 7600", "Performa 4400"]
def sh_cut(t):              # 0 - 7.6
    im = BG.copy(); dust(im, t, 0.4)
    rng = random.Random(4)
    for i, name in enumerate(TILES):
        cx, cy = 260 + (i % 6) * 280, 200 + (i // 6) * 150
        dead = rng.random() < 0.72 and name != "Power Mac 8600"
        appear = r(t, 0.1 + i * 0.03, 0.4 + i * 0.03)
        fall = eio(r(t, 2.6 + rng.random() * 1.2, 3.6 + rng.random() * 1.2)) if dead else 0
        if appear <= 0: continue
        ti = txt(name, "sansm", 22, IVORY); card = Image.new("RGBA", (250, 100), (20, 30, 62, 230)); d = ImageDraw.Draw(card)
        d.rectangle([0, 0, 249, 99], outline=(70, 86, 130, 255), width=2); card.alpha_composite(ti, (int(125 - ti.width / 2), 36))
        place(im, card, cx, cy + fall * 900 + (1 - appear) * 20, alpha=appear * (1 - fall * 0.6))
    a = eo5(r(t, 3.9, 4.4))
    if a > 0:
        place(im, txt("−70%", "disp", 190, GOLD), W / 2, 470, scale=1.3 - 0.3 * a, alpha=a * (1 - r(t, 5.0, 5.3)))
    if t > 5.0:   # Newton cut-out + CANCELLED stamp
        im.alpha_composite(Image.new("RGBA", (W, H), NAVY + (int(170 * r(t, 5.0, 5.4)),)))
        nx = W / 2 + (1 - eo(r(t, 5.0, 5.6))) * 900
        place(im, rot(collage("newton_cut.png", 560, 12, 2), -6), nx, 500)
        hl_label(im, "APPLE NEWTON MESSAGEPAD", 1180, 330, t, 5.6, 28)
        stamp(im, "CANCELLED", W / 2 + 40, 560, t, 6.3, 74, -10)
        credit(im, "Photo: Felix Winkelnkemper, CC BY-SA 4.0", r(t, 5.4, 5.8))
    return im

GX0, GY0, GW, GH = 560, 150, 800, 680
def grid(im, t, t0, labels=True, fill=None):
    d = ImageDraw.Draw(im); p1 = eo(r(t, t0, t0 + 0.8)); p2 = eo(r(t, t0 + 0.5, t0 + 1.3))
    if p1 > 0: d.line([(GX0 + GW / 2, GY0), (GX0 + GW / 2, GY0 + GH * p1)], fill=GOLD + (255,), width=5)
    if p2 > 0: d.line([(GX0, GY0 + GH / 2), (GX0 + GW * p2, GY0 + GH / 2)], fill=GOLD + (255,), width=5)
    if labels:
        for (s, x, y, tt) in [("CONSUMER", GX0 + GW / 4, GY0 - 40, t0 + 1.2), ("PRO", GX0 + 3 * GW / 4, GY0 - 40, t0 + 1.6),
                              ("DESKTOP", GX0 - 150, GY0 + GH / 4, t0 + 2.6), ("PORTABLE", GX0 - 150, GY0 + 3 * GH / 4, t0 + 3.0)]:
            place(im, txt(s, "sansb", 34, IVORY, 8), x, y, alpha=r(t, tt, tt + 0.4))

def sh_grid(t):             # 7.6 - 24.8
    tt = t - 7.6; im = BG.copy(); dust(im, t, 0.4)
    grid(im, tt, 0.2)
    four = r(tt, 7.6, 8.0)
    if four > 0: place(im, txt("4 BOXES. 4 PRODUCTS.", "sansb", 30, GOLD, 8), GX0 + GW / 2, GY0 + GH + 50, alpha=four * (1 - r(tt, 14.0, 14.5)))
    # pro desktop: real Power Mac G3 photo
    a = eo(r(tt, 4.6, 5.3))
    if a > 0:
        place(im, rot(collage("powermac_beige_cut.png", 240, 9, 5), 3), GX0 + 3 * GW / 4, GY0 + GH / 4 + (1 - a) * -300, alpha=a)
        place(im, txt("POWER MAC G3", "sansb", 20, IVORY, 4), GX0 + 3 * GW / 4, GY0 + GH / 2 - 22, alpha=a)
        credit(im, "Photo: Klodo6975, public domain", a * (1 - r(tt, 14.3, 14.6)))
    b = r(tt, 5.6, 6.2)
    if b > 0:
        place(im, txt("POWERBOOK G3", "sansb", 26, IVORY, 4), GX0 + 3 * GW / 4, GY0 + 3 * GH / 4, alpha=b)
        place(im, txt("(1997)", "sansm", 20, (150, 156, 175)), GX0 + 3 * GW / 4, GY0 + 3 * GH / 4 + 36, alpha=b)
    c = r(tt, 6.4, 7.0)
    if c > 0: place(im, txt("LATER: iBOOK", "sansm", 22, (150, 156, 175), 4), GX0 + GW / 4, GY0 + 3 * GH / 4, alpha=c)
    # empty consumer desktop box pulses
    if tt > 9.1:
        pul = 0.5 + 0.5 * math.sin((tt - 9.1) * 4)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rectangle([GX0 + 14, GY0 + 14, GX0 + GW / 2 - 14, GY0 + GH / 2 - 14], outline=GOLD + (int(90 + 120 * pul),), width=4)
        im.alpha_composite(lay)
        if tt < 14.4: place(im, txt("?", "serif", 160, GOLD), GX0 + GW / 4, GY0 + GH / 4, alpha=r(tt, 9.3, 9.9) * (0.6 + 0.4 * pul))
    if tt > 14.3:   # iMac flies into the empty box
        f = eo5(r(tt, 14.3, 15.1))
        x = GX0 + GW / 4 + (1 - f) * -700; y = GY0 + GH / 4 + (1 - f) * 200
        place(im, rot(collage("imac34_cut.png", 250, 9, 7), -3), x, y, alpha=f)
        place(im, txt("iMAC", "sansb", 22, GOLD, 6), GX0 + GW / 4, GY0 + GH / 2 - 22, alpha=r(tt, 15.0, 15.4))
        stamp(im, "MAY 6, 1998", GX0 + GW / 4 + 40, GY0 + GH / 2 + 60, tt, 15.2, 40, -6, GOLD)
        credit(im, "Photos: Rama, alterations by David Fuchs, CC BY-SA 4.0; Klodo6975, public domain", r(tt, 14.6, 15.0))
    return im

def sh_imac(t):             # 24.8 - 40.1  hero photo with editorial callouts
    tt = t - 24.8; im = BG.copy(); dust(im, t, 0.5)
    z = 1.0 + 0.06 * tt / 15.3
    cx, cy = 820 - tt * 6, 520
    hero = collage("imac34_cut.png", 640, 14, 7)
    place(im, rot(hero, -2), cx, cy, scale=z * (0.9 + 0.1 * eo(r(tt, 0, 0.8))), alpha=eio(r(tt, 0, 0.5)))
    # callouts (points on the photo approx, relative to center)
    P = lambda dx, dy: (cx + dx * z, cy + dy * z)
    calls = [("ALL-IN-ONE", (-170, -90), (1240, 220), 2.0), ("TRANSLUCENT \"BONDI BLUE\"", (150, -120), (1240, 330), 4.0),
             ("HANDLE ON TOP", (-20, -300), (1240, 440), 6.8), ("NO FLOPPY DRIVE", (-150, 230), (1240, 600), 10.6), ("USB PORTS", (240, 150), (1240, 710), 12.9)]
    for text, (dx, dy), (lx, ly), t0 in calls:
        x0, y0 = P(dx, dy); leader(im, x0, y0, lx - 10, ly, eo(r(tt, t0, t0 + 0.5)))
        hl_label(im, text, lx, ly, tt, t0 + 0.4, 30)
    if tt > 10.6: stamp(im, "NO FLOPPY", 560, 860, tt, 10.9, 46, -7)
    credit(im, "Photo: Rama, alterations by David Fuchs, CC BY-SA 4.0")
    return im

def sh_sale(t):             # 40.1 - 53.1
    tt = t - 40.1; im = BG.copy(); dust(im, t, 0.5)
    card = rot(photo_card("imac_lineup_crop.jpg", 900), 2)
    place(im, card, 640, 470 + (1 - eo(r(tt, 0, 0.7))) * 600)
    place(im, txt("Later iMac colours, 1999", "sansm", 20, (170, 176, 195)), 640, 800, alpha=r(tt, 0.6, 1.0))
    credit(im, "Photo: Stephen Hackett, CC BY-SA 4.0")
    stamp(im, "AUG 15, 1998", 1440, 260, tt, 1.0, 46, -6, GOLD)
    a = eo5(r(tt, 3.2, 3.8))
    if a > 0:
        tag = Image.new("RGBA", (420, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(tag)
        d.rounded_rectangle([0, 0, 419, 169], 14, fill=IVORY + (255,)); d.ellipse([22, 70, 46, 94], fill=NAVY + (255,))
        tag.alpha_composite(txt("$1,299", "disp", 100, NAVY), (90, 22))
        place(im, rot(tag, -5), 1440, 450, scale=0.6 + 0.4 * a, alpha=a)
    if tt > 5.9:
        n = int(278000 * eo(r(tt, 6.2, 9.5)))
        place(im, txt(f"{n:,}", "disp", 130, GOLD), 1440, 690, alpha=r(tt, 5.9, 6.3))
        place(im, txt("iMACS SHIPPED IN 6 WEEKS", "sansb", 26, IVORY, 5), 1440, 790, alpha=r(tt, 6.3, 6.8))
        if tt > 9.6: hl_label(im, "FASTEST-SELLING MAC EVER", 1250, 860, tt, 9.6, 26)
    return im

NI = [("FY1996", -816), ("FY1997", -1045), ("FY1998", 309)]
def sh_profit(t):           # 53.1 - 63.5
    tt = t - 53.1; im = BG.copy(); dust(im, t, 0.5); d = ImageDraw.Draw(im)
    place(im, txt("APPLE NET INCOME", "sansb", 30, GOLD, 10), W / 2, 130, alpha=r(tt, 0.1, 0.6))
    zero = 470; sc = 300 / 1045; x0 = 660
    d.line([(520, zero), (1400, zero)], fill=(150, 156, 175), width=2)
    for i, (fy, v) in enumerate(NI):
        x = x0 + i * 300; p = eo(r(tt, 0.3 + i * 0.5, 1.0 + i * 0.5)); h = v * sc * p
        col = GOLD if v > 0 else RED
        if abs(h) > 1: d.rectangle([x - 70, min(zero, zero - h), x + 70, max(zero, zero - h)], fill=col + (255,))
        if p > 0.9:
            lab = (f"+${v}M" if v > 0 else (f"−${-v/1000:.2f}B" if -v >= 1000 else f"−${-v}M"))
            place(im, txt(lab, "disp", 40, col), x, zero - h - (34 if v > 0 else -34))
        place(im, txt(fy, "sansb", 26, IVORY, 4), x, 870, alpha=r(tt, 0.3 + i * 0.5, 0.8 + i * 0.5))
    if tt > 2.4: hl_label(im, "FIRST PROFITABLE YEAR SINCE 1995", 1060, 220, tt, 2.6, 28)
    place(im, txt("Sources: Apple results via TidBITS (Oct 1997, Oct 1998); FY1997 as filed", "sansm", 18, (140, 146, 165)), W / 2, 960, alpha=r(tt, 1.0, 1.5))
    fo = r(tt, 9.4, 10.4)
    if fo > 0: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
    return im

SHOTS = [(0.0, 7.6, sh_cut), (7.6, 24.8, sh_grid), (24.8, 40.1, sh_imac), (40.1, 53.1, sh_sale), (53.1, 63.5, sh_profit)]
DUR = 63.5; XF = 0.45
VIG = None
def frame(t):
    global VIG
    im, start = None, 0
    for a, b, fn in SHOTS:
        if a <= t < b: im, start = fn(t), a; break
    if im is None: im, start = SHOTS[-1][2](t), SHOTS[-1][0]
    if 0 < start and t - start < XF:
        prev = [s for s in SHOTS if s[1] == start][0][2](start - 0.001); im = Image.blend(prev, im, eio((t - start) / XF))
    captions(im, t)
    arr = np.asarray(im.convert("RGB"), np.int16)
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; VIG = (1 - 0.30 * (((xx - W / 2) / (W / 1.15)) ** 2 + ((yy - H / 2) / (H / 0.95)) ** 2)).astype(np.float32)[..., None]
    arr = (arr + E.GRAIN[int(t * 24) % 6] // 2) * VIG
    return arr.clip(0, 255).astype(np.uint8)

def render(t0, t1, path):
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f_ in range(int(round(t0 * FPS)), int(round(t1 * FPS))): p.stdin.write(frame(f_ / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, path)

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        c = Image.new("RGB", (640 * 3, 360 * ((len(ts) + 2) // 3)))
        for i, t in enumerate(ts): c.paste(Image.fromarray(frame(t)).resize((640, 360)), ((i % 3) * 640, (i // 3) * 360))
        c.save("/home/claude/es/out/_s2.jpg", quality=85)
    else:
        a, b = float(sys.argv[2]), float(sys.argv[3]); render(a, b, f"/home/claude/es/out/s2_{int(a*10):04d}.mp4")
