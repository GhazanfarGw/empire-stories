import sys; sys.path.insert(0, "/home/claude/es/thumbkit")
from tk import *
def build(v):
    im = base(); glow(im, 1380, 470, 560, RED, 120); glow(im, 380, 560, 420, GOLD, 40)
    # people (AI illustrations): Sonneborn back-left, brothers back-right, Kroc front
    son = fit_h(key_flood(Image.open(A + "people/harry-sonneborn.png")), 640)
    bro = fit_h(key_flood(Image.open(A + "people/dick-&-mac-mcdonald.png")), 700)
    kroc = fit_h(key_flood(Image.open(A + "people/ray-kroc.png")), 1000)
    put(im, son, 880, H - son.height + 40, rim=(120, 140, 170))
    put(im, bro, W - bro.width + 120, H - bro.height + 30, rim=(120, 140, 170))
    put(im, kroc, 1050, H - kroc.height + 60, rim=RED)
    tag(im, W - 290, 24)
    # company icon: real photo of the Golden Arches sign
    sign = Image.open("/home/claude/es/assets/mcd_sign_crop.jpg").crop((0, 40, 457, 600)); sign = fit_h(key_sky(sign), 330)
    put(im, sign, 60, 40, rim=IVORY, rimw=9)
    # story object: the Big Mac
    bm = Image.open(A + "mcd_bigmac.jpg"); bm = key_white(bm.crop((0, 0, bm.width, bm.height)))
    bm = bm.crop(bm.getbbox()); bm = fit_h(bm, 250); put(im, bm, 70, H - bm.height - 24, shadow=True)
    if v == "A":
        text(im, "BURGERS?", 150, IVORY, 70, 590, stroke=4)
        text(im, "NO. RENT.", 190, GOLD, 64, 790, stroke=5)
    else:
        text(im, "THE $139B", 150, IVORY, 70, 590, stroke=4)
        text(im, "LANDLORD", 190, GOLD, 64, 790, stroke=5)
    pill(im, "McDONALD'S · 1948–2026", 320, 290, bg=RED, fg=IVORY, size=36)
    save(im, f"/home/claude/es/ep02/thumbs/thumb_V2_{v}.jpg")
for v in "AB": build(v)
