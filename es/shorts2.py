"""EMPIRE STORIES Shorts layout v2 (owner feedback 21 Nov 2026):
thin header (brand + hook line), BIG story window in the middle (1120x1080 crop -> 1080x1041), captions centred
under the picture, thin footer. Person cards enter as centred 'hero' portraits (engine feature), so faces fill the middle.
Usage: python3 shorts2.py <episode_dir> <module> <ep_label>   (segments defined in <episode_dir>/shorts_v2.json)"""
import os, sys, json, subprocess
from PIL import Image, ImageDraw
EP_DIR, MOD, LABEL = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", "q"]; sys.path.insert(0, EP_DIR); sys.path.insert(0, "/home/claude/es/tl3")
import importlib; X = importlib.import_module(MOD)
from tl3 import font, NAVY_US, RED_US, IVORY, V
OUT = f"{EP_DIR}/shorts_v2"; os.makedirs(OUT, exist_ok=True)
VID_Y, VID_H = 168, 1041

def bg(title):
    im = V.bg().resize((1080, 1920)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1080, 150], fill=NAVY_US + (255,)); d.rectangle([0, 148, 1080, 156], fill=RED_US + (255,))
    em = X.emblem_us(52); im.alpha_composite(em, (32, 14)); d.text((96, 40), "EMPIRE STORIES", font=font("cardo", 30), fill=IVORY, anchor="lm")
    d.text((540, 108), title, font=font("disp", 50), fill=IVORY, anchor="mm")
    d.rectangle([0, 1846, 1080, 1920], fill=NAVY_US + (255,))
    d.text((540, 1883), f"FULL STORY · {LABEL} ON THE CHANNEL", font=font("sansb", 26), fill=IVORY, anchor="mm")
    return im

def ass(a, b, path):
    def ts(s): s = max(0, s); return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: C,Inter,72,&H00611F0A,&H00611F0A,&H00F4F1EA,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for m in X.META:
        s0, s1 = m["t"], m["t"] + m["dur"] + 0.1
        if s1 <= a or s0 >= b: continue
        w = m["cap"].split(); ch = [w[i:i + 5] for i in range(0, len(w), 5)]; dt = (s1 - s0) / len(ch)
        for j, c in enumerate(ch):
            c0, c1 = max(a, s0 + j * dt), min(b, s0 + (j + 1) * dt)
            if c1 > c0: ev.append(f"Dialogue: 0,{ts(c0 - a)},{ts(c1 - a)},C,,0,0,0,,{{\\pos(540,1500)}}{' '.join(c)}")
    open(path, "w").write(head + "\n".join(ev) + "\n")

for sh in json.load(open(f"{EP_DIR}/shorts_v2.json")):
    a, b, name = sh["a"], sh["b"], sh["name"]; dur = b - a
    bgp = f"{OUT}/{name}_bg.png"; bg(sh["title"]).convert("RGB").save(bgp); ap = f"{OUT}/{name}.ass"; ass(a, b, ap)
    vin = ["-ss", f"{sh.get('v_off', a):.3f}", "-t", f"{dur:.3f}", "-i", sh["video"]]
    ain = ["-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", sh["audio"]]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *vin, *ain, "-loop", "1", "-i", bgp, "-filter_complex",
                    f"[0:v]crop=1120:1080:400:0,scale=1080:{VID_H}[v];[2:v][v]overlay=0:{VID_Y}:shortest=1,ass={ap},format=yuv420p[o];"
                    f"[1:a]afade=t=in:d=0.3,afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]",
                    "-map", "[o]", "-map", "[au]", "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", f"{OUT}/{name}.mp4"], check=True)
    print(name, round(dur, 1), "s")
