"""Draws the placeholder model sheet for a character with pure geometry —
no image API needed. Replace with a real generated sheet before shipping."""
import math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pnglib import write_png

SIZE = 1024
PAPER = (245, 239, 224, 255)     # cream riso paper
INK = (43, 43, 51, 255)          # structure ink (charcoal)
BODY = (253, 248, 236, 255)      # light body
ACCENT = (255, 108, 47, 255)     # riso orange


def dist_to_segment(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def in_poly(px, py, pts):
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def rounded_polygon_dist(px, py, pts, r):
    """Signed distance: negative inside the polygon, extended by radius r
    (rounds convex corners)."""
    d = min(dist_to_segment(px, py, *pts[i], *pts[(i + 1) % len(pts)])
            for i in range(len(pts)))
    if in_poly(px, py, pts):
        return -d if d > r else d - r
    return d - r


# Cursor silhouette, normalized coords (tip up-left like a real pointer)
CURSOR = [(0.40, 0.08), (0.68, 0.48), (0.545, 0.515), (0.615, 0.70),
          (0.545, 0.735), (0.475, 0.55), (0.40, 0.60)]
SCALE = SIZE * 0.62
OFF = SIZE * 0.16
pts = [(OFF + x * SCALE, OFF + y * SCALE) for x, y in CURSOR]
R = SIZE * 0.045      # corner rounding
OUT = SIZE * 0.016    # outline thickness


def draw(preview=False):
    rows = []
    bg = ACCENT if preview else PAPER
    cx, cy = SIZE * 0.42, SIZE * 0.78
    pad_w, pad_h = SIZE * 0.115, SIZE * 0.055
    for y in range(SIZE):
        row = []
        for x in range(SIZE):
            if preview:
                d = math.hypot(x - SIZE / 2, y - SIZE / 2)
                c = tuple(round(bg[i] * (1 - 0.10 * d / (SIZE / 2))) for i in range(3)) + (255,)
            else:
                c = bg
            # shadow
            if math.hypot(x - cx, (y - cy) * 2.6) < SIZE * 0.24:
                c = tuple(round(v * 0.93) for v in c[:3]) + (255,)
            d = rounded_polygon_dist(x, y, pts, R)
            if d <= 0:
                c = INK if d > -OUT else BODY
            # accent click pad capping the tail stub (bottom of the shape)
            if (abs(x - SIZE * 0.52) < pad_w / 2 and abs(y - SIZE * 0.66) < pad_h / 2):
                c = ACCENT
            # dot eyes on the upper body
            for ex, ey in ((SIZE * 0.445, SIZE * 0.33), (SIZE * 0.515, SIZE * 0.31)):
                if math.hypot(x - ex, y - ey) < SIZE * 0.022:
                    c = INK
            row.append(c)
        rows.append(row)
    return rows


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "reference.png")
    write_png(out, SIZE, SIZE, draw(preview="--preview" in sys.argv))
    print(f"wrote {out}")
