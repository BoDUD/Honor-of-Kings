#!/usr/bin/env python3
"""Import Lee Sin's effects (assets/source/leesin/PROMPTS.md, 11-19) as game sheets.

    python tools/art/import_leesin.py

The body comes from tools/art/fit_native.py + tools/art/import_native.py. The nine effect strips
came back from the Codex run as native pixel art: every game pixel one flat 8x8 block, frames in
equal cells (32 px square, the Q wave 32x16, the dragon 64x32). They are read one pixel per block,
enlarged by a whole factor where the effect must cover more than its 32 px cell (Tempest's ring
covers the 32000 radius, Safeguard's bubble the whole unit: 2x), and each frame is anchored on its
cell - GPT and Codex left every frame where it is drawn in its cell - or, for the two projectiles,
on their head (the wave's front crescent, the dragon's head), then placed at a spot relative to the
unit's pivot (11.5 px above the feet): hits and marks on the chest, the ground ring at the feet.
No palette or outline pass: the effects keep the delivery's colours.
Writes league/effects/league_leesin_fx (hit, q_wave, q_mark, q2_hit, e_wave, shield, knockup) and
league/effects/league_leesin_r (kick, dragon).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "leesin")
MOD = os.path.join(ROOT, "league")
Z = 8


def cells(name, n):
    """The strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"leesin_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"leesin_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def centre(f):
    """Anchor: the middle of the cell."""
    return f.shape[1] / 2.0, f.shape[0] / 2.0


def head(f):
    """Anchor for a projectile flying right: the front of its drawing, 3 px back, at the height of
    the pixels in its front quarter."""
    ys, xs = np.nonzero(f[..., 3])
    x1 = xs.max()
    front = xs >= x1 - max(3, (x1 - xs.min()) // 4)
    return x1 - 2.5, float(np.median(ys[front])) + 0.5


def loop(frames, first, last, times):
    """Frames [first, last) played `times` times."""
    return frames[:first] + frames[first:last] * times + frames[last:]


# sprite: {tag: (strip, frames, enlarge, anchor, spot from the pivot, ms per frame, loop)}
FX = {
    "league_leesin_fx": {
        "hit": ("fx_hit", 5, 1, centre, (0, -4), [60] * 5, None),
        "q_wave": ("fx_q_wave", 4, 1, head, (0, 0), [60] * 4, None),
        # from the wave's hit until Resonating Strike lands (0.2 s delay + the dash)
        "q_mark": ("fx_q_mark", 6, 1, centre, (0, -4), [60, 60, 60, 60, 60, 80], (1, 5, 2)),
        "q2_hit": ("fx_q2_hit", 6, 1, centre, (0, -4), [70] * 6, None),
        # the ring lies on the ground around Lee Sin: its centre on the feet line
        "e_wave": ("fx_e_wave", 7, 2, centre, (0, 11), [70] * 7, None),
        # the 2 s shield: frames 3-6 three times
        "shield": ("fx_shield", 8, 2, centre, (0, -5), [100, 100, 133, 133, 133, 134, 100, 100], (2, 6, 3)),
        "knockup": ("fx_knockup", 6, 1, centre, (0, 2), [70] * 6, None),
    },
    "league_leesin_r": {
        "kick": ("fx_r_kick", 7, 1, centre, (0, -4), [70] * 7, None),
        "dragon": ("fx_r_dragon", 4, 1, head, (0, 0), [70] * 4, None),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (strip, n, k, anchor, (sx, sy), ms, lp_) in tags.items():
            frames = []
            for f, m in zip(cells(strip, n), ms):
                ax, ay = anchor(f)
                if k > 1:
                    f = np.kron(f, np.ones((k, k, 1), np.uint8))
                    ax, ay = ax * k, ay * k
                # the frame's top-left corner relative to the pivot pixel
                u0, r0 = int(round(sx - ax)), int(round(sy - ay))
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
