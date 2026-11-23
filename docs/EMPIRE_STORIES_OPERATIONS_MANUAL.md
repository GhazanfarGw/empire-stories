# EMPIRE STORIES — Operations Manual (master backup)

*The stories behind global empires.*
Version 1.0 · 21 Nov 2026 · Owner: Ghazanfar Abbas (Karachi) · Maintained by the channel's AI production agent

This document is the single source of truth for running the channel. If the current AI account, membership or automation is lost, a new AI agent (Claude, ChatGPT, Gemini or a human editor) can read this file and continue the channel with the same look, voice, quality and workflow. **Read it top to bottom before producing anything.**

---

> **APPROVED SYSTEM — locked by the owner on 21 Nov 2026 (final approval 20:33 PKT, incl. §5j moods + slam, Shorts v3).** Everything in this manual up to and including §5j (sound v3, motion and badges, journey to today + TODAY card, chapters, place photos and big images, time-travel rewind, torn-paper image frame, cinematic `cine` scenes with archive footage and ambience, centre-first layout, sound moments, punchy cold open, vertical centring) is the **approved house style** for every future episode and Short. Reference render: `Ep02 DEMO v8` (+ §5j: `Ep02 DEMO v10`/`v11`). Frozen copy: GitHub branch `approved-2026-11-21`. Do not change any of it without the owner's approval.

## 0. Where everything lives (backup map)

| What | Primary location | Backup copies |
|---|---|---|
| Production code (renderer, sound, voice, Shorts, thumbnails) | GitHub `GhazanfarGw/empire-stories` (public) | `E:\Empire Stories\_backup\empire-stories-full-backup.zip`, Google Drive folder **EMPIRE STORIES** |
| Voice engine model files (too big for git) | `E:\Empire Stories\_backup\` inside the full-backup zip (`kok/`) | Re-downloadable (see §6) |
| This manual | `docs/EMPIRE_STORIES_OPERATIONS_MANUAL.md` in the repo | `E:\Empire Stories\_backup\`, Google Drive (Google Doc), Claude Project "Empire Stories" |
| Finished episodes, Shorts, thumbnails, SRT, descriptions | `E:\Empire Stories\EpXX - <title>\final\` | YouTube (originals downloadable from Studio) |
| Product photos + credits | `es/assets/` + `es/assets/CREDITS.txt` | Episode folder `assets\photos_products\` |
| Founder illustrations | `es/assets/people/<first-last>.png` | Episode folder `assets\photos_people\` |
| Brand files (banner, icon/watermark) | `E:\Empire Stories\_brand\` | — |
| Master creative brief | `docs/MASTER_BRIEF.txt` | Claude Project doc `claude/empire-stories-master-brief.txt` |

**Accounts used** (owner holds all passwords; never store passwords in files):
- YouTube channel **Empire Stories Documentary** · handle `@EmpireStoriesDocumentary` · channel ID `UCjzZkbXiGjlBgK1EGjJws7A` · owned by the owner's Google account.
- GitHub `GhazanfarGw` (code).
- Zapier (YouTube + Google Drive connections, used for automatic upload/scheduling/localization).
- Google Drive folder "EMPIRE STORIES" (id `1BjQCsO4Bvex2ZHB2B-S1l0r09s0FW7Dr`).
- Google Gemini (owner's account) for founder illustrations.

**Security checklist for the owner:** 2-step verification on the Google account that owns the channel; save Google backup codes offline; add a second trusted *Manager* to the channel (Studio → Settings → Permissions) so the channel is never tied to one login; keep the `E:\Empire Stories\_backup` folder also on an external drive.

---

## 1. Channel identity (locked)

- **What we are:** an international *business documentary* channel. Company stories only: origins, history, case studies, rise of empires, rise and fall, rivalries, innovation. Founders appear only where their decisions matter to the company story. No motivational content, no billionaire biographies, no fiction.
- **Promise to the viewer:** a premium, cinematic, accurate explanation of *why* a company became what it is — Netflix-style story, Vox-style visual explanation.
- **Global coverage:** USA, Europe, China, Japan, Korea, India, Pakistan, the Gulf, Brazil, Africa. Pakistani and Indian companies are a deliberate differentiator.
- **Every episode answers one central question** and ends with **OUR TAKE**: the business lesson.
- **Length:** long-form as long as the story needs (10–25 min); Shorts 40–60 s.

## 2. Brand system (locked — do not redesign per episode)

| Token | Value | Use |
|---|---|---|
| Navy | `#0A3161` (RGB 10,49,97) | Primary: labels, numbers going up, end screen, ident background |
| Navy 2 | `#1C4A84` | Secondary panels |
| Red | `#B31942` (RGB 179,25,66) | Accent: losses, highlights, active timeline pin, stamps, underline swipes |
| Ivory | `#F4F1EA` | Text on navy |
| Ink | dark navy-black (from toolkit `INK`) | Body text on paper |
| Page grey | `#D6D5D1` textured paper | Background of every story scene |

Gold is **retired** (old palette). No dollar-bill watermark. No burnt-in subtitles on long-form (YouTube CC uses our SRT / published captions).

**Fonts:** Inter Display Bold (big numbers, display), Inter Bold/Medium (labels, UI), Crimson Text SemiBold / SemiBold Italic (headlines, quotes), Cardo Bold (EMPIRE STORIES wordmark).

**Visual grammar (every episode):**
1. **Cold open** (~45 s): the most surprising fact/quote, counting numbers, a question → no logo yet.
2. **Ident** (7.8 s, navy): emblem (columned temple in red ring) → "EMPIRE STORIES" → tagline → "PRESENTS" → red label "EPISODE NN" → episode title in serif.
3. **Composed timeline**: horizontal axis at the bottom; year changes roll like an odometer with "+N YEARS", a red travel line runs to the next pin, the pin lands with a shockwave; every panel element is connected to its pin by an elbow branch line. Past pins stay visible.
4. **Elements**: illustration cards (torn-paper frame, navy name band, "AI ILLUSTRATION" tag; no red borders), product photos with **thin torn-paper edges hugging the image's shape**, label boxes (navy/red with traced outline), big counting numbers (count up/down with calculator ticks), red rubber stamps, quote cards with a big red “ and red highlighter swipe, bar charts, 2×2 grids, chain diagrams.
5. **Map scene** for geography (Albers projection, US Census / world-atlas boundaries), pins + arcs.
6. **OUR TAKE** section: red label, serif headline, the lesson in one big word (e.g. FOCUS.).
7. **End screen** (14 s navy): emblem + wordmark + subscribe circle (left), two video boxes "WATCH NEXT" / "MORE STORIES" (right). Add YouTube end-screen elements on top after publishing.
8. Subtle grain + vignette on every frame. 1920×1080, 30 fps.

**Panels rule:** a beat with many sentences is split into panels; elements leave (fade up) when the narration moves on; nothing ever overlaps. Before every full render, render QC contact sheets of the busiest moment of every panel and fix overlaps.

## 3. Thumbnail standard (v2, locked by the owner 22 Nov 2026 — replaces the v1 "PRO" style)

Rule: **a viewer who cannot read must know the company from the thumbnail alone.** Kit: `es/thumbkit/tk.py`; per episode `epNN/thumb_v2.py` (references: `ep01/thumbs/thumb_V2_A.jpg`, `ep02/thumbs/thumb_V2_A.jpg`).
- **Company icon, top-left, big and clear:** a real, licensed photo of the company's logo/sign (e.g. the Golden Arches pylon, a glowing Apple Store logo), cut out or in a round badge with an ivory rim. Credit the photo in the description. (We use a real photo of the sign, not a redrawn logo.)
- **The people of the story, right side:** the founder/main leader big in front (AI illustration, red rim light), plus 1–2 other key people of the story smaller behind (e.g. Kroc + the McDonald brothers + Sonneborn; Jobs + Michael Dell). Always the "AI ILLUSTRATION" tag. Nobody hidden behind another face.
- **One story object, small, bottom-left:** the product that sums up the story (Big Mac, iMac G3, a phone, a car), cut out.
- **Crunchy headline in the middle-left:** 2 short lines, max ~3 words each, ivory + gold/red, thick outline + shadow (e.g. "BURGERS? / NO. RENT.", "ALMOST / FINISHED"). Small red pill "COMPANY · YEARS" under the icon.
- Dark navy gradient + red glow behind the people. Nothing overlaps the headline.
- Export 1280×720 JPG < 2 MB. Always make **A** (matches title) and **B** (alternative hook) for Test & Compare.

## 4. Narration voice (locked)

- Engine: **Kokoro TTS** (`kokoro-onnx 0.6.1`, model `kokoro-v1.0.int8.onnx` + `voices-v1.0.bin`), language `en-gb`.
- Voice: **blend 75 % `bm_lewis` + 25 % `bm_george`** saved as `es/vt/lewis_blend.npy` (shape 510×1×256). Recreate: `np.load` style vectors from `voices-v1.0.bin` and compute `0.75*lewis + 0.25*george`.
- Generate one WAV per sentence; speed = per-sentence value (0.82–0.9) **+ 0.07**. Slower on money, decisions and turning points; pauses 0.3–1.0 s after sentences (stored in the script).
- Numbers are written out in the spoken text ("nineteen ninety-seven"); the caption text keeps digits ("1997").
- Post-processing (ffmpeg, deep British documentary tone):
  `asetrate=24000*0.96,aresample=48000,atempo=1.0417,highpass=f=50,lowshelf=f=120:g=4.5,equalizer=f=260:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-18dB:ratio=3:attack=5:release=80`
- If Kokoro is unavailable: use any deep British male narrator (e.g. ElevenLabs "documentary British male"), same pacing and pauses. Keep it consistent from then on.

## 5. Sound design (locked v3, 21 Nov 2026 — owner feedback #2; replaces v2)

Code: `es/ep02/audio.py` (stems: voice, sfx, bed; works for any episode with `EP_DIR=… EP_MODULE=…`) + `es/ep02/mix.sh`. **Same sound in episodes AND Shorts** (Shorts take their audio from the v3 mix, never from an older episode mix). Rules:
- **Voice first.** The narration is always the clearest thing; everything else sits underneath it like a calm history documentary.
- **Background bed = deep, slow, meditative felt piano**: one soft low note every ~2.7 s over a warm low pad (A minor → F → C → G, 10.8 s per chord), long room reverb. Low volume (`volume=0.14`), side-chain ducked hard under the voice (threshold 0.012, ratio 10, attack 60 ms, release 1.2 s).
- *(Superseded by §5j: no appear sounds at all.)* Previously: **every pop/click/appear sound is soft:** 30 ms fade-in, smooth fade-out tail, low-passed (≈1.3 kHz), small room reverb. Effects bus `volume=0.12` (peaks stay below the voice). No ticking counters: numbers get one soft tonal glide + a quiet bell.
- **No sound when the timeline travels or branch lines draw. No noise-based "shh/snake" sounds anywhere** (v2 rules kept).
- Signature ident: tonal riser → pad → 3-note bell chime → soft sub (no noise).
- Final mix −14 LUFS, true peak −1.5 dB, AAC 192 kbps 48 kHz.

## 5b. Motion and badges (locked 21 Nov 2026 — owner feedback #2)
- **Everything enters by fading UP smoothly** (0.6 s ease, ~26 px rise) and leaves with a 0.5 s fade. No sideways slides for text/labels.
- **Badges** (`badge()` in the engine): the coloured label box and its thin red frame are ONE image, so the frame always lines up with the box. The identical badge style is used in episodes and Shorts.

## 5c. Story scope: journey to TODAY (locked 21 Nov 2026)
Every documentary carries the story from the beginning **up to the present year (2026)**, then shows an **"<COMPANY> TODAY · 2026" status card** (`today` element): 3–4 tiles such as restaurants/stores/users, latest annual revenue or sales, global brand rank (Kantar BrandZ / Interbrand), stock-market value with month, plus the next stated goal. Every tile carries its source and date. When a founder/leader in the story is alive, show their current role and **net worth from Forbes real-time (with date)**; when they have died, say so with the year. Reputation is shown only with a named source (rankings, surveys, awards, major controversies reported by reputable press) — never our opinion stated as fact.

## 5d. YouTube chapters (every long video)
The description always has a CHAPTERS block: first line `00:00`, at least 3 chapters, each ≥ 10 s, one per story section (cold open, each year/turning point, today, our take). This gives the clickable key-moments bar on the timeline. Generated with `python3 epNN.py chapters` from the real scene start times. Ep01 has 9 live chapters.

**Hooks (owner rule):** the cold open must force the viewer to stay: open on a simple question everyone thinks they can answer, flip it with one verified, surprising number, add a quote, end on the central question. 45–55 s max.

**Visual-first rule (owner feedback, 21 Nov 2026):** a viewer with the sound off, or who doesn't speak English, must still follow the story from the pictures. Prefer photos, illustrations, maps, charts and simple diagrams over text labels; keep labels to a few words; never fill the screen with text.

**Hero portraits (engine feature, `HERO_SCALE = 1.45`):** every new person card first appears big in the centre of the screen for ~2 s (or until the next element arrives), then slides into its timeline slot and the branch line draws to it.

**Shorts = native mobile video (owner rule, 21 Nov 2026; `es/vshort.py`; same badges, motion and v3 sound as the episodes):** never a desktop video placed in a vertical frame. Full-screen 1080×1920 on the paper background, **no subtitles**, no letterbox bands. Small brand mark + one-line title + red year badge at the top; the story fills the screen. Every scene is re-laid out for the phone: whatever is on screen is stacked top-to-bottom, **picture first and its text underneath**, scaled to fill the width; when something arrives or leaves the others slide smoothly. Quotes and headlines re-wrap at phone width. Map scenes are framed for the phone. The previous scene holds through short narration gaps (no empty screens). Same timing as the episode so voice and sound line up. Segments in `<episode>/shorts_v2.json`. Zapier free plan = **max 5 uploads per day**: plan uploads (episode + Shorts) across days.

## 5e. Places, big images, time travel (locked 21 Nov 2026 — owner feedback #3)
- **Every city or country the narration names gets a real photo, never just a text label** (`place` element): the photo big and centred (≈1100–1460 px wide), ivory border with a thin navy frame, slow push-in, and a navy caption band **under** the photo (place name + one short line). Licensed photos only (Wikimedia Commons / Library of Congress), credited.
- **Use the full screen width.** Columns at x = 600 / 1320; person cards 40 % bigger (`PS = 1.4`); a single person or a single key image is shown big in the centre. Quotes get wider lines.
- **More real images for every era**: period photos, places, products, buildings. Text supports the picture, never replaces it.
- **Open in the present, then travel back** (`rewind` scene, 3.6 s, before the first year): the cold open shows the empire as it is today; after the ident a cinematic time-travel takes us back. A big year counter rolls back from 2026 to the first year, a film reel of the story's photos races past (turning sepia as we go back), light streaks, a soft flash on arrival, and the counter lands as the first timeline year. It is a designed sequence; we never play the finished video backwards. Sound: tonal film-reel spin that speeds up and slows down, then a soft arrival (thud + bell + pad), with no hiss.

## 5f. Image frame (locked 21 Nov 2026 — owner: "this is our design")
**Every image uses the torn-paper frame**: product photos, place photos, founder/illustration cards and any other picture get the thin torn white-paper rim that follows the image's shape, with a soft drop shadow (`paper.torn_image()` / `edge_card()`). **No red outline, no traced red line, no second border around images, ever** (that looked amateur). Founder cards are square-cornered illustrations with the navy name band inside the torn rim; long names shrink to fit. Place cards: photo + navy caption band inside one torn-paper card. Episodes and Shorts use the same frame.

## 5g. Cinematic documentary, not a presentation (locked 21 Nov 2026 — owner feedback #4)
- **Length follows the story:** 10, 15, 20 or 25 minutes is fine. Cover every turning point properly and comfortably; never rush to hit a length.
- **Always name the year in narration.** Say "in 2007" / "in twenty twenty-five", never "in a single year", "last year" or "that year" alone. The audio must make complete sense with no picture, because episodes will also be sold/streamed as audio (e.g. Shopify, podcast platforms). Every number gets its year and its owner (who earned it, when).
- **Netflix-style cinema, not slides:** the paper timeline is the spine, but between data panels the story cuts to **full-screen cinematic shots** (`cine` element): full-bleed photos with a slow camera push/pan, and **real archive film** (public-domain footage) with a lower-third caption (red bar + place/year + one line), soft colour grade, grain and vignette. Every era should have real pictures and, where available, real moving footage. Text panels are kept for numbers only.
- **Footage sources (licence-safe only):** Prelinger Archives / Internet Archive films marked with the Creative Commons Public Domain dedication; Wikimedia Commons videos marked public domain or CC; US government films (NARA, NASA). Films without a public-domain mark need permission and are not used. Credit every clip on screen and in the description. Archive footage is labelled as archive/illustrative, never passed off as the exact event.
- Cinematic shots get a soft low swell instead of a pop.
- **Voice chain:** the locked deep-voice filter (§4) is part of `mix.sh` for every episode.

## 5h. Centre-first layout + film ambience (locked 21 Nov 2026 — owner feedback #5)
**These rules are the house system for EVERY future episode and Short, not just one video.**
- **Centre-first:** the viewer's eye is in the middle of the screen, so every new number, label, headline or picture first appears **in the centre**. When the next item of the same panel arrives, the first one glides smoothly to the left (0.7 s ease) and shrinks slightly (×1.12 → ×1.0), and the new item comes in beside it. Same idea as hero portraits (a person appears big in the centre, then moves to their slot). Nothing should ever start at the edge. Engine: `_set_centre_first()` / `centre_first()`; columns of a panel are detected automatically.
- **Film ambience:** archive film and full-screen shots carry soft, real-sounding ambience under the narration: cars passing (engine + road rumble with doppler and stereo movement), town/traffic rumble, crowds, kitchens, etc. It sits in its own `amb` stem at `volume=0.22`, gently ducked under the voice (ratio 4). Rumble/tonal only, never hiss.
- **More cinema, less text:** as much real footage and real photography as possible in every era; text only where a number needs it. Target length 15–25 minutes, covering the story properly.

## 5i. Sound moments, cold open, vertical centring (locked 21 Nov 2026 — owner feedback #6)
- **Sound moments on film:** when archive film or a full-screen shot plays, give it a moment of its own: the narration pauses ~2–2.5 s (a longer pause after the sentence), the music stays low, and the film's ambience (car passing, crowd, kitchen…) rises so it is clearly heard, then fades out as the voice returns. Ambience stem `volume=0.36`, light ducking (ratio 3); effects bus `volume=0.16`.
- **Cold open = short and punchy (~40–50 s), then the ident.** Question → one surprising number → the twist → one quote → the central question → a cinematic location shot → ident. Short sentences, short pauses, faster delivery, a soft low heartbeat pulse under it (stops at the ident). After the ident the calm documentary pace begins.
- **Everything sits on the screen's middle line.** Whatever its size, content is vertically centred in the stage area above the timeline (≈ y 465 on timeline scenes, ≈ 500–540 on scenes without the timeline). Two items side by side share the same centre line and the same height (their widths may differ), placed symmetrically around the centre (x ≈ 600 / 1320). A label belongs directly under its picture. Nothing drifts to the top or bottom edge.

## 5j. Story-driven sound only + moods (locked 21 Nov 2026 — owner feedback #7/#8; reference `Ep02 DEMO v10`)
**Principle: cinematic, not commercial.** Sound and motion serve the story; nothing is added "just because something appears".
- **No sound on ordinary appearances:** images, labels, numbers, charts and full-screen shots enter silently (no pops, clicks, ticks, whooms). What you hear is the voice, the music, the real ambience inside archive film, the ident, and the time-travel sequence.
- **Mood moments only where the story truly turns** (usually 1–3 per episode, sometimes none): `mood(kind, t0, t1)`.
  - *tension*: very slow push-in (+3 %) and a soft darkening of the edges; a low drone rising quietly underneath.
  - *impact*: the music drops out just before, then one deep held note + a dark piano chord. **No camera shake, no snap-zoom, no flash.**
  - *danger* (losses, near-bankruptcy, collapse): soft red edge tint + slow pulsing low drone. *sad*: slow minor piano. *triumph/happy*: warm swell + bells.
- **The score follows the journey** at the same smooth, low volume: tense/minor for today's mystery and dark chapters, warm/nostalgic major for the founding years, brighter for growth, minor for decline. The level never jumps; only the colour changes.
- **Voice emotion:** same narrator and tone; pace changes with the moment (slower, with a pause after a key line).
- **SLAM on tension moments (owner feedback #9, reference `Ep02 DEMO v11`):** at the key tension line, the key words (a red stamp, e.g. "THEY PAY RENT") are thrown at the screen like a stone. They fly in ~3× size, land hard in 0.2 s with a tiny bounce, at full strength. **At that exact instant:** a hard low hit sound + the dark impact chord, the music drops out, and the screen gives one short jolt (≈0.35 s), then stillness. `el(..., "stamp", ...); EL[-1].update(slam=True)` + `mood("impact", t); MOODS[-1]["jolt"] = True`.
- **Keep people awake:** we are telling a big story, not a lullaby. Calm passages stay calm, but every tension/danger/turning point gets motion + sound so viewers feel it and stay active. Ordinary appearances stay silent and smooth; no random zoom-in/zoom-out.

## 5k. Real documentary, not a presentation (locked by the owner 22 Nov 2026, from Episode 03)
- **Pictures first, every few seconds.** Most of the runtime is full-screen photos and film; paper panels are only for key numbers. Target: a new real picture or clip at least every 8–10 seconds.
- **Images never touch the timeline.** A picture is either (a) centred in the stage area with its bottom edge above the timeline axis, or (b) full screen (`cine`), with the timeline hidden while it plays. Tall photos are cropped to fit; nothing rises over or overlaps the axis.
- **Evidence like a news documentary:** period photos, newspaper headlines and documents, the company's own annual-report pages, old adverts, buildings and offices, and the founders' own words (short quotes on screen with the source and year).
- **Real footage and real voices, only where we are allowed:** public-domain archive film (Prelinger/Internet Archive, NARA, NASA, Library of Congress), Creative Commons video, and licensed free stock (with credit). TV interviews and news clips owned by networks are not downloaded or re-used (copyright claims/strikes would hit the channel); instead their words are quoted briefly on screen with source and year, over a matching picture.
- **When no real material exists: AI reconstructions.** Scenes are made with image/video AI (Gemini / vidIQ models) — places, crowds, kitchens, streets, objects, moments — shown full screen with no on-screen label (owner decision 22 Nov 2026); disclosed through YouTube's altered/synthetic content setting and a line in the description. All images and footage run full screen, never as bordered cards. No period music under images; keep the normal background bed. Real film sound plays only in narration gaps, with the bed ducked. Real people are never shown as photorealistic AI; people stay as the labelled AI illustrations.
- Research for every episode includes a visual hunt list per era (photos, film, documents, quotes) before the script is final.

## 6. Tools and environment

- Python 3.13, numpy, scipy, Pillow, soundfile, onnxruntime, kokoro-onnx; ffmpeg 6.1 with libx264 + libass.
- The workspace was a Linux cloud container (Claude). Everything also runs on any Linux/Mac/WSL machine.
- Kokoro files: in the backup zip `kok/` (model + wheels for offline install). Public source: the `kokoro-onnx` project releases (`kokoro-v1.0.int8.onnx`, `voices-v1.0.bin`).
- Rebuild: `git clone https://github.com/GhazanfarGw/empire-stories && bash empire-stories/setup.sh`, copy `kok/` to `/home/claude/kok/` (or edit the path in `gen.py`).
- Founder illustrations: Google Gemini (owner's account) — prompt style: *"flat editorial vector portrait of [person], head and shoulders, navy (#0A3161) and red (#B31942) palette on light grey, no text, not photorealistic"*. Always label "AI ILLUSTRATION". Never present as a photograph.
- Upload automation: Zapier MCP → YouTube "Upload Video" (needs a public file URL), "Update Video Thumbnail", "Make API Mutating Request" (localizations, status). Files are staged temporarily on a throwaway GitHub branch (raw.githubusercontent URL), then the branch is deleted.
- Browser automation (Claude in Chrome) for YouTube Studio pages that the API can't reach (Languages page, settings).

## 7. Episode production pipeline (step by step)

Folder per episode in the repo: `es/epNN/` (copy `es/ep01/` as the template).

1. **Pick the topic** from the Season slate (§10). Write the central question + lesson.
2. **Research fact sheet**: every number, date and quote with a source (annual reports, SEC filings, official press releases, reputable press). Mark estimates as estimates.
3. **Script** (`script.py`): list of `(beat, spoken text, caption text, pause, speed)`. Beats: `hook` → `y0..y7` (timeline pins) → map/deal beats → `lesson` → `outro`. ~1,400–1,600 words ≈ 10 min.
4. **Fact-check the script against sources before voicing.** (Ep01 lesson: two errors were caught — "worst quarter ever" and "3,000 layoffs" were wrong; corrected to "$708M in a single quarter" and "about 2,700 employees".)
5. **Voice**: `python3 gen.py` (per-sentence WAVs + `voice/meta.json`).
6. **Visual plan**: edit the element list in `epNN.py` (`el(beat, kind, x, y, payload, t_in, branch, t_out)`), years/labels of the 8 timeline pins, map scene.
7. **QC stills**: `python3 qc.py` → contact sheets in `qc/`; fix overlaps/cut-offs; re-check.
8. **Render**: `./run.sh` → parallel 60 s parts → concat → `audio.py` → mix/duck/loudnorm → final MP4 (CRF 24 slow, tune animation, hqdn3d; keeps the file < 100 MB) + `EMPIRE_STORIES_EpNN.srt`. ~35–45 min on 2 CPUs.
9. **Check final**: duration, −14 LUFS, 48 kHz audio, 6 sample frames.
10. **Thumbnails** A + B (`thumb_pro.py`), **Shorts** ×3 (`shorts.py`: 1080×1920, navy header with hook title, story crop in the middle, big captions below, footer "FULL STORY · EPISODE NN ON THE CHANNEL").
11. **Description** (`description.txt`): hook paragraph, "EMPIRE STORIES · Episode NN · Company", CHAPTERS, SOURCES, PHOTO CREDITS, AI-illustration note, narration note, tagline, 3 hashtags.
12. **Upload + schedule** (§8), **localize** (§9), copy finals to `E:\…\EpNN…\final\`, commit code to GitHub.

## 8. Publishing standard

- Title: curiosity + company, ≤ 60 characters (Ep01: "Apple Was Almost Finished. Here's How It Survived").
- Category Education (27), not made for kids, Standard licence, embedding on, language en, 12–15 tags (company, founders, "business documentary", "company history", "business case study", topic words, "empire stories").
- **Publish time: 14:30 UTC** (7:30 PM Pakistan · 9:30 AM New York · 2:30 PM London).
- **Cadence (CEO decision, 21 Nov 2026): 3 full documentaries per week (Mon / Wed / Fri) + 1 Short every day.** Move to 4–5 per week only once research + fact-check keeps up — accuracy is the brand and YouTube's inauthentic/mass-produced content policy punishes templated volume.
- After publishing: add end-screen (subscribe + "best for viewer" video), pin a comment with a question, add to a playlist, reply to early comments.

## 9. Localization (every video)

**Dubbed audio is mandatory on every video (owner decision, 21 Nov 2026).** YouTube auto-dubs English into 20 languages: Arabic, Bengali, Dutch, French, German, Hebrew, Hindi, Indonesian, Italian, Japanese, Korean, Malayalam, Polish, Portuguese, Punjabi, Russian, Spanish, Tamil, Telugu, Ukrainian. Dubs start "Processing…" on the Languages page after upload and go live automatically. YouTube cannot dub English into Urdu, Chinese or Turkish. **Owner decision: no custom dubs — the Hindi dub serves Urdu speakers**; all 20 YouTube auto-dub languages stay on for every video. Urdu/Chinese/Turkish viewers also get translated titles + descriptions and auto-translated subtitles. (If ever needed, Kokoro can make a custom Chinese track: `lang="cmn"`, voice `zm_yunjian`, uploaded by hand in Studio → Languages → Audio → Add.)

- Studio → Settings → Channel → Advanced: **Automatic dubbing ON, manual review OFF** (dubs publish automatically). YouTube auto-dubs English into ~20 languages (incl. Hindi, Spanish, Portuguese, French, German, Japanese, Korean, Indonesian, Bengali).
- English captions: Studio → video → Languages → English → publish the auto captions (check names/numbers) or upload the SRT. Viewers can auto-translate captions to any language.
- **Titles + descriptions in 6 priority languages: Hindi (hi), Urdu (ur), Arabic (ar), Chinese Simplified (zh-Hans), Russian (ru), Turkish (tr)** — via Studio Languages page or the API (`PUT videos?part=localizations` with the full localizations map; include `en`).
- Translate hook paragraph + chapters; point to the English description for sources.

## 10. Content plan — Season 1 slate (full list of 100: `docs/SLATE_TOP_100.md`)

01 Apple (1997 turnaround) ✔ published · 02 McDonald's (burger or property company?) · 03 Nokia (rise and fall) · 04 Toyota (production system) · 05 Coca-Cola vs Pepsi · 06 Tata Group · 07 Engro (Pakistan) · 08 Samsung · 09 Netflix vs Blockbuster · 10 Nike · 11 Alibaba · 12 IKEA. Next season ideas: Reliance, Huawei, BYD, Zara, Toyota vs Tesla, Starbucks, Jazz, HBL, Emirates, Aramco.

## 11. Channel settings (as configured 21 Nov 2026)

Country Pakistan; 10 channel keywords; audience "not made for kids"; interest-based ads ON; third-party AI training OFF; auto-dubbing ON (no manual review); upload defaults: Private, Education, English (UK), caption certification "never aired on US TV", comments ON (Basic), description template; community moderation: 12 blocked scam phrases (whatsapp me, telegram me, crypto/forex signals, investment manager, bitcoin giveaway, sub4sub…), hold comments with links/hashtags; channel guidelines (welcome + 3 rules); banner, icon, watermark uploaded; contact email set; phone verified (intermediate features); video verification submitted for advanced features (A/B tests, description links, monetization application).

## 12. Monetization roadmap

YPP: 1,000 subscribers + 4,000 public watch hours (12 months) or 10 M Shorts views (90 days). Fan funding tier: 500 subs + 3 uploads + 3,000 hours. Weekly KPIs: subscribers, watch hours, CTR (target 6 %+), average view duration (45 %+), top countries/languages. Weak thumbnail → replace within 48 h.

## 13. Rules that never change

- Never invent figures, quotes or events. Distinguish facts / estimates / interpretation. Sources in every description.
- AI-generated portraits are always labelled "AI ILLUSTRATION"; never realistic depictions of real people.
- Only licensed photos (Wikimedia Commons CC / public domain) with credits.
- Quality over upload frequency. Protect existing approved work: change only what is asked; show short demos of changes.

## 14. Emergency: moving the channel to a new AI or account

1. Download the backup zip from `E:\Empire Stories\_backup\` (or clone the GitHub repo + copy `kok/`).
2. Give the new agent this manual + `MASTER_BRIEF.txt` + the Claude Project instructions text.
3. Install Python deps + ffmpeg; run `setup.sh`; test with `python3 es/ep01/ep01.py info` and a 10-second render.
4. Reconnect upload automation (Zapier YouTube, or manual Studio upload). Keep the publish time, cadence, localization and thumbnail standard.
5. If the YouTube login is compromised: Google account recovery → remove unknown managers → change password → re-enable 2-step verification.
