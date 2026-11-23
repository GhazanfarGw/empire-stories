import sys; sys.path.insert(0, "/home/claude/es/thumbkit")
from journey import *
im = cover(A + "hq_infinite_loop.jpg", crop=(286, 0, 1250, 674)); brand(im)
jobs = fit_h(key_flood(Image.open(A + "people/steve-jobs.png")), 1020)
put(im, jobs, -40, H - jobs.height + 40, rim=(212, 175, 55))
tag(im, 30, H - 60)
badge(im, A + "apple_logo_crop.jpg", None, W - 160, 160, 125)
slab(im, "APPLE", 1250, 70, 140, (23, 23, 23), (255, 255, 255))
slab(im, "1985 – 2007", 1250, 300, 150, (244, 241, 234), (11, 19, 43))
slab(im, "THE COMEBACK STORY", 1250, 520, 60, (11, 19, 43), (212, 175, 55), k="sansb", padx=36, pady=16)
x = W - 40
for f, h in (("iphone_cut.png", 300), ("ipod_cut.png", 230), ("imac34_cut.png", 360)):
    o = Image.open(A + f).convert("RGBA"); o = key_flood(o) if f.startswith("iphone") else o; o = o.crop(o.getbbox()); o = fit_h(o, h); x -= o.width; put(im, o, x, H - o.height - 40); x += 10
save(im, "/home/claude/es/ep01/thumbs/thumb_V3_journey.jpg")
