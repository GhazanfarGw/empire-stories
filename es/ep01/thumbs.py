"""Three 1280x720 thumbnails for A/B testing — brand navy/red on grey paper, max 4 big words each."""
import os, sys
os.environ.setdefault("EP_META", "/home/claude/es/ep01/meta_test.json"); sys.argv = ["x", "q"]
sys.path.insert(0, "/home/claude/es/ep01")
import ep01 as X
from PIL import Image, ImageDraw, ImageFilter
from tl3 import font, txt, place, NAVY_US, RED_US, IVORY, INK, PK, V, person_card
W, H = 1920, 1080
OUT = "/home/claude/es/ep01/thumbs"; os.makedirs(OUT, exist_ok=True)
def paper(): return V.bg().copy()
def shadow_text(im, text, k, size, col, x, y, anchor="lm", stroke=0, sc=None):
    d = ImageDraw.Draw(im); f = font(k, size)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 6, y + 10), text, font=f, fill=(0, 0, 0, 90), anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d.text((x, y), text, font=f, fill=col, anchor=anchor, stroke_width=stroke, stroke_fill=sc)
def tag(im, text, x, y, size=44, bg=RED_US):
    lb = X.label_box(text, size, bg, IVORY); im.alpha_composite(lb, (int(x), int(y)))
def brand(im):
    d = ImageDraw.Draw(im); d.rectangle([0, H - 14, W, H], fill=RED_US)
    em = X.emblem_us(120); im.alpha_composite(em, (W - 150, 30))
def save(im, name):
    im.convert("RGB").resize((1280, 720), Image.LANCZOS).save(f"{OUT}/{name}.jpg", quality=92); print(name, os.path.getsize(f"{OUT}/{name}.jpg") // 1024, "KB")

# A — the turnaround in numbers
im = paper(); c = X.cutimg("imac34_cut.png", 640); im.alpha_composite(c, (W - c.width - 40, 170))
shadow_text(im, "ALMOST", "disp", 230, NAVY_US, 70, 260); shadow_text(im, "FINISHED", "disp", 230, RED_US, 70, 480)
tag(im, "1997", 80, 640, 64, NAVY_US)
shadow_text(im, "−$1B", "disp", 130, RED_US, 80, 900); shadow_text(im, "→ +$3.5B", "disp", 130, NAVY_US, 470, 900)
brand(im); save(im, "thumb_A_almost_finished")

# B — the 90 days hook with the (illustrated) founder
im = paper(); src = Image.open("/home/claude/es/assets/people/steve-jobs.png").convert("RGBA"); hh = 680; src = src.resize((int(src.width * hh / src.height), hh), Image.LANCZOS)
fr = Image.new("RGBA", (src.width + 20, src.height + 20), RED_US + (255,)); fr.alpha_composite(src, (10, 10)); dd = ImageDraw.Draw(fr)
dd.rounded_rectangle([24, 24, 300, 70], 6, fill=(10, 49, 97, 230)); dd.text((162, 47), "AI ILLUSTRATION", font=font("sansb", 26), fill=IVORY, anchor="mm")
im.alpha_composite(V.shadowed(fr, 18, (10, 16), 0.35), (W - fr.width - 70, 190))
shadow_text(im, "90 DAYS", "disp", 230, RED_US, 60, 330); shadow_text(im, "FROM BROKE", "disp", 150, NAVY_US, 70, 560)
tag(im, "HOW APPLE SURVIVED 1997", 86, 720, 52, NAVY_US)
brand(im); save(im, "thumb_B_90_days")

# C — Michael Dell's line
im = paper(); hq = X.photocard("hq_infinite_loop_crop.jpg", 880); im.alpha_composite(hq.rotate(-3, expand=True, resample=Image.BICUBIC), (1000, 200))
shadow_text(im, "“SHUT IT", "disp", 190, NAVY_US, 60, 300); shadow_text(im, "DOWN.”", "disp", 190, RED_US, 60, 500)
tag(im, "— MICHAEL DELL ON APPLE", 70, 690, 46, NAVY_US)
brand(im); save(im, "thumb_C_shut_it_down")
