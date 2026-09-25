"""Turn the generated effect sheets into game-scale pixel sprites.

Source: assets/source/arthur_fx/*.png (gpt-image-2 via Codex, one row of frames per sheet, real
alpha, generous padding; see its README.md and manifest.json). Every frame is:
  1. cut from the sheet with the manifest rectangle,
  2. cropped with a box shared by all frames of that sheet (keeps the anchor between frames),
  3. area-averaged down to game scale in premultiplied alpha,
  4. made hard-edged: alpha is 0 or 255 (small bright sparks are kept by a max-pooled test),
  5. snapped to Arthur's gold ramp (or a small adaptive palette for the flaming shield).
"""
import functools
import json
import math
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SRC = os.path.join(ROOT, "assets", "source", "arthur_fx")

# white-hot core -> pale gold -> gold -> orange -> deep amber (shared with the sprite's sword light)
GOLD_FX = [(255, 255, 255), (255, 250, 214), (255, 236, 150), (255, 214, 86), (246, 168, 46),
           (214, 120, 30), (158, 74, 22), (100, 44, 16)]


def _lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


@functools.lru_cache(maxsize=None)
def _manifest():
    with open(_lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {a["file"].rsplit(".", 1)[0]: a for a in json.load(f)["assets"]}


@functools.lru_cache(maxsize=None)
def cells(name):
    """Full-height cells of one sheet, as RGBA arrays (float 0..1)."""
    entry = _manifest()[name]
    img = Image.open(_lp(os.path.join(SRC, entry["file"]))).convert("RGBA")
    out = []
    for c in entry["source_cells"]:
        x, y, w, h = c["suggested_source_rect_xywh"]
        out.append(np.asarray(img.crop((x, y, x + w, y + h))).astype(np.float32) / 255.0)
    return tuple(out)


def shared_box(arrs, alpha_min=0.08):
    """One crop box (x0, y0, x1, y1) covering every frame's visible pixels."""
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    for a in arrs:
        ys, xs = np.nonzero(a[..., 3] >= alpha_min)
        if len(xs):
            x0, y0 = min(x0, xs.min()), min(y0, ys.min())
            x1, y1 = max(x1, xs.max() + 1), max(y1, ys.max() + 1)
    return int(x0), int(y0), int(x1), int(y1)


def _resize_f(ch, size, resample):
    return np.asarray(Image.fromarray(ch.astype(np.float32), "F").resize(size, resample))


def pixelize(arr, scale, palette=GOLD_FX, cut=0.4, keep=0.85, boost=1.08):
    """Premultiplied area downscale -> hard alpha -> nearest palette colour. Returns RGBA Image."""
    h, w = arr.shape[:2]
    W, H = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    al = arr[..., 3]
    prem = arr[..., :3] * al[..., None]
    a_avg = _resize_f(al, (W, H), Image.BOX)
    rgb = np.stack([_resize_f(prem[..., c], (W, H), Image.BOX) for c in range(3)], -1)
    rgb = rgb / np.maximum(a_avg, 1e-4)[..., None]
    # tiny bright sparks would average away: keep a pixel whose block holds a near-opaque dot
    k = max(3, int(round(1 / scale)) | 1)
    a_max = _resize_f(np.asarray(Image.fromarray(al, "F").filter(ImageFilter.MaxFilter(min(k, 15)))), (W, H),
                      Image.NEAREST)
    opaque = (a_avg >= cut) | ((a_max >= keep) & (a_avg >= cut * 0.3))
    rgb = np.clip((rgb - 0.5) * boost + 0.5, 0, 1) * 255
    out = np.zeros((H, W, 4), np.uint8)
    if palette is None:  # adaptive (flaming shield): median cut over the opaque pixels
        pix = rgb[opaque].astype(np.uint8)
        if len(pix):
            q = Image.fromarray(pix.reshape(1, -1, 3), "RGB").quantize(colors=20, method=Image.Quantize.MEDIANCUT,
                                                                        dither=Image.Dither.NONE)
            out[opaque, :3] = np.asarray(q.convert("RGB")).reshape(-1, 3)
    else:
        pal = np.array(palette, np.float32)
        d = ((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1)
        out[..., :3] = pal[d.argmin(-1)].astype(np.uint8)
    out[..., 3] = np.where(opaque, 255, 0)
    out[~opaque, :3] = 0
    return Image.fromarray(out, "RGBA")


@functools.lru_cache(maxsize=None)
def sheet(name, scale, palette=tuple(GOLD_FX)):
    """All frames of a sheet cropped with one shared box and pixelized at `scale` (same size each)."""
    arrs = cells(name)
    x0, y0, x1, y1 = shared_box(arrs)
    pal = None if palette is None else list(palette)
    return tuple(pixelize(a[y0:y1, x0:x1], scale, pal) for a in arrs), (x0, y0)


def centred(img, size, anchor=None):
    """Paste `img` into a size x size canvas with `anchor` (default: its centre) on the centre pixel."""
    W, H = (size, size) if isinstance(size, int) else size
    ax, ay = anchor if anchor else (img.width / 2, img.height / 2)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(img, (int(round(W // 2 + 0.5 - ax)), int(round(H // 2 + 0.5 - ay))))
    out.alpha_composite(layer)
    return out


def scale_for(name, frame, target, axis="max"):
    """Scale that makes `frame`'s visible size `target` px (width, height or the larger one)."""
    b = _manifest()[name]["source_cells"][frame]["opaque_bounds_in_source_xywh"]
    size = {"w": b[2], "h": b[3], "max": max(b[2], b[3])}[axis]
    return target / size


def circle_centre(img):
    """Least-squares circle through the opaque pixels (rings: robust to the little flame wisps)."""
    a = np.asarray(img)[..., 3] > 0
    ys, xs = np.nonzero(a)
    A = np.c_[2 * xs, 2 * ys, np.ones(len(xs))]
    cx, cy, _ = np.linalg.lstsq(A.astype(np.float64), (xs ** 2 + ys ** 2).astype(np.float64), rcond=None)[0]
    return float(cx), float(cy)


# ----------------------------------------------------------------------------- pieces for the sprite
def _alpha_centroid(a, thresh=0.5):
    ys, xs = np.nonzero(a[..., 3] >= thresh)
    return float(xs.mean()), float(ys.mean())


@functools.lru_cache(maxsize=None)
def arc_sprite(frame, radius, max_thick=7):
    """Sword swing arc (opens to the left, faces right). Returns (image, pivot = circle centre).

    The circle is fitted to the outer rim of the full arc (frame 1), then shared by all frames.
    The inner side is trimmed to `max_thick` px so the arc never covers Arthur's face."""
    arrs = cells("slash_arc")
    full = arrs[1][..., 3] >= 0.5
    pts = []
    for y in range(full.shape[0]):
        xs = np.nonzero(full[y])[0]
        if len(xs):
            pts.append((xs.max(), y))
    p = np.array(pts, np.float64)
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    b = (p ** 2).sum(1)
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    r_src = math.sqrt(c + cx * cx + cy * cy)
    scale = radius / r_src
    x0, y0, x1, y1 = shared_box(arrs)
    img = pixelize(arrs[frame][y0:y1, x0:x1], scale)
    pv = ((cx - x0) * scale, (cy - y0) * scale)
    a = np.asarray(img).copy()
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    a[np.hypot(xx + 0.5 - pv[0], yy + 0.5 - pv[1]) < radius - max_thick, 3] = 0
    return Image.fromarray(a, "RGBA"), pv


@functools.lru_cache(maxsize=None)
def light_sword(length):
    """The generated blade of light (excalibur frame 0), pointing up. Returns (image, grip pivot)."""
    a = cells("excalibur")[0]
    x0, y0, x1, y1 = shared_box([a], 0.3)
    crop = a[y0:y1, x0:x1][::-1]          # source points down; flip so the blade points up
    scale = length / (y1 - y0)
    img = pixelize(crop, scale, cut=0.35)
    grip = (img.width / 2, img.height * 0.9)   # hilt end
    return img, grip


@functools.lru_cache(maxsize=None)
def spark(frame, size, squash=1.0):
    """A hit_spark frame, `size` px across (for sword-tip glints and ground flashes)."""
    a = cells("hit_spark")[frame]
    x0, y0, x1, y1 = shared_box([a], 0.2)
    img = pixelize(a[y0:y1, x0:x1], size / max(x1 - x0, y1 - y0), cut=0.35)
    if squash != 1.0:
        img = img.resize((img.width, max(1, int(round(img.height * squash)))), Image.NEAREST)
    return img
