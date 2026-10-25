# Prompt recipe

The full generation prompt is assembled in this order. Keep the whole
prompt under 250 words — every token competes with the character spec.

```
1. Style opening        1–2 sentences from styles/<style>.md rendering rules
2. Character block      the pack's Prompt spec, verbatim (value rule kept)
3. Scene                what the mascot is doing, where, with which props
4. Layout               framing from references/layouts.md
5. Palette              the palette's paper/ink/accent hexes
6. Closure              "It MUST perform the move, not decorate." + negatives
```

## Rules

- The character block is never paraphrased — it is the on-model anchor and
  the same wording goes into every image of the run.
- Negatives at the end repeat only the Locked-design items most likely to
  break in THIS scene (a scene with speech → repeat "no text"; a seated
  scene → repeat the leg rules).
- Reference images are passed to the engine separately (the adapter does
  this); never paste a reference image path into the prompt text except
  for the grok engine, where the path is part of the instruction.
- One retry = one meaningful change: tighten a negative, simplify the
  scene, or change the composition — never shuffle the same words.
