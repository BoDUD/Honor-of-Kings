#!/usr/bin/env python3
"""Import Ashe's generated source art (assets/source/ashe; prompts in ../CHIBI_REDRAW.md) into game sprites.

    python tools/art/import_ashe.py [--body] [--review DIR]

Writes (exported sheet format: name#sheet.png + name#anim.fanim, frames centred on the unit)
  league/champions/league_ashe       idle run attack q_attack skill skill2 ult hit dead   (only with --body)
  league/effects/league_ashe_fx      arrow volley flurry hit focus
  league/effects/league_ashe_r       arrow hit

The body sheet now comes from the native-size redraw (tools/art/import_native.py, drawn over
this round's frames); --body writes this round-1 body again.
Body: the chibi redraw - every strip was drawn from one design reference (ashe_ref_chibi.png) and
a front-view render of League's own clip at fixed times with the head enlarged to TFM2 proportions
(pose_ref.py --head 2.0 --legs 0.8). GPT drew each strip at its own size, so each gets its own
scale: `tall` is her standing height at that strip's size (hood tip to soles, 34 px in game), set so
her head is as big as in idle. The feet sit 11.5 px below the frame centre (base-game convention).
Horizontally, idle and hit stand on the middle of their stance / line their legs up with idle;
every other strip puts each frame's head where League's skeleton has it at that frame's time
(pose_ref.py --track, camera yaw 55, pitch 25, not mirrored), shifted once so idle's own head lands
where League puts it - so lunges, the wide Q stance and the fall of the death come out as in the
game and nothing jumps against idle.
Pixels: GPT drew her ~12 source px per game px with thin bright details (crystal bow, silver hair
on a black hood), which an area average turns into brown mud. So every game pixel takes one
colour of a shared 56-colour palette - the colour covering most of it, with the bow's ice-blue,
the hair, skin and gold weighted up (strips.render_vote) - then a 1 px dark outline that skips the
bow (it is all edge; outlined it turned black).
Effects: own palette each, no outline, anchored on the arrow / impact point / ring centre.
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

SRC = os.path.join(ROOT, "assets", "source", "ashe")
MOD = os.path.join(ROOT, "league")

HEIGHT = 34.0   # px from hood tip to soles, standing
FEET = 11.5     # feet (bottom edge) below the pivot
SUP = 4         # alignment works at 4x game resolution
BAND = 12       # px of legs used to line frames up
LEAGUE_IDLE_HEAD = 0.4   # League idle1@0: head joint x, px from the unit

# tall: source px of her standing height (hood tip to soles) at that strip's drawing size. GPT
#       drew every strip at its own size and with slightly different head-to-body ratios, so each
#       strip is scaled to make her HEAD as big as in idle (the most visible part of a chibi; its
#       size changing between actions reads as the hero growing and shrinking): idle's head matched
#       over each frame at several scales (normalized cross-correlation), checked side by side
# anchor: feet = line the legs up with idle f0 (idle f0 itself: middle of its stance)
#         head = put each frame's head `head[i]` px from the pivot: League's head joint at the
#                frame times of the pose reference, camera of the references, from the big-head
#                skeleton they were drawn from (pose_ref.py --head 2.0 --legs 0.8 --track 34)
# ground: per-frame lowest pixel, or "strip" = median of the grounded frames
# air: frames in the air; they keep their drawn height above the ground of the others
# specks: drop detached blobs up to this many game px (loose sparkles around the body)
CHAR = {
    # idle1 0-1333 ms: the 1.6 s breathing loop
    "idle":     dict(n=6, tall=424, ms=[267] * 6, anchor="feet"),
    # Run2 (ashe_run_jog) 0-875 ms: a run, both feet off the ground in frames 3 and 7
    "run":      dict(n=8, tall=242, ms=[125] * 8, anchor="head", ground="strip", air=[2, 6],
                     head=[3.1, 3.1, 2.9, 2.7, 2.4, 1.9, 2.0, 2.5]),
    # idle>attack1 blend, attack1 0/367/533/800, attack1>idle blend; the arrow leaves in frame 3 (tick 9)
    "attack":   dict(n=6, tall=411, ms=[50, 100, 60, 60, 65, 65], anchor="head", ground="strip",
                     head=[0.5, 0.7, 0.9, 1.3, 2.0, 1.5]),
    # idle>spell1 blend, spell1 0/67/267/500, spell1>idle blend: she steps back into the wide stance
    "q_attack": dict(n=6, tall=416, ms=[50, 80, 60, 70, 70, 70], anchor="head", ground="strip",
                     head=[-0.6, -2.6, -2.8, -3.8, -5.5, -2.2]),
    # idle, Ashe_spell1_IN 83/167/250/333, blend back
    "skill":    dict(n=6, tall=343, ms=[67] * 6, anchor="head", ground="strip", specks=12,
                     head=[0.4, 0.3, -0.3, -1.5, -2.5, -0.6]),
    # idle>spell2 blend, spell2 0/267/333/450/700, blend back; the volley leaves in frame 4 (tick 12)
    "skill2":   dict(n=7, tall=259, ms=[60, 70, 70, 60, 70, 90, 80], anchor="head", ground="strip",
                     head=[0.5, 0.7, 0.8, 1.1, 1.4, 1.3, 0.9]),
    # idle>crit1 blend, crit1 0/200/300/367/500/700, blend back; the crystal arrow leaves in frame 5 (tick 22)
    "ult":      dict(n=8, tall=343, ms=[60, 100, 100, 100, 70, 90, 100, 80], anchor="head", ground="strip",
                     head=[0.5, 0.7, 0.6, 0.5, 0.7, 1.2, 2.2, 1.5]),
    "hit":      dict(n=2, tall=780, ms=[120, 120], anchor="feet", ground="strip"),
    # death 0/500/700/900/1100/1300/1900 ms: struck, thrown back, lands and lies. League throws her
    # 29 px back (head 0.9 -> -29.4); kept at 75% so the body stays near where she fell
    "dead":     dict(n=7, tall=297, ms=[100, 120, 120, 120, 150, 200, 400], anchor="head", air=[3, 4],
                     head=[0.7, -8.3, -10.7, -12.2, -18.8, -22.1, -22.1]),
}
CHAR_COLORS = 56
# palette entries per colour class (the rest come from the other pixels) and each class's vote
# weight: without their own entries the lavender hair merged into light skin
SHARE = {"light": 4, "blue": 8, "gold": 7, "skin": 5}
WEIGHT = {"blue": 2.2, "light": 2.3, "skin": 1.3, "gold": 1.3, "other": 1.0}


def src(name):
    return os.path.join(SRC, f"ashe_{name}.png")


# ----------------------------------------------------------------------------- measuring
def hair_mask(a):
    """Her silver-lavender hair: light, low-saturation pixels (the bow is saturated ice-blue)."""
    rgb = a[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    return (a[..., 3] > 0.5) & (mn >= 150) & (mx - mn <= 60) & (rgb[..., 2] >= rgb[..., 1] - 4)


def head_x(fr, min_px=40):
    """x (strip coordinates) of the head: median of the biggest hair blob in the upper body;
    None if no hair shows (she lies face down)."""
    x0, y0, x1, y1 = fr.bbox()
    lab, n = G.label(hair_mask(fr.a))
    sizes = np.bincount(lab.ravel())[1:]
    for k in np.argsort(sizes)[::-1] + 1:
        ys, xs = np.nonzero(lab == k)
        if len(xs) < min_px:
            break
        if ys.min() + fr.oy < y0 + 0.6 * (y1 - y0):
            return float(np.median(xs)) + fr.ox
    return None


def heads(frames):
    """Head x per frame; a frame without visible hair takes its neighbours' head offset from the
    left edge of the body (the head leads the fall)."""
    hx = [head_x(f) for f in frames]
    for i, h in enumerate(hx):
        if h is None:
            rel = [hx[j] - frames[j].bbox()[0] for j in (i - 1, i + 1) if 0 <= j < len(hx) and hx[j] is not None]
            hx[i] = frames[i].bbox()[0] + float(np.mean(rel))
    return hx


def drop_specks(arr, max_px):
    """Clear connected blobs of at most max_px opaque pixels that are not the body."""
    lab, n = G.label(arr[..., 3] > 0)
    if n < 2:
        return arr
    sizes = np.bincount(lab.ravel())[1:]
    out = arr.copy()
    for k, size in enumerate(sizes, 1):
        if size <= max_px and k != int(sizes.argmax()) + 1:
            out[lab == k] = 0
    return out


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
        if c["anchor"] == "feet":
            ax = []
            for i, fr in enumerate(st["frames"]):
                guess = G.feet_mid(fr, s)
                band = G.leg_band(fr, s, guess, st["gy"][i], BAND, sup=SUP)
                ax.append(guess + G.best_shift(ref, band, 10 * SUP) / (SUP * s))
            st["ax"] = ax
    # where idle's own head stands against its feet, relative to League's idle head
    shift = (head_x(f0) - idle["ax"][0]) * idle["s"] - LEAGUE_IDLE_HEAD
    for tag, st in strips.items():
        c, s = CHAR[tag], st["s"]
        if c["anchor"] == "head":
            st["ax"] = [h - (c["head"][i] + shift) / s for i, h in enumerate(heads(st["frames"]))]
    return strips, shift


def colour_classes(rgb):
    """(N, 3) uint8 -> class per pixel: blue (the crystal bow and arrows), light (silver hair,
    highlights), skin, gold, other."""
    c = rgb.astype(np.float32) / 255.0
    mx, mn = c.max(1), c.min(1)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    r, g, b = c[:, 0], c[:, 1], c[:, 2]
    d = np.maximum(mx - mn, 1e-4)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    out = np.full(len(c), "other", object)
    out[(h >= 0.10) & (h <= 0.17) & (sat > 0.45) & (mx > 0.45)] = "gold"
    out[(h >= 0.02) & (h <= 0.10) & (sat > 0.18) & (sat < 0.6) & (mx > 0.55)] = "skin"
    out[(mx > 0.72) & (sat < 0.25)] = "light"
    out[(h >= 0.50) & (h <= 0.64) & (sat > 0.40) & (mx > 0.45)] = "blue"
    return out


def char_palette(strips):
    """One palette for every body frame: a median cut per salient class, the rest from the others."""
    pix = []
    for st in strips.values():
        for fr in st["frames"]:
            pix.append((fr.a[..., :3][fr.a[..., 3] > 0.5] * 255).astype(np.uint8)[::3])
    pix = np.concatenate(pix)
    cls = colour_classes(pix)
    parts = [G.median_cut(pix[cls == c], n) for c, n in SHARE.items() if (cls == c).sum() > 50]
    parts.append(G.median_cut(pix[cls == "other"], CHAR_COLORS - sum(len(p) for p in parts)))
    pal = np.concatenate(parts)
    weights = np.array([WEIGHT[c] for c in colour_classes(pal.astype(np.uint8))], np.float32)
    return pal, weights


def build_char(strips):
    pal, weights = char_palette(strips)
    bow = [tuple(int(v) for v in c) for c, k in zip(pal, colour_classes(pal.astype(np.uint8))) if k == "blue"]
    out = {}
    for tag, st in strips.items():
        frames = []
        for i, (fr, ms) in enumerate(zip(st["frames"], CHAR[tag]["ms"])):
            arr, u0, r0 = G.render_vote(fr, st["s"], st["s"], st["ax"][i], st["gy"][i], 0.0, FEET, pal, weights)
            keep = np.zeros(arr.shape[:2], bool)
            for c in bow:
                keep |= (arr[..., :3] == c).all(-1)
            arr = G.drop_lonely(G.outline(arr, keep=keep))
            if CHAR[tag].get("specks"):
                arr = drop_specks(arr, CHAR[tag]["specks"])
            frames.append((G.centre_frame(arr, u0, r0), ms))
        assert len(frames) == len(st["frames"]), tag
        out[tag] = frames
    return out


# ----------------------------------------------------------------------------- effects
def biggest_blob_box(fr, thresh=0.3):
    lab, n = G.label(fr.a[..., 3] > thresh)
    sizes = np.bincount(lab.ravel())[1:]
    ys, xs = np.nonzero(lab == int(sizes.argmax()) + 1)
    return xs.min() + fr.ox, ys.min() + fr.oy, xs.max() + 1 + fr.ox, ys.max() + 1 + fr.oy


def bbox_centre(fr, thresh=0.15):
    x0, y0, x1, y1 = fr.bbox(thresh)
    return (x0 + x1) / 2.0, (y0 + y1) / 2.0


def anchors_arrow(frames):
    """A point on the shaft a third of the way back from the tip (the arrow leads, the trail
    follows), at the height of the arrow body."""
    out = []
    for f in frames:
        x0, y0, x1, y1 = biggest_blob_box(f)
        out.append((x1 - 0.33 * (x1 - x0), (y0 + y1) / 2.0))
    return out


def anchors_centre(frames):
    return [bbox_centre(f) for f in frames]


def anchors_ring(frames):
    """The ground ring is the biggest connected blob; the rising motes are separate (by row
    extent the motes at both sides made the rows above the ring look 'wide')."""
    out = []
    for f in frames:
        x0, y0, x1, y1 = biggest_blob_box(f)
        out.append(((x0 + x1) / 2.0, (y0 + y1) / 2.0))
    return out


def anchors_r_hit(frames):
    """Ice on the enemy's feet: the ground line the strip was drawn on (source px), each frame's
    own centre across."""
    return [(bbox_centre(f)[0], 512.0) for f in frames]


# W Volley as League draws it: 9 frost arrows fanning out in a cone. The kit casts it as a
# LineRangeProjectile, whose sprite the game centres on the rectangle and turns to the cast
# direction (oppi's Swain Q fan and Lux beam are laid out that way), so the fan's apex - Ashe -
# sits half the rectangle's length behind the pivot.
VOLLEY_ANGLES = [-28, -21, -14, -7, 0, 7, 14, 21, 28]   # degrees
VOLLEY_RADII = [16, 26, 36, 46, 56, 66, 75]              # px from the apex to the arrow tips, per frame
                                                         # (the arrows are ~15 px: frame 0 leaves the bow)
VOLLEY_LENGTH = 80                                       # px, = the LineRangeProjectile's length


def fan_frames(strip, s, cut):
    """The frost arrow of `strip` rotated at source resolution (so the pixels come out clean) and
    fanned out from the apex, one frame per radius."""
    f = G.split_strip(G.load_rgba(src(strip)), 4, blob_thresh=0.05)[0]
    x0, y0, x1, y1 = biggest_blob_box(f)
    tipx, tipy = x1 - f.ox, (y0 + y1) / 2.0 - f.oy
    a8 = (np.clip(f.a, 0, 1) * 255).astype(np.uint8)
    R = int(max(a8.shape[:2]) + 4)
    canvas = np.zeros((2 * R, 2 * R, 4), np.uint8)          # the tip at the centre
    oy, ox = int(round(R - tipy)), int(round(R - tipx))
    canvas[oy:oy + a8.shape[0], ox:ox + a8.shape[1]] = a8
    base = Image.fromarray(canvas, "RGBA")
    rots = {a: G.Frame(np.asarray(base.rotate(-a, resample=Image.BICUBIC)).astype(np.float32) / 255.0, 0, 0, 0)
            for a in VOLLEY_ANGLES}                          # PIL turns counter-clockwise; +y is down
    apex = -VOLLEY_LENGTH / 2.0
    out = []
    for r in VOLLEY_RADII:
        layers = [G.render(rots[a], s, s, R, R, apex + r * np.cos(np.radians(a)), r * np.sin(np.radians(a)),
                           cut=cut, keep=0.9) for a in VOLLEY_ANGLES]
        u0, r0 = min(l[1] for l in layers), min(l[2] for l in layers)
        u1 = max(l[1] + l[0].shape[1] for l in layers)
        r1 = max(l[2] + l[0].shape[0] for l in layers)
        acc = np.zeros((r1 - r0, u1 - u0, 4), np.uint8)
        for arr, lu, lr in layers:
            sub = acc[lr - r0:lr - r0 + arr.shape[0], lu - u0:lu - u0 + arr.shape[1]]
            sub[arr[..., 3] > 0] = arr[arr[..., 3] > 0]
        out.append((acc, u0, r0))
    return out


# sprite: {tag: (source strip, frames, scale x/y, anchor rule, pivot-relative spot, ms, cut[, mode])}
# "vote": strips.render_vote with the arrows' saturated blue weighted up - averaged, the five
# arrows of the flurry and their white streaks melted into one pale blob
# "fan": fan_frames() - the W volley, until GPT draws its own
FX = {
    "league_ashe_fx": {
        "arrow": ("fx_arrow", 4, (0.05, 0.05), anchors_arrow, (0, 0), [70] * 4, 0.4),
        "volley": ("fx_arrow", 4, (0.04, 0.04), None, (0, 0), [40] * 7, 0.4, "fan"),
        "flurry": ("fx_flurry", 4, (0.06, 0.06), anchors_arrow, (0, 0), [70] * 4, 0.4, "vote"),
        "hit": ("fx_hit", 5, (0.05, 0.05), anchors_centre, (0, -6), [60] * 5, 0.4),
        "focus": ("fx_focus", 6, (0.094, 0.094), anchors_ring, (0, 11), [83] * 6, 0.4),
    },
    "league_ashe_r": {
        "arrow": ("fx_crystal", 4, (0.09, 0.09), anchors_arrow, (0, 0), [70] * 4, 0.4),
        "hit": ("fx_r_hit", 9, (0.12, 0.12), anchors_r_hit, (0, 11), [80, 80, 100, 250, 250, 250, 250, 250, 250], 0.4),
    },
}
FX_COLORS = 32


def build_fx():
    sprites = {}
    for sprite, tags in FX.items():
        raw = {}
        for tag, (strip, n, (sx, sy), rule, (X0, Y0), ms, cut, *mode) in tags.items():
            if mode == ["fan"]:
                raw[tag] = list(zip(fan_frames(strip, sx, cut), ms))
                continue
            frames = G.split_strip(G.load_rgba(src(strip)), n, blob_thresh=0.05)
            if mode == ["vote"]:
                pix = np.concatenate([(f.a[..., :3][f.a[..., 3] > 0.5] * 255).astype(np.uint8) for f in frames])
                vpal = G.median_cut(pix, 24)
                sat = (vpal.max(1) - vpal.min(1)) / np.maximum(vpal.max(1), 1)
                vw = np.where((sat > 0.55) & (G.lum(vpal) < 170), 2.0, 1.0).astype(np.float32)
                raw[tag] = [(G.render_vote(f, sx, sy, ax, ay, X0, Y0, vpal, vw, cut=cut, thin=0.25), m)
                            for f, (ax, ay), m in zip(frames, rule(frames), ms)]
            else:
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
    ap.add_argument("--body", action="store_true", help="also write the round-1 body sheet "
                    "(replaced by tools/art/import_native.py)")
    ap.add_argument("--review", help="write alignment review sheets of the round-1 body to this folder")
    args = ap.parse_args()
    if args.body or args.review:
        body(args)
    for sprite, tags in build_fx().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " +
              ", ".join(f"{t} {len(v)}f" for t, v in tags.items()))


def body(args):
    strips, shift = load_char()
    print(f"idle head vs League: {shift:+.2f} px (added to every head track)")
    for tag, st in strips.items():
        print(f"{tag:9s} scale {st['s']:.4f}  {len(st['frames'])} frames")
    char = build_char(strips)
    if args.body:
        w, h = G.write_sheet(os.path.join(MOD, "champions", "league_ashe"), char)
        print(f"league/champions/league_ashe#sheet.png {w}x{h}, {sum(len(v) for v in char.values())} frames")
    if args.review:
        review(char, args.review)


if __name__ == "__main__":
    main()
