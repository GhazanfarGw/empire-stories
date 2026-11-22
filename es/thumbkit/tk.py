"""Thumbnail kit v2 (owner rule 22 Nov 2026): company icon (real photo of its sign/logo), founder AI illustrations,
small story objects, one crunchy headline in the middle. 1920x1080 -> 1280x720."""
import sys, math, numpy as np
sys.path.insert(0, "/home/claude/es/tl3"); sys.path.insert(0, "/home/claude/es")
_a = sys.argv; sys.argv = ["x", "q"]
from tl3 import font, NAVY_US, RED_US, IVORY
sys.argv = _a
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W, H = 1920, 1080; NAVY = (8, 30, 64); RED = RED_US; GOLD = (255, 199, 44)
A = "/home/claude/es/assets/"
def base():
    im = Image.new("RGBA", (W, H), NAVY + (255,))
    g = Image.linear_gradient("L").resize((W, H)); im = Image.composite(Image.new("RGBA", (W, H), (3, 12, 30, 255)), im, g)
    return im
def glow(im, cx, cy, r, col, a=130):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.45)))
def key_flat(src, thr=18):
    """Illustration on flat grey -> transparent."""
    src = src.convert("RGBA"); bg = np.array(src.getpixel((8, 8))[:3])
    a = np.asarray(src).astype(np.int16); d = np.abs(a[..., :3] - bg).sum(-1)
    al = np.clip((d - thr) * 10, 0, 255).astype(np.uint8)
    src.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(1.2))); return src
def key_white(src, thr=28):
    src = src.convert("RGBA"); a = np.asarray(src).astype(np.int16)
    d = (765 - a[..., :3].sum(-1)); al = np.clip((d - thr) * 6, 0, 255).astype(np.uint8)
    src.putalpha(Image.fromarray(al).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))); return src
def key_sky(src):
    src = src.convert("RGBA"); a = np.asarray(src).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sky = (b - np.maximum(r, g)) ; al = np.clip((40 - sky) * 8, 0, 255).astype(np.uint8)
    src.putalpha(Image.fromarray(al).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))); return src
def fit_h(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
def put(base_, obj, x, y, rim=None, shadow=True, rimw=13):
    """x,y = top-left. Optional coloured rim light + soft drop shadow."""
    al = obj.getchannel("A")
    if shadow:
        sh = Image.new("RGBA", obj.size, (0, 0, 0, 0)); sh.putalpha(al.point(lambda v: int(v * 0.6)))
        base_.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (x + 14, y + 18))
    if rim:
        r = Image.new("RGBA", obj.size, rim + (0,)); r.putalpha(al.filter(ImageFilter.MaxFilter(rimw)).point(lambda v: int(v * 0.95)))
        base_.alpha_composite(r.filter(ImageFilter.GaussianBlur(3)), (x, y))
    base_.alpha_composite(obj, (x, y))
def tag(im, x, y, s="AI ILLUSTRATION"):
    f = font("sansb", 22); w = ImageDraw.Draw(im).textlength(s, font=f)
    ImageDraw.Draw(im).rounded_rectangle([x, y, x + w + 28, y + 38], 6, fill=(3, 12, 30, 225))
    ImageDraw.Draw(im).text((x + 14, y + 19), s, font=f, fill=IVORY, anchor="lm")
def text(im, s, size, col, x, y, k="disp", anchor="ls", stroke=0):
    f = font(k, size); l = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(l).text((x + 8, y + 12), s, font=f, fill=(0, 0, 0, 190), anchor=anchor); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).text((x, y), s, font=f, fill=col, anchor=anchor, stroke_width=stroke, stroke_fill=(3, 12, 30))
def pill(im, s, x, y, bg=IVORY, fg=NAVY, size=40):
    f = font("sansb", size); w = ImageDraw.Draw(im).textlength(s, font=f)
    ImageDraw.Draw(im).rounded_rectangle([x, y, x + w + 48, y + size + 30], 10, fill=bg + (255,))
    ImageDraw.Draw(im).text((x + 24, y + (size + 30) / 2), s, font=f, fill=fg, anchor="lm")
def save(im, out):
    im.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=93); print(out)
def key_flood(src, tol=34):
    """Remove the illustration's grey background: low-saturation light pixels connected to the border."""
    from scipy import ndimage
    src = src.convert("RGBA"); a = np.asarray(src).astype(np.int16)[..., :3]
    mx, mn = a.max(-1), a.min(-1); lum = a.mean(-1)
    cand = (mx - mn < 22) & (lum > 160) & (lum < 236)
    lab, n = ndimage.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(border))
    al = np.where(bgm, 0, 255).astype(np.uint8)
    al = Image.fromarray(al).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.4))
    src.putalpha(al); return src
