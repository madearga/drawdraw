# Security policy

## Reporting

Report vulnerabilities privately to the maintainer (GitHub Security
Advisory on this repo, or the email on the profile). Do not open a public
issue for anything exploitable.

## Scope and design notes

- The only script that performs network calls is
  `skills/sketsa/scripts/generate.mjs`, and only to the image endpoints of
  the configured engine (generativelanguage.googleapis.com,
  api.openai.com, openrouter.ai) or to the local `pi` CLI.
- API keys are read from the environment (`GEMINI_API_KEY`,
  `OPENAI_API_KEY`, `OPENROUTER_API_KEY`) and are never logged, echoed, or
  written to disk by any script. The Codex engine uses the user's existing
  `pi` ChatGPT login and never sees the token itself.
- Everything a run produces lands in `illo-build/` inside the user's
  project; nothing is uploaded anywhere by the skill itself.
- Python verification tools are stdlib-only on purpose: no dependency
  supply chain.

## Known limitations

- The Codex engine drives `pi` non-interactively; image requests pass
  through the Codex backend's own prompt handling. Treat prompts as
  user-controlled content and do not concatenate untrusted text into
  commands.
