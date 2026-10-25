# Character pack spec

A pack is a recurring mascot the skill can draw on-model. It is **data, not
code**: three files and one entry in `index.json`. Follow this contract
exactly — the loader and the verification gate read it.

```
<pack-root>/<name>/
├── character.md   # the brain (structure below)
├── reference.png  # canonical model sheet, square, ≥1024×1024, plain background
└── preview.png    # one finished illustration, for galleries and product pages
```

`index.json` at the pack root:

```json
{
  "packs": [
    {
      "name": "klik",
      "author": "You",
      "version": "1.0.0",
      "description": "One sentence: what it is and what it stands for.",
      "style": "riso",
      "aliases": ["cursor", "pointer"],
      "cutout_chroma": "magenta"
    }
  ]
}
```

- `name` — lowercase, one word, matches the folder name.
- `style` — must be one the style guide knows (see `../references/style-guide.md`).
- `aliases` — alternate names the user may type.
- `cutout_chroma` — a color that never appears in the character, used when a
  transparent cutout is needed.

## character.md structure (required sections, in order)

### 1. Title & identity
Name, one-paragraph personality ("what it stands for"), credit line
(`**<Name> by <Author>**`), style, cutout chroma, aliases.

### 2. Locked design
The physical invariant. Bullet per body part, absolute wording, plus a
`Never add:` list. Rule of thumb: everything a future prompt could get wrong
must be forbidden here in writing. Consistency comes from what you forbid,
not what you allow.

### 3. Interaction model
What surfaces touch the world (`Contact surfaces:`), reach, grip, how it
moves (`Support/locomotion:`), and `Protected regions:` that no scene may
cover or alter.

### 4. Prompt spec
One blockquote paragraph — the exact fragment injected into every generation
prompt, ending with a behavioral rule ("It MUST perform the move, not
decorate."). Keep it under 120 words; detail lives in sections 2–3.

### 5. Value rules
Per-palette invariants: which tones stay light/dark so the character reads in
every palette (e.g. "in dark palettes the character stays the light spot").

### 6. Reference sheet
A note stating what `reference.png` shows: front view, flat plain
background, no props, no scene — the model sheet is the anchor the verifier
compares against.

## Making the model sheet

Generate it with the same engine the skill will use, from the prompt spec
plus locked design, then **curate by hand**: the shipped sheet is the ground
truth for both the model and `onmodel.py`. If you regenerate it later, bump
the pack version.

## Checklist before shipping a pack

- [ ] Folder name == `name` in `index.json`
- [ ] All five sections of `character.md` present, in order
- [ ] `reference.png` ≥1024×1024, square, plain background, no props
- [ ] `preview.png` shows the character mid-action
- [ ] Style name exists in the style guide
- [ ] `python3 ../scripts/onmodel.py reference.png reference.png` prints `1.0`
- [ ] Ten test scenes across three palettes all pass the gate
