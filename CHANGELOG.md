# Changelog

All notable changes to Sketsa are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is
semver.

## [0.3.1] - 2026-10-25

### Added
- **Monetization layer** — `scripts/license.py` (Gumroad + Lemon Squeezy
  activation, entitlement in `~/.sketsa/entitlement.json`), a `paid` gate in
  `pack.py install` (`--dev` bypass for development), `store.json` for the
  in-agent upsell, and `docs/monetize.md` — the full store setup and launch
  playbook.
- SKILL.md upsell now names a concrete pack with its real store link and
  the two activation commands.

## [0.3.0] - 2026-10-25

### Added
- **Cutouts** — transparent sticker renders on any engine: chroma-key
  background in the prompt + `scripts/cutout.py` (border flood-fill with
  feathered edges, subject-internal chroma survives). Validated end-to-end
  with a real codex render.
- **Character builder** — guided flow (two user gates) from concept to an
  installed pack (`references/character-builder.md`).
- **Quality bar + prompt recipe** — the aesthetic checklist and the exact
  prompt assembly order as references, wired into SKILL.md.
- **Surprise mode** — `/sketsa surprise` picks a specific dev moment from
  two curated tables.
- **Doctor** — `scripts/doctor.py` prints per-engine readiness and the
  resolved fallback order; preflight now runs it.
- **Four new styles** — woodcut, gouache, phosphor, snes (8 total), each in
  its own `references/styles/<name>.md` like illo.
- **Diagram routing rule** — architecture/ERD/chart requests build SVG/
  Mermaid in code instead of image generation.

### Changed
- style-guide.md is now an index; per-style content lives in
  `references/styles/`.

## [0.2.1] - 2026-10-25

### Added
- **Grok engine** — free image generation through the user's Grok (xAI) CLI
  subscription (`grok -p`, built-in `image_gen`/`image_edit` tools), mirroring
  illo's grok backend: sandboxed auto-approve single-turn run, verify-first
  output, freshest-session-image fallback, JPEG-to-PNG conversion via `sips`.
  Engine order is now: codex > grok > gemini > openrouter > openai.

## [0.2.0] - 2026-10-25

### Added
- **Codex engine** — free image generation through the user's ChatGPT
  (Codex) login via the `pi` CLI's `imagegen` tool; now the default engine
  when available.
- **OpenRouter engine** — one key, many image models; the catch-all when no
  subscription or first-party key exists. Engine order: codex → gemini →
  openrouter → openai.
- **Character pack manager** (`scripts/pack.py`): list, install, set
  default, and resolve packs by name or alias.
- **New styles**: blueprint, pixel, chalk (each with 2–3 palettes).
- **New layout**: explainer (how-it-works cutaway).
- Multi-runtime plugin packaging: Claude Code (plugin + marketplace), Codex,
  Cursor, Gemini CLI, Grok, and `.agents` marketplace.
- Repo meta: CHANGELOG, version.txt, CONTRIBUTING, SECURITY, CI workflow.

### Changed
- Klik's model sheet is now a real generated image (was a geometric
  placeholder); character.md synced to it. Pack version 0.1.1.
- PNG decoder handles row-0 "up" filters (as emitted by gpt-image backends).

## [0.1.0] - 2026-10-25

### Added
- Foundation: SKILL.md pipeline (spec → generate → verify → gate), shot
  matrix with resumable runs (`spec.py`), edge-map on-model parity
  (`onmodel.py`), quality gate (`gate.py`), dual-engine adapter
  (`generate.mjs`: Gemini + OpenAI).
- Built-in mascot **Klik** (riso) with the character pack spec
  (`characters/PACK-SPEC.md`).
- Unit tests for every script (stdlib-only Python tools).
