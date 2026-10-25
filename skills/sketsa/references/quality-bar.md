# Quality bar

Every image must clear this before the gate runs. The bar is what separates
"AI drew something" from "this looks intentional".

## The five checks

1. **The mascot performs.** It is mid-action — pressing, inspecting,
   carrying, failing — never floating as a sticker. If you can't say what
   it's doing in one verb, the scene has no idea in it.
2. **One idea per frame.** A single metaphor, one focal point. Two ideas
   make an infographic, not an illustration.
3. **On-model or out.** Locked design holds: no added facial features, no
   extra accessories, proportions intact. `onmodel.py` scores structure;
   you enforce the rules.
4. **The style is obeyed, not suggested.** Flat styles stay flat; pixel
   styles stay hard-edged. A gouache gradient in a riso image is a fail.
5. **Restraint.** Fewer props, fewer colors, more negative space. When in
   doubt, remove one element and re-check.

## Common failure modes (regenerate on sight)

- Mascot with a vacant sticker smile doing nothing
- Arms/hands with the wrong count for the species
- Props so many the mascot disappears
- A gradient sneaking into a flat style
- Backgrounds busier than the subject
