"""Thumbnail v3.1 (owner 23 Nov 2026): text column LEFT, every block centred on one axis and the same width;
leader RIGHT; logo badge + products under the text."""
import sys; sys.path.insert(0, "/home/claude/es/thumbkit")
from journey import *
GOLDB = (212, 175, 55); NAV = (11, 19, 43); IVO = (244, 241, 234)
def block(im, s, cx, y, bw, size, bg, fg, k="disp", h=None, stroke=0, sc=(0, 0, 0)):
    f = font(k, size); d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), s, font=f, stroke_width=stroke); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    h = h or th + 64; box = [cx - bw // 2, y, cx + bw // 2, y + h]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([box[0] + 10, box[1] + 14, box[2] + 10, box[3] + 14], 20, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d.rounded_rectangle(box, 20, fill=bg + (255,), outline=GOLDB, width=6)
    # exact optical centre: subtract the glyph bbox offsets
    d.text((cx - tw / 2 - bb[0], y + (h - th) / 2 - bb[1]), s, font=f, fill=fg, stroke_width=stroke, stroke_fill=sc)
    return y + h
def make(bg, bgcrop, person, name, namebg, namefg, years, sub, logo, logocrop, products, out, namestroke=0, namesc=(0, 0, 0)):
    im = cover(bg, crop=bgcrop)
    # soft dark veil behind the text column so it always reads
    v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).rectangle([0, 0, 1080, H], fill=120); v = v.filter(ImageFilter.GaussianBlur(120))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, H), (3, 12, 30, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), v))
    p = fit_h(key_flood(Image.open(A + "people/" + person)), 1030)
    put(im, p, W - p.width + 60, H - p.height + 40, rim=GOLDB)
    tag(im, W - 290, H - 62)
    cx, bw = 560, 960
    y = block(im, name, cx, 60, bw, 132, namebg, namefg, stroke=namestroke, sc=namesc) + 28
    y = block(im, years, cx, y, bw, 160, IVO, NAV) + 28
    y = block(im, sub, cx, y, bw, 62, NAV, GOLDB, k="sansb", h=110) + 30
    # bottom row: logo badge + products, centred on the same axis
    objs = []
    for f, hh in products:
        o = Image.open(A + f).convert("RGBA")
        if f.endswith(".jpg"): o = key_white(o)
        elif f == "iphone_cut.png": o = key_flood(o)
        o = o.crop(o.getbbox()); objs.append(fit_h(o, hh))
    r = 115; gap = 34; total = 2 * r + sum(o.width for o in objs) + gap * len(objs)
    x = cx - total // 2; base_y = H - 36
    badge(im, logo, logocrop, x + r, base_y - r - 10, r); x += 2 * r + gap
    for o in objs: put(im, o, x, base_y - o.height); x += o.width + gap
    # brand tag top-right
    f = font("sansb", 30); s = "EMPIRE STORIES"; d = ImageDraw.Draw(im); w = d.textlength(s, font=f)
    d.rounded_rectangle([W - w - 70, 28, W - 30, 84], 8, fill=(11, 19, 43, 235)); d.text((W - 50 - w, 56), s, font=f, fill=GOLDB, anchor="lm")
    save(im, out)
