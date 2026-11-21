"""EMPIRE STORIES Ep001 - demo v3: bright editorial (ivory paper), voiced, real product photos, cinematic moves."""
import sys, os, math, json, random, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import es_demo as E
import es_seg2 as S
from es_demo import W, H, FPS, NAVY, GOLD, IVORY, place, txt, wtxt, r, eo, eio, eo5, cl, font

INK = NAVY; RED = (196, 58, 46); MUTE = (110, 112, 125); WHITE = (255, 255, 255)
VDIR = "/home/claude/es/voice"
META = json.load(open(f"{VDIR}/lines.json"))
GAP = {2: 0.5, 4: 0.9, 5: 0.35, 8: 0.6, 9: 0.9, 10: 0.8, 11: 1.4, 12: 0.6, 15: 0.6, 16: 0.9, 17: 0.6, 19: 0.5, 21: 0.6}
T0 = []; t = 0.6
for i, d, _ in META:
    T0.append(t); t += d + GAP.get(i, 0.35)
END = t + 1.8
def L(i): return T0[i]
def LE(i): return T0[i] + META[i][1]

# ---------- light paper ----------
def make_paper():
    rng = np.random.default_rng(7)
    low = Image.fromarray((rng.random((H // 30, W // 30)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    low = np.asarray(low.filter(ImageFilter.GaussianBlur(50)), np.float32) / 255 - 0.5
    fib = Image.fromarray((rng.random((H // 2, W // 7)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    fib = np.asarray(fib, np.float32) / 255 - 0.5
    yy, xx = np.mgrid[0:H, 0:W]; v = 1 - 0.10 * (((xx - W / 2) / (W / 1.3)) ** 2 + ((yy - H / 2) / (H / 1.1)) ** 2)
    a = np.array(IVORY, np.float32)[None, None, :] * (1 + low[..., None] * 0.06 + fib[..., None] * 0.02) * v[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
PAPER = make_paper()
def bg(): return PAPER.copy()

def hl_words(im, cx, cy, words, t, t0, size, k="serif", color=INK, gold=(), stagger=0.1, maxw=1500, lh=1.22):
    """serif headline, words rise in; gold highlighter swipes behind chosen words"""
    f = font(k, size); D = ImageDraw.Draw(Image.new("L", (4, 4))); sp = D.textlength(" ", font=f)
    lines, cur, cw = [], [], 0
    for w_ in words:
        ww = D.textlength(w_, font=f)
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w_, ww)); cw += (sp if cw else 0) + ww
    if cur: lines.append(cur)
    y = cy - (len(lines) - 1) * size * lh / 2; n = 0
    for ln in lines:
        tw = sum(w for _, w in ln) + sp * (len(ln) - 1); x = cx - tw / 2
        for w_, ww in ln:
            a = r(t, t0 + n * stagger, t0 + n * stagger + 0.4)
            if a > 0:
                if n in gold:
                    p = eo(r(t, t0 + n * stagger + 0.3, t0 + n * stagger + 0.75))
                    if p > 0:
                        lay = Image.new("RGBA", (int(ww + 24), int(size * 0.95)), (0, 0, 0, 0))
                        ImageDraw.Draw(lay).polygon([(0, 6), ((ww + 24) * p, 0), ((ww + 24) * p - 4, size * 0.95), (4, size * 0.95 - 4)], fill=GOLD + (200,))
                        im.alpha_composite(lay, (int(x - 12), int(y - size * 0.42)))
                place(im, wtxt(w_, k, size, color), x + ww / 2, y + (1 - eo(a)) * 22, alpha=eio(a))
            x += ww + sp; n += 1
        y += size * lh

def label(im, text, x, y, t, t0, size=28, bgc=INK, fg=IVORY, anchor="c"):
    a = r(t, t0, t0 + 0.35)
    if a <= 0: return
    ti = txt(text, "sansb", size, fg, 3); w, h = ti.width + 30, ti.height + 14
    lay = Image.new("RGBA", (w, h), bgc + (255,)); lay.alpha_composite(ti, (15, 7))
    xx = x if anchor == "c" else (x + w / 2 if anchor == "l" else x - w / 2)
    place(im, lay, xx + (1 - eo(a)) * 30, y, alpha=eio(a))

def gl(im, x0, y, x1, prog, w=4, c=GOLD):
    if prog > 0: ImageDraw.Draw(im).line([(x0, y), (x0 + (x1 - x0) * prog, y)], fill=c + (255,), width=w)

def credit(im, text, a=1.0):
    t_ = txt(text, "sansm", 17, MUTE); place(im, t_, W - 30 - t_.width / 2, 34, alpha=a)

@functools.lru_cache(None)
def photo_slot(name, role, w=420, h=520):
    """framed slot showing where a licensed archival portrait goes (no likeness drawn)"""
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 30, w + 30, h + 30], fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (8, 12))
    d.rectangle([30, 30, w + 30, h + 30], fill=(226, 222, 212, 255), outline=WHITE + (255,), width=14)
    for i in range(-h, w, 26): d.line([(30 + i, h + 30), (30 + i + h, 30)], fill=(214, 209, 198, 255), width=2)
    d.rectangle([44, 44, w + 16, h + 16], outline=(214, 209, 198, 255), width=2)
    d.text((w / 2 + 30, h / 2 + 4), "ARCHIVAL PHOTO", font=font("sansb", 26), fill=MUTE, anchor="mm")
    d.text((w / 2 + 30, h / 2 + 40), "licensed image goes here", font=font("sansm", 20), fill=MUTE, anchor="mm")
    return im

def stamp(im, text, x, y, t, t0, size=60, deg=-8, color=RED): S.stamp(im, text, x, y, t, t0, size, deg, color)

def shadowed(img, blur=16, off=(10, 16), alpha=0.35):
    out = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0)); sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * alpha)); s = Image.new("RGBA", img.size, (20, 20, 30, 0)); s.putalpha(a)
    sh.alpha_composite(s, (40 + off[0], 40 + off[1])); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); out.alpha_composite(img, (40, 40)); return out

@functools.lru_cache(None)
def cut(name, h):
    return shadowed(S.collage(name, h, 12, hash(name) % 9))

# ---------- shots ----------
def sh_open(t):                     # line 0
    im = bg(); s = "OCTOBER 6, 1997"; n = int(cl((t - 0.7) / 1.3) * len(s))
    full = txt(s, "sansb", 72, INK, 16)
    if n: im.alpha_composite(txt(s[:n], "sansb", 72, INK, 16), (int(W / 2 - full.width / 2), 440))
    gl(im, W / 2 - 300, 548, W / 2 + 300, eo(r(t, 1.9, 2.6)), 4)
    p = txt("ORLANDO, FLORIDA", "sansb", 30, GOLD, 12); place(im, p, W / 2, 592, alpha=r(t, 2.2, 2.8))
    return im

FLP = E.FLP
def sh_map(t):                      # lines 1-2
    tt = t - L(1); im = bg(); e = eio(r(tt, 0, 8)); k = 150 + 60 * e; clon, clat = -83.4 + 1.5 * e, 28.0 + 0.3 * e
    P = lambda lo, la: (W / 2 + (lo - clon) * k * math.cos(math.radians(28)), H / 2 + (clat - la) * k)
    d = ImageDraw.Draw(im)
    for g in range(-92, -74, 2): x, _ = P(g, 28); d.line([(x, 0), (x, H)], fill=(222, 216, 202), width=1)
    for g in range(20, 36, 2): _, y = P(-84, g); d.line([(0, y), (W, y)], fill=(222, 216, 202), width=1)
    pts = [P(*p) for p in FLP]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(pts, fill=(0, 0, 0, 70)); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(18)).transform((W, H), Image.AFFINE, (1, 0, -8, 0, 1, -12)))
    ImageDraw.Draw(im).polygon(pts, fill=WHITE + (255,), outline=INK + (255,)); ImageDraw.Draw(im).line(pts + [pts[0]], fill=INK + (255,), width=4)
    place(im, txt("FLORIDA", "sansb", 28, MUTE, 12), *P(-82.6, 30.25))
    x, y = P(-81.38, 28.54); a = r(tt, 0.6, 1.1)
    if a > 0:
        for kk in range(3):
            ph = ((tt - 0.6) * 0.7 + kk / 3) % 1; rr = 14 + ph * 80
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=RED + (int(200 * (1 - ph) * a),), width=3)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=RED + (255,), outline=WHITE + (255,), width=4)
        label(im, "ORLANDO", x + 40, y - 46, tt, 0.9, 30, INK, IVORY, "l")
    label(im, "GARTNER SYMPOSIUM  ·  OCT 6, 1997", 150, 900, tt, 1.6, 26, GOLD, INK, "l")
    q0 = L(2) - L(1)
    if tt > q0 - 0.3:
        im.alpha_composite(Image.new("RGBA", (W, H), IVORY + (int(215 * eio(r(tt, q0 - 0.3, q0 + 0.2))),)))
        hl_words(im, W / 2, 500, "“What would you do with Apple?”".split(), tt, q0, 104, "serifi", INK, gold=(5,), stagger=0.09)
    return im

def sh_quote(t):                    # lines 3-4
    tt = t - L(3); im = bg()
    place(im, photo_slot("Michael Dell", ""), 470, 500, scale=0.98 + 0.02 * tt / 8)
    label(im, "MICHAEL DELL", 470, 830, tt, 0.4, 30, INK, IVORY)
    place(im, txt("Founder & CEO, Dell Computer", "sansm", 24, MUTE), 470, 878, alpha=r(tt, 0.7, 1.1))
    hl_words(im, 1260, 330, "One of the most famous lines in tech history".split(), tt, 0.3, 44, "serifi", MUTE, stagger=0.05, maxw=900)
    q = L(4) - L(3)
    place(im, txt("“", "cardo", 300, GOLD), 830, 470, alpha=0.9 * r(tt, q - 0.2, q + 0.3))
    hl_words(im, 1270, 560, "I'd shut it down and give the money back to the shareholders.".split(), tt, q, 76, "serif", INK, gold=(1, 2, 3), stagger=0.16, maxw=860)
    place(im, txt("Oct 6, 1997 · source: Cult of Mac", "sansm", 20, MUTE), 1270, 790, alpha=r(tt, q + 2.0, q + 2.6))
    return im

def stat(im, x, y, big, lab, t, t0, col=INK, flip=None):
    a = eo5(r(t, t0, t0 + 0.5))
    if a <= 0: return
    w, h = 460, 290; c = Image.new("RGBA", (w, h), WHITE + (255,)); d = ImageDraw.Draw(c)
    d.rectangle([0, 0, w - 1, h - 1], outline=(220, 214, 200), width=2); d.rectangle([0, 0, w, 10], fill=col + (255,))
    b = txt(big, "disp", 104, col); c.alpha_composite(b, (int(w / 2 - b.width / 2), 50))
    l_ = txt(lab, "sansb", 21, MUTE, 3); c.alpha_composite(l_, (int(w / 2 - l_.width / 2), 220))
    if flip is not None:
        sx = max(0.02, abs(math.cos(flip * math.pi))); c = c.resize((max(1, int(w * sx)), h), Image.BICUBIC)
    place(im, shadowed(c, 18, (8, 14), 0.30), x, y + (1 - a) * 120, alpha=a)

def sh_stats(t):                    # lines 5-9
    tt = t - L(5); im = bg()
    label(im, "APPLE IN 1997", W / 2, 190, tt, 0.1, 30, INK, IVORY)
    t6, t7, t8, t9 = L(6) - L(5), L(7) - L(5), L(8) - L(5), L(9) - L(5)
    out = eio(r(tt, t9 - 0.2, t9 + 0.5)); fl = r(tt, t9 + 0.6, t9 + 1.3)
    cx1 = 420 + (W / 2 - 420) * eio(r(tt, t9, t9 + 0.8))
    if fl < 0.5: stat(im, cx1, 520, "−$1.0B", "FY1997 NET LOSS", tt, t6 + 0.4, RED, fl if fl > 0 else None)
    else: stat(im, cx1, 520, "+$3.5B", "FY2007 NET INCOME", tt, t6 + 0.4, (176, 140, 30), fl)
    if out < 1:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        v = 5.2 - (5.2 - 3.1) * eo(r(tt, t7 + 0.5, t7 + 1.8))
        stat(lay, W / 2, 520, f"{v:.1f}%", "WORLD PC MARKET SHARE", tt, t7 + 0.3, INK)
        place(lay, txt("DOWN FROM 5.2% A YEAR EARLIER", "sansb", 20, (176, 140, 30), 3), W / 2, 705, alpha=r(tt, t7 + 1.8, t7 + 2.3))
        stat(lay, 1500, 520, f"{int(12 * eo(r(tt, t8 + 0.6, t8 + 1.4)))} YRS", "SINCE THE CO-FOUNDER LEFT", tt, t8 + 0.3, INK)
        if out > 0: lay.putalpha(lay.getchannel("A").point(lambda q: int(q * (1 - out))))
        im.alpha_composite(lay)
    place(im, txt("Sources: Apple FY1997 results; Apple 10-K via Wired, Jan 1998", "sansm", 19, MUTE), W / 2, 800, alpha=r(tt, t7, t7 + 0.5) * (1 - out))
    if tt > t9 + 1.2:
        p = eo(r(tt, t9 + 1.3, t9 + 2.4)); y = 790; gl(im, W / 2 - 360, y, W / 2 + 360, p, 4, (176, 140, 30))
        place(im, txt("1997", "sansb", 30, INK, 4), W / 2 - 360, y + 38); place(im, txt("2007", "sansb", 30, (176, 140, 30), 4), W / 2 + 360, y + 38, alpha=r(tt, t9 + 2.2, t9 + 2.6))
        place(im, txt("Source: Apple Q4 FY2007 results", "sansm", 19, MUTE), W / 2, 880, alpha=r(tt, t9 + 2.4, t9 + 2.9))
    return im

def sh_question(t):                 # line 10
    tt = t - L(10); im = bg()
    hl_words(im, W / 2, 430, "So what actually changed?".split(), tt, 0.1, 110, "serif", INK, stagger=0.1)
    hl_words(im, W / 2, 590, "And how much of it was one man?".split(), tt, 1.6, 110, "serifi", INK, gold=(6, 7), stagger=0.1)
    return im

def sh_title(t):                    # line 11 (navy brand card for punch)
    tt = t - L(11); im = Image.new("RGBA", (W, H), NAVY + (255,)); im.alpha_composite(E.BG)
    a = r(tt, -0.2, 1.0)
    if 0 < a < 1:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x = -400 + a * (W + 800)
        d.polygon([(x - 120, 0), (x + 40, 0), (x - 260, H), (x - 420, H)], fill=GOLD + (60,)); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)))
    place(im, E.emblem(250), W / 2, 330, scale=0.9 + 0.1 * eo(r(tt, 0, 1.0)), alpha=eio(r(tt, 0, 0.8)))
    gl(im, W / 2 - 430, 500, W / 2 + 430, eo(r(tt, 0.3, 1.2)), 2)
    E.words_in(im, W / 2, 575, ["EMPIRE", "STORIES"], tt, 0.4, 112, "cardo", IVORY, 0.18)
    place(im, txt("THE STORIES BEHIND GLOBAL EMPIRES", "sansm", 26, GOLD, 9), W / 2, 668, alpha=r(tt, 1.2, 1.8))
    place(im, txt("EPISODE 001", "sansb", 26, GOLD, 8), W / 2, 820, alpha=r(tt, 2.0, 2.5))
    E.words_in(im, W / 2, 880, "How Steve Jobs Helped Save Apple".split(), tt, 2.2, 62, "serif", IVORY, 0.08)
    E.dust(im, t, 1.0); return im

def sh_subtract(t):                 # line 12
    tt = t - L(12); im = bg()
    hl_words(im, W / 2, 380, ["ADD"], tt, 0.2, 230, "disp", INK)
    p = eo(r(tt, 1.1, 1.5))
    if p > 0: ImageDraw.Draw(im).line([(W / 2 - 260, 400), (W / 2 - 260 + 520 * p, 370)], fill=RED + (255,), width=18)
    hl_words(im, W / 2, 660, ["SUBTRACT."], tt, 1.9, 230, "disp", INK, gold=(0,))
    return im

TILES = S.TILES
def sh_cut(t):                      # line 13
    tt = t - L(13); im = bg(); rng = random.Random(4); d13 = META[13][1]
    for i, name in enumerate(TILES):
        cx, cy = 230 + (i % 6) * 292, 190 + (i // 6) * 150
        dead = rng.random() < 0.72 and name != "Power Mac 8600"
        appear = r(tt, 0.05 + i * 0.025, 0.3 + i * 0.025)
        fall = eio(r(tt, 1.6 + rng.random() * 1.0, 2.4 + rng.random() * 1.0)) if dead else 0
        if appear <= 0: continue
        c = Image.new("RGBA", (262, 104), WHITE + (255,)); dd = ImageDraw.Draw(c); dd.rectangle([0, 0, 261, 103], outline=(214, 207, 192), width=2)
        ti = txt(name, "sansb", 22, INK); c.alpha_composite(ti, (int(131 - ti.width / 2), 38))
        place(im, c, cx, cy + fall * 900 + (1 - appear) * 20, alpha=appear * (1 - fall * 0.5))
    a = eo5(r(tt, 2.6, 3.0))
    if a > 0: place(im, txt("−70%", "disp", 210, RED), W / 2, 500, scale=1.3 - 0.3 * a, alpha=a * (1 - r(tt, 3.9, 4.2)))
    if tt > 3.9:
        im.alpha_composite(Image.new("RGBA", (W, H), IVORY + (int(200 * r(tt, 3.9, 4.2)),)))
        nx = W / 2 + (1 - eo(r(tt, 3.9, 4.5))) * 1000
        place(im, S.rot(cut("newton_cut.png", 560), -6), nx, 500)
        label(im, "APPLE NEWTON", 1260, 300, tt, 4.4, 30, INK, IVORY, "l")
        stamp(im, "CANCELLED", W / 2 + 40, 560, tt, min(d13 - 0.6, 5.0), 78, -10)
        credit(im, "Photo: Felix Winkelnkemper, CC BY-SA 4.0", r(tt, 4.0, 4.4))
    return im

GX0, GY0, GW, GH = 600, 170, 800, 660
def sh_grid(t):                     # lines 14-17
    tt = t - L(14); im = bg(); d = ImageDraw.Draw(im)
    t15, t16, t17 = L(15) - L(14), L(16) - L(14), L(17) - L(14)
    p1, p2 = eo(r(tt, 0.8, 1.6)), eo(r(tt, 1.2, 2.0))
    if p1 > 0: d.line([(GX0 + GW / 2, GY0), (GX0 + GW / 2, GY0 + GH * p1)], fill=INK + (255,), width=6)
    if p2 > 0: d.line([(GX0, GY0 + GH / 2), (GX0 + GW * p2, GY0 + GH / 2)], fill=INK + (255,), width=6)
    for s_, x, y, k in [("CONSUMER", GX0 + GW / 4, GY0 - 40, 2.6), ("PRO", GX0 + 3 * GW / 4, GY0 - 40, 3.2), ("DESKTOP", GX0 - 160, GY0 + GH / 4, 4.4), ("PORTABLE", GX0 - 160, GY0 + 3 * GH / 4, 5.1)]:
        place(im, txt(s_, "sansb", 34, INK, 8), x, y, alpha=r(tt, k, k + 0.4))
    label(im, "FOUR BOXES. FOUR PRODUCTS.", GX0 + GW / 2, GY0 + GH + 60, tt, t15, 28, GOLD, INK)
    a = eo(r(tt, t15 + 0.3, t15 + 0.9))
    if a > 0:
        place(im, S.rot(cut("powermac_beige_cut.png", 250), 3), GX0 + 3 * GW / 4, GY0 + GH / 4 + (1 - a) * -300, alpha=a)
        place(im, txt("POWER MAC G3", "sansb", 20, INK, 4), GX0 + 3 * GW / 4, GY0 + GH / 2 - 22, alpha=a)
    if tt > t15 + 0.8:
        place(im, txt("POWERBOOK G3", "sansb", 26, INK, 4), GX0 + 3 * GW / 4, GY0 + 3 * GH / 4, alpha=r(tt, t15 + 0.8, t15 + 1.2))
        place(im, txt("LATER: iBOOK", "sansm", 22, MUTE, 4), GX0 + GW / 4, GY0 + 3 * GH / 4, alpha=r(tt, t15 + 1.2, t15 + 1.6))
    if tt > t16 - 0.2:
        pul = 0.5 + 0.5 * math.sin((tt - t16) * 5)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rectangle([GX0 + 16, GY0 + 16, GX0 + GW / 2 - 16, GY0 + GH / 2 - 16], outline=RED + (int(110 + 130 * pul),), width=5); im.alpha_composite(lay)
        if tt < t17 + 0.3: place(im, txt("?", "serif", 170, RED), GX0 + GW / 4, GY0 + GH / 4, alpha=r(tt, t16, t16 + 0.5) * (0.6 + 0.4 * pul))
    if tt > t17 + 0.2:
        f = eo5(r(tt, t17 + 0.2, t17 + 0.9)); x = GX0 + GW / 4 + (1 - f) * -800; y = GY0 + GH / 4 + (1 - f) * 220
        place(im, S.rot(cut("imac34_cut.png", 260), -3), x, y, alpha=f)
        stamp(im, "MAY 6, 1998", GX0 + GW / 4 + 30, GY0 + GH / 2 + 70, tt, t17 + 0.9, 42, -6, RED)
    cr = "Photo: Klodo6975, public domain" if tt < t17 + 0.2 else "Photos: Rama / David Fuchs, CC BY-SA 4.0; Klodo6975, public domain"
    if tt > t15 + 0.3: credit(im, cr)
    return im

def sh_imac(t):                     # lines 18-19
    tt = t - L(18); im = bg(); dur = L(20) - L(18)
    z = 1.0 + 0.07 * tt / dur; cx, cy = 760 - tt * 5, 540
    place(im, S.rot(cut("imac34_cut.png", 700), -2), cx, cy, scale=z * (0.92 + 0.08 * eo(r(tt, 0, 0.7))), alpha=eio(r(tt, 0, 0.4)))
    P = lambda dx, dy: (cx + dx * z, cy + dy * z)
    t19 = L(19) - L(18)
    calls = [("ALL-IN-ONE", (-180, -80), (1260, 250), 2.6), ("TRANSLUCENT \"BONDI BLUE\"", (160, -110), (1260, 360), 4.2),
             ("HANDLE ON TOP", (-30, -310), (1260, 470), 6.6), ("NO FLOPPY DRIVE", (-160, 240), (1260, 640), t19 + 1.6), ("USB PORTS", (250, 160), (1260, 750), t19 + 3.4)]
    for text, (dx, dy), (lx, ly), k in calls:
        x0, y0 = P(dx, dy); p = eo(r(tt, k, k + 0.45))
        if p > 0:
            dr = ImageDraw.Draw(im); dr.line([(x0, y0), (x0 + (lx - 12 - x0) * p, y0 + (ly - y0) * p)], fill=INK + (255,), width=3); dr.ellipse([x0 - 8, y0 - 8, x0 + 8, y0 + 8], fill=RED + (255,), outline=WHITE + (255,), width=3)
        label(im, text, lx, ly, tt, k + 0.35, 28, GOLD, INK, "l")
    credit(im, "Photo: Rama, alterations by David Fuchs, CC BY-SA 4.0")
    return im

def sh_sale(t):                     # lines 20-21
    tt = t - L(20); im = bg(); t21 = L(21) - L(20)
    place(im, shadowed(S.rot(S.photo_card("imac_lineup_crop.jpg", 900), 2), 20, (10, 16), 0.3), 640, 470 + (1 - eo(r(tt, 0, 0.6))) * 600)
    place(im, txt("Later iMac colours, 1999", "sansm", 20, MUTE), 640, 800, alpha=r(tt, 0.6, 1.0))
    credit(im, "Photo: Stephen Hackett, CC BY-SA 4.0")
    stamp(im, "AUG 15, 1998", 1450, 250, tt, 1.6, 46, -6, RED)
    a = eo5(r(tt, 3.6, 4.1))
    if a > 0:
        tag = Image.new("RGBA", (420, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(tag)
        d.rounded_rectangle([0, 0, 419, 169], 14, fill=INK + (255,)); d.ellipse([22, 72, 46, 96], fill=IVORY + (255,))
        tag.alpha_composite(txt("$1,299", "disp", 100, IVORY), (90, 22)); place(im, shadowed(S.rot(tag, -5)), 1450, 450, scale=0.6 + 0.4 * a, alpha=a)
    if tt > t21:
        n = int(278000 * eo(r(tt, t21 + 0.4, t21 + 3.0)))
        place(im, txt(f"{n:,}", "disp", 132, (176, 140, 30)), 1450, 690, alpha=r(tt, t21, t21 + 0.3))
        place(im, txt("iMACS SHIPPED IN 6 WEEKS", "sansb", 26, INK, 5), 1450, 790, alpha=r(tt, t21 + 0.3, t21 + 0.7))
    return im

NI = [("FY1996", -816), ("FY1997", -1045), ("FY1998", 309)]
def sh_profit(t):                   # line 22
    tt = t - L(22); im = bg(); d = ImageDraw.Draw(im)
    label(im, "APPLE NET INCOME", W / 2, 140, tt, 0.1, 30, INK, IVORY)
    zero, sc, x0 = 470, 300 / 1045, 660
    d.line([(520, zero), (1400, zero)], fill=MUTE, width=3)
    for i, (fy, v) in enumerate(NI):
        x = x0 + i * 300; p = eo(r(tt, 0.3 + i * 0.6, 1.0 + i * 0.6)); h = v * sc * p; col = (176, 140, 30) if v > 0 else RED
        if abs(h) > 1: d.rectangle([x - 72, min(zero, zero - h), x + 72, max(zero, zero - h)], fill=col + (255,))
        if p > 0.9:
            lab = f"+${v}M" if v > 0 else (f"−${-v/1000:.2f}B" if -v >= 1000 else f"−${-v}M")
            place(im, txt(lab, "disp", 42, col), x, zero - h - (36 if v > 0 else -36))
        place(im, txt(fy, "sansb", 26, INK, 4), x, 870, alpha=r(tt, 0.3 + i * 0.6, 0.8 + i * 0.6))
    if tt > 2.6: label(im, "FIRST PROFITABLE YEAR SINCE 1995", 1060, 230, tt, 2.8, 28, GOLD, INK)
    place(im, txt("Sources: Apple results via TidBITS (Oct 1997, Oct 1998); FY1997 as filed", "sansm", 18, MUTE), W / 2, 965, alpha=r(tt, 1.0, 1.5))
    fo = r(t, END - 1.2, END)
    if fo > 0: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
    return im

SHOTS = [(0.0, sh_open), (L(1) - 0.2, sh_map), (L(3) - 0.2, sh_quote), (L(5) - 0.2, sh_stats), (L(10) - 0.3, sh_question), (L(11) - 0.15, sh_title),
         (L(12) - 0.3, sh_subtract), (L(13) - 0.2, sh_cut), (L(14) - 0.2, sh_grid), (L(18) - 0.25, sh_imac), (L(20) - 0.2, sh_sale), (L(22) - 0.2, sh_profit)]
BOUNDS = [(SHOTS[i][0], SHOTS[i + 1][0] if i + 1 < len(SHOTS) else END, SHOTS[i][1]) for i in range(len(SHOTS))]
WHIP = 0.32
CAPS = [(L(i) - 0.05, LE(i) + 0.15, META[i][2].replace("nineteen ninety-seven", "1997").replace("nineteen ninety-eight", "1998").replace("nineteen ninety-five", "1995").replace("U S B", "USB").replace("October sixth", "October 6th").replace("May sixth", "May 6th").replace("August fifteenth", "August 15th")) for i in range(len(META))]
def captions(im, t):
    for a, b, text in CAPS:
        if a <= t < b:
            ti = txt(text, "sansm", 31, WHITE)
            if ti.width > 1700: return
            box = Image.new("RGBA", (ti.width + 40, ti.height + 18), (12, 18, 40, 200)); box.alpha_composite(ti, (20, 9))
            place(im, box, W / 2, H - 56, alpha=min(r(t, a, a + 0.15), 1 - r(t, b - 0.15, b))); return

def camera(im, t, a, b):
    """slow push-in per shot"""
    p = (t - a) / max(0.1, b - a); z = 1.0 + 0.045 * p
    cw, ch = W / z, H / z; x0 = (W - cw) / 2; y0 = (H - ch) / 2
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)

VIG = None
def frame(t):
    global VIG
    for i, (a, b, fn) in enumerate(BOUNDS):
        if a <= t < b: break
    im = camera(fn(t), t, a, b)
    if i > 0 and t - a < WHIP:          # whip-pan transition with motion blur
        pa, pb, pfn = BOUNDS[i - 1]; prev = camera(pfn(a - 0.001), a - 0.001, pa, pb)
        q = eio((t - a) / WHIP); off = int(q * W)
        strip = Image.new("RGBA", (W * 2, H)); strip.paste(prev, (0, 0)); strip.paste(im, (W, 0))
        im = strip.crop((off, 0, off + W, H))
        bl = int(60 * math.sin(q * math.pi))
        if bl > 2: im = im.resize((max(1, W // (1 + bl // 6)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    captions(im, t)
    arr = np.asarray(im.convert("RGB"), np.int16)
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; VIG = (1 - 0.16 * (((xx - W / 2) / (W / 1.15)) ** 2 + ((yy - H / 2) / (H / 0.95)) ** 2)).astype(np.float32)[..., None]
    arr = (arr + E.GRAIN[int(t * 24) % 6] // 2) * VIG
    return arr.clip(0, 255).astype(np.uint8)

def render(t0, t1, path):
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f_ in range(int(round(t0 * FPS)), int(round(t1 * FPS))): p.stdin.write(frame(f_ / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, path)

if __name__ == "__main__":
    if sys.argv[1] == "info": print("END", round(END, 2)); [print(i, round(L(i), 2), m[1]) for i, m in enumerate(META)]
    elif sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        c = Image.new("RGB", (640 * 3, 360 * ((len(ts) + 2) // 3)))
        for i, t in enumerate(ts): c.paste(Image.fromarray(frame(t)).resize((640, 360)), ((i % 3) * 640, (i // 3) * 360))
        c.save("/home/claude/es/out/_v3.jpg", quality=85)
    else:
        a, b = float(sys.argv[2]), float(sys.argv[3]); render(a, b, f"/home/claude/es/out/v3_{int(a*10):04d}.mp4")
