"""Thumbnail standard v3 'JOURNEY' (owner, 23 Nov 2026): real company building as bright background,
founder (AI illustration) large on the left, company name + logo top right, big YEAR – YEAR span,
'THE COMPLETE STORY' line, products bottom right."""
import sys; sys.path.insert(0, "/home/claude/es/thumbkit")
from tk import *
from PIL import ImageOps
def cover(path, crop=None, sat=1.18, bri=1.04):
    im = Image.open(path).convert("RGB")
    if crop: im = im.crop(crop)
    im = ImageOps.fit(im, (W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(sat); im = ImageEnhance.Brightness(im).enhance(bri)
    im = im.convert("RGBA")
    g = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(max(0, v - 150) * 1.6))  # dark foot
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, H), (3, 12, 30, 255)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), g))
    return im
def slab(im, s, cx, y, size, bg, fg, k="disp", padx=46, pady=22, stroke=0, sc=(0, 0, 0)):
    f = font(k, size); d = ImageDraw.Draw(im); bb = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    w, h = bb[2] - bb[0], bb[3] - bb[1]; x0 = cx - w / 2 - padx; box = [x0, y, cx + w / 2 + padx, y + h + 2 * pady]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([box[0] + 10, box[1] + 14, box[2] + 10, box[3] + 14], 18, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d.rounded_rectangle(box, 18, fill=bg + (255,), outline=(212, 175, 55), width=6)
    d.text((cx, y + pady - bb[1]), s, font=f, fill=fg, anchor="mt", stroke_width=stroke, stroke_fill=sc)
    return box
def brand(im):
    f = font("sansb", 30); s = "EMPIRE STORIES"; d = ImageDraw.Draw(im); w = d.textlength(s, font=f)
    d.rounded_rectangle([30, 28, 30 + w + 40, 84], 8, fill=(11, 19, 43, 235)); d.text((50, 56), s, font=f, fill=(212, 175, 55), anchor="lm")
def badge(im, path, crop, cx, cy, r):
    src = Image.open(path).convert("RGB")
    if crop: src = src.crop(crop)
    src = ImageOps.fit(src, (2 * r, 2 * r), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255); src.putalpha(m)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - r + 10, cy - r + 14, cx + r + 10, cy + r + 14], fill=(0, 0, 0, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(im).ellipse([cx - r - 9, cy - r - 9, cx + r + 9, cy + r + 9], fill=(212, 175, 55))
    im.alpha_composite(src, (cx - r, cy - r))
