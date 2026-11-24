"""Season 2 score for the demo: music that follows the drama, soft musical accents on every title. No ticks, clicks or whooshes."""
import json, numpy as np, soundfile as sf, scipy.signal as ss
SR = 48000
VM = json.load(open("/home/claude/demo2/vmeta.json"))
def T(i, f=0.0): return VM[i]["t0"] + f * VM[i]["dur"]
END = VM[-1]["t0"] + VM[-1]["dur"] + 3.2; n = int(END * SR)
M = np.zeros((n, 2)); ACC = np.zeros((n, 2))
def k(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): b, a = ss.butter(o, fc / (SR / 2)); return ss.lfilter(b, a, x)
def hp(x, fc, o=2): b, a = ss.butter(o, fc / (SR / 2), "high"); return ss.lfilter(b, a, x)
def env(x, att, rel): e = np.minimum(1, x / max(att, 1e-3)); return e * np.clip((x[-1] - x) / max(rel, 1e-3), 0, 1)
def add(B, at, sig, g, pan=0.0):
    i = int(at * SR)
    if i >= n or i < 0: return
    x = sig[: n - i] * g; B[i:i + len(x), 0] += x * (1 - max(0, pan)); B[i:i + len(x), 1] += x * (1 + min(0, pan))
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def piano(f, d=4.0, v=1.0):
    x = k(d); s = sum(a * np.sin(2 * np.pi * f * h * x * (1 + 0.0004 * h * h)) * np.exp(-x * (1.1 + 0.8 * h)) for h, a in [(1, 1), (2, .4), (3, .18), (4, .08)])
    return lp(s * np.minimum(1, x / 0.012), 2200) * v
def pluck(f, d=0.9, v=1.0):                     # marimba-like
    x = k(d); s = np.sin(2 * np.pi * f * x) * np.exp(-x * 7) + 0.3 * np.sin(2 * np.pi * f * 4 * x) * np.exp(-x * 20)
    return s * np.minimum(1, x / 0.004) * v
def pad(ms, d, att=2.0, rel=2.0, bright=900):
    x = k(d); s = sum(np.sin(2 * np.pi * hz(m) * (1 + det / 100) * x + j) for j, m in enumerate(ms) for det in (-0.12, 0.12))
    return lp(s, bright) * env(x, att, rel)
def strings(ms, d, att=3.0, rel=2.5, bright=1600):   # saw-ish ensemble with vibrato
    x = k(d); s = np.zeros_like(x)
    for j, m in enumerate(ms):
        for det in (-0.15, 0.0, 0.15):
            ph = 2 * np.pi * hz(m) * (1 + det / 100) * x + 0.004 * np.sin(2 * np.pi * 5.2 * x + j)
            s += sum(np.sin(h * ph) / h for h in range(1, 7))
    return lp(s, bright) * env(x, att, rel)
def drone(m, d):
    x = k(d); s = np.sin(2 * np.pi * hz(m) * x) + 0.5 * np.sin(2 * np.pi * hz(m + 12) * x) + 0.25 * np.sin(2 * np.pi * hz(m + 7) * x)
    return lp(s * (1 + 0.15 * np.sin(2 * np.pi * 0.25 * x)), 500) * env(x, 1.5, 2.0)
def pulse(f, d):                                 # soft low heartbeat, tonal
    x = k(d); return np.sin(2 * np.pi * f * x * (1 + 0.4 * np.exp(-x * 30))) * np.exp(-x * 9) * np.minimum(1, x / 0.01)
def bell(f, d=2.5):
    x = k(d); return (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * f * 2.0 * x) * np.exp(-x * 3) + 0.15 * np.sin(2 * np.pi * f * 3.01 * x) * np.exp(-x * 5)) * np.exp(-x * 2.2) * np.minimum(1, x / 0.006)
def swell(ms, d):                               # soft rising swell into a moment (no noise)
    x = k(d); s = sum(np.sin(2 * np.pi * hz(m) * x) for m in ms); return lp(s, 1200) * (x / d) ** 2.2 * np.clip((d - x) / 0.08, 0, 1)

# ACT A (0 -> T2): warm, curious, moving.  C major-ish, 96 bpm piano arpeggio + pad + heartbeat
A1 = T(2) - 0.4; beat = 60 / 96
prog = [[48, 55, 60, 64, 67], [45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [43, 50, 55, 59, 62]]
t = 0.3; j = 0
while t < A1:
    ch = prog[(j // 8) % 4]
    add(M, t, piano(hz(ch[1 + j % 4] + 12), 2.0, 0.55), 0.5, pan=0.3 * np.sin(j))
    if j % 2 == 0: add(M, t, pulse(55, 0.5), 0.35)
    if j % 8 == 0: add(M, t, pad(ch[:3], 8 * beat + 1.0, 1.0, 1.0), 0.18); add(M, t, piano(hz(ch[0]), 3.0, 0.7), 0.5)
    t += beat; j += 1
# the drop: everything stops, then a low tense drone (A minor) with sparse high notes
add(M, T(2) + 0.25, piano(hz(45), 6.0, 1.0), 0.8); add(M, T(2) + 0.25, piano(hz(33), 6.0, 1.0), 0.6)
B0 = T(2) + 1.0; B1 = T(5) + 0.2
add(M, B0, drone(33, B1 - B0 + 1.5), 0.32)
add(M, B0 + 0.5, strings([57, 60, 64], B1 - B0 + 1.0, 4.0, 1.5, 900), 0.06)
for q, m in [(0.0, 76), (2.6, 72), (5.2, 74), (7.4, 71)]:
    add(M, B0 + 1.2 + q, piano(hz(m), 4.0, 0.5), 0.35, pan=0.4)
# ACT B (T5 -> T8): the plan; bright marimba ostinato that builds, 104 bpm, D major lift
C0 = T(5) - 0.2; C1 = T(8) - 0.5; beat = 60 / 104
add(M, C0 - 1.4, swell([62, 66, 69], 1.5), 0.18)
ost = [62, 69, 74, 69, 66, 69, 74, 78]; bass = [38, 38, 35, 35, 31, 31, 33, 33]
t = C0; j = 0
while t < C1:
    g = 0.35 + 0.35 * min(1, (t - C0) / (C1 - C0))
    add(M, t, pluck(hz(ost[j % 8]), 0.8), 0.32 * g, pan=0.25 * ((j % 2) * 2 - 1))
    if j % 4 == 0: add(M, t, pulse(hz(bass[(j // 4) % 8]), 0.7), 0.5 * g); add(M, t, pad([bass[(j // 4) % 8] + 24, bass[(j // 4) % 8] + 28, bass[(j // 4) % 8] + 31], 4 * beat + 0.8, 0.6, 0.8), 0.12 * g)
    t += beat / 2; j += 1
add(M, C1 - 0.2, piano(hz(62), 4.0, 0.8), 0.5); add(M, C1 - 0.2, pad([50, 57, 62, 66], 3.0, 0.3, 2.5), 0.15)
# ACT C (T8 -> T11): mystery; minor, pizzicato low pulse, slow rising strings, a held breath before 'Eight.'
D0 = T(8) - 0.3; D1 = T(10); beat = 60 / 84
t = D0; j = 0
while t < D1 - 0.6:
    add(M, t, pluck(hz([40, 47, 43, 47][j % 4]), 1.0), 0.45)
    if j % 4 == 2: add(M, t, piano(hz([71, 74, 72, 76][(j // 4) % 4]), 3.0, 0.5), 0.3, pan=-0.3)
    t += beat; j += 1
add(M, D0, strings([52, 55, 59], D1 - D0 + 0.5, 5.0, 0.6, 1100), 0.07)
add(M, D1 - 1.6, swell([64, 67, 71], 1.6), 0.22)
add(M, D1, piano(hz(40), 5.0, 1.0), 0.7); add(M, D1, bell(hz(76), 3.0), 0.25)          # the '8' lands
# ACT D (T11 -> end): the journey; heroic swell, strings + piano melody, final chord
E0 = T(11) - 0.2
add(M, E0, strings([48, 55, 60, 64], END - E0, 3.0, 3.0, 1800), 0.08)
add(M, E0, pad([36, 43, 48], END - E0, 2.0, 3.0), 0.2)
mel = [(0.0, 67), (1.2, 72), (2.4, 74), (3.2, 76), (4.6, 79), (6.2, 76)]
for q, m in mel: add(M, E0 + 0.4 + q, piano(hz(m), 4.0, 0.7), 0.45, pan=0.2)
t = E0; beat = 60 / 96
while t < T(12) + 1.0: add(M, t, pulse(48, 0.6), 0.35); t += beat
add(M, T(12, 0.7), strings([41, 48, 53, 57, 60], END - T(12, 0.7), 1.2, 2.8, 2000), 0.1)
add(M, T(12, 0.7), piano(hz(53), 6, 0.9), 0.6); add(M, T(12, 0.7), bell(hz(77), 4.0), 0.22)
# soft musical accent on every title (a bell + piano note in the act's key)
import film
keyacc = {0: 72, 1: 69, 2: 74, 3: 78, 4: 74, 5: 71, 6: 76, 7: 72, 8: 77}
for i, (ti, *_r) in enumerate(film.TITLES):
    m = keyacc.get(i, 72); add(ACC, ti, bell(hz(m), 2.4), 0.28, pan=-0.15); add(ACC, ti, piano(hz(m - 12), 2.0, 0.6), 0.25)
# room + master fades
ir_t = k(2.6); ir = np.exp(-ir_t * 2.0) * np.random.default_rng(2).standard_normal(len(ir_t)) * 0.02
for B in (M, ACC):
    for ch in (0, 1): B[:, ch] = B[:, ch] * 0.75 + ss.fftconvolve(B[:, ch], ir)[:n] * 0.5
tt = np.arange(n) / SR; fade = (np.clip(tt / 1.0, 0, 1) * np.clip((END - tt) / 2.0, 0, 1))[:, None]
M *= fade; ACC *= fade
sf.write("/home/claude/demo2/music.wav", M / np.abs(M).max() * 0.9, SR)
sf.write("/home/claude/demo2/accents.wav", ACC / max(1e-6, np.abs(ACC).max()) * 0.9, SR)
# narration track
V = np.zeros(n)
for m in VM:
    a, sr = sf.read(f"/home/claude/demo2/v{m['i']:02d}.wav"); a = ss.resample_poly(a, SR, sr); i = int(m["t0"] * SR); V[i:i + len(a)] += a[: n - i]
sf.write("/home/claude/demo2/voice.wav", V, SR); print("score ok", round(END, 1))
