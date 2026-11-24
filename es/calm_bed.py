"""EMPIRE STORIES calm bed (owner rule 24 Nov 2026): one slow, soft music bed under the whole episode.
No ticks, pops, whooshes, hits or stingers. Fades in at the start and out at the end, smoothly.
usage: python3 calm_bed.py <seconds> <out.wav>"""
import sys
import numpy as np, soundfile as sf, scipy.signal as ss
SR = 48000; DUR = float(sys.argv[1]); OUT = sys.argv[2]; n = int(DUR * SR)
def k(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): b, a = ss.butter(o, fc / (SR / 2)); return ss.lfilter(b, a, x)
def env(x, att, rel): e = np.minimum(1, x / max(att, 1e-3)); return e * np.clip((x[-1] - x) / max(rel, 1e-3), 0, 1)
def piano(f, d=6.0, vel=1.0):
    x = k(d); s = np.zeros_like(x)
    for h, a in [(1, 1.0), (2, 0.4), (3, 0.18), (4, 0.08)]:
        s += a * np.sin(2 * np.pi * f * h * x * (1 + 0.0004 * h * h)) * np.exp(-x * (0.9 + 0.7 * h))
    return lp(s * np.minimum(1, x / 0.03), 1400) * vel
def pad(freqs, d, att=3.0, rel=3.5):
    x = k(d); s = np.zeros_like(x)
    for j, f in enumerate(freqs):
        for det in (-0.12, 0.12): s += np.sin(2 * np.pi * f * (1 + det / 100) * x + j)
    return lp(s, 700) * env(x, att, rel)
M = np.zeros((n, 2))
def add(at, sig, g, pan=0.0):
    i = int(at * SR)
    if i >= n: return
    x = sig[: n - i] * g; M[i:i + len(x), 0] += x * (1 - max(0, pan)); M[i:i + len(x), 1] += x * (1 + min(0, pan))
# warm, unhurried progression: C - Am - F - G (two bars of ~4.8 s each), around 50 bpm feel
CH = [[130.81, 164.81, 196.00, 246.94], [110.00, 130.81, 164.81, 196.00], [87.31, 130.81, 174.61, 220.00], [98.00, 123.47, 146.83, 196.00]]
MEL = [[523.25, 392.00, 329.63], [440.00, 329.63, 392.00], [349.23, 440.00, 523.25], [392.00, 293.66, 246.94]]
L = 9.6; t = 0.0; j = 0
while t < DUR:
    c = CH[j % 4]
    add(t, pad(c, L + 3.0), 0.22)
    add(t, piano(c[0] / 2, 7.0, 0.5), 0.5)
    for s_, f in enumerate(MEL[j % 4]):                          # three gentle notes per chord, far apart
        add(t + 0.8 + s_ * 3.0, piano(f, 6.0, 0.55), 0.42, pan=0.25 * np.sin(j + s_))
    t += L; j += 1
# soft room
ir_t = k(3.2); ir = np.exp(-ir_t * 1.6) * np.random.default_rng(3).standard_normal(len(ir_t)) * 0.02
for ch in (0, 1): M[:, ch] = M[:, ch] * 0.7 + ss.fftconvolve(M[:, ch], ir)[:n] * 0.6
tt = np.arange(n) / SR
fade = np.clip(tt / 3.0, 0, 1) * np.clip((DUR - tt) / 3.5, 0, 1)
M *= (0.5 - 0.5 * np.cos(np.pi * fade))[:, None]
sf.write(OUT, M / max(1e-3, np.abs(M).max()) * 0.85, SR); print("calm bed", DUR, "s")
