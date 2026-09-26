#!/usr/bin/env python3
"""Reference images for redrawing a hero at its real pixel size (assets/source/NATIVE_REDRAW.md).

    python tools/art/native_refs.py --out DIR [--hero lux --hero ashe] [--style]

For every animation of league/champions/league_<hero> writes <hero>_now_<tag>.png: the current
game frames at 8x (every game pixel an 8x8 block), in a grid of 56x64-pixel cells read left to
right, top to bottom (2 frames: 2x1, 6: 3x2, 7-8: 4x2), each frame centred across its cell with its
feet on the cell's line 10 px above the bottom. <hero>_now_design.png: idle frame 1 on a 128x128
canvas at 8x (1024x1024). The redraw keeps these cells, so tools/art/import_native.py can put each
redrawn frame back where the current one stands.
--style writes tfm2_style_ref.png / tfm2_style_ref_mage.png: base heroes' idle frame 1 (top row)
and attack middle frame (bottom row), feet aligned, at 8x - read from the game's bundle, keep local.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

Z = 8                    # game pixel -> 8x8 block
CELL = (56, 64)          # cell size in game pixels
FEET_ROW = CELL[1] - 10  # the feet line in a cell (the row under the soles)
BG = (225, 225, 225, 255)
STYLE = {
    "tfm2_style_ref.png": ["archer", "crossbowman", "harpooner", "knight", "spellbreaker", "fighter", "swordman", "priest"],
    "tfm2_style_ref_mage.png": ["white_mage", "priest", "enchanter", "druid", "pyromancer", "illusionist", "dark_mage",
                                "barrier_magician"],
}


def layout(n):
    """Columns x rows of the grid for n frames."""
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def cells(sp, tag):
    """[(frame image cropped to its content, (x, y) of the crop in the cell)] for a tag."""
    out = []
    for i in sp.tag_frames(tag):
        f = sp.frames[i]
        x0, y0, x1, y1 = f.getbbox()
        feet = sp.h // 2 + 12                       # pivot row + 11.5 -> the row under the soles
        top = FEET_ROW - (feet - y0)
        left = (CELL[0] - (x1 - x0)) // 2
        out.append((f.crop((x0, y0, x1, y1)), (left, top)))
    return out


def grid(sp, tag):
    items = cells(sp, tag)
    cols, rows = layout(len(items))
    img = Image.new("RGBA", (cols * CELL[0], rows * CELL[1]), BG)
    for k, (f, (x, y)) in enumerate(items):
        cx, cy = (k % cols) * CELL[0], (k // cols) * CELL[1]
        img.alpha_composite(f, (cx + x, cy + y))
    return img.resize((img.width * Z, img.height * Z), Image.NEAREST)


def design(sp):
    f = sp.frames[sp.tag_frames("idle")[0]]
    x0, y0, x1, y1 = f.getbbox()
    img = Image.new("RGBA", (128, 128), BG)
    img.alpha_composite(f.crop((x0, y0, x1, y1)), ((128 - (x1 - x0)) // 2, 100 - (y1 - y0)))
    return img.resize((128 * Z, 128 * Z), Image.NEAREST)


def style(names):
    rows = {"idle": [], "attack": []}
    for n in names:
        sp = T.load_sprite(f"asset/base/aseprite_resources/champions/{n}")
        for tag in rows:
            fr = sp.tag_frames(tag)
            f = sp.frames[fr[0] if tag == "idle" else fr[len(fr) // 2]]
            rows[tag].append(f.crop(f.getbbox()))
    cw = max(max(i.width for i in r) for r in rows.values()) + 6
    ch = max(max(i.height for i in r) for r in rows.values()) + 6
    img = Image.new("RGBA", (cw * len(names), ch * 2), BG)
    for y, r in enumerate(rows.values()):
        for x, im in enumerate(r):
            img.alpha_composite(im, (x * cw + (cw - im.width) // 2, y * ch + ch - 3 - im.height))
    return img.resize((img.width * Z, img.height * Z), Image.NEAREST).convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hero", action="append", default=[])
    ap.add_argument("--style", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for hero in args.hero:
        sp = T.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}#sheet.png"))
        design(sp).convert("RGB").save(os.path.join(args.out, f"{hero}_now_design.png"))
        for t in sp.tags:
            img = grid(sp, t["name"])
            img.convert("RGB").save(os.path.join(args.out, f"{hero}_now_{t['name']}.png"))
            cols, rows = layout(len(sp.tag_frames(t["name"])))
            print(f"{hero}_now_{t['name']}.png  {len(sp.tag_frames(t['name']))} frames, {cols}x{rows} cells, {img.size[0]}x{img.size[1]}")
    if args.style:
        for fname, names in STYLE.items():
            img = style(names)
            img.save(os.path.join(args.out, fname))
            print(fname, img.size)


if __name__ == "__main__":
    main()
