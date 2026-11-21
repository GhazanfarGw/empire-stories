"""EMPIRE STORIES Ep001 - demo v4: v3 + founder intro beat, tracing gold borders, translucent cards."""
import sys, math, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
argv = sys.argv; sys.argv = ["x", "info_quiet"]
import es_v3 as V
sys.argv = argv
from es_v3 import W, H, NAVY, GOLD, IVORY, place, txt, r, eo, eio, eo5, cl, font, L, LE, INK, RED, MUTE, WHITE
GOLD2 = (176, 140, 30)

def perim_pts(x0, y0, x1, y1, n=240):
    P = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    seg = [math.dist(P[i], P[i + 1]) for i in range(4)]; tot = sum(seg); out = []
    for k in range(n + 1):
        d = tot * k / n
        for i in range(4):
            if d <= seg[i] or i == 3:
                f = min(1, d / seg[i]); out.append((P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f)); break
            d -= seg[i]
    return out

def trace(im, box, t, t0, color=GOLD, width=4, loop=True):
    """gold line draws around the box, then a bright comet keeps circling it"""
    p = eo(r(t, t0, t0 + 0.9))
    if p <= 0: return
    pts = perim_pts(*box); n = len(pts) - 1
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    k = max(2, int(n * p)); d.line(pts[:k], fill=color + (200,), width=width)
    if loop and p >= 1:
        head = int(((t - t0 - 0.9) * 0.35 % 1) * n); L_ = 28
        for j in range(L_):
            a = pts[(head - j) % n]; b = pts[(head - j + 1) % n]
            d.line([a, b], fill=(255, 236, 160, int(255 * (1 - j / L_))), width=width + 3)
        glow = lay.filter(ImageFilter.GaussianBlur(6)); im.alpha_composite(glow)
    im.alpha_composite(lay)

# translucent stat card with tracing border
def stat(im, x, y, big, lab, t, t0, col=INK, flip=None):
    a = eo5(r(t, t0, t0 + 0.5))
    if a <= 0: return
    w, h = 460, 290; c = Image.new("RGBA", (w, h), (255, 255, 255, 205)); d = ImageDraw.Draw(c)
    d.rectangle([0, 0, w, 10], fill=col + (255,))
    b = txt(big, "disp", 104, col); c.alpha_composite(b, (int(w / 2 - b.width / 2), 50))
    l_ = txt(lab, "sansb", 21, MUTE, 3); c.alpha_composite(l_, (int(w / 2 - l_.width / 2), 220))
    sx = 1.0
    if flip is not None:
        sx = max(0.02, abs(math.cos(flip * math.pi))); c = c.resize((max(1, int(w * sx)), h), Image.BICUBIC)
    yy = y + (1 - a) * 120
    place(im, V.shadowed(c, 18, (8, 14), 0.22), x, yy, alpha=a)
    if flip is None or flip == 0: trace(im, (x - w / 2 - 6, yy - h / 2 - 6, x + w / 2 + 6, yy + h / 2 + 6), t, t0 + 0.3, col if col != INK else GOLD, 3)
V.stat = stat

_slot = V.photo_slot
def slot_with_trace(im, name, x, y, t, t0, scale=1.0):
    s = _slot(name, ""); place(im, s, x, y, scale=scale)
    w, h = (s.width - 60) * scale, (s.height - 60) * scale
    trace(im, (x - w / 2 - 4, y - h / 2 - 4, x + w / 2 + 4, y + h / 2 + 4), t, t0, GOLD, 4)

def sh_quote(t):
    tt = t - L(3); im = V.bg()
    slot_with_trace(im, "Michael Dell", 470, 500, tt, 0.2, 0.98 + 0.02 * tt / 8)
    V.label(im, "MICHAEL DELL", 470, 830, tt, 0.4, 30, INK, IVORY)
    place(im, txt("Founder & CEO, Dell Computer", "sansm", 24, MUTE), 470, 878, alpha=r(tt, 0.7, 1.1))
    V.hl_words(im, 1260, 330, "One of the most famous lines in tech history".split(), tt, 0.3, 44, "serifi", MUTE, stagger=0.05, maxw=900)
    q = L(4) - L(3)
    place(im, txt("“", "cardo", 300, GOLD), 830, 470, alpha=0.9 * r(tt, q - 0.2, q + 0.3))
    V.hl_words(im, 1270, 560, "I'd shut it down and give the money back to the shareholders.".split(), tt, q, 76, "serif", INK, gold=(1, 2, 3), stagger=0.16, maxw=860)
    place(im, txt("Oct 6, 1997 · source: Cult of Mac", "sansm", 20, MUTE), 1270, 790, alpha=r(tt, q + 2.0, q + 2.6))
    return im

def sh_jobs(t):                     # line 8: introduce the founder
    tt = t - L(8); im = V.bg()
    slot_with_trace(im, "Steve Jobs", 520, 470, tt, 0.15, 1.0 + 0.03 * tt / 5)
    V.label(im, "STEVE JOBS", 520, 800, tt, 0.35, 34, INK, IVORY)
    place(im, txt("Co-founder of Apple, 1976", "sansm", 24, MUTE), 520, 852, alpha=r(tt, 0.6, 1.0))
    # timeline 1976 -> 1985 -> 1997
    x0, x1, y = 1000, 1700, 470; p = eo(r(tt, 0.5, 2.2)); dr = ImageDraw.Draw(im)
    dr.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=INK + (255,), width=5)
    for yr, xf, k, txt_, col in [(1976, 0.0, 0.6, "CO-FOUNDS APPLE", INK), (1985, 0.36, 1.2, "LEAVES APPLE", RED), (1997, 1.0, 2.2, "BACK", GOLD2)]:
        if tt > k:
            xx = x0 + (x1 - x0) * xf; e = eo5(r(tt, k, k + 0.3)); rr = 16 * e
            dr.ellipse([xx - rr, y - rr, xx + rr, y + rr], fill=col + (255,), outline=WHITE + (255,), width=4)
            place(im, txt(str(yr), "disp", 54, col), xx, y - 62, alpha=e); place(im, txt(txt_, "sansb", 20, MUTE, 3), xx, y + 52, alpha=e)
    if tt > 1.6:
        a = r(tt, 1.6, 2.0); xm = x0 + (x1 - x0) * 0.68
        place(im, txt("12 YEARS AWAY", "sansb", 28, IVORY, 4), xm, 640, alpha=a)
        bb = txt("12 YEARS AWAY", "sansb", 28, IVORY, 4)
        lay = Image.new("RGBA", (bb.width + 34, bb.height + 16), RED + (255,)); lay.alpha_composite(bb, (17, 8)); place(im, lay, xm, 640, alpha=a)
        trace(im, (xm - lay.width / 2 - 6, 640 - lay.height / 2 - 6, xm + lay.width / 2 + 6, 640 + lay.height / 2 + 6), tt, 2.0, GOLD, 3)
    return im

_sale = V.sh_sale
def sh_sale(t):
    im = _sale(t); tt = t - L(20)
    trace(im, (1450 - 230, 450 - 105, 1450 + 230, 450 + 105), tt, 4.0, GOLD, 4)
    return im

_grid = V.sh_grid
def sh_grid(t):
    im = _grid(t); tt = t - L(14); t16 = L(16) - L(14); t17 = L(17) - L(14)
    G = (V.GX0, V.GY0, V.GW, V.GH)
    if tt > t17 + 0.8: trace(im, (G[0] + 16, G[1] + 16, G[0] + G[2] / 2 - 16, G[1] + G[3] / 2 - 16), tt, t17 + 0.8, GOLD, 5)
    return im

V.sh_quote, V.sh_sale, V.sh_grid = sh_quote, sh_sale, sh_grid
V.SHOTS = [(0.0, V.sh_open), (L(1) - 0.2, V.sh_map), (L(3) - 0.2, sh_quote), (L(5) - 0.2, V.sh_stats), (L(8) - 0.2, sh_jobs), (L(9) - 0.2, V.sh_stats),
           (L(10) - 0.3, V.sh_question), (L(11) - 0.15, V.sh_title), (L(12) - 0.3, V.sh_subtract), (L(13) - 0.2, V.sh_cut), (L(14) - 0.2, sh_grid),
           (L(18) - 0.25, V.sh_imac), (L(20) - 0.2, sh_sale), (L(22) - 0.2, V.sh_profit)]
V.BOUNDS = [(V.SHOTS[i][0], V.SHOTS[i + 1][0] if i + 1 < len(V.SHOTS) else V.END, V.SHOTS[i][1]) for i in range(len(V.SHOTS))]

if __name__ == "__main__":
    if sys.argv[1] == "cues": print(json.dumps([round(s[0], 2) for s in V.SHOTS[1:]]))
    elif sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        c = Image.new("RGB", (640 * 3, 360 * ((len(ts) + 2) // 3)))
        for i, t in enumerate(ts): c.paste(Image.fromarray(V.frame(t)).resize((640, 360)), ((i % 3) * 640, (i // 3) * 360))
        c.save("/home/claude/es/out/_v4.jpg", quality=85)
    else:
        a, b = float(sys.argv[2]), float(sys.argv[3]); V.render(a, b, f"/home/claude/es/out/v4_{int(a*10):04d}.mp4")
