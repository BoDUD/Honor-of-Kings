#!/usr/bin/env python3
"""Game-size pose references straight from League's animations (a native-size redraw in one round).

    python tools/lol/native_pose.py assets/source/leesin/poses.json --out DIR

The native-size redraw (assets/source/NATIVE_REDRAW.md) needed a first GPT round only to turn
League's poses into game frames. This renders the clips at game size instead: the chibi model
(pose_ref.py's --head / --legs / --hair) seen through one camera, scaled so the spec's `design`
pose is `height` px from the crown to the soles (hair chains hanging from the head not counted),
every game pixel the mean colour of one 8x8 block of an --hq render (a block at least half covered
is opaque). Per tag of the spec it writes
  <hero>_native_<tag>.png  the frames at game size, shown at 8x, in native_refs.py's grid of 56x64
                           cells read left to right, top to bottom (feet line 10 px above the bottom)
  <hero>_pose_<tag>.png    the same frames as the 8x render itself: same grid, same place
and <hero>_native_design.png (the design pose on a 128x128 canvas at 8x, feet line 28 px above the
bottom, like native_refs.py's <hero>_now_design.png), <hero>_pose_design.png (the same at 8x
render), and <hero>_cells.json: each frame's pivot in its cell and its duration, the table
tools/art/import_native.py cuts the redrawn frames out with, plus where League's head joint is in
the cell (tools/art/fit_native.py puts a redrawn frame's head there).

Placement: the unit stands at the world origin. Every frame keeps League's height (jumps,
landings, the death fall) and one vertical offset puts the design pose's soles on the feet line.
Sideways, an action keeps `lunge` of League's travel around the design pose's head (the importers
kept 65-70%: League blends back to idle, a sprite snaps back), then each frame is centred across
its cell by its content and its pivot recorded. Per tag, "anchor": "first" measures that travel
from the tag's first frame instead and puts that frame's head where the design pose has it (Lee
Sin's death starts 140 units in front of the unit), and "flat": true puts every frame's lowest
point as high above the feet line as it is above League's floor: knocked back away from the camera,
a body lying diagonally in depth otherwise floats or sinks (the pitch turns depth into height),
while a sprite has one ground line.

Spec (JSON): {"hero", "champ", "camera": {"yaw", "pitch", "mirror"}, "chibi": {"head", "legs",
"hair"}, "height", "cell": [w, h] (optional, default 56x64), "design": "<clip@ms>", "tags": {"<tag>": {"lunge": 1.0, "anchor": "design",
"flat": false, "frames": [["<clip@ms or clipA@ms>clipB@ms:w>", <ms>, {"turn": <deg>}], ...]}}}
(the third item is optional). The renders show
Riot's model: keep them local, never commit them (the spec and the cells table are fine).
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
import pose_ref as P  # noqa: E402
from native_refs import CELL, FEET_ROW, Z, layout  # noqa: E402
from riot import Wad  # noqa: E402

BG = (225, 225, 225)
PIVOT_ROW = FEET_ROW - 12            # base sprites: pivot 11.5 px above the soles


def set_cell(w, h):
    """A bigger cell than native_refs.py's 56x64 (Lee Sin's braid and flying kick need 64x72);
    the feet line stays 10 px above the bottom."""
    global CELL, FEET_ROW, PIVOT_ROW
    CELL, FEET_ROW = (w, h), h - 10
    PIVOT_ROW = FEET_ROW - 12


class Champ:
    """A champion's base skin: mesh, skeleton, texture and clips, read from the local client."""

    def __init__(self, lol, champ):
        w = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", f"{champ}.wad.client"))
        skin_bin = w.read_path(f"data/characters/{champ.lower()}/skins/skin0.bin")
        refs = lambda blob, ext: sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\." + ext, blob)))
        skn = [p for p in refs(skin_bin, rb"skn") if "/Base/" in p][0]
        skl = [p for p in refs(skin_bin, rb"skl") if "/Base/" in p][0]
        texs = [p for p in refs(skin_bin, rb"(?:tex|dds)") if "/Base/" in p and re.search(r"_tx_cm|_cm_tx", p, re.I)]
        self.tris, self.verts = P.read_skn(w.read_path(skn.lower()))
        self.joints, self.influences = P.read_skl(w.read_path(skl.lower()))
        self.tex = P.read_tex(w.read_path(texs[0].lower()))
        bind = P.globals_(self.joints, [P.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]
        anims = refs(w.read_path(f"data/characters/{champ.lower()}/animations/skin0.bin"), rb"anm")
        self.by_name = {os.path.splitext(os.path.basename(a))[0].lower(): a for a in anims}
        self.wad, self.loaded = w, {}
        self.legv = P.leg_vertices(self.joints, self.influences, self.verts)
        head = P.chain_vertices(self.joints, self.influences, self.verts, re.compile(r"^head$", re.I))
        hair = P.chain_vertices(self.joints, self.influences, self.verts, P.HAIR)
        self.headv = head & ~hair
        self.head = next(i for i, j in enumerate(self.joints) if j["name"].lower() == "head")

    def clip(self, name):
        if name.lower() not in self.by_name:
            raise SystemExit(f"no clip {name!r}; clips: {', '.join(sorted(self.by_name))}")
        if name.lower() not in self.loaded:
            self.loaded[name.lower()] = P.read_anim(self.wad.read_path(self.by_name[name.lower()].lower()))
        return self.loaded[name.lower()]

    def local(self, spec):
        a, ta, b, tb, wgt = P.parse_frame(spec)
        local = P.local_pose(self.joints, self.clip(a), ta)
        return P.blend_pose(local, P.local_pose(self.joints, self.clip(b), tb), wgt) if b else local

    def posed(self, spec, chibi, turn=0.0):
        """World vertices of the chibi model in a pose, feet where League has them, and the chibi
        skeleton's global matrices; `turn` degrees about the vertical axis through the unit (a
        spin or a bent-over slam turned toward the camera so the chest shows, as animators cheat)."""
        local = self.local(spec)
        glob = P.globals_(self.joints, [P.trs(*p) for p in P.chibi(self.joints, local, **chibi)])
        pv = P.skin(self.verts, self.influences, self.bind_inv, glob)
        adult = P.skin(self.verts, self.influences, self.bind_inv, P.globals_(self.joints, [P.trs(*p) for p in local]))
        lift = adult[self.legv, 1].min() - pv[self.legv, 1].min()
        pv[:, 1] += lift
        if turn:
            c, s = np.cos(np.radians(turn)), np.sin(np.radians(turn))
            r = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            pv = pv @ r.T
            glob = [np.vstack([np.c_[r @ g[:3, :3], r @ g[:3, 3]], g[3]]) for g in glob]
        return pv, glob, lift


def camera(cam):
    yaw = -cam["yaw"] if cam.get("mirror") else cam["yaw"]
    cy, sy = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(cam["pitch"])), np.sin(np.radians(cam["pitch"]))
    return np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])


def render(ch, pv, cam, scale, dy):
    """8x render two cells wide (RGBA float), the unit's origin at the centre of game column
    CELL[0] and dy px (8x) below the feet line; frames are cut out of it by their content."""
    W, H = 2 * CELL[0] * Z, CELL[1] * Z
    x0 = (CELL[0] + 0.5) * Z
    shift = x0 / W - 0.5
    yaw = cam["yaw"]
    if cam.get("mirror"):
        img = P.render_hq(pv, ch.tris, ch.verts["uv"], ch.tex, -yaw, cam["pitch"], (W, H), scale,
                          FEET_ROW * Z + dy, -shift).transpose(Image.FLIP_LEFT_RIGHT)
    else:
        img = P.render_hq(pv, ch.tris, ch.verts["uv"], ch.tex, yaw, cam["pitch"], (W, H), scale, FEET_ROW * Z + dy, shift)
    return np.asarray(img).astype(np.float32)


def blocks(img):
    """8x render -> game pixels: mean colour of the covered part of each 8x8 block, opaque when
    at least half covered."""
    h, w = img.shape[0] // Z, img.shape[1] // Z
    b = img.reshape(h, Z, w, Z, 4)
    a = (b[..., 3] >= 128).astype(np.float32)
    cov = a.mean((1, 3))
    col = (b[..., :3] * a[..., None]).sum((1, 3)) / np.maximum(a.sum((1, 3))[..., None], 1)
    out = np.zeros((h, w, 4), np.uint8)
    on = cov >= 0.5
    out[on, :3] = np.clip(np.round(col[on]), 0, 255)
    out[on, 3] = 255
    return out


def on_bg(a):
    img = Image.new("RGBA", (a.shape[1], a.shape[0]), BG + (255,))
    img.alpha_composite(Image.fromarray(a, "RGBA"))
    return img.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder")
    ap.add_argument("--tag", action="append", help="only these tags (default: all, plus the design canvas)")
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    hero, cam, chibi = spec["hero"], spec["camera"], spec["chibi"]
    set_cell(*spec.get("cell", CELL))
    ch = Champ(args.lol, spec["champ"])
    rot = camera(cam)
    sign = -1.0 if cam.get("mirror") else 1.0
    os.makedirs(args.out, exist_ok=True)

    # scale: the design pose is `height` game px from the crown to the soles, seen through the camera
    pv, glob, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())       # game px per world unit
    scale = unit * Z

    def head_x(g):
        return sign * (rot @ g[ch.head][:3, 3])[0] * unit

    ref_head = head_x(glob)
    # one vertical offset for every frame: the design pose's soles on the feet line
    probe = blocks(render(ch, pv, cam, scale, 0.0))
    dy = (FEET_ROW - 1 - np.nonzero(probe[..., 3].any(1))[0].max()) * Z
    design = blocks(render(ch, pv, cam, scale, dy))
    rows = np.nonzero(design[..., 3].any(1))[0]
    print(f"{hero}: {unit * 100:.3f} game px per 100 units; design pose {rows.max() - rows.min() + 1} px tall with "
          f"what hangs from the head, feet on row {rows.max()}, offset {dy / Z:+.0f} px")

    def cell(frame_spec, lunge, base, flat, turn=0.0):
        pv, glob, _ = ch.posed(frame_spec, chibi, turn)
        hi = render(ch, pv, cam, scale, dy)
        lo = blocks(hi)
        down = 0
        if flat:   # lowest point as high above the feet line as it is above League's floor
            lift = int(round(max(0.0, pv[:, 1].min()) * unit * np.cos(np.radians(cam["pitch"]))))
            down = (FEET_ROW - 1 - lift) - np.nonzero(lo[..., 3].any(1))[0].max()
            if down:
                hi = render(ch, pv, cam, scale, dy + down * Z)
                lo = blocks(hi)
        hx = head_x(glob)
        head_y = FEET_ROW + dy / Z + down - (rot @ glob[ch.head][:3, 3])[1] * unit
        pivot = CELL[0] + int(round((1.0 - lunge) * (hx - base) + (base - ref_head)))
        ys, xs = np.nonzero(lo[..., 3])
        if len(xs) == 0:
            raise SystemExit(f"{frame_spec}: nothing in the cell")
        clipped = []
        if ys.min() == 0:
            clipped.append("top")
        if xs.max() - xs.min() + 1 > CELL[0] or xs.min() == 0 or xs.max() == lo.shape[1] - 1:
            clipped.append("sides")
        x0 = xs.min() - (CELL[0] - (xs.max() - xs.min() + 1)) // 2          # the cell's left edge
        x0 = min(max(x0, 0), lo.shape[1] - CELL[0])
        lo = lo[:, x0:x0 + CELL[0]]
        hi = np.clip(hi, 0, 255).astype(np.uint8)[:, x0 * Z:(x0 + CELL[0]) * Z]
        return lo, hi, (pivot - x0, PIVOT_ROW), hx - ref_head, clipped, (CELL[0] + 0.5 + hx - x0, head_y)

    table = {}
    tags = args.tag or list(spec["tags"])
    for tag in tags:
        t = spec["tags"][tag]
        base = ref_head
        if t.get("anchor", "design") == "first":
            base = head_x(ch.posed(t["frames"][0][0], chibi)[1])
        frames = [cell(f[0], t.get("lunge", 1.0), base, t.get("flat", False), (f[2] if len(f) > 2 else {}).get("turn", 0.0))
                  for f in t["frames"]]
        cols, nrows = layout(len(frames))
        lo_img = Image.new("RGB", (cols * CELL[0], nrows * CELL[1]), BG)
        hi_img = Image.new("RGB", (cols * CELL[0] * Z, nrows * CELL[1] * Z), BG)
        for k, (lo, hi, *_) in enumerate(frames):
            cx, cy = k % cols, k // cols
            lo_img.paste(on_bg(lo), (cx * CELL[0], cy * CELL[1]))
            hi_img.paste(on_bg(hi), (cx * CELL[0] * Z, cy * CELL[1] * Z))
        lo_img.resize((lo_img.width * Z, lo_img.height * Z), Image.NEAREST).save(
            os.path.join(args.out, f"{hero}_native_{tag}.png"))
        hi_img.save(os.path.join(args.out, f"{hero}_pose_{tag}.png"))
        table[tag] = [{"pivot": list(map(int, p)), "ms": int(ms), "head": [round(float(h[0]), 1), round(float(h[1]), 1)]}
                      for (_, _, p, _, _, h), (_, ms, *_) in zip(frames, t["frames"])]
        colours = len(np.unique(np.concatenate([lo[lo[..., 3] > 0][:, :3] for lo, *_ in frames]), axis=0))
        print(f"{hero}_native_{tag}.png  {len(frames)} frames, {cols}x{nrows} cells, {colours} colours; head x from the "
              f"design pose " + " ".join(f"{fr[3]:+.1f}" for fr in frames) +
              "".join(f"\n  frame {k + 1} touches the cell's {' and '.join(fr[4])}" for k, fr in enumerate(frames) if fr[4]))

    if not args.tag:
        canvas = np.zeros((128, 128, 4), np.uint8)
        ys, xs = np.nonzero(design[..., 3])
        crop = design[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        top, left = 100 - crop.shape[0], (128 - crop.shape[1]) // 2
        canvas[top:100, left:left + crop.shape[1]] = crop
        on_bg(canvas).resize((128 * Z, 128 * Z), Image.NEAREST).save(os.path.join(args.out, f"{hero}_native_design.png"))
        hi = np.clip(render(ch, pv, cam, scale, dy), 0, 255).astype(np.uint8)
        big = np.zeros((128 * Z, 128 * Z, 4), np.uint8)
        y0, x0 = (top - ys.min()) * Z, (left - xs.min()) * Z
        sy0, sx0 = max(0, -y0), max(0, -x0)
        h = min(hi.shape[0] - sy0, big.shape[0] - max(0, y0))
        w = min(hi.shape[1] - sx0, big.shape[1] - max(0, x0))
        big[max(0, y0):max(0, y0) + h, max(0, x0):max(0, x0) + w] = hi[sy0:sy0 + h, sx0:sx0 + w]
        on_bg(big).save(os.path.join(args.out, f"{hero}_pose_design.png"))
        lines = [f'  "{tag}": [' + ", ".join(f'{{"pivot": [{r["pivot"][0]}, {r["pivot"][1]}], "ms": {r["ms"]}, '
                                             f'"head": [{r["head"][0]}, {r["head"][1]}]}}'
                                             for r in rows_) + "]" for tag, rows_ in table.items()]
        text = f'{{"cell": [{CELL[0]}, {CELL[1]}], "scale": {Z}, "tags": {{\n' + ",\n".join(lines) + "\n}}\n"
        json.loads(text)
        with open(os.path.join(args.out, f"{hero}_cells.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"{hero}_native_design.png, {hero}_pose_design.png, {hero}_cells.json")


if __name__ == "__main__":
    main()
