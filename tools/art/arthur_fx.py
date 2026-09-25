"""Arthur's VFX sheets and skill icons.

    python tools/art/arthur_fx.py [--preview out.png]

Placement rules measured from base-game effects:
  * body-attached effects (buffs, hit effects) share the champion pivot: frame centre = 11.5 px above ground
  * ground zones (projectile views such as RangePeriodProjectile) are centred on the frame centre
VFX follow the TFM2 look: saturated gold/white, hard pixels, no black outline.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw  # noqa: E402

import arthur_parts as P  # noqa: E402
from pixel import draw_part, new_frame, put, save_json, save_png, sheet_and_fanim  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOD = os.path.join(ROOT, "hok")
WHITE, PALE, GOLD, DEEP, NAVY = (255, 255, 255), (255, 244, 176), (255, 206, 84), (214, 140, 40), (58, 70, 128)
RAMP = [WHITE, PALE, GOLD, DEEP]


def ellipse_ring(img, cx, cy, rx, ry, col, a0=0, a1=360, step=1.0):
    t = a0
    while t <= a1:
        a = math.radians(t)
        put(img, round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a)), col)
        t += step


def disc(img, cx, cy, r, col):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(img, x, y, col)


def crescent(img, cx, cy, r, thick, a0, a1):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if r - thick <= d <= r:
                ang = math.degrees(math.atan2(y - cy, x - cx)) % 360
                lo, hi = a0 % 360, a1 % 360
                if (lo <= ang <= hi) if lo <= hi else (ang >= lo or ang <= hi):
                    put(img, x, y, RAMP[min(3, int((r - d) / max(thick, 1) * 4))])


def sparkle(img, x, y, size=2, col=WHITE):
    put(img, x, y, col)
    for k in range(1, size + 1):
        c = col if k < size else GOLD
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            put(img, x + dx, y + dy, c)


# ------------------------------------------------------------------ effects
def slash():
    """Body hit: big crescent (skill 1 landing) and small spark (Oath-empowered basic attack)."""
    hit, small = [], []
    cx, cy = 32, 40  # body centre in a 65x81 frame (ground at 52)
    for k, (a0, a1, th) in enumerate([(200, 260, 3), (200, 320, 4), (220, 20, 5), (260, 40, 3), (300, 50, 2)]):
        img = new_frame(65, 81)
        crescent(img, cx, cy, 14 + k, th, a0, a1)
        if k in (2, 3):
            for s in range(4):
                a = math.radians(30 + s * 40 + k * 7)
                sparkle(img, round(cx + math.cos(a) * (18 + k)), round(cy + math.sin(a) * (12 + k)), 1)
        hit.append((img, 50))
    for k in range(4):
        img = new_frame(65, 81)
        r = 2 + k * 2
        if k < 3:
            sparkle(img, cx + 2, cy - 2, r, WHITE if k == 0 else PALE)
        for s in range(5):
            a = math.radians(s * 72 + k * 15)
            put(img, round(cx + 2 + math.cos(a) * (r + 2)), round(cy - 2 + math.sin(a) * (r + 2)), GOLD if k < 3 else DEEP)
        small.append((img, 50))
    return [("hit", hit), ("small", small)]


def mini_shield(img, x, y, dim=False):
    rim, face = (DEEP, NAVY) if dim else (GOLD, (72, 88, 150))
    rows = [".rrr.", "rfffr", "rfgfr", "rfffr", ".rfr.", "..r.."]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "r":
                put(img, x + i - 2, y + j - 3, rim)
            elif ch == "f":
                put(img, x + i - 2, y + j - 3, face)
            elif ch == "g":
                put(img, x + i - 2, y + j - 3, PALE if not dim else GOLD)


def whirl():
    """Skill 2 buff: three holy shields orbit Arthur at waist height (loop)."""
    frames = []
    cx, cy, rx, ry = 40, 39, 19, 7  # 81x81 frame, ground at 52 -> waist 13 px up
    for f in range(8):
        img = new_frame(81, 81)
        base = f * 360 / 8
        for trail in range(1, 5):  # golden trails behind each shield
            for s in range(3):
                a = math.radians(base + s * 120 - trail * 9)
                put(img, round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a)), GOLD if trail < 3 else DEEP)
        for s in range(3):
            a = math.radians(base + s * 120)
            sx, sy = round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a))
            mini_shield(img, sx, sy, dim=math.sin(a) < 0)  # far side of the orbit is darker
        frames.append((img, 60))
    return [("loop", frames)]


def oath():
    """Oath buff: small golden ring at Arthur's feet with rising motes (loop, drawn under the unit)."""
    frames = []
    cx, cy = 32, 51
    for f in range(6):
        img = new_frame(65, 81)
        ellipse_ring(img, cx, cy, 11, 4, GOLD, step=6)
        ellipse_ring(img, cx, cy, 11, 4, PALE, a0=f * 60, a1=f * 60 + 70, step=5)
        for m in range(3):
            h = (f * 3 + m * 7) % 14
            put(img, cx - 8 + m * 8, cy - 2 - h, PALE if h < 9 else GOLD)
        frames.append((img, 100))
    return [("loop", frames)]


def ult_impact():
    """Ult landing: flash, pillar of light, holy cross, expanding ring (97x97, ground at 60)."""
    frames = []
    cx, gy = 48, 60
    for f in range(8):
        img = new_frame(97, 97)
        ring = 6 + f * 5
        if f < 7:
            ellipse_ring(img, cx, gy, ring, ring * 0.72, GOLD if f < 4 else DEEP, step=2.5)
            if f < 5:
                ellipse_ring(img, cx, gy, ring - 2, (ring - 2) * 0.72, PALE, step=3)
        if f == 0:
            disc(img, cx, gy - 2, 6, WHITE)
        if 1 <= f <= 4:  # pillar
            h = [28, 44, 40, 30][f - 1]
            w = [3, 4, 3, 2][f - 1]
            for y in range(gy - h, gy + 1):
                for x in range(cx - w, cx + w + 1):
                    put(img, x, y, WHITE if abs(x - cx) < w - 1 else PALE)
        if 2 <= f <= 5:  # holy cross flare
            L = [10, 16, 14, 8][f - 2]
            for d in range(-L, L + 1):
                put(img, cx + d, gy - 18, WHITE if abs(d) < L - 3 else GOLD)
        for s in range(6):
            if 3 <= f <= 7:
                a = math.radians(s * 60 + f * 12)
                r = ring + 2
                put(img, round(cx + math.cos(a) * r), round(gy - 10 + math.sin(a) * r * 0.6), PALE if f < 6 else GOLD)
        frames.append((img, 60))
    return [("impact", frames)]


def seal():
    """Ult zone: golden holy seal on the ground, centred on the frame (loop, z -2)."""
    frames = []
    cx, cy, rx, ry = 32, 24, 26, 19
    for f in range(8):
        img = new_frame(65, 49)
        ellipse_ring(img, cx, cy, rx, ry, GOLD, step=1.2)
        ellipse_ring(img, cx, cy, rx - 4, ry - 3, DEEP, step=2)
        for s in range(8):  # rotating runes
            a = math.radians(f * 11 + s * 45)
            put(img, round(cx + (rx - 2) * math.cos(a)), round(cy + (ry - 1.5) * math.sin(a)), PALE)
        # sword-cross emblem, pulsing
        c = WHITE if f % 4 < 2 else PALE
        for d in range(-8, 9):
            put(img, cx, cy + d, c if abs(d) < 7 else GOLD)
        for d in range(-5, 6):
            put(img, cx + d, cy - 3, c if abs(d) < 4 else GOLD)
        frames.append((img, 100))
    return [("loop", frames)]


# ------------------------------------------------------------------ icons (24x24, base-game glyph style)
def icon_skill():
    img = new_frame(24, 24)
    for k in range(3):  # charge lines
        for x in range(1 + k, 7 + k):
            put(img, x, 7 + k * 4, PALE if x > 3 + k else GOLD)
    shield = [
        "..ffffffff..", ".fGGGGGGGGf.", "fGGWWGGGGGGf", "fGWGGGGGGGGf", "fGGGGnnGGGGf", "fGGGnGGnGGGf",
        "fGGGGnnGGGGf", ".fGGGGGGGGf.", ".fGGGGGGGGf.", "..fGGGGGGf..", "...fGGGGf...", "....fGGf....", ".....ff.....",
    ]
    cols = {"f": DEEP, "G": GOLD, "W": WHITE, "n": (160, 60, 50)}
    for j, row in enumerate(shield):
        for i, ch in enumerate(row):
            if ch in cols:
                put(img, 10 + i, 4 + j, cols[ch])
    return img


def icon_skill2():
    img = new_frame(24, 24)
    ellipse_ring(img, 12, 12, 9, 9, DEEP, step=4)
    ellipse_ring(img, 12, 12, 9, 9, GOLD, a0=0, a1=250, step=3)
    for s in range(3):
        a = math.radians(-90 + s * 120)
        mini_shield(img, round(12 + 8 * math.cos(a)), round(12 + 8 * math.sin(a)))
    sparkle(img, 12, 12, 2, WHITE)
    return img


def icon_ult():
    img = new_frame(24, 24)
    for k in range(8):  # radiant burst
        a = math.radians(k * 45 + 22.5)
        for t in range(6, 11):
            put(img, round(12 + math.cos(a) * t), round(9 + math.sin(a) * t), GOLD if t < 9 else DEEP)
    disc(img, 12, 9, 4, PALE)
    for y in range(2, 22):  # sword pointing down
        put(img, 12, y, WHITE if y < 19 else PALE)
        put(img, 11, y, (133, 148, 230) if y < 18 else PALE)
        put(img, 13, y, (74, 79, 164) if y < 18 else PALE)
    for x in range(8, 17):
        put(img, x, 6, GOLD if 9 <= x <= 15 else DEEP)
    put(img, 12, 1, (224, 70, 61))
    return img


def build():
    return {
        "hok_arthur_slash": (slash(), (65, 81)),
        "hok_arthur_whirl": (whirl(), (81, 81)),
        "hok_arthur_oath": (oath(), (65, 81)),
        "hok_arthur_ult_impact": (ult_impact(), (97, 97)),
        "hok_arthur_seal": (seal(), (65, 49)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    args = ap.parse_args()
    fx = build()
    for name, (tags, (w, h)) in fx.items():
        sheet, fanim = sheet_and_fanim(tags, w, h)
        save_png(sheet, os.path.join(MOD, "effects", f"{name}#sheet.png"))
        save_json(fanim, os.path.join(MOD, "effects", f"{name}#anim.fanim"))
    icons = {"hok_arthur_skill": icon_skill(), "hok_arthur_skill2": icon_skill2(), "hok_arthur_ult": icon_ult()}
    for name, img in icons.items():
        save_png(img, os.path.join(MOD, "icons", f"{name}.png"))
    print("effects:", ", ".join(fx), "| icons:", ", ".join(icons))
    if args.preview:
        S, bg = 4, (92, 98, 86, 255)
        rows = []
        for name, (tags, (w, h)) in fx.items():
            for tag, frames in tags:
                row = Image.new("RGBA", (200 + len(frames) * (w * S + 4), h * S), (28, 28, 28, 255))
                ImageDraw.Draw(row).text((4, 4), f"{name}\n{tag} {len(frames)}f", fill=(255, 255, 255, 255))
                for i, (img, _) in enumerate(frames):
                    cell = Image.new("RGBA", (w, h), bg)
                    cell.alpha_composite(img)
                    row.paste(cell.resize((w * S, h * S), Image.NEAREST), (200 + i * (w * S + 4), 0))
                rows.append(row)
        irow = Image.new("RGBA", (200 + 3 * (24 * 8 + 8), 24 * 8), (28, 28, 28, 255))
        ImageDraw.Draw(irow).text((4, 4), "icons 24x24", fill=(255, 255, 255, 255))
        for i, img in enumerate(icons.values()):
            cell = Image.new("RGBA", (24, 24), (40, 40, 48, 255))
            cell.alpha_composite(img)
            irow.paste(cell.resize((24 * 8, 24 * 8), Image.NEAREST), (200 + i * (24 * 8 + 8), 0))
        rows.append(irow)
        W = max(r.width for r in rows)
        out = Image.new("RGBA", (W, sum(r.height + 6 for r in rows)), (20, 20, 20, 255))
        y = 0
        for r in rows:
            out.paste(r, (0, y))
            y += r.height + 6
        save_png(out, args.preview)
        print("preview", out.size)


if __name__ == "__main__":
    main()
