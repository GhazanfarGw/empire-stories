"""EMPIRE STORIES demo v2 — conversational narration, one wav per sentence (pauses added in the timeline)."""
import soundfile as sf, json, os
from kokoro_onnx import Kokoro
os.chdir("/home/claude/es/tl3"); os.makedirs("voice", exist_ok=True)
k = Kokoro("/home/claude/kok/kokoro-v1.0.int8.onnx", "/home/claude/kok/voices-v1.0.bin")
import numpy as np; VOICE = np.load("/home/claude/es/vt/lewis_blend.npy")
# (beat, sentence, pause_after, speed)  — slower on money, decisions and turning points
S = [
 ("hook", "Now, here's something surprising.", 0.55, 0.9),
 ("hook", "In nineteen ninety-seven, Apple was in serious trouble.", 0.35, 0.88),
 ("hook", "Steve Jobs later said the company was about ninety days from going broke.", 0.7, 0.86),
 ("hook", "So how did it survive?", 0.4, 0.9),
 ("hook", "To understand that, we need to go back to the beginning.", 0.6, 0.9),
 ("y0", "In nineteen seventy-six, Steve Jobs and Steve Wozniak start a small company.", 0.25, 0.9),
 ("y0", "They call it Apple.", 0.7, 0.88),
 ("y1", "But in nineteen eighty-five, after a fight with Apple's board, Jobs is pushed out of his own company.", 0.4, 0.88),
 ("y1", "So he starts again. A new company, called NeXT.", 0.7, 0.9),
 ("y2", "Meanwhile, Apple keeps growing.", 0.25, 0.9),
 ("y2", "By nineteen ninety-five, its sales reach eleven billion dollars.", 0.45, 0.86),
 ("y2", "But here's the problem. The company is about to fall.", 0.7, 0.88),
 ("y3", "One year later, Apple loses more than eight hundred million dollars.", 0.4, 0.86),
 ("y3", "It badly needs a modern operating system. So it buys NeXT, for four hundred million.", 0.35, 0.88),
 ("y3", "And that deal brings Steve Jobs back.", 0.7, 0.88),
 ("y4", "By nineteen ninety-seven, Jobs is running Apple again. And his first move surprises everyone.", 0.6, 0.9),
 ("map", "He makes peace with his biggest rival.", 0.35, 0.88),
 ("map", "Microsoft, up in Redmond, agrees to invest a hundred and fifty million dollars in Apple.", 0.4, 0.86),
 ("map", "Jobs announces the deal on stage, at Macworld in Boston.", 0.7, 0.9),
 ("y4b", "Then he cuts about seventy percent of Apple's products.", 0.3, 0.86),
 ("y4b", "Fewer products. But better ones.", 0.7, 0.86),
 ("y5", "In nineteen ninety-eight, the iMac arrives.", 0.3, 0.9),
 ("y5", "And Apple makes its first yearly profit since nineteen ninety-five.", 0.7, 0.88),
 ("y6", "In two thousand one, the iPod puts a thousand songs in your pocket.", 0.7, 0.9),
 ("y7", "And in two thousand seven, the iPhone.", 0.35, 0.88),
 ("y7", "That year, Apple earns three and a half billion dollars.", 0.8, 0.86),
 ("lesson", "So what really saved Apple?", 0.5, 0.88),
 ("lesson", "Not one product. It was focus.", 0.4, 0.86),
 ("lesson", "Saying no to almost everything, so the few things that mattered could be great.", 1.0, 0.88),
]
meta = []
for i, (b, s, p, sp) in enumerate(S):
    a, sr = k.create(s, voice=VOICE, speed=sp + 0.07, lang="en-gb"); sf.write(f"voice/s{i:02d}.wav", a, sr)
    meta.append({"i": i, "beat": b, "text": s, "dur": len(a) / sr, "pause": p})
json.dump(meta, open("voice/meta.json", "w"), indent=1)
print(round(sum(m["dur"] + m["pause"] for m in meta), 1), "s of narration")
