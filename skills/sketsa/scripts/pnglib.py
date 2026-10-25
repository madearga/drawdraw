"""Minimal PNG encode/decode (8-bit RGB/RGBA) — stdlib only, so every
verification tool runs with no pip installs."""
import struct, zlib


def encode_png(width, height, rows):
    """rows: list of `height` lists of `width` (r, g, b[, a]) tuples."""
    has_alpha = any(len(px) == 4 for row in rows for px in row)
    bpp = 4 if has_alpha else 3
    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter: none
        for px in row:
            raw.extend(px[:bpp])
    return _chunks(width, height, bytes(raw), bpp)


def _chunks(width, height, raw, bpp):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    color = 6 if bpp == 4 else 2
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def write_png(path, width, height, rows):
    with open(path, "wb") as f:
        f.write(encode_png(width, height, rows))


def decode_png(path):
    """Returns (width, height, rows) with rows of (r, g, b, a) tuples."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat, meta = 8, bytearray(), None
    while pos < len(data):
        (length,) = struct.unpack_from(">I", data, pos)
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack_from(">IIBB", body)
            meta = (w, h, depth, ctype)
        elif tag == b"IDAT":
            idat.extend(body)
        pos += 12 + length
    w, h, depth, ctype = meta
    if depth != 8 or ctype not in (2, 6):
        raise ValueError(f"{path}: need 8-bit RGB or RGBA, got depth={depth} ctype={ctype}")
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = w * bpp
    out, prev = [], bytes(stride)  # spec: filters on row 0 see a zero row
    for y in range(h):
        line = bytearray(raw[y * (stride + 1):(y + 1) * (stride + 1)])
        ftype, line = line[0], line[1:]
        if ftype == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        prev = line
        row = []
        for x in range(w):
            o = x * bpp
            px = tuple(line[o:o + bpp])
            row.append(px if bpp == 4 else (px[0], px[1], px[2], 255))
        out.append(row)
    return w, h, out


def to_gray_small(path, size=64):
    """Decode, composite over white, box-downsample to `size`×`size` gray floats."""
    w, h, rows = decode_png(path)
    cell_w, cell_h = w / size, h / size
    small = []
    for sy in range(size):
        row = []
        for sx in range(size):
            x0, x1 = int(sx * cell_w), max(int((sx + 1) * cell_w), int(sx * cell_w) + 1)
            y0, y1 = int(sy * cell_h), max(int((sy + 1) * cell_h), int(sy * cell_h) + 1)
            n = t = 0
            for y in range(y0, min(y1, h)):
                for x in range(x0, min(x1, w)):
                    r, g, b, a = rows[y][x]
                    lum = (0.299 * r + 0.587 * g + 0.114 * b)
                    t += (a / 255) * lum + (1 - a / 255) * 255
                    n += 1
            row.append(t / max(n, 1))
        small.append(row)
    return small
