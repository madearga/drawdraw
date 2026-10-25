# Character builder

A guided flow for creating a NEW character pack from scratch (user says
"create a character" / "make me a mascot"). You drive; the user approves
at the two gates.

## Step 1 — Concept (gate 1)

Propose, in one short list: 3 name+concept pairs fitted to the user's
domain. A pair is: **Name** (one word, reads off the design), what it is
(one object/creature), what it stands for (one dev/startup theme), and a
style from the style guide that fits. Example shape:

- **Ganti** — a chameleon that adapts: refactors, migrations, A/B switches
  (gouache)
- **Cache** — a squirrel that never loses an acorn: warm starts, prepared
  state (woodcut)

The user picks one or hands over their own. Nothing is generated yet.

## Step 2 — Design the spec

Write the full `character.md` following `../characters/PACK-SPEC.md`
sections in order. The Locked design section is where the character is
won or lost:

- Describe every body part with absolute wording; proportions explicit.
- Build the `Never add:` list adversarially — everything a prompt could
  get wrong.
- Keep a `Protected regions:` list for anything that must stay visible.

Present the spec to the user. On approval → gate 2 passed.

## Step 3 — Model sheet

- Compose the sheet prompt: style rendering rules + Prompt spec blockquote
  + "front-facing, centered, flat plain background, no props, no scene"
- Generate via the normal pipeline (`generate.mjs`, no reference image —
  this is the first image of the character).
- **Curate by hand**: look at it. If the face/expression is charming and
  the design is clean, it ships. Otherwise regenerate with a tightened
  prompt (up to 3 tries), then pick the best.

## Step 4 — Verify and register

- Generate one action preview with the sheet as reference (the edit path
  also proves on-model consistency holds).
- Score it: `onmodel.py preview.png reference.png` — record the score in
  the pack's notes; a low score means the sheet is ambiguous, fix the
  spec first.
- Complete the PACK-SPEC checklist, register in `index.json`, install
  with `pack.py install`, set default if the user wants.

## Rules

- The design must be original — never derive from an existing pack's
  mascot, and never imitate recognizable mascots from other products.
- Sheets are ground truth: whatever ships as reference.png is what
  character.md describes, never the reverse.
