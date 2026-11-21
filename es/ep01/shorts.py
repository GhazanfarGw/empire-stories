"""Cut vertical Shorts (1080x1920) from the finished Episode 01: brand header + hook title, the 16:9 story crop in the middle,
big readable captions underneath (Shorts are often watched muted), and a 'full story' footer."""
import os, sys, json, subprocess
sys.argv = ["x", "q"]; sys.path.insert(0, "/home/claude/es/ep01")
import ep01 as X
from PIL import Image, ImageDraw
from tl3 import font, txt, NAVY_US, RED_US, IVORY, INK, V
D = "/home/claude/es/ep01"; SRC = f"{D}/EMPIRE_STORIES_Ep01_Apple_Was_Almost_Finished.mp4"; OUT = f"{D}/shorts"; os.makedirs(OUT, exist_ok=True)
def m_end(b, i): m = [x for x in X.META if x["beat"] == b][i]; return m["t"] + m["dur"]
SHORTS = [
    ("short1_shut_it_down", ["Michael Dell said Apple", "should be SHUT DOWN."], 0.6, X.st("hook", 9) + 1.4),
    ("short2_four_boxes", ["How Steve Jobs saved", "Apple with FOUR BOXES"], X.st("y4b", 4) - 0.3, m_end("y4b", 15) + 0.6),
    ("short3_microsoft_deal", ["Why Apple took", "MICROSOFT'S MONEY"], X.TR["map"] + 0.2, m_end("deal", 5) + 0.7),
]
def bg(title):
    im = V.bg().resize((1080, 1920)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1080, 440], fill=NAVY_US + (255,)); d.rectangle([0, 434, 1080, 446], fill=RED_US + (255,))
    em = X.emblem_us(96); im.alpha_composite(em, (60, 50)); d.text((176, 98), "EMPIRE STORIES", font=font("cardo", 46), fill=IVORY, anchor="lm")
    for k, line in enumerate(title):
        hi = any(w.isupper() and len(w) > 2 for w in line.split())
        d.text((540, 250 + k * 92), line, font=font("disp", 74), fill=(RED_US if hi else IVORY) if k else IVORY, anchor="mm")
    d.rectangle([0, 1790, 1080, 1920], fill=NAVY_US + (255,))
    d.text((540, 1855), "FULL STORY · EPISODE 01 ON THE CHANNEL", font=font("sansb", 34), fill=IVORY, anchor="mm")
    return im
def ass(a, b, path):
    def ts(s): s = max(0, s); return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: C,Inter,64,&H00611F0A,&H00611F0A,&H00F4F1EA,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,70,70,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for m in X.META:
        s0, s1 = m["t"], m["t"] + m["dur"] + 0.1
        if s1 <= a or s0 >= b: continue
        words = m["cap"].split(); chunks = [words[i:i + 6] for i in range(0, len(words), 6)]; dt = (s1 - s0) / len(chunks)
        for j, c in enumerate(chunks):
            c0, c1 = max(a, s0 + j * dt), min(b, s0 + (j + 1) * dt)
            if c1 > c0: ev.append(f"Dialogue: 0,{ts(c0 - a)},{ts(c1 - a)},C,,0,0,0,,{{\\pos(540,1500)}}{' '.join(c)}")
    open(path, "w").write(head + "\n".join(ev) + "\n")
for name, title, a, b in SHORTS:
    bgp = f"{OUT}/{name}_bg.png"; bg(title).convert("RGB").save(bgp); ap = f"{OUT}/{name}.ass"; ass(a, b, ap); dur = b - a
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", SRC, "-loop", "1", "-i", bgp, "-filter_complex",
                    f"[0:v]crop=1680:1080:120:0,scale=1080:694[v];[1:v][v]overlay=0:500:shortest=1,ass={ap},format=yuv420p[o];"
                    f"[0:a]afade=t=in:d=0.3,afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]",
                    "-map", "[o]", "-map", "[au]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", f"{OUT}/{name}.mp4"], check=True)
    print(name, round(dur, 1), "s", os.path.getsize(f"{OUT}/{name}.mp4") // 1024 // 1024, "MB")
