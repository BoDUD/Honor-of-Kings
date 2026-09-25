"""Turn generated sprite strips (one row of frames, real alpha) into TFM2 pixel frames.

A library for per-hero import scripts (worked example: tools/art/import_garen.py in the
TFM2-League-Heroes repo); see references/art-spec.md "Generated art". Needs numpy + Pillow.

  split_strip   find the N frames of a strip: cut near the equal-width boundaries at the emptiest
                columns, then give every connected blob to the frame holding most of it (a sword
                reaching into the neighbour cell stays whole)
  feet_mid, leg_band, best_shift
                line frames up by their legs (generated frames are not evenly spaced)
  render        area-downscale a frame so a chosen source point lands on a chosen sub-pixel of the
                output grid (pivot-relative), hard alpha, no anti-aliasing
  Palette       one shared palette per sprite (median cut), nearest-colour mapping
  outline       1 px near-black silhouette outline (glowing pixels are left alone)
  centre_frame  trim to an odd size centred on the pivot (the exported-sheet convention)
  write_sheet   pack frames into name#sheet.png + name#anim.fanim
"""
import json
import os

import numpy as np
from PIL import Image, ImageFilter

OUTLINE = (14, 12, 18)


def lp(path):
    """Windows long-path form (the repo can live in a deep folder)."""
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith("\\\\?\\"):
        path = "\\\\?\\UNC\\" + path[2:] if path.startswith("\\\\") else "\\\\?\\" + path
    return path


def load_rgba(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).astype(np.float32) / 255.0


# ----------------------------------------------------------------------------- segmentation
def gap_cuts(alpha, n, window=0.28, thresh=0.35):
    """Column cuts: near each equal-width boundary, the middle of the widest emptiest run."""
    col = (alpha > thresh).sum(0)
    W = len(col)
    cuts = [0]
    for i in range(1, n):
        c = int(round(i * W / n))
        win = int(W / n * window)
        lo, hi = max(cuts[-1] + 5, c - win), min(W - 5, c + win)
        seg = col[lo:hi]
        idx = np.nonzero(seg == seg.min())[0]
        runs, start = [], idx[0]
        for a, b in zip(idx, idx[1:]):
            if b != a + 1:
                runs.append((start, a))
                start = b
        runs.append((start, idx[-1]))
        s, e = max(runs, key=lambda r: r[1] - r[0])
        cuts.append(lo + (s + e) // 2)
    cuts.append(W)
    return cuts


def label(mask):
    """8-connected component labels (run-length union-find). Returns (labels, count)."""
    H, W = mask.shape
    labels = np.zeros((H, W), np.int32)
    parent = [0]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    prev = []
    for y in range(H):
        d = np.diff(np.concatenate([[0], mask[y].astype(np.int8), [0]]))
        starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        cur = []
        for s, e in zip(starts, ends):
            lab = None
            for ps, pe, pl in prev:
                if ps <= e and pe >= s:          # touching, diagonals included
                    r = find(pl)
                    if lab is None:
                        lab = r
                    elif r != lab:
                        parent[r] = lab
            if lab is None:
                lab = len(parent)
                parent.append(lab)
            labels[y, s:e] = lab
            cur.append((s, e, lab))
        prev = cur
    lut = np.array([find(i) for i in range(len(parent))], np.int32)
    uniq, inv = np.unique(lut[labels], return_inverse=True)
    return inv.reshape(H, W).astype(np.int32), len(uniq) - 1


class Frame:
    """One frame cut from a strip: `a` is float RGBA cropped to the content, (ox, oy) its offset
    in strip coordinates, `cell` the index of the frame."""

    def __init__(self, a, ox, oy, cell):
        self.a, self.ox, self.oy, self.cell = a, ox, oy, cell

    def bbox(self, thresh=0.5):
        """Content box in strip coordinates (x0, y0, x1, y1), exclusive ends."""
        ys, xs = np.nonzero(self.a[..., 3] > thresh)
        return (int(xs.min()) + self.ox, int(ys.min()) + self.oy,
                int(xs.max()) + 1 + self.ox, int(ys.max()) + 1 + self.oy)

    @property
    def ground(self):
        """Bottom edge of the lowest solid row (strip coordinates)."""
        return self.bbox()[3]


def split_strip(img, n, blob_thresh=0.12, margin=6):
    """Float RGBA strip -> n Frames."""
    alpha = img[..., 3]
    cuts = gap_cuts(alpha, n)
    lab, count = label(alpha > blob_thresh)
    col_frame = np.zeros(alpha.shape[1], np.int32)
    for i in range(n):
        col_frame[cuts[i]:cuts[i + 1]] = i
    keep = np.full(alpha.shape, -1, np.int32)   # frame index per pixel
    ys, xs = np.nonzero(lab)
    ids = lab[ys, xs]
    order = np.argsort(ids, kind="stable")
    ids, ys, xs = ids[order], ys[order], xs[order]
    bounds = np.searchsorted(ids, np.arange(1, count + 2))
    for k in range(count):
        s, e = bounds[k], bounds[k + 1]
        if s == e:
            continue
        fy, fx = ys[s:e], xs[s:e]
        frames = col_frame[fx]
        counts = np.bincount(frames, minlength=n)
        best = int(counts.argmax())
        if counts[best] >= 0.7 * len(fx):
            keep[fy, fx] = best
        else:                                   # a blob across two bodies: cut at the column
            keep[fy, fx] = frames
    out = []
    H, W = alpha.shape
    for i in range(n):
        m = keep == i
        ys, xs = np.nonzero(m)
        x0, x1 = max(0, xs.min() - margin), min(W, xs.max() + 1 + margin)
        y0, y1 = max(0, ys.min() - margin), min(H, ys.max() + 1 + margin)
        a = img[y0:y1, x0:x1].copy()
        a[..., 3] = np.where(m[y0:y1, x0:x1], a[..., 3], 0.0)
        out.append(Frame(a, x0, y0, i))
    return out


# ----------------------------------------------------------------------------- alignment
def feet_mid(fr, s):
    """Middle of the solid pixels in the lowest 1.2 game px of the frame (strip x); s = scale."""
    x0, y0, x1, y1 = fr.bbox()
    h = max(3, int(round(1.2 / s)))
    band = fr.a[y1 - fr.oy - h:y1 - fr.oy, :, 3] > 0.5
    xs = np.nonzero(band.any(0))[0]
    return (xs.min() + xs.max() + 1) / 2.0 + fr.ox


def leg_band(fr, s, ax, gy, height=12, half=40, sup=4):
    """Solid mask of the lowest `height` game px around strip x=ax (ground edge gy),
    sampled at sup x game resolution."""
    k = 1.0 / s
    box = (ax - half * k - fr.ox, gy - height * k - fr.oy, ax + half * k - fr.ox, gy - fr.oy)
    return resample(fr.a[..., 3], box, (2 * half * sup, height * sup)) > 0.5


def best_shift(ref, mov, r=40):
    """Sub-pixel shift d so that `mov` moved left by d overlaps `ref` best (ties: the middle of
    the plateau). Divide by sup * scale to get source px."""
    W = ref.shape[1]
    scores = []
    for d in range(-r, r + 1):
        if d >= 0:
            scores.append((ref[:, :W - d] & mov[:, d:]).sum())
        else:
            scores.append((ref[:, -d:] & mov[:, :W + d]).sum())
    scores = np.array(scores)
    best = np.nonzero(scores == scores.max())[0]
    return (best[0] + best[-1]) / 2.0 - r


# ----------------------------------------------------------------------------- resampling
def resample(ch, box, size, method=Image.BOX):
    """Resize the float channel region `box` (x0, y0, x1, y1; may leave the array) to `size`."""
    x0, y0, x1, y1 = box
    H, W = ch.shape
    pl, pt = max(0, int(np.ceil(-x0))) + 1, max(0, int(np.ceil(-y0))) + 1
    pr, pb = max(0, int(np.ceil(x1 - W))) + 1, max(0, int(np.ceil(y1 - H))) + 1
    ch = np.pad(ch, ((pt, pb), (pl, pr)))
    im = Image.fromarray(ch.astype(np.float32), "F")
    return np.asarray(im.resize(size, method, box=(x0 + pl, y0 + pt, x1 + pl, y1 + pt)))


def render(fr, sx, sy, ax, ay, X0=0.0, Y0=0.0, cut=0.5, keep=None, pad=2):
    """Downscale Frame `fr` so the strip point (ax, ay) lands at (X0, Y0) in pivot coordinates
    (pivot pixel centre = (0, 0), +y down). Returns (uint8 RGBA, u0, r0): the array and the
    pivot-relative column/row of its top-left pixel.

    cut:  minimum covered fraction for an opaque pixel
    keep: if set, a pixel is also opaque when a solid source pixel (alpha >= keep) falls in it
          and it is at least cut/3 covered - small bright sparks survive the downscale."""
    a = fr.a
    x0, y0, x1, y1 = fr.bbox(0.05)
    u0 = int(np.floor((x0 - ax) * sx + X0 + 0.5)) - pad
    u1 = int(np.ceil((x1 - ax) * sx + X0 - 0.5)) + pad
    r0 = int(np.floor((y0 - ay) * sy + Y0 + 0.5)) - pad
    r1 = int(np.ceil((y1 - ay) * sy + Y0 - 0.5)) + pad
    W, H = u1 - u0 + 1, r1 - r0 + 1
    # output pixel (u, r) spans [u-0.5, u+0.5] -> source x = ax + (X - X0) / sx, minus the crop offset
    bx0 = ax + (u0 - 0.5 - X0) / sx - fr.ox
    bx1 = ax + (u1 + 0.5 - X0) / sx - fr.ox
    by0 = ay + (r0 - 0.5 - Y0) / sy - fr.oy
    by1 = ay + (r1 + 0.5 - Y0) / sy - fr.oy
    box = (bx0, by0, bx1, by1)
    al = a[..., 3]
    a_avg = resample(al, box, (W, H))
    rgb = np.stack([resample(a[..., c] * al, box, (W, H)) for c in range(3)], -1)
    rgb = rgb / np.maximum(a_avg, 1e-4)[..., None]
    opaque = a_avg >= cut
    if keep is not None:
        k = int(max(3, round(1 / min(sx, sy)))) | 1
        solid = np.asarray(Image.fromarray((al >= keep).astype(np.float32), "F")
                           .filter(ImageFilter.MaxFilter(min(k, 31))))
        hit = resample(solid, box, (W, H), Image.NEAREST) > 0.5
        opaque |= hit & (a_avg >= cut / 3)
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(opaque, 255, 0)
    out[~opaque, :3] = 0
    return out, u0, r0


# ----------------------------------------------------------------------------- colour
class Palette:
    """Median-cut palette over the opaque pixels of many frames; nearest-colour mapping."""

    def __init__(self, arrays, colors=64, extra=(OUTLINE,)):
        pix = np.concatenate([f[f[..., 3] > 0][:, :3] for f in arrays])
        img = Image.fromarray(pix.reshape(1, -1, 3), "RGB")
        q = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        pal = np.array(q.getpalette()[:colors * 3], np.float32).reshape(-1, 3)
        pal = pal[np.unique(np.asarray(q).ravel())]
        for c in extra:
            if not (np.abs(pal - np.array(c, np.float32)).sum(1) < 30).any():
                pal = np.vstack([pal, [c]])
        self.colors = pal

    def apply(self, f):
        out = f.copy()
        m = out[..., 3] > 0
        px = out[m][:, :3].astype(np.float32)
        d = ((px[:, None, :] - self.colors[None]) ** 2).sum(-1)
        out[m, :3] = self.colors[d.argmin(1)].astype(np.uint8)
        return out


def lum(rgb):
    rgb = rgb.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def outline(f, color=OUTLINE, glow=205):
    """Silhouette-edge pixels become `color`, except glowing ones (luminance > glow)."""
    out = f.copy()
    op = out[..., 3] > 0
    p = np.pad(op, 1)
    edge = op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    edge &= lum(out[..., :3]) <= glow
    out[edge, :3] = color
    return out


def drop_lonely(f):
    """Remove opaque pixels without any opaque 8-neighbour (downscale crumbs)."""
    op = f[..., 3] > 0
    p = np.pad(op, 1).astype(np.int8)
    n = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx]
            for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    out = f.copy()
    out[op & (n == 0)] = 0
    return out


# ----------------------------------------------------------------------------- output
def centre_frame(arr, u0, r0):
    """Trim to the content and pad symmetrically so the pivot pixel is the exact centre (odd size)."""
    ys, xs = np.nonzero(arr[..., 3])
    if not len(xs):
        return np.zeros((1, 1, 4), np.uint8)
    cu0, cu1 = xs.min() + u0, xs.max() + u0          # pivot-relative content extents
    cr0, cr1 = ys.min() + r0, ys.max() + r0
    hw = max(-cu0, cu1, 0)
    hh = max(-cr0, cr1, 0)
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    sub = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out[hh + cr0:hh + cr0 + sub.shape[0], hw + cu0:hw + cu0 + sub.shape[1]] = sub
    return out


def write_sheet(path_stem, tags, gap=1, max_w=2048):
    """tags: {tag: [(frame_array, duration_ms), ...]} -> path_stem#sheet.png + path_stem#anim.fanim.
    Frames are shelf-packed left to right (1 px gaps), a new shelf when max_w is reached."""
    rects, x, y, shelf_h = [], 0, 0, 0
    for tag, frames in tags.items():
        for arr, _ in frames:
            h, w = arr.shape[:2]
            if x and x + w > max_w:
                x, y, shelf_h = 0, y + shelf_h + gap, 0
            rects.append((x, y, w, h))
            x += w + gap
            shelf_h = max(shelf_h, h)
    W = max(r[0] + r[2] for r in rects)
    H = max(r[1] + r[3] for r in rects)
    sheet = np.zeros((H, W, 4), np.uint8)
    anims, i = {}, 0
    for tag, frames in tags.items():
        out = []
        for arr, ms in frames:
            rx, ry, rw, rh = rects[i]
            sheet[ry:ry + rh, rx:rx + rw] = arr
            out.append({"duration": round(ms / 1000.0, 6),
                        "data": {"x": float(rx), "y": float(ry), "w": float(rw), "h": float(rh)}})
            i += 1
        anims[tag] = {"frames": out}
    os.makedirs(os.path.dirname(lp(path_stem)), exist_ok=True)
    Image.fromarray(sheet, "RGBA").save(lp(path_stem + "#sheet.png"), optimize=True)
    with open(lp(path_stem + "#anim.fanim"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"anims": anims}, f, separators=(",", ":"))
    return W, H
