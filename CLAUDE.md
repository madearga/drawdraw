# CLAUDE.md — working on this repo

Sketsa is an editorial-illustration agent skill with a character pack
system. The free foundation ships in `skills/sketsa/`; original character
packs are the paid product (separate repo).

## Map

- `skills/sketsa/SKILL.md` — the workflow agents follow. The pipeline:
  spec → generate → on-model verify → gate → deliver.
- `skills/sketsa/scripts/` — `generate.mjs` (the only online script;
  engines: codex via pi → gemini → openrouter → openai), `spec.py`
  (resumable shot matrix), `onmodel.py` (edge-map parity vs reference
  sheet), `gate.py` (final quality gate), `pack.py` (pack manager),
  `pnglib.py` + `make_placeholder.py` (stdlib PNG toolkit).
- `skills/sketsa/characters/` — built-in packs + `PACK-SPEC.md` (the pack
  contract) + `index.json` registry.
- `skills/sketsa/references/` — style guide (styles + palettes) and layout
  playbooks (editorial, flowchart, mini-comic, explainer).
- `tests/` — unittest for every script.

## Commands

```sh
python3 -m unittest discover skills/sketsa/tests
node --check skills/sketsa/scripts/generate.mjs
python3 skills/sketsa/scripts/pack.py list
```

## Conventions

- Python tools: stdlib only, no network, Python 3.8+ compatible.
- The quality gate and the pack spec are contracts; changes to them are
  breaking and must be called out in CHANGELOG.md.
- Every user-visible change bumps `version.txt` + `CHANGELOG.md`.
- Model sheets are ground truth: when a reference.png is replaced, sync the
  pack's character.md and bump the pack version.
