"""EMPIRE STORIES · Episode 01 — full-length renderer.
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
D = "/home/claude/es/ep01"
META = json.load(open(os.environ.get("EP_META", f"{D}/voice/meta.json")))

# ---------------- timing ----------------
IDENT_DUR = 7.8; TRAVEL = 1.5; XF = 0.6; ENDSCREEN = 14.0
YB = ["y0", "y1", "y2", "y3", "y4", "y5", "y6", "y7"]
SENT = {}; TR = {}; BEATS = []; t = 0.9; prev = None; IDENT_T = None; OUTRO = None
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
END = max(OUTRO + ENDSCREEN, t + 2.0)
NEXT_TR = {b: (TR[BEATS[k + 1]] if k + 1 < len(BEATS) else OUTRO) for k, b in enumerate(BEATS)}
NEXT_TR["lesson"] = OUTRO
def st(b, i=0, off=0.0): return SENT[b][i] + off
def mid(b, i, frac): m = [x for x in META if x["beat"] == b][i]; return m["t"] + m["dur"] * frac
def P(b, i): return SENT[b][i] - 0.1          # panel boundary: elements of the previous panel leave here

# ---------------- timeline geometry ----------------
AX_Y = 862; BUS_Y = 780; PX = [250 + i * 203 for i in range(8)]; LX0 = 110; LX1 = 1840
YEARS = [1976, 1985, 1995, 1996, 1997, 1998, 2001, 2007]
DESC = ["Apple founded", "Jobs leaves", "Revenue: $11B", "Buys NeXT", "Jobs returns", "The iMac", "The iPod", "The iPhone"]
PIN_T = {i: TR[YB[i]] + TRAVEL for i in range(8)}
PIN_OF = {"y0": 0, "y1": 1, "y2": 2, "y3": 3, "y4": 4, "deal": 4, "y4b": 4, "y5": 5, "y6": 6, "y7": 7}

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

# --- cold open
h = "hook"
el(h, "photo", L, 500, ("hq_infinite_loop_crop.jpg", 820, CR["hq"]), st(h, 0, 0.1), False, tout=mid(h, 1, 0.5))
el(h, "lab", L, 860, ("APPLE · CUPERTINO, CALIFORNIA", INK), st(h, 0, 0.8), False, tout=mid(h, 1, 0.5))
el(h, "big", R_ + 60, 430, ("OCT 1997", INK, 150), st(h, 1, 0.6), False, tout=P(h, 2))
el(h, "person", L, 520, ("Michael Dell", "Dell Computer"), mid(h, 1, 0.55), False, tout=P(h, 5))
el(h, "lab", R_ + 60, 560, ("ONE OF THE MOST POWERFUL MEN IN COMPUTERS", INK), mid(h, 1, 0.7), False, tout=P(h, 2))
el(h, "lab", R_, 360, ("WHAT WOULD YOU DO WITH APPLE?", INK), st(h, 2, 0.1), False, tout=P(h, 5))
el(h, "quote", R_ + 20, 560, ("“I'd shut it down and give the money back to the shareholders.”", "Michael Dell, October 1997", 50, (1, 2, 3)), st(h, 4, 0.0), False, tout=P(h, 5))
el(h, "big", L, 450, ("−$1B", RED, 150), mid(h, 6, 0.55), False, tout=P(h, 9))
el(h, "lab", L, 570, ("APPLE'S NET LOSS · 1997", INK), mid(h, 6, 0.8), False, tout=P(h, 9))
el(h, "big", R_, 450, ("3%", RED, 150), mid(h, 7, 0.6), False, tout=P(h, 8) + 0.2)
el(h, "lab", R_, 570, ("SHARE OF THE WORLD PC MARKET", INK), mid(h, 7, 0.8), False, tout=P(h, 8) + 0.2)
el(h, "big", R_, 450, ("+$3.5B", NAVY_US, 150), mid(h, 8, 0.6), False, tout=P(h, 9))
el(h, "lab", R_, 570, ("NET INCOME · 2007", INK), mid(h, 8, 0.8), False, tout=P(h, 9))
el(h, "words", 960, 440, ("So what changed?", 120, "serifi", INK, (2,), 1500), st(h, 9, 0.0), False)
el(h, "words", 960, 620, ("And how much of it was really one man?", 56, "serif", MUTE, (), 1500), st(h, 10, 0.0), False)
# --- 1976
el("y0", "lab", 960, 150, ("TO UNDERSTAND THE RESCUE, START WITH THE FALL", INK), st("y0", 0, 0.3), False, tout=P("y0", 1) + 0.3)
el("y0", "person", 780, 420, ("Steve Jobs", "Co-founder"), st("y0", 1, 1.5))
el("y0", "person", 1120, 420, ("Steve Wozniak", "Co-founder"), st("y0", 1, 2.1))
el("y0", "lab", 950, 150, ("APPLE COMPUTER · 1976", INK), mid("y0", 1, 0.6), False)
# --- 1985
el("y1", "person", L, 420, ("Steve Jobs", "Leaves Apple, 1985"), st("y1", 0, 0.5))
el("y1", "lab", L, 150, ("OUT AFTER A BOARDROOM FIGHT", RED), mid("y1", 0, 0.6), False)
el("y1", "cut", R_, 380, ("nextcube_cut.png", 330, CR["next"]), st("y1", 1, 0.4))
el("y1", "lab", R_, 150, ("STARTS AGAIN: NeXT", INK), mid("y1", 1, 0.7), False)
# --- 1995
b = "y2"
el(b, "chart", 860, 640, None, st(b, 1, 0.0), tout=P(b, 3))
el(b, "lab", 860, 150, ("APPLE REVENUE · FY1991–FY1995", INK), st(b, 1, 0.0), False, tout=P(b, 3))
el(b, "stamp", 1450, 380, ("THEN THE FALL", RED), mid(b, 2, 0.3), False, tout=P(b, 3))
el(b, "lab", 560, 200, ("1 · WINDOWS PCs: CHEAPER EVERY YEAR", INK), st(b, 3, 0.3), False)
el(b, "lab", 560, 300, ("2 · MAC CLONES TAKE APPLE'S CUSTOMERS", INK), st(b, 4, 0.5), False)
el(b, "lab", 560, 400, ("3 · A MAZE OF NUMBERED MODELS", INK), st(b, 5, 0.5), False)
el(b, "lab", 560, 500, ("4 · THE NEW MAC OS IS FALLING APART", RED), st(b, 6, 0.6))
el(b, "photo", 1380, 380, ("clone_powercomputing_crop.jpg", 560, CR["clone"]), st(b, 4, 0.3), False, tout=P(b, 5))
el(b, "cut", 1380, 400, ("powermac_beige_cut.png", 380, CR["pm"]), st(b, 5, 0.3), False)
# --- 1996
b = "y3"
el(b, "big", L, 330, ("−$816M", RED, 130), mid(b, 0, 0.55), tout=P(b, 3))
el(b, "lab", L, 450, ("NET LOSS · FY1996", INK), mid(b, 0, 0.8), False, tout=P(b, 3))
el(b, "words", R_ + 20, 360, ("“Beleaguered.”", 96, "serifi", INK, (0,), 900), mid(b, 2, 0.55), False, tout=P(b, 3))
el(b, "note", R_ + 20, 470, "the press's favourite word for Apple", mid(b, 2, 0.8), False, tout=P(b, 3))
el(b, "person", L, 420, ("Gil Amelio", "CEO, 1996–97"), st(b, 3, 0.3), tout=P(b, 6))
el(b, "lab", R_, 320, ("NEEDED: A MODERN OPERATING SYSTEM", INK), st(b, 4, 0.4), False, tout=P(b, 6))
el(b, "stamp", R_, 470, ("BUILDING ONE FAILED", RED), st(b, 5, 0.3), False, tout=P(b, 6))
el(b, "photo", L, 380, ("bebox_crop.jpg", 520, CR["be"]), st(b, 6, 0.4), tout=P(b, 9))
el(b, "lab", L, 650, ("THE FAVOURITE: Be", MUTE), mid(b, 6, 0.7), False, tout=P(b, 9))
el(b, "cut", R_, 380, ("nextcube_cut.png", 330, CR["next"]), st(b, 7, 0.6), tout=P(b, 9))
el(b, "lab", R_, 650, ("THE SURPRISE: NeXT", RED), mid(b, 8, 0.6), False, tout=P(b, 9))
el(b, "big", L, 330, ("$400M", NAVY_US, 150), mid(b, 9, 0.6), tout=P(b, 11))
el(b, "lab", L, 450, ("APPLE BUYS NeXT · DEC 20, 1996", INK), mid(b, 9, 0.85), False, tout=P(b, 11))
el(b, "person", R_, 420, ("Steve Jobs", "Adviser, 1997"), st(b, 10, 0.3), tout=P(b, 11))
el(b, "lab", 960, 200, ("NeXT SOFTWARE → MAC OS X", INK), st(b, 12, 0.3), False)
el(b, "words", 960, 330, ("…and something nobody had put a price on.", 54, "serifi", MUTE, (), 1500), st(b, 13, 0.2), False, tout=P(b, 14) + 0.2)
el(b, "person", 960, 450, ("Steve Jobs", "The real acquisition"), st(b, 14, 0.0))
# --- 1997: the takeover
b = "y4"
el(b, "lab", L, 300, ("−$708M IN ONE QUARTER", RED), mid(b, 1, 0.35), tout=P(b, 2))
el(b, "big", R_, 330, ("−2,700", RED, 140), mid(b, 1, 0.75), False, tout=P(b, 2))
el(b, "lab", R_, 450, ("FULL-TIME JOBS CUT", INK), mid(b, 1, 0.9), False, tout=P(b, 2))
el(b, "person", L, 420, ("Gil Amelio", "CEO, 1996–97"), st(b, 2, 0.4), tout=P(b, 4))
el(b, "stamp", L, 470, ("RESIGNED · JULY 9", RED), mid(b, 2, 0.5), False, tout=P(b, 4))
el(b, "lab", R_, 330, ("JOBS: ADVISER ON PAPER", INK), st(b, 3, 0.4), False, tout=P(b, 4))
el(b, "lab", R_, 430, ("…STEERING IN PRACTICE", RED), mid(b, 3, 0.6), False, tout=P(b, 4))
el(b, "person", L, 420, ("Steve Jobs", "Interim CEO, 1997"), st(b, 4, 0.6))
el(b, "lab", R_, 330, ("SEPT 16, 1997 · INTERIM CEO", NAVY_US), mid(b, 4, 0.7), False)
el(b, "lab", R_, 430, ("KEPT “INTERIM” UNTIL 2000", INK), mid(b, 5, 0.6), False)
# --- 1997: deal terms, the boos, the signal
b = "deal"
el(b, "big", R_, 300, ("$150M", NAVY_US, 130), st(b, 0, 0.0), False, tout=P(b, 3))
el(b, "lab", R_, 420, ("MICROSOFT STAKE · NON-VOTING", INK), st(b, 0, 0.3), False, tout=P(b, 3))
el(b, "lab", L, 220, ("+ OFFICE FOR MAC · 5+ YEARS", NAVY_US), mid(b, 0, 0.5), False, tout=P(b, 3))
el(b, "lab", L, 320, ("+ INTERNET EXPLORER AS DEFAULT", INK), mid(b, 1, 0.5), False, tout=P(b, 3))
el(b, "lab", L, 420, ("+ LEGAL DISPUTES SETTLED", INK), mid(b, 2, 0.5), tout=P(b, 3))
el(b, "screen", 520, 400, ("Bill Gates", "Microsoft"), st(b, 3, 0.6), False, tout=P(b, 6))
el(b, "stamp", R_ + 60, 230, ("BOOS", RED), st(b, 4, 0.3), False, tout=P(b, 6))
el(b, "quote", 1340, 470, ("“We have to let go of this notion that for Apple to win, Microsoft has to lose.”", "Steve Jobs, Macworld Boston 1997", 42, (13, 14, 15, 16)), st(b, 5, 0.8), False, tout=P(b, 6))
el(b, "words", 960, 250, ("Not the money. The signal.", 92, "serif", INK, (4,), 1600), mid(b, 6, 0.6), False)
el(b, "lab", 960, 420, ("WITHOUT OFFICE → LITTLE REASON TO BUY A MAC", RED), st(b, 7, 0.5), False)
el(b, "lab", 960, 520, ("WITH OFFICE → THE MAC HAS A FUTURE", NAVY_US), st(b, 8, 0.3))
# --- 1997: subtraction
b = "y4b"
el(b, "person", L, 420, ("Michael Dell", "Dell Computer"), st(b, 0, 0.3), tout=P(b, 2))
el(b, "lab", R_, 380, ("“I'D SHUT IT DOWN”", RED), mid(b, 0, 0.6), False, tout=P(b, 2))
el(b, "big", L, 330, ("−28%", RED, 140), mid(b, 2, 0.4), tout=P(b, 4))
el(b, "lab", L, 450, ("REVENUE · DOWN TO $7.1B", INK), mid(b, 2, 0.75), False, tout=P(b, 4))
el(b, "big", R_, 330, ("−$1B", RED, 140), mid(b, 3, 0.25), False, tout=P(b, 4))
el(b, "lab", R_, 450, ("FY1997 NET LOSS", INK), mid(b, 3, 0.45), False, tout=P(b, 4))
el(b, "note", R_, 520, "about two-thirds one-time costs, like buying NeXT", mid(b, 3, 0.7), False, tout=P(b, 4))
el(b, "words", 960, 280, ("He didn't add. He subtracted.", 100, "serif", INK, (4,), 1600), mid(b, 4, 0.4), False, tout=P(b, 8))
el(b, "quote", 960, 520, ("“Which ones should I tell my friends to buy?”", "Steve Jobs, 1997", 58, (6, 7)), st(b, 6, 0.0), False, tout=P(b, 8))
el(b, "cut", L, 380, ("newton_cut.png", 330, CR["newton"]), mid(b, 8, 0.75), tout=P(b, 10))
el(b, "stamp", L + 40, 420, ("CUT", RED), mid(b, 8, 0.88), False, tout=P(b, 10))
el(b, "big", R_, 320, ("−70%", RED, 140), mid(b, 8, 0.4), False, tout=P(b, 10))
el(b, "lab", R_, 440, ("OF APPLE'S PRODUCTS CANCELLED", INK), mid(b, 8, 0.6), False, tout=P(b, 10))
el(b, "lab", R_, 540, ("MAC CLONES: ENDED", RED), st(b, 9, 0.3), False, tout=P(b, 10))
el(b, "grid", 960, 420, dict(lab=st(b, 11, 0.0), fill=st(b, 12, 0.0), rule=st(b, 13, 0.2), pulse=mid(b, 15, 0.1)), st(b, 10, 0.5), False)
# --- 1998
b = "y5"
el(b, "cut", 700, 400, ("imac34_cut.png", 420, CR["imac"]), st(b, 0, 0.6), tout=P(b, 6))
el(b, "lab", R_ + 20, 220, ("MAY 6, 1998 · THE iMAC", NAVY_US), mid(b, 0, 0.6), False, tout=P(b, 4))
el(b, "lab", R_ + 20, 320, ("ALL-IN-ONE · SEE-THROUGH BLUE-GREEN", INK), mid(b, 2, 0.4), False, tout=P(b, 4))
el(b, "lab", R_ + 20, 420, ("“i” = INTERNET", RED), mid(b, 3, 0.5), False, tout=P(b, 4))
el(b, "lab", R_ + 20, 220, ("NO FLOPPY DRIVE", RED), mid(b, 4, 0.35), False, tout=P(b, 6))
el(b, "lab", R_ + 20, 320, ("USB PORTS", INK), mid(b, 4, 0.65), False, tout=P(b, 6))
el(b, "big", R_ + 20, 470, ("$1,299", NAVY_US, 120), mid(b, 5, 0.75), False, tout=P(b, 6))
el(b, "lab", R_ + 20, 580, ("ON SALE AUG 15, 1998", INK), mid(b, 5, 0.9), False, tout=P(b, 6))
el(b, "big", L, 330, ("278,000", NAVY_US, 130), mid(b, 6, 0.6), tout=P(b, 10))
el(b, "lab", L, 450, ("iMACS IN THE FIRST 6 WEEKS", INK), mid(b, 6, 0.85), False, tout=P(b, 10))
el(b, "note", L, 515, "the fastest-selling Mac Apple had made", mid(b, 7, 0.3), False, tout=P(b, 10))
el(b, "big", R_, 330, ("+$309M", NAVY_US, 130), mid(b, 8, 0.75), False, tout=P(b, 10))
el(b, "lab", R_, 450, ("FY1998 PROFIT · FIRST SINCE 1995", INK), mid(b, 9, 0.2), False, tout=P(b, 10))
el(b, "big", L, 330, ("6 DAYS", NAVY_US, 140), mid(b, 11, 0.7), False)
el(b, "lab", L, 450, ("OF STOCK IN THE WAREHOUSE", INK), mid(b, 11, 0.85))
el(b, "person", R_, 420, ("Michael Dell", "Dell Computer"), mid(b, 12, 0.5), False)
el(b, "stamp", R_, 680, ("BEATEN AT HIS OWN GAME?", RED), mid(b, 13, 0.75), False)
# --- 2001
b = "y6"
el(b, "bars", 960, 600, dict(data=[("FY98", 0.309), ("FY99", 0.601), ("FY00", 0.786), ("FY01", -0.025)], sc=380, labs=["$309M", "$601M", "$786M", "−$25M"],
                             t=[st(b, 0, 0.0), mid(b, 0, 0.35), mid(b, 0, 0.75), mid(b, 1, 0.7)]), st(b, 0, 0.0), tout=P(b, 2))
el(b, "lab", 960, 150, ("APPLE NET INCOME · FY1998–FY2001", INK), st(b, 0, 0.0), False, tout=P(b, 2))
el(b, "words", 960, 330, ("The Mac alone wasn't going to build an empire.", 70, "serif", INK, (2, 3), 1500), st(b, 2, 0.4), False, tout=P(b, 4))
el(b, "cut", 720, 400, ("ipod_cut.png", 400, CR["ipod"]), mid(b, 4, 0.55))
el(b, "lab", R_ + 20, 250, ("OCTOBER 23, 2001", NAVY_US), mid(b, 4, 0.3), False)
el(b, "lab", R_ + 20, 350, ("1,000 SONGS IN YOUR POCKET", INK), mid(b, 5, 0.35), False)
el(b, "big", R_ + 20, 480, ("$399", NAVY_US, 110), mid(b, 5, 0.8), False)
el(b, "lab", R_ + 20, 600, ("COMPUTERS → CONSUMER ELECTRONICS", RED), mid(b, 6, 0.5), False)
# --- 2007
b = "y7"
el(b, "lab", 960, 220, ("JANUARY 9, 2007 · SAN FRANCISCO", NAVY_US), mid(b, 0, 0.4), False, tout=P(b, 3))
el(b, "lab", 470, 380, ("A WIDESCREEN iPOD", INK), mid(b, 1, 0.15), False, tout=P(b, 3))
el(b, "lab", 960, 380, ("A MOBILE PHONE", INK), mid(b, 1, 0.45), False, tout=P(b, 3))
el(b, "lab", 1450, 380, ("AN INTERNET COMMUNICATOR", INK), mid(b, 1, 0.75), False, tout=P(b, 3))
el(b, "stamp", 960, 530, ("ONE DEVICE", RED), mid(b, 2, 0.75), False, tout=P(b, 3))
el(b, "cut", 720, 400, ("iphone_cut.png", 460, CR["iphone"]), st(b, 3, 0.3))
el(b, "big", R_, 330, ("$3.5B", NAVY_US, 150), mid(b, 4, 0.65), False)
el(b, "lab", R_, 450, ("FY2007 NET INCOME", INK), mid(b, 4, 0.85), False)
el(b, "lab", R_, 540, ("TEN YEARS AFTER A $1B LOSS", RED), st(b, 5, 0.3), False)
# --- OUR TAKE
b = "lesson"
el(b, "lab", 960, 120, ("OUR TAKE", RED), st(b, 0, 0.0), False)
el(b, "words", 960, 250, ("So, did Steve Jobs save Apple?", 84, "serif", INK, (), 1600), st(b, 0, 0.0), False, tout=P(b, 6))
el(b, "words", 960, 380, ("The rescue was a chain.", 60, "serifi", MUTE, (3, 4), 1500), mid(b, 1, 0.4), False, tout=P(b, 2) + 0.3)
el(b, "chain", 960, 470, [("THE NeXT DEAL", "brought Jobs + Mac OS X", mid(b, 2, 0.1)), ("THE MICROSOFT DEAL", "bought time and trust", mid(b, 3, 0.1)),
                          ("FOUR PRODUCTS", "do a few things well", mid(b, 4, 0.1)), ("THE iMAC", "people wanted a Mac again", mid(b, 5, 0.1))], st(b, 2, 0.0), False, tout=P(b, 6))
el(b, "count", 960, 380, (90, RED), mid(b, 6, 0.75), False, tout=P(b, 8))
el(b, "lab", 960, 540, ("DAYS FROM GOING BROKE?", RED), mid(b, 6, 0.9), False, tout=P(b, 8))
el(b, "note", 960, 610, "Steve Jobs, looking back · 90 or 190, the lesson is the same", st(b, 7, 0.3), False, tout=P(b, 8))
el(b, "words", 960, 260, ("The hardest decision is rarely what to build.", 70, "serif", INK, (), 1600), st(b, 8, 0.6), False, tout=P(b, 10))
el(b, "focus", 960, 480, "FOCUS.", st(b, 9, 0.0), False, tout=P(b, 10))
el(b, "words", 960, 640, ("It's what to stop doing.", 54, "serifi", INK, (3, 4, 5), 1500), st(b, 9, 0.1), False, tout=P(b, 10))
el(b, "words", 960, 240, ("Every empire has a turning point.", 80, "serif", INK, (4,), 1600), st(b, 10, 0.0), False)
el(b, "grid", 960, 520, dict(lab=1e9, fill=1e9, rule=1e9, pulse=1e9, small=True), st(b, 11, 0.4), False)

# ---------------- hero portraits: a new person first fills the centre, big, then slides to their slot ----------------
HERO_SCALE = 1.45
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
    d = ImageDraw.Draw(im); data = p["data"]; n = len(data); bw, gap = 120, 70; x0 = x - (n * bw + (n - 1) * gap) / 2
    d.line([(x0 - 30, y), (x0 + n * bw + (n - 1) * gap + 30, y)], fill=INK + (int(255 * a),), width=3)
    for k, ((lab, v), tk) in enumerate(zip(data, p["t"])):
        q = eo(r(t, tk, tk + 0.7)); hh = v * p["sc"] * q; bx = x0 + k * (bw + gap); col = RED if v < 0 else NAVY_US
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
            m = eio(r(t, he, he + 0.6)); cx, cy = 960, (470 if PIN_OF.get(e["b"]) is not None else 540)
            hx, hy, hs = cx + (x - cx) * m, cy + (y - cy) * m, HERO_SCALE + (1 - HERO_SCALE) * m
        c = person_card(*p); place(im, c, hx, hy + (1 - s) * 30, scale=hs * (0.86 + 0.14 * back(a)), alpha=min(1, a * 1.5))
        if not he or t >= he + 0.6: trace(im, (x - 144, y - 179, x + 144, y + 179), t, (he + 0.6 if he else e["tin"]) + 0.25, RED, 3, loop=False)
        return y + 185
    if k == "cut":
        c = cutimg(p[0], p[1]); place(im, c, x, y + (1 - s) * 34, scale=0.84 + 0.16 * back(a), alpha=min(1, a * 1.5))
        if a > 0.5: V.credit(im, p[2], a)
        return y + p[1] / 2 + 10
    if k == "photo":
        c = photocard(p[0], p[1]); z = 1.0 + 0.03 * cl(ti / 12); place(im, c, x, y + (1 - s) * 26, scale=z * (0.97 + 0.03 * s), alpha=eio(cl(a)))
        if a > 0.5: V.credit(im, p[2], a)
        return y + c.height / 2
    if k == "lab":
        lb = badge(p[0], p[1]); place(im, lb, x, y + (1 - s) * 26, alpha=eio(cl(a)))      # one unit: box + aligned frame, fades up
        return y + lb.height / 2 + 2
    if k == "big":
        place(im, txt(counted(p[0], count_frac(ti)), "disp", p[2], p[1]), x, y + (1 - s) * 22, scale=1.12 - 0.12 * eo5(a) + 0.05 * (1 - r(ti, COUNT_DUR, COUNT_DUR + 0.25)) * r(ti, COUNT_DUR - 0.05, COUNT_DUR), alpha=a); return y + p[2] * 0.55
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
        mw = e.get("mw") or (860 if size < 50 else 1000)
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
        aout = eio(1 - r(t, e["tout"] - 0.5, e["tout"])); ain = eio(r(t, e["tin"], e["tin"] + 0.6)); a = ain * aout
        pin = PIN_OF.get(e["b"])
        if pin is not None and e["branch"]:
            tb = (e["hero"] + 1.1) if e.get("hero") else e["tin"]; bp = eo(r(t, tb - 0.55, tb)); ey = ANCH.get(id(e), e["y"] + 150)
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
        if i == 4: nx = TR["map"]
        if a <= t < a + TRAVEL: return 1 + 0.035 * (1 - eio(r(t, a, a + 0.7)))
        if a + TRAVEL <= t < nx: return 1 + 0.035 * eio(r(t, a + TRAVEL, nx))
    for b0 in ("deal", "y4b"):
        a = TR[b0]; nx = NEXT_TR[b0]
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
        place(im, label_box("EPISODE 01", 26, RED, IVORY), W / 2, 380, alpha=eio(r(tt, 4.8, 5.2)))
        E.words_in(im, W / 2, 520, ["Apple", "Was", "Almost"], tt, 5.0, 104, "serif", IVORY, 0.1)
        E.words_in(im, W / 2, 650, ["Finished."], tt, 5.3, 104, "serif", IVORY, 0.1)
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
    return [(0, "Cold open: \"I'd shut it down\""), (TR["y0"], "The fall"), (st("y3", 3) - 0.5, "The $400 million gamble"), (TR["y4"], "The takeover"),
            (TR["map"], "A deal with the enemy"), (TR["y4b"], "The art of subtraction"), (TR["y5"], "Hello, again: the iMac"), (TR["y6"], "Beyond the computer"),
            (TR["lesson"], "Our take: what really saved Apple?")], f

def render(t0, t1, path):
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f_ in range(int(round(t0 * FPS)), int(round(t1 * FPS))): p.stdin.write(frame(f_ / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, path)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "info":
        print("END", round(END, 1), "IDENT", round(IDENT_T, 1), {b: round(TR[b], 1) for b in BEATS}, "OUTRO", round(OUTRO, 1))
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
