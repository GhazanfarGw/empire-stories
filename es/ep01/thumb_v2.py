import sys; sys.path.insert(0, "/home/claude/es/thumbkit")
from tk import *
def badge_round(path, d):
    ph = Image.open(path).convert("RGB").resize((d, d), Image.LANCZOS)
    ph = ImageEnhance.Brightness(ph).enhance(1.05); m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse([0, 0, d - 1, d - 1], fill=255)
    o = Image.new("RGBA", (d, d), (0, 0, 0, 0)); o.paste(ph, (0, 0), m); return o
def build(v):
    im = base(); glow(im, 1380, 470, 560, RED, 120)
    dell = fit_h(key_flood(Image.open(A + "people/michael-dell.png")), 600)
    gates = fit_h(key_flood(Image.open(A + "people/bill-gates.png")), 640)
    jobs = fit_h(key_flood(Image.open(A + "people/steve-jobs.png")), 1000)
    put(im, dell, 880, H - dell.height + 40, rim=(120, 140, 170))
    pass  # Gates omitted: hidden behind Jobs
    put(im, jobs, 1050, H - jobs.height + 60, rim=RED)
    tag(im, W - 290, 24)
    logo = badge_round(A + "apple_logo_crop.jpg", 300); put(im, logo, 70, 40, rim=IVORY, rimw=11)
    imac = Image.open(A + "imac34_cut.png").convert("RGBA"); imac = fit_h(imac.crop(imac.getbbox()), 230); put(im, imac, 70, H - imac.height - 26)
    if v == "A":
        text(im, "ALMOST", 170, IVORY, 70, 560, stroke=4); text(im, "FINISHED", 190, RED, 64, 760, stroke=5)
    else:
        text(im, "90 DAYS", 190, RED, 70, 570, stroke=5); text(im, "FROM BROKE", 140, IVORY, 74, 750, stroke=4)
    pill(im, "APPLE · 1997", 410, 290, bg=RED, fg=IVORY, size=36)
    save(im, f"/home/claude/es/ep01/thumbs/thumb_V2_{v}.jpg")
for v in "AB": build(v)
