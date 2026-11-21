"""MONEY ATLAS brand generator (v2: jade / gold / ivory). Writes icon, watermark and banner (content inside YouTube's 1546x423 safe area)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, numpy as np, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
BG1 = (5, 24, 28); BG2 = (9, 52, 56); JADE = (30, 170, 140); JADE2 = (18, 110, 96); GOLD = (244, 184, 72); IVORY = (248, 243, 230)
FM = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"; AB = "/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"

def grad(w, h, c1, c2, cx, cy, rad):
    yy, xx = np.mgrid[0:h, 0:w]; d = np.clip(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad, 0, 1)[..., None]
    return Image.fromarray((np.array(c2) * (1 - d) + np.array(c1) * d).astype(np.uint8))

def emblem(S):
    k = 4; s = S * k; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); c = s / 2; R = s * 0.47
    g = grad(s, s, BG1, BG2, c, c * 0.8, R); m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).ellipse([c - R, c - R, c + R, c + R], fill=255); im.paste(g, (0, 0), m)
    d = ImageDraw.Draw(im); d.ellipse([c - R, c - R, c + R, c + R], outline=GOLD + (255,), width=int(s * 0.028))
    r = R * 0.76; w = max(2, int(s * 0.011))
    for lat in range(-75, 90, 15):
        for lon in range(-180, 180, 10):
            la, lo = math.radians(lat), math.radians(lon); x = math.cos(la) * math.sin(lo); z = math.cos(la) * math.cos(lo); y = math.sin(la)
            if z < 0: continue
            px, py = c + x * r, c - y * r; rr = s * 0.006 * (0.5 + 0.5 * z); d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=JADE + (int(120 + 135 * z),))
    d.ellipse([c - r, c - r, c + r, c + r], outline=JADE + (200,), width=w)
    pts = [(c - r * 0.9, c + r * 0.42), (c - r * 0.42, c + r * 0.08), (c - r * 0.02, c + r * 0.24), (c + r * 0.62, c - r * 0.48)]
    gl = Image.new("RGBA", (s, s), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(pts, fill=GOLD + (160,), width=int(s * 0.07), joint="curve"); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(s * 0.02)))
    d = ImageDraw.Draw(im); d.line(pts, fill=GOLD + (255,), width=int(s * 0.034), joint="curve")
    tx, ty = pts[-1]; a = math.atan2(ty - pts[-2][1], tx - pts[-2][0]); L = s * 0.1
    d.polygon([(tx + math.cos(a) * L * 0.7, ty + math.sin(a) * L * 0.7), (tx + math.cos(a + 2.45) * L, ty + math.sin(a + 2.45) * L), (tx + math.cos(a - 2.45) * L, ty + math.sin(a - 2.45) * L)], fill=GOLD + (255,))
    return im.resize((S, S), Image.LANCZOS)

if __name__ == "__main__":
    ic = grad(800, 800, BG1, BG2, 400, 300, 600).convert("RGB"); e = emblem(720); ic.paste(e, (40, 40), e); ic.save("money_atlas_icon.png")
    emblem(300).save("money_atlas_watermark.png"); emblem(150).save("money_atlas_watermark150.png")
    W, H = 2560, 1440; b = grad(W, H, BG1, BG2, 1280, 640, 1300).convert("RGBA"); d = ImageDraw.Draw(b)
    for y in range(40, H, 46):
        for x in range(40, W, 46):
            v = 0.5 + 0.5 * math.sin(x * 0.004) * math.cos(y * 0.006)
            if v > 0.55: d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=JADE2 + (int(70 * v),))
    # safe area: x 507-2053, y 508-931  -> lay out emblem + text centred inside it
    f1 = ImageFont.truetype(AB, 122); f2 = ImageFont.truetype(FM, 38)
    tw = d.textlength("MONEY ATLAS", font=f1); ES = 250; gap = 44; total = ES + gap + tw; x0 = int(1280 - total / 2); yc = 720
    e = emblem(ES); b.alpha_composite(e, (x0, yc - ES // 2))
    tx = x0 + ES + gap; d = ImageDraw.Draw(b)
    d.text((tx, yc - 112), "MONEY", font=f1, fill=IVORY); d.text((tx + d.textlength("MONEY ", font=f1), yc - 112), "ATLAS", font=f1, fill=GOLD)
    d.line([(tx + 4, yc + 50), (tx + tw, yc + 50)], fill=JADE + (255,), width=4)
    d.text((tx + 4, yc + 68), "WHY NATIONS GET RICH, POOR OR STUCK", font=f2, fill=(200, 228, 220))
    b = b.convert("RGB"); b.save("money_atlas_banner.png"); b.save("money_atlas_banner.jpg", quality=92)
    print("safe-area x:", x0, int(tx + tw), "(must be within 507..2053)")
