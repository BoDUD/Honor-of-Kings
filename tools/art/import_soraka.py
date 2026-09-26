#!/usr/bin/env python3
"""Import Soraka's effects (assets/source/soraka/PROMPTS.md, 10-18) as game sheets.

    python tools/art/import_soraka.py

The body comes from tools/art/import_native.py (with assets/source/native/soraka_retouch.json).
The nine effect strips came back from the Codex run as native pixel art: every game pixel one flat
8x8 block, frames in equal cells (32 px square; the bolt 32x16; the falling star and the Wish
pillar 32x64). They are read one pixel per block and anchored where the handoff says each frame is
drawn (codex/HANDOFF.md): the bolt on its crescent, hits on their centre, the ground effects on the
landing point or the ring's centre, the effects around a person on that person's feet. Everything
drawn around a person-sized space is enlarged 2x - the space is about 19 px tall in a 32 px cell,
a hero 34 - and so are the star's ring and the Equinox field, which then span about 60 px, the
30000 radius of league_soraka's Q and E. Views are drawn at the unit's pivot, 11 px above the feet
line (import_leesin.py and import_lux.py do the same), so feet and ground anchors go 11 px below it.
No palette or outline pass: the effects keep the delivery's colours.
Writes league/effects/league_soraka_fx (bolt, hit, rejuv, e_bind, w_heal),
league/effects/league_soraka_zone (q_star, e_field) and league/effects/league_soraka_r (cast, heal).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "soraka")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                        # the feet line / the ground, from the pivot


def cells(name, n):
    """The strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"soraka_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"soraka_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def loop(frames, first, last, times):
    """Frames [first, last) played `times` times."""
    return frames[:first] + frames[first:last] * times + frames[last:]


# sprite: {tag: (strip, frames, enlarge, anchor in the cell, spot from the pivot, ms per frame, loop)}
# The anchors are the handoff's (codex/HANDOFF.md, "特效接线").
FX = {
    "league_soraka_fx": {
        "bolt": ("fx_bolt", 4, 1, (24, 8), (0, 0), [60] * 4, None),
        "hit": ("fx_hit", 5, 1, (16, 16), (0, -4), [60] * 5, None),
        "rejuv": ("fx_rejuv", 6, 2, (16, 28), FEET, [80] * 6, None),
        # the 1 s root: frames 3-5 twice
        "e_bind": ("fx_e_bind", 6, 2, (16, 28), FEET, [100, 100, 120, 120, 120, 80], (2, 5, 2)),
        "w_heal": ("fx_w_heal", 7, 2, (16, 28), FEET, [80] * 7, None),
    },
    "league_soraka_zone": {
        # 24 ticks falling, the hit on frame 5, 10 ticks live: 34 ticks = 570 ms
        "q_star": ("fx_q_star", 8, 2, (16, 56), FEET, [100, 100, 100, 100, 40, 40, 40, 50], None),
        # 90 ticks: opening, frames 3-6 twice, the flash that closes it just before the root
        "e_field": ("fx_e_field", 8, 2, (16, 16), FEET, [80, 80, 135, 135, 135, 135, 180, 80], (2, 6, 2)),
    },
    "league_soraka_r": {
        "cast": ("fx_r_cast", 7, 2, (16, 29), FEET, [90] * 7, None),
        "heal": ("fx_r_heal", 8, 2, (16, 60), FEET, [90] * 8, None),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (strip, n, k, (ax, ay), (sx, sy), ms, lp_) in tags.items():
            frames = []
            for f, m in zip(cells(strip, n), ms):
                if k > 1:
                    f = np.kron(f, np.ones((k, k, 1), np.uint8))
                # the frame's top-left corner relative to the pivot pixel (anchors are pixel corners)
                u0, r0 = int(sx - ax * k), int(sy - ay * k)
                frames.append((G.centre_frame(f, u0, r0), m))
            if lp_:
                frames = loop(frames, *lp_)
            out[tag] = frames
        sheets[sprite] = out
    return sheets


def main():
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
