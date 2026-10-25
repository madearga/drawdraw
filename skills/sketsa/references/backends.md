# Backends and engines

Full details live in [`../../docs/engines.md`](../../docs/engines.md) —
that table is the source of truth (needs, cost, reference-image support,
and per-engine notes).

Quick order for prompt assembly decisions:

1. **codex** — pi + ChatGPT (Codex) login; free on the plan; gpt-image-2.5.
2. **grok** — Grok CLI login; free on the plan; JPEG (no alpha).
3. **gemini** — `GEMINI_API_KEY`; cheapest per image; best consistency/$.
4. **openrouter** — `OPENROUTER_API_KEY`; one key, many models.
5. **openai** — `OPENAI_API_KEY`; gpt-image-1.

Engine readiness is checked by `scripts/doctor.py` (preflight). Engines
that bill per image are only chosen when no subscription engine is
available — matches illo's "free subscription first" posture.
