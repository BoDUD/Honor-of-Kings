"""Pixel-art toolkit for the HoK sprites: palette grids, layered parts, RotSprite, sheets.

Parts are hand-placed pixel grids (one character per pixel, see PAL) with a pivot. Frames are
built by placing parts, never by drawing lines or shapes, so every body pixel is authored.
Rotation uses RotSprite (Scale2x x3, rotate, sample) so rotated weapons keep clean pixel lines.
"""
import json
import math
import os

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------------- palette
# Arthur, default skin: golden blond hair, gold + silver plate, red cape, navy underlayer.
PAL = {
    "k": (16, 11, 18),      # outline / deepest shadow
    "K": (48, 30, 34),      # soft inner line
    # skin
    "a": (255, 226, 198), "b": (240, 182, 146), "c": (192, 120, 96),
    # eyes
    "e": (84, 170, 255), "q": (26, 48, 118), "w": (255, 255, 255),
    # hair (golden blond)
    "1": (255, 248, 190), "2": (255, 218, 102), "3": (230, 168, 52), "4": (176, 108, 36), "5": (112, 64, 30),
    # gold plate
    "A": (255, 248, 210), "B": (255, 218, 104), "C": (230, 164, 54), "D": (172, 104, 36), "E": (108, 60, 28),
    # silver plate
    "x": (232, 238, 246), "y": (178, 188, 210), "z": (116, 128, 158), "Z": (66, 72, 104),
    # red cape / cloth
    "r": (255, 120, 104), "s": (226, 54, 58), "t": (172, 28, 48), "u": (114, 18, 42), "v": (68, 12, 32),
    # navy underlayer / grip
    "n": (104, 118, 204), "m": (58, 66, 140), "o": (32, 34, 82),
    # sword fuller (violet) and gem
    "p": (150, 112, 236), "P": (92, 60, 164), "g": (255, 80, 80), "G": (170, 20, 36),
}
TRANSPARENT = ".", " "


def rgba(ch):
    r, g, b = PAL[ch]
    return (r, g, b, 255)


def grid(rows, pal=None):
    """Rows of palette characters -> RGBA image."""
    pal = pal or PAL
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in TRANSPARENT:
                continue
            r, g, b = pal[ch][:3]
            px[x, y] = (r, g, b, 255)
    return img


class Part:
    """A pixel grid with a pivot (in grid coordinates) and named attachment points."""

    def __init__(self, rows, pivot, points=None, pal=None):
        self.img = grid(rows, pal)
        self.pivot = pivot
        self.points = points or {}

    def point(self, name, angle=0.0, flip=False):
        """Attachment point relative to the pivot after rotating the part by `angle` degrees."""
        x, y = self.points[name]
        dx, dy = x - self.pivot[0], y - self.pivot[1]
        if flip:
            dx = -dx
        a = math.radians(angle)
        return (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))


# ---------------------------------------------------------------------------------- RotSprite
def _scale2x(a):
    """EPX / Scale2x on an (h, w) array of packed colours."""
    h, w = a.shape
    p = np.pad(a, 1, mode="edge")
    A, B, C, D = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1]  # up, left, right, down
    E = a
    out = np.empty((h * 2, w * 2), a.dtype)
    e0 = np.where((B == A) & (B != D) & (A != C), A, E)
    e1 = np.where((A == C) & (A != B) & (C != D), C, E)
    e2 = np.where((B == D) & (B != A) & (D != C), B, E)
    e3 = np.where((D == C) & (D != B) & (C != A), C, E)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    return out


def rotsprite(img, angle, pivot):
    """Rotate `img` by `angle` degrees (clockwise on screen) about `pivot`.

    Returns (image, new_pivot). Right angles are exact; other angles use RotSprite so
    single-pixel lines stay single-pixel lines.
    """
    angle = angle % 360
    if angle == 0:
        return img.copy(), pivot
    a = np.asarray(img.convert("RGBA")).astype(np.uint32)
    packed = (a[..., 0] << 24) | (a[..., 1] << 16) | (a[..., 2] << 8) | a[..., 3]
    big = _scale2x(_scale2x(_scale2x(packed)))  # 8x
    H, W = big.shape
    s = 8
    px, py = (pivot[0] + 0.5) * s, (pivot[1] + 0.5) * s
    r = math.hypot(max(px, W - px), max(py, H - py))
    n = int(math.ceil(r / s)) + 1
    size = 2 * n + 1
    # sample the output grid (1x) at the centre of each output pixel, mapped back into the 8x image
    ys, xs = np.mgrid[0:size, 0:size]
    ox, oy = (xs - n) * s, (ys - n) * s  # offsets from pivot in 8x units
    t = math.radians(angle)
    ct, st = math.cos(t), math.sin(t)
    sx = ct * ox + st * oy + px
    sy = -st * ox + ct * oy + py
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    out = np.zeros((size, size), np.uint32)
    out[ok] = big[iy[ok], ix[ok]]
    rgba_arr = np.stack([(out >> 24) & 255, (out >> 16) & 255, (out >> 8) & 255, out & 255], -1).astype(np.uint8)
    res = Image.fromarray(rgba_arr, "RGBA")
    return res, (n, n)


# ---------------------------------------------------------------------------------- canvas
def new(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def paste(dst, src, x, y):
    """Alpha-paste with integer placement (hard pixels only)."""
    x, y = int(round(x)), int(round(y))
    layer = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    layer.paste(src, (x, y))
    dst.alpha_composite(layer)


def place(dst, part_img, pivot, x, y, angle=0.0, flip=False):
    """Draw a part so its pivot lands on (x, y); optional mirror and rotation."""
    img, pv = part_img, pivot
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        pv = (img.width - 1 - pv[0], pv[1])
    if angle:
        img, pv = rotsprite(img, angle, pv)
    paste(dst, img, x - pv[0], y - pv[1])


def pad(img, n=1):
    out = new(img.width + 2 * n, img.height + 2 * n)
    out.paste(img, (n, n))
    return out


def outline(img, color=None, diagonal=False, grow_canvas=False):
    """Add a 1 px outline around all opaque pixels (grow_canvas: pad by 1 px first)."""
    color = color or rgba("k")
    if grow_canvas:
        img = pad(img, 1)
    a = np.asarray(img).copy()
    alpha = a[..., 3] > 0
    grow = np.zeros_like(alpha)
    grow[1:, :] |= alpha[:-1, :]
    grow[:-1, :] |= alpha[1:, :]
    grow[:, 1:] |= alpha[:, :-1]
    grow[:, :-1] |= alpha[:, 1:]
    if diagonal:
        grow[1:, 1:] |= alpha[:-1, :-1]
        grow[1:, :-1] |= alpha[:-1, 1:]
        grow[:-1, 1:] |= alpha[1:, :-1]
        grow[:-1, :-1] |= alpha[1:, 1:]
    edge = grow & ~alpha
    a[edge] = color
    return Image.fromarray(a, "RGBA")


def recolor(img, mapping):
    """Swap palette colours: mapping {src_char: dst_char}."""
    a = np.asarray(img).copy()
    for s, d in mapping.items():
        m = (a[..., 0] == PAL[s][0]) & (a[..., 1] == PAL[s][1]) & (a[..., 2] == PAL[s][2]) & (a[..., 3] > 0)
        a[m, :3] = PAL[d]
    return Image.fromarray(a, "RGBA")


def tint(img, rgb, amount):
    """Blend opaque pixels toward a colour (for flashes); keeps hard alpha."""
    a = np.asarray(img).astype(float)
    m = a[..., 3] > 0
    for i in range(3):
        a[..., i][m] = a[..., i][m] * (1 - amount) + rgb[i] * amount
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def dissolve(img, keep, seed=0):
    """Ordered-dither fade: keep a fraction of opaque pixels (no semi-transparency)."""
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    a = np.asarray(img).copy()
    h, w = a.shape[:2]
    th = np.tile(bayer, (h // 4 + 1, w // 4 + 1))[:h, :w]
    th = np.roll(th, seed, axis=1)
    a[..., 3] = np.where(th < keep, a[..., 3], 0)
    return Image.fromarray(a, "RGBA")


def shift(img, dx, dy):
    out = new(img.width, img.height)
    out.paste(img, (dx, dy))
    return out


# ---------------------------------------------------------------------------------- output
def lp(path):
    """Windows: allow paths over 260 characters."""
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith("\\\\?\\"):
        path = "\\\\?\\UNC\\" + path[2:] if path.startswith("\\\\") else "\\\\?\\" + path
    return path


def save_png(img, path):
    os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
    img.save(lp(path))


def save_json(obj, path):
    os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
    with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")


def sheet_and_fanim(tag_frames, frame_w, frame_h):
    """tag_frames: [(tag, [(image, duration_ms), ...]), ...] -> (sheet image, fanim dict)."""
    total = sum(len(fr) for _, fr in tag_frames)
    sheet = Image.new("RGBA", (frame_w * total, frame_h), (0, 0, 0, 0))
    anims, i = {}, 0
    for tag, frames in tag_frames:
        out = []
        for img, ms in frames:
            sheet.paste(img, (i * frame_w, 0))
            out.append({"duration": round(ms / 1000.0, 3),
                        "data": {"x": i * frame_w, "y": 0, "w": frame_w, "h": frame_h}})
            i += 1
        anims[tag] = {"frames": out}
    return sheet, {"anims": anims}


def zoom(img, scale, bg=(92, 98, 86, 255), grid_alpha=0):
    """Preview helper: nearest-neighbour upscale on the arena colour, optional pixel grid."""
    base = Image.new("RGBA", img.size, bg)
    base.alpha_composite(img)
    big = base.resize((img.width * scale, img.height * scale), Image.NEAREST)
    if grid_alpha:
        a = np.asarray(big).copy()
        a[::scale, :, :3] = (a[::scale, :, :3] * (1 - grid_alpha)).astype(np.uint8)
        a[:, ::scale, :3] = (a[:, ::scale, :3] * (1 - grid_alpha)).astype(np.uint8)
        big = Image.fromarray(a, "RGBA")
    return big


def hstack(images, gap=6, bg=(30, 30, 30, 255), align="bottom"):
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    h = max(i.height for i in images)
    out = Image.new("RGBA", (w, h), bg)
    x = 0
    for i in images:
        out.paste(i, (x, h - i.height if align == "bottom" else 0))
        x += i.width + gap
    return out


def vstack(images, gap=6, bg=(30, 30, 30, 255)):
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGBA", (w, h), bg)
    y = 0
    for i in images:
        out.paste(i, (0, y))
        y += i.height + gap
    return out
