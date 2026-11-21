# EMPIRE STORIES — production engine

**The stories behind global empires.**
Business documentaries about how the world's companies were built, told Netflix-style with Vox-style visual explanation.

This repository holds everything needed to produce an episode from a cloud session: the render engine, brand system, map data, licensed product photos, the narration voice blend and the episode files. Finished videos are **not** stored here (they live in `E:\Empire Stories\EpXXX\render` and the synced Drive folder).

## Quick start (new session)
```bash
git clone https://github.com/GhazanfarGw/empire-stories
bash empire-stories/setup.sh
cd /home/claude/es/tl3
python3 tl3.py info                 # timing of every beat
python3 tl3.py stills 5,42,114      # QC frames -> es/out/_tl3.jpg
python3 audio4.py                   # music + SFX + voice tracks
python3 tl3.py part 0 40            # render a part (run parts in parallel), then concat + mux
```

## Layout
| Path | What it is |
|---|---|
| `es/es_demo.py, es_seg2.py, es_v3.py, es_v4.py` | Core drawing toolkit (text, labels, highlights, stamps, traces, brand helpers) |
| `es/paper.py` | Grey page background + thin torn-paper edges that hug each image's shape |
| `es/geo.py` | TopoJSON decoder, Albers projection, animated brand maps |
| `es/data/geo/` | US Census boundaries (us-atlas) + world-atlas, ISC licence |
| `es/assets/` | Licensed product/building photos, see `CREDITS.txt`. `assets/people/` = owner-supplied portraits (`first-last.jpg`) |
| `es/tl3/tl3.py` | Episode renderer: cold open → ident → composed timeline (rolling year counter, red travel line, pin shockwave) → map → OUR TAKE → end screen |
| `es/tl3/gen3.py` | Narration: Kokoro British blend (75% bm_lewis + 25% bm_george), one wav per sentence |
| `es/tl3/audio4.py` | Sound design: signature ident chime, quiet ambient bed, micro-SFX (pops, zips, counter ticks, thumps) |
| `es/vt/lewis_blend.npy` | The channel voice |
| `docs/` | Master brief, Ep001 description/sources |

## Brand (current)
- Navy `#0A3161` · Red `#B31942` · page grey `#D6D5D1` · ivory `#F4F1EA`
- No burnt-in subtitles (SRT for YouTube CC)
- Every rising/falling number counts with calculator ticks; every element pops in with sound
- Founder photos are owner-supplied; otherwise a clearly labelled illustration card

## Workflow
Topic → research fact sheet (sourced) → script (approved) → assets → voice → render → sound → QC → MP4 + SRT + description + thumbnail + Shorts → E:\ + Drive → YouTube **private** → owner approves → public.
