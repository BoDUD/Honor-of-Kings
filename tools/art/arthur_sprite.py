"""Build Arthur's sprite sheet (hok/champions/hok_arthur#sheet.png + #anim.fanim).

    python tools/art/arthur_sprite.py                      # write the sheet + fanim into the mod
    python tools/art/arthur_sprite.py --preview out.png    # also write a 6x contact sheet

Frame 65x81; the feet's bottom edge sits 11.5 px below the frame centre (TFM2 base convention),
leaving 16 px of headroom above the head for jumps and raised swords.
Tags match the champion data: idle, run, attack, skill, skill2, ult, hit, dead.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw  # noqa: E402

import arthur_parts as P  # noqa: E402
from pixel import (add_outline, draw_arm, draw_part, draw_sword, fade, new_frame, put,  # noqa: E402
                   save_json, save_png, sheet_and_fanim)

PAL = P.PALETTE
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOD = os.path.join(ROOT, "hok")

FW, FH = 65, 81
GROUND = 50  # last row of the soles (outline adds row 51 -> bottom edge 52 = 40.5 + 11.5)
CX = 32
GOLD_FX = [(255, 255, 255), (255, 244, 176), (255, 214, 92), (232, 160, 48)]  # hot core -> outer glow


def arc(img, cx, cy, r, thick, a0, a1, cols=GOLD_FX, sparkle=0):
    """Hard-pixel crescent: ring sector from angle a0 to a1 (degrees, screen coords)."""
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if r - thick <= d <= r:
                ang = math.degrees(math.atan2(y - cy, x - cx)) % 360
                lo, hi = a0 % 360, a1 % 360
                inside = lo <= ang <= hi if lo <= hi else (ang >= lo or ang <= hi)
                if inside:
                    k = min(len(cols) - 1, int((r - d) / max(thick, 1) * len(cols)))
                    put(img, x, y, cols[k])
    for s in range(sparkle):
        a = math.radians(a0 + (a1 - a0) * (s + 0.5) / sparkle)
        put(img, round(cx + math.cos(a) * (r + 2)), round(cy + math.sin(a) * (r + 2)), cols[1])


def rays(img, cx, cy, n=6, r0=3, r1=7, phase=0, col=(255, 244, 176)):
    for k in range(n):
        a = math.radians(phase + k * 360 / n)
        for t in range(r0, r1):
            put(img, round(cx + math.cos(a) * t), round(cy + math.sin(a) * t), col if t < r1 - 1 else (255, 255, 255))


def pose(legs="stand", body_dy=0, body_dx=0, head_dy=0, cape="still", shield=(0, 0), hand=(-7, 7),
         sword_angle=125, sword_len=14, glow=False, lift=0, sword_front=False, fx=None, fx_behind=None):
    """Compose one frame from parts. Offsets are relative to the idle layout."""
    img = new_frame(FW, FH)
    hip_y = GROUND - lift - (len(P.LEGS[legs]["grid"]) - 1)
    torso_y = hip_y - len(P.TORSO["grid"]) + body_dy
    x = CX + body_dx
    if fx_behind:
        fx_behind(img, x, torso_y)
    draw_part(img, P.CAPE[cape], x - 1, torso_y + 1, PAL)
    draw_part(img, P.LEGS[legs], x, hip_y, PAL)
    draw_part(img, P.TORSO, x, torso_y, PAL)
    sx, sy = x - 5, torso_y + 2
    hx, hy = sx + hand[0] + 5, sy + hand[1]

    def sword_arm():
        draw_sword(img, hx, hy, sword_angle, PAL, length=sword_len, glow=glow)
        draw_arm(img, sx, sy, hx, hy, PAL)
        draw_part(img, P.GAUNTLET, hx, hy, PAL)

    if not sword_front:
        sword_arm()
    draw_part(img, P.HEAD, x + 1, torso_y + head_dy, PAL)
    draw_part(img, P.SHIELD, x + 6 + shield[0], torso_y + 3 + shield[1], PAL)
    if sword_front:
        sword_arm()
    img = add_outline(img)
    if fx:  # effects are drawn after the outline: VFX in TFM2 have no black outline
        fx(img, x, torso_y)
    return img


# ---------------------------------------------------------------- animations
def idle():
    return [(pose(), 180), (pose(cape="still"), 180), (pose(body_dy=1, head_dy=0), 180), (pose(body_dy=1), 180)]


def run():
    common = dict(hand=(-9, 4), sword_angle=160, sword_len=14, cape="flow", shield=(1, 0))
    seq = [("stride_a", -1), ("stride_b", 0), ("stand", 0), ("stride_a", -1), ("stride_b", 0), ("stand", 0)]
    return [(pose(legs=l, body_dy=b, **common), 80) for l, b in seq]


def attack():
    def slash(a0, a1, r=17, thick=4, dy=4):
        return lambda img, x, ty: arc(img, x + 4, ty + dy, r, thick, a0, a1, sparkle=3)
    return [
        (pose(hand=(-9, -1), sword_angle=225, shield=(-1, 0)), 55),
        (pose(hand=(-3, -5), sword_angle=285, shield=(-1, 0), body_dy=0), 55),
        (pose(hand=(5, -3), sword_angle=330, shield=(-2, 1), sword_front=True, fx=slash(250, 330)), 55),
        (pose(hand=(9, 3), sword_angle=25, shield=(-2, 1), sword_front=True, body_dx=1, fx=slash(270, 60)), 55),
        (pose(hand=(7, 7), sword_angle=60, shield=(-1, 1), sword_front=True, fx=slash(330, 70, thick=2)), 55),
        (pose(hand=(-5, 6), sword_angle=115), 55),
    ]


def skill():
    def impact(img, x, ty):
        arc(img, x + 6, ty + 8, 16, 4, 290, 80, sparkle=4)
        rays(img, x + 16, ty + 18, n=5, r0=2, r1=6, phase=10)
    return [
        (pose(legs="crouch", body_dy=0, hand=(-9, 3), sword_angle=165, shield=(1, -2)), 70),
        (pose(legs="tuck", lift=4, hand=(-6, -3), sword_angle=250, shield=(1, -1), cape="flow"), 70),
        (pose(legs="tuck", lift=8, hand=(-2, -6), sword_angle=290, shield=(1, -1), cape="flow"), 70),
        (pose(legs="tuck", lift=5, hand=(6, -2), sword_angle=345, shield=(0, 0), cape="flow", sword_front=True,
              fx=lambda img, x, ty: arc(img, x + 4, ty + 4, 16, 3, 250, 350, sparkle=3)), 70),
        (pose(legs="crouch", hand=(9, 5), sword_angle=40, shield=(-1, 1), sword_front=True, fx=impact), 70),
        (pose(legs="crouch", hand=(4, 7), sword_angle=80, shield=(0, 0)), 70),
        (pose(hand=(-6, 7), sword_angle=120), 70),
    ]


def skill2():
    def swirl(a0, a1):
        return lambda img, x, ty: arc(img, x + 1, ty + 9, 19, 3, a0, a1, cols=GOLD_FX[1:], sparkle=4)
    return [
        (pose(hand=(-10, 4), sword_angle=185, shield=(0, 0)), 55),
        (pose(hand=(-8, 8), sword_angle=150, shield=(0, 0), fx=swirl(120, 200)), 55),
        (pose(hand=(4, 8), sword_angle=70, shield=(-2, 0), sword_front=True, fx=swirl(40, 170)), 55),
        (pose(hand=(9, 4), sword_angle=5, shield=(-2, 0), sword_front=True, fx=swirl(330, 90)), 55),
        (pose(hand=(7, -1), sword_angle=320, shield=(-1, 0), sword_front=True, fx=swirl(250, 20)), 55),
        (pose(hand=(-6, 6), sword_angle=125), 55),
    ]


def ult():
    def charge(n, phase):
        def f(img, x, ty):
            rays(img, x - 1, ty - 12, n=n, r0=3, r1=8, phase=phase)
        return f

    def slam(img, x, ty):
        for dx in range(-9, 10):  # ground flash line
            put(img, x + 10 + dx, GROUND + 1, GOLD_FX[0] if abs(dx) < 4 else GOLD_FX[2])
        rays(img, x + 12, GROUND - 2, n=7, r0=2, r1=9, phase=200)

    up = dict(hand=(-1, -6), sword_angle=272, glow=True, sword_len=13)
    return [
        (pose(legs="crouch", hand=(-4, -4), sword_angle=255, glow=True, shield=(0, 0)), 65),
        (pose(legs="crouch", fx=charge(6, 0), **up), 65),
        (pose(legs="tuck", lift=5, cape="flow", fx=charge(8, 20), **up), 65),
        (pose(legs="tuck", lift=9, cape="flow", fx=charge(8, 40), **up), 65),
        (pose(legs="tuck", lift=10, cape="flow", fx=charge(10, 0), **up), 65),
        (pose(legs="tuck", lift=6, cape="flow", hand=(6, -3), sword_angle=340, glow=True, sword_front=True,
              fx=lambda img, x, ty: arc(img, x + 3, ty + 4, 17, 4, 240, 350, sparkle=4)), 65),
        (pose(legs="crouch", hand=(8, 6), sword_angle=75, glow=True, sword_front=True, fx=slam), 65),
        (pose(legs="crouch", hand=(8, 7), sword_angle=80, glow=True, sword_front=True), 65),
        (pose(legs="crouch", body_dy=0, hand=(6, 8), sword_angle=85, sword_front=True), 65),
        (pose(hand=(-6, 7), sword_angle=120), 65),
    ]


def hit():
    return [(pose(body_dx=-1, head_dy=1, hand=(-8, 5), sword_angle=140, shield=(-1, -1)), 100)]


def dead():
    kneel = pose(legs="crouch", head_dy=1, hand=(-8, 9), sword_angle=165, shield=(0, 2))
    slump = pose(legs="crouch", head_dy=2, body_dy=1, hand=(-9, 10), sword_angle=175, shield=(0, 3))
    frames = [(pose(body_dx=-1, head_dy=1, hand=(-8, 5), sword_angle=140), 100), (kneel, 100), (slump, 160)]
    for a in (0.85, 0.65, 0.45, 0.25, 0.0):
        frames.append((fade(slump, a), 100))
    return frames


def build():
    return [("idle", idle()), ("run", run()), ("attack", attack()), ("skill", skill()), ("skill2", skill2()),
            ("ult", ult()), ("hit", hit()), ("dead", dead())]


def contact_sheet(tags, S=5):
    bg = (92, 98, 86, 255)
    rows = []
    for tag, frames in tags:
        row = Image.new("RGBA", (130 + len(frames) * (FW * S + 4), FH * S), (28, 28, 28, 255))
        ImageDraw.Draw(row).text((4, 4), f"{tag}\n{len(frames)}f {frames[0][1]}ms", fill=(255, 255, 255, 255))
        for i, (img, _) in enumerate(frames):
            cell = Image.new("RGBA", (FW, FH), bg)
            cell.alpha_composite(img)
            ImageDraw.Draw(cell).line((0, GROUND + 2, 3, GROUND + 2), fill=(255, 80, 80, 255))  # bottom edge
            row.paste(cell.resize((FW * S, FH * S), Image.NEAREST), (130 + i * (FW * S + 4), 0))
        rows.append(row)
    W = max(r.width for r in rows)
    out = Image.new("RGBA", (W, sum(r.height + 6 for r in rows)), (20, 20, 20, 255))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height + 6
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    ap.add_argument("--scale", type=int, default=5)
    args = ap.parse_args()
    tags = build()
    sheet, fanim = sheet_and_fanim(tags, FW, FH)
    save_png(sheet, os.path.join(MOD, "champions", "hok_arthur#sheet.png"))
    save_json(fanim, os.path.join(MOD, "champions", "hok_arthur#anim.fanim"))
    print("sheet", sheet.size, "frames", sum(len(f) for _, f in tags))
    if args.preview:
        out = contact_sheet(tags, args.scale)
        save_png(out, args.preview)
        print("preview", out.size)


if __name__ == "__main__":
    main()
