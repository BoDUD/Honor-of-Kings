"""Arthur's view effects (HoK look: holy gold, white-hot cores, fire on the orbiting shields).

    python tools/art/arthur_fx.py [--preview out_dir]

Anchoring (measured on base sprites):
  * body effects and buffs share the unit pivot: frame centre = 11.5 px above the feet
  * area effects are true circles centred on the frame centre (base shield_bearer / knight rings)
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_lib as fx  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import px  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
EFX = os.path.join(ROOT, "hok", "effects")


def frame(w, h):
    return px.new(w, h), w // 2, h // 2


def cool(ramp, k):
    """Drop the k hottest colours (fading effects cool down)."""
    return ramp[k:] if k < len(ramp) else ramp[-1:]


# ----------------------------------------------------------------------------- slash (skill 1 hit / empowered attack)
def slash_arc(img, cx, cy, direction, length, thick, ramp, bend=48):
    """Near-straight slash through (cx, cy) along `direction` (screen degrees), bowed slightly."""
    d = math.radians(direction)
    nx, ny = -math.sin(d), math.cos(d)            # normal (the side the arc bows away from)
    ox, oy = cx + nx * bend, cy + ny * bend        # circle centre
    base = math.degrees(math.atan2(cy - oy, cx - ox))
    half = math.degrees(length / 2 / bend)
    fx.crescent(img, ox, oy, bend + thick / 2, base - half, base + half, thick, ramp, taper=0.5, lead_cap=True)


def slash_hit():
    frames = []
    for i in range(7):
        f, cx, cy = frame(91, 91)
        if i == 0:
            slash_arc(f, cx, cy, 35, 44, 3, fx.WHITE)
            fx.burst(f, cx, cy, 2, 7, 6, fx.HOLY, seed=1)
        elif i == 1:
            slash_arc(f, cx, cy, 35, 70, 10, fx.HOLY)
            fx.burst(f, cx, cy, 4, 16, 8, fx.HOLY, seed=2)
        elif i == 2:
            slash_arc(f, cx, cy, 35, 74, 9, fx.GOLD)
            slash_arc(f, cx, cy, 145, 70, 10, fx.HOLY)
            fx.burst(f, cx, cy, 5, 18, 10, fx.HOLY, seed=3, rot=10)
            for k, (sx, sy) in enumerate(((-24, -18), (22, -22), (26, 16), (-20, 20))):
                fx.sparkle(f, cx + sx, cy + sy, 3 if k % 2 else 2)
        elif i == 3:
            slash_arc(f, cx, cy, 35, 74, 6, cool(fx.GOLD, 1))
            slash_arc(f, cx, cy, 145, 72, 7, fx.GOLD)
            fx.burst(f, cx, cy, 4, 14, 10, cool(fx.HOLY, 1), seed=4, rot=20)
            fx.particles(f, cx, cy, 16, 6, 34, 0.45, fx.GOLD, seed=5)
        elif i == 4:
            slash_arc(f, cx, cy, 35, 58, 3, cool(fx.GOLD, 2))
            slash_arc(f, cx, cy, 145, 56, 3, cool(fx.GOLD, 1))
            fx.particles(f, cx, cy, 16, 6, 38, 0.7, fx.GOLD, seed=5)
            fx.sparkle(f, cx + 18, cy - 12, 2)
            f = px.dissolve(f, 0.8, 1)
        elif i == 5:
            fx.particles(f, cx, cy, 16, 6, 40, 0.88, fx.GOLD, seed=5)
            slash_arc(f, cx, cy, 145, 50, 2, cool(fx.GOLD, 2))
            f = px.dissolve(f, 0.55, 2)
        else:
            fx.particles(f, cx, cy, 12, 6, 42, 1.0, fx.GOLD, seed=5)
            f = px.dissolve(f, 0.35, 3)
        frames.append((f, 55))
    return frames


def slash_small():
    frames = []
    for i in range(5):
        f, cx, cy = frame(91, 91)
        if i == 0:
            slash_arc(f, cx, cy, 40, 26, 2, fx.WHITE, bend=30)
            fx.burst(f, cx, cy, 1, 5, 6, fx.HOLY, seed=7)
        elif i == 1:
            slash_arc(f, cx, cy, 40, 36, 5, fx.HOLY, bend=30)
            fx.burst(f, cx, cy, 3, 11, 8, fx.HOLY, seed=8)
            fx.sparkle(f, cx + 14, cy - 10, 2)
        elif i == 2:
            slash_arc(f, cx, cy, 40, 38, 4, fx.GOLD, bend=30)
            fx.burst(f, cx, cy, 2, 7, 8, cool(fx.HOLY, 1), seed=9)
            fx.particles(f, cx, cy, 8, 4, 20, 0.5, fx.GOLD, seed=10)
        elif i == 3:
            slash_arc(f, cx, cy, 40, 34, 2, cool(fx.GOLD, 2), bend=30)
            fx.particles(f, cx, cy, 8, 4, 22, 0.8, fx.GOLD, seed=10)
            f = px.dissolve(f, 0.7, 1)
        else:
            fx.particles(f, cx, cy, 8, 4, 24, 1.0, fx.GOLD, seed=10)
            f = px.dissolve(f, 0.4, 2)
        frames.append((f, 50))
    return frames


# ----------------------------------------------------------------------------- ult: Excalibur strike
def ult_impact():
    W, H = 141, 181
    frames = []
    for i in range(9):
        f, cx, cy = frame(W, H)
        ground = cy + 11
        if i == 0:   # the blade of light appears high above
            fx.pillar(f, cx, 0, ground - 44, 5, cool(fx.HOLY, 1), seed=1, t=i)
            fx.light_blade(f, cx, ground - 118, 90, 64, 12)
        elif i == 1:  # plunging
            fx.pillar(f, cx, 0, ground, 9, cool(fx.HOLY, 1), seed=1, t=i)
            fx.light_blade(f, cx, ground - 80, 90, 72, 14)
            fx.burst(f, cx, ground, 3, 10, 8, fx.HOLY, seed=2, ry_scale=0.4)
        elif i == 2:  # impact
            fx.pillar(f, cx, 0, ground, 22, fx.HOLY, seed=1, t=i)
            fx.light_blade(f, cx, ground - 70, 90, 72, 16)
            fx.burst(f, cx, ground, 8, 40, 12, fx.HOLY, seed=3, ry_scale=0.42)
            fx.ring(f, cx, ground, 26, 11, 5, fx.HOLY)
            for sx, sy in ((-30, -40), (28, -58), (-22, -80), (34, -20)):
                fx.sparkle(f, cx + sx, ground + sy, 3)
        elif i == 3:
            fx.pillar(f, cx, 0, ground, 16, fx.HOLY, seed=1, t=i)
            fx.light_blade(f, cx, ground - 70, 90, 72, 12, ramp=cool(fx.HOLY, 1))
            fx.burst(f, cx, ground, 6, 30, 12, cool(fx.HOLY, 1), seed=4, ry_scale=0.42, rot=12)
            fx.ring(f, cx, ground, 38, 15, 5, fx.GOLD)
            fx.particles(f, cx, ground - 6, 22, 4, 40, 0.35, fx.GOLD, seed=5, rise=30, ry_scale=0.5)
        elif i == 4:
            fx.pillar(f, cx, 0, ground, 9, cool(fx.HOLY, 1), seed=1, t=i)
            fx.light_blade(f, cx, ground - 70, 90, 72, 8, ramp=cool(fx.HOLY, 2))
            fx.ring(f, cx, ground, 46, 18, 4, cool(fx.GOLD, 1))
            fx.particles(f, cx, ground - 6, 22, 4, 44, 0.55, fx.GOLD, seed=5, rise=30, ry_scale=0.5)
        elif i == 5:
            fx.pillar(f, cx, 20, ground, 4, cool(fx.HOLY, 2), seed=1, t=i)
            fx.ring(f, cx, ground, 52, 20, 3, cool(fx.GOLD, 2))
            fx.particles(f, cx, ground - 6, 22, 4, 48, 0.72, fx.GOLD, seed=5, rise=30, ry_scale=0.5)
            f = px.dissolve(f, 0.8, 1)
        elif i == 6:
            fx.ring(f, cx, ground, 56, 22, 2, cool(fx.GOLD, 3))
            fx.particles(f, cx, ground - 6, 22, 4, 50, 0.86, fx.GOLD, seed=5, rise=30, ry_scale=0.5)
            f = px.dissolve(f, 0.55, 2)
        else:
            fx.particles(f, cx, ground - 6, 18, 4, 52, 1.0, cool(fx.GOLD, 1), seed=5, rise=30, ry_scale=0.5)
            f = px.dissolve(f, 0.4 if i == 7 else 0.2, 3)
        frames.append((f, 35 if i < 2 else 70))  # the blade lands right as Arthur does
    return frames


# ----------------------------------------------------------------------------- ult zone: holy seal (loop)
def seal():
    W = H = 91
    frames = []
    n = 8
    for i in range(n):
        f, cx, cy = frame(W, H)
        ph = i / n
        pulse = 0.5 + 0.5 * math.cos(ph * 2 * math.pi)
        fx.ring(f, cx, cy, 27, 27, 3, cool(fx.GOLD, 1), gaps=8, gap_phase=ph * 45)
        fx.ring(f, cx, cy, 22, 22, 2, cool(fx.GOLD, 2 if pulse < 0.5 else 1))
        fx.ring(f, cx, cy, 13, 13, 2, cool(fx.GOLD, 1), gaps=4, gap_phase=-ph * 90)
        # sword emblem: cross of light, brighter on the pulse
        ramp = fx.HOLY if pulse > 0.5 else cool(fx.HOLY, 1)
        fx.light_blade(f, cx, cy - 12, 90, 22, 3, ramp=ramp, guard=False)
        fx.light_blade(f, cx - 6, cy - 5, 0, 12, 2, ramp=ramp, guard=False)
        # rune ticks on the outer ring
        for k in range(8):
            a = math.radians(k * 45 + 22.5 + ph * 45)
            fx.sparkle(f, cx + math.cos(a) * 24.5, cy + math.sin(a) * 24.5, 1, cool(fx.HOLY, 1))
        # motes rising from the rim (looping)
        for k in range(6):
            a = math.radians(k * 60 + 15)
            t = (ph + k / 6) % 1
            x = cx + math.cos(a) * 20
            y = cy + math.sin(a) * 20 - t * 18
            if t < 0.85:
                fx.sparkle(f, x, y, 1 if t > 0.4 else 2, cool(fx.HOLY, 1 if t < 0.5 else 2))
        frames.append((f, 100))
    return frames


# ----------------------------------------------------------------------------- skill 2: orbiting flaming shields (loop)
FLAME_SHIELD = [  # small golden lion shield, bright face (seen lit by its own fire)
    "DCBBBBBCD",
    "CBAAAAABC",
    "CBBCBCBBC",
    "CBCgBgCBC",
    "CBBCACBBC",
    ".CBBCBBC.",
    ".CBBmBBC.",
    "..CBBBC..",
    "...CBC...",
    "....D....",
]


def whirl():
    W = H = 91
    n = 8
    frames = []
    sh = px.outline(px.grid(FLAME_SHIELD), grow_canvas=True)
    sh_back = px.recolor(sh, {"A": "B", "B": "C", "C": "D", "D": "E"})
    hole = np.zeros((H, W), bool)          # Arthur's body hides the back half of the orbit
    hole[H // 2 - 26:H // 2 + 12, W // 2 - 9:W // 2 + 10] = True
    for i in range(n):
        f, cx, cy = frame(W, H)
        back, front = px.new(W, H), px.new(W, H)
        ph = i / n
        # damage radius ring (true circle around the pivot, like base-game area rings)
        fx.ring(back, cx, cy, 28, 28, 2, cool(fx.GOLD, 1), gaps=6, gap_phase=ph * 60, rough=0.4, seed=i % 2)
        for k in range(3):
            ang = math.radians(ph * 120 + k * 120)       # clockwise on screen
            ox, oy = math.cos(ang) * 24, math.sin(ang) * 10 + 4
            is_front = math.sin(ang) >= -0.15
            layer = front if is_front else back
            # flame trail streams behind the direction of travel
            vx, vy = -math.sin(ang) * 24, math.cos(ang) * 10
            trail = math.degrees(math.atan2(-vy, -vx))
            fx.flame(layer, cx + ox, cy + oy, 12, 20, direction=trail, ramp=fx.FIRE, seed=k, t=i * 0.8)
            fx.flame(layer, cx + ox, cy + oy, 7, 12, direction=trail - 25, ramp=fx.FIRE[1:], seed=k + 5, t=i)
            img = sh if is_front else sh_back
            px.paste(layer, img, cx + ox - img.width // 2, cy + oy - img.height // 2)
        b = np.asarray(back).copy()
        b[hole, 3] = 0
        f.alpha_composite(Image.fromarray(b, "RGBA"))
        f.alpha_composite(front)
        frames.append((f, 50))
    return frames


# ----------------------------------------------------------------------------- oath buff: golden aura (loop, behind)
def oath():
    W = H = 71
    n = 6
    frames = []
    for i in range(n):
        f, cx, cy = frame(W, H)
        feet = cy + 11
        ph = i / n
        fx.ring(f, cx, feet, 13, 5, 2, cool(fx.GOLD, 1 if i % 2 == 0 else 2), gaps=5, gap_phase=ph * 72)
        for k in range(7):
            t = (ph + k / 7) % 1
            x = cx + [-11, -6, -1, 4, 9, 12, -13][k]
            y = feet - 2 - t * 30
            if t < 0.9:
                fx.sparkle(f, x, y, 2 if t < 0.35 else 1, cool(fx.HOLY, 0 if t < 0.35 else 1))
        frames.append((f, 90))
    return frames


EFFECTS = {
    "hok_arthur_slash": [("hit", slash_hit), ("small", slash_small)],
    "hok_arthur_ult_impact": [("impact", ult_impact)],
    "hok_arthur_seal": [("loop", seal)],
    "hok_arthur_whirl": [("loop", whirl)],
    "hok_arthur_oath": [("loop", oath)],
}


def build():
    out = {}
    for name, tags in EFFECTS.items():
        out[name] = [(tag, fn()) for tag, fn in tags]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="folder for contact sheets + GIFs")
    args = ap.parse_args()
    for name, tags in build().items():
        w, h = tags[0][1][0][0].size
        sheet, fanim = px.sheet_and_fanim(tags, w, h)
        px.save_png(sheet, os.path.join(EFX, name + "#sheet.png"))
        px.save_json(fanim, os.path.join(EFX, name + "#anim.fanim"))
        print(name, sheet.size, [(t, len(f)) for t, f in tags])
        if args.preview:
            from preview import contact, gifs
            contact(tags, os.path.join(args.preview, name + ".png"))
            gifs(tags, args.preview, name)


if __name__ == "__main__":
    main()
