#!/usr/bin/env python3
"""Fit a native-size delivery to its references: one head size for every strip, heads where League has them.

    python tools/art/fit_native.py --hero leesin --src DELIVERY_DIR --refs REFS_DIR --scale TAG=S ... [--review DIR]

Lee Sin's strips (straight from League, tools/lol/native_pose.py) came back clean - exact 8x8
blocks, the approved 16 colours - but GPT drew most actions about 1.4x the approved design (the
head even more than the body): in game he would grow whenever he moved. This puts the delivery
back on the references:
  1. --scale says how much bigger than the design each strip (or each frame) was drawn, judged by
     the head against idle (Lee Sin: run/attack/skill 1.4, skill2/ult/hit 1.38, dead 1.35, q2 1.0
     in the air and 1.18 landing); each frame shrinks by it about its ground point under the pivot,
     every game pixel taking the palette colour (or transparency) covering most of its footprint -
     weighted so outlines, the blindfold and gold survive - so it stays flat 16-colour pixel art;
  2. placement: the blindfold's centre goes where League's head joint is in the reference frame
     (the "head" of <hero>_cells.json, plus the offset measured on idle frame 1); frames whose
     reference stands on the feet line get their soles back on it; frames with no blindfold in
     view are placed by their overlap with the reference silhouette (REFS_DIR, native_pose.py);
  3. loops (run) keep one blindfold column relative to the pivot.
Idle is kept as delivered (the approved design, re-layered by Codex). Writes
assets/source/native/<hero>_<tag>.png (8x blocks, the delivery's layout) and <hero>_fit.json.
--review DIR writes <hero>_fit_<tag>.png: reference silhouette | delivery | fitted, 4x, with the
feet line, the pivot column and the blindfold target.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from native_refs import Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
LOOPS = ("run",)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def load_cells(path, n, cell):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    cols, _ = layout(n)
    cw, ch = cell
    return [a[k // cols * ch:(k // cols + 1) * ch, k % cols * cw:(k % cols + 1) * cw].copy() for k in range(n)]


def save_cells(frames, cell, path):
    cols, rows = layout(len(frames))
    cw, ch = cell
    sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, f in enumerate(frames):
        sheet[k // cols * ch:(k // cols + 1) * ch, k % cols * cw:(k % cols + 1) * cw] = f
    Image.fromarray(sheet, "RGBA").resize((cols * cw * Z, rows * ch * Z), Image.NEAREST).save(lp(path))


def classes(rgb):
    """Colour class per pixel: 0 outline/dark, 1 skin, 2 red, 3 gold, 4 other."""
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    cls = np.full(rgb.shape[:2], 4, np.int8)
    cls[(r < 70) & (g < 70) & (b < 80)] = 0
    cls[(r > 150) & (g > 90) & (b > 60) & (r > b + 40) & (g > b)] = 1
    cls[(r > 100) & (g < 60) & (b < 70)] = 2
    cls[(r > 130) & (g > 90) & (b < 90) & (r - b > 90) & ~((r > 150) & (b > 60))] = 3
    return cls


def shrink(f, s, cx, cy, weight, sub=8):
    """Scale by 1/s about (cx, cy): each target pixel takes the colour covering most of its
    footprint (transparency included), weighted per colour."""
    H, W = f.shape[:2]
    cols = sorted({tuple(int(v) for v in c) for c in f[f[..., 3] > 0][:, :3]})
    idx = np.zeros((H + 1, W + 1), np.int16)                   # 0 = transparent (also off the cell)
    for i, c in enumerate(cols, 1):
        idx[:H, :W][(f[..., :3] == c).all(-1) & (f[..., 3] > 0)] = i
    offs = (np.arange(sub) + 0.5) / sub
    sy = np.floor(cy + (np.arange(H)[:, None] + offs[None] - cy) * s).astype(int)
    sx = np.floor(cx + (np.arange(W)[:, None] + offs[None] - cx) * s).astype(int)
    sy[(sy < 0) | (sy >= H)] = H
    sx[(sx < 0) | (sx >= W)] = W
    g = idx[sy[:, None, :, None], sx[None, :, None, :]]         # (H, W, sub, sub)
    wts = np.array([1.0] + [weight.get(c, 1.0) for c in cols])
    votes = np.stack([(g == i).sum((2, 3)) * wts[i] for i in range(len(cols) + 1)], -1)
    win = votes.argmax(-1)
    out = np.zeros_like(f)
    for i, c in enumerate(cols, 1):
        out[win == i, :3] = c
        out[win == i, 3] = 255
    return out


def shift(f, dx, dy):
    out = np.zeros_like(f)
    H, W = f.shape[:2]
    ys, xs = slice(max(0, dy), min(H, H + dy)), slice(max(0, dx), min(W, W + dx))
    yd, xd = slice(max(0, -dy), min(H, H - dy)), slice(max(0, -dx), min(W, W - dx))
    out[ys, xs] = f[yd, xd]
    return out


def lowest(m):
    ys = np.nonzero(m.any(1))[0]
    return int(ys.max()) if len(ys) else None


def overlap_shift(f, ref_mask, span=12):
    m = f[..., 3] > 0
    best = (-1.0, 0, 0)
    for dy in range(-span, span + 1):
        for dx in range(-span, span + 1):
            sh = np.roll(np.roll(m, dy, 0), dx, 1)
            iou = (sh & ref_mask).sum() / max(1, (sh | ref_mask).sum())
            if iou > best[0]:
                best = (float(iou), dx, dy)
    return best


def band_centre(f):
    """Centre (x, y) of the blindfold: the longest run of bright blindfold red at least 3 px long
    with skin right above it; None when the head is turned away or tucked."""
    op = f[..., 3] > 0
    c = classes(f[..., :3])
    red = op & (c == 2) & (f[..., 0].astype(int) > 140)
    skin = op & (c == 1)
    best = None
    for y in range(1, f.shape[0]):
        xs = np.nonzero(red[y])[0]
        if len(xs) < 3:
            continue
        runs, a = [], xs[0]
        for p, q in zip(xs, xs[1:]):
            if q != p + 1:
                runs.append((a, p))
                a = q
        runs.append((a, xs[-1]))
        for r0, r1 in runs:
            if r1 - r0 + 1 >= 3 and skin[max(0, y - 2):y, r0:r1 + 1].sum() >= 2:
                if best is None or r1 - r0 > best[2] - best[1]:
                    best = (y, r0, r1)
    if best is None:
        return None
    y, r0, r1 = best
    y1 = y
    while y1 + 1 < f.shape[0] and red[y1 + 1, r0:r1 + 1].sum() >= 3:
        y1 += 1
    return ((r0 + r1 + 1) / 2.0, (y + y1 + 1) / 2.0)


def parse_scales(items, tags):
    """TAG=S or TAG=S1,S2,... (one per frame) -> {tag: [scale per frame]}."""
    out = {}
    for item in items:
        tag, v = item.split("=")
        vals = [float(x) for x in v.split(",")]
        n = len(tags[tag])
        out[tag] = vals * n if len(vals) == 1 else vals
        if len(out[tag]) != n:
            sys.exit(f"--scale {tag}: {len(vals)} values for {n} frames")
    return out


def review_sheet(path, cell, feet, rows, ref, src, out, off):
    n = len(rows)
    img = Image.new("RGBA", (n * (cell[0] + 2) * 4, 3 * (cell[1] + 2) * 4), (60, 64, 70, 255))
    d = ImageDraw.Draw(img)
    for k in range(n):
        for j, a in enumerate([None, src[k], out[k]]):
            tile = Image.new("RGBA", cell, (92, 98, 86, 255))
            if a is None:
                rr = np.zeros(cell[::-1] + (4,), np.uint8)
                rr[ref[k]] = (200, 200, 200, 255)
                tile.alpha_composite(Image.fromarray(rr, "RGBA"))
            else:
                tile.alpha_composite(Image.fromarray(a, "RGBA"))
            x0, y0 = k * (cell[0] + 2) * 4, j * (cell[1] + 2) * 4
            img.alpha_composite(tile.resize((cell[0] * 4, cell[1] * 4), Image.NEAREST), (x0, y0))
            d.line((x0, y0 + feet * 4, x0 + cell[0] * 4, y0 + feet * 4), fill=(120, 200, 120, 255))
            px = rows[k]["pivot"][0]
            d.line((x0 + px * 4 + 2, y0, x0 + px * 4 + 2, y0 + cell[1] * 4), fill=(200, 120, 120, 255))
            bx, by = rows[k]["head"][0] + off[0], rows[k]["head"][1] + off[1]
            d.rectangle((x0 + bx * 4 - 3, y0 + by * 4 - 3, x0 + bx * 4 + 3, y0 + by * 4 + 3), outline=(80, 160, 255, 255))
    img.save(lp(path))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--src", required=True, help="the delivery folder with <hero>_<tag>.png")
    ap.add_argument("--refs", required=True, help="native_pose.py's output folder (<hero>_native_<tag>.png)")
    ap.add_argument("--scale", action="append", default=[],
                    help="TAG=S or TAG=S1,...,Sn: how much bigger than the design the delivery drew this strip "
                         "(or each frame); strips not named are kept at 1")
    ap.add_argument("--review", help="write reference | delivery | fitted sheets here")
    args = ap.parse_args()
    hero = args.hero
    with open(lp(os.path.join(SRC, f"{hero}_cells.json")), encoding="utf-8") as fh:
        table = json.load(fh)
    cell, tags = tuple(table["cell"]), table["tags"]
    feet = cell[1] - 10                                  # the row under the soles
    scales = parse_scales(args.scale, tags)

    idle = load_cells(os.path.join(args.src, f"{hero}_idle.png"), len(tags["idle"]), cell)
    b0 = band_centre(idle[0])
    joint0 = tags["idle"][0]["head"]
    off = (b0[0] - joint0[0], b0[1] - joint0[1])          # blindfold centre from League's head joint
    print(f"idle frame 1: blindfold centre {b0}, League's head joint {joint0} -> offset {off[0]:+.1f}, {off[1]:+.1f}")
    palette = sorted({tuple(int(v) for v in c) for f in idle for c in f[f[..., 3] > 0][:, :3]})
    cls = {c: int(classes(np.array([[c]], np.uint8))[0, 0]) for c in palette}
    weight = {c: {0: 1.6, 2: 1.3, 3: 1.25}.get(k, 1.0) for c, k in cls.items()}

    report = {"blindfold_offset_from_head_joint": [round(off[0], 2), round(off[1], 2)], "tags": {}}
    if args.review:
        os.makedirs(lp(args.review), exist_ok=True)
    for tag, rows in tags.items():
        n = len(rows)
        src = load_cells(os.path.join(args.src, f"{hero}_{tag}.png"), n, cell)
        r = np.asarray(Image.open(lp(os.path.join(args.refs, f"{hero}_native_{tag}.png"))).convert("RGB"))[::Z, ::Z]
        cols, _ = layout(n)
        ref = [(np.abs(r[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]]
                       .astype(int) - 225).sum(-1) > 0) for k in range(n)]
        if tag == "idle":
            out, info = src, [{"kept": True} for _ in src]
        else:
            ss = scales.get(tag, [1.0] * n)
            out, info = [], []
            for k, f in enumerate(src):
                g = shrink(f, ss[k], rows[k]["pivot"][0] + 0.5, float(feet), weight) if ss[k] > 1.001 else f.copy()
                bc = band_centre(g)
                jx, jy = rows[k]["head"]
                if bc is not None:
                    dx, dy = int(round(jx + off[0] - bc[0])), int(round(jy + off[1] - bc[1]))
                    how = "blindfold"
                else:
                    iou, dx, dy = overlap_shift(g, ref[k])
                    how = f"silhouette {iou:.2f}"
                if lowest(ref[k]) is not None and lowest(ref[k]) >= feet - 2:
                    dy = (feet - 1) - lowest(g[..., 3] > 0)          # soles on the feet line, as in the reference
                    how += ", soles on the line"
                out.append(shift(g, dx, dy))
                info.append({"scale": ss[k], "placed_by": how, "move": [dx, dy]})
            if tag in LOOPS:   # one blindfold column relative to the pivot
                rel = []
                for k, g in enumerate(out):
                    c = band_centre(g)
                    rel.append(None if c is None else c[0] - rows[k]["pivot"][0])
                sure = [v for v in rel if v is not None]
                if sure:
                    target = float(np.median(sure))
                    for k, v in enumerate(rel):
                        m = int(round(target - v)) if v is not None else 0
                        if m:
                            out[k] = shift(out[k], m, 0)
                            info[k]["move"][0] += m
        save_cells(out, cell, os.path.join(SRC, f"{hero}_{tag}.png"))
        report["tags"][tag] = info
        print(f"{tag:7s} " + "  ".join(
            "kept" if i.get("kept") else f"x{i['scale']:.2f} {i['move'][0]:+d},{i['move'][1]:+d} "
            f"{i['placed_by'].split()[0][:5]}{'+feet' if 'soles' in i['placed_by'] else ''}" for i in info))
        if args.review:
            review_sheet(os.path.join(args.review, f"{hero}_fit_{tag}.png"), cell, feet, rows, ref, src, out, off)
    with open(lp(os.path.join(SRC, f"{hero}_fit.json")), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
