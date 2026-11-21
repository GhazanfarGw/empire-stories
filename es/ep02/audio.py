"""EMPIRE STORIES sound v3 (locked 21 Nov 2026, owner feedback #2) — supersedes v2:
- bed: deep, slow, meditative felt piano (one soft note every ~2.7 s, low register, long reverb tail) over a warm low pad
- every pop/click is soft: 20-40 ms fade-in, smooth fade-out tail, low-passed, room reverb; nothing sharp
- no ticking counters, no timeline sound, no noise sounds (v2 rules still hold)
- effects bus ~12-15% of voice, bed lower still and ducked; voice always clear
(v2 notes:)
- NO sound when the timeline travels / branch lines draw (no odometer ticks, no zips, no whooshes)
- NO noise-based 'shh' sounds at all (no swish, swell, hiss): every effect is tonal and soft
- effects bus sits at ~20-25% of the voice; background bed very low, smooth, ducked under the voice
- bed: slow felt-piano arpeggios over a warm pad (documentary tone)
Writes three stems: voice.wav, sfx.wav, bed.wav -> mixed in run.sh."""
import sys, os, numpy as np, soundfile as sf, scipy.signal as ss
sys.argv = ["x", "q"]; D = os.environ.get("EP_DIR") or os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import importlib; T = importlib.import_module(os.environ.get("EP_MODULE", "ep02"))
SR = 48000; END = T.END; n = int(END * SR)
rng = np.random.default_rng(11)
def k(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): b, a = ss.butter(o, fc / (SR / 2)); return ss.lfilter(b, a, x)
def env(x, att, rel): e = np.minimum(1, x / max(att, 1e-3)); return e * np.clip((x[-1] - x) / max(rel, 1e-3), 0, 1)
class Bus:
    def __init__(s): s.m = np.zeros((n, 2))
    def add(s, at, sig, g=1.0, pan=0.0):
        i = int(at * SR)
        if i < 0 or i >= n: return
        x = sig[: n - i] * g; s.m[i:i + len(x), 0] += x * (1 - max(0, pan)); s.m[i:i + len(x), 1] += x * (1 + min(0, pan))
    def save(s, path, peak=0.9): sf.write(path, s.m / max(1e-3, np.abs(s.m).max()) * peak, SR)
SFX, BED, AMB = Bus(), Bus(), Bus()      # AMB: ambience/foley under archive film and cinematic shots

# ---------- instruments (all tonal, no noise) ----------
def piano(f, d=3.0, vel=1.0):
    x = k(d); s = np.zeros_like(x)
    for h, a in [(1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)]:
        s += a * np.sin(2 * np.pi * f * h * x * (1 + 0.0004 * h * h)) * np.exp(-x * (1.6 + 0.9 * h))
    return lp(s * np.minimum(1, x / 0.018), 1500) * vel          # felt: slow hammer, dark tone
def pad(freqs, d, att=2.0, rel=2.5, g=1.0):
    x = k(d); s = np.zeros_like(x)
    for j, f in enumerate(freqs):
        for det in (-0.1, 0.1): s += np.sin(2 * np.pi * f * (1 + det / 100) * x + j)
    return lp(s, 900) * env(x, att, rel) * g
def bell(f, d=2.2):
    x = k(d); return (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 4)) * np.exp(-x * 1.9) * np.minimum(1, x / 0.004)
def pop(f0=520, d=0.45):                     # soft round 'bloop': fades in, fades out, no click
    x = k(d); f = f0 * 0.75 * (1 + 0.25 * np.exp(-x * 30))
    e = np.minimum(1, x / 0.03) * np.exp(-x * 9) * np.clip((d - x) / 0.15, 0, 1)
    return lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * e, 1300)
def tick(f=1150): x = k(0.03); return lp(np.sin(2 * np.pi * f * x) * np.exp(-x * 150), 3000)
def chime(up=True):
    x = k(0.6); f1, f2 = (1046.5, 1568) if up else (880, 659.3)
    return np.sin(2 * np.pi * f1 * x) * np.exp(-x * 9) * 0.5 + np.sin(2 * np.pi * f2 * x) * np.exp(-np.maximum(x - 0.08, 0) * 7) * (x > 0.08) * 0.45
def thud(): x = k(0.7); return np.sin(2 * np.pi * 62 * x) * np.minimum(1, x / 0.03) * np.exp(-x * 7) * 0.7
def sub(d=2.2): x = k(d); return np.sin(2 * np.pi * 49 * x * (1 + 0.2 * np.exp(-x * 5))) * np.exp(-x * 2.0)
def riser(d=1.4): x = k(d); return np.sin(2 * np.pi * np.cumsum(220 + 440 * (x / d) ** 2) / SR) * (x / d) ** 2 * 0.25
def swell(d, up=True):                      # a soft tonal glide that fades in and out (replaces ticking counters)
    x = k(d); f = (392 + 130 * (x / d)) if up else (523 - 130 * (x / d))
    return lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / d) ** 2, 1200)
def counter(t0, dur, up=True, n_=18, g=0.5):
    SFX.add(t0, swell(dur + 0.3, up), g * 0.5); SFX.add(t0 + dur, bell(784 if up else 587, 2.0), g * 0.35)

# ---------- signature ident (tonal riser instead of the old noise swell) ----------
def ident(t0):
    SFX.add(t0 - 0.2, riser(1.6), 1.0); BED.add(t0 + 1.5, pad([130.81, 164.81, 196.0, 246.94, 293.66], 5.0, 0.8, 2.2), 1.0)
    for j, f in enumerate([659.25, 987.77, 1318.5]): SFX.add(t0 + 1.95 + j * 0.2, bell(f), 0.55, pan=(j - 1) * 0.3)
    SFX.add(t0 + 2.4, sub(), 0.9)
if T.IDENT_T: ident(T.IDENT_T + 0.4)

# ---------- ambience / foley for film shots (soft, low, under the voice; rumble only, never hiss) ----------
def brown(d):
    w = rng.standard_normal(int(d * SR)); b_ = np.cumsum(w); b_ -= np.convolve(b_, np.ones(4801) / 4801, "same"); return b_ / (np.abs(b_).max() + 1e-9)
def car_pass(t0, d, pass_frac=0.75):
    x = k(d); tp = d * pass_frac; dist = np.sqrt(((x - tp) * 14.0) ** 2 + 6.0 ** 2)             # car at ~14 m/s, 6 m from the camera
    vel = -14.0 * 14.0 * (x - tp) / dist; dop = 343 / (343 - vel)                               # doppler: higher coming, lower going
    f0 = 38 * dop * (1 + 0.02 * np.sin(2 * np.pi * 0.7 * x)); ph = 2 * np.pi * np.cumsum(f0) / SR
    eng = sum(np.sin(h * ph + h) / h ** 0.9 for h in range(1, 9))
    loud = (6.0 / dist) ** 1.6; fade = np.minimum(1, x / 0.6) * np.clip((d - x) / 0.6, 0, 1)
    road = lp(brown(d), 260) * 0.9
    sig = lp(eng * 0.35 + road, 700) * loud * fade
    pan = np.clip((x - tp) / 2.5, -1, 1) * 0.7
    i = int(t0 * SR); m = min(len(sig), n - i)
    AMB.m[i:i + m, 0] += sig[:m] * (1 - np.maximum(0, pan[:m])); AMB.m[i:i + m, 1] += sig[:m] * (1 + np.minimum(0, pan[:m]))
    AMB.add(t0, lp(brown(d), 180) * 0.12 * fade)                                                # distant traffic bed
def town(t0, d):
    x = k(d); fade = np.minimum(1, x / 1.0) * np.clip((d - x) / 1.0, 0, 1); AMB.add(t0, lp(brown(d), 220) * 0.25 * fade)

# ---------- cold-open tension: a soft low heartbeat pulse under the hook (stops at the ident) ----------
if T.IDENT_T:
    tq = 0.4
    while tq < T.IDENT_T - 0.8:
        x_ = k(0.5); hb = np.sin(2 * np.pi * 52 * x_) * np.exp(-x_ * 9) * np.minimum(1, x_ / 0.01)
        BED.add(tq, lp(hb, 300), 0.9); BED.add(tq + 0.28, lp(hb, 300), 0.55); tq += 1.25

# ---------- time travel (rewind 2026 -> first year): film-reel spin, tonal only, soft arrival ----------
def rewind_sfx(t0, d):
    x = k(d); u = x / d
    sp = np.sin(np.pi * np.clip((u - 0.05) / 0.8, 0, 1))                       # reel speed 0 -> fast -> 0
    f = 180 + 700 * sp                                                           # pitch follows the speed (tape spin)
    flutter = 1 + 0.06 * np.sin(2 * np.pi * np.cumsum(6 + 26 * sp) / SR)       # wobble gets faster with speed
    s_ = np.sin(2 * np.pi * np.cumsum(f * flutter) / SR) + 0.35 * np.sin(2 * np.pi * np.cumsum(f * 1.5 * flutter) / SR)
    s_ = lp(s_ * (0.15 + 0.85 * sp) * np.minimum(1, x / 0.25) * np.clip((d - x) / 0.3, 0, 1), 1800)
    SFX.add(t0, s_, 0.55)
    # click-free reel 'whirr' = amplitude-modulated low tone
    wh = np.sin(2 * np.pi * 95 * x) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(4 + 30 * sp) / SR)) * sp
    SFX.add(t0, lp(wh, 900), 0.45)
    arr = t0 + 0.86 * d
    SFX.add(arr - 0.05, thud(), 0.5); SFX.add(arr, bell(523.25, 3.0), 0.35); SFX.add(arr + 0.05, pad([130.81, 196.0, 261.63], 3.0, 0.05, 2.5), 0.5)
if getattr(T, "REW_T", None): rewind_sfx(T.REW_T, T.REWIND)

# ---------- background: felt piano over warm pad, A minor -> F -> C -> G ----------
PROG = [[55.0, 110.0, 130.81, 164.81], [43.65, 87.31, 110.0, 130.81], [65.41, 98.0, 130.81, 164.81], [49.0, 98.0, 123.47, 146.83]]
q, j = 0.4, 0
while q < min(END, T.OUTRO + 1.0) - 1.0:
    if T.IDENT_T and T.IDENT_T - 0.6 < q < T.IDENT_T + T.IDENT_DUR - 0.8: q = T.IDENT_T + T.IDENT_DUR - 0.8; continue
    if getattr(T, "REW_T", None) and T.REW_T - 2.0 < q < T.REW_T + T.REWIND: q = T.REW_T + T.REWIND; continue
    ch = PROG[j % 4]; BED.add(q, pad([c * 2 for c in ch[:3]], 12.4, 4.0, 4.5), 0.30)
    for s_, note in enumerate([ch[2] * 2, ch[3] * 2, ch[2] * 4, ch[3] * 2]):            # meditative: one soft note every ~2.7 s
        BED.add(q + 0.6 + s_ * 2.7, piano(note, 6.0, 0.8 - 0.1 * (s_ % 2)), 0.55, pan=0.2 * np.sin(s_ * 1.7))
    q += 10.8; j += 1

# ---------- element sounds: soft, tonal, quiet (no sound for timeline travel or branch lines) ----------
for e in T.EL:
    tin, kd = e["tin"], e["kind"]; pan = (e["x"] - 960) / 1800
    if tin > min(END, T.OUTRO): continue
    if kd == "cine":
        BED.add(tin, pad([65.41, 98.0, 130.81], 5.0, 1.5, 2.5), 0.5)      # cinematic shots: a soft low swell, no pop
        amb = e["pay"].get("amb"); dur_ = e["tout"] - tin
        if amb == "car": car_pass(tin, dur_, e["pay"].get("passby", 0.75))
        elif amb == "town": town(tin, dur_)
        continue
    if kd in ("cut", "person", "photo", "screen", "place"): SFX.add(tin, pop(440), 0.8, pan=pan)
    elif kd == "lab": SFX.add(tin, pop(620), 0.45, pan=pan)
    elif kd == "stamp": SFX.add(tin, thud(), 0.6); SFX.add(tin, pop(330), 0.4)
    elif kd in ("words", "quote"): SFX.add(tin, piano(784, 1.6, 0.6), 0.35, pan=pan)
    elif kd == "focus": SFX.add(tin, thud(), 0.6); SFX.add(tin + 0.02, bell(784), 0.35)
    elif kd == "bars":
        for j_, tk in enumerate(e["pay"]["t"]): SFX.add(tk, pop(520), 0.6, pan=-0.3 + 0.3 * j_); counter(tk, 0.7, e["pay"]["data"][j_][1] >= 0, 10, 0.3)
    elif kd == "chain":
        for j_, it in enumerate(e["pay"]): SFX.add(it[2], pop(500), 0.7, pan=-0.45 + 0.3 * j_)
    elif kd in ("big", "count"):
        txt_ = str(e["pay"][0]); SFX.add(tin, pop(480), 0.6)
        if kd == "count" or T.parse_num(txt_): counter(tin, T.COUNT_DUR, not txt_.startswith(("−", "-")), 18, 0.4)
    elif kd == "grid": SFX.add(tin, pop(500), 0.5)

# ---------- end screen ----------
if not getattr(T, "DEMO", False):
    BED.add(T.OUTRO + 0.3, pad([130.81, 164.81, 196.0, 246.94, 293.66], T.ENDSCREEN, 1.2, 3.0), 0.8)
    for j_, f in enumerate([659.25, 987.77, 1318.5]): SFX.add(T.OUTRO + 0.6 + j_ * 0.2, bell(f), 0.55, pan=(j_ - 1) * 0.3)
    SFX.add(T.OUTRO + 1.0, sub(), 0.8)

fade = np.clip((END - 0.2 - np.arange(n) / SR) / 1.6, 0, 1)[:, None]; SFX.m *= fade; BED.m *= fade
def room(bus, sec, wet):
    x = k(sec); ir = lp(rng.standard_normal(len(x)), 2500) * np.exp(-x * 6.9 / sec); ir /= np.abs(ir).sum() ** 0.5 * 8
    for c in range(2): bus.m[:, c] = bus.m[:, c] * (1 - wet) + ss.fftconvolve(bus.m[:, c], ir)[:n] * wet * 4
room(BED, 3.5, 0.45); room(SFX, 1.6, 0.3)
SFX.m *= fade; BED.m *= fade; AMB.m *= fade
SFX.save(f"{D}/sfx.wav"); BED.save(f"{D}/bed.wav"); AMB.save(f"{D}/amb.wav")
v = np.zeros(int(END * 24000), np.float32)
for m in T.META:
    a, _ = sf.read(f"{D}/voice/s{m['i']:03d}.wav"); s0 = int(m["t"] * 24000); v[s0:s0 + len(a)] += a[: max(0, len(v) - s0)]
sf.write(f"{D}/voice.wav", v, 24000); print("stems ok", round(END, 2))
