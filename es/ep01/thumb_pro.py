"""Premium Ep01 thumbnail: dark navy, big founder illustration, 2 huge words, crash-and-recovery line."""
import os, sys
os.environ.setdefault("EP_META", "/home/claude/es/ep01/voice/meta.json"); sys.argv = ["x", "q"]
sys.path.insert(0, "/home/claude/es/ep01")
import ep01 as X
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from tl3 import font, NAVY_US, RED_US, IVORY
W, H = 1920, 1080; NAVY = (8, 30, 64); RED = RED_US
def glow(size, col, a, blur):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([size * .15, size * .15, size * .85, size * .85], fill=col + (a,)); return g.filter(ImageFilter.GaussianBlur(blur))
def text(im, s, size, col, x, y, k="disp", anchor="ls", sh=True):
    f = font(k, size)
    if sh:
        l = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((x + 8, y + 12), s, font=f, fill=(0, 0, 0, 160), anchor=anchor); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).text((x, y), s, font=f, fill=col, anchor=anchor)

def build(variant):
    im = Image.new("RGBA", (W, H), NAVY + (255,))
    # vertical gradient + vignette + faint paper grain
    g = Image.linear_gradient("L").resize((W, H)); im = Image.composite(Image.new("RGBA", (W, H), (4, 16, 38, 255)), im, g)
    grain = X.V.bg().convert("L").resize((W, H)); grain = ImageEnhance.Contrast(grain).enhance(1.6)
    im = Image.blend(im, Image.merge("RGBA", [grain, grain, grain, Image.new("L", (W, H), 255)]), 0.06)
    # red glow behind the founder
    im.alpha_composite(glow(1300, (179, 25, 66), 120, 160), (W - 1180, -60))
    # founder illustration, cut to a circle-free bust with soft bottom fade
    src = Image.open("/home/claude/es/assets/people/steve-jobs.png").convert("RGBA")
    hh = 1080; src = src.resize((int(src.width * hh / src.height), hh), Image.LANCZOS)
    bg = src.getpixel((8, 8))[:3]                       # flat illustration background -> transparent
    import numpy as np
    a = np.asarray(src).astype(np.int16); d = np.abs(a[..., :3] - np.array(bg)).sum(-1)
    alpha = np.clip((d - 18) * 10, 0, 255).astype(np.uint8); src.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.2)))
    rim = Image.new("RGBA", src.size, RED + (0,)); rim.putalpha(src.getchannel("A").filter(ImageFilter.MaxFilter(15)).point(lambda v: int(v * 0.9)))
    x0 = W - src.width + 60; im.alpha_composite(rim.filter(ImageFilter.GaussianBlur(4)), (x0, 10)); im.alpha_composite(src, (x0, 10))
    ImageDraw.Draw(im).rounded_rectangle([x0 + 70, 40, x0 + 330, 82], 6, fill=(4, 16, 38, 220))
    ImageDraw.Draw(im).text((x0 + 200, 61), "AI ILLUSTRATION", font=font("sansb", 24), fill=IVORY, anchor="mm")
    # crash -> recovery line (bottom-left)
    pts = [(80, 760), (260, 790), (400, 900), (520, 990), (640, 900), (780, 820), (930, 640)]
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(l)
    dl.line(pts[:4], fill=RED + (255,), width=16, joint="curve"); dl.line(pts[3:], fill=(240, 240, 235, 255), width=16, joint="curve")
    p, q = pts[-2], pts[-1]; import math; ang = math.atan2(q[1] - p[1], q[0] - p[0])
    dl.polygon([(q[0] + 30 * math.cos(ang), q[1] + 30 * math.sin(ang)), (q[0] - 34 * math.cos(ang - 0.6), q[1] - 34 * math.sin(ang - 0.6)), (q[0] - 34 * math.cos(ang + 0.6), q[1] - 34 * math.sin(ang + 0.6))], fill=(240, 240, 235, 255))
    lo = pts[3]; dl.ellipse([lo[0] - 22, lo[1] - 22, lo[0] + 22, lo[1] + 22], fill=RED + (255,), outline=IVORY + (255,), width=6)
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(0.6)))
    text(im, "−$1B", 64, (255, 120, 140), 560, 1040, anchor="ls")
    text(im, "+$3.5B", 64, IVORY, 960, 640, anchor="ls")
    # headline
    if variant == "A":
        text(im, "ALMOST", 230, IVORY, 70, 250); text(im, "FINISHED", 230, RED, 64, 480)
    else:
        text(im, "90 DAYS", 250, RED, 70, 260); text(im, "FROM BROKE", 160, IVORY, 74, 450)
    ImageDraw.Draw(im).rounded_rectangle([76, 520, 76 + 330, 584], 8, fill=IVORY + (255,))
    ImageDraw.Draw(im).text((76 + 165, 552), "APPLE · 1997", font=font("sansb", 40), fill=NAVY, anchor="mm")
    em = X.emblem_us(110); im.alpha_composite(em, (30, 30)) if False else None
    out = f"/home/claude/es/ep01/thumbs/thumb_PRO_{variant}.jpg"
    im.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=93); print(out, os.path.getsize(out) // 1024, "KB")
for v in ("A", "B"): build(v)
