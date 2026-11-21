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
IDENT_DUR = 7.8; REWIND = 3.6; REW_T = None; TRAVEL = 1.5; XF = 0.6; ENDSCREEN = 14.0
YB = ["y0", "y1", "y2", "y3", "y4", "y5", "y6", "y7"]
from collections import defaultdict
SENT = {}; TR = defaultdict(lambda: 1e9); BEATS = []; t = 0.9; prev = None; IDENT_T = None; OUTRO = None
for m in META:
    b = m["beat"]
    if b != prev:
        if prev == "hook": IDENT_T = t - 0.2; t = IDENT_T + IDENT_DUR + 0.2
        if b == "y0": REW_T = t - 0.2; t += REWIND - 0.2          # cinematic time travel 2026 -> 1948 before the first pin
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
YC_SHIFT = 45     # owner rule: content sits on the screen's middle line (timeline scenes were ~45 px too high)
def el(b, kind, x, y, pay, tin, branch=True, tout=None):
    if b in YB and kind not in ("cine",): y = y + YC_SHIFT
    EL.append(dict(b=b, kind=kind, x=x, y=y, pay=pay, tin=tin, tout=tout or NEXT_TR[b], branch=branch))
L, R_ = 600, 1320          # left / right columns of the stage (widened 21 Nov: use the full screen)
CR = {"hq": "Apple HQ, Cupertino · Photo: Joe Ravi, CC BY-SA 3.0", "next": "NeXTcube · Wikimedia Commons, CC BY-SA 3.0",
      "newton": "Newton MessagePad · Felix Winkelnkemper, CC BY-SA 4.0", "imac": "iMac G3 · Rama / David Fuchs, CC BY-SA 4.0",
      "ipod": "iPod (1st gen) · Rjcflyer, CC BY 2.5", "iphone": "iPhone (1st gen) · Carl Berkeley, CC BY-SA 2.0",
      "clone": "Power Computing Mac clone · Angelgreat, CC BY-SA 4.0", "pm": "Power Macintosh G3 · Klodo6975, public domain",
      "be": "BeBox · Josh Carlson, CC BY 2.0", "lineup": "iMac G3 colours · Stephen Hackett, CC BY-SA 4.0"}

CR.update({"road": "Archive film: Look at Pontiac for 1954 (Jam Handy Organization) · Prelinger Archives, public domain",
           "valley": "San Bernardino Valley · Photo: Doc Searls, CC BY-SA 2.0", "motel": "Route 66, San Bernardino · Photo: John Margolies, Library of Congress (public domain)",
           "downey": "Oldest operating McDonald's, Downey CA · Photo: Northwalker, CC0", "sign": "Speedee sign, Downey CA · Photo: Northwalker, CC0",
           "sbd": "Site of the first McDonald's, San Bernardino · Photo: Cogart Strangehill, CC BY-SA 2.0",
           "desplaines": "McDonald's #1 Store Museum, Des Plaines · Photo: Jerry Huddleston, CC BY 2.0"})
# --- cold open: a simple question, turned upside down (tight cut, everything centre-first)
h = "hook"
el(h, "cine", 960, 540, dict(img="mcd_downey_museum.jpg", z=(1.0, 1.12), pan=(0.3, 0.5), shade="right", cr=CR["downey"]), st(h, 0, -0.6), False, tout=P(h, 2))
el(h, "words", 1500, 470, ("What does McDonald's sell?", 84, "serif", IVORY, (3,), 620), st(h, 0, 0.0), False, tout=P(h, 2))
el(h, "lab", 1500, 690, ("BURGERS · FRIES · MILKSHAKES", RED), st(h, 1, 0.1), False, tout=P(h, 2))
el(h, "big", 580, 480, ("$139.4B", NAVY_US, 150), mid(h, 2, 0.55), False, tout=P(h, 5))
el(h, "lab", 580, 600, ("SPENT AT McDONALD'S · 2025", INK), mid(h, 2, 0.8), False, tout=P(h, 5))
el(h, "big", 1360, 480, ("95%", RED, 150), mid(h, 3, 0.4), False, tout=P(h, 5))
el(h, "lab", 1360, 600, ("RUN BY FRANCHISEES", INK), mid(h, 3, 0.7), False, tout=P(h, 5))
el(h, "stamp", 960, 780, ("THEY PAY RENT", RED), mid(h, 4, 0.7), False, tout=P(h, 5))
el(h, "lab", 960, 200, ("WHAT McDONALD'S ITSELF COLLECTED · 2025", INK), st(h, 5, 0.1), False, tout=P(h, 7))
el(h, "bars", 960, 730, dict(data=[("RENT", 10.442), ("FOOD SALES*", 9.690), ("ROYALTIES", 6.018)], sc=38, bw=230, gap=150,
                             labs=["$10.4B", "$9.7B", "$6.0B"], cols=[RED, NAVY_US, NAVY_US],
                             t=[mid(h, 5, 0.6), mid(h, 6, 0.75), mid(h, 6, 0.3)]), st(h, 5, 0.1), False, tout=P(h, 7))
el(h, "note", 960, 830, "*food sold in the restaurants McDonald's runs itself · source: McDonald's 2025 annual report", mid(h, 6, 0.8), False, tout=P(h, 7))
el(h, "person", 560, 500, ("Harry Sonneborn", "McDonald's first president"), st(h, 7, 0.1), False, tout=P(h, 9))
el(h, "quote", 1280, 480, ("“We are not technically in the food business. We are in the real estate business.”", "Harry Sonneborn, as recounted in McDonald's: Behind the Arches", 50, (12, 13, 14)), st(h, 8, 0.0), False, tout=P(h, 9)); EL[-1]["mw"] = 820
el(h, "words", 960, 450, ("A burger company…", 104, "serif", INK, (), 1600), st(h, 9, 0.0), False, tout=P(h, 10))
el(h, "words", 960, 620, ("…or a landlord that sells burgers?", 80, "serifi", INK, (3,), 1600), mid(h, 9, 0.45), False, tout=P(h, 10))
el(h, "cine", 960, 540, dict(img="sb_valley.jpg", z=(1.0, 1.14), amb="town", pan=(0.45, 0.4), cap="SAN BERNARDINO, CALIFORNIA", sub="the valley today, from the air", cr=CR["valley"]), st(h, 10, 0.0), False)
# --- 1948: the Speedee Service System
b = "y0"
el(b, "place", 960, 430, ("sb_motel66.jpg", 1120, "SAN BERNARDINO · ROUTE 66", "a car town on America's main road", CR["motel"], 0.42), st(b, 0, -0.3), False, tout=mid(b, 0, 0.55))
el(b, "person", L, 420, ("Dick & Mac McDonald", "San Bernardino, 1948"), mid(b, 0, 0.55))
el(b, "photo", R_, 420, ("mcd_sanbernardino_site.jpg", 735, CR["sbd"]), mid(b, 0, 0.7), False, tout=P(b, 1))
el(b, "lab", R_, 712, ("THE ORIGINAL SITE, TODAY A MUSEUM", MUTE), mid(b, 0, 0.9), False, tout=P(b, 1))
el(b, "lab", R_, 250, ("9 MENU ITEMS", NAVY_US), mid(b, 1, 0.45), False, tout=P(b, 2))
el(b, "lab", R_, 330, ("NO CARHOPS", RED), mid(b, 1, 0.62), False, tout=P(b, 2))
el(b, "big", R_, 465, ("15¢", NAVY_US, 150), mid(b, 1, 0.8), False, tout=P(b, 2))
el(b, "lab", R_, 590, ("THE HAMBURGER", INK), mid(b, 1, 0.9), False, tout=P(b, 2))
el(b, "photo", R_, 420, ("mcd_downey_sign.jpg", 327, CR["sign"]), st(b, 2, 0.3), False)
el(b, "lab", R_, 712, ("THE SPEEDEE SERVICE SYSTEM", RED), st(b, 2, 0.6), False)
# --- 1954: Ray Kroc
b = "y1"
el(b, "person", L, 420, ("Ray Kroc", "Milkshake-machine salesman"), st(b, 0, 0.5))
el(b, "big", R_, 370, ("8", NAVY_US, 170), mid(b, 0, 0.82), False, tout=P(b, 2))
el(b, "lab", R_, 500, ("MULTIMIXERS, ONE RESTAURANT", INK), mid(b, 0, 0.9), False, tout=P(b, 2))
el(b, "cine", 960, 540, dict(vid="fr_road1", n=217, z=(1.0, 1.06), amb="car", passby=0.80, cap="1954 · KROC DRIVES WEST", sub="to see one small restaurant in San Bernardino", cr=CR["road"]), st(b, 1, -0.2), False, tout=P(b, 2) + 0.3)
el(b, "words", R_, 420, ("A system that could be copied anywhere.", 62, "serif", INK, (4, 5, 6), 760), st(b, 2, 0.4), False)


# ---------------- hero portraits: a new person first fills the centre, big, then slides to their slot ----------------
HERO_SCALE = 1.4; PS = 1.4          # PS: person cards 30% bigger (owner, 21 Nov)
def _set_hero():
    for e in EL:
        if e["kind"] != "person" or e.get("hero") is False: continue
        later = [o["tin"] for o in EL if o is not e and o["b"] == e["b"] and e["tin"] < o["tin"] < e["tin"] + 3.0]
        he = min([e["tin"] + 2.4] + [x - 0.15 for x in later])
        e["hero"] = he if he - e["tin"] >= 1.1 else None
_set_hero()


# ---------------- badge (locked 21 Nov): label box + red frame baked into ONE image, so frame and box always line up ----------------
@functools.lru_cache(None)
def badge(text, col, size=28):
    lb = label_box(text, size, col, IVORY); g, w = 6, 3
    im = Image.new("RGBA", (lb.width + 2 * (g + w), lb.height + 2 * (g + w)), (0, 0, 0, 0))
    im.alpha_composite(lb, (g + w, g + w))
    ImageDraw.Draw(im).rectangle([0, 0, im.width - 1, im.height - 1], outline=RED + (215,), width=w)
    return im


# ---------------- EMPIRE TODAY card (locked 21 Nov): where the company stands in 2026, every number sourced ----------------
def today(im, x, y, p, t, t0, a):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hd = eo(r(t, t0, t0 + 0.6))
    place(lay, badge(p["title"], RED, 30), x, y - 330 + (1 - hd) * 20, alpha=hd)
    tiles = p["tiles"]; n = len(tiles); cw, ch, gap = 400, 300, 36; x0 = x - (n * cw + (n - 1) * gap) / 2 + cw / 2
    for j, (big, lab, sub) in enumerate(tiles):
        q = eo(r(t, t0 + 0.5 + 0.45 * j, t0 + 1.2 + 0.45 * j))
        if q <= 0: continue
        cx, cy = x0 + j * (cw + gap), y - 40 + (1 - q) * 30
        d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2], 16, fill=(255, 255, 255, int(215 * q)), outline=NAVY_US + (int(255 * q),), width=3)
        d.rectangle([cx - cw / 2 + 3, cy - ch / 2 + 3, cx + cw / 2 - 3, cy - ch / 2 + 12], fill=(RED if j % 2 else NAVY_US) + (int(255 * q),))
        place(lay, txt(counted(big, eo(r(t, t0 + 0.6 + 0.45 * j, t0 + 1.8 + 0.45 * j))), "disp", 92, NAVY_US), cx, cy - 40, alpha=q)
        place(lay, txt(lab, "sansb", 23, INK, 2), cx, cy + 50, alpha=q)
        place(lay, txt(sub, "sansm", 19, MUTE), cx, cy + 92, alpha=q)
    if p.get("foot"): place(lay, txt(p["foot"], "serifi", 28, MUTE), x, y + 190, alpha=r(t, t0 + 2.4, t0 + 3.0))
    im.alpha_composite(lay_alpha(lay, a))


# ---------------- PLACE card (locked 21 Nov): every city/country named gets a real photo, big, framed, caption underneath ----------------
@functools.lru_cache(None)
def place_card(name, w, title, sub, crop_top=None):
    src = Image.open(f"/home/claude/es/assets/{name}").convert("RGB")
    if crop_top is not None:                       # tall photo -> wide strip around a chosen height
        bw_ = int(src.width * 0.92); x0 = (src.width - bw_) // 2; hh = int(bw_ / 1.9); y0 = int((src.height - hh) * crop_top)
        src = src.crop((x0, y0, x0 + bw_, y0 + hh))
    h = int(w * src.height / src.width); h = min(h, 760); ph = src.resize((w, int(w * src.height / src.width)), Image.LANCZOS).crop((0, 0, w, h))
    bd, cap = 0, 96; im = Image.new("RGBA", (w, h + cap), NAVY_US + (255,))
    im.paste(ph, (0, 0)); d = ImageDraw.Draw(im)
    t1 = txt(title, "sansb", 40, IVORY, 4); t2 = txt(sub, "serifi", 26, SOFT)
    top = h; gap_ = 6; blk = t1.height + gap_ + t2.height; y_ = top + (cap - blk) / 2
    im.alpha_composite(t1, (int(im.width / 2 - t1.width / 2), int(y_))); im.alpha_composite(t2, (int(im.width / 2 - t2.width / 2), int(y_ + t1.height + gap_)))
    return T0.PK.torn_image(im, sum(map(ord, name)) % 97), h
def place_el(im, x, y, p, t, t0, a):
    name, w, title, sub, cr = p[:5]; crop = p[5] if len(p) > 5 else None
    c, h = place_card(name, w, title, sub, crop); ti = t - t0; s = eo(a)
    z = 1.0 + 0.035 * cl(ti / 10)                    # slow Ken Burns push-in
    place(im, c, x, y + (1 - s) * 30, scale=z * (0.97 + 0.03 * s), alpha=eio(cl(a)))
    if a > 0.5: V.credit(im, cr, a)
    return y + c.height / 2

# ---------------- TIME TRAVEL (locked 21 Nov): from today back to the first year, like a film rewinding ----------------
REW_IMGS = ["sb_valley.jpg", "mcd_desplaines_museum.jpg", "mcd_downey_museum.jpg", "mcd_downey_sign.jpg", "mcd_sanbernardino_site.jpg", "sb_motel66.jpg"]
@functools.lru_cache(None)
def rew_frame(name, sep):
    im = Image.open(f"/home/claude/es/assets/{name}").convert("RGB"); w, h = 300, 210
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1)); x0 = (im.width - w) // 2; y0 = (im.height - h) // 2
    im = im.crop((x0, y0, x0 + w, y0 + h))
    if sep:
        from PIL import ImageOps
        im = ImageOps.colorize(im.convert("L"), black=(40, 28, 18), mid=(140, 112, 80), white=(244, 232, 205))
    return im
def rewind(t):
    u = r(t, REW_T, REW_T + REWIND); sp = eio(r(u, 0.05, 0.85))          # 0..1 along the journey
    year = 2026 - (2026 - YEARS[0]) * sp
    im = V.bg(); age = sp                                                 # the paper slowly turns sepia as we go back
    if age > 0:
        tint = Image.new("RGBA", (W, H), (150, 112, 60, int(70 * age * (1 - r(u, 0.88, 1.0))))); im.alpha_composite(tint)
    speed = math.sin(math.pi * r(u, 0.05, 0.85))                         # 0 -> fast -> 0
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(strip)
    band = 300; by = 760; a_strip = eio(r(u, 0.0, 0.12)) * (1 - eio(r(u, 0.8, 0.95)))
    if a_strip > 0:
        d.rectangle([0, by - band / 2, W, by + band / 2], fill=(18, 16, 14, 235))
        pos = 3800 * (sp + 0.15 * u)                                       # film runs to the right = going back in time
        fw = 340
        for k in range(-2, 9):
            fx = (k * fw + pos) % (fw * 8) - fw
            for hx in range(int(fx) + 14, int(fx) + fw, 34):              # sprocket holes
                d.rounded_rectangle([hx, by - band / 2 + 10, hx + 18, by - band / 2 + 26], 3, fill=(230, 225, 215, 255))
                d.rounded_rectangle([hx, by + band / 2 - 26, hx + 18, by + band / 2 - 10], 3, fill=(230, 225, 215, 255))
            idx = int((k * fw + pos) // (fw * 8) * 8 + k) % len(REW_IMGS)
            strip.paste(rew_frame(REW_IMGS[idx], age > 0.45), (int(fx + 20), int(by - 105)))
        if speed > 0.2:                                                    # motion blur when the reel spins fast
            strip = strip.filter(ImageFilter.BoxBlur(int(2 + 10 * speed))) if False else strip.transform(strip.size, Image.AFFINE, (1, 0, 0, 0, 1, 0)).filter(ImageFilter.GaussianBlur(1.5 * speed))
        im.alpha_composite(lay_alpha(strip, a_strip))
        dd = ImageDraw.Draw(im)
        for j in range(14):                                                # light streaks rushing right
            sx = (j * 263 + (t - REW_T) * 2600 * (0.4 + speed)) % (W + 600) - 300; sy = 90 + (j * 71) % 360
            dd.line([(sx, sy), (sx + 220 * speed, sy)], fill=(255, 250, 235, int(90 * speed)), width=2)
    lab = r(u, 0.02, 0.15) * (1 - r(u, 0.8, 0.9))
    if lab > 0: place(im, txt("GOING BACK IN TIME", "sansb", 30, RED, 8), W / 2, 210, alpha=lab)
    odometer(im, year, W / 2, 430, 230, NAVY if u < 0.9 else NAVY, 1.0, 1.0)
    fl = math.exp(-((u - 0.86) / 0.035) ** 2)                            # soft flash when we arrive
    if fl > 0.02: im.alpha_composite(Image.new("RGBA", (W, H), (255, 252, 240, int(150 * fl))))
    return im


# ---------------- CINE scene (locked 21 Nov): full-screen photo or archive film, slow camera move, lower-third caption ----------------
FOOT = "/home/claude/es/assets/footage"
@functools.lru_cache(None)
def _cine_photo(name, z):
    im = Image.open(f"/home/claude/es/assets/{name}").convert("RGB"); s = max(W * z / im.width, H * z / im.height)
    return im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
@functools.lru_cache(maxsize=48)
def _cine_frame(d, i): return Image.open(f"{FOOT}/{d}/{i:04d}.jpg").convert("RGB")
@functools.lru_cache(None)
def _shade(kind):
    g = np.zeros((H, W), np.float32); yy, xx = np.mgrid[0:H, 0:W]
    if kind == "right": g = np.clip((xx / W - 0.38) / 0.62, 0, 1) ** 1.2 * 200
    elif kind == "left": g = np.clip((0.62 - xx / W) / 0.62, 0, 1) ** 1.2 * 200
    g = np.maximum(g, np.clip((yy / H - 0.62) / 0.38, 0, 1) ** 1.5 * 210)          # bottom gradient for the lower third
    lay = Image.new("RGBA", (W, H), (8, 12, 24, 0)); lay.putalpha(Image.fromarray(g.astype(np.uint8))); return lay
def cine(im, e, t, a):
    p = e["pay"]; ti = t - e["tin"]; dur = max(1.0, e["tout"] - e["tin"]); u = cl(ti / dur)
    z0, z1 = p.get("z", (1.0, 1.08)); z = z0 + (z1 - z0) * eio(u); px, py = p.get("pan", (0.5, 0.5))
    if "vid" in p:
        n = p["n"]; fr = _cine_frame(p["vid"], max(1, min(n, 1 + int(ti * 30)))); base = fr
        if z != 1.0:
            cw, ch = int(W / z), int(H / z); x0 = int((W - cw) * px); y0 = int((H - ch) * py); base = fr.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    else:
        src = _cine_photo(p["img"], 1.0)
        vw = int(src.width / z); vh = int(vw * H / W)
        if vh > src.height: vh = src.height; vw = int(vh * W / H)
        x0 = int((src.width - vw) * px); y0 = int((src.height - vh) * py); base = src.crop((x0, y0, x0 + vw, y0 + vh)).resize((W, H), Image.BILINEAR)
    lay = base.convert("RGBA"); lay.alpha_composite(_shade(p.get("shade", "bottom")))
    if p.get("cap"):
        la = r(ti, 0.5, 1.1) * (1 - r(t, e["tout"] - 0.6, e["tout"] - 0.1)); s_ = eo(la)
        if la > 0:
            d = ImageDraw.Draw(lay); yb = 900 + (1 - s_) * 16
            d.rectangle([110, yb - 4, 118, yb + 78], fill=RED + (int(255 * la),))
            place(lay, txt(p["cap"], "sansb", 44, IVORY, 4), 140 + txt(p["cap"], "sansb", 44, IVORY, 4).width / 2, yb + 20, alpha=la)
            if p.get("sub"): t2 = txt(p["sub"], "serifi", 30, SOFT); place(lay, t2, 140 + t2.width / 2, yb + 62, alpha=la)
    im.alpha_composite(lay_alpha(lay, a))
    if p.get("cr") and a > 0.5: V.credit(im, p["cr"], a)
    return 0

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
        hx, hy, hs, he = x, y, 1.0, e.get("hero")
        if he:
            m = eio(r(t, he, he + 0.6)); cx, cy = 960, (470 + YC_SHIFT if PIN_OF.get(e["b"]) is not None else 540)
            hx, hy, hs = cx + (x - cx) * m, cy + (y - cy) * m, HERO_SCALE + (1 - HERO_SCALE) * m
        c = person_card(*p); place(im, c, hx, hy + (1 - s) * 30, scale=PS * hs * (0.86 + 0.14 * back(a)), alpha=min(1, a * 1.5))
        return y + 185 * PS
    if k == "cut":
        c = cutimg(p[0], p[1]); place(im, c, x, y + (1 - s) * 34, scale=0.84 + 0.16 * back(a), alpha=min(1, a * 1.5))
        if a > 0.5: V.credit(im, p[2], a)
        return y + p[1] / 2 + 10
    if k == "photo":
        c = photocard(p[0], p[1]); z = 1.0 + 0.03 * cl(ti / 12); place(im, c, x, y + (1 - s) * 26, scale=z * (0.97 + 0.03 * s), alpha=eio(cl(a)))
        if a > 0.5: V.credit(im, p[2], a)
        return y + c.height / 2
    if k == "lab":
        lb = badge(p[0], p[1]); place(im, lb, x, y + (1 - s) * 26, scale=e.get("sc", 1.0), alpha=eio(cl(a)))      # one unit: box + aligned frame, fades up
        return y + lb.height / 2 + 2
    if k == "big":
        place(im, txt(counted(p[0], count_frac(ti)), "disp", p[2], p[1]), x, y + (1 - s) * 22, scale=e.get("sc", 1.0) * (1.12 - 0.12 * eo5(a)) + 0.05 * (1 - r(ti, COUNT_DUR, COUNT_DUR + 0.25)) * r(ti, COUNT_DUR - 0.05, COUNT_DUR), alpha=a); return y + p[2] * 0.55
    if k == "count":
        v = int(round(p[0] * count_frac(ti))); place(im, txt(str(v), "disp", 230, p[1]), x, y, alpha=a); return y + 120
    if k == "note":
        place(im, txt("— " + p, "serifi", 30, MUTE), x, y + (1 - s) * 18, alpha=eio(cl(a))); return y + 20
    if k == "stamp":
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); V.stamp(lay, p[0], x, y, t, e["tin"], 58, -8, p[1]); im.alpha_composite(lay_alpha(lay, cl(a))); return y + 40
    if k == "chart":
        T0.rev_chart(im, x, y, t, e["tin"], a); return y + 40
    if k == "words": words(im, x, y, p, t, e["tin"], a); return y + p[1]
    if k == "quote":
        text, attr, size, gold = p
        mw = e.get("mw") or (940 if size < 50 else 1060)
        place(im, quote_mark(), x - mw / 2 - 30, y - size * 0.9, alpha=a * r(ti, 0, 0.3))
        words(im, x, y, (text, size, "serifi", INK, gold, mw), t, e["tin"], a)
        nl = math.ceil(txt(text, "serifi", size).width / mw); place(im, txt("— " + attr, "sansm", 26, MUTE), x, y + nl * size * 0.62 + 30, alpha=a * r(ti, 0.8, 1.2))
        return y + 120
    if k == "cine": return cine(im, e, t, a)
    if k == "place": return place_el(im, x, y, p, t, e["tin"], a)
    if k == "today": today(im, x, y, p, t, e["tin"], a); return y + 200
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


# ---------------- CENTRE-FIRST layout (locked 21 Nov, owner): new information appears in the centre of the screen;
# when the next item of the same panel arrives, the first one glides left (and shrinks a little) to make room ----------------
MOVABLE = {"big", "lab", "words", "count", "stamp", "note", "photo", "quote", "cut"}
def _set_centre_first():
    from collections import defaultdict as dd
    panels = dd(list)
    for e in EL:
        if e["kind"] in ("cine", "place", "today", "bars", "chain", "grid", "chart", "focus", "screen"): continue
        panels[(e["b"], round(e["tout"], 2))].append(e)
    for es in panels.values():
        cols = []
        for e in sorted(es, key=lambda o: o["tin"]):
            for c in cols:
                if abs(c["x"] - e["x"]) < 200: c["els"].append(e); break
            else: cols.append(dict(x=e["x"], t=e["tin"], els=[e]))
        if len(cols) < 2: continue
        first, nxt = cols[0], cols[1]
        if any(o["kind"] == "person" or o["kind"] not in MOVABLE for o in first["els"]): continue
        if abs(first["x"] - 960) < 60 or nxt["t"] - first["t"] < 0.8: continue
        for o in first["els"]: o["cf"] = (960 - first["x"], nxt["t"] - 0.15)
_set_centre_first()
def centre_first(e, t):
    cf = e.get("cf")
    if not cf: return e
    m = eio(r(t, cf[1], cf[1] + 0.7)); return dict(e, x=e["x"] + cf[0] * (1 - m), sc=1.12 - 0.12 * m)

ANCH = {}
def scene_stage(t):
    im = V.bg(); draw_axis(im, t)
    for e in EL:
        if t < e["tin"] - 0.6 or t > e["tout"] + 0.05: continue
        aout = eio(1 - r(t, e["tout"] - 0.5, e["tout"])); ain = eio(r(t, e["tin"], e["tin"] + 0.6)); a = ain * aout
        pin = PIN_OF.get(e["b"])
        if pin is not None and e["branch"]:
            tb = (e["hero"] + 1.1) if e.get("hero") else e["tin"]; bp = eo(r(t, tb - 0.55, tb)); ey = ANCH.get(id(e), e["y"] + 150)
            if bp > 0 and aout > 0:
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); branch(ImageDraw.Draw(lay), PX[pin], e["x"], ey, bp); im.alpha_composite(lay_alpha(lay, aout))
        if a > 0:
            e2 = centre_first(e, t)
            if aout < 1: e2 = dict(e2, y=e["y"] - 60 * (1 - eo(aout)) ** 0.7)
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
        y0 = YEARS[i - 1] if i else YEARS[0]; y1 = YEARS[i]; tt = t - a
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
        if t >= IDENT_T + IDENT_DUR - 0.7: return Image.blend(b, rewind(t) if REW_T else stage(t), eio(r(t, IDENT_T + IDENT_DUR - 0.7, IDENT_T + IDENT_DUR)))
        return b
    if REW_T and REW_T <= t < REW_T + REWIND: return rewind(t)
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
