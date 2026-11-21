"""EMPIRE STORIES - Ep001 cold-open demo (graphics only, brand: navy / gold / ivory / charcoal)."""
import math, os, subprocess, sys, functools, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
OUT = "/home/claude/es/out"; os.makedirs(OUT, exist_ok=True)
NAVY = (11, 19, 43); GOLD = (212, 175, 55); IVORY = (244, 241, 234); CHAR = (23, 23, 23); NAVY2 = (22, 33, 66); RED = (196, 72, 60)
G = "/usr/share/fonts/truetype/google-fonts/"
@functools.lru_cache(None)
def font(k, s):
    p = {"serif": G + "ofl/crimsontext/CrimsonText-SemiBold.ttf", "serifb": G + "ofl/crimsontext/CrimsonText-Bold.ttf",
         "serifi": G + "ofl/crimsontext/CrimsonText-SemiBoldItalic.ttf", "cardo": G + "ofl/cardo/Cardo-Bold.ttf",
         "sans": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "sansb": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
         "sansm": "/usr/share/fonts/opentype/inter/Inter-Medium.otf", "disp": "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"}[k]
    return ImageFont.truetype(p, s)

def cl(x): return max(0.0, min(1.0, x))
def r(t, a, b): return cl((t - a) / (b - a)) if b > a else float(t >= a)
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def eo5(x): x = cl(x); return 1 - (1 - x) ** 5

def place(dst, src, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.003 or scale <= 0.005: return
    s = src; w, h = max(1, int(s.width * scale)), max(1, int(s.height * scale))
    if (w, h) != s.size: s = s.resize((w, h), Image.BICUBIC)
    if alpha < 1: s = s.copy(); s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    dst.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

@functools.lru_cache(None)
def txt(text, k, size, color=IVORY, track=0):
    f = font(k, size)
    if track:
        ws = [ImageDraw.Draw(Image.new("L", (4, 4))).textlength(c, font=f) for c in text]
        tw = int(sum(ws) + track * (len(text) - 1)) + 10; bb = f.getbbox("Hg")
        im = Image.new("RGBA", (tw, bb[3] + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 5
        for c, w_ in zip(text, ws): d.text((x, 4), c, font=f, fill=color); x += w_ + track
        return im
    bb = ImageDraw.Draw(Image.new("L", (4, 4))).textbbox((0, 0), text, font=f)
    im = Image.new("RGBA", (bb[2] - bb[0] + 12, bb[3] - bb[1] + 12), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((6 - bb[0], 6 - bb[1]), text, font=f, fill=color); return im

# ---------------- backgrounds ----------------
def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xx - W * 0.5) / W, (yy - H * 0.42) / H)
    a = np.array(NAVY2, np.float32) * (1 - d[..., None] * 1.3).clip(0, 1) + np.array(NAVY, np.float32) * (d[..., None] * 1.3).clip(0, 1)
    a = a * (1 - 0.55 * (d[..., None] ** 2))
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
BG = make_bg()
rng0 = np.random.default_rng(1)
GRAIN = [rng0.normal(0, 5, (H, W, 1)).astype(np.int16) for _ in range(6)]
DUST = [(rng0.random() * W, rng0.random() * H, 0.6 + rng0.random() * 2.2, rng0.random() * 6.28, 0.2 + rng0.random() * 0.6) for _ in range(70)]
def dust(im, t, amt=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, s, ph, sp in DUST:
        X = (x + t * 14 * sp) % W; Y = (y - t * 9 * sp + 6 * math.sin(t * 0.5 + ph)) % H
        a = int(amt * 110 * (0.5 + 0.5 * math.sin(t * 0.8 + ph)))
        d.ellipse([X - s, Y - s, X + s, Y + s], fill=GOLD + (a,))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))

# ---------------- map ----------------
MASKHEX = open("/home/claude/v3/landmask_192x96.hex").read().strip()
MASK = np.array([int(c) for c in bin(int(MASKHEX, 16))[2:].zfill(len(MASKHEX) * 4)], np.uint8).reshape(96, 192)
LON0, LON1, LAT0, LAT1 = -136, -54, 54, 14; KPX = 60; CXF = math.cos(math.radians(35))
MPW, MPH = int((LON1 - LON0) * KPX * CXF), int((LAT0 - LAT1) * KPX)
def mp(lon, lat): return ((lon - LON0) * KPX * CXF, (LAT0 - lat) * KPX)
def make_map():
    c0, c1 = int((LON0 + 180) / 360 * 192) - 2, int((LON1 + 180) / 360 * 192) + 2; r0, r1 = int((90 - LAT0) / 180 * 96) - 2, int((90 - LAT1) / 180 * 96) + 2
    sub = Image.fromarray((MASK[r0:r1, c0:c1] * 255).astype(np.uint8))
    lon_a, lon_b = c0 / 192 * 360 - 180, c1 / 192 * 360 - 180; lat_a, lat_b = 90 - r0 / 96 * 180, 90 - r1 / 96 * 180
    fw, fh = int((lon_b - lon_a) * KPX * CXF), int((lat_a - lat_b) * KPX)
    big = sub.resize((fw, fh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
    ox, oy = int((LON0 - lon_a) * KPX * CXF), int((lat_a - LAT0) * KPX)
    land = big.crop((ox, oy, ox + MPW, oy + MPH)).point(lambda v: 255 if v > 118 else 0)
    FL = [(-87.6, 31.0), (-87.4, 30.35), (-86.5, 30.4), (-85.4, 29.95), (-84.9, 29.7), (-84.3, 30.05), (-83.6, 29.85), (-83.0, 29.15),
          (-82.75, 28.2), (-82.65, 27.6), (-82.2, 26.85), (-81.8, 26.1), (-81.25, 25.6), (-80.95, 25.15), (-80.45, 25.2), (-80.15, 25.75),
          (-80.05, 26.6), (-80.2, 27.3), (-80.5, 28.0), (-80.6, 28.45), (-81.0, 29.2), (-81.3, 29.9), (-81.45, 30.7), (-82.0, 30.6),
          (-84.9, 30.7), (-85.0, 31.0)]
    ImageDraw.Draw(land).polygon([mp(*p) for p in FL], fill=255)
    land = land.filter(ImageFilter.GaussianBlur(3)).point(lambda v: 255 if v > 128 else 0)
    m = Image.new("RGBA", (MPW, MPH), NAVY + (255,)); d = ImageDraw.Draw(m)
    for g in range(-130, -59, 5): x = (g - LON0) * KPX * CXF; d.line([(x, 0), (x, MPH)], fill=(30, 42, 74), width=2)
    for g in range(20, 53, 5): y = (LAT0 - g) * KPX; d.line([(0, y), (MPW, y)], fill=(30, 42, 74), width=2)
    glow = land.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
    m.paste((60, 80, 130, 255), (0, 0), glow.point(lambda v: int(v * 0.5)))
    m.paste((36, 50, 92, 255), (0, 0), land)
    edge = Image.fromarray((np.asarray(land.filter(ImageFilter.MaxFilter(5)), np.int16) - np.asarray(land, np.int16)).clip(0, 255).astype(np.uint8))
    m.paste((170, 160, 130, 255), (0, 0), edge)
    return m
USMAP = make_map()
def map_view(lon, lat, s):
    mx, my = mp(lon, lat); cw, ch = W / s, H / s; x0, y0 = mx - cw / 2, my - ch / 2
    crop = USMAP.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BICUBIC)
    def P(lo, la): px, py = mp(lo, la); return ((px - int(x0)) * W / int(cw), (py - int(y0)) * H / int(ch))
    return crop, P

# ---------------- elements ----------------
def gold_line(im, x0, y, x1, prog, w=3):
    if prog <= 0: return
    d = ImageDraw.Draw(im); d.line([(x0, y), (x0 + (x1 - x0) * prog, y)], fill=GOLD + (255,), width=w)

def lower_third(im, title, sub, t, t0, x=150, y=860):
    a = eo(r(t, t0, t0 + 0.6))
    if a <= 0: return
    gold_line(im, x, y, x + 520, a, 3)
    place(im, txt(title, "sans", 30, IVORY, 4), x + txt(title, "sans", 30, IVORY, 4).width / 2 + (1 - a) * -40, y + 34, alpha=a)
    place(im, txt(sub, "sansm", 24, GOLD, 2), x + txt(sub, "sansm", 24, GOLD, 2).width / 2 + (1 - a) * -40, y + 76, alpha=r(t, t0 + 0.3, t0 + 0.8))

@functools.lru_cache(None)
def wtxt(word, k, size, color):
    f = font(k, size); w = int(ImageDraw.Draw(Image.new("L", (4, 4))).textlength(word, font=f)) + 16
    im = Image.new("RGBA", (w, int(size * 1.7)), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, int(size * 1.15)), word, font=f, fill=color, anchor="ls"); return im

def words_in(im, cx, cy, words, t, t0, size, k="serif", color=IVORY, stagger=0.12, gold_words=(), lh=1.25, maxw=1400):
    """multi-line centered serif text, word-by-word fade-up; returns rects of gold words"""
    f = font(k, size); sp = ImageDraw.Draw(Image.new("L", (4, 4))).textlength(" ", font=f)
    lines, cur, cw = [], [], 0
    for w_ in words:
        ww = ImageDraw.Draw(Image.new("L", (4, 4))).textlength(w_, font=f)
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w_, ww)); cw += (sp if cw else 0) + ww
    if cur: lines.append(cur)
    n = 0; y = cy - (len(lines) - 1) * size * lh / 2; rects = []
    for ln in lines:
        tw = sum(w for _, w in ln) + sp * (len(ln) - 1); x = cx - tw / 2
        for w_, ww in ln:
            a = r(t, t0 + n * stagger, t0 + n * stagger + 0.45)
            col = GOLD if n in gold_words else color
            if a > 0: place(im, wtxt(w_, k, size, col), x + ww / 2, y + (1 - eo(a)) * 18, alpha=eio(a))
            if n in gold_words: rects.append((x, y, x + ww))
            x += ww + sp; n += 1
        y += size * lh
    return rects

def stat_card(im, cx, cy, big, label, t, t0, color=IVORY, flip=None):
    a = eo5(r(t, t0, t0 + 0.6))
    if a <= 0: return
    w, h = 470, 300
    sx = 1.0
    if flip is not None:   # flip value 0..1 -> scaleX
        sx = max(0.02, abs(math.cos(flip * math.pi)))
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=(17, 26, 54, 235), outline=(212, 175, 55, 120), width=2)
    d.line([(40, 210), (w - 40, 210)], fill=GOLD + (150,), width=2)
    card.alpha_composite(txt(big, "disp", 104, color), (int(w / 2 - txt(big, "disp", 104, color).width / 2), 52))
    card.alpha_composite(txt(label, "sans", 22, IVORY, 3), (int(w / 2 - txt(label, "sans", 22, IVORY, 3).width / 2), 232))
    if sx < 0.999: card = card.resize((max(1, int(w * sx)), h), Image.BICUBIC)
    place(im, card, cx, cy + (1 - a) * 120, alpha=a)
flip_to = None

def captions(im, t):
    for a, b, text in CAPS:
        if a <= t < b:
            ti = txt(text, "sansm", 34, IVORY)
            box = Image.new("RGBA", (ti.width + 40, ti.height + 18), (11, 15, 30, 170)); box.alpha_composite(ti, (20, 9))
            place(im, box, W / 2, H - 58, alpha=min(r(t, a, a + 0.2), 1 - r(t, b - 0.2, b))); return

# narration timing (estimated until the real voice is recorded)
CAPS = [(0.3, 3.4, "October 6th, 1997. Orlando, Florida."),
        (3.8, 9.0, "At a technology conference, someone asks Michael Dell,"),
        (9.0, 13.4, "one of the most powerful men in the computer business... what would he do with Apple?"),
        (13.8, 17.3, "His answer becomes one of the most famous lines in tech history."),
        (17.6, 22.6, "\"I'd shut it down and give the money back to the shareholders.\""),
        (23.4, 27.6, "It wasn't a crazy thing to say. That year, Apple lost a billion dollars."),
        (27.8, 32.6, "Its share of the world's computer market had fallen to about three percent."),
        (32.8, 38.8, "Its co-founder had been gone for twelve years, and had only just come back."),
        (39.6, 45.2, "Ten years later, Apple would earn three and a half billion dollars in a single year."),
        (46.2, 50.4, "So what actually changed? And how much of it was one man?"),
        (51.0, 53.2, "This is Empire Stories.")]

# ---------------- shots ----------------
def sh_date(t):          # 0 - 3.7
    im = Image.new("RGBA", (W, H), (5, 8, 18, 255)); im.alpha_composite(BG.point(lambda v: int(v * eio(r(t, 0.3, 2.5)))))
    s = "OCTOBER 6, 1997"; n = int(cl((t - 0.3) / 1.4) * len(s))
    if n: ti = txt(s[:n], "sansb", 64, GOLD, 14); im.alpha_composite(ti, (int(W / 2 - txt(s, "sansb", 64, GOLD, 14).width / 2), 470))
    gold_line(im, W / 2 - 260, 572, W / 2 + 260, eo(r(t, 1.6, 2.4)), 2)
    place(im, txt("ORLANDO, FLORIDA", "sansm", 30, IVORY, 10), W / 2, 612, alpha=r(t, 2.0, 2.7))
    return im

FLP = [(-87.6, 31.0), (-87.4, 30.35), (-86.5, 30.4), (-85.4, 29.95), (-84.9, 29.7), (-84.3, 30.05), (-83.6, 29.85), (-83.0, 29.15),
       (-82.75, 28.2), (-82.65, 27.6), (-82.2, 26.85), (-81.8, 26.1), (-81.25, 25.6), (-80.95, 25.15), (-80.45, 25.2), (-80.15, 25.75),
       (-80.05, 26.6), (-80.2, 27.3), (-80.5, 28.0), (-80.6, 28.45), (-81.0, 29.2), (-81.3, 29.9), (-81.45, 30.7), (-82.0, 30.6),
       (-84.9, 30.7), (-85.0, 31.0)]
def sh_map(t):           # 3.7 - 13.7  (local tt)
    tt = t - 3.7; im = BG.copy()
    e = eio(r(tt, 0, 9.5)); k = 150 + 70 * e; clon, clat = -83.6 + 1.6 * e, 28.0 + 0.3 * e
    P = lambda lo, la: (W / 2 + (lo - clon) * k * math.cos(math.radians(28)), H / 2 + (clat - la) * k)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for g in range(-92, -74, 2):
        x, _ = P(g, 28); d.line([(x, 0), (x, H)], fill=(40, 54, 92, 120), width=1)
    for g in range(20, 36, 2):
        _, y = P(-84, g); d.line([(0, y), (W, y)], fill=(40, 54, 92, 120), width=1)
    for g, lab in [(26, "26°N"), (30, "30°N")]:
        _, y = P(-84, g); d.text((40, y - 26), lab, font=font("sansm", 18), fill=(110, 120, 150, 200))
    pts = [P(*p) for p in FLP]; prog = eo(r(tt, 0.1, 1.8)); n = max(2, int(len(pts) * prog))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).polygon(pts, fill=(60, 80, 140, int(140 * prog)))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
    ImageDraw.Draw(lay).polygon(pts, fill=(30, 44, 84, int(255 * prog)))
    ImageDraw.Draw(lay).line(pts[:n] + ([pts[0]] if prog >= 1 else []), fill=IVORY + (220,), width=3, joint="curve")
    im.alpha_composite(lay)
    place(im, txt("FLORIDA", "sansm", 28, (160, 170, 200), 10), *P(-82.6, 30.25), alpha=r(tt, 1.2, 1.9) * 0.9)
    x, y = P(-81.38, 28.54); a = r(tt, 1.8, 2.4) * (1 - r(tt, 5.8, 6.4)); d = ImageDraw.Draw(im)
    if a > 0:
        for kk in range(3):
            ph = ((tt - 1.8) * 0.7 + kk / 3) % 1
            rr = 14 + ph * 80; d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=GOLD + (int(200 * (1 - ph) * a),), width=3)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=GOLD + (255,))
        place(im, txt("ORLANDO", "sansb", 36, IVORY, 6), x + 130, y - 36, alpha=r(tt, 2.1, 2.7) * (1 - r(tt, 5.8, 6.4)))
    dust(im, t, 0.6)
    lower_third(im, "GARTNER SYMPOSIUM", "OCTOBER 6, 1997  ·  ORLANDO, FLORIDA", tt, 3.0)
    if tt > 6.0:
        im.alpha_composite(Image.new("RGBA", (W, H), NAVY + (int(150 * eio(r(tt, 6.0, 7.0))),)))
        words_in(im, W / 2, 450, "“What would you do with Apple?”".split(), tt, 6.4, 92, "serifi", IVORY, 0.14, gold_words=(5,))
        place(im, txt("A QUESTION FROM THE AUDIENCE TO MICHAEL DELL", "sansm", 24, GOLD, 4), W / 2, 580, alpha=r(tt, 7.6, 8.4))
    return im

def sh_quote(t):         # 13.7 - 23.3
    tt = t - 13.7; im = BG.copy()
    z = 1 + 0.04 * tt / 9.6
    place(im, txt("“", "cardo", 420, GOLD), 300, 330, alpha=0.18 * r(tt, 0.2, 1.2))
    words = "I'd shut it down and give the money back to the shareholders.".split()
    rects = words_in(im, W / 2, 470, words, tt, 3.9, int(84 * z), "serif", IVORY, 0.17, gold_words=(1, 2, 3), maxw=1400)
    if rects:
        p = eo(r(tt, 5.0, 5.8)); x0, y0, _ = rects[0]; x1 = rects[-1][2]
        gold_line(im, x0, y0 + 42 * z, x0 + (x1 - x0), p, 4)
    a = r(tt, 6.6, 7.4)
    gold_line(im, W / 2 - 50, 640, W / 2 + 50, a, 2)
    place(im, txt("MICHAEL DELL", "sansb", 34, IVORY, 8), W / 2, 690, alpha=a)
    place(im, txt("FOUNDER & CEO, DELL COMPUTER  ·  OCTOBER 6, 1997", "sansm", 22, GOLD, 3), W / 2, 735, alpha=r(tt, 7.0, 7.8))
    if tt < 3.9: words_in(im, W / 2, 500, "One of the most famous lines in tech history".split(), tt, 0.2, 54, "serifi", (190, 186, 176), 0.08)
    dust(im, t, 0.8); return im

def sh_stats(t):         # 23.3 - 46.0
    global flip_to
    tt = t - 23.3; im = BG.copy(); dust(im, t, 0.5)
    place(im, txt("APPLE, 1997", "sansb", 30, GOLD, 12), W / 2, 200, alpha=r(tt, 0.3, 1.0) * (1 - r(tt, 16.0, 16.6)))
    gold_line(im, W / 2 - 120, 232, W / 2 + 120, eo(r(tt, 0.4, 1.2)) * (1 - r(tt, 16.0, 16.6)), 2)
    out = eio(r(tt, 16.2, 16.9))
    # card 1 counts down to -1.0B then flips to +3.5B
    v1 = "−$1.0B"
    fl = r(tt, 17.0, 17.8)
    cx1 = 420 + (W / 2 - 420) * eio(r(tt, 16.4, 17.4))
    if fl < 0.5: flip_to = None; stat_card(im, cx1, 520, v1, "FY1997 NET LOSS", tt, 3.0, (226, 120, 104), flip=fl if fl > 0 else None)
    else:
        flip_to = ("+$3.5B", "FY2007 NET INCOME", GOLD); stat_card(im, cx1, 520, "+$3.5B", "FY2007 NET INCOME", tt, 3.0, GOLD, flip=fl)
    if out < 1:
        v2 = f"{3.1 * cl((tt - 4.8) / 1.0) + (5.2 - 3.1) * (1 - cl((tt - 4.8) / 1.0)):.1f}%"
        imc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        stat_card(imc, W / 2, 520, v2, "WORLD PC MARKET SHARE", tt, 4.5)
        place(imc, txt("DOWN FROM 5.2% A YEAR EARLIER", "sansm", 20, GOLD, 3), W / 2, 700, alpha=r(tt, 6.0, 6.6))
        stat_card(imc, 1500, 520, f"{int(12 * cl((tt - 9.8) / 0.8))} YRS", "SINCE THE CO-FOUNDER LEFT", tt, 9.5)
        if out > 0: imc.putalpha(imc.getchannel("A").point(lambda v: int(v * (1 - out))))
        im.alpha_composite(imc)
    place(im, txt("Sources: Apple FY1997 results; Apple 10-K via Wired, Jan 1998", "sansm", 20, (150, 150, 160)), W / 2, 790, alpha=r(tt, 5.0, 5.6) * (1 - out))
    if tt > 17.2:   # timeline under the card
        p = eo(r(tt, 17.4, 18.6)); y = 780; gold_line(im, W / 2 - 360, y, W / 2 - 360 + 720 * p, 1, 3)
        place(im, txt("1997", "sansb", 30, IVORY, 4), W / 2 - 360, y + 36, alpha=r(tt, 17.4, 17.8))
        place(im, txt("2007", "sansb", 30, GOLD, 4), W / 2 + 360, y + 36, alpha=r(tt, 18.4, 18.8))
        d = ImageDraw.Draw(im); d.ellipse([W / 2 - 368, y - 8, W / 2 - 352, y + 8], fill=IVORY)
        if p >= 1: d.ellipse([W / 2 + 352, y - 9, W / 2 + 370, y + 9], fill=GOLD)
        place(im, txt("Source: Apple Q4 FY2007 results, Oct 2007", "sansm", 20, (150, 150, 160)), W / 2, 880, alpha=r(tt, 18.6, 19.2))
    return im

def sh_question(t):      # 46.0 - 50.8
    tt = t - 46.0; im = BG.copy(); dust(im, t, 0.6)
    words_in(im, W / 2, 440, "So what actually changed?".split(), tt, 0.2, 100, "serif", IVORY, 0.12)
    words_in(im, W / 2, 590, "And how much of it was one man?".split(), tt, 1.9, 100, "serifi", IVORY, 0.12, gold_words=(6, 7))
    return im

@functools.lru_cache(None)
def emblem(size=300):
    k = 3; S = size * k; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S / 2
    d.ellipse([c - S * 0.46, c - S * 0.46, c + S * 0.46, c + S * 0.46], outline=GOLD + (255,), width=int(S * 0.012))
    d.ellipse([c - S * 0.40, c - S * 0.40, c + S * 0.40, c + S * 0.40], outline=GOLD + (140,), width=int(S * 0.005))
    for i in range(5):   # five columns = an empire's facade
        x = c - S * 0.2 + i * S * 0.1; d.rectangle([x - S * 0.018, c - S * 0.07, x + S * 0.018, c + S * 0.17], fill=GOLD + (255,))
    d.polygon([(c - S * 0.27, c - S * 0.09), (c, c - S * 0.26), (c + S * 0.27, c - S * 0.09)], fill=GOLD + (255,))
    d.rectangle([c - S * 0.27, c + S * 0.19, c + S * 0.27, c + S * 0.225], fill=GOLD + (255,))
    return im.resize((size, size), Image.LANCZOS)

def sh_title(t):         # 50.8 - 58.5
    tt = t - 50.8; im = Image.new("RGBA", (W, H), (6, 10, 24, 255)); im.alpha_composite(BG.point(lambda v: int(v * 0.85)))
    # light sweep
    a = r(tt, 0.2, 1.4)
    if 0 < a < 1:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x = -400 + a * (W + 800)
        d.polygon([(x - 120, 0), (x + 40, 0), (x - 260, H), (x - 420, H)], fill=GOLD + (40,)); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)))
    place(im, emblem(260), W / 2, 330, scale=0.92 + 0.08 * eo(r(tt, 0.3, 1.5)), alpha=eio(r(tt, 0.3, 1.2)))
    gold_line(im, W / 2 - 430, 500, W / 2 + 430, eo(r(tt, 0.6, 1.6)), 2)
    words_in(im, W / 2, 575, ["EMPIRE", "STORIES"], tt, 0.9, 110, "cardo", IVORY, 0.2)
    place(im, txt("THE STORIES BEHIND GLOBAL EMPIRES", "sansm", 26, GOLD, 9), W / 2, 668, alpha=r(tt, 1.8, 2.5))
    if tt > 3.2:
        place(im, txt("EPISODE 001", "sansb", 26, GOLD, 8), W / 2, 820, alpha=r(tt, 3.3, 3.9))
        words_in(im, W / 2, 880, "How Steve Jobs Helped Save Apple".split(), tt, 3.6, 64, "serif", IVORY, 0.1)
    dust(im, t, 1.0)
    fo = r(tt, 6.9, 7.7)
    if fo > 0: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
    return im

SHOTS = [(0.0, 3.7, sh_date), (3.7, 13.7, sh_map), (13.7, 23.3, sh_quote), (23.3, 46.0, sh_stats), (46.0, 50.8, sh_question), (50.8, 58.6, sh_title)]
DUR = 58.6; XF = 0.5

def raw(t):
    for a, b, fn in SHOTS:
        if a <= t < b: return fn(t), a
    return SHOTS[-1][2](t), SHOTS[-1][0]

VIG = None
def frame(t):
    global VIG
    im, start = raw(t)
    if t - start < XF and start > 0:       # cross-dissolve from previous shot
        prev = [s for s in SHOTS if s[1] == start][0][2](start - 0.001)
        im = Image.blend(prev, im, eio((t - start) / XF))
    z = 1.0 + 0.02 * ((t * 0.37) % 1.0) if False else 1.0 + 0.012 * math.sin(t * 0.21)  # gentle breathing camera
    if z != 1:
        cw, ch = W / z, H / z; im = im.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H), Image.BILINEAR)
    captions(im, t)
    arr = np.asarray(im.convert("RGB"), np.int16)
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; VIG = (1 - 0.30 * (((xx - W / 2) / (W / 1.15)) ** 2 + ((yy - H / 2) / (H / 0.95)) ** 2)).astype(np.float32)[..., None]
    arr = (arr + GRAIN[int(t * 24) % 6]) * VIG
    return arr.clip(0, 255).astype(np.uint8)

def render(t0, t1, path):
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f_ in range(int(round(t0 * FPS)), int(round(t1 * FPS))): p.stdin.write(frame(f_ / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, path)

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        c = Image.new("RGB", (640 * 3, 360 * ((len(ts) + 2) // 3)))
        for i, t in enumerate(ts): c.paste(Image.fromarray(frame(t)).resize((640, 360)), ((i % 3) * 640, (i // 3) * 360))
        c.save(f"{OUT}/_stills.jpg", quality=85)
    elif sys.argv[1] == "part":
        a, b = float(sys.argv[2]), float(sys.argv[3]); render(a, b, f"{OUT}/part_{int(a*10):04d}.mp4")
