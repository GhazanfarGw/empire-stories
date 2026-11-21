"""EMPIRE STORIES sound v2 (locked 21 Nov 2026, owner feedback):
- NO sound when the timeline travels / branch lines draw (no odometer ticks, no zips, no whooshes)
- NO noise-based 'shh' sounds at all (no swish, swell, hiss): every effect is tonal and soft
- effects bus sits at ~20-25% of the voice; background bed very low, smooth, ducked under the voice
- bed: slow felt-piano arpeggios over a warm pad (documentary tone)
Writes three stems: voice.wav, sfx.wav, bed.wav -> mixed in run.sh."""
import sys, os, numpy as np, soundfile as sf, scipy.signal as ss
sys.argv = ["x", "q"]; D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
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
    def save(s, path, peak=0.9): sf.write(path, s.m / max(1e-9, np.abs(s.m).max()) * peak, SR)
SFX, BED = Bus(), Bus()

# ---------- instruments (all tonal, no noise) ----------
def piano(f, d=3.0, vel=1.0):
    x = k(d); s = np.zeros_like(x)
    for h, a in [(1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)]:
        s += a * np.sin(2 * np.pi * f * h * x * (1 + 0.0004 * h * h)) * np.exp(-x * (1.6 + 0.9 * h))
    return lp(s * np.minimum(1, x / 0.006), 2600) * vel
def pad(freqs, d, att=2.0, rel=2.5, g=1.0):
    x = k(d); s = np.zeros_like(x)
    for j, f in enumerate(freqs):
        for det in (-0.1, 0.1): s += np.sin(2 * np.pi * f * (1 + det / 100) * x + j)
    return lp(s, 900) * env(x, att, rel) * g
def bell(f, d=2.2):
    x = k(d); return (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 4)) * np.exp(-x * 1.9) * np.minimum(1, x / 0.004)
def pop(f0=520, d=0.12):                     # soft round 'bloop'
    x = k(d); f = f0 * (1 + 0.6 * np.exp(-x * 40)); return lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 32), 2200)
def tick(f=1150): x = k(0.03); return lp(np.sin(2 * np.pi * f * x) * np.exp(-x * 150), 3000)
def chime(up=True):
    x = k(0.6); f1, f2 = (1046.5, 1568) if up else (880, 659.3)
    return np.sin(2 * np.pi * f1 * x) * np.exp(-x * 9) * 0.5 + np.sin(2 * np.pi * f2 * x) * np.exp(-np.maximum(x - 0.08, 0) * 7) * (x > 0.08) * 0.45
def thud(): x = k(0.45); return np.sin(2 * np.pi * 70 * x * (1 + 0.5 * np.exp(-x * 25))) * np.exp(-x * 11)
def sub(d=2.2): x = k(d); return np.sin(2 * np.pi * 49 * x * (1 + 0.2 * np.exp(-x * 5))) * np.exp(-x * 2.0)
def riser(d=1.4): x = k(d); return np.sin(2 * np.pi * np.cumsum(220 + 440 * (x / d) ** 2) / SR) * (x / d) ** 2 * 0.25
def counter(t0, dur, up=True, n_=18, g=0.5):
    for j in range(1, n_ + 1):
        fr = j / n_; tx = 1 - (1 - fr) ** (1 / 3); f = (900 + 700 * fr) if up else (1500 - 600 * fr)
        SFX.add(t0 + dur * tx, tick(f), g * (0.7 + 0.3 * fr), pan=0.1 * (1 if j % 2 else -1))
    SFX.add(t0 + dur + 0.02, chime(up), g * 1.1)

# ---------- signature ident (tonal riser instead of the old noise swell) ----------
def ident(t0):
    SFX.add(t0 - 0.2, riser(1.6), 1.0); BED.add(t0 + 1.5, pad([130.81, 164.81, 196.0, 246.94, 293.66], 5.0, 0.8, 2.2), 1.0)
    for j, f in enumerate([659.25, 987.77, 1318.5]): SFX.add(t0 + 1.95 + j * 0.2, bell(f), 0.55, pan=(j - 1) * 0.3)
    SFX.add(t0 + 2.4, sub(), 0.9)
if T.IDENT_T: ident(T.IDENT_T + 0.4)

# ---------- background: felt piano over warm pad, A minor -> F -> C -> G ----------
PROG = [[110.0, 220.0, 261.63, 329.63], [87.31, 174.61, 220.0, 261.63], [130.81, 196.0, 261.63, 329.63], [98.0, 196.0, 246.94, 293.66]]
q, j = 0.4, 0
while q < min(END, T.OUTRO + 1.0) - 1.0:
    if T.IDENT_T and T.IDENT_T - 0.6 < q < T.IDENT_T + T.IDENT_DUR - 0.8: q = T.IDENT_T + T.IDENT_DUR - 0.8; continue
    ch = PROG[j % 4]; BED.add(q, pad(ch[:3], 8.6, 2.5, 3.0), 0.35)
    for s_, note in enumerate([ch[1], ch[2], ch[3], ch[2] * 2, ch[3], ch[2]]):        # gentle arpeggio, one note every ~1.3 s
        BED.add(q + 0.3 + s_ * 1.33, piano(note, 3.2, 0.9 - 0.08 * (s_ % 3)), 0.5, pan=0.25 * np.sin(s_))
    q += 8.0; j += 1

# ---------- element sounds: soft, tonal, quiet (no sound for timeline travel or branch lines) ----------
for e in T.EL:
    tin, kd = e["tin"], e["kind"]; pan = (e["x"] - 960) / 1800
    if tin > min(END, T.OUTRO): continue
    if kd in ("cut", "person", "photo", "screen"): SFX.add(tin, pop(440), 0.8, pan=pan)
    elif kd == "lab": SFX.add(tin, pop(660, 0.09), 0.55, pan=pan)
    elif kd == "stamp": SFX.add(tin, thud(), 0.8); SFX.add(tin, pop(330), 0.5)
    elif kd in ("words", "quote"): SFX.add(tin, piano(784, 1.6, 0.6), 0.35, pan=pan)
    elif kd == "focus": SFX.add(tin, thud(), 0.8); SFX.add(tin + 0.02, bell(784), 0.5)
    elif kd == "bars":
        for j_, tk in enumerate(e["pay"]["t"]): SFX.add(tk, pop(520), 0.6, pan=-0.3 + 0.3 * j_); counter(tk, 0.7, e["pay"]["data"][j_][1] >= 0, 10, 0.35)
    elif kd == "chain":
        for j_, it in enumerate(e["pay"]): SFX.add(it[2], pop(500), 0.7, pan=-0.45 + 0.3 * j_)
    elif kd in ("big", "count"):
        txt_ = str(e["pay"][0]); SFX.add(tin, pop(480), 0.6)
        if kd == "count" or T.parse_num(txt_): counter(tin, T.COUNT_DUR, not txt_.startswith(("−", "-")), 18, 0.5)
    elif kd == "grid": SFX.add(tin, pop(500), 0.5)

# ---------- end screen ----------
if not T.DEMO:
    BED.add(T.OUTRO + 0.3, pad([130.81, 164.81, 196.0, 246.94, 293.66], T.ENDSCREEN, 1.2, 3.0), 0.8)
    for j_, f in enumerate([659.25, 987.77, 1318.5]): SFX.add(T.OUTRO + 0.6 + j_ * 0.2, bell(f), 0.55, pan=(j_ - 1) * 0.3)
    SFX.add(T.OUTRO + 1.0, sub(), 0.8)

fade = np.clip((END - 0.2 - np.arange(n) / SR) / 1.6, 0, 1)[:, None]; SFX.m *= fade; BED.m *= fade
SFX.save(f"{D}/sfx.wav"); BED.save(f"{D}/bed.wav")
v = np.zeros(int(END * 24000), np.float32)
for m in T.META:
    a, _ = sf.read(f"{D}/voice/s{m['i']:03d}.wav"); s0 = int(m["t"] * 24000); v[s0:s0 + len(a)] += a[: max(0, len(v) - s0)]
sf.write(f"{D}/voice.wav", v, 24000); print("stems ok", round(END, 2))
