"""EMPIRE STORIES map kit — TopoJSON (us-atlas / world-atlas, ISC) decoder + Albers projection + brand-styled animated map frames."""
import json, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os
GEO = next((p for p in [os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "geo"), "/mnt/user-data/uploads/e/Empire Stories/_tools/geo"] if os.path.isdir(p)), "")

def topo(path):
    tj = json.load(open(path)); sc, tr = tj["transform"]["scale"], tj["transform"]["translate"]; arcs = []
    for a in tj["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a: x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)
    def ring(ix):
        out = []
        for i in ix:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(p if not out else p[1:])
        return out
    def geom(g):
        if g["type"] == "Polygon": return [[ring(r) for r in g["arcs"]]]
        if g["type"] == "MultiPolygon": return [[ring(r) for r in poly] for poly in g["arcs"]]
        return []
    return tj, geom

# Albers equal-area conic, USA (29.5N / 45.5N, origin 23N 96W) — output in km
P1, P2, LAT0, LON0 = map(math.radians, (29.5, 45.5, 23.0, -96.0))
_n = (math.sin(P1) + math.sin(P2)) / 2; _C = math.cos(P1) ** 2 + 2 * _n * math.sin(P1); _r0 = math.sqrt(_C - 2 * _n * math.sin(LAT0)) / _n
def albers(lon, lat):
    la, lo = math.radians(lat), math.radians(lon); rho = math.sqrt(max(_C - 2 * _n * math.sin(la), 0)) / _n; th = _n * (lo - LON0)
    return 6371 * rho * math.sin(th), 6371 * (_r0 - rho * math.cos(th))   # x east, y north (km)

SKIP = {"02", "15", "60", "66", "69", "72", "78"}
@functools.lru_cache(None)
def us_states():
    tj, geom = topo(f"{GEO}/states-10m.json"); out = []
    for g in tj["objects"]["states"]["geometries"]:
        if g.get("id") in SKIP: continue
        for poly in geom(g):
            out.append([np.array([albers(*p) for p in ring]) for ring in poly])
    return out

def view_xy(pk, cx, cy, kpp, W, H):
    """km -> px. (cx,cy) view centre in km, kpp = km per pixel"""
    return np.stack([W / 2 + (pk[:, 0] - cx) / kpp, H / 2 - (pk[:, 1] - cy) / kpp], 1)

def us_map(cx, cy, kpp, W=1920, H=1080, ss=2, land=(255, 255, 255), border=(196, 188, 170), coast=(11, 19, 43), sea=None, hi=()):
    """render lower-48 at a view; returns RGBA (transparent sea unless sea colour). hi: set of state polygons idx to tint"""
    Wb, Hb = W * ss, H * ss; im = Image.new("RGBA", (Wb, Hb), (0, 0, 0, 0) if sea is None else sea + (255,)); d = ImageDraw.Draw(im)
    polys = us_states(); sh = Image.new("L", (Wb, Hb), 0); ds = ImageDraw.Draw(sh)
    pp = []
    for poly in polys:
        rings = [view_xy(r, cx, cy, kpp / ss, Wb, Hb) for r in poly]
        if all((r[:, 0].max() < 0) or (r[:, 0].min() > Wb) or (r[:, 1].max() < 0) or (r[:, 1].min() > Hb) for r in rings): continue
        pp.append(rings); ds.polygon([tuple(p) for p in rings[0]], fill=255)
    shadow = sh.filter(ImageFilter.GaussianBlur(14 * ss)); sl = Image.new("RGBA", (Wb, Hb), (11, 19, 43, 0)); sl.putalpha(shadow.point(lambda v: int(v * 0.22)))
    im.alpha_composite(sl, (int(6 * ss), int(10 * ss)))
    for rings in pp: d.polygon([tuple(p) for p in rings[0]], fill=land + (255,))
    for rings in pp: d.line([tuple(p) for p in rings[0]] + [tuple(rings[0][0])], fill=border + (255,), width=max(1, int(1.3 * ss)))
    # crisp outer coastline: draw the land mask edge
    edge = sh.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(3))
    cl_ = Image.new("RGBA", (Wb, Hb), coast + (0,)); cl_.putalpha(edge.point(lambda v: int(v * 0.9))); im.alpha_composite(cl_)
    return im.resize((W, H), Image.LANCZOS)
