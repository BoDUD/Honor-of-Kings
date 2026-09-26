#!/usr/bin/env python3
"""Inspect, preview and measure Teamfight Manager 2 sprites.

Accepts:
  * Aseprite files (.aseprite / .ase) - TFM2 loads these natively
  * exported sheets: path to <name>#sheet.png (or <name>) with a sibling <name>#anim.fanim
  * base-game sprites by asset path, e.g. asset/base/aseprite_resources/champions/fighter
    (read from bundle.game_data; see bundle_tool.py for --game)

    python tfm2_ase.py info    hero.aseprite
    python tfm2_ase.py render  hero.aseprite --out hero_preview.png --scale 3 [--tag idle]
    python tfm2_ase.py metrics hero.aseprite [--tag idle] [--kind champion|effect]

`metrics` compares the sprite with numbers measured from the 78 base champions and from the
oppi-style benchmark packs (see references/art-spec.md) and prints PASS / WARN lines.
Needs Pillow (pip install pillow).
"""
import argparse
import io
import json
import os
import struct
import sys
import zlib

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ARENA_BG = (92, 98, 86, 255)  # neutral olive-grey, close to the in-game arena floor


# ----------------------------------------------------------------------------- Aseprite
class Sprite:
    """Frames (RGBA PIL images, all the same canvas size), per-frame durations in ms, tags."""

    def __init__(self, w, h, frames, durations, tags, layers=None, source=""):
        self.w, self.h = w, h
        self.frames = frames
        self.durations = durations
        self.tags = tags  # list of dict(name, frm, to)
        self.layers = layers or []
        self.source = source

    def tag(self, name):
        return next((t for t in self.tags if t["name"] == name), None)

    def tag_frames(self, name):
        t = self.tag(name)
        return [] if t is None else list(range(t["frm"], t["to"] + 1))


def read_aseprite(data, source=""):
    (_fsize, magic, nframes, w, h, depth, _flags, _speed, _z1, _z2, tidx) = struct.unpack_from("<IHHHHHIHIIB", data, 0)
    if magic != 0xA5E0:
        raise ValueError("not an Aseprite file")
    palette = [(0, 0, 0, 255)] * 256
    layers, tags, durations, cels_per_frame = [], [], [], []
    pos = 128
    for _ in range(nframes):
        fbytes, fmagic, oldchunks, dur = struct.unpack_from("<IHHH", data, pos)
        if fmagic != 0xF1FA:
            raise ValueError("bad frame header")
        newchunks = struct.unpack_from("<I", data, pos + 12)[0]
        durations.append(dur)
        cp, cels = pos + 16, []
        for _ in range(newchunks or oldchunks):
            csize, ctype = struct.unpack_from("<IH", data, cp)
            body = cp + 6
            if ctype == 0x2004:  # layer
                lflags, ltype, lchild, _, _, blend, opacity = struct.unpack_from("<HHHHHHB", data, body)
                nlen = struct.unpack_from("<H", data, body + 16)[0]
                layers.append(dict(name=data[body + 18: body + 18 + nlen].decode("utf-8", "replace"),
                                   visible=bool(lflags & 1), type=ltype, child=lchild, blend=blend, opacity=opacity))
            elif ctype == 0x2018:  # tags
                ntags = struct.unpack_from("<H", data, body)[0]
                tp = body + 10
                for _ in range(ntags):
                    frm, to = struct.unpack_from("<HH", data, tp)
                    nlen = struct.unpack_from("<H", data, tp + 17)[0]
                    tags.append(dict(name=data[tp + 19: tp + 19 + nlen].decode("utf-8", "replace"), frm=frm, to=to))
                    tp += 19 + nlen
            elif ctype == 0x2019:  # palette
                _psize, first, last = struct.unpack_from("<III", data, body)
                pp = body + 20
                for i in range(first, last + 1):
                    eflags, r, g, b, a = struct.unpack_from("<HBBBB", data, pp)
                    palette[i] = (r, g, b, a)
                    pp += 6
                    if eflags & 1:
                        pp += 2 + struct.unpack_from("<H", data, pp)[0]
            elif ctype in (0x0004, 0x0011) and depth == 8:  # old palette (only matters for indexed)
                npk = struct.unpack_from("<H", data, body)[0]
                pp, idx = body + 2, 0
                for _ in range(npk):
                    skip, n = data[pp], data[pp + 1] or 256
                    pp += 2
                    idx += skip
                    for _ in range(n):
                        r, g, b = data[pp], data[pp + 1], data[pp + 2]
                        if ctype == 0x0011:
                            r, g, b = r * 4, g * 4, b * 4
                        if idx < 256:
                            palette[idx] = (r, g, b, 255)
                        idx += 1
                        pp += 3
            elif ctype == 0x2005:  # cel
                li, x, y, op, ctyp, z = struct.unpack_from("<HhhBHh", data, body)
                cb = body + 16
                if ctyp in (0, 2):
                    cw, ch = struct.unpack_from("<HH", data, cb)
                    raw = data[cb + 4: cp + csize]
                    if ctyp == 2:
                        raw = zlib.decompress(raw)
                    cels.append(dict(layer=li, x=x, y=y, op=op, w=cw, h=ch, raw=raw, z=z))
                elif ctyp == 1:
                    cels.append(dict(layer=li, x=x, y=y, op=op, z=z, link=struct.unpack_from("<H", data, cb)[0]))
                # ctyp 3 = tilemap cel: not supported (TFM2 packs do not use tilemaps)
            cp += csize
        cels_per_frame.append(cels)
        pos += fbytes

    def cel_image(c):
        cw, ch, raw = c["w"], c["h"], c["raw"]
        if depth == 32:
            return Image.frombytes("RGBA", (cw, ch), raw)
        if depth == 16:
            im = Image.new("RGBA", (cw, ch))
            im.putdata([(raw[2 * i], raw[2 * i], raw[2 * i], raw[2 * i + 1]) for i in range(cw * ch)])
            return im
        im = Image.new("RGBA", (cw, ch))
        im.putdata([(0, 0, 0, 0) if raw[i] == tidx else palette[raw[i]] for i in range(cw * ch)])
        return im

    # effective visibility (a layer inside a hidden group is hidden)
    vis, stack = [], []
    for L in layers:
        while len(stack) > L["child"]:
            stack.pop()
        v = L["visible"] and all(stack)
        vis.append(v)
        if L["type"] == 1:
            stack.append(v)

    frames = []
    for fi in range(nframes):
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        resolved = []
        for c in cels_per_frame[fi]:
            if "link" in c:
                src = next((k for k in cels_per_frame[c["link"]] if k["layer"] == c["layer"] and "raw" in k), None)
                if src is None:
                    continue
                c = dict(src, op=c["op"], z=c["z"])
            resolved.append(c)
        resolved.sort(key=lambda c: (c["layer"] + c["z"], c["z"]))
        for c in resolved:
            li = c["layer"]
            if li >= len(layers) or not vis[li] or layers[li]["type"] != 0:
                continue
            im = cel_image(c)
            mult = (c["op"] / 255.0) * (layers[li]["opacity"] / 255.0)
            if mult < 1:
                im.putalpha(im.getchannel("A").point(lambda a: int(a * mult)))
            layer_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            layer_img.paste(im, (c["x"], c["y"]))
            canvas.alpha_composite(layer_img)
        frames.append(canvas)
    return Sprite(w, h, frames, durations, tags, layers, source)


def read_sheet(sheet_png_bytes, fanim, source=""):
    """Exported format: frames are rects in one PNG; each tag is an anim in the .fanim json."""
    sheet = Image.open(io.BytesIO(sheet_png_bytes)).convert("RGBA")
    frames, durations, tags = [], [], []
    rects = [(k, fr) for k, a in fanim["anims"].items() for fr in a["frames"]]
    fw = max(int(round(fr["data"]["w"])) for _, fr in rects)
    fh = max(int(round(fr["data"]["h"])) for _, fr in rects)
    for name, anim in fanim["anims"].items():
        start = len(frames)
        for fr in anim["frames"]:
            d = fr["data"]
            x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
            crop = sheet.crop((x, y, x + w, y + h))
            # frames of different sizes are drawn centred on the same pivot -> centre them
            cell = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
            cell.paste(crop, ((fw - w) // 2, (fh - h) // 2))
            frames.append(cell)
            durations.append(int(round(fr["duration"] * 1000)))
        tags.append(dict(name=name, frm=start, to=len(frames) - 1))
    return Sprite(fw, fh, frames, durations, tags, [], source)


def long_path(p):
    """On Windows, lift the 260-character limit (deep Steam / OneDrive / app-sandbox folders)."""
    p = os.path.abspath(p)
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        p = "\\\\?\\UNC\\" + p[2:] if p.startswith("\\\\") else "\\\\?\\" + p
    return p


def load_sprite(path, game=None):
    sp = _load_sprite(path if path.startswith("asset/") else long_path(path), game)
    sp.source = path
    return sp


def _load_sprite(path, game=None):
    if path.startswith("asset/"):
        from bundle_tool import Bundle, find_game_dir
        gd = find_game_dir(game)
        if not gd:
            sys.exit("bundle.game_data not found; pass --game")
        b = Bundle(gd)
        png, fan = b.read_path(path + "#sheet", "png"), b.read_json(path + "#anim", "fanim")
        if png is None or fan is None:
            sys.exit(f"base sprite not found: {path}")
        return read_sheet(png, fan, path)
    low = path.lower()
    if low.endswith((".aseprite", ".ase")):
        with open(path, "rb") as f:
            return read_aseprite(f.read(), path)
    stem = path
    for suf in ("#sheet.png", "#anim.fanim", ".png", ".fanim"):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
            break
    if os.path.isfile(stem + ".aseprite"):
        with open(stem + ".aseprite", "rb") as f:
            return read_aseprite(f.read(), stem + ".aseprite")
    png, fan = stem + "#sheet.png", stem + "#anim.fanim"
    if not (os.path.isfile(png) and os.path.isfile(fan)):
        sys.exit(f"could not find {stem}.aseprite or {png} + {fan}")
    with open(png, "rb") as f, open(fan, encoding="utf-8-sig") as g:
        return read_sheet(f.read(), json.load(g), png)


# ----------------------------------------------------------------------------- metrics
def _lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def measure(sp, tag="idle"):
    idx = sp.tag_frames(tag) or list(range(min(len(sp.frames), 8)))
    ub = None
    colors, semi = set(), 0
    for i in idx:
        im = sp.frames[i]
        b = im.getbbox()
        if b:
            ub = b if ub is None else (min(ub[0], b[0]), min(ub[1], b[1]), max(ub[2], b[2]), max(ub[3], b[3]))
        pixels = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
        for p in pixels:
            if p[3]:
                colors.add(p)
                if p[3] < 255:
                    semi += 1
    if ub is None:
        return None
    f0 = sp.frames[idx[0]]
    px, W, H = f0.load(), f0.width, f0.height
    edge = dark_edge = opaque = inner_dark = 0
    for y in range(H):
        for x in range(W):
            p = px[x, y]
            if not p[3]:
                continue
            opaque += 1
            is_edge = any(not (0 <= a < W and 0 <= b < H) or px[a, b][3] == 0
                          for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            if is_edge:
                edge += 1
                dark_edge += _lum(p) < 40
            elif _lum(p) < 40:
                inner_dark += 1
    return dict(frames=len(idx), height=ub[3] - ub[1], width=ub[2] - ub[0],
                feet_below_center=ub[3] - sp.h / 2.0, x_off=(ub[0] + ub[2]) / 2.0 - sp.w / 2.0,
                outline=dark_edge / max(edge, 1), inner_dark=inner_dark / max(opaque, 1),
                colors=len(colors), semi_alpha_px=semi)


REQUIRED_TAGS = ("idle", "run")
RECOMMENDED_TAGS = ("attack", "hit", "dead")


def cmd_metrics(sp, tag, kind):
    m = measure(sp, tag)
    if m is None:
        print("empty sprite")
        return 1
    print(f"{sp.source}  canvas {sp.w}x{sp.h}  tag '{tag}' ({m['frames']} frames)")
    print(f"  character height {m['height']} px, width {m['width']} px")
    print(f"  feet {m['feet_below_center']:+.1f} px below canvas centre, x offset {m['x_off']:+.1f}")
    print(f"  outline dark {m['outline']:.0%} | interior near-black {m['inner_dark']:.0%} | "
          f"{m['colors']} colours | {m['semi_alpha_px']} semi-transparent px")
    warn = 0

    def verdict(ok, msg):
        nonlocal warn
        warn += not ok
        print(("  PASS  " if ok else "  WARN  ") + msg)

    if kind == "champion":
        verdict(28 <= m["height"] <= 52,
                "height in 28-52 px (base median 35, IQR 34-37; big units 41-45; oppi 33-39, tanks 44-51)")
        verdict(m["outline"] >= 0.85, "1px near-black outline on >=85% of silhouette edge (base median 100%)")
        verdict(m["semi_alpha_px"] == 0, "no semi-transparent body pixels (base and oppi: 0)")
        verdict(10 <= m["colors"] <= 160,
                "colour count 10-160 per idle set (base median 25, oppi 49-120; >160 smells like downscaled painting)")
        missing = [t for t in REQUIRED_TAGS if not sp.tag(t)]
        verdict(not missing, "has tags " + "/".join(REQUIRED_TAGS) + (f" (missing: {', '.join(missing)})" if missing else ""))
        soft = [t for t in RECOMMENDED_TAGS if not sp.tag(t)]
        if soft:
            print(f"  INFO  no {'/'.join(soft)} tag - fine only if the champion data uses other names "
                  "(every action_name must be a tag; Jinx uses attack_pewpew, Nocturne ships without hit/dead). "
                  "Run lint_mod.py to check against the data.")
        print("  INFO  anchoring: base exported frames keep feet 11.5 px below frame centre; oppi .aseprite "
              "canvases keep feet 17-20 px below canvas centre. Check in-game next to a base champion.")
    else:
        verdict(m["semi_alpha_px"] <= m["colors"] * 50, "mostly opaque effect pixels")
    return 1 if warn else 0


# ----------------------------------------------------------------------------- face / portrait point
FACE_BASE = ("archer", "knight", "priest", "fighter")   # heroes drawn next to yours by `face --out`


def head_of(sp, tag="idle"):
    """On the tag's first frame: (feet row, crown row, head centre x from the canvas centre).
    The crown is the first row at least half as wide as the widest of the top 12 rows, so a hair
    bun, a hat tip or a pointed hood does not count as the head."""
    f = sp.frames[(sp.tag_frames(tag) or [0])[0]].convert("RGBA")
    px, W = f.load(), f.width
    bb = f.getbbox()
    widths = [sum(1 for x in range(W) if px[x, y][3]) for y in range(bb[1], min(bb[1] + 12, bb[3]))]
    crown = bb[1] + next(i for i, w in enumerate(widths) if w >= 0.5 * max(widths))
    xs = [x for y in range(crown, min(crown + 6, bb[3])) for x in range(W) if px[x, y][3]]
    return bb[3], crown, sum(xs) / len(xs) - W / 2.0


def suggest_face(sp):
    """champion_view `face` the way the 68 base champions set it: at the crown (median 0 px below
    it) and ~1.5 px ahead of the head centre."""
    feet, crown, cx = head_of(sp)
    return {"x": int(round(cx + 1.5)), "y": -(feet - crown)}


def face_ok(face, sug):
    """Within the base champions' spread: at most 4 px above the crown, 10 below, 8 aside (62 of
    the 68 pass; the others are a mount, the ogre, the werewolf, two big hats and the strongman).
    A small head fails too: its crown is found at the shoulders, below the head (league_garen
    before the chibi redraw: 6 px above)."""
    above = sug["y"] - face.get("y", 0)
    return -10 <= above <= 4 and abs(face.get("x", 0) - sug["x"]) <= 8


def face_sheet(sp, face, out, game=None, z=4, hz=10):
    """Your hero next to base champions: idle at 1x and z x with each face point (red cross), and
    their heads at hz x - look for a head about a third of the height and eyes you can see at 1x."""
    rows = [(sp, face)]
    try:
        import bundle_tool
        views = bundle_tool.Bundle(bundle_tool.find_game_dir(game)).read_json(
            "asset/base/style/champion_view", "champion_view")["entries"]
        rows += [(load_sprite(f"asset/base/aseprite_resources/champions/{n}", game), views[n]["face"])
                 for n in FACE_BASE]
    except Exception as e:  # noqa: BLE001 - the comparison is optional
        print(f"  (no base heroes to compare: {e})")
    H, HH = 48, 16                   # rows above the feet shown; rows of the head strip
    cells = []                       # (1x crop, face point in crop px, crown row in crop)
    for s, fc in rows:
        f = s.frames[(s.tag_frames("idle") or [0])[0]].convert("RGBA")
        x0, _, x1, feet = f.getbbox()
        x0, x1 = x0 - 2, x1 + 2
        cell = Image.new("RGBA", (x1 - x0, H), ARENA_BG)
        cell.alpha_composite(f.crop((x0, feet - H + 1, x1, feet + 1)))
        _, crown, _ = head_of(s)
        pt = (f.width / 2.0 + fc["x"] - x0, H - 1 + fc["y"]) if fc else None
        cells.append((cell, pt, crown - (feet - H + 1)))
    gap = 3
    W1 = sum(c.width + gap for c, *_ in cells)
    img = Image.new("RGBA", (max(W1 * z, W1 * hz // 2), H + 4 + H * z + 4 + HH * hz // 2), (28, 28, 28, 255))
    d = ImageDraw.Draw(img)
    x = 0
    for cell, pt, crown in cells:
        img.alpha_composite(cell, (x, 0))                                           # 1x
        img.alpha_composite(cell.resize((cell.width * z, H * z), Image.NEAREST), (x * z, H + 4))
        if pt:
            cx, cy = x * z + (pt[0] + 0.5) * z, H + 4 + (pt[1] + 0.5) * z
            d.line((cx - 2 * z, cy, cx + 2 * z, cy), fill=(255, 40, 40, 255), width=2)
            d.line((cx, cy - 2 * z, cx, cy + 2 * z), fill=(255, 40, 40, 255), width=2)
        top = max(0, crown - 2)                                                     # head, hz/2 x
        head = cell.crop((0, top, cell.width, min(H, top + HH)))
        img.alpha_composite(head.resize((head.width * hz // 2, head.height * hz // 2), Image.NEAREST),
                            (x * hz // 2, H + 8 + H * z))
        x += cell.width + gap
    img.save(long_path(out))


def cmd_face(sp, face=None, out=None, game=None):
    feet, crown, cx = head_of(sp)
    sug = suggest_face(sp)
    print(f"{sp.source}: crown {feet - crown} px above the feet, head centre x {cx:+.1f}")
    print(f"  suggested champion_view face: {{\"x\": {sug['x']}, \"y\": {sug['y']}}}  "
          f"(base heroes: at the crown, ~1.5 px ahead of the head centre)")
    bad = 0
    if face:
        ok = face_ok(face, sug)
        bad += not ok
        print(("  PASS  " if ok else "  WARN  ") + f"face {face} is {sug['y'] - face['y']:+d} px above / "
              f"{face['x'] - sug['x']:+d} px right of the suggestion (base: at most 4 above, 10 below, 8 aside; "
              f"portraits crop around it - above the head they show hair and empty space)")
    if out:
        face_sheet(sp, face or sug, out, game)
        print(f"  wrote {out}: look at the 1x row - is the head about a third of the height and are the eyes visible?")
    return 1 if bad else 0


# ----------------------------------------------------------------------------- render
def render(sp, out, scale=3, only_tag=None, maxcols=10):
    tags = [t for t in sp.tags if not only_tag or t["name"] == only_tag] or \
        [dict(name="(all)", frm=0, to=len(sp.frames) - 1)]
    rows = []
    for t in tags:
        fr = list(range(t["frm"], t["to"] + 1))
        for i in range(0, len(fr), maxcols):
            rows.append((t, fr[i:i + maxcols], i == 0))
    label_w, cw, ch = 120, sp.w * scale, sp.h * scale
    img = Image.new("RGBA", (label_w + maxcols * (cw + 2), len(rows) * (ch + 4)), (28, 28, 28, 255))
    d = ImageDraw.Draw(img)
    for r, (t, frs, first) in enumerate(rows):
        y = r * (ch + 4)
        if first:
            d.text((4, y + 4), t["name"], fill=(255, 255, 255, 255))
            d.text((4, y + 18), f"{t['to'] - t['frm'] + 1}f {sp.durations[t['frm']]}ms", fill=(190, 190, 190, 255))
        for c, fi in enumerate(frs):
            cell = Image.new("RGBA", (sp.w, sp.h), ARENA_BG)
            cell.alpha_composite(sp.frames[fi])
            img.paste(cell.resize((cw, ch), Image.NEAREST), (label_w + c * (cw + 2), y))
    img.save(long_path(out))
    return img.size


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", help="Teamfight Manager2 folder (for asset/base/... paths)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info")
    p.add_argument("sprite")
    p = sub.add_parser("render")
    p.add_argument("sprite")
    p.add_argument("--out", required=True)
    p.add_argument("--scale", type=int, default=3)
    p.add_argument("--tag")
    p = sub.add_parser("metrics")
    p.add_argument("sprite")
    p.add_argument("--tag", default="idle")
    p.add_argument("--kind", choices=("champion", "effect"), default="champion")
    p = sub.add_parser("face", help="suggest/check the champion_view face point; --out draws the hero next to "
                                    "base champions (head size, eyes at 1x, portrait points)")
    p.add_argument("sprite")
    p.add_argument("--view", help="your champion_view file, to check the face point already set")
    p.add_argument("--id", help="champion id in --view (default: the sprite's file name)")
    p.add_argument("--out", help="write the comparison PNG here")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    sp = load_sprite(args.sprite, args.game)
    if args.cmd == "info":
        print(f"{sp.source}: canvas {sp.w}x{sp.h}, {len(sp.frames)} frames")
        if sp.layers:
            print("layers: " + ", ".join(f"{L['name']}{'' if L['visible'] else ' (hidden)'}" for L in sp.layers))
        for t in sp.tags:
            ms = sorted(set(sp.durations[t["frm"]: t["to"] + 1]))
            print(f"  {t['name']:24s} frames {t['frm']:3d}-{t['to']:3d} ({t['to'] - t['frm'] + 1:2d})  ms {ms}")
    elif args.cmd == "render":
        print("wrote", args.out, render(sp, args.out, args.scale, args.tag))
    elif args.cmd == "metrics":
        sys.exit(cmd_metrics(sp, args.tag, args.kind))
    elif args.cmd == "face":
        face = None
        if args.view:
            with open(long_path(args.view), encoding="utf-8-sig") as fh:
                entries = json.load(fh).get("entries", {})
            cid = args.id or os.path.basename(args.sprite.replace("#sheet.png", "").rstrip("/\\"))
            face = (entries.get(cid) or {}).get("face")
            if face is None:
                print(f"  no face for '{cid}' in {args.view}")
        sys.exit(cmd_face(sp, face, args.out, args.game))


if __name__ == "__main__":
    main()
