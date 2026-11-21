"""EMPIRE STORIES · Episode 01 sound: signature ident, quiet ambient bed, odometer ticks on year changes, pops/zips/swishes
on every element, calculator ticks on counting numbers, thuds on stamps, then voice placed per sentence."""
import sys, os, numpy as np, wave, soundfile as sf, scipy.signal as ss
sys.argv = ["x", "q"]; sys.path.insert(0, "/home/claude/es/ep01"); sys.path.insert(0, "/home/claude/es/tl3")
import ep01 as T
D = "/home/claude/es/ep01"
SR = 48000; END = T.END; n = int(END * SR); t = np.arange(n) / SR
rng = np.random.default_rng(7); mix = np.zeros((n, 2), np.float64)
def k(d): return np.arange(int(d * SR)) / SR
def add(at, sig, g=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0 or i >= n: return
    s = sig[: n - i] * g; mix[i:i + len(s), 0] += s * (1 - max(0, pan)); mix[i:i + len(s), 1] += s * (1 + min(0, pan))
def lp(x, fc, o=2): b, a = ss.butter(o, fc / (SR / 2)); return ss.lfilter(b, a, x)
def hp(x, fc): b, a = ss.butter(2, fc / (SR / 2), "high"); return ss.lfilter(b, a, x)
def env(x, att, rel): e = np.minimum(1, x / max(att, 1e-3)); return e * np.clip((x[-1] - x) / max(rel, 1e-3), 0, 1)
def bell(f, d=2.4):
    x = k(d); return (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3) + 0.18 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 6)) * np.exp(-x * 1.7) * np.minimum(1, x / 0.004)
def pad(freqs, d, att=1.6, rel=2.2, g=0.05):
    x = k(d); s = np.zeros_like(x)
    for j, f in enumerate(freqs):
        for det in (-0.12, 0.12): s += np.sin(2 * np.pi * (f + det * f / 100) * x + j) + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * x)
    return lp(s, 1400) * env(x, att, rel) * g
def boom(): x = k(2.5); return (np.sin(2 * np.pi * 52 * x * (1 + 0.25 * np.exp(-x * 6))) * np.exp(-x * 2.2) + lp(rng.normal(0, 1, len(x)), 220) * np.exp(-x * 5) * 0.5) * 0.55
def swell(d): x = k(d); return lp(rng.normal(0, 1, len(x)), 900) * (x / d) ** 2.5 * 0.16
def tick(): x = k(0.08); return np.sin(2 * np.pi * 1400 * x) * np.exp(-x * 60) * 0.5
def soft_whoosh(d=0.9): x = k(d); return lp(hp(rng.normal(0, 1, len(x)), 300), 1600) * np.sin(np.pi * x / d) ** 2 * 0.35
def thud(): x = k(0.5); return (np.sin(2 * np.pi * 75 * x * (1 + 0.6 * np.exp(-x * 25))) * np.exp(-x * 10) + lp(rng.normal(0, 1, len(x)), 700) * np.exp(-x * 30) * 0.5) * 0.7
def pop_big():
    x = k(0.16); f = 620 * np.exp(-x * 22) + 180; body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 26)
    return (body + hp(rng.normal(0, 1, len(x)), 3000) * np.exp(-x * 400) * 0.5) * 0.8
def pop_small():
    x = k(0.09); f = 1400 * np.exp(-x * 40) + 520; return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 45) + hp(rng.normal(0, 1, len(x)), 4000) * np.exp(-x * 600) * 0.35) * 0.6
def zip_(d=0.45):
    x = k(d); n_ = hp(rng.normal(0, 1, len(x)), 1800); f = np.linspace(1200, 5200, len(x))
    return lp(n_ * (0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(f / 40) / SR)), 6000) * np.sin(np.pi * x / d) ** 1.5 * 0.22
def swish(d=0.8): x = k(d); return lp(hp(rng.normal(0, 1, len(x)), 2500), 7000) * np.sin(np.pi * x / d) ** 2 * 0.12
def ctick(f=1200): x = k(0.035); return (np.sin(2 * np.pi * f * x) * 0.7 + hp(rng.normal(0, 1, len(x)), 5000) * 0.3) * np.exp(-x * 140) * 0.55
def lock(up=True):
    x = k(0.5); f1, f2 = (1568, 2093) if up else (1175, 880)
    return np.sin(2 * np.pi * f1 * x) * np.exp(-x * 9) * 0.35 + np.sin(2 * np.pi * f2 * x) * np.exp(-np.maximum(x - 0.07, 0) * 8) * (x > 0.07) * 0.3
def counter(t0, dur, up=True, n_=20, g=0.26):
    for j in range(1, n_ + 1):
        fr = j / n_; tx = 1 - (1 - fr) ** (1 / 3); f = (900 + 900 * fr) if up else (1800 - 800 * fr)
        add(t0 + dur * tx, ctick(f), g * (0.75 + 0.25 * fr), pan=0.12 * (1 if j % 2 else -1))
    add(t0 + dur + 0.02, ctick(2600), g * 1.2); add(t0 + dur + 0.03, lock(up), g * 0.9)
def ident(t0):
    add(t0 + 0.1, swell(1.9), 1.0)
    x = k(6.5); dr = (np.sin(2 * np.pi * 55 * x) * 0.6 + np.sin(2 * np.pi * 82.41 * x) * 0.3) * env(x, 1.4, 2.0) * 0.12; add(t0, dr)
    add(t0 + 1.7, pad([130.81, 164.81, 196.0, 246.94, 293.66], 5.2, 0.9, 2.4, 0.045))
    for j, f in enumerate([659.25, 987.77, 1318.5]): add(t0 + 1.95 + j * 0.2, bell(f), 0.11, pan=(j - 1) * 0.3)
    add(t0 + 2.4, boom(), 0.8); add(t0 + 3.4, bell(1975.5, 2.0), 0.035, pan=0.2)

# cold open bed -> signature ident
add(0.3, pad([130.81, 196.0, 246.94, 329.63], T.IDENT_T, 2.0, 1.2, 0.03))
add(T.IDENT_T - 0.5, swell(1.0), 0.6); ident(T.IDENT_T + 0.4)
# ambient bed: a slow four-chord cycle, very soft, under the whole story
CH = [[130.81, 196.0, 246.94, 329.63], [110.0, 164.81, 196.0, 261.63], [87.31, 130.81, 164.81, 220.0], [98.0, 146.83, 196.0, 261.63]]
q = T.IDENT_T + T.IDENT_DUR - 1.2; j = 0
while q < T.OUTRO + 1.0:
    add(q, pad(CH[j % 4], 9.6, 2.4, 3.0, 0.028)); add(q + 0.4, bell(CH[j % 4][3] * 2, 3.0), 0.011, pan=0.35 if j % 2 else -0.35)
    q += 8.0; j += 1
# crunchy year changes
for i, b in enumerate(T.YB):
    a0 = T.TR[b]; y0 = T.YEARS[i - 1] if i else 1970; y1 = T.YEARS[i]; last = y0
    for f in np.linspace(0, 1, 400):
        roll = T.r(f * 0.9 + 0.05, 0.05, 0.95); v = int(y0 + (y1 - y0) * (1 - (1 - roll) ** 2.2))
        if v != last: add(a0 + 0.05 + f * 0.9, tick(), 0.22, pan=0.15 * ((v % 2) * 2 - 1)); last = v
    add(a0 + 0.02, soft_whoosh(0.8), 0.16); add(a0 + 0.95, soft_whoosh(0.5), 0.2)
    add(T.PIN_T[i] - 0.03, thud(), 0.42); add(T.PIN_T[i] - 0.02, tick(), 0.3)
# every element gets its micro-sound
for e in T.EL:
    tin, kd = e["tin"], e["kind"]; pan = (e["x"] - 960) / 1600
    if tin > T.OUTRO: continue
    if T.PIN_OF.get(e["b"]) is not None and e["branch"] and kd != "stamp": add(tin - 0.55, zip_(0.5), 1.0, pan=pan)
    if kd in ("cut", "person", "photo", "screen"): add(tin, pop_big(), 0.55, pan=pan); add(tin + 0.22, swish(0.8), 1.0)
    elif kd == "lab": add(tin, pop_small(), 0.45, pan=pan); add(tin + 0.2, swish(0.7), 0.8)
    elif kd == "stamp": add(tin, thud(), 0.5); add(tin, pop_big(), 0.3)
    elif kd == "note": add(tin, pop_small(), 0.2)
    elif kd in ("words", "quote"): add(tin, swish(0.9), 1.1, pan=pan); add(tin + 0.05, pop_small(), 0.22)
    elif kd == "focus": add(tin, pop_big(), 0.55); add(tin, thud(), 0.45)
    elif kd == "chart":
        for j_ in range(5): add(tin + 0.12 * j_, pop_small(), 0.3, pan=-0.3 + 0.15 * j_); counter(tin + 0.12 * j_, 0.6, True, 8, 0.16)
    elif kd == "bars":
        for j_, tk in enumerate(e["pay"]["t"]): add(tk, pop_small(), 0.32, pan=-0.3 + 0.2 * j_); counter(tk, 0.7, e["pay"]["data"][j_][1] >= 0, 10, 0.17)
    elif kd == "chain":
        for j_, it in enumerate(e["pay"]): add(it[2], pop_big(), 0.45, pan=-0.45 + 0.3 * j_); add(it[2] - 0.2, zip_(0.35), 0.8, pan=-0.45 + 0.3 * j_)
    elif kd == "grid":
        p = e["pay"]
        if not p.get("small"):
            for j_ in range(4): add(tin + 0.15 * j_, zip_(0.5), 0.9, pan=-0.2 + 0.13 * j_)
            add(p["lab"], pop_small(), 0.35); add(p["fill"], pop_big(), 0.4); add(p["fill"] + 0.3, pop_big(), 0.35); add(p["rule"], pop_small(), 0.4); add(p["pulse"], thud(), 0.3)
        else:
            for j_ in range(4): add(tin + 0.15 * j_, pop_small(), 0.25)
    elif kd in ("big", "count"):
        txt_ = str(e["pay"][0]); up = not txt_.startswith(("−", "-")); add(tin, pop_big(), 0.4)
        if kd == "count" or T.parse_num(txt_): counter(tin, T.COUNT_DUR, up, 22, 0.26)
# map: pins pop, arcs zip, $150M counts
for at in (T.st("map", 0, 0.6), T.mid("map", 1, 0.5), T.st("map", 2, 2.2)): add(at, pop_big(), 0.5)
add(T.st("map", 2, 1.0), zip_(1.4), 1.2); add(T.mid("map", 3, 0.6), zip_(1.3), 1.2); counter(T.st("map", 4, 0.3), T.COUNT_DUR, True, 22, 0.26)
add(T.mid("map", 4, 0.6), pop_small(), 0.4)
for b0 in ("map", "deal"): add(T.TR[b0], soft_whoosh(1.1), 0.25)
add(T.TR["lesson"], soft_whoosh(1.2), 0.22)
# end screen: signature chime + warm pad
add(T.OUTRO, swell(1.0), 0.5); add(T.OUTRO + 0.3, pad([130.81, 164.81, 196.0, 246.94, 293.66], T.ENDSCREEN, 1.2, 3.0, 0.05))
for j_, f in enumerate([659.25, 987.77, 1318.5]): add(T.OUTRO + 0.6 + j_ * 0.2, bell(f), 0.1, pan=(j_ - 1) * 0.3)
add(T.OUTRO + 1.0, boom(), 0.6)
for dt in (0.2, 1.0, 1.3, 1.4): add(T.OUTRO + 0.2 + dt, pop_big() if dt != 1.4 else pop_small(), 0.4)
fade = np.clip((END - 0.2 - t) / 1.6, 0, 1); mix *= fade[:, None]; mix /= np.abs(mix).max() * 1.12
w = wave.open(f"{D}/music.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
v = np.zeros(int(END * 24000), np.float32)
for m in T.META:
    a, _ = sf.read(f"{D}/voice/s{m['i']:03d}.wav"); s = int(m["t"] * 24000); v[s:s + len(a)] += a[: len(v) - s]
sf.write(f"{D}/voice.wav", v, 24000); print("ok", round(END, 2))
