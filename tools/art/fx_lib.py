"""Small pixel VFX primitives (hard colour ramps, alpha 0 or 255) for the few effects still drawn in
code: dash streaks and the oath aura. Skill art comes from generated images (import_fx.py).

Angles are screen angles in degrees: 0 = right, 90 = down, -90 = up (y grows downward).
Every function paints into an RGBA PIL image in place.
"""
import math
import random

import numpy as np
from PIL import Image

# ramps go from the hot edge / core (index 0) to the cool fringe
GOLD = [(255, 255, 236), (255, 244, 170), (255, 214, 86), (240, 160, 40), (196, 104, 26)]
HOLY = [(255, 255, 255), (255, 250, 206), (255, 226, 120), (250, 186, 58), (214, 128, 30)]
FIRE = [(255, 255, 214), (255, 232, 110), (255, 170, 44), (234, 96, 26), (170, 44, 24)]
WHITE = [(255, 255, 255), (236, 244, 255), (196, 214, 244), (150, 170, 220)]


def _put(a, x, y, rgb):
    h, w = a.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        a[y, x, :3] = rgb
        a[y, x, 3] = 255


def _grid(img):
    a = np.asarray(img).copy()
    h, w = a.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    return a, xs + 0.5, ys + 0.5


def _paint(img, a, mask, idx, ramp):
    idx = np.clip(idx, 0, len(ramp) - 1).astype(int)
    cols = np.array(ramp, np.uint8)
    a[mask, :3] = cols[idx[mask]]
    a[mask, 3] = 255
    img.paste(Image.fromarray(a, "RGBA"))


def ang_diff(a, b):
    """Signed smallest difference a - b in degrees."""
    return (a - b + 180) % 360 - 180


def ring(img, cx, cy, rx, ry, thick, ramp=GOLD, a0=None, a1=None, gaps=0, gap_phase=0.0, seed=None,
         rough=0.0):
    """Elliptic band (ground rings). Optional arc range, dashed gaps and rough edges."""
    a, X, Y = _grid(img)
    dx, dy = X - cx, Y - cy
    rr = np.hypot(dx / rx, dy / ry) * rx  # radius in x-pixels
    th = np.degrees(np.arctan2(dy / ry, dx / rx))
    t = np.full(rr.shape, float(thick))
    if rough and seed is not None:
        rnd = np.random.default_rng(seed)
        ph = rnd.uniform(0, 2 * np.pi, 4)
        t = t * (1 + rough * (np.sin(np.radians(th) * 3 + ph[0]) * 0.5 + np.sin(np.radians(th) * 7 + ph[1]) * 0.5))
    mask = (rr <= rx) & (rr >= rx - t)
    if a0 is not None:
        mask &= (ang_diff(th, a0) >= 0) & (ang_diff(th, a0) <= ang_diff(a1, a0) % 360)
    if gaps:
        seg = (th + 180 + gap_phase) % (360 / gaps)
        mask &= seg > (360 / gaps) * 0.28
    depth = (rx - rr) / np.maximum(t, 1e-3)
    idx = np.floor(np.abs(depth - 0.35) * 2 * (len(ramp) - 0.01))  # brightest a third of the way in
    _paint(img, a, mask, idx, ramp)


def sparkle(img, x, y, size=2, ramp=HOLY):
    """4-point star: white centre, arms of length `size` fading through the ramp."""
    a = np.asarray(img).copy()
    x, y = int(round(x)), int(round(y))
    _put(a, x, y, ramp[0])
    for k in range(1, size + 1):
        c = ramp[min(len(ramp) - 1, k)]
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            _put(a, x + dx, y + dy, c)
    if size >= 3:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            _put(a, x + dx, y + dy, ramp[2])
    img.paste(Image.fromarray(a, "RGBA"))


def streaks(img, x0, x1, ys, ramp=GOLD, seed=0, dash=True):
    """Horizontal speed lines from x1 (hot, near the body) back to x0."""
    rnd = random.Random(seed)
    a = np.asarray(img).copy()
    for y in ys:
        start = x1 - rnd.randint(0, 4)
        length = rnd.randint(max(3, (x1 - x0) // 2), max(4, x1 - x0))
        for i in range(length):
            x = start - i
            if dash and rnd.random() < 0.08:
                continue
            c = ramp[min(len(ramp) - 1, int(i / max(1, length) * len(ramp)))]
            _put(a, x, y, c)
    img.paste(Image.fromarray(a, "RGBA"))
