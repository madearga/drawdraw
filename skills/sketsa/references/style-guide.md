# Style guide — index

A character pack declares one `style`. Each style lives in its own file in
`styles/` and defines: rendering rules, 2–3 palettes, and composition
guidance. Only styles listed here are valid.

| Style | Look | File |
|---|---|---|
| riso | flat spot-color print poster | [styles/riso.md](styles/riso.md) |
| blueprint | technical drawing linework | [styles/blueprint.md](styles/blueprint.md) |
| pixel | 8/16-bit sprite, hard edges | [styles/pixel.md](styles/pixel.md) |
| chalk | hand-drawn chalkboard | [styles/chalk.md](styles/chalk.md) |
| woodcut | carved high-contrast ink | [styles/woodcut.md](styles/woodcut.md) |
| gouache | opaque painterly poster | [styles/gouache.md](styles/gouache.md) |
| phosphor | glowing CRT terminal | [styles/phosphor.md](styles/phosphor.md) |
| snes | 16-bit console key art | [styles/snes.md](styles/snes.md) |

## Palettes

Every palette has three roles: **paper/background**, **structure ink**
(outlines/linework), and **accents** (2–3 spot colors). The character's
value rules (in its pack) decide which roles stay light/dark so the mascot
reads in every palette. The accent never covers more than ~20% of the frame.

## Adding a style

Add `styles/<name>.md` (rendering rules, 3+ palettes with hexes, one
sentence on composition), then add a row to the table above. Packs may only
reference styles listed here.
