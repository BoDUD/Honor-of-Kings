"""Review helpers: contact sheets and animated GIFs on the arena colour."""
import os

from PIL import Image, ImageDraw

import px

ARENA = (92, 98, 86, 255)


def _union_bbox(images):
    bb = None
    for im in images:
        b = im.getbbox()
        if b:
            bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    return bb


def contact(tags, path, scale=3, pad=3):
    """One row per tag, all frames cropped to one shared box so motion is comparable."""
    allf = [im for _, fr in tags for im, _ in fr]
    bb = _union_bbox(allf)
    bb = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    rows = []
    for name, frames in tags:
        cells = []
        for im, ms in frames:
            c = px.zoom(im.crop(bb), scale, ARENA)
            ImageDraw.Draw(c).text((3, 2), f"{ms}", fill=(255, 255, 255, 255))
            cells.append(c)
        label = Image.new("RGBA", (90, cells[0].height), (30, 30, 30, 255))
        ImageDraw.Draw(label).text((6, 6), name, fill=(255, 255, 255, 255))
        rows.append(px.hstack([label] + cells, gap=4))
    px.save_png(px.vstack(rows, gap=4), path)


def gifs(tags, folder, prefix, scale=4, pad=4):
    allf = [im for _, fr in tags for im, _ in fr]
    bb = _union_bbox(allf)
    bb = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    for name, frames in tags:
        seq = [px.zoom(im.crop(bb), scale, ARENA).convert("RGB") for im, _ in frames]
        durs = [ms for _, ms in frames]
        path = os.path.join(folder, f"{prefix}_{name}.gif")
        os.makedirs(px.lp(folder), exist_ok=True)
        seq[0].save(px.lp(path), save_all=True, append_images=seq[1:], duration=durs, loop=0, disposal=2)
