"""Arthur's view effects, built from the generated art in assets/source/arthur_fx.

    python tools/art/arthur_fx.py [--preview out_dir]

The artwork comes from gpt-image-2 (via Codex, prompts in assets/source/arthur_fx/PROMPTS.md);
import_fx.py turns it into game-scale hard-edged pixels. This file only sizes, anchors, times
and composes it. The small oath aura is still drawn here with fx_lib.

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
import import_fx as gen  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import px  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
EFX = os.path.join(ROOT, "hok", "effects")
SLASH_CANVAS = 91


def frame(w, h):
    return px.new(w, h), w // 2, h // 2


def cool(ramp, k):
    """Drop the k hottest colours (fading effects cool down)."""
    return ramp[k:] if k < len(ramp) else ramp[-1:]


def one_shot(name, size_px, ms, canvas=SLASH_CANVAS):
    """A centred one-shot effect sized by its largest frame; frames keep their relative places."""
    bounds = [c["opaque_bounds_in_source_xywh"] for c in gen._manifest()[name]["source_cells"]]
    key = max(range(len(bounds)), key=lambda i: max(bounds[i][2:]))
    frames, _ = gen.sheet(name, gen.scale_for(name, key, size_px))
    return [(gen.centred(f, canvas), m) for f, m in zip(frames, ms)]


# ----------------------------------------------------------------------------- hits
def slash_hit():      # skill 1 lands: golden cross slash
    return one_shot("cross_slash", 72, [45, 55, 70, 60, 60, 60, 70])


def slash_small():    # empowered (oath) basic attack
    return one_shot("oath_slash", 44, [40, 55, 55, 50, 50])


def slash_spark():    # every basic attack: yellow-white flash
    return one_shot("hit_spark", 24, [35, 50, 50, 50])


# ----------------------------------------------------------------------------- ult: Excalibur strike
def ult_impact():
    """The blade of light falls on the target; the ground contact point is the unit's feet."""
    W, H = 101, 331
    scale = 62 / 220            # ground ring ~62 px wide (ult radius 24-26k)
    frames, (x0, y0) = gen.sheet("excalibur", scale)
    cells = gen.cells("excalibur")
    # ground contact: centre of the shockwave ring low in the cells; column: the falling sword
    ys = np.concatenate([np.nonzero(cells[i][..., 3] >= 0.5)[0] for i in (4, 5, 6)])
    ground_src = float(np.mean(ys[ys > 0.78 * cells[0].shape[0]]))
    col_src = float(np.nonzero(cells[0][..., 3] >= 0.5)[1].mean())
    anchor = ((col_src - x0) * scale, (ground_src - y0) * scale)
    feet_row = H // 2 + 11            # pivot row + 11.5
    out = []
    for f, ms in zip(frames, [35, 35, 60, 80, 80, 80, 90, 90]):
        canvas = px.new(W, H)
        px.paste(canvas, f, W // 2 - anchor[0], feet_row - anchor[1])
        out.append((canvas, ms))
    return out


# ----------------------------------------------------------------------------- ult zone: holy seal (loop)
def seal():
    """Ground seal, 54 px across (seal radius 26k), centred like the base-game area rings."""
    frames, _ = gen.sheet("holy_seal", gen.scale_for("holy_seal", 0, 54, "w"))
    return [(gen.centred(f, 71, gen.circle_centre(f)), 120) for f in frames]


# ----------------------------------------------------------------------------- skill 2: orbiting flaming shields (loop)
def whirl():
    """Three flaming lion shields orbit Arthur for 5 s inside the golden damage ring.

    The buff is drawn in front of him (z 1); shields on the far half of the orbit are dimmed and
    cut out where his body is, so they pass behind him."""
    W = H = 91
    n = 8
    shields, _ = gen.sheet("flaming_shield", gen.scale_for("flaming_shield", 0, 24, "w"), None)
    shield_px = [np.asarray(s) for s in shields]
    rings, _ = gen.sheet("whirl_ring", gen.scale_for("whirl_ring", 0, 58, "w"))
    # the shield body (not the flickering flames) is the anchor: the right part of the sprite
    sw, sh = shields[0].size
    anchor = (sw * 0.72, sh * 0.5)
    hole = np.zeros((H, W), bool)
    hole[H // 2 - 26:H // 2 + 12, W // 2 - 9:W // 2 + 10] = True
    frames = []
    for i in range(n):
        back, front = px.new(W, H), px.new(W, H)
        ring = rings[i % len(rings)]
        back.alpha_composite(gen.centred(ring, W, gen.circle_centre(ring)))
        for k in range(3):
            ang = math.radians(i / n * 120 + k * 120)        # clockwise on screen
            ox, oy = math.cos(ang) * 25, math.sin(ang) * 9 + 5
            far = math.sin(ang) < -0.15
            a = shield_px[(i + k) % len(shield_px)].copy()
            if -math.sin(ang) < 0:          # moving left: flames must trail to the right
                a = a[:, ::-1]
                ax = sw - anchor[0]
            else:
                ax = anchor[0]
            if far:
                a[..., :3] = (a[..., :3] * 0.72).astype(np.uint8)
            img = Image.fromarray(a, "RGBA")
            px.paste(back if far else front, img, W // 2 + ox - ax, H // 2 + oy - anchor[1])
        b = np.asarray(back).copy()
        b[hole, 3] = 0
        f = Image.fromarray(b, "RGBA")
        f.alpha_composite(front)
        frames.append((f, 55))
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
    "hok_arthur_slash": [("hit", slash_hit), ("small", slash_small), ("spark", slash_spark)],
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
