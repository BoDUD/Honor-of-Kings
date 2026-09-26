#!/usr/bin/env python3
"""Import Lux's generated source art (assets/source/lux, prompts in PROMPTS.md) into game sprites.

    python tools/art/import_lux.py [--body] [--review DIR]

Writes (exported sheet format: name#sheet.png + name#anim.fanim, frames centred on the unit)
  league/champions/league_lux     idle run attack skill skill2 ult hit dead   (only with --body)
  league/effects/league_lux_fx    bolt hit q_orb q_bind shield e_orb e_zone mark ignite
  league/effects/league_lux_r     beam

The body sheet now comes from the native-size redraw (tools/art/import_native.py, drawn over
this round's frames); --body writes this round-1 body again.
Body: every strip was drawn from one design sheet (lux_ref.png) and a front-view render of League's
own clip at fixed times, head enlarged to TFM2 proportions (pose_ref.py --head 2.0 --legs 0.8
--mirror). GPT drew each strip at its own size, so each gets its own scale: `tall` is her standing
height at that strip's size (hair top to soles, 34 px in game), set so her HEAD is as big as in
idle - idle f0's head correlated over every frame at a range of scales (normalized
cross-correlation; within a strip the sure matches agreed to 0.03). The feet sit 11.5 px below
the frame centre (base-game convention). Idle and hit stand on the middle of their stance / line
their legs up with idle; every other strip puts each frame's head where League's skeleton has it
at that frame's time and camera (pose_ref.py --track 34), shifted once so idle's own head lands
where League puts it. The attack, Q and E lunges keep 70% of League's travel around idle's head
(a sprite snaps back to idle where League blends), the death's knock-back 65%.
Final Spark's wand floats off her hands, past the equal-width cells, so that strip is split by
blobs: each blob holding navy bodysuit is a body, every other blob joins the nearest body on its
left. The floating wand sits ~14 px above the ground, inside the 16 px beam drawn at the pivot.
Pixels: one shared palette; every game pixel takes the colour covering most of it (strips.render_vote)
with her blue eyes, gold, skin and whites weighted up so the face and the wand's trim survive,
then a 1 px dark outline.
Effects: own palette per sheet, no outline; projectiles anchored on the orb, bursts and marks on
their centre, the E field on its ring (drawn on the ground, 60 px = its 30000 radius), the Final
Spark beam from 6 px past the caster to the end of its 240 px rectangle (the view is centred on the
LineRangeProjectile and turned to the cast direction).
--review DIR writes one alignment sheet per strip (pivot + feet lines, idle silhouette in red).
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from import_ashe import bbox_centre, biggest_blob_box, drop_specks, review  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lux")
MOD = os.path.join(ROOT, "league")

HEIGHT = 34.0   # px from hair top to soles, standing
FEET = 11.5     # feet (bottom edge) below the pivot
SUP = 4         # alignment works at 4x game resolution
BAND = 12       # px of legs used to line frames up
LEAGUE_IDLE_HEAD = -0.9   # League idle1@0: head joint x, px from the unit (mirrored camera)


def kept(track, keep):
    """League head track with only `keep` of its travel around idle's head."""
    return [round(LEAGUE_IDLE_HEAD + keep * (h - LEAGUE_IDLE_HEAD), 2) for h in track]


# tall: source px of her standing height at that strip's drawing size (see the docstring)
# anchor: feet = line the legs up with idle f0 (idle f0 itself: middle of its stance)
#         head = put each frame's head `head[i]` px from the pivot (pose_ref.py --track 34, same
#                camera as the references: --mirror --head 2.0 --legs 0.8 --yaw 55, pitch 25/12)
# ground: per-frame lowest pixel, or "strip" = median of the grounded frames
# air: frames in the air; they keep their drawn height above the ground of the others
# split: "bodies" = split_bodies() (props floating off the body)
CHAR = {
    # idle1 0-889 ms: League's 1.07 s idle loop
    "idle":   dict(n=6, tall=409, ms=[178] * 6, anchor="feet"),
    # run 0-700 ms: one 0.8 s cycle; both feet off the ground at 0, 300, 400 and 700 ms
    "run":    dict(n=8, tall=336, ms=[100] * 8, anchor="head", ground="strip", air=[0, 3, 4, 7],
                   head=[3.1, 3.1, 3.3, 3.7, 3.7, 3.5, 3.3, 3.3]),
    # idle>attack1 blend, attack1 133/200/233/300, attack1>idle blend; the bolt leaves in frame 4 (tick 13)
    "attack": dict(n=6, tall=361, ms=[70, 80, 60, 100, 100, 90], anchor="head", ground="strip",
                   head=kept([-3.5, -6.0, 1.1, 4.5, 8.0, 1.0], 0.7)),
    # Q: idle>spell1 blend, spell1 100/167/233/267/433, blend back; the orb leaves in frame 4 (tick 13)
    "skill":  dict(n=7, tall=273, ms=[60, 70, 90, 90, 80, 100, 90], anchor="head", ground="strip",
                   head=kept([-3.5, -9.3, -6.0, 3.8, 4.8, 7.6, 1.4], 0.7)),
    # E: idle>spell3 blend, spell3 100/167/233/267/433, blend back; the orb leaves in frame 5 (tick 16)
    "skill2": dict(n=7, tall=218, ms=[60, 70, 70, 60, 100, 120, 90], anchor="head", ground="strip",
                   head=kept([-3.6, -6.5, -6.1, -0.3, 3.8, 4.2, 1.2], 0.7)),
    # R: idle>spell4 blend, spell4 200/400/600/800/933/1200/1800: leap, float with the wand
    # hovering, the beam at frame 5 (tick 30), recoil, tuck, land
    "ult":    dict(n=8, tall=281, ms=[100, 80, 120, 200, 180, 120, 150, 150], anchor="head", ground="strip",
                   air=[1, 2, 3, 4, 5, 6], head=[1.1, 0.8, -3.5, -4.4, -4.9, -4.9, 1.7, -4.7], split="bodies"),
    "hit":    dict(n=2, tall=772, ms=[120, 120], anchor="feet", ground="strip"),
    # death 0/133/267/400/533/800/1400 ms: struck, thrown back 41 px, lands and lies
    "dead":   dict(n=7, tall=281, ms=[100, 100, 120, 120, 150, 200, 400], anchor="head", air=[2, 3],
                   head=kept([2.4, -9.7, -24.7, -31.2, -36.3, -38.9, -41.4], 0.65)),
}
CHAR_COLORS = 60
# palette entries per colour class (the rest come from the other pixels) and each class's vote weight
SHARE = {"gold": 10, "skin": 5, "light": 5, "eye": 3, "red": 2}
WEIGHT = {"eye": 3.0, "gold": 1.3, "skin": 1.3, "light": 1.3, "red": 1.2, "other": 1.0}


def src(name):
    return os.path.join(SRC, f"lux_{name}.png")


def hsv(rgb):
    """float RGB (0-1) -> hue (0-1), saturation, value."""
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = np.maximum(mx - mn, 1e-4)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    return h, (mx - mn) / np.maximum(mx, 1e-4), mx


# ----------------------------------------------------------------------------- splitting, measuring
def navy_mask(a):
    """Her royal-blue bodysuit: dark saturated blue."""
    h, s, v = hsv(a[..., :3])
    return (a[..., 3] > 0.5) & (h >= 0.58) & (h <= 0.70) & (s > 0.45) & (v > 0.12) & (v < 0.6)


def split_bodies(img, n, blob_thresh=0.12, margin=6):
    """Float RGBA strip -> n Frames, for strips whose prop floats away from the body (the Final
    Spark wand crosses into the next equal-width cell): each blob holding bodysuit is a body, every
    other blob (wand, glow, sparks) joins the nearest body to its left."""
    alpha = img[..., 3]
    lab, count = G.label(alpha > blob_thresh)
    ys, xs = np.nonzero(lab)
    ids = lab[ys, xs]
    size = np.bincount(ids, minlength=count + 1).astype(np.float64)
    cx = np.bincount(ids, xs, minlength=count + 1) / np.maximum(size, 1)
    navy = np.bincount(ids, navy_mask(img)[ys, xs], minlength=count + 1)
    bodies = sorted((k for k in range(1, count + 1) if navy[k] > 200), key=lambda k: cx[k])
    if len(bodies) != n:
        raise SystemExit(f"split_bodies: {len(bodies)} bodies, expected {n}")
    owner = np.zeros(count + 1, np.int32)
    bx = np.array([cx[k] for k in bodies])
    for k in range(1, count + 1):
        left = np.nonzero(bx <= cx[k])[0]
        owner[k] = left[-1] if len(left) else 0
    keep = np.full(alpha.shape, -1, np.int32)
    keep[ys, xs] = owner[ids]
    out = []
    H, W = alpha.shape
    for i in range(n):
        m = keep == i
        fy, fx = np.nonzero(m)
        x0, x1 = max(0, fx.min() - margin), min(W, fx.max() + 1 + margin)
        y0, y1 = max(0, fy.min() - margin), min(H, fy.max() + 1 + margin)
        a = img[y0:y1, x0:x1].copy()
        a[..., 3] = np.where(m[y0:y1, x0:x1], a[..., 3], 0.0)
        out.append(G.Frame(a, x0, y0, i))
    return out


def hair_mask(a):
    """Her honey-blonde hair: bright, moderately saturated yellow (the wand's gold is darker and
    more saturated, its glow near white)."""
    h, s, v = hsv(a[..., :3])
    return (a[..., 3] > 0.5) & (h >= 0.085) & (h <= 0.145) & (s >= 0.40) & (s <= 0.80) & (v >= 0.84)


def head_x(fr, min_px=200):
    """x (strip coordinates) of the head: median of the biggest hair blob."""
    lab, n = G.label(hair_mask(fr.a))
    if not n:
        return None
    sizes = np.bincount(lab.ravel())[1:]
    k = int(sizes.argmax()) + 1
    if sizes[k - 1] < min_px:
        return None
    ys, xs = np.nonzero(lab == k)
    return float(np.median(xs)) + fr.ox


# ----------------------------------------------------------------------------- characters
def load_char():
    """-> {tag: dict(frames, s, gy, ax)}: per frame the ground edge gy and the strip x that
    becomes the pivot column."""
    strips = {}
    for tag, c in CHAR.items():
        img = G.load_rgba(src(tag))
        frames = split_bodies(img, c["n"]) if c.get("split") == "bodies" else G.split_strip(img, c["n"])
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
            hx = [head_x(f) for f in st["frames"]]
            if None in hx:
                raise SystemExit(f"{tag}: no hair found in frame {hx.index(None) + 1}")
            st["ax"] = [h - (c["head"][i] + shift) / s for i, h in enumerate(hx)]
    return strips, shift


def colour_classes(rgb):
    """(N, 3) uint8 -> class per pixel: gold (hair, trim, wand), skin, light (white cloth, gloves,
    highlights), eye (her bright blue eyes; the bodysuit is darker), red (collar gems), other."""
    h, s, v = hsv(rgb.astype(np.float32) / 255.0)
    out = np.full(len(rgb), "other", object)
    out[(h >= 0.08) & (h <= 0.16) & (s > 0.40) & (v > 0.45)] = "gold"
    out[(h >= 0.02) & (h < 0.08) & (s > 0.15) & (s < 0.55) & (v > 0.60)] = "skin"
    out[(v > 0.75) & (s < 0.20)] = "light"
    out[(h >= 0.55) & (h <= 0.70) & (s > 0.50) & (v > 0.55)] = "eye"
    out[((h < 0.02) | (h > 0.95)) & (s > 0.55) & (v > 0.50)] = "red"
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
    out = {}
    for tag, st in strips.items():
        frames = []
        for i, (fr, ms) in enumerate(zip(st["frames"], CHAR[tag]["ms"])):
            arr, u0, r0 = G.render_vote(fr, st["s"], st["s"], st["ax"][i], st["gy"][i], 0.0, FEET, pal, weights)
            arr = drop_specks(G.drop_lonely(G.outline(arr)), 3)
            frames.append((G.centre_frame(arr, u0, r0), ms))
        assert len(frames) == len(st["frames"]), tag
        out[tag] = frames
    return out


# ----------------------------------------------------------------------------- effects
def anchors_orb(frames, width):
    """The glowing ball at the front of a projectile (its tail trails to the left): the right end of
    the biggest blob, one ball radius back."""
    out = []
    for f in frames:
        x0, y0, x1, y1 = biggest_blob_box(f)
        out.append((x1 - 0.5 * (y1 - y0), (y0 + y1) / 2.0))
    return out


def in_cells(frames, width, y):
    """Effects drawn in place: GPT centres each frame in its equal-width cell (within ~8 px; a
    frame's own box drifts with its loose sparks), so each frame takes its cell's centre plus the
    strip's median offset, and all frames one height."""
    cw = width / len(frames)
    off = float(np.median([bbox_centre(f)[0] - (i + 0.5) * cw for i, f in enumerate(frames)]))
    return [((i + 0.5) * cw + off, y) for i in range(len(frames))]


def anchors_centre(frames, width):
    return in_cells(frames, width, float(np.median([bbox_centre(f)[1] for f in frames])))


def anchors_rings(frames, width):
    """Light Binding: the lower of its two rings (around the knees) - the widest rows of the frames
    that show both rings."""
    ys = []
    for f in frames[1:6]:
        op = f.a[..., 3] > 0.5
        w = op.sum(1)
        rows = np.nonzero(w > 0.7 * w.max())[0]
        groups = np.split(rows, np.nonzero(np.diff(rows) > 5)[0] + 1)
        ys.append(float(np.mean(groups[-1])) + f.oy)
    return in_cells(frames, width, float(np.median(ys)))


def anchors_oval(frames, width):
    """Prismatic Barrier: the centre of the bubble (the biggest blob while it stands, frames 2-6)."""
    boxes = [biggest_blob_box(f) for f in frames[1:6]]
    return in_cells(frames, width, float(np.median([(b[1] + b[3]) / 2.0 for b in boxes])))


def anchors_field(frames, width):
    """Lucent Singularity: the centre of the ring on the ground (the biggest blob of the first four
    frames; the orb floats above it), so the blast goes off where the field was drawn."""
    boxes = [biggest_blob_box(f) for f in frames[:4]]
    return in_cells(frames, width, float(np.median([(b[1] + b[3]) / 2.0 for b in boxes])))


def loop(frames_ms, first, last, times, ms):
    """Repeat frames[first:last] `times` times at `ms` each, between the frames before and after."""
    return frames_ms[:first] + [(f, ms) for _ in range(times) for f, _ in frames_ms[first:last]] + frames_ms[last:]


# Final Spark: the LineRangeProjectile is 240 px long; its view is centred on the rectangle, so the
# caster stands at -120. The beam's drawn left end goes 6 px past her (her wand, whose flash sits a
# further ~7 px out), the right end at +120.
BEAM_LENGTH = 240
BEAM_START = 6


def beam_frames(cut):
    """The six rows of lux_fx_r_beam.png (one column), each scaled so the beam spans its rectangle."""
    img = G.load_rgba(src("fx_r_beam"))
    rows = G.split_strip(np.ascontiguousarray(img.transpose(1, 0, 2)), 6, blob_thresh=0.05)
    rows = [G.Frame(np.ascontiguousarray(r.a.transpose(1, 0, 2)), r.oy, r.ox, r.cell) for r in rows]
    left = min(r.bbox(0.3)[0] for r in rows)
    right = max(r.bbox(0.3)[2] for r in rows)
    s = (BEAM_LENGTH - BEAM_START) / float(right - left)
    out = []
    for r in rows:
        op = r.a[..., 3] > 0.5
        core = int(np.argmax(op.sum(1))) + r.oy          # the row the beam line runs along
        out.append(G.render(r, s, s, left, core, -BEAM_LENGTH / 2.0 + BEAM_START, 0.0, cut=cut, keep=0.9))
    return out, s


# sprite: {tag: (source strip, frames, scale, anchor rule, pivot-relative spot, ms, cut)}
FX = {
    "league_lux_fx": {
        "bolt": ("fx_bolt", 4, 0.05, anchors_orb, (0, 0), [60] * 4, 0.4),
        "hit": ("fx_hit", 5, 0.05, anchors_centre, (0, -6), [60] * 5, 0.4),
        "q_orb": ("fx_q_orb", 4, 0.055, anchors_orb, (0, 0), [70] * 4, 0.4),
        # rings at the knees and the chest of a 34 px unit; binds 1.5 s: frames 3-6 loop twice
        "q_bind": ("fx_q_bind", 8, 0.083, anchors_rings, (0, 5), [80, 80, 130, 130, 130, 130, 90, 90], 0.4),
        # a bubble around the whole unit, centred on its body
        "shield": ("fx_shield", 8, 0.115, anchors_oval, (0, -5), [80, 80, 110, 110, 110, 110, 90, 90], 0.4),
        "e_orb": ("fx_e_orb", 4, 0.03, anchors_centre, (0, 0), [80] * 4, 0.4),
        # the field ring = 60 px (its 30000 radius) on the ground; 1-4 twice (1 s), then the blast
        "e_zone": ("fx_e_zone", 8, 0.29, anchors_field, (0, 11), [125] * 4 + [100] * 4, 0.4),
        "mark": ("fx_mark", 6, 0.05, anchors_centre, (0, -8), [80, 110, 110, 110, 110, 100], 0.4),
        "ignite": ("fx_ignite", 6, 0.06, anchors_centre, (0, -6), [60] * 6, 0.4),
    },
    "league_lux_r": {
        # telegraph 467 ms (the beam fires 28 ticks after the view appears), then 467 ms of beam
        "beam": ("fx_r_beam", 6, None, None, None, [230, 237, 60, 135, 135, 137], 0.4),
    },
}
LOOPS = {"q_bind": (2, 6, 2, 130), "shield": (2, 6, 2, 110), "e_zone": (0, 4, 2, 125), "mark": (1, 5, 2, 110)}
FX_COLORS = {"league_lux_fx": 48, "league_lux_r": 32}


def build_fx():
    sprites = {}
    for sprite, tags in FX.items():
        raw = {}
        for tag, (strip, n, s, rule, spot, ms, cut) in tags.items():
            if tag == "beam":
                frames, s = beam_frames(cut)
                print(f"  beam scale {s:.4f}")
                raw[tag] = list(zip(frames, ms))
                continue
            img = G.load_rgba(src(strip))
            frames = G.split_strip(img, n, blob_thresh=0.05)
            X0, Y0 = spot
            raw[tag] = [(G.render(f, s, s, ax, ay, X0, Y0, cut=cut, keep=0.9), m)
                        for f, (ax, ay), m in zip(frames, rule(frames, img.shape[1]), ms)]
        pal = G.Palette([r[0][0] for rs in raw.values() for r in rs], colors=FX_COLORS[sprite], extra=())
        out = {}
        for tag, rs in raw.items():
            fr = [(G.centre_frame(pal.apply(arr), u0, r0), m) for (arr, u0, r0), m in rs]
            if tag in LOOPS:
                first, last, times, ms = LOOPS[tag]
                fr = loop(fr, first, last, times, ms)
            out[tag] = fr
        sprites[sprite] = out
    return sprites


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
        print(f"{tag:7s} scale {st['s']:.4f}  {len(st['frames'])} frames")
    char = build_char(strips)
    if args.body:
        w, h = G.write_sheet(os.path.join(MOD, "champions", "league_lux"), char)
        print(f"league/champions/league_lux#sheet.png {w}x{h}, {sum(len(v) for v in char.values())} frames")
    if args.review:
        review(char, args.review)


if __name__ == "__main__":
    main()
