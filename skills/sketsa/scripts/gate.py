#!/usr/bin/env python3
"""Quality gate — the last check before anything is shown to the user.

  gate.py [build-dir]

Fails (exit 1) unless every shot is `pass` with a real PNG on disk and a
parity score at or above spec.json's min_score. Prints a per-shot report.
"""
import csv, json, pathlib, sys, struct, zlib

BUILD = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "illo-build")


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main():
    problems = []
    spec = json.loads((BUILD / "spec.json").read_text())
    minimum = float(spec.get("min_score", 0.55))
    with open(BUILD / "shots.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        problems.append("shots.csv is empty")
    gens = 0
    for r in rows:
        sid = r["id"]
        if r["status"] != "pass":
            problems.append(f"{sid}: status={r['status']} (needs pass)")
            continue
        img = BUILD / r["file"]
        if not img.exists():
            problems.append(f"{sid}: missing {r['file']}")
            continue
        try:
            w, h = png_size(img)
        except Exception as e:
            problems.append(f"{sid}: unreadable image ({e})")
            continue
        if w < 512 or h < 512:
            problems.append(f"{sid}: {w}x{h} too small")
        try:
            if float(r["score"]) < minimum:
                problems.append(f"{sid}: score {r['score']} < {minimum}")
        except ValueError:
            problems.append(f"{sid}: no parity score recorded")
        gens += int(r["tries"] or 0)
    print(f"gate: {len(rows)} shots, min_score={minimum}, {gens} generation(s)")
    for r in rows:
        print(f"  {r['id']}\t{r['status']}\tscore={r['score'] or '-'}\t{r['file']}")
    if problems:
        print("\nGATE FAILED:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("GATE PASSED")


if __name__ == "__main__":
    main()
