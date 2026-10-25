# Engines

`generate.mjs` picks the first engine available, in this order:

| # | Engine   | Needs                                  | Cost                | Reference images | Notes |
|---|----------|----------------------------------------|---------------------|------------------|-------|
| 1 | codex    | `pi` CLI logged into ChatGPT (Codex)   | your plan's quota   | yes (up to 5)    | gpt-image-2.5 via the `imagegen` tool; saves to `<workspace>/.pi/openai-codex-images/` |
| 2 | grok     | `grok` CLI logged in (`~/.grok/`)      | your plan's quota   | yes (by path)    | built-in `image_gen`/`image_edit` via `grok -p`; returns JPEG (converted with `sips`); no alpha |
| 3 | gemini   | `GEMINI_API_KEY`                       | ~$0.02–0.04/image   | yes (inline)     | `gemini-2.5-flash-image` — best character consistency per dollar |
| 4 | openrouter | `OPENROUTER_API_KEY`                 | per model           | yes (data URL)   | one key, many models (`OPENROUTER_IMAGE_MODEL`, default `google/gemini-2.5-flash-image`) |
| 5 | openai   | `OPENAI_API_KEY`                       | ~$0.08–0.19/image   | yes (images/edits)| `gpt-image-1` via `/v1/images/edits` |

## Grok engine details

Mirrors illo's grok backend: `grok -p "<prompt + tool instructions>"
--always-approve --sandbox workspace --cwd <shot dir>`. The prompt tells the
agent to use its built-in `image_gen`/`image_edit` tool (reference images are
passed as filesystem paths inside the prompt — there is no `-i` flag), save
to the exact output path, and never build the image with code. Verify-first:
if the CLI didn't write the file, the freshest image newer than run start
under `~/.grok/sessions/**/images/` is used. The sandbox keeps the
auto-approved agent's writes confined to cwd/tmp/`~/.grok`. Grok returns
JPEG with no alpha, so it is never used for transparent cutouts.

Override with `--engine <name>`. Model overrides: `GEMINI_IMAGE_MODEL`,
`OPENROUTER_IMAGE_MODEL`, `OPENAI_IMAGE_MODEL`.

Force the engine in the skill by passing `--engine` through from SKILL.md's
generate step; otherwise leave it on `auto`.

## Codex engine details

The codex engine spawns `pi -p --mode text` and instructs the session to
call the `imagegen` tool exactly once with the prompt (plus `referenced_image_paths`
for edits). It then picks the newest image in `<workspace>/.pi/openai-codex-images/`
(the workspace is the nearest `.git` parent of the cwd) and converts to PNG
with `sips` if the backend returned jpeg/webp. Sessions that end without an
image are retried up to 3 times — the codex backend occasionally refuses
silently.
