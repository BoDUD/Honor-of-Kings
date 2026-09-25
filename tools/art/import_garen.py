#!/usr/bin/env python3
"""Import Garen's generated source art (assets/source/garen, see PROMPTS.md) into game sprites.

    python tools/art/import_garen.py [--review DIR]

Writes (exported sheet format: name#sheet.png + name#anim.fanim, frames centred on the unit)
  league/champions/league_garen       idle run attack q_attack skill spin ult hit dead
  league/effects/league_garen_hits    spark q
  league/effects/league_garen_buffs   decisive courage
  league/effects/league_garen_spin    loop
  league/effects/league_garen_r       impact

Body: each strip gets its own scale so Garen measures 36 px from hair to soles; the feet sit
11.5 px below the frame centre (the base-game convention). Horizontally every frame is lined up
by its feet with idle frame 0 (run and spin by the head, airborne frames follow their
neighbours), so the generator's uneven frame spacing does not make him slide. Pixels: area
downscale, hard alpha, one shared palette, 1 px dark outline.
Effects: own palette each, no outline, anchored on their impact point / ring centre.
--review DIR writes one alignment sheet per strip (pivot + feet lines, idle silhouette in red).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "garen")
MOD = os.path.join(ROOT, "league")

HEIGHT = 36.0   # px from hair to soles, standing (base humans ~31, ogre ~38: a big knight)
FEET = 11.5     # feet (bottom edge) below the pivot
SUP = 4         # alignment works at 4x game resolution
BAND = 12       # px of legs used to line frames up

# tall: source px from hair to soles in that strip (measured on a standing frame)
# anchor: feet = line the legs up with idle f0; head = keep the head still (loops) at
#         head=("idle", dx): dx px ahead of idle's head, or ("abs", x): x px from the pivot
# free: frames placed by the drawn spacing, corrected like their aligned neighbours (used where
#       a sword tip or burst touches the ground and would be mistaken for a foot)
# dx: extra shift per frame in source px (+ = right), to keep the planted foot still
# ground: per-frame lowest pixel, or "strip" = the strip's median (keeps the run bounce)
CHAR = {
    "idle":     dict(n=6, tall=272, ms=[130] * 6, anchor="feet"),
    "run":      dict(n=6, tall=259, ms=[85] * 6, anchor="head", head=("idle", 2.0), ground="strip"),
    "attack":   dict(n=6, tall=289, ms=[60, 70, 70, 60, 55, 52], anchor="feet", free=[1, 2, 3, 4],
                     dx=[0, -12, 14, 0, -11, 0]),          # front foot planted, back foot steps
    "q_attack": dict(n=7, tall=272, ms=[50, 50, 55, 55, 90, 100, 100], anchor="feet", free=[1, 2, 3, 4]),
    "skill":    dict(n=4, tall=355, ms=[80, 90, 80, 83], anchor="feet"),
    "spin":     dict(n=8, tall=196, ms=[54] * 8, anchor="head", head=("abs", 1.0)),
    "ult":      dict(n=8, tall=267, ms=[80, 80, 90, 80, 70, 90, 90, 87], anchor="feet"),
    "hit":      dict(n=2, tall=560, ms=[70, 70], anchor="feet", free=[0], dx=[-120, 0]),  # back foot planted
    "dead":     dict(n=7, tall=285, ms=[100, 100, 120, 160, 120, 120, 400], anchor="feet", free=[5, 6]),
}
CHAR_COLORS = 64


def src(name):
    return os.path.join(SRC, f"garen_{name}.png")


# ----------------------------------------------------------------------------- measuring
def hair_mask(a):
    rgb = a[..., :3] * 255
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return ((a[..., 3] > 0.5) & (r >= 36) & (r <= 140) & (g >= 18) & (g <= 95) & (b <= 85)
            & (r - g >= 12) & (r - b >= 18))


def head_x(fr):
    """x (strip coordinates) of the head: median of the topmost hair cluster."""
    hy, hx = np.nonzero(hair_mask(fr.a))
    top = hy.min()
    return float(np.median(hx[hy < top + 60])) + fr.ox


# ----------------------------------------------------------------------------- characters
def load_char():
    """-> {tag: dict(frames, s, gy, pitch, ax)}: per frame the ground edge gy and the strip x
    that becomes the pivot column."""
    strips = {}
    for tag, c in CHAR.items():
        img = G.load_rgba(src(tag))
        frames = G.split_strip(img, c["n"])
        s = HEIGHT / c["tall"]
        grounds = [f.ground for f in frames]
        free = set(c.get("free", []))
        fixed = [g for i, g in enumerate(grounds) if i not in free]
        if c.get("ground") == "strip":
            grounds = [float(np.median(fixed))] * len(frames)
        elif tag == "q_attack":     # airborne frames keep their height above the landing ground
            grounds = [g if i not in free else float(np.median(fixed)) for i, g in enumerate(grounds)]
        pitch = img.shape[1] / c["n"]
        strips[tag] = dict(frames=frames, s=s, gy=grounds, pitch=pitch)
    # idle f0 defines the pivot: the middle of its stance
    idle = strips["idle"]
    f0 = idle["frames"][0]
    idle_ax0 = G.feet_mid(f0, idle["s"])
    ref = G.leg_band(f0, idle["s"], idle_ax0, idle["gy"][0], BAND, sup=SUP)
    idle_head = (head_x(f0) - idle_ax0) * idle["s"]         # head position in px, pivot-relative

    for tag, st in strips.items():
        c, s = CHAR[tag], st["s"]
        n = len(st["frames"])
        free = set(c.get("free", []))
        ax = [None] * n
        if c["anchor"] == "head":
            ref_kind, dx = c["head"]
            at = (idle_head if ref_kind == "idle" else 0.0) + dx
            for i, fr in enumerate(st["frames"]):
                ax[i] = head_x(fr) - at / s
        else:
            for i, fr in enumerate(st["frames"]):
                if i in free:
                    continue
                guess = G.feet_mid(fr, s)
                band = G.leg_band(fr, s, guess, st["gy"][i], BAND, sup=SUP)
                ax[i] = guess + G.best_shift(ref, band, 10 * SUP) / (SUP * s)
            # free frames: drawn spacing plus the correction of the aligned neighbours
            grid = [(i + 0.5) * st["pitch"] for i in range(n)]
            known = [i for i in range(n) if ax[i] is not None]
            corr = np.interp(range(n), known, [ax[i] - grid[i] for i in known])
            for i in free:
                ax[i] = grid[i] + corr[i]
        for i, d in enumerate(c.get("dx", [])):
            ax[i] -= d
        st["ax"] = ax
    return strips


def build_char(strips):
    raw = {}
    for tag, st in strips.items():
        raw[tag] = [G.render(fr, st["s"], st["s"], st["ax"][i], st["gy"][i], 0.0, FEET, cut=0.5)
                    for i, fr in enumerate(st["frames"])]
    pal = G.Palette([r[0] for rs in raw.values() for r in rs], colors=CHAR_COLORS)
    out = {}
    for tag, rs in raw.items():
        frames = []
        for (arr, u0, r0), ms in zip(rs, CHAR[tag]["ms"]):
            arr = G.drop_lonely(G.outline(pal.apply(arr)))
            frames.append((G.centre_frame(arr, u0, r0), ms))
        out[tag] = frames
    return out


# ----------------------------------------------------------------------------- effects
def wide_rows_centre(fr, frac=0.6, thresh=0.15):
    """Centre (strip coords) of the rows whose solid run is wide - the flat ground ring."""
    al = fr.a[..., 3] > thresh
    xs_any = np.nonzero(al.any(0))[0]
    width = xs_any.max() - xs_any.min() + 1
    rows = [y for y in range(al.shape[0]) if al[y].any() and
            (np.nonzero(al[y])[0].max() - np.nonzero(al[y])[0].min() + 1) >= frac * width]
    y0, y1 = min(rows), max(rows) + 1
    sub = al[y0:y1]
    xs = np.nonzero(sub.any(0))[0]
    return (xs.min() + xs.max() + 1) / 2.0 + fr.ox, (y0 + y1) / 2.0 + fr.oy


def core_x(fr, level=0.85):
    """x of the white-hot core (brightness-weighted, strip coords)."""
    a = fr.a
    lum = (a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)) * a[..., 3]
    ys, xs = np.nonzero(lum > level)
    return float(xs.mean()) + fr.ox


def biggest_blob_centre(fr, thresh=0.3):
    lab, n = G.label(fr.a[..., 3] > thresh)
    sizes = np.bincount(lab.ravel())[1:]
    ys, xs = np.nonzero(lab == int(sizes.argmax()) + 1)
    return (xs.min() + xs.max() + 1) / 2.0 + fr.ox, (ys.min() + ys.max() + 1) / 2.0 + fr.oy


def bbox_centre(fr, thresh=0.15):
    x0, y0, x1, y1 = fr.bbox(thresh)
    return (x0 + x1) / 2.0, (y0 + y1) / 2.0


# fixed y values are source px measured on the generated strips: the spark centre line, the
# point where the Q slash lands, the R ground line (85% of the cell height, as prompted)
def anchors_spark(frames):
    return [(bbox_centre(f)[0], 362.0) for f in frames]


def anchors_q_hit(frames):
    return [(core_x(f), 520.0) for f in frames]


def anchors_q_ready(frames):
    return [wide_rows_centre(f) for f in frames]


def anchors_courage(frames):
    return [biggest_blob_centre(f) for f in frames]


def anchors_spin(frames):
    c = [bbox_centre(f) for f in frames]
    n = len(frames)
    x0, x1 = c[0][0], c[-1][0]
    y = float(np.mean([p[1] for p in c]))
    return [(x0 + (x1 - x0) * i / (n - 1), y) for i in range(n)]


def anchors_r(frames):
    out = []
    for i, f in enumerate(frames):
        x = core_x(f) if i <= 6 else wide_rows_centre(f, frac=0.5)[0]
        out.append((x, 711.0))
    return out


# sprite: {tag: (source strip, frames, scale x/y, anchor rule, pivot-relative spot, ms, cut)}
FX = {
    "league_garen_hits": {
        "spark": ("fx_hit", 4, (0.05, 0.05), anchors_spark, (0, -6), [50, 60, 60, 60], 0.4),
        "q": ("fx_q_hit", 6, (0.08, 0.08), anchors_q_hit, (0, -3), [60, 60, 70, 90, 90, 90], 0.4),
    },
    "league_garen_buffs": {
        "decisive": ("fx_q_ready", 6, (0.095, 0.095), anchors_q_ready, (0, 10), [100] * 6, 0.4),
        "courage": ("fx_courage", 6, (0.128, 0.128), anchors_courage, (0, -6), [90] * 6, 0.4),
    },
    "league_garen_spin": {
        "loop": ("fx_spin", 8, (0.32, 0.24), anchors_spin, (0, -4), [54] * 8, 0.4),
    },
    "league_garen_r": {
        "impact": ("fx_r", 9, (0.18, 0.18), anchors_r, (0, 10), [100, 60, 80, 80, 80, 80, 80, 80, 80], 0.4),
    },
}
FX_COLORS = 32


def build_fx():
    sprites = {}
    for sprite, tags in FX.items():
        raw = {}
        for tag, (strip, n, (sx, sy), rule, (X0, Y0), ms, cut) in tags.items():
            frames = G.split_strip(G.load_rgba(src(strip)), n, blob_thresh=0.05)
            raw[tag] = [(G.render(f, sx, sy, ax, ay, X0, Y0, cut=cut, keep=0.9), m)
                        for f, (ax, ay), m in zip(frames, rule(frames), ms)]
        pal = G.Palette([r[0][0] for rs in raw.values() for r in rs], colors=FX_COLORS, extra=())
        sprites[sprite] = {tag: [(G.centre_frame(pal.apply(arr), u0, r0), m) for (arr, u0, r0), m in rs]
                           for tag, rs in raw.items()}
    return sprites


# ----------------------------------------------------------------------------- review
ARENA = (92, 98, 86, 255)


def review(char, out_dir, z=4):
    """One PNG per tag: frames on the arena colour, pivot column + feet row lines, idle f0
    silhouette in red for comparison."""
    os.makedirs(G.lp(out_dir), exist_ok=True)
    idle0 = char["idle"][0][0]
    ih, iw = idle0.shape[:2]
    op = idle0[..., 3] > 0
    p = np.pad(op, 1)
    edge = np.nonzero(op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]))
    for tag, frames in char.items():
        hw = max(f.shape[1] for f, _ in frames) // 2
        hh = max(max(f.shape[0] for f, _ in frames) // 2, 24)
        W, H = 2 * hw + 1, 2 * hh + 1
        row = Image.new("RGBA", ((W + 2) * len(frames) * z, H * z), (30, 30, 30, 255))
        for i, (f, _) in enumerate(frames):
            cell = Image.new("RGBA", (W, H), ARENA)
            fh, fw = f.shape[:2]
            cell.alpha_composite(Image.fromarray(f, "RGBA"), (hw - fw // 2, hh - fh // 2))
            big = cell.resize((W * z, H * z), Image.NEAREST)
            d = ImageDraw.Draw(big)
            for y, x in zip(*edge):                     # idle f0 silhouette
                X, Y = (hw - iw // 2 + x) * z, (hh - ih // 2 + y) * z
                d.rectangle((X + 1, Y + 1, X + 2, Y + 2), fill=(255, 60, 60, 255))
            d.line(((hw * z + z // 2), 0, (hw * z + z // 2), H * z), fill=(255, 255, 0, 120))
            d.line((0, (hh + 12) * z, W * z, (hh + 12) * z), fill=(0, 255, 255, 160))
            row.paste(big, (i * (W + 2) * z, 0))
        row.save(G.lp(os.path.join(out_dir, f"review_{tag}.png")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write alignment review sheets to this folder")
    args = ap.parse_args()
    strips = load_char()
    for tag, st in strips.items():
        rel = [f"{(a - (i + 0.5) * st['pitch']) * st['s']:+.1f}" for i, a in enumerate(st["ax"])]
        print(f"{tag:9s} scale {st['s']:.4f}  pivot vs cell centre (px): {' '.join(rel)}")
    char = build_char(strips)
    w, h = G.write_sheet(os.path.join(MOD, "champions", "league_garen"), char)
    print(f"league/champions/league_garen#sheet.png {w}x{h}, "
          f"{sum(len(v) for v in char.values())} frames")
    for sprite, tags in build_fx().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " +
              ", ".join(f"{t} {len(v)}f" for t, v in tags.items()))
    if args.review:
        review(char, args.review)


if __name__ == "__main__":
    main()
