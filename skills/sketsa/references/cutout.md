# Cutouts (transparent backgrounds)

When the user asks for a sticker/transparent/PNG-alpha result:

1. **Pick a key-capable engine.** gemini, openrouter, and openai return
   alpha-capable images; codex and grok do not. The chroma-key method
   below works on every engine, so the default is: chroma route on
   subscription engines, native alpha on key engines.
2. **Add to the prompt**: the scene background is a single flat chroma
   color `#FF00FF` (magenta), edge-to-edge, with nothing else in it. The
   chroma never appears on the character (packs declare `cutout_chroma`).
3. **Generate** as usual (reference sheet included).
4. **Cut**:
   `python3 $SKILL/scripts/cutout.py illo-build/<file> illo-build/<file>-cut.png --chroma FF00FF`
5. **Check**: open the result — if halo pixels remain around edges,
   re-run with `--tolerance 120`. Record the cut file in shots.csv as a
   note (`<file>-cut.png`); the gate still scores the original.

## Notes

- Magenta is the default key because no built-in mascot uses it. A pack
  whose design contains magenta must declare a different `cutout_chroma`.
- The flood-fill starts from the borders only, so chroma-colored details
  inside the character survive.
- Cut outputs are deliverables, not gate inputs — the gate checks the
  original render.
