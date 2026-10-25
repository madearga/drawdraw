# Contributing

## Setup

No dependencies to install — the Python tools are stdlib-only (3.8+) and the
adapter runs on Node 18+/Bun.

```sh
python3 -m unittest discover skills/sketsa/tests   # run the tests
node --check skills/sketsa/scripts/generate.mjs    # syntax-check the adapter
```

CI runs both on every push (`.github/workflows/ci.yml`).

## Ground rules

- **Verification scripts stay dependency-free.** No pip installs, no
  network calls in anything under `scripts/` except `generate.mjs`.
- **Every script has a test.** New behavior in `spec.py`/`onmodel.py`/
  `gate.py`/`pack.py` comes with unittest coverage in `tests/`.
- **Character packs follow the spec** — see
  [`skills/sketsa/characters/PACK-SPEC.md`](skills/sketsa/characters/PACK-SPEC.md)
  and run its checklist before shipping a pack.
- **The gate is law.** Anything that weakens the quality gate (lowering
  min_score, skipping verification) needs a very good reason in the PR
  description.
- Bump `version.txt` and `CHANGELOG.md` in the same PR as user-visible
  changes.

## Developing the skill locally

Point your agent at the repo, or symlink the skill into your runtime's
skills folder, then ask for an illustration. Set one of the engines up
first — see [`docs/engines.md`](docs/engines.md).
