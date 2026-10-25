# Klik — character pack

A rounded arrow-cursor: the pointer that gets things moving. Klik is about
acting on things — clicks, choices, launches, and the moment an idea gets
selected.

Credit: **Klik by Sketsa** (the built-in mascot).

Style: **riso**
Cutout chroma: **magenta**
Aliases: cursor, pointer

## Locked design

- **Body**: ONE arrow-cursor silhouette (pointer triangle with a curved
  tail), drawn with soft rounded corners everywhere — no sharp points.
  Proportions: body about 1.5× taller than wide, tail a short stub at the
  bottom-right ending in the accent pad.
- **Feet**: two small rounded feet at the base of the body — simple rounded
  shapes, same body color with structure-ink outline.
- **Face**: two small dark dot eyes on the upper half of the arrow body.
  Deadpan and friendly — **no mouth, no eyebrows, no cheeks, ever**.
- **Outline**: every edge carries the structure-ink outline, same weight
  everywhere.
- **Accent**: the tail stub tip is the accent carrier — a small rounded
  patch in the accent color.
- Cuteness comes from roundness and proportion, never from added parts.
- Never add: hands, fingers, gloves, shoes, clothing, hats, headphones,
  wings, sparks, motion lines, pixel trails, eyebrows, mouth, teeth, pupils
  inside the dots, extra cursor arrows, text, logos.

## Interaction model

- Contact surfaces: the flat edges of the arrow body (press, point, push,
  hold); the tail stub (brace, lean).
- Reach: short — it points and presses, it does not grasp.
- Grip: pressure/contact only.
- Support/locomotion: the tail stub and lower body edge; it hops for big
  moves.
- Protected regions: the dot eyes and the accent tail pad must stay visible
  and unchanged in every scene.

## Prompt spec

> the recurring mascot — a rounded arrow-cursor silhouette with soft corners,
> two small rounded feet at its base, a short tail stub ending in a small
> accent-colored rounded patch, two small dark dot eyes on the upper body
> (the only facial features — no mouth, no eyebrows), structure-ink outline
> of even weight on every edge. It MUST perform the move, not decorate.
> {value rule: in every palette, the body stays the light spot with a
> structure-ink outline; the eyes are the darkest notes on the body}

## Value rules

- **All palettes**: light body, structure-ink outline, dark dot eyes. The
  accent pad stays saturated. In dark palettes the scene may go heavy —
  Klik stays the light spot in it.

## Reference sheet

`reference.png` shows Klik front-facing, centered, flat plain background,
no props, no scene, standard riso palette. This sheet is the anchor for
on-model verification.
