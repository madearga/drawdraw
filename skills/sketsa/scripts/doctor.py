#!/usr/bin/env python3
"""Engine readiness check — what image generation can run right now?

  doctor.py [--skill-dir PATH]

Prints one line per engine (ok / not configured) plus the resolved default
order, and exits 0 when at least one engine is usable.
"""
import json, os, pathlib, shutil, sys

SKILL = pathlib.Path(__file__).resolve().parent.parent


def check_codex():
    auth = pathlib.Path.home() / ".pi/agent/auth.json"
    if not auth.is_file():
        return False, "pi not installed (~/.pi/agent/auth.json missing)"
    try:
        data = auth.read_text()
    except OSError as e:
        return False, f"unreadable: {e}"
    if "openai-codex" not in data:
        return False, "no openai-codex login in pi (run /login in pi)"
    return True, "pi openai-codex login found"


def check_grok():
    home = pathlib.Path(os.environ.get("GROK_HOME") or pathlib.Path.home() / ".grok")
    if not shutil.which("grok"):
        return False, "grok CLI not on PATH"
    if not (home / "auth.json").is_file():
        return False, "grok not logged in (run `grok login`)"
    return True, "grok CLI logged in"


def key_check(env):
    name = env[0]
    if os.environ.get(name):
        return True, f"{name} set"
    return False, f"{name} not set"


def main():
    engines = [
        ("codex", check_codex),
        ("grok", check_grok),
        ("gemini", lambda: key_check(("GEMINI_API_KEY",))),
        ("openrouter", lambda: key_check(("OPENROUTER_API_KEY",))),
        ("openai", lambda: key_check(("OPENAI_API_KEY",))),
    ]
    usable = []
    for name, fn in engines:
        ok, msg = fn()
        print(f"{'ok ' if ok else '—  '} {name}: {msg}")
        if ok:
            usable.append(name)
    if usable:
        print(f"\ndefault engine: {usable[0]}  (fallback order: {' -> '.join(usable)})")
        return 0
    print("\nno engine usable — set one up (see docs/engines.md)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
