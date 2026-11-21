"""EMPIRE STORIES paper kit — aged-page background + torn-paper photo edges."""
import numpy as np, functools
from PIL import Image, ImageDraw, ImageFilter
W, H = 1920, 1080
A = "/home/claude/es/assets/"
PAPER_EDGE = (250, 246, 236)

def _noise(rng, w, h, cell, blur=0):
    n = Image.fromarray((rng.random((max(2, h // cell), max(2, w // cell))) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    if blur: n = n.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(n, np.float32) / 255 - 0.5

def make_aged_paper(seed=11):
    """old book page: warm parchment, darker foxed edges, soft stains, fibres and specks"""
    rng = np.random.default_rng(seed); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([238, 226, 200], np.float32); edge = np.array([196, 172, 128], np.float32)
    d = np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0, 1.6)
    t = np.clip(d - 0.35, 0, 1) ** 1.6
    img = base[None, None] * (1 - t[..., None]) + edge[None, None] * t[..., None]
    low = _noise(rng, W, H, 40, 60); mid = _noise(rng, W, H, 10, 6)
    img *= (1 + low[..., None] * 0.10 + mid[..., None] * 0.035)
    fib = _noise(rng, W, H // 1, 3) ; fibh = np.asarray(Image.fromarray(((fib + 0.5) * 255).astype(np.uint8)).resize((W // 9, H), Image.BICUBIC).resize((W, H), Image.BICUBIC), np.float32) / 255 - 0.5
    img *= (1 + fibh[..., None] * 0.03)
    for _ in range(5):   # faint foxing / stains
        cx, cy, r = rng.random() * W, rng.random() * H, 60 + rng.random() * 220
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=255)
        m = np.asarray(m.filter(ImageFilter.GaussianBlur(r * 0.5)), np.float32) / 255
        ring = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
        img *= (1 - m[..., None] * 0.045 - ring[..., None] * 0.35 * np.array([0.6, 0.8, 1.2])[None, None])
    sp = rng.random((H, W)) > 0.9993; img[sp] *= 0.72
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")

def _torn_mask(mask, seed, amp=1.0):
    """roughen a binary mask's edge into a ripped-paper edge (coarse wobble + fine fibre teeth), only in a band at the edge"""
    w, h = mask.size; rng = np.random.default_rng(seed)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(9)), np.float32)
    band = np.clip(1 - np.abs(m - 128) / 128, 0, 1) ** 0.5
    nz = (_noise(rng, w, h, 26, 4) * 150 + _noise(rng, w, h, 7) * 110 + _noise(rng, w, h, 2) * 60) * amp
    g = m + nz * band
    out = Image.fromarray(((g > 128) * 255).astype(np.uint8))
    return out.filter(ImageFilter.MedianFilter(3))

def _assemble(content, paper_mask, photo_mask, seed):
    w, h = content.size; rng = np.random.default_rng(seed + 9)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (30, 22, 10, 0)); sh.putalpha(paper_mask.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.5)))
    out.alpha_composite(sh, (8, 14))
    # fibrous white tear-rim: slightly translucent, speckled
    fib = (rng.random((h, w)) * 60 + 195).astype(np.uint8)
    rim = Image.new("RGBA", (w, h), PAPER_EDGE + (0,)); rim.putalpha(Image.fromarray(np.minimum(np.asarray(paper_mask), fib)))
    out.alpha_composite(rim)
    ph = content.copy(); ph.putalpha(Image.fromarray(np.minimum(np.asarray(content.getchannel("A")), np.asarray(photo_mask))))
    out.alpha_composite(ph)
    # thin warm shading just inside the paper edge
    edge = paper_mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: int(min(255, v * 0.9)))
    e = Image.new("RGBA", (w, h), (160, 140, 110, 0)); e.putalpha(edge); out.alpha_composite(e)
    return out

@functools.lru_cache(None)
def torn_card(name, w, seed=None):
    """rectangular photo torn out of a page: ragged white rim around a ragged-edged photo"""
    seed = seed if seed is not None else (sum(map(ord, name)) % 97)
    im = Image.open(A + name).convert("RGBA"); s = w / im.width; im = im.resize((w, int(im.height * s)), Image.LANCZOS)
    pad = 60; rim = 20; Wc, Hc = im.width + 2 * (pad + rim), im.height + 2 * (pad + rim)
    content = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); content.paste(im, (pad + rim, pad + rim))
    pm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(pm).rectangle([pad, pad, Wc - pad, Hc - pad], fill=255)
    hm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(hm).rectangle([pad + rim, pad + rim, Wc - pad - rim, Hc - pad - rim], fill=255)
    return _assemble(content, _torn_mask(pm, seed, 1.0), _torn_mask(hm, seed + 1, 0.55), seed)

@functools.lru_cache(None)
def torn_cut(name, h, seed=None):
    """cut-out object glued on a torn scrap of paper"""
    seed = seed if seed is not None else (sum(map(ord, name)) % 97)
    im = Image.open(A + name).convert("RGBA"); s = h / im.height; im = im.resize((int(im.width * s), h), Image.LANCZOS)
    pad = 70; Wc, Hc = im.width + 2 * pad, im.height + 2 * pad
    content = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); content.alpha_composite(im, (pad, pad))
    a = content.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    grown = a
    for _ in range(3): grown = grown.filter(ImageFilter.MaxFilter(15))
    grown = grown.filter(ImageFilter.GaussianBlur(10)).point(lambda v: 255 if v > 90 else 0)
    hm = a.filter(ImageFilter.MaxFilter(3))
    return _assemble(content, _torn_mask(grown, seed, 1.0), hm, seed)

# ======================= v2: grey concrete page + banknote engraving + white torn sheets =======================
GREY = (214, 213, 209); SHEET = (244, 243, 240); NAVY_L = (10, 49, 97); RED_L = (179, 25, 66)

def _guilloche(d, cx, cy, R, amp, lobes, rings, col, k=2, w=1):
    th = np.linspace(0, 2 * np.pi, 2400)
    for j in range(rings):
        ph = j * 2 * np.pi / rings; rr = R + amp * np.sin(lobes * th + ph) + amp * 0.35 * np.sin((lobes * 3 + 1) * th - ph)
        pts = list(zip((cx + rr * np.cos(th)) * k, (cy + rr * np.sin(th)) * k)); d.line(pts + [pts[0]], fill=col, width=w * k)

def make_note_bg(seed=5):
    """light grey concrete paper + faint banknote engraving: guilloche rosettes, wave bands, halftone dot fields"""
    rng = np.random.default_rng(seed); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.array(GREY, np.float32)[None, None] * np.ones((H, W, 1), np.float32)
    img *= (1 + _noise(rng, W, H, 60, 50)[..., None] * 0.07 + _noise(rng, W, H, 14, 5)[..., None] * 0.05 + _noise(rng, W, H, 3)[..., None] * 0.035)
    v = 1 - 0.10 * (((xx - W / 2) / (W / 1.2)) ** 2 + ((yy - H / 2) / (H / 1.0)) ** 2); img *= v[..., None]
    sp = rng.random((H, W)); img[sp > 0.9985] *= 0.82; img[sp < 0.0008] *= 1.06
    base = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")
    k = 2; eng = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0)); d = ImageDraw.Draw(eng)
    c = (40, 52, 70, 34)
    _guilloche(d, 1640, 860, 300, 34, 18, 14, c); _guilloche(d, 1640, 860, 210, 22, 12, 10, c); _guilloche(d, 1640, 860, 120, 14, 9, 8, c)
    _guilloche(d, 230, 170, 220, 26, 15, 12, c); _guilloche(d, 230, 170, 140, 16, 10, 8, c)
    xs = np.linspace(-50, W + 50, 900)
    for j in range(16):   # engraved wave band along the bottom (like the border of a bill)
        y0 = 1000 + j * 3.2; ys = y0 + 9 * np.sin(xs / 38 + j * 0.45) + 4 * np.sin(xs / 11 - j * 0.3)
        d.line(list(zip(xs * k, ys * k)), fill=(40, 52, 70, 22), width=k)
    for j in range(10):
        y0 = 40 + j * 3.2; ys = y0 + 7 * np.sin(xs / 31 - j * 0.5)
        d.line(list(zip(xs * k, ys * k)), fill=(40, 52, 70, 16), width=k)
    eng = eng.resize((W, H), Image.LANCZOS)
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dots)
    field = _noise(rng, W, H, 220, 80) + 0.5
    for y in range(0, H, 12):
        for x in range((y // 12 % 2) * 6, W, 12):
            f = field[y, x]; edge_w = max(0.0, (abs(x - W / 2) / (W / 2)) ** 2)
            rr = 2.2 * f * edge_w
            if rr > 0.45: dd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(40, 52, 70, 30))
    base.alpha_composite(dots); base.alpha_composite(eng)
    return base

def _rip_mask(mask, seed, amp=1.0):
    """big irregular rips (like hand-torn paper): large chunks, a few medium bites, light fibre teeth"""
    w, h = mask.size; rng = np.random.default_rng(seed)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(14)), np.float32)
    band = np.clip(1 - np.abs(m - 128) / 128, 0, 1) ** 0.4
    nz = (_noise(rng, w, h, 90, 10) * 260 + _noise(rng, w, h, 22, 2) * 110 + _noise(rng, w, h, 3) * 40) * amp
    return Image.fromarray((((m + nz * band) > 128) * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))

def _sheet_tex(w, h, seed):
    rng = np.random.default_rng(seed); a = np.array(SHEET, np.float32)[None, None] * np.ones((h, w, 1), np.float32)
    a *= (1 + _noise(rng, w, h, 30, 10)[..., None] * 0.03 + _noise(rng, w, h, 3)[..., None] * 0.02)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")

def _sheet_assemble(content, sheet_mask, photo_mask, seed, line_col=NAVY_L, line_off=(-22, -20), rect=None):
    """white torn sheet: soft lifted shadow, paper texture, tear-thickness rim, inner shading, plus a thin brand hairline frame behind"""
    w, h = content.size; out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if line_col and rect:   # thin brand line frame, offset behind the sheet (keeps the theme)
        fr = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(fr).rectangle([rect[0] + line_off[0], rect[1] + line_off[1], rect[2] + line_off[0], rect[3] + line_off[1]], outline=line_col + (235,), width=3)
        out.alpha_composite(fr)
    for blur, off, a_ in ((26, (16, 22), 0.30), (6, (4, 6), 0.35)):
        sh = Image.new("RGBA", (w, h), (20, 20, 24, 0)); sh.putalpha(sheet_mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v, a_=a_: int(v * a_))); out.alpha_composite(sh, off)
    tex = _sheet_tex(w, h, seed); tex.putalpha(sheet_mask); out.alpha_composite(tex)
    # tear thickness: bright fibrous edge + a grey crease just inside it
    edge = np.asarray(sheet_mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2)), np.float32)
    inner = np.asarray(sheet_mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(5)), np.float32)
    crease = np.clip((np.asarray(sheet_mask, np.float32) - inner) / 255, 0, 1) * 0.22
    sh2 = Image.new("RGBA", (w, h), (90, 92, 98, 0)); sh2.putalpha(Image.fromarray((crease * 255).astype(np.uint8))); out.alpha_composite(sh2)
    hi = Image.new("RGBA", (w, h), (255, 255, 255, 0)); hi.putalpha(Image.fromarray(np.clip(edge * 0.8, 0, 255).astype(np.uint8))); out.alpha_composite(hi)
    if photo_mask is not None:
        ph = content.copy(); ph.putalpha(Image.fromarray(np.minimum(np.asarray(content.getchannel("A")), np.asarray(photo_mask)))); out.alpha_composite(ph)
    else: out.alpha_composite(content)
    return out

@functools.lru_cache(None)
def sheet_card(name, w, seed=None):
    """photo printed on a white page whose edges are torn"""
    seed = seed if seed is not None else (sum(map(ord, name)) % 97)
    im = Image.open(A + name).convert("RGBA"); s = w / im.width; im = im.resize((w, int(im.height * s)), Image.LANCZOS)
    pad, rim = 90, 26; Wc, Hc = im.width + 2 * (pad + rim), im.height + 2 * (pad + rim)
    content = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); content.paste(im, (pad + rim, pad + rim))
    pm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(pm).rectangle([pad, pad, Wc - pad, Hc - pad], fill=255)
    hm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(hm).rectangle([pad + rim, pad + rim, Wc - pad - rim, Hc - pad - rim], fill=255)
    return _sheet_assemble(content, _rip_mask(pm, seed, 1.0), _torn_mask(hm, seed + 1, 0.35), seed, NAVY_L, (-48, -42), (pad + 30, pad + 30, Wc - pad - 30, Hc - pad - 30))

@functools.lru_cache(None)
def sheet_cut(name, h, seed=None, line_col=RED_L):
    """cut-out object resting on a torn white sheet (like the reference collage)"""
    seed = seed if seed is not None else (sum(map(ord, name)) % 97)
    im = Image.open(A + name).convert("RGBA"); s = h / im.height; im = im.resize((int(im.width * s), h), Image.LANCZOS)
    side = int(max(im.width, im.height) * 1.32); pad = 100; Wc = Hc = side + 2 * pad
    content = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    osh = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); a = im.getchannel("A"); oshl = Image.new("RGBA", im.size, (20, 20, 24, 0)); oshl.putalpha(a.point(lambda v: int(v * 0.35)))
    ox, oy = (Wc - im.width) // 2, (Hc - im.height) // 2
    osh.alpha_composite(oshl, (ox + 10, oy + 16)); content.alpha_composite(osh.filter(ImageFilter.GaussianBlur(12))); content.alpha_composite(im, (ox, oy))
    pm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(pm).rectangle([pad, pad + 20, Wc - pad, Hc - pad - 10], fill=255)
    return _sheet_assemble(content, _rip_mask(pm, seed, 1.0), None, seed, line_col, (46, 40), (pad + 30, pad + 50, Wc - pad - 30, Hc - pad - 40))

# ======================= v3: plain grey page, thin shape-hugging torn edges =======================
def make_grey_bg(seed=5):
    """light grey concrete-paper page, no watermark"""
    rng = np.random.default_rng(seed); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.array(GREY, np.float32)[None, None] * np.ones((H, W, 1), np.float32)
    img *= (1 + _noise(rng, W, H, 60, 50)[..., None] * 0.07 + _noise(rng, W, H, 14, 5)[..., None] * 0.05 + _noise(rng, W, H, 3)[..., None] * 0.035)
    v = 1 - 0.10 * (((xx - W / 2) / (W / 1.2)) ** 2 + ((yy - H / 2) / (H / 1.0)) ** 2); img *= v[..., None]
    sp = rng.random((H, W)); img[sp > 0.9985] *= 0.82; img[sp < 0.0008] *= 1.06
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")

def _thin_torn(mask, seed, amp):
    w, h = mask.size; rng = np.random.default_rng(seed)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(4)), np.float32)
    band = np.clip(1 - np.abs(m - 128) / 128, 0, 1) ** 0.6
    nz = (_noise(rng, w, h, 30, 3) * 120 + _noise(rng, w, h, 6) * 90 + _noise(rng, w, h, 2) * 60) * amp
    return Image.fromarray((((m + nz * band) > 128) * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3))

def _thin_assemble(content, rim_mask, photo_mask, seed):
    w, h = content.size; rng = np.random.default_rng(seed + 3); out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (20, 20, 24, 0)); sh.putalpha(rim_mask.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.32))); out.alpha_composite(sh, (4, 7))
    fib = (rng.random((h, w)) * 50 + 205).astype(np.uint8)
    rim = Image.new("RGBA", (w, h), (247, 246, 242, 0)); rim.putalpha(Image.fromarray(np.minimum(np.asarray(rim_mask), fib))); out.alpha_composite(rim)
    ph = content.copy(); ph.putalpha(Image.fromarray(np.minimum(np.asarray(content.getchannel("A")), np.asarray(photo_mask)))); out.alpha_composite(ph)
    return out

@functools.lru_cache(None)
def edge_cut(name, h, seed=None):
    """cut-out object with a thin torn-paper rim that follows its own outline"""
    seed = seed if seed is not None else (sum(map(ord, name)) % 97)
    im = Image.open(A + name).convert("RGBA"); s = h / im.height; im = im.resize((int(im.width * s), h), Image.LANCZOS)
    pad = 40; content = Image.new("RGBA", (im.width + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); content.alpha_composite(im, (pad, pad))
    a = content.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    grown = a.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.MaxFilter(5))
    return _thin_assemble(content, _thin_torn(grown, seed, 0.9), a.filter(ImageFilter.MaxFilter(3)), seed)

@functools.lru_cache(None)
def edge_card(name, w, seed=None):
    """rectangular photo whose own edges are torn, with a thin paper rim"""
    seed = seed if seed is not None else (sum(map(ord, name)) % 97)
    im = Image.open(A + name).convert("RGBA"); s = w / im.width; im = im.resize((w, int(im.height * s)), Image.LANCZOS)
    pad, rim = 40, 9; Wc, Hc = im.width + 2 * pad, im.height + 2 * pad
    content = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); content.paste(im, (pad, pad))
    rm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(rm).rectangle([pad - rim, pad - rim, Wc - pad + rim, Hc - pad + rim], fill=255)
    pm = Image.new("L", (Wc, Hc), 0); ImageDraw.Draw(pm).rectangle([pad + 2, pad + 2, Wc - pad - 2, Hc - pad - 2], fill=255)
    return _thin_assemble(content, _thin_torn(rm, seed, 1.0), _thin_torn(pm, seed + 1, 0.6), seed)
