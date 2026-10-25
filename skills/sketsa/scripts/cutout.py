#!/usr/bin/env python3
"""Chroma-key cutout: turn a flat chroma background into transparency.

  cutout.py input.png output.png [--chroma FF00FF] [--tolerance 90]

Flood-fills from the image borders so chroma-colored parts INSIDE the
character survive. Edges get one feathered pixel. Stdlib only.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pnglib import decode_png, write_png


def hex_to_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def cutout(rows, chroma, tolerance):
    h, w = len(rows), len(rows[0])
    tol2 = tolerance * tolerance

    def close(px):
        dr = px[0] - chroma[0]
        dg = px[1] - chroma[1]
        db = px[2] - chroma[2]
        return dr * dr + dg * dg + db * db <= tol2

    alpha = [[255] * w for _ in range(h)]
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if close(rows[y][x]) and alpha[y][x]:
                stack.append((y, x)); alpha[y][x] = 0
    for y in range(h):
        for x in (0, w - 1):
            if close(rows[y][x]) and alpha[y][x]:
                stack.append((y, x)); alpha[y][x] = 0
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and alpha[ny][nx] and close(rows[ny][nx]):
                alpha[ny][nx] = 0
                stack.append((ny, nx))
    # feather: one soft pixel where transparent meets opaque
    soft = [row[:] for row in alpha]
    for y in range(h):
        for x in range(w):
            if alpha[y][x]:
                near = sum(1 for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                           if 0 <= ny < h and 0 <= nx < w and alpha[ny][nx] == 0)
                if near:
                    soft[y][x] = 128
    return [[(px[0], px[1], px[2], soft[y][x]) for x, px in enumerate(row)]
            for y, row in enumerate(rows)]


if __name__ == "__main__":
    argv = sys.argv[1:]
    vals, args, i = {}, [], 0
    while i < len(argv):
        if argv[i].startswith("--"):
            name = argv[i][2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                vals[name] = argv[i + 1]
                i += 2
            else:
                i += 1
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    chroma = hex_to_rgb(vals.get("chroma", "FF00FF"))
    tol = int(vals.get("tolerance", "90"))
    w, h, rows = decode_png(args[0])
    write_png(args[1], w, h, cutout(rows, chroma, tol))
    print(f"cutout: {args[1]} (chroma #{'%02X%02X%02X' % chroma}, tol {tol})")
