"""EMPIRE STORIES — demo v3 (US red + navy, cold open -> ident, crunchy year changes, end screen) (master brief): brand ident -> hook -> composed Vox-style timeline (all past pins stay) -> animated US map -> lesson -> brand outro."""
import sys, os, math, json, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, "/home/claude/es"); _a = sys.argv; sys.argv = ["x", "q"]
import es_v4 as V4
sys.argv = _a
import types, es_demo, es_seg2, es_v3
NAVY_US = (10, 49, 97); NAVY_US2 = (28, 74, 132); RED_US = (179, 25, 66)
_MAP = {(212, 175, 55): RED_US, (11, 19, 43): NAVY_US, (196, 58, 46): RED_US, (196, 72, 60): RED_US, (176, 140, 30): NAVY_US, (22, 33, 66): NAVY_US2}
for _m in (es_demo, es_seg2, es_v3, V4):
    for _n, _v in list(vars(_m).items()):
        if isinstance(_v, tuple) and _v in _MAP: setattr(_m, _n, _MAP[_v])
        elif isinstance(_v, types.FunctionType) and _v.__defaults__:
            _v.__defaults__ = tuple(_MAP.get(d, d) if isinstance(d, tuple) else d for d in _v.__defaults__)
es_demo.BG = es_demo.make_bg(); es_seg2.BG = es_demo.BG
import paper as PK
es_v3.PAPER = PK.make_grey_bg()
import geo
sys.path.insert(0, "/home/claude/es/tl3")
V = V4.V; S = V.S; E = V.E
from es_v3 import W, H, FPS, NAVY, GOLD, IVORY, place, txt, r, eo, eio, eo5, cl, font, INK, RED, MUTE, WHITE
GOLD2 = NAVY_US; NAVY2 = NAVY_US2; trace = V4.trace
SOFT = (200, 208, 222)
META = json.load(open("/home/claude/es/tl3/voice/meta.json"))

def back(x): x = cl(x); return 1 + 2.4 * (x - 1) ** 3 + 1.4 * (x - 1) ** 2
from es_v3 import wtxt
def hl_us(im, cx, cy, words, t, t0, size, k="serif", color=INK, gold=(), stagger=0.1, maxw=1500, lh=1.22):
    f = font(k, size); D = ImageDraw.Draw(Image.new("L", (4, 4))); sp = D.textlength(" ", font=f); lines, cur, cw = [], [], 0
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
                hot = n in gold
                if hot:
                    p = eo(r(t, t0 + n * stagger + 0.3, t0 + n * stagger + 0.7))
                    if p > 0: ImageDraw.Draw(im).rectangle([x - 4, y + size * 0.48, x - 4 + (ww + 8) * p, y + size * 0.48 + max(5, size * 0.09)], fill=RED + (255,))
                place(im, wtxt(w_, k, size, RED if hot else color), x + ww / 2, y + (1 - eo(a)) * 22, alpha=eio(a))
            x += ww + sp; n += 1
        y += size * lh
V.hl_words = hl_us

# ---------------- timing ----------------
IDENT_DUR = 7.8; TRAVEL = 1.5; XF = 0.6; ENDSCREEN = 12.0; IDENT_T = None
YB = ["y0", "y1", "y2", "y3", "y4", "y5", "y6", "y7"]
SENT = {}; TR = {}; BEATS = []; t = 0.9; prev = None
for m in META:
    b = m["beat"]
    if m["i"] == 4: IDENT_T = t; t += IDENT_DUR + 0.3
    if b != prev:
        if b in YB: TR[b] = t; t += TRAVEL
        elif b in ("map", "y4b"): TR[b] = t; t += XF + 0.2
        elif b == "lesson": TR[b] = t; t += 1.4
        else: TR[b] = t
        BEATS.append(b); SENT[b] = []; prev = b
    m["t"] = t; SENT[b].append(t); t += m["dur"] + m["pause"]
OUTRO = t - 0.4; END = OUTRO + ENDSCREEN
INTRO_END = 0.0
NEXT_TR = {b: (TR[BEATS[k + 1]] if k + 1 < len(BEATS) else OUTRO) for k, b in enumerate(BEATS)}
def st(b, i=0, off=0.0): return SENT[b][i] + off
def _m(): pass
def mid(b, i, frac): m = [x for x in META if x["beat"] == b][i]; return m["t"] + m["dur"] * frac

# ---------------- timeline geometry ----------------
AX_Y = 862; BUS_Y = 780; PX = [250 + i * 203 for i in range(8)]; LX0 = 110; LX1 = 1840
YEARS = [1976, 1985, 1995, 1996, 1997, 1998, 2001, 2007]
DESC = ["Apple founded", "Jobs pushed out", "Peak: $11.1B", "Buys NeXT", "Jobs returns", "The iMac", "The iPod", "The iPhone"]
PIN_T = {i: TR[YB[i]] + TRAVEL for i in range(8)}

def head_x(t):
    if t < st("hook", 4): return None
    if t < TR["y0"]: return LX0 + 60 * eo(r(t, st("hook", 4), TR["y0"]))
    for i in range(8):
        a = TR[YB[i]]
        if t < a + TRAVEL: x0 = PX[i - 1] if i else LX0 + 60; return x0 + (PX[i] - x0) * eio(r(t, a, a + TRAVEL - 0.05))
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

# ---------------- visual atoms ----------------
@functools.lru_cache(None)
def label_box(text, size, bgc, fg):
    ti = txt(text, "sansb", size, fg, 3); im = Image.new("RGBA", (ti.width + 32, ti.height + 16), bgc + (255,)); im.alpha_composite(ti, (16, 8)); return im

PEOPLE = next((p for p in ["/mnt/user-data/uploads/e/Empire Stories/Ep01 - How Steve Jobs Helped Save Apple/assets/photos_people", "/home/claude/es/assets/people"] if os.path.isdir(p)), "/home/claude/es/assets/people")
def person_photo(name):
    base = name.lower().replace(".", "")
    for slug in (base.replace(" ", "-"), base.replace(" ", "_")):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            p = os.path.join(PEOPLE, slug + ext)
            if os.path.exists(p): return p
    return None
def duotone(img, w, h):
    """brand treatment for a supplied portrait: cover-crop, B&W, navy shadows -> ivory highlights"""
    im = img.convert("L"); s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x0 = (im.width - w) // 2; im = im.crop((x0, 0, x0 + w, h))
    from PIL import ImageOps
    im = ImageOps.autocontrast(im, cutoff=1); return ImageOps.colorize(im, black=(6, 26, 56), mid=(88, 112, 150), white=IVORY).convert("RGBA")
@functools.lru_cache(None)
def person_card(name, role, w=280, h=350):
    ph = person_photo(name)
    if ph:
        k = 2; im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * k - 1, h * k - 1], 18 * k, fill=255)
        body = Image.new("RGBA", im.size, NAVY + (255,)); body.alpha_composite(duotone(Image.open(ph), w * k, int(h * k * 0.79)), (0, 0)); im.paste(body, (0, 0), mask); d = ImageDraw.Draw(im)
        d.line([(w * k * 0.12, h * k * 0.79), (w * k * 0.88, h * k * 0.79)], fill=RED + (255,), width=2 * k)
        d.text((w * k / 2, h * k * 0.855), name.upper(), font=font("sansb", 23 * k), fill=IVORY, anchor="mm")
        d.text((w * k / 2, h * k * 0.935), role, font=font("sansm", 17 * k), fill=SOFT, anchor="mm")
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], 18 * k, outline=RED + (220,), width=3 * k)
        return V.shadowed(im.resize((w, h), Image.LANCZOS), 16, (8, 14), 0.3)
    return person_card_ill(name, role, w, h)
@functools.lru_cache(None)
def person_card_ill(name, role, w=280, h=350):
    """clearly illustrative profile card — abstract silhouette, NOT a likeness; tagged ILLUSTRATION"""
    k = 2; im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], 18 * k, fill=NAVY + (255,))
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([w * k * 0.15, h * k * 0.05, w * k * 0.85, h * k * 0.75], fill=(120, 150, 200, 70)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(40 * k)))
    cx = w * k / 2; hy = h * k * 0.36; hr = w * k * 0.17
    d.ellipse([cx - w * k * 0.36, h * k * 0.56, cx + w * k * 0.36, h * k * 1.08], fill=NAVY2 + (255,), outline=SOFT + (255,), width=3 * k)
    d.ellipse([cx - hr, hy - hr * 1.12, cx + hr, hy + hr * 1.12], fill=NAVY2 + (255,), outline=SOFT + (255,), width=3 * k)
    d.rounded_rectangle([0, h * k * 0.79, w * k, h * k], 0, fill=NAVY + (255,))
    d.line([(w * k * 0.12, h * k * 0.79), (w * k * 0.88, h * k * 0.79)], fill=GOLD + (255,), width=2 * k)
    d.text((cx, h * k * 0.855), name.upper(), font=font("sansb", 23 * k), fill=IVORY, anchor="mm")
    d.text((cx, h * k * 0.935), role, font=font("sansm", 17 * k), fill=SOFT, anchor="mm")
    d.text((16 * k, 16 * k), "ILLUSTRATION", font=font("sansb", 11 * k), fill=SOFT + (200,), anchor="lt")
    d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], 18 * k, outline=RED + (200,), width=3 * k)
    return V.shadowed(im.resize((w, h), Image.LANCZOS), 16, (8, 14), 0.3)

@functools.lru_cache(None)
def cutimg(name, h, deg=0): return S.rot(PK.edge_cut(name, h), deg) if deg else PK.edge_cut(name, h)
@functools.lru_cache(None)
def photocard(name, w, deg=0): return S.rot(PK.edge_card(name, w), deg) if deg else PK.edge_card(name, w)

# revenue FY1991-FY1995 (US$B, Apple 10-K)
REV = [("FY91", 6.31), ("FY92", 7.09), ("FY93", 7.98), ("FY94", 9.19), ("FY95", 11.06)]
def rev_chart(im, x, y, t, t0, a):
    d = ImageDraw.Draw(im); bw, gap, sc = 78, 34, 30; x0 = x - (5 * bw + 4 * gap) / 2
    d.line([(x0 - 20, y), (x0 + 5 * bw + 4 * gap + 20, y)], fill=INK + (int(255 * a),), width=3)
    for k, (lab, v) in enumerate(REV):
        p = eo(r(t, t0 + 0.12 * k, t0 + 0.12 * k + 0.6)); hh = v * sc * p; bx = x0 + k * (bw + gap)
        col = GOLD if k == 4 else (198, 190, 170)
        if hh > 1: d.rectangle([bx, y - hh, bx + bw, y], fill=col + (int(255 * a),))
        place(im, txt(lab, "sansb", 20, MUTE, 2), bx + bw / 2, y + 22, alpha=a * r(t, t0, t0 + 0.4))
        if p > 0.02: place(im, txt(f"${v * p:.1f}B", "sansb", 21, INK if k < 4 else RED), bx + bw / 2, y - hh - 20, alpha=a * r(t, t0 + 0.12 * k, t0 + 0.12 * k + 0.2))
    return (x0, y - 11.06 * sc - 40, x0 + 5 * bw + 4 * gap, y + 36)

import re
COUNT_DUR = 1.2
def parse_num(text):
    m = re.match(r"^([+−-]?)(\$?)([\d.,]+)([A-Z%]*)$", text)
    if not m or not (m.group(1) or m.group(2) or m.group(4)): return None
    num = m.group(3).replace(",", ""); dec = len(num.split(".")[1]) if "." in num else 0
    return m.group(1), m.group(2), float(num), dec, m.group(4)
def counted(text, frac):
    p = parse_num(text)
    if p is None: return text
    sg, cur, v, dec, suf = p; x = v * frac
    return f"{sg}{cur}{x:,.{dec}f}{suf}" if dec else f"{sg}{cur}{int(round(x)):,}{suf}"
def count_frac(ti): return eo(r(ti, 0.0, COUNT_DUR))

# ---------------- stage elements: (beat, kind, x, y, payload, t_in) ----------------
EL = []
def el(b, kind, x, y, pay, tin, branch=True, tout=None): EL.append(dict(b=b, kind=kind, x=x, y=y, pay=pay, tin=tin, tout=tout or NEXT_TR[b], branch=branch))
el("hook", "photo", 640, 400, ("hq_infinite_loop_crop.jpg", 820, "Apple HQ, Cupertino · Photo: Joe Ravi, CC BY-SA 3.0"), st("hook", 0, 0.1), False, tout=SENT['hook'][3] + 0.1)
el("hook", "lab", 640, 760, ("APPLE · CUPERTINO, CALIFORNIA", INK), st("hook", 0, 0.8), False, tout=SENT['hook'][3] + 0.1)
el("hook", "big", 1390, 300, ("1997", INK, 170), st("hook", 1, 0.2), False, tout=SENT['hook'][3] + 0.1)
el("hook", "count", 1390, 500, (90, RED), mid("hook", 2, 0.45), False, tout=SENT['hook'][3] + 0.1)
el("hook", "lab", 1390, 640, ("DAYS FROM GOING BROKE", RED), mid("hook", 2, 0.75), False, tout=SENT['hook'][3] + 0.1)
el("hook", "note", 1390, 700, "Steve Jobs, looking back", mid("hook", 2, 0.85), False, tout=SENT['hook'][3] + 0.1)
el("y0", "person", 760, 420, ("Steve Jobs", "Co-founder"), st("y0", 0, 0.9))
el("y0", "person", 1100, 420, ("Steve Wozniak", "Co-founder"), st("y0", 0, 1.5))
el("y0", "lab", 930, 150, ("APPLE COMPUTER · 1976", INK), st("y0", 1, 0.1))
el("y1", "lab", 640, 330, ("PUSHED OUT BY THE BOARD", RED), mid("y1", 0, 0.45))
el("y1", "cut", 1180, 360, ("nextcube_cut.png", 330, "Photo: NeXTcube, Wikimedia Commons, CC BY-SA 3.0"), st("y1", 1, 0.2))
el("y1", "lab", 1180, 640, ("FOUNDS NeXT · 1985", INK), mid("y1", 1, 0.6))
el("y2", "chart", 860, 640, None, st("y2", 0, 0.2))
el("y2", "lab", 860, 150, ("APPLE REVENUE · FY1991–FY1995", INK), st("y2", 1, 0.0), False)
el("y2", "stamp", 1420, 380, ("THEN THE FALL", RED), mid("y2", 2, 0.55))
el("y3", "big", 620, 330, ("−$816M", RED, 120), mid("y3", 0, 0.5))
el("y3", "lab", 620, 450, ("NET LOSS · FY1996", INK), mid("y3", 0, 0.7))
el("y3", "cut", 1200, 340, ("nextcube_cut.png", 290, "Photo: NeXTcube, Wikimedia Commons, CC BY-SA 3.0"), st("y3", 1, 0.3))
el("y3", "lab", 1200, 590, ("APPLE BUYS NeXT · $400M", GOLD), mid("y3", 1, 0.75))
el("y3", "lab", 1200, 670, ("…AND GETS STEVE JOBS BACK", INK), st("y3", 2, 0.3), False)
el("y4", "person", 700, 420, ("Steve Jobs", "Interim CEO, 1997"), st("y4", 0, 0.3))
el("y4", "lab", 1200, 420, ("HIS FIRST MOVE?", GOLD), mid("y4", 0, 0.65))
el("y4b", "cut", 720, 380, ("newton_cut.png", 330, "Photo: Felix Winkelnkemper, CC BY-SA 4.0"), st("y4b", 0, 0.2))
el("y4b", "stamp", 760, 420, ("CUT", RED), mid("y4b", 0, 0.55), False)
el("y4b", "big", 1260, 320, ("−70%", RED, 140), mid("y4b", 0, 0.55))
el("y4b", "lab", 1260, 450, ("OF THE PRODUCT LINE", INK), mid("y4b", 0, 0.8))
el("y4b", "lab", 1260, 600, ("FEWER. BETTER.", GOLD), st("y4b", 1, 0.2))
el("y5", "cut", 740, 400, ("imac34_cut.png", 400, "Photo: Rama / David Fuchs, CC BY-SA 4.0"), st("y5", 0, 0.5))
el("y5", "big", 1270, 320, ("+$309M", GOLD2, 120), mid("y5", 1, 0.45))
el("y5", "lab", 1270, 440, ("FY1998 PROFIT · FIRST SINCE 1995", INK), mid("y5", 1, 0.7))
el("y6", "cut", 740, 400, ("ipod_cut.png", 380, "Photo: Rjcflyer, CC BY 2.5"), mid("y6", 0, 0.35))
el("y6", "lab", 1260, 360, ("1,000 SONGS IN YOUR POCKET", INK), mid("y6", 0, 0.6))
el("y6", "lab", 1260, 450, ("OCTOBER 2001 · $399", GOLD), mid("y6", 0, 0.8))
el("y7", "cut", 740, 400, ("iphone_cut.png", 450, "Photo: Carl Berkeley, CC BY-SA 2.0"), st("y7", 0, 0.6))
el("y7", "big", 1270, 320, ("$3.5B", GOLD2, 140), mid("y7", 1, 0.55))
el("y7", "lab", 1270, 450, ("FY2007 NET INCOME", INK), mid("y7", 1, 0.8))

def el_draw(im, e, t, a):
    """draw element, return bottom-centre anchor for its branch"""
    k, x, y, p = e["kind"], e["x"], e["y"], e["pay"]; ti = t - e["tin"]; s = eo(a)
    if k == "person":
        c = person_card(*p); place(im, c, x, y + (1 - s) * 30, scale=0.86 + 0.14 * back(a), alpha=min(1, a * 1.5))
        trace(im, (x - 144, y - 179, x + 144, y + 179), t, e["tin"] + 0.25, GOLD, 3, loop=False); return y + 185
    if k == "cut":
        c = cutimg(p[0], p[1]); place(im, c, x, y + (1 - s) * 34, scale=0.84 + 0.16 * back(a), alpha=min(1, a * 1.5))
        if a > 0.5: V.credit(im, p[2], a)
        return y + p[1] / 2 + 10
    if k == "photo":
        c = photocard(p[0], p[1]); z = 1.0 + 0.03 * cl(ti / 12); place(im, c, x, y, scale=z * (0.95 + 0.05 * s), alpha=a)
        if a > 0.5: V.credit(im, p[2], a)
        return y + 250
    if k == "lab":
        lb = label_box(p[0], 28, p[1], IVORY); place(im, lb, x + (1 - s) * 24, y, alpha=a)
        trace(im, (x - lb.width / 2 - 6, y - lb.height / 2 - 6, x + lb.width / 2 + 6, y + lb.height / 2 + 6), t, e["tin"] + 0.2, GOLD, 3, loop=False)
        return y + lb.height / 2 + 8
    if k == "big":
        place(im, txt(counted(p[0], count_frac(ti)), "disp", p[2], p[1]), x, y, scale=1.12 - 0.12 * eo5(a) + 0.05 * (1 - r(ti, COUNT_DUR, COUNT_DUR + 0.25)) * r(ti, COUNT_DUR - 0.05, COUNT_DUR), alpha=a); return y + p[2] * 0.55
    if k == "count":
        v = int(round(p[0] * count_frac(ti))); place(im, txt(str(v), "disp", 230, p[1]), x, y, alpha=a); return y + 120
    if k == "note":
        place(im, txt("— " + p, "serifi", 30, MUTE), x, y, alpha=a); return y + 20
    if k == "stamp":
        V.stamp(im, p[0], x, y, t, e["tin"], 58, -8, p[1]); return y + 40
    if k == "chart":
        bb = rev_chart(im, x, y, t, e["tin"], a); return y + 40
    return y

def branch(d, px, ex, ey, p):
    """elbow tree: pin -> up to bus -> across -> up to element bottom"""
    pts = [(px, AX_Y - 26), (px, BUS_Y), (ex, BUS_Y), (ex, ey)]
    seg = [math.dist(pts[k], pts[k + 1]) for k in range(3)]; tot = sum(seg) * p; out = [pts[0]]
    for k, sl in enumerate(seg):
        if tot >= sl: out.append(pts[k + 1]); tot -= sl
        else: f = tot / max(sl, 1); out.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)); break
    if len(out) > 1: d.line(out, fill=GOLD2 + (int(230 * min(1, p * 3)),), width=3, joint="curve")
    if p >= 1: d.ellipse([ex - 7, BUS_Y - 7, ex + 7, BUS_Y + 7], fill=RED + (255,)); d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=RED + (255,))

PIN_OF = {"y0": 0, "y1": 1, "y2": 2, "y3": 3, "y4": 4, "y4b": 4, "y5": 5, "y6": 6, "y7": 7}

def draw_axis(im, t):
    d = ImageDraw.Draw(im); hx = head_x(t)
    if hx is None: return
    ap = active_pin(t); fade_all = r(t, st("hook", 4), st("hook", 4) + 0.6)
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
        px = PX[i]; cur = (i == ap)
        e = eo5(r(tt, -0.05, 0.3))
        if cur and 0 <= tt < 0.6:
            q = eo(tt / 0.6); rr = 20 + 150 * q; d.ellipse([px - rr, AX_Y - rr, px + rr, AX_Y + rr], outline=RED + (int(200 * (1 - q)),), width=max(1, int(6 * (1 - q))))
        if cur:
            for kk in range(2):
                ph = (tt * 0.55 + kk / 2) % 1; rr = 20 + ph * 42
                d.ellipse([px - rr, AX_Y - rr, px + rr, AX_Y + rr], outline=RED + (int(130 * (1 - ph)),), width=3)
            rr = 17 * e; d.ellipse([px - rr - 5, AX_Y - rr - 5, px + rr + 5, AX_Y + rr + 5], fill=WHITE + (255,)); d.ellipse([px - rr, AX_Y - rr, px + rr, AX_Y + rr], fill=RED + (255,))
            yb = label_box(str(YEARS[i]), 30, RED, IVORY); place(im, yb, px, AX_Y + 50, scale=0.9 + 0.1 * e, alpha=e)
        else:
            d.ellipse([px - 14, AX_Y - 14, px + 14, AX_Y + 14], fill=IVORY + (255,)); d.ellipse([px - 10, AX_Y - 10, px + 10, AX_Y + 10], fill=GOLD2 + (255,), outline=INK + (255,), width=3)
            place(im, txt(str(YEARS[i]), "sansb", 30, INK, 2), px, AX_Y + 50, alpha=e)
        place(im, txt(DESC[i], "sansm", 21, INK if cur else MUTE), px, AX_Y + 92, alpha=r(tt, 0.3, 0.7))

def scene_stage(t):
    im = V.bg(); d = ImageDraw.Draw(im)
    draw_axis(im, t)
    for e in EL:
        if t < e["tin"] - 0.6 or t > e["tout"] + 0.05: continue
        aout = 1 - r(t, e["tout"] - 0.45, e["tout"])
        pin = PIN_OF.get(e["b"])
        ain = eio(r(t, e["tin"], e["tin"] + 0.4)); a = ain * aout
        if pin is not None and e["branch"]:
            bp = eo(r(t, e["tin"] - 0.55, e["tin"]))
            # anchor estimated from a dry layout (cheap): use bottom from previous draw cache
            ey = ANCH.get(id(e), e["y"] + 150)
            if bp > 0 and aout > 0:
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); branch(ImageDraw.Draw(lay), PX[pin], e["x"], ey, bp)
                if aout < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * aout)))
                im.alpha_composite(lay)
        if a > 0:
            e2 = e if aout >= 1 else dict(e, y=e["y"] - 60 * (1 - eo(aout)) ** 0.7)
            an = el_draw(im, e2, t, a)
            if aout >= 1: ANCH[id(e)] = an
    # hook question & lesson text
    if SENT["hook"][3] - 0.3 <= t < IDENT_T + 0.6:
        tt = t - st("hook", 3); qa = 1 - r(t, IDENT_T + 0.1, IDENT_T + 0.6)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); V.hl_words(lay, W / 2, 430, "So how did it survive?".split(), tt, 0.0, 108, "serifi", INK, gold=(4,), stagger=0.08)
        if qa < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * qa)))
        im.alpha_composite(lay)
    if t >= TR["lesson"] + 0.8:
        lt = t; L0, L1, L2 = st("lesson", 0), st("lesson", 1), st("lesson", 2)
        place(im, label_box("OUR TAKE", 20, RED, IVORY), W / 2, 130, alpha=r(lt, L0, L0 + 0.4))
        V.hl_words(im, W / 2, 240, "So what really saved Apple?".split(), lt, L0, 64, "serif", INK, stagger=0.06)
        if lt >= L1: V.hl_words(im, W / 2, 380, "Not one product.".split(), lt, L1, 50, "serifi", MUTE, stagger=0.06)
        if lt >= mid("lesson", 1, 0.55):
            f0 = mid("lesson", 1, 0.55); place(im, txt("FOCUS.", "disp", 190, RED), W / 2, 520, scale=1.1 - 0.1 * eo5(r(lt, f0, f0 + 0.5)), alpha=r(lt, f0, f0 + 0.3))
        if lt >= L2: V.hl_words(im, W / 2, 670, "Saying no to almost everything, so the few things that mattered could be great.".split(), lt, L2, 42, "serifi", INK, gold=(2, 3, 4), stagger=0.05, maxw=1500)
    return im
ANCH = {}

# ---------------- map scene (1997 deal) ----------------
CUP, RED_, BOS = (-122.03, 37.32), (-122.12, 47.67), (-71.06, 42.36)
VA = geo.albers(-116.6, 42.7); VB = geo.albers(-97.0, 39.2)
def map_view(t):
    a = eio(r(t, st("map", 2, -0.2), st("map", 2, 1.6)))
    k0 = 2.0 - 0.12 * eio(r(t, TR["map"], st("map", 2, -0.2)))
    cx = VA[0] + (VB[0] - VA[0]) * a; cy = VA[1] + (VB[1] - VA[1]) * a
    return cx, cy, k0 * math.exp(math.log(3.05 / k0) * a)
def mp(lonlat, v): x, y = geo.albers(*lonlat); return W / 2 + (x - v[0]) / v[2], H / 2 - (y - v[1]) / v[2]
def arc_pts(p0, p1, bend, n=60):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2; dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
    cx, cy = mx - dy / L * L * bend, my + dx / L * L * bend
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * cx + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * cy + u * u * p1[1]) for u in np.linspace(0, 1, n)]
def map_pin(im, d, p, t, t0, name, sub, side="r"):
    a = r(t, t0, t0 + 0.3)
    if a <= 0: return
    x, y = p; e = eo5(a)
    for kk in range(2):
        ph = ((t - t0) * 0.6 + kk / 2) % 1; rr = 14 + ph * 46; d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=RED + (int(140 * (1 - ph)),), width=3)
    rr = 13 * e; d.ellipse([x - rr - 5, y - rr - 5, x + rr + 5, y + rr + 5], fill=WHITE + (255,)); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=RED + (255,))
    lb = label_box(name, 26, INK, IVORY); dx = 40 + lb.width / 2 if side == "r" else -40 - lb.width / 2
    place(im, lb, x + dx + (1 - eo(r(t, t0 + 0.15, t0 + 0.5))) * 20 * (1 if side == "r" else -1), y - 20, alpha=r(t, t0 + 0.15, t0 + 0.5))
    sb = txt(sub, "sansm", 21, INK); bx = Image.new("RGBA", (sb.width + 16, sb.height + 8), IVORY + (225,)); bx.alpha_composite(sb, (8, 4))
    place(im, bx, x + dx, y + 24, alpha=r(t, t0 + 0.35, t0 + 0.7))
def draw_arc(im, pts, p, t):
    if p <= 0: return
    n = max(2, int(len(pts) * p)); seg = pts[:n]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).line(seg, fill=(11, 19, 43, 70), width=7, joint="curve")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), (3, 6)); d = ImageDraw.Draw(im)
    d.line(seg, fill=GOLD + (255,), width=5, joint="curve")
    x, y = seg[-1]
    if p < 1: d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=GOLD + (255,), outline=WHITE + (255,), width=3)
    else:
        x0, y0 = seg[-2]; ang = math.atan2(y - y0, x - x0)
        d.polygon([(x + 4 * math.cos(ang), y + 4 * math.sin(ang)), (x - 22 * math.cos(ang - 0.45), y - 22 * math.sin(ang - 0.45)), (x - 22 * math.cos(ang + 0.45), y - 22 * math.sin(ang + 0.45))], fill=GOLD + (255,))
def scene_map(t):
    v = map_view(t); im = V.bg(); im.alpha_composite(geo.us_map(*v)); d = ImageDraw.Draw(im)
    zo = eio(r(t, st("map", 2, -0.2), st("map", 2, 1.6)))
    for name, ll in [("WASHINGTON", (-120.5, 47.3)), ("OREGON", (-120.6, 43.9)), ("CALIFORNIA", (-119.6, 37.0)), ("NEVADA", (-116.8, 39.4)), ("MASSACHUSETTS", (-72.0, 43.6))]:
        x, y = mp(ll, v); al = (1 - zo) if name != "MASSACHUSETTS" else zo
        if name in ("WASHINGTON", "CALIFORNIA", "MASSACHUSETTS") or zo < 0.5: place(im, txt(name, "sansb", 20 if zo < 0.5 else 15, (170, 164, 150), 8), x, y, alpha=al * 0.95)
    pc, pr, pb = mp(CUP, v), mp(RED_, v), mp(BOS, v)
    m0, m1, m2 = st("map", 0), st("map", 1), st("map", 2)
    place(im, label_box("1997 · A DEAL WITH THE RIVAL", 26, NAVY, IVORY), W / 2, 70, alpha=r(t, TR["map"] + 0.3, TR["map"] + 0.8))
    p1 = eio(r(t, mid("map", 1, 0.3), mid("map", 1, 0.3) + 1.4)); draw_arc(im, arc_pts(pr, pc, 0.28 * (1 - 0.6 * zo)), p1, t)
    if p1 > 0.6:
        ap = arc_pts(pr, pc, 0.28 * (1 - 0.6 * zo)); mx, my = ap[len(ap) // 2]
        f0 = mid("map", 1, 0.3) + 0.9; place(im, txt(counted("$150M", count_frac(t - f0)), "disp", int(96 - 40 * zo), GOLD2), mx + 150 - 90 * zo, my, scale=1.1 - 0.1 * eo5(r(t, f0, f0 + 0.5)), alpha=r(t, f0, f0 + 0.3))
        place(im, txt("MICROSOFT INVESTS IN APPLE", "sansb", int(22 - 6 * zo), INK, 3), mx + 150 - 90 * zo, my + 62 - 26 * zo, alpha=r(t, f0 + 0.3, f0 + 0.7))
    map_pin(im, d, pc, t, m0 + 0.6, "APPLE", "Cupertino, California")
    map_pin(im, d, pr, t, m0 + 1.3, "MICROSOFT", "Redmond, Washington")
    p2 = eio(r(t, m2 + 1.4, m2 + 2.8)); draw_arc(im, arc_pts(pc, pb, -0.18), p2, t)
    map_pin(im, d, pb, t, m2 + 2.6, "BOSTON", "Macworld Expo · Aug 6, 1997", side="l")
    place(im, txt("Map: US Census Bureau boundaries (us-atlas)", "sansm", 16, MUTE), W - 230, 34, alpha=0.9)
    return im

# ---------------- year odometer (crunchy year change) ----------------
@functools.lru_cache(None)
def digit(ch, size, col): return txt(ch, "disp", size, col)
def odometer(im, v, cx, cy, size, col, alpha=1.0, scale=1.0):
    a0 = int(math.floor(v)); f = v - a0; sa, sb = f"{a0:04d}", f"{a0 + 1:04d}"
    dw = digit("0", size, col).width; dh = int(size * 1.08); lay = Image.new("RGBA", (dw * 4 + 12, dh), (0, 0, 0, 0))
    ease = eio(min(1, f * 1.0))
    for k in range(4):
        ca, cb = digit(sa[k], size, col), digit(sb[k], size, col); x = k * (dw + 4) + (dw - ca.width) // 2
        if sa[k] == sb[k]: lay.alpha_composite(ca, (x, (dh - ca.height) // 2))
        else:
            off = int(dh * ease); col_ = Image.new("RGBA", (dw + 4, dh), (0, 0, 0, 0))
            col_.alpha_composite(ca, ((dw - ca.width) // 2, (dh - ca.height) // 2 - off)); col_.alpha_composite(cb, ((dw - cb.width) // 2, (dh - cb.height) // 2 + dh - off))
            lay.alpha_composite(col_, (k * (dw + 4), 0))
    place(im, lay, cx, cy, scale=scale, alpha=alpha)

def draw_travel(im, t):
    for i in range(8):
        a = TR[YB[i]]
        if not (a <= t < a + TRAVEL + 0.15): continue
        y0 = YEARS[i - 1] if i else 1970; y1 = YEARS[i]; tt = t - a
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
        if a <= t < a + TRAVEL: return 1 + 0.035 * (1 - eio(r(t, a, a + 0.7)))
        if a + TRAVEL <= t < nx: return 1 + 0.035 * eio(r(t, a + TRAVEL, nx))
    return 1.0
def zoom(im, z, cx=W / 2, cy=520):
    if z <= 1.0005: return im
    w, h = W / z, H / z; x0, y0 = cx - w * cx / W, cy - h * cy / H
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)

# ---------------- brand: ident (after cold open) + end screen ----------------
@functools.lru_cache(None)
def emblem_us(size=230):
    k = 3; S_ = size * k; im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S_ / 2
    d.ellipse([c - S_ * 0.46, c - S_ * 0.46, c + S_ * 0.46, c + S_ * 0.46], outline=RED + (255,), width=int(S_ * 0.022))
    d.ellipse([c - S_ * 0.40, c - S_ * 0.40, c + S_ * 0.40, c + S_ * 0.40], outline=IVORY + (150,), width=int(S_ * 0.006))
    for i in range(5):
        x = c - S_ * 0.2 + i * S_ * 0.1; d.rectangle([x - S_ * 0.018, c - S_ * 0.07, x + S_ * 0.018, c + S_ * 0.17], fill=IVORY + (255,))
    d.polygon([(c - S_ * 0.27, c - S_ * 0.09), (c, c - S_ * 0.26), (c + S_ * 0.27, c - S_ * 0.09)], fill=IVORY + (255,))
    d.rectangle([c - S_ * 0.27, c + S_ * 0.19, c + S_ * 0.27, c + S_ * 0.225], fill=RED + (255,))
    return im.resize((size, size), Image.LANCZOS)
@functools.lru_cache(None)
def glow(size, col, a):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([size * 0.2, size * 0.2, size * 0.8, size * 0.8], fill=col + (a,)); return g.filter(ImageFilter.GaussianBlur(size * 0.12))
def navy_bg(): im = Image.new("RGBA", (W, H), NAVY + (255,)); im.alpha_composite(E.BG); return im

def ident(t, t0):
    tt = t - t0; im = navy_bg()
    out = eio(r(tt, 4.4, 5.0)); g1 = 1 - out
    if g1 > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        p = eo(r(tt, 0.1, 1.3)); hw = 440 * p
        if p > 0: place(lay, glow(700, (120, 160, 220), 60), W / 2, 495, alpha=p * 0.8); V.gl(lay, W / 2 - hw, 495, W / 2 + hw, 1, 3, RED)
        er = r(tt, 0.8, 1.7); place(lay, glow(560, (255, 255, 255), 70), W / 2, 320, alpha=er * (1 - er) * 2.4)
        place(lay, emblem_us(230), W / 2, 320, scale=0.84 + 0.16 * back(er), alpha=eio(er))
        E.words_in(lay, W / 2, 578, ["EMPIRE", "STORIES"], tt, 1.4, 112, "cardo", IVORY, 0.16)
        place(lay, txt("THE STORIES BEHIND GLOBAL EMPIRES.", "sansm", 26, SOFT, 9), W / 2, 668, alpha=eio(r(tt, 2.4, 3.0)))
        place(lay, txt("PRESENTS", "sansb", 26, RED, 16), W / 2, 790, alpha=eio(r(tt, 3.3, 3.8)))
        if g1 < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * g1)))
        im.alpha_composite(lay, (0, int(-40 * out)))
    if tt > 4.7:
        place(im, label_box("EPISODE 01", 26, RED, IVORY), W / 2, 380, alpha=eio(r(tt, 4.8, 5.2)))
        E.words_in(im, W / 2, 520, ["How", "Steve", "Jobs"], tt, 5.0, 104, "serif", IVORY, 0.1)
        E.words_in(im, W / 2, 650, ["Helped", "Save", "Apple"], tt, 5.3, 104, "serif", IVORY, 0.1)
        V.gl(im, W / 2 - 260 * eo(r(tt, 5.6, 6.3)), 745, W / 2 + 260 * eo(r(tt, 5.6, 6.3)), 1, 3, RED)
    E.dust(im, t, 0.6)
    return im

def end_screen(t, t0):
    tt = t - t0; im = navy_bg(); d = ImageDraw.Draw(im)
    LXc = 500
    place(im, emblem_us(170), LXc, 250, scale=0.85 + 0.15 * back(r(tt, 0.2, 0.9)), alpha=eio(r(tt, 0.2, 0.7)))
    E.words_in(im, LXc, 380, ["EMPIRE", "STORIES"], tt, 0.5, 76, "cardo", IVORY, 0.12)
    V.gl(im, LXc - 230 * eo(r(tt, 0.9, 1.5)), 440, LXc + 230 * eo(r(tt, 0.9, 1.5)), 1, 3, RED)
    place(im, txt("THE STORIES BEHIND GLOBAL EMPIRES.", "sansm", 19, SOFT, 6), LXc, 478, alpha=eio(r(tt, 1.2, 1.7)))
    # subscribe element area (YouTube places the subscribe button here)
    sa = eio(r(tt, 1.4, 2.0)); cy = 690
    if sa > 0:
        rr = 105 * (0.9 + 0.1 * back(sa)); d.ellipse([LXc - rr, cy - rr, LXc + rr, cy + rr], outline=IVORY + (int(220 * sa),), width=4)
        ph = (tt * 0.5) % 1; r2 = rr + 6 + 26 * ph; d.ellipse([LXc - r2, cy - r2, LXc + r2, cy + r2], outline=RED + (int(150 * (1 - ph) * sa),), width=3)
        place(im, txt("SUBSCRIBE", "sansb", 26, IVORY, 8), LXc, cy + 168, alpha=sa)
        place(im, txt("for the next story", "serifi", 26, SOFT), LXc, cy + 208, alpha=sa)
    # two video element areas
    for j, (cy2, lab) in enumerate([(300, "WATCH NEXT"), (700, "MORE STORIES")]):
        a = eio(r(tt, 1.0 + 0.3 * j, 1.6 + 0.3 * j)); bx = 1340 + (1 - eo(a)) * 120; w_, h_ = 640, 360
        if a <= 0: continue
        lay = Image.new("RGBA", (w_, h_), NAVY2 + (int(150 * a),)); ImageDraw.Draw(lay).rectangle([0, 0, w_ - 1, h_ - 1], outline=SOFT + (int(120 * a),), width=2)
        im.alpha_composite(lay, (int(bx - w_ / 2), int(cy2 - h_ / 2)))
        trace(im, (bx - w_ / 2 - 6, cy2 - h_ / 2 - 6, bx + w_ / 2 + 6, cy2 + h_ / 2 + 6), tt, 1.4 + 0.3 * j, RED, 3, loop=True)
        place(im, label_box(lab, 22, RED, IVORY), bx - w_ / 2 + 90, cy2 - h_ / 2 - 30, alpha=a)
    place(im, txt("THANKS FOR WATCHING", "sansb", 20, SOFT, 10), LXc, 1010, alpha=eio(r(tt, 2.0, 2.6)))
    E.dust(im, t, 0.5)
    return im

STAGE_CACHE = {}
def stage(t):
    im = scene_stage(t); draw_travel(im, t); return zoom(im, cam_z(t))

def frame_rgba(t):
    if IDENT_T - 0.5 <= t < IDENT_T + IDENT_DUR:
        b = ident(t, IDENT_T)
        if t < IDENT_T + 0.1: return Image.blend(stage(t), b, eio(r(t, IDENT_T - 0.5, IDENT_T + 0.1)))
        if t >= IDENT_T + IDENT_DUR - 0.7: return Image.blend(b, stage(t), eio(r(t, IDENT_T + IDENT_DUR - 0.7, IDENT_T + IDENT_DUR)))
        return b
    if TR["map"] <= t < TR["y4b"] + XF:
        m = scene_map(t)
        if t < TR["map"] + XF: return Image.blend(stage(t), m, eio(r(t, TR["map"], TR["map"] + XF)))
        if t >= TR["y4b"]: return Image.blend(m, stage(t), eio(r(t, TR["y4b"], TR["y4b"] + XF)))
        return m
    if t >= OUTRO:
        b = end_screen(t, OUTRO + 0.2)
        if t < OUTRO + 0.8: b = Image.blend(stage(t), b, eio(r(t, OUTRO, OUTRO + 0.8)))
        fo = r(t, END - 0.8, END)
        if fo > 0: b.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fo))))
        return b
    if t < 0.6: b = stage(t); b.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.6))))); return b
    return stage(t)

# ---------------- captions ----------------
CAPFIX = {"nineteen ninety-seven": "1997", "nineteen seventy-six": "1976", "nineteen eighty-five": "1985", "nineteen ninety-five": "1995", "nineteen ninety-eight": "1998",
          "two thousand one": "2001", "two thousand seven": "2007", "eleven billion dollars": "$11 billion", "eight hundred million dollars": "$800 million",
          "four hundred million": "$400 million", "a hundred and fifty million dollars": "$150 million", "seventy percent": "70%", "three and a half billion dollars": "$3.5 billion",
          "ninety days": "90 days", "a thousand songs": "1,000 songs"}
def cap_text(s):
    for a, b in CAPFIX.items(): s = s.replace(a, b).replace(a[0].upper() + a[1:], b)
    return s
CAPS = [(m["t"], m["t"] + m["dur"] + 0.12, cap_text(m["text"])) for m in META]
def captions(im, t):
    for a, b, text in CAPS:
        if a <= t < b:
            ti = txt(text, "sansm", 30, WHITE)
            if ti.width > 1700:
                ws = text.split(); h_ = len(ws) // 2; ti = txt(" ".join(ws[:h_]), "sansm", 30, WHITE); t2 = txt(" ".join(ws[h_:]), "sansm", 30, WHITE)
                c = Image.new("RGBA", (max(ti.width, t2.width), ti.height + t2.height + 6), (0, 0, 0, 0)); c.alpha_composite(ti, ((c.width - ti.width) // 2, 0)); c.alpha_composite(t2, ((c.width - t2.width) // 2, ti.height + 6)); ti = c
            box = Image.new("RGBA", (ti.width + 40, ti.height + 16), (8, 34, 72, 215)); box.alpha_composite(ti, (20, 8))
            place(im, box, W / 2, H - 18 - box.height / 2, alpha=min(r(t, a, a + 0.15), 1 - r(t, b - 0.15, b))); return
def srt():
    f = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(s * 1000 % 1000):03d}"
    return "\n".join(f"{k + 1}\n{f(a)} --> {f(b)}\n{x}\n" for k, (a, b, x) in enumerate(CAPS))

VIG = None
def frame(t):
    global VIG
    im = frame_rgba(t)
    # no burnt-in subtitles: captions ship as the .srt for YouTube CC
    arr = np.asarray(im.convert("RGB"), np.int16)
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; VIG = (1 - 0.13 * (((xx - W / 2) / (W / 1.15)) ** 2 + ((yy - H / 2) / (H / 0.95)) ** 2)).astype(np.float32)[..., None]
    arr = (arr + E.GRAIN[int(t * 24) % 6] // 3) * VIG
    return arr.clip(0, 255).astype(np.uint8)

def render(t0, t1, path):
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f_ in range(int(round(t0 * FPS)), int(round(t1 * FPS))): p.stdin.write(frame(f_ / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, path)

if __name__ == "__main__":
    if sys.argv[1] == "info":
        print("END", round(END, 1), "IDENT", round(IDENT_T, 1), {b: round(TR[b], 1) for b in BEATS}, "OUTRO", round(OUTRO, 1))
    elif sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        c = Image.new("RGB", (640 * 3, 360 * ((len(ts) + 2) // 3)))
        for k, t in enumerate(ts):
            for tw in np.arange(max(0, t - 1.5), t, 0.25): frame_rgba(tw)   # warm branch anchors
            c.paste(Image.fromarray(frame(t)).resize((640, 360)), ((k % 3) * 640, (k // 3) * 360))
        c.save(sys.argv[3] if len(sys.argv) > 3 else "/home/claude/es/out/_tl3.jpg", quality=85)
    elif sys.argv[1] == "srt": open("/home/claude/es/tl3/EMPIRE_STORIES_demo_v3.srt", "w").write(srt())
    else:
        a, b = float(sys.argv[2]), float(sys.argv[3])
        for tw in np.arange(max(0, a - 1.5), a, 0.2): frame_rgba(tw)
        render(a, b, f"/home/claude/es/tl3/p_{int(a*10):04d}.mp4")
