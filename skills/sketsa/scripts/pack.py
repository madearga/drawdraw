#!/usr/bin/env python3
"""Character pack manager for Sketsa.

  pack.py list                    # every installed pack (builtin + installed)
  pack.py install <path> [--dev]  # copy a pack dir in; paid packs need a license
                                  # (or --dev while developing)
  pack.py default [NAME]          # show or set the default character
  pack.py resolve <name-or-alias> # print the canonical pack dir (TSV: dir style)

A pack is a folder with character.md + reference.png (+ preview.png) and an
index.json at its repo root describing it. Built-ins live in characters/,
installed packs in characters/packs/<name>/. The default character is stored
in settings.json next to this script.
"""
import json, pathlib, shutil, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import license as licensing

SKILL = pathlib.Path(__file__).resolve().parent.parent
CHARACTERS = SKILL / "characters"
PACKS = CHARACTERS / "packs"
SETTINGS = SKILL / "settings.json"


def load_index(root):
    f = root / "index.json"
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text()).get("packs", [])
    except json.JSONDecodeError as e:
        print(f"warning: bad index.json in {root}: {e}", file=sys.stderr)
        return []


def all_packs():
    """Returns list of (meta, dir). Built-ins first, then installed packs."""
    out = []
    for meta in load_index(CHARACTERS):
        d = CHARACTERS / meta["name"]
        if d.is_dir():
            out.append((meta, d))
    if PACKS.is_dir():
        for meta in load_index(PACKS):
            d = PACKS / meta["name"]
            if d.is_dir():
                out.append((meta, d))
    return out


def read_default():
    if SETTINGS.exists():
        try:
            return json.loads(SETTINGS.read_text()).get("default_character")
        except json.JSONDecodeError:
            return None
    return None


def resolve(name_or_alias):
    want = (name_or_alias or "").strip().lower()
    if not want:
        want = read_default() or "klik"
    packs = all_packs()
    for meta, d in packs:  # exact name wins, built-ins before packs
        if meta["name"].lower() == want:
            return meta, d
    for meta, d in packs:  # then aliases
        if want in [a.lower() for a in meta.get("aliases", [])]:
            return meta, d
    return None, None


def cmd_list(_):
    default = read_default()
    for meta, d in all_packs():
        star = " *" if meta["name"] == default else ""
        aliases = ", ".join(meta.get("aliases", []))
        print(f"{meta['name']}{star}\t{meta.get('style', '?')}\tv{meta.get('version', '?')}\t"
              f"{meta.get('author', '?')}\t{aliases}\t{d}")


def find_pack_meta(index_root, pack_name):
    for meta in load_index(index_root):
        if meta["name"] == pack_name:
            return meta
    return None


def cmd_install(args):
    dev = "--dev" in args
    args = [a for a in args if a != "--dev"]
    src = pathlib.Path(args[0]).expanduser().resolve()
    if not src.is_dir():
        sys.exit(f"not a directory: {src}")
    # Accepted shapes:
    #  a) repo root: index.json + packs/<name>/ (illo-characters layout)
    #  b) self-listing pack dir: character.md + index.json describing itself
    #  c) bare pack dir: character.md, with index.json in the parent listing it
    if load_index(src) and (src / "packs").is_dir():
        targets = [(m, src / "packs" / m["name"]) for m in load_index(src)]
    elif (src / "character.md").exists() and (src / "index.json").exists():
        metas = [m for m in load_index(src) if m["name"] == src.name]
        if not metas:
            sys.exit(f"{src}/index.json does not describe a pack named '{src.name}'")
        targets = [(metas[0], src)]
    elif (src / "character.md").exists():
        # bare pack dir: look upward for an index.json that lists it
        meta = None
        ancestor = src.parent
        for _ in range(3):
            if (ancestor / "index.json").exists():
                meta = find_pack_meta(ancestor, src.name)
                if meta:
                    break
            if ancestor.parent == ancestor:
                break
            ancestor = ancestor.parent
        if not meta:
            sys.exit(f"no index.json describing pack '{src.name}' above {src}")
        targets = [(meta, src)]
    else:
        sys.exit(f"no installable pack in {src} (need index.json + character.md)")
    PACKS.mkdir(parents=True, exist_ok=True)
    for meta, pack_dir in targets:
        if meta.get("paid") and not dev and not licensing.entitled():
            sys.exit(f"pack '{meta['name']}' is a paid pack. Activate a license first:\n"
                     f"  license.py activate <key> --provider gumroad --product <id>\n"
                     f"Buy packs at the Sketsa store (see SKILL.md / the repo README). "
                     f"Developing your own? pass --dev.")
        if not (pack_dir / "character.md").exists() or not (pack_dir / "reference.png").exists():
            sys.exit(f"{pack_dir}: missing character.md or reference.png")
        dest = PACKS / meta["name"]
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(pack_dir, dest)
        # keep the pack's own index entry so resolve works after install
        idx_dest = PACKS / "index.json"
        data = [m for m in load_index(PACKS) if m["name"] != meta["name"]] + [meta]
        idx_dest.write_text(json.dumps({"packs": data}, indent=2) + "\n")
        print(f"installed {meta['name']} v{meta.get('version', '?')} -> {dest}")


def cmd_default(args):
    if not args:
        print(read_default() or "(none, klik is the fallback)")
        return
    meta, d = resolve(args[0])
    if not meta:
        sys.exit(f"unknown character or alias: {args[0]}")
    SETTINGS.write_text(json.dumps({"default_character": meta["name"]}, indent=1) + "\n")
    print(f"default character: {meta['name']}")


def cmd_resolve(args):
    meta, d = resolve(args[0] if args else None)
    if not meta:
        sys.exit(f"unknown character or alias: {args[0] if args else '(default)'}")
    print(f"{d}\t{meta.get('style', 'riso')}")


if __name__ == "__main__":
    cmds = {"list": cmd_list, "install": cmd_install,
            "default": cmd_default, "resolve": cmd_resolve}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    cmds[sys.argv[1]](sys.argv[2:])
