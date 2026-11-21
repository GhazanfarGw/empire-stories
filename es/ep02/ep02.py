"""EMPIRE STORIES · Episode 02 (McDonald's) renderer — built on the locked Episode 01 engine.
Same approved look as tl3 (US navy/red, grey paper, thin torn edges, odometer years, pin shockwave, US map, OUR TAKE, end screen),
extended to the full ~10 minute script: beats are split into panels that swap as the narration moves on."""
import sys, os, math, json, subprocess, functools, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/claude/es/tl3"); sys.path.insert(0, "/home/claude/es")
_a = sys.argv; sys.argv = ["x", "q"]
import tl3 as T0                     # palette patch, paper, torn edges, cards, ident/end-screen atoms
sys.argv = _a
from tl3 import (W, H, FPS, NAVY, GOLD, IVORY, place, txt, r, eo, eio, eo5, cl, font, INK, RED, MUTE, WHITE, V, E, geo, PK,
                 NAVY_US, NAVY_US2, RED_US, SOFT, back, label_box, person_card, cutimg, photocard, odometer, emblem_us, glow,
                 navy_bg, zoom, map_pin, draw_arc, arc_pts, trace)
GOLD2 = NAVY_US; NAVY2 = NAVY_US2
D = "/home/claude/es/ep02"
META = json.load(open(os.environ.get("EP_META", f"{D}/voice/meta.json")))

# ---------------- timing ----------------
IDENT_DUR = 7.8; TRAVEL = 1.5; XF = 0.6; ENDSCREEN = 14.0
YB = ["y0", "y1", "y2", "y3", "y4", "y5", "y6", "y7"]
from collections import defaultdict
SENT = {}; TR = defaultdict(lambda: 1e9); BEATS = []; t = 0.9; prev = None; IDENT_T = None; OUTRO = None
for m in META:
    b = m["beat"]
    if b != prev:
        if prev == "hook": IDENT_T = t - 0.2; t = IDENT_T + IDENT_DUR + 0.2
        if b in YB: TR[b] = t; t += TRAVEL
        elif b in ("map", "deal"): TR[b] = t; t += XF + 0.3
        elif b == "y4b": TR[b] = t; t += 0.4
        elif b == "lesson": TR[b] = t; t += 1.4
        elif b == "outro": OUTRO = t - 0.2; TR[b] = OUTRO; t = OUTRO + 2.2
        else: TR[b] = t
        BEATS.append(b); SENT[b] = []; prev = b
    m["t"] = t; SENT[b].append(t); t += m["dur"] + m["pause"]
DEMO = OUTRO is None
if DEMO: OUTRO = 1e9
END = (t + 1.2) if DEMO else max(OUTRO + ENDSCREEN, t + 2.0)
NEXT_TR = {b: (TR[BEATS[k + 1]] if k + 1 < len(BEATS) else OUTRO) for k, b in enumerate(BEATS)}
NEXT_TR["lesson"] = OUTRO
def st(b, i=0, off=0.0): return SENT[b][i] + off
def mid(b, i, frac): m = [x for x in META if x["beat"] == b][i]; return m["t"] + m["dur"] * frac
def P(b, i): return SENT[b][i] - 0.1          # panel boundary: elements of the previous panel leave here

# ---------------- timeline geometry ----------------
AX_Y = 862; BUS_Y = 780; PX = [250 + i * 203 for i in range(8)]; LX0 = 110; LX1 = 1840
YEARS = [1948, 1954, 1955, 1956, 1961, 1967, 1990, 2025]
DESC = ["Speedee System", "Kroc arrives", "Des Plaines", "Franchise Realty", "$2.7M buyout", "Goes global", "Moscow", "$10.4B in rent"]
PIN_T = {i: TR[YB[i]] + TRAVEL for i in range(8)}
PIN_OF = {"y0": 0, "y1": 1, "y2": 2, "y3": 3, "y4": 4, "y5": 5, "y6": 6, "y7": 7}

def head_x(t):
    if t < TR["y0"]: return None
    for i in range(8):
        a = TR[YB[i]]
        if t < a + TRAVEL: x0 = PX[i - 1] if i else LX0; return x0 + (PX[i] - x0) * eio(r(t, a, a + TRAVEL - 0.05))
        if i == 7 or t < TR[YB[i + 1]]:
            if i == 7 and t >= TR["lesson"]: return PX[7] + (LX1 - PX[7]) * eio(r(t, TR["lesson"], TR["lesson"] + 1.2))
            return PX[i]
    return LX1
def active_pin(t):
    if t >= TR["lesson"]: return None
    k = None
    for i in range(8):
        if t >= PIN_T[i] - 0.05: k = i
    return k

# ---------------- numbers that count ----------------
COUNT_DUR = 1.2
def parse_num(text):
    m = re.match(r"^([+−-]?)(\$?)([\d.,]+)([A-Z%]*)$", text)
    if not m or not (m.group(1) or m.group(2) or m.group(4) or "," in m.group(3)): return None
    num = m.group(3).replace(",", ""); dec = len(num.split(".")[1]) if "." in num else 0
    return m.group(1), m.group(2), float(num), dec, m.group(4)
def counted(text, frac):
    p = parse_num(text)
    if p is None: return text
    sg, cur, v, dec, suf = p; x = v * frac
    return f"{sg}{cur}{x:,.{dec}f}{suf}" if dec else f"{sg}{cur}{int(round(x)):,}{suf}"
def count_frac(ti): return eo(r(ti, 0.0, COUNT_DUR))

# ---------------- elements ----------------
EL = []
def el(b, kind, x, y, pay, tin, branch=True, tout=None):
    EL.append(dict(b=b, kind=kind, x=x, y=y, pay=pay, tin=tin, tout=tout or NEXT_TR[b], branch=branch))
L, R_ = 640, 1280          # left / right columns of the stage
CR = {"hq": "Apple HQ, Cupertino · Photo: Joe Ravi, CC BY-SA 3.0", "next": "NeXTcube · Wikimedia Commons, CC BY-SA 3.0",
      "newton": "Newton MessagePad · Felix Winkelnkemper, CC BY-SA 4.0", "imac": "iMac G3 · Rama / David Fuchs, CC BY-SA 4.0",
      "ipod": "iPod (1st gen) · Rjcflyer, CC BY 2.5", "iphone": "iPhone (1st gen) · Carl Berkeley, CC BY-SA 2.0",
      "clone": "Power Computing Mac clone · Angelgreat, CC BY-SA 4.0", "pm": "Power Macintosh G3 · Klodo6975, public domain",
      "be": "BeBox · Josh Carlson, CC BY 2.0", "lineup": "iMac G3 colours · Stephen Hackett, CC BY-SA 4.0"}

CR.update({"downey": "Oldest operating McDonald's, Downey CA · Photo: Northwalker, CC0", "sign": "Speedee sign, Downey CA · Photo: Northwalker, CC0",
           "sbd": "Site of the first McDonald's, San Bernardino · Photo: Cogart Strangehill, CC BY-SA 2.0",
           "desplaines": "McDonald's #1 Store Museum, Des Plaines · Photo: Jerry Huddleston, CC BY 2.0"})
# --- cold open: a simple question, turned upside down
h = "hook"
el(h, "photo", L, 540, ("mcd_downey_museum.jpg", 860, CR["downey"]), st(h, 0, 0.0), False, tout=P(h, 2))
el(h, "words", R_ + 60, 490, ("What does McDonald's sell?", 78, "serif", INK, (3,), 700), st(h, 0, 0.0), False, tout=P(h, 2))
el(h, "lab", R_ + 60, 690, ("BURGERS · FRIES · MILKSHAKES", INK), mid(h, 1, 0.3), False, tout=P(h, 2))
el(h, "big", 580, 500, ("$139.4B", NAVY_US, 150), mid(h, 2, 0.55), False, tout=P(h, 4))
el(h, "lab", 580, 620, ("SPENT AT McDONALD'S · 2025", INK), mid(h, 2, 0.8), False, tout=P(h, 4))
el(h, "big", 1360, 500, ("95%", RED, 150), mid(h, 3, 0.6), False, tout=P(h, 4))
el(h, "lab", 1360, 620, ("RUN BY FRANCHISEES", INK), mid(h, 3, 0.8), False, tout=P(h, 4))
el(h, "lab", 960, 230, ("WHAT McDONALD'S ITSELF COLLECTED · 2025", INK), st(h, 4, 0.6), False, tout=P(h, 8))
el(h, "bars", 960, 760, dict(data=[("RENT", 10.442), ("FOOD SALES*", 9.690), ("ROYALTIES", 6.018)], sc=38, bw=230, gap=150,
                             labs=["$10.4B", "$9.7B", "$6.0B"], cols=[RED, NAVY_US, NAVY_US],
                             t=[st(h, 5, 0.1), mid(h, 7, 0.55), mid(h, 7, 0.25)]), st(h, 4, 0.6), False, tout=P(h, 8))
el(h, "note", 960, 860, "*food sold in the restaurants McDonald's runs itself · source: McDonald's 2025 annual report", mid(h, 7, 0.6), False, tout=P(h, 8))
el(h, "stamp", 1560, 360, ("RENT", RED), st(h, 5, 0.35), False, tout=P(h, 8))
el(h, "person", L, 540, ("Harry Sonneborn", "McDonald's first president"), st(h, 8, 0.3), False, tout=P(h, 10))
el(h, "quote", R_ + 40, 510, ("“We are not technically in the food business. We are in the real estate business.”", "Harry Sonneborn, as recounted in McDonald's: Behind the Arches", 48, (12, 13, 14)), st(h, 9, 0.0), False, tout=P(h, 10))
el(h, "words", 960, 460, ("A burger company…", 104, "serif", INK, (), 1600), st(h, 10, 0.1), False, tout=P(h, 12))
el(h, "words", 960, 630, ("…or a landlord that sells burgers?", 80, "serifi", INK, (3,), 1600), st(h, 11, 0.0), False, tout=P(h, 12))
el(h, "lab", 960, 540, ("SAN BERNARDINO, CALIFORNIA", NAVY_US), st(h, 12, 1.2), False)
# --- 1948: the Speedee Service System
b = "y0"
el(b, "person", L, 420, ("Dick & Mac McDonald", "San Bernardino, 1948"), st(b, 0, 0.8))
el(b, "photo", R_ + 20, 380, ("mcd_sanbernardino_site.jpg", 600, CR["sbd"]), mid(b, 0, 0.6), False, tout=P(b, 1))
el(b, "lab", R_ + 20, 660, ("THE ORIGINAL SITE, TODAY A MUSEUM", MUTE), mid(b, 0, 0.85), False, tout=P(b, 1))
el(b, "lab", R_ + 20, 230, ("9 MENU ITEMS", NAVY_US), mid(b, 1, 0.45), False, tout=P(b, 2))
el(b, "lab", R_ + 20, 330, ("NO CARHOPS", RED), mid(b, 1, 0.62), False, tout=P(b, 2))
el(b, "big", R_ + 20, 480, ("15¢", NAVY_US, 150), mid(b, 1, 0.8), False, tout=P(b, 2))
el(b, "lab", R_ + 20, 600, ("THE HAMBURGER", INK), mid(b, 1, 0.9), False, tout=P(b, 2))
el(b, "photo", R_ + 40, 400, ("mcd_downey_sign.jpg", 330, CR["sign"]), st(b, 2, 0.3), False)
el(b, "lab", R_ + 40, 120, ("THE SPEEDEE SERVICE SYSTEM", RED), st(b, 2, 0.6), False)
# --- 1954: Ray Kroc
b = "y1"
el(b, "person", L, 420, ("Ray Kroc", "Milkshake-machine salesman"), st(b, 0, 0.5))
el(b, "big", R_, 330, ("8", NAVY_US, 170), mid(b, 0, 0.82), False, tout=P(b, 2))
el(b, "lab", R_, 460, ("MULTIMIXERS, ONE RESTAURANT", INK), mid(b, 0, 0.9), False, tout=P(b, 2))
el(b, "lab", R_, 560, ("1954 · KROC DRIVES WEST", RED), mid(b, 1, 0.6), False, tout=P(b, 2))
el(b, "words", R_ + 20, 420, ("A system that could be copied anywhere.", 62, "serif", INK, (4, 5, 6), 760), st(b, 2, 0.4), False)


# ---------------- drawing ----------------
def lay_alpha(lay, a):
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    return lay
def words(im, x, y, p, t, t0, a):
    text, size, k, col, gold, maxw = p
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); V.hl_words(lay, x, y, text.split(), t, t0, size, k, col, gold=gold, stagger=0.06, maxw=maxw)
    im.alpha_composite(lay_alpha(lay, a))
@functools.lru_cache(None)
def quote_mark(): return txt("“", "serif", 200, RED)

def grid(im, x, y, p, t, t0, a):
    small = p.get("small"); k = 0.55 if small else 1.0
    bw, bh, gp = 300 * k, 150 * k, 18 * k; x0 = x - bw - gp / 2; y0 = y - bh - gp / 2
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    boxes = [(0, 0, "", None), (1, 0, "POWER MAC G3", NAVY_US), (0, 1, "", None), (1, 1, "POWERBOOK G3", NAVY_US)]
    for j, (cx, cy, name, fillc) in enumerate(boxes):
        bp = eo(r(t, t0 + 0.15 * j, t0 + 0.15 * j + 0.6)); bx, by = x0 + cx * (bw + gp), y0 + cy * (bh + gp)
        if bp <= 0: continue
        f = eo(r(t, p["fill"] + 0.25 * cx + 0.3 * cy, p["fill"] + 0.25 * cx + 0.3 * cy + 0.4))
        if fillc and f > 0: d.rectangle([bx, by, bx + bw, by + bh], fill=fillc + (int(235 * f),))
        pts = [(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh), (bx, by)]
        segs = []; tot = 4 * bp
        for q in range(4):
            if tot <= 0: break
            u = min(1, tot); (ax, ay), (bx2, by2) = pts[q], pts[q + 1]; segs.append(((ax, ay), (ax + (bx2 - ax) * u, ay + (by2 - ay) * u))); tot -= 1
        for s0, s1 in segs: d.line([s0, s1], fill=INK + (255,), width=max(2, int(5 * k)))
        if fillc and f > 0: place(lay, txt(name, "sansb", int(30 * k), IVORY, 3), bx + bw / 2, by + bh / 2, alpha=f)
        if not fillc and t >= p["fill"] + 0.6: place(lay, txt("?", "disp", int(90 * k), MUTE), bx + bw / 2, by + bh / 2, alpha=r(t, p["fill"] + 0.6, p["fill"] + 1.0))
        if not fillc and cy == 0 and t >= p["pulse"]:
            ph = ((t - p["pulse"]) * 0.8) % 1; e = 6 + 18 * ph
            d.rectangle([bx - e, by - e, bx + bw + e, by + bh + e], outline=RED + (int(200 * (1 - ph)),), width=4)
            d.rectangle([bx, by, bx + bw, by + bh], outline=RED + (255,), width=6)
    la = r(t, p["lab"], p["lab"] + 0.4) if not small else r(t, t0 + 0.6, t0 + 1.0)
    for j, (lab, lx, ly) in enumerate([("CONSUMER", x0 + bw / 2, y0 - 34 * k), ("PRO", x0 + bw * 1.5 + gp, y0 - 34 * k)]):
        place(lay, txt(lab, "sansb", int(28 * k), RED, 4), lx, ly, alpha=r(t, p["lab"] + 0.3 * j, p["lab"] + 0.3 * j + 0.4) if not small else la)
    for j, (lab, ly) in enumerate([("DESKTOP", y0 + bh / 2), ("PORTABLE", y0 + bh * 1.5 + gp)]):
        tl = txt(lab, "sansb", int(24 * k), RED, 4); ta = r(t, mid("y4b", 11, 0.55) + 0.3 * j, mid("y4b", 11, 0.55) + 0.3 * j + 0.4) if not small else la
        place(lay, tl, x0 - 24 * k - tl.width / 2, ly, alpha=ta)
    if not small and t >= p["rule"]:
        place(lay, label_box("NO BOX → NO PRODUCT", 24, RED, IVORY), x + bw + gp / 2 + 190, y, alpha=r(t, p["rule"], p["rule"] + 0.4))
    im.alpha_composite(lay_alpha(lay, a))

def bars(im, x, y, p, t, t0, a):
    d = ImageDraw.Draw(im); data = p["data"]; n = len(data); bw, gap = p.get("bw", 120), p.get("gap", 70); x0 = x - (n * bw + (n - 1) * gap) / 2
    d.line([(x0 - 30, y), (x0 + n * bw + (n - 1) * gap + 30, y)], fill=INK + (int(255 * a),), width=3)
    for k, ((lab, v), tk) in enumerate(zip(data, p["t"])):
        q = eo(r(t, tk, tk + 0.7)); hh = v * p["sc"] * q; bx = x0 + k * (bw + gap); col = p["cols"][k] if "cols" in p else (RED if v < 0 else NAVY_US)
        if abs(hh) > 1: d.rectangle([bx, min(y, y - hh), bx + bw, max(y, y - hh)], fill=col + (int(255 * a),))
        place(im, txt(lab, "sansb", 24, MUTE, 2), bx + bw / 2, y + 28 + (14 if v < 0 else 0), alpha=a * r(t, t0, t0 + 0.4))
        if q > 0.02:
            vy = y - hh - 26 if v >= 0 else y + 84
            place(im, txt(counted(p["labs"][k], q), "sansb", 28, col), bx + bw / 2, vy, alpha=a * r(t, tk, tk + 0.2))

def chain(im, x, y, items, t, t0, a):
    n = len(items); bw, bh, gap = 360, 150, 70; x0 = x - (n * bw + (n - 1) * gap) / 2
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, (title, sub, tk) in enumerate(items):
        q = eo(r(t, tk, tk + 0.5)); bx = x0 + k * (bw + gap)
        if q <= 0: continue
        if k:
            lq = eo(r(t, tk - 0.2, tk + 0.2)); lx0 = bx - gap; d.line([(lx0, y), (lx0 + gap * lq, y)], fill=RED + (255,), width=6)
            for e_ in (lx0 + 8, lx0 + gap - 8):
                if lq > 0.5: d.ellipse([e_ - 8, y - 8, e_ + 8, y + 8], fill=RED + (255,))
        yy = y + (1 - q) * 30; d.rounded_rectangle([bx, yy - bh / 2, bx + bw, yy + bh / 2], 14, fill=(NAVY_US if k < 3 else RED) + (int(240 * q),))
        place(lay, txt(title, "sansb", 25, IVORY, 2), bx + bw / 2, yy - 22, alpha=q); place(lay, txt(sub, "serifi", 26, SOFT), bx + bw / 2, yy + 28, alpha=q)
    im.alpha_composite(lay_alpha(lay, a))

def screen(im, x, y, p, t, t0, a):
    s = eo(a); w_, h_ = 600, 440; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x - w_ / 2, y - h_ / 2, x + w_ / 2, y + h_ / 2], 10, fill=(14, 22, 40, 255), outline=INK + (255,), width=6)
    gl = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse([w_ * 0.1, h_ * 0.05, w_ * 0.9, h_ * 0.95], fill=(90, 130, 200, 90)); lay.alpha_composite(gl.filter(ImageFilter.GaussianBlur(50)), (int(x - w_ / 2), int(y - h_ / 2)))
    place(lay, person_card(*p), x, y - 5, scale=0.9)
    for yy in range(int(y - h_ / 2) + 8, int(y + h_ / 2) - 8, 4): d.line([(x - w_ / 2 + 8, yy), (x + w_ / 2 - 8, yy)], fill=(0, 0, 0, 22), width=1)
    place(lay, label_box("ON THE BIG SCREEN · LIVE", 20, RED, IVORY), x, y + h_ / 2 + 28)
    place(im, lay_alpha(lay, a), W / 2, H / 2 + (1 - s) * 30, scale=0.92 + 0.08 * back(a))
    return y + h_ / 2 + 50

def el_draw(im, e, t, a):
    """draw one element; returns the bottom anchor for its branch"""
    k, x, y, p = e["kind"], e["x"], e["y"], e["pay"]; ti = t - e["tin"]; s = eo(a)
    if k == "person":
        c = person_card(*p); place(im, c, x, y + (1 - s) * 30, scale=0.86 + 0.14 * back(a), alpha=min(1, a * 1.5))
        trace(im, (x - 144, y - 179, x + 144, y + 179), t, e["tin"] + 0.25, RED, 3, loop=False); return y + 185
    if k == "cut":
        c = cutimg(p[0], p[1]); place(im, c, x, y + (1 - s) * 34, scale=0.84 + 0.16 * back(a), alpha=min(1, a * 1.5))
        if a > 0.5: V.credit(im, p[2], a)
        return y + p[1] / 2 + 10
    if k == "photo":
        c = photocard(p[0], p[1]); z = 1.0 + 0.03 * cl(ti / 12); place(im, c, x, y, scale=z * (0.95 + 0.05 * s), alpha=a)
        if a > 0.5: V.credit(im, p[2], a)
        return y + c.height / 2
    if k == "lab":
        lb = label_box(p[0], 28, p[1], IVORY); place(im, lb, x + (1 - s) * 24, y, alpha=a)
        trace(im, (x - lb.width / 2 - 6, y - lb.height / 2 - 6, x + lb.width / 2 + 6, y + lb.height / 2 + 6), t, e["tin"] + 0.2, RED, 3, loop=False)
        return y + lb.height / 2 + 8
    if k == "big":
        place(im, txt(counted(p[0], count_frac(ti)), "disp", p[2], p[1]), x, y, scale=1.12 - 0.12 * eo5(a) + 0.05 * (1 - r(ti, COUNT_DUR, COUNT_DUR + 0.25)) * r(ti, COUNT_DUR - 0.05, COUNT_DUR), alpha=a); return y + p[2] * 0.55
    if k == "count":
        v = int(round(p[0] * count_frac(ti))); place(im, txt(str(v), "disp", 230, p[1]), x, y, alpha=a); return y + 120
    if k == "note":
        place(im, txt("— " + p, "serifi", 30, MUTE), x, y, alpha=a); return y + 20
    if k == "stamp":
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); V.stamp(lay, p[0], x, y, t, e["tin"], 58, -8, p[1]); im.alpha_composite(lay_alpha(lay, cl(a))); return y + 40
    if k == "chart":
        T0.rev_chart(im, x, y, t, e["tin"], a); return y + 40
    if k == "words": words(im, x, y, p, t, e["tin"], a); return y + p[1]
    if k == "quote":
        text, attr, size, gold = p
        mw = 860 if size < 50 else 1000
        place(im, quote_mark(), x - mw / 2 - 30, y - size * 0.9, alpha=a * r(ti, 0, 0.3))
        words(im, x, y, (text, size, "serifi", INK, gold, mw), t, e["tin"], a)
        nl = math.ceil(txt(text, "serifi", size).width / mw); place(im, txt("— " + attr, "sansm", 26, MUTE), x, y + nl * size * 0.62 + 30, alpha=a * r(ti, 0.8, 1.2))
        return y + 120
    if k == "grid": grid(im, x, y, p, t, e["tin"], a); return y + 200
    if k == "bars": bars(im, x, y, p, t, e["tin"], a); return y + 40
    if k == "chain": chain(im, x, y, p, t, e["tin"], a); return y + 80
    if k == "screen": return screen(im, x, y, p, t, e["tin"], a)
    if k == "focus":
        place(im, txt("FOCUS.", "disp", 200, RED), x, y, scale=1.1 - 0.1 * eo5(r(ti, 0, 0.5)), alpha=a * r(ti, 0, 0.3)); return y + 100
    return y

def branch(d, px, ex, ey, p):
    pts = [(px, AX_Y - 26), (px, BUS_Y), (ex, BUS_Y), (ex, ey)]
    seg = [math.dist(pts[k], pts[k + 1]) for k in range(3)]; tot = sum(seg) * p; out = [pts[0]]
    for k, sl in enumerate(seg):
        if tot >= sl: out.append(pts[k + 1]); tot -= sl
        else: f = tot / max(sl, 1); out.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)); break
    if len(out) > 1: d.line(out, fill=GOLD2 + (int(230 * min(1, p * 3)),), width=3, joint="curve")
    if p >= 1: d.ellipse([ex - 7, BUS_Y - 7, ex + 7, BUS_Y + 7], fill=RED + (255,)); d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=RED + (255,))

def draw_axis(im, t):
    d = ImageDraw.Draw(im); hx = head_x(t)
    if hx is None: return
    ap = active_pin(t); fade_all = r(t, TR["y0"] - 0.3, TR["y0"] + 0.3)
    d.line([(LX0, AX_Y), (hx, AX_Y)], fill=INK + (int(255 * fade_all),), width=5)
    d.ellipse([LX0 - 7, AX_Y - 7, LX0 + 7, AX_Y + 7], fill=INK + (int(255 * fade_all),))
    moving = any(TR[YB[i]] <= t < PIN_T[i] for i in range(8)) or (TR["lesson"] <= t < TR["lesson"] + 1.25)
    if moving:
        seg0 = max([LX0] + [PX[i] for i in range(8) if PIN_T[i] <= t])
        if hx > seg0 + 2: d.line([(seg0, AX_Y), (hx, AX_Y)], fill=RED + (255,), width=7)
        d.ellipse([hx - 10, AX_Y - 10, hx + 10, AX_Y + 10], fill=RED + (255,)); d.ellipse([hx - 18, AX_Y - 18, hx + 18, AX_Y + 18], outline=RED + (110,), width=3)
    if t >= TR["lesson"] + 1.0:
        a = r(t, TR["lesson"] + 1.0, TR["lesson"] + 1.3); d.polygon([(LX1 + 18, AX_Y), (LX1 - 4, AX_Y - 13), (LX1 - 4, AX_Y + 13)], fill=INK + (int(255 * a),))
    for i in range(8):
        tt = t - PIN_T[i]
        if tt < -0.05: continue
        px = PX[i]; cur = (i == ap); e = eo5(r(tt, -0.05, 0.3))
        if cur and 0 <= tt < 0.6:
            q = eo(tt / 0.6); rr = 20 + 150 * q; d.ellipse([px - rr, AX_Y - rr, px + rr, AX_Y + rr], outline=RED + (int(200 * (1 - q)),), width=max(1, int(6 * (1 - q))))
        if cur:
            for kk in range(2):
                ph = (tt * 0.55 + kk / 2) % 1; rr = 20 + ph * 42; d.ellipse([px - rr, AX_Y - rr, px + rr, AX_Y + rr], outline=RED + (int(130 * (1 - ph)),), width=3)
            rr = 17 * e; d.ellipse([px - rr - 5, AX_Y - rr - 5, px + rr + 5, AX_Y + rr + 5], fill=WHITE + (255,)); d.ellipse([px - rr, AX_Y - rr, px + rr, AX_Y + rr], fill=RED + (255,))
            place(im, label_box(str(YEARS[i]), 30, RED, IVORY), px, AX_Y + 50, scale=0.9 + 0.1 * e, alpha=e)
        else:
            d.ellipse([px - 14, AX_Y - 14, px + 14, AX_Y + 14], fill=IVORY + (255,)); d.ellipse([px - 10, AX_Y - 10, px + 10, AX_Y + 10], fill=GOLD2 + (255,), outline=INK + (255,), width=3)
            place(im, txt(str(YEARS[i]), "sansb", 30, INK, 2), px, AX_Y + 50, alpha=e)
        place(im, txt(DESC[i], "sansm", 21, INK if cur else MUTE), px, AX_Y + 92, alpha=r(tt, 0.3, 0.7))

ANCH = {}
def scene_stage(t):
    im = V.bg(); draw_axis(im, t)
    for e in EL:
        if t < e["tin"] - 0.6 or t > e["tout"] + 0.05: continue
        aout = 1 - r(t, e["tout"] - 0.45, e["tout"]); ain = eio(r(t, e["tin"], e["tin"] + 0.4)); a = ain * aout
        pin = PIN_OF.get(e["b"])
        if pin is not None and e["branch"]:
            bp = eo(r(t, e["tin"] - 0.55, e["tin"])); ey = ANCH.get(id(e), e["y"] + 150)
            if bp > 0 and aout > 0:
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); branch(ImageDraw.Draw(lay), PX[pin], e["x"], ey, bp); im.alpha_composite(lay_alpha(lay, aout))
        if a > 0:
            e2 = e if aout >= 1 else dict(e, y=e["y"] - 60 * (1 - eo(aout)) ** 0.7)
            an = el_draw(im, e2, t, a)
            if aout >= 1: ANCH[id(e)] = an
    return im

# ---------------- map scene: the Microsoft deal ----------------
CUP, RED_, BOS = (-122.03, 37.32), (-122.12, 47.67), (-71.06, 42.36)
VA = geo.albers(-116.6, 42.7); VB = geo.albers(-97.0, 39.2)
def map_view(t):
    a = eio(r(t, st("map", 2, -0.2), st("map", 2, 1.6))); k0 = 2.0 - 0.12 * eio(r(t, TR["map"], st("map", 2, -0.2)))
    return VA[0] + (VB[0] - VA[0]) * a, VA[1] + (VB[1] - VA[1]) * a, k0 * math.exp(math.log(3.05 / k0) * a)
def mp(lonlat, v): x, y = geo.albers(*lonlat); return W / 2 + (x - v[0]) / v[2], H / 2 - (y - v[1]) / v[2]
def scene_map(t):
    v = map_view(t); im = V.bg(); im.alpha_composite(geo.us_map(*v)); d = ImageDraw.Draw(im)
    zo = eio(r(t, st("map", 2, -0.2), st("map", 2, 1.6)))
    for name, ll in [("WASHINGTON", (-120.5, 47.3)), ("OREGON", (-120.6, 43.9)), ("CALIFORNIA", (-119.6, 37.0)), ("NEVADA", (-116.8, 39.4)), ("MASSACHUSETTS", (-72.0, 43.6))]:
        x, y = mp(ll, v); al = (1 - zo) if name != "MASSACHUSETTS" else zo
        if name in ("WASHINGTON", "CALIFORNIA", "MASSACHUSETTS") or zo < 0.5: place(im, txt(name, "sansb", 20 if zo < 0.5 else 15, (170, 164, 150), 8), x, y, alpha=al * 0.95)
    pc, pr, pb = mp(CUP, v), mp(RED_, v), mp(BOS, v)
    place(im, label_box("1997 · A DEAL WITH THE RIVAL", 26, NAVY, IVORY), W / 2, 70, alpha=r(t, TR["map"] + 0.3, TR["map"] + 0.8))
    map_pin(im, d, pc, t, st("map", 0, 0.6), "APPLE", "Cupertino, California")
    map_pin(im, d, pr, t, mid("map", 1, 0.5), "MICROSOFT", "Redmond, Washington")
    p2 = eio(r(t, st("map", 2, 1.0), st("map", 2, 2.4))); draw_arc(im, arc_pts(pc, pb, -0.18), p2, t)
    map_pin(im, d, pb, t, st("map", 2, 2.2), "BOSTON", "Macworld Expo · Aug 6, 1997", side="l")
    f1 = mid("map", 3, 0.6); p1 = eio(r(t, f1, f1 + 1.4)); arc = arc_pts(pr, pc, 0.28 * (1 - 0.6 * zo)); draw_arc(im, arc, p1, t)
    if p1 > 0.6:
        mx, my = arc[len(arc) // 2]; f0 = st("map", 4, 0.3)
        if t >= f0:
            place(im, txt(counted("$150M", count_frac(t - f0)), "disp", int(96 - 40 * zo), NAVY_US), mx + 150 - 90 * zo, my, scale=1.1 - 0.1 * eo5(r(t, f0, f0 + 0.5)), alpha=r(t, f0, f0 + 0.3))
            place(im, txt("MICROSOFT INVESTS IN APPLE", "sansb", int(22 - 6 * zo), INK, 3), mx + 150 - 90 * zo, my + 62 - 26 * zo, alpha=r(t, f0 + 0.3, f0 + 0.7))
        f2 = mid("map", 4, 0.6)
        if t >= f2: place(im, label_box("NON-VOTING SHARES · NO CONTROL", 24, RED, IVORY), W / 2, 980, alpha=r(t, f2, f2 + 0.4))
    place(im, txt("Map: US Census Bureau boundaries (us-atlas)", "sansm", 16, MUTE), W - 230, 34, alpha=0.9)
    return im

# ---------------- year changes, camera ----------------
def draw_travel(im, t):
    for i in range(8):
        a = TR[YB[i]]
        if not (a <= t < a + TRAVEL + 0.15): continue
        y0 = YEARS[i - 1] if i else 1925; y1 = YEARS[i]; tt = t - a
        roll = r(tt, 0.05, 0.95); v = y0 + (y1 - y0) * (1 - (1 - roll) ** 2.2)
        if roll >= 1: v = y1
        fly = eio(r(tt, 0.95, 1.45)); cx = W / 2 + (PX[i] - W / 2) * fly; cy = 430 + (AX_Y + 50 - 430) * fly
        sc = 1 - 0.86 * fly; al = eio(r(tt, 0.0, 0.2)) * (1 - r(tt, 1.35, 1.5))
        if fly < 0.05:
            d = ImageDraw.Draw(im); uw = 330 * eo(r(tt, 0.1, 0.5)); d.rectangle([W / 2 - uw, 560, W / 2 + uw, 568], fill=RED + (int(255 * al),))
            if i: place(im, txt(f"+{y1 - y0} YEARS", "sansb", 26, MUTE, 8), W / 2, 610, alpha=al * r(tt, 0.3, 0.6))
        odometer(im, v, cx, cy, 230, NAVY if roll < 1 else RED, al, sc)
def cam_z(t):
    for i in range(8):
        a = TR[YB[i]]; nx = TR[YB[i + 1]] if i < 7 else TR["lesson"]
        if i == 4: nx = TR["map"]
        if a <= t < a + TRAVEL: return 1 + 0.035 * (1 - eio(r(t, a, a + 0.7)))
        if a + TRAVEL <= t < nx: return 1 + 0.035 * eio(r(t, a + TRAVEL, nx))
    for b0 in ("deal", "y4b"):
        a = TR[b0]; nx = NEXT_TR.get(b0, 1e9)
        if a <= t < nx: return 1 + 0.035 * eio(r(t, a, nx))
    return 1.0
def stage(t): im = scene_stage(t); draw_travel(im, t); return zoom(im, cam_z(t))

# ---------------- brand ident + end screen ----------------
def ident(t, t0):
    tt = t - t0; im = navy_bg(); out = eio(r(tt, 4.4, 5.0)); g1 = 1 - out
    if g1 > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); p = eo(r(tt, 0.1, 1.3)); hw = 440 * p
        if p > 0: place(lay, glow(700, (120, 160, 220), 60), W / 2, 495, alpha=p * 0.8); V.gl(lay, W / 2 - hw, 495, W / 2 + hw, 1, 3, RED)
        er = r(tt, 0.8, 1.7); place(lay, glow(560, (255, 255, 255), 70), W / 2, 320, alpha=er * (1 - er) * 2.4)
        place(lay, emblem_us(230), W / 2, 320, scale=0.84 + 0.16 * back(er), alpha=eio(er))
        E.words_in(lay, W / 2, 578, ["EMPIRE", "STORIES"], tt, 1.4, 112, "cardo", IVORY, 0.16)
        place(lay, txt("THE STORIES BEHIND GLOBAL EMPIRES.", "sansm", 26, SOFT, 9), W / 2, 668, alpha=eio(r(tt, 2.4, 3.0)))
        place(lay, txt("PRESENTS", "sansb", 26, RED, 16), W / 2, 790, alpha=eio(r(tt, 3.3, 3.8)))
        im.alpha_composite(lay_alpha(lay, g1), (0, int(-40 * out)))
    if tt > 4.7:
        place(im, label_box("EPISODE 02", 26, RED, IVORY), W / 2, 380, alpha=eio(r(tt, 4.8, 5.2)))
        E.words_in(im, W / 2, 520, ["The", "Burger"], tt, 5.0, 104, "serif", IVORY, 0.1)
        E.words_in(im, W / 2, 650, ["Landlord."], tt, 5.3, 104, "serif", IVORY, 0.1)
        V.gl(im, W / 2 - 260 * eo(r(tt, 5.6, 6.3)), 745, W / 2 + 260 * eo(r(tt, 5.6, 6.3)), 1, 3, RED)
    E.dust(im, t, 0.6); return im

def frame_rgba(t):
    if IDENT_T - 0.5 <= t < IDENT_T + IDENT_DUR:
        b = ident(t, IDENT_T)
        if t < IDENT_T + 0.1: return Image.blend(stage(t), b, eio(r(t, IDENT_T - 0.5, IDENT_T + 0.1)))
        if t >= IDENT_T + IDENT_DUR - 0.7: return Image.blend(b, stage(t), eio(r(t, IDENT_T + IDENT_DUR - 0.7, IDENT_T + IDENT_DUR)))
        return b
    if TR["map"] <= t < TR["deal"] + XF:
        m = scene_map(t)
        if t < TR["map"] + XF: return Image.blend(stage(t), m, eio(r(t, TR["map"], TR["map"] + XF)))
        if t >= TR["deal"]: return Image.blend(m, stage(t), eio(r(t, TR["deal"], TR["deal"] + XF)))
        return m
    if t >= OUTRO:
        b = T0.end_screen(t, OUTRO + 0.2)
        if t < OUTRO + 0.8: b = Image.blend(stage(t), b, eio(r(t, OUTRO, OUTRO + 0.8)))
        fo = r(t, END - 0.8, END)
        if fo > 0: b.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
        return b
    if t < 0.6: b = stage(t); b.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.6))))); return b
    return stage(t)

VIG = None
def frame(t):
    global VIG
    arr = np.asarray(frame_rgba(t).convert("RGB"), np.int16)
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; VIG = (1 - 0.13 * (((xx - W / 2) / (W / 1.15)) ** 2 + ((yy - H / 2) / (H / 0.95)) ** 2)).astype(np.float32)[..., None]
    return ((arr + E.GRAIN[int(t * 24) % 6] // 3) * VIG).clip(0, 255).astype(np.uint8)

def srt():
    f = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(s * 1000 % 1000):03d}"
    caps = [(m["t"], m["t"] + m["dur"] + 0.12, m["cap"]) for m in META]
    return "\n".join(f"{k + 1}\n{f(a)} --> {f(b)}\n{x}\n" for k, (a, b, x) in enumerate(caps))
def chapters():
    def f(s): s = int(s); return f"{s // 60}:{s % 60:02d}"
    return [(0, "Cold open"), (TR["y0"], "1948: the Speedee System")], f

def render(t0, t1, path):
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f_ in range(int(round(t0 * FPS)), int(round(t1 * FPS))): p.stdin.write(frame(f_ / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, path)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "info":
        print("END", round(END, 1), "IDENT", round(IDENT_T, 1), {b: round(TR[b], 1) for b in BEATS}, "OUTRO", OUTRO)
    elif cmd == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]; c = Image.new("RGB", (640 * 3, 360 * ((len(ts) + 2) // 3)))
        for k, t in enumerate(ts):
            for tw in np.arange(max(0, t - 1.5), t, 0.25): frame_rgba(tw)
            c.paste(Image.fromarray(frame(t)).resize((640, 360)), ((k % 3) * 640, (k // 3) * 360))
        c.save(sys.argv[3], quality=85)
    elif cmd == "full":
        t = float(sys.argv[2]); Image.fromarray(frame(t)).save(sys.argv[3], quality=90)
    elif cmd == "srt": open(f"{D}/EMPIRE_STORIES_Ep01.srt", "w").write(srt())
    elif cmd == "chapters":
        ch, f = chapters(); print("\n".join(f"{f(a)} {n}" for a, n in ch))
    else:
        a, b = float(sys.argv[2]), float(sys.argv[3])
        for tw in np.arange(max(0, a - 1.5), a, 0.2): frame_rgba(tw)
        render(a, b, f"{D}/parts/p_{int(a * 10):05d}.mp4")
