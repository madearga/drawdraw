#!/usr/bin/env python3
"""On-model parity: edge-map Dice score between a generated image and the
character's reference sheet. Colors don't matter — structure does.

  onmodel.py generated.png reference.png [--min 0.55]

Prints `score=X.XXX` and exits 0 when the score clears the bar.
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pnglib import to_gray_small

SIZE = 64


def edge_map(gray):
    """Sobel magnitude, binarized at the 70th percentile."""
    n = len(gray)
    mag = [[0.0] * n for _ in range(n)]
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            gx = (-gray[y - 1][x - 1] + gray[y - 1][x + 1]
                  - 2 * gray[y][x - 1] + 2 * gray[y][x + 1]
                  - gray[y + 1][x - 1] + gray[y + 1][x + 1])
            gy = (-gray[y - 1][x - 1] - 2 * gray[y - 1][x] - gray[y - 1][x + 1]
                  + gray[y + 1][x - 1] + 2 * gray[y + 1][x] + gray[y + 1][x + 1])
            mag[y][x] = math.hypot(gx, gy)
    flat = sorted(v for row in mag for v in row)
    cut = flat[int(len(flat) * 0.70)]
    return [[1 if v > cut else 0 for v in row] for row in mag]


def dilate(m):
    n = len(m)
    out = [[0] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            out[y][x] = 1 if any(
                m[yy][xx]
                for yy in range(max(0, y - 1), min(n, y + 2))
                for xx in range(max(0, x - 1), min(n, x + 2))) else 0
    return out


def score(a_path, b_path):
    a = edge_map(to_gray_small(a_path, SIZE))
    b = edge_map(to_gray_small(b_path, SIZE))
    bd = dilate(b)
    inter = sum(1 for y in range(SIZE) for x in range(SIZE) if a[y][x] and bd[y][x])
    total = sum(sum(r) for r in a) + sum(sum(r) for r in b)
    return 2 * inter / total if total else 0.0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--min"]
    minimum = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 0.55
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    s = score(args[0], args[1])
    print(f"score={s:.3f} min={minimum:.2f} {'PASS' if s >= minimum else 'FAIL'}")
    sys.exit(0 if s >= minimum else 1)
