#!/usr/bin/env python3
"""Shot matrix for an illustration run — the resumable state.

Usage (from the project dir):
  spec.py init --character klik [--brief brief.md] [--scenes "a; b; c"]
  spec.py next                       # print first pending shot as TSV
  spec.py set <id> <status> [score]  # status: pending|generated|pass|failed
  spec.py list                       # print the whole matrix
State lives in ./illo-build/ (shots.csv + spec.json + prompts/ + shots/).
"""
import csv, json, pathlib, sys, time

BUILD = pathlib.Path("illo-build")
FIELDS = ["id", "concept", "palette", "status", "file", "score", "tries"]
VALID = {"pending", "generated", "pass", "failed"}


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def save_rows(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def scenes_from_brief(text):
    """Bullet lines become shots; otherwise the whole brief is one shot."""
    bullets = [ln.lstrip("-*• ").strip() for ln in text.splitlines()
               if ln.strip().startswith(("-", "*", "•"))]
    return bullets or [text.strip()]


def cmd_init(args):
    if BUILD.exists() and any(BUILD.iterdir()) and "--force" not in args:
        sys.exit("illo-build/ already exists — resume it, or pass --force")
    BUILD.mkdir(exist_ok=True)
    brief = ""
    brief_path = args[args.index("--brief") + 1] if "--brief" in args else None
    if brief_path:
        brief = pathlib.Path(brief_path).read_text()
    if "--scenes" in args:
        scenes = [s.strip() for s in args[args.index("--scenes") + 1].split(";") if s.strip()]
    elif brief:
        scenes = scenes_from_brief(brief)
    else:
        scenes = ["single illustration from the user's request"]
    character = args[args.index("--character") + 1] if "--character" in args else "klik"
    spec = {"character": character, "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "brief": brief.strip()[:2000], "min_score": 0.55, "max_tries": 3}
    (BUILD / "spec.json").write_text(json.dumps(spec, indent=1))
    rows = [{"id": f"s{i + 1:02d}", "concept": s, "palette": "default",
             "status": "pending", "file": f"shots/{sid}.png", "score": "", "tries": 0}
            for i, (sid, s) in enumerate(zip([f"s{i + 1:02d}" for i in range(len(scenes))], scenes))]
    save_rows(BUILD / "shots.csv", rows)
    (BUILD / "prompts").mkdir(exist_ok=True)
    (BUILD / "shots").mkdir(exist_ok=True)
    (BUILD / "brief.md").write_text(brief)
    print(f"initialized: {len(rows)} shot(s), character={character}")


def cmd_next(_):
    rows = load_rows(BUILD / "shots.csv")
    pending = [r for r in rows if r["status"] in ("pending", "failed")]
    if not pending:
        print("none")
        return
    r = pending[0]
    print("\t".join([r["id"], r["concept"], r["palette"], r["file"], r["tries"]]))


def cmd_set(args):
    sid, status = args[0], args[1]
    if status not in VALID:
        sys.exit(f"status must be one of {sorted(VALID)}")
    rows = load_rows(BUILD / "shots.csv")
    for r in rows:
        if r["id"] == sid:
            r["status"] = status
            if len(args) > 2:
                r["score"] = args[2]
            if status in ("generated", "pass", "failed"):
                r["tries"] = str(int(r["tries"] or 0) + (1 if status == "generated" else 0))
            save_rows(BUILD / "shots.csv", rows)
            return
    sys.exit(f"unknown shot id: {sid}")


def cmd_list(_):
    for r in load_rows(BUILD / "shots.csv"):
        print(f"{r['id']}\t{r['status']}\t{r['score'] or '-'}\t{r['concept'][:60]}")


if __name__ == "__main__":
    cmds = {"init": cmd_init, "next": cmd_next, "set": cmd_set, "list": cmd_list}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    cmds[sys.argv[1]](sys.argv[2:])
