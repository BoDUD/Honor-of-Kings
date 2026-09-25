"""Tiny pixel-art compositor used by the HoK sprite generators.

Frames are PIL RGBA images. Parts are dicts {anchor: (x, y), grid: [str, ...]} whose characters
index a palette. Everything is drawn with hard pixels (no anti-aliasing) to match TFM2's style.
"""
import json
import math
import os

from PIL import Image

OUTLINE = (20, 18, 32, 255)


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


def new_frame(w=65, h=65):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def put(img, x, y, rgb, alpha=255):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), tuple(rgb[:3]) + (alpha,))


def draw_part(img, part, x, y, palette, flip=False, recolor=None):
    """Place `part` so that its anchor lands on (x, y)."""
    ax, ay = part["anchor"]
    grid = part["grid"]
    w = max(len(r) for r in grid)
    for gy, row in enumerate(grid):
        for gx, ch in enumerate(row):
            if ch == "." or ch == " ":
                continue
            if recolor and ch in recolor:
                ch = recolor[ch]
            px = x + ((w - 1 - gx) - (w - 1 - ax) if flip else gx - ax)
            put(img, px, y + gy - ay, palette[ch])


def line_points(x0, y0, x1, y1):
    """Bresenham line, inclusive."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    pts = []
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return pts


def draw_line(img, x0, y0, x1, y1, rgb):
    for x, y in line_points(x0, y0, x1, y1):
        put(img, x, y, rgb)


def draw_sword(img, hx, hy, angle_deg, pal, length=15, glow=False):
    """Longsword held at (hx, hy). angle 0 = pointing right, 90 = pointing down (screen coords)."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx  # perpendicular
    # grip + pommel behind the hand
    for t in (1, 2):
        put(img, round(hx - dx * t), round(hy - dy * t), pal["l"])
    put(img, round(hx - dx * 3), round(hy - dy * 3), pal["R"])
    # blade (two pixels wide: bright edge + blue core), starting past the guard
    tip = (hx + dx * length, hy + dy * length)
    core = line_points(hx + dx * 2, hy + dy * 2, *tip)
    for i, (x, y) in enumerate(core):
        put(img, x, y, pal["V"] if i < len(core) - 1 else pal["B"])
        ex, ey = round(x + px), round(y + py)
        put(img, ex, ey, pal["B"] if glow or i % 5 != 4 else pal["a"])
    for x, y in line_points(hx + dx * 2 - px, hy + dy * 2 - py, hx + dx * (length - 3) - px, hy + dy * (length - 3) - py):
        put(img, x, y, pal["v"])
    # crossguard (gold, perpendicular)
    for t in (-2, -1, 0, 1, 2):
        put(img, round(hx + dx * 1 + px * t), round(hy + dy * 1 + py * t), pal["g"] if abs(t) < 2 else pal["f"])


def draw_arm(img, sx, sy, hx, hy, pal):
    """Armoured arm from shoulder (sx, sy) to hand (hx, hy): 2px thick."""
    pts = line_points(sx, sy, hx, hy)
    for x, y in pts:
        put(img, x, y, pal["c"])
        put(img, x + 1, y, pal["b"])
    put(img, sx, sy, pal["g"])


def add_outline(img, color=OUTLINE):
    """1px outline around every opaque region (4-neighbourhood), like TFM2 base sprites."""
    w, h = img.size
    px = img.load()
    solid = [[px[x, y][3] > 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if solid[y][x]:
                continue
            if any(0 <= x + ox < w and 0 <= y + oy < h and solid[y + oy][x + ox]
                   for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = color
    return img


def shifted(img, dx, dy):
    out = new_frame(img.width, img.height)
    out.alpha_composite(img, (dx, dy)) if dx >= 0 and dy >= 0 else out.paste(img, (dx, dy), img)
    return out


def rotate90(img, clockwise=True):
    return img.transpose(Image.Transpose.ROTATE_270 if clockwise else Image.Transpose.ROTATE_90)


def fade(img, alpha_mult):
    out = img.copy()
    a = out.getchannel("A").point(lambda v: int(v * alpha_mult))
    out.putalpha(a)
    return out


def sheet_and_fanim(tag_frames, frame_w=65, frame_h=65):
    """tag_frames: list of (tag, [(image, duration_ms), ...]) -> (sheet image, fanim dict)."""
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
