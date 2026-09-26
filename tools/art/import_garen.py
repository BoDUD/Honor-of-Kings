#!/usr/bin/env python3
"""Import Garen's generated source art (assets/source/garen; prompts in ../CHIBI_REDRAW.md) into game sprites.

    python tools/art/import_garen.py [--review DIR]

Writes (exported sheet format: name#sheet.png + name#anim.fanim, frames centred on the unit)
  league/champions/league_garen       idle run attack q_attack skill spin ult hit dead
  league/effects/league_garen_hits    spark q
  league/effects/league_garen_buffs   decisive courage
  league/effects/league_garen_spin    loop
  league/effects/league_garen_r       impact

Body: the chibi redraw - every strip is drawn from the same design reference (garen_ref_chibi.png)
and, where League has the clip, from a front-view pose render of it with the head enlarged to TFM2
proportions (pose_ref.py --head 2.0 --legs 0.8). Each strip gets its own scale so Garen's head is as
big as in idle (~36 px tall); the feet sit 11.5 px below the frame centre (the base-game
convention). Horizontally, idle stands on the middle of its stance, skill and hit line their legs up
with idle, and the League-drawn strips put each frame's head where League's skeleton has it for
that frame (tools/lol/pose_ref.py --track, same camera), so their own body motion (lunges, leaps,
the spin's lean) comes out as in the game. Pixels: area downscale, hard alpha, one shared palette,
1 px dark outline.
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

# tall: source px of his standing height (hair to soles, idle stance) at that strip's drawing size.
#       GPT drew every strip at its own size and with slightly different head-to-body ratios, so
#       each strip is scaled to make his HEAD as big as in idle (the most visible part of a chibi;
#       its size changing between actions reads as the hero growing and shrinking): idle's head
#       matched over each frame at several scales, checked side by side at source size (attack
#       and death by face and hair width: their heads turn and bow, the match was unsure)
# anchor: feet = line the legs up with idle f0 (idle f0 itself: middle of its stance)
#         feetmid = head=("track", [x per frame]): put the middle of both feet there instead (the
#                spin: its body leans less than League's, so the head path would make it wobble)
#         head = head=("track", [x per frame]): put each frame's head x px from the pivot, taken
#                from League's skeleton for the frame times of the pose reference, big-head
#                skeleton and camera of the references (pose_ref.py --mirror --yaw 55 --pitch 25
#                --head 2.0 --legs 0.8 --track 36), plus one shift that puts idle's drawn head where
#                League has it (LEAGUE_IDLE_HEAD)
# ground: per-frame lowest pixel, or "strip" = median of the grounded frames (keeps a run
#         bounce; ignores a sword tip or burst below the feet)
# air: frames in the air; they keep their drawn height above the ground of the others
CHAR = {
    "idle":     dict(n=6, tall=300, ms=[150] * 6, anchor="feet"),
    # League Run: a walk, 8 frames over its 0.933 s cycle (0-817 ms)
    "run":      dict(n=8, tall=255, ms=[117] * 8, anchor="head", ground="strip",
                     head=("track", [5.6, 6.4, 5.7, 4.7, 5.0, 5.5, 5.1, 4.6])),
    # Attack_01 0/300/333/367/400/560 ms; damage lands in the slash frame (tick 13). League lunges
    # 15 px (raw -4.9, 0.3, 3.0, 9.4, 10.2, 9.9) and blends back over 0.2 s; a sprite snaps back to
    # idle at once, so the lunge is kept at 70% around idle's head (the look of the previous round)
    "attack":   dict(n=6, tall=240, ms=[50, 60, 50, 60, 70, 77], anchor="head", ground="strip",
                     head=("track", [-1.9, 0.7, 2.6, 7.0, 7.6, 7.4])),
    # spell1 (Decisive Strike) 0-810 ms; 500 ms = the 30-tick CasterAnimation, impact at 200 ms;
    # the leap likewise at 70% (raw -4.9, -4.8, -4.6, -3.4, 8.7, 7.2, 1.6)
    "q_attack": dict(n=7, tall=237, ms=[45, 45, 50, 60, 90, 110, 100], anchor="head", ground="strip",
                     air=[0, 1, 2, 3], head=("track", [-3.0, -2.9, -2.8, -1.9, 6.6, 5.5, 1.6])),
    "skill":    dict(n=4, tall=417, ms=[80, 90, 80, 83], anchor="feet"),
    # spell3 one turn (8 x 45 deg); League's pelvis stays put and the feet's middle within 2 px
    "spin":     dict(n=8, tall=219, ms=[50] * 8, anchor="feetmid", ground="strip",
                     head=("track", [-0.4, 0.6, 1.3, 1.0, 0.2, -1.0, -1.8, -1.8])),
    # spell4: leap forward and slam. League starts it 23 px behind the unit and ends 2 px ahead;
    # re-based with a ramp so the first frame stands where idle does, and the leap kept at 65%
    # (-23.2, -30.2, -5.8, 9.0, 8.9, 9.0, 10.4, 3.5 raw) so the body lands near the unit; the slam
    # frame (4th) comes at 320 ms, when the giant sword lands
    "ult":      dict(n=8, tall=188, ms=[90, 110, 120, 90, 90, 80, 50, 37], anchor="head", ground="strip",
                     air=[2], head=("track", [1.5, -5.4, 8.2, 15.5, 13.2, 11.0, 9.6, 2.8])),
    "hit":      dict(n=2, tall=666, ms=[70, 70], anchor="feet", ground="strip"),
    # Death 0-2340 ms (raw -1.0 ... -0.6), re-based by +2.5 so the first frame stands where idle does
    "dead":     dict(n=7, tall=294, ms=[120, 150, 150, 160, 160, 200, 400], anchor="head",
                     head=("track", [1.5, -9.0, -12.9, -15.6, -14.5, -0.1, 1.9])),
}
LEAGUE_IDLE_HEAD = 1.5   # League idle1@0: head joint x, px from the unit (same camera and skeleton)
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
    """x (strip coordinates) of the head: median of the biggest hair blob in the upper body
    (a raised sword grip can be higher than the head and has the same brown)."""
    x0, y0, x1, y1 = fr.bbox()
    lab, n = G.label(hair_mask(fr.a))
    sizes = np.bincount(lab.ravel())[1:]
    for k in np.argsort(sizes)[::-1] + 1:
        ys, xs = np.nonzero(lab == k)
        if ys.min() + fr.oy < y0 + 0.6 * (y1 - y0):
            return float(np.median(xs)) + fr.ox
    raise ValueError("no head found")


# ----------------------------------------------------------------------------- characters
def load_char():
    """-> {tag: dict(frames, s, gy, ax)}: per frame the ground edge gy and the strip x that
    becomes the pivot column."""
    strips = {}
    for tag, c in CHAR.items():
        frames = G.split_strip(G.load_rgba(src(tag)), c["n"])
        air = set(c.get("air", []))
        grounds = [f.ground for f in frames]
        base = float(np.median([g for i, g in enumerate(grounds) if i not in air]))
        if c.get("ground") == "strip":
            grounds = [base] * len(frames)
        else:
            grounds = [base if i in air else g for i, g in enumerate(grounds)]
        strips[tag] = dict(frames=frames, s=HEIGHT / c["tall"], gy=grounds)
    idle = strips["idle"]
    f0 = idle["frames"][0]
    ref = G.leg_band(f0, idle["s"], G.feet_mid(f0, idle["s"]), idle["gy"][0], BAND, sup=SUP)
    for tag, st in strips.items():
        c, s = CHAR[tag], st["s"]
        if c["anchor"] == "feetmid":
            track = c["head"][1]
            st["ax"] = [G.feet_mid(fr, s, px=3.0) - track[i] / s for i, fr in enumerate(st["frames"])]
        elif c["anchor"] != "head":
            ax = []
            for i, fr in enumerate(st["frames"]):
                guess = G.feet_mid(fr, s)
                band = G.leg_band(fr, s, guess, st["gy"][i], BAND, sup=SUP)
                ax.append(guess + G.best_shift(ref, band, 10 * SUP) / (SUP * s))
            st["ax"] = ax
    # where idle's own drawn head stands against its feet, relative to League's idle head
    shift = (head_x(f0) - idle["ax"][0]) * idle["s"] - LEAGUE_IDLE_HEAD
    for tag, st in strips.items():
        c, s = CHAR[tag], st["s"]
        if c["anchor"] == "head":
            track = c["head"][1]
            st["ax"] = [head_x(fr) - (track[i] + shift) / s for i, fr in enumerate(st["frames"])]
    print(f"idle head vs League: {shift:+.2f} px (added to every head track)")
    return strips


def build_char(strips):
    raw = {}
    for tag, st in strips.items():
        raw[tag] = [G.render(fr, st["s"], st["s"], st["ax"][i], st["gy"][i], 0.0, FEET, cut=0.5)
                    for i, fr in enumerate(st["frames"])]
        assert len(raw[tag]) == len(CHAR[tag]["ms"]), tag
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
        print(f"{tag:9s} scale {st['s']:.4f}  {len(st['frames'])} frames")
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
