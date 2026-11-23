"""Thumbnail v4 (owner 23 Nov 2026): fresh HD illustrated background with deep blue sky, clean natural portrait RIGHT,
LEFT column in this order: company LOGO -> NAME -> YEARS -> THE COMPLETE STORY, all on one centre line. No AI tag."""
import sys; sys.path.insert(0, "/home/claude/es/thumbkit")
from journey import *
from journey2 import block, GOLDB, NAV, IVO
def key_border_white(src, lo=175, sat=45):
    from scipy import ndimage
    src = src.convert("RGBA"); a = np.asarray(src).astype(np.int16)
    rgb = a[..., :3]; al0 = a[..., 3]
    cand = (((rgb.max(-1) - rgb.min(-1)) < sat) & (rgb.mean(-1) > lo)) | (al0 < 20)
    lab, n = ndimage.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = np.isin(lab, list(border))
    al = np.where(m, 0, al0).astype(np.uint8)
    al = Image.fromarray(al).point(lambda v: 0 if v < 90 else v).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    src.putalpha(al); return src
def make(bg, flip, person, name, namebg, namefg, years, sub, logo, logocrop, products, out, namestroke=0, namesc=(0, 0, 0)):
    src = Image.open(bg).convert("RGB")
    if flip: src = ImageOps.mirror(src)
    src = ImageOps.fit(src, (W, H), Image.LANCZOS)
    src = ImageEnhance.Color(src).enhance(1.08); src = ImageEnhance.Contrast(src).enhance(1.04)
    im = src.convert("RGBA")
    p = key_flood(Image.open(A + "people/" + person)); p = p.crop(p.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()); p = fit_h(p, 990)
    put(im, p, W - p.width - 40, H - p.height, rim=(255, 255, 255), rimw=9)
    cx, bw = 560, 960
    r = 130; top = 70; badge(im, logo, logocrop, cx, top + r, r)
    y = top + 2 * r + 40
    y = block(im, name, cx, y, bw, 140, namebg, namefg, stroke=namestroke, sc=namesc) + 28
    y = block(im, years, cx, y, bw, 150, IVO, NAV, h=200) + 28
    y = block(im, sub, cx, y, bw, 62, NAV, GOLDB, k="sansb", h=108)
    objs = []
    for f, hh in []:
        o = Image.open(A + f).convert("RGBA")
        o = key_border_white(o)
        o = o.crop(o.getbbox()); objs.append(fit_h(o, hh))
    gap = 40; total = sum(o.width for o in objs) + gap * (len(objs) - 1); x = cx - total // 2
    for o in objs: put(im, o, x, H - 24 - o.height); x += o.width + gap
    f = font("sansb", 30); s = "EMPIRE STORIES"; d = ImageDraw.Draw(im); w = d.textlength(s, font=f)
    d.rounded_rectangle([W - w - 70, 28, W - 30, 84], 8, fill=(11, 19, 43, 235)); d.text((W - 50 - w, 56), s, font=f, fill=GOLDB, anchor="lm")
    save(im, out)
