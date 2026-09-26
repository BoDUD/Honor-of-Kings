#!/usr/bin/env python3
"""Render a champion's real in-game animation from the local League client as pose references.

    python tools/lol/pose_ref.py --lol "D:\\WeGameApps\\lol" --champ Garen --anim Run --frames 6 --out ref/

For each animation whose file name contains --anim, writes <out>/<anim>.png: N frames spread over
the clip (or --t0..--t1 seconds; attack clips hold a long recovery after the swing), the textured
model seen from a 3/4 view facing right (like TFM2 sprites), with the frame times. Use them to judge a sprite's motion, or attach them to image-model
prompts as the pose to copy. The renders show Riot's model: keep them local, never commit them.

An exact strip instead, with League-style cross-fades into and out of a clip (so a sprite action can
start and end near the idle pose), and per-pixel texturing that shows the face and trim:

    python tools/lol/pose_ref.py --champ Ashe --hq --name ashe_pose_attack --out ref/ \\
        --frame "ashe_idle1@0>ashe_attack1@0:0.5" --frame ashe_attack1@0 --frame ashe_attack1@367

A frame is <clip>@<ms> or <clipA>@<ms>><clipB>@<ms>:<weight of B>; <clip> is the .anm file name
without extension (case-insensitive).

Reads (read-only) Champions/<Champ>.wad.client: the skin bin (-> .skn/.skl/texture), the
animation bin (-> .anm list). Formats handled: SKN 1.x-4.x, SKL (0x22FD4FC3), compressed ANM
("r3d2canm" v1-3) and legacy "r3d2anmd" v5, TEX (DXT1/DXT5/BGRA8). Needs numpy + Pillow.
"""
import argparse
import io
import os
import re
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riot import Wad  # noqa: E402


def elf(name):
    h = 0
    for c in name.lower().encode():
        h = ((h << 4) + c) & 0xFFFFFFFF
        g = h & 0xF0000000
        if g:
            h ^= g >> 24
        h &= ~g & 0xFFFFFFFF
    return h


# ----------------------------------------------------------------------------- formats
def read_skn(b):
    magic, major, minor = struct.unpack_from("<IHH", b, 0)
    if magic != 0x00112233:
        raise ValueError("not a SKN")
    pos = 8
    if major > 0:
        (nsub,) = struct.unpack_from("<I", b, pos)
        pos += 4 + nsub * 80
    if major == 4:
        pos += 4                                    # flags
    ic, vc = struct.unpack_from("<II", b, pos)
    pos += 8
    vsize = 52
    if major == 4:
        vsize, _vtype = struct.unpack_from("<II", b, pos)
        pos += 8 + 24 + 16                          # vertex size/type, bbox, bounding sphere
    idx = np.frombuffer(b, "<u2", ic, pos).astype(np.int64)
    pos += 2 * ic
    dt = np.dtype([("pos", "<f4", 3), ("bones", "u1", 4), ("w", "<f4", 4), ("n", "<f4", 3), ("uv", "<f4", 2)])
    raw = np.frombuffer(b, np.uint8, vc * vsize, pos).reshape(vc, vsize)[:, :52].copy()
    v = raw.view(dt).reshape(vc)
    return idx.reshape(-1, 3), v


def read_skl(b):
    _size, token, _ver = struct.unpack_from("<III", b, 0)
    if token != 0x22FD4FC3:
        raise ValueError("only the new SKL format is supported")
    _flags, njoints, ninf = struct.unpack_from("<HHI", b, 12)
    joints_off, _ji_off, inf_off = struct.unpack_from("<iii", b, 20)
    joints = []
    for j in range(njoints):
        p = joints_off + 100 * j
        _f, jid, parent, _pad, nhash, _radius = struct.unpack_from("<hhhhIf", b, p)
        vals = struct.unpack_from("<3f3f4f3f3f4f", b, p + 16)
        (noff,) = struct.unpack_from("<i", b, p + 96)
        s = p + 96 + noff
        name = b[s:b.index(b"\0", s)].decode("latin1")
        joints.append(dict(id=jid, parent=parent, hash=nhash, name=name,
                           t=np.array(vals[0:3]), s=np.array(vals[3:6]), r=np.array(vals[6:10])))
    influences = struct.unpack_from(f"<{ninf}h", b, inf_off)
    return joints, list(influences)


def quat48(a, c, d):
    """Riot's 48-bit quantized quaternion: 2-bit index of the dropped largest component + 3x15 bits."""
    bits = a | (c << 16) | (d << 32)
    mx = (bits >> 45) & 3
    comps = [((bits >> sh) & 0x7FFF) / 32767.0 * 1.41421356237 - 0.70710678118 for sh in (30, 15, 0)]
    comps.insert(mx, np.sqrt(max(0.0, 1.0 - sum(x * x for x in comps))))
    return np.array(comps)                                            # x, y, z, w


def read_anmd_v5(b):
    """Legacy uncompressed "r3d2anmd" v5: per frame and track, palette indices."""
    (_res, _tok, _ver, _flags, ntracks, nframes, dt, hashes_off, _asset, _time, vec_off, quat_off,
     frames_off) = struct.unpack_from("<IIIIiifiiiiii", b, 12)
    hashes = struct.unpack_from(f"<{ntracks}I", b, hashes_off + 12)
    vecs = np.frombuffer(b, "<f4", (quat_off - vec_off) // 4, vec_off + 12).reshape(-1, 3)
    quats = np.frombuffer(b, "<u2", (hashes_off - quat_off) // 2, quat_off + 12).reshape(-1, 3)
    idx = np.frombuffer(b, "<u2", nframes * ntracks * 3, frames_off + 12).reshape(nframes, ntracks, 3)
    keys = {}
    for f in range(nframes):
        for tr in range(ntracks):
            ti, si, ri = idx[f, tr]
            keys.setdefault((tr, 1), []).append((f * dt, vecs[ti].astype(float)))
            keys.setdefault((tr, 2), []).append((f * dt, vecs[si].astype(float)))
            keys.setdefault((tr, 0), []).append((f * dt, quat48(*(int(x) for x in quats[ri]))))
    return dict(duration=(nframes - 1) * dt, fps=1.0 / dt, hashes=hashes, keys=keys)


def read_anim(b):
    if b[:8] == b"r3d2canm":
        return read_canm(b)
    if b[:8] == b"r3d2anmd" and struct.unpack_from("<I", b, 8)[0] == 5:
        return read_anmd_v5(b)
    raise ValueError(f"unsupported animation {b[:8]!r} v{struct.unpack_from('<I', b, 8)[0]}")


def read_canm(b):
    if b[:8] != b"r3d2canm":
        raise ValueError(f"unsupported animation {b[:8]!r} (only compressed r3d2canm)")
    (_ver, _res, _tok, _flags, njoints, nframes, _njump, duration, fps) = struct.unpack_from("<IIIIiiiff", b, 8)
    tmin = np.array(struct.unpack_from("<3f", b, 68))
    tmax = np.array(struct.unpack_from("<3f", b, 80))
    smin = np.array(struct.unpack_from("<3f", b, 92))
    smax = np.array(struct.unpack_from("<3f", b, 104))
    frames_off, _jump_off, hashes_off = struct.unpack_from("<iii", b, 116)
    hashes = struct.unpack_from(f"<{njoints}I", b, hashes_off + 12)
    fr = np.frombuffer(b, "<u2", nframes * 5, frames_off + 12).reshape(nframes, 5)
    keys = {}                                   # (joint, kind) -> list of (time, value)
    for t, jid, a, c, d in fr.tolist():
        joint, kind = jid & 0x3FFF, jid >> 14
        tt = t / 65535.0 * duration
        if kind == 0:
            val = quat48(a, c, d)
        elif kind == 1:
            val = tmin + (tmax - tmin) * np.array([a, c, d]) / 65535.0
        else:
            val = smin + (smax - smin) * np.array([a, c, d]) / 65535.0
        keys.setdefault((joint, kind), []).append((tt, val))
    for k in keys:
        keys[k].sort(key=lambda kv: kv[0])
    return dict(duration=duration, fps=fps, hashes=hashes, keys=keys)


def read_tex(b):
    if b[:4] != b"TEX\0":
        return Image.open(io.BytesIO(b)).convert("RGBA")          # plain DDS
    w, h, _one, fmt, _rt, _flags = struct.unpack_from("<HHBBBB", b, 4)
    if fmt == 20:                                                   # BGRA8
        data = b[-w * h * 4:]
        return Image.frombytes("RGBA", (w, h), data, "raw", "BGRA")
    block = 8 if fmt == 10 else 16
    size = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * block
    four = b"DXT1" if fmt == 10 else b"DXT5"
    # DDS header: size, flags, height, width, linear size, depth, mips, reserved[11],
    # pixel format (size, FOURCC flag, fourcc, bit count, 4 masks), caps[4], reserved
    hdr = struct.pack("<4sIIIIIII44sII4sIIIIIIIIII", b"DDS ", 124, 0x81007, h, w, size, 0, 1, b"\0" * 44,
                      32, 4, four, 0, 0, 0, 0, 0, 0x1000, 0, 0, 0, 0)
    return Image.open(io.BytesIO(hdr + b[-size:])).convert("RGBA")


# ----------------------------------------------------------------------------- pose
def qmat(q):
    x, y, z, w = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def trs(t, r, s):
    m = np.eye(4)
    m[:3, :3] = qmat(r) * s[None, :]
    m[:3, 3] = t
    return m


def sample(keys, t):
    if len(keys) == 1 or t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            if len(v0) == 4:                                        # nlerp on the short arc
                v1 = v1 if np.dot(v0, v1) >= 0 else -v1
                q = v0 * (1 - u) + v1 * u
                return q / np.linalg.norm(q)
            return v0 * (1 - u) + v1 * u
    return keys[-1][1]


def globals_(joints, local):
    g = [None] * len(joints)
    for i, j in enumerate(joints):                   # parents come first in SKL order
        g[i] = local[i] if j["parent"] < 0 else g[j["parent"]] @ local[i]
    return g


def local_pose(joints, anim, t):
    """(translation, rotation, scale) of every joint relative to its parent at clip time t."""
    by_hash = {h: k for k, h in enumerate(anim["hashes"])}
    local = []
    for j in joints:
        tr, rot, sc = j["t"], j["r"], j["s"]
        k = by_hash.get(j["hash"], by_hash.get(elf(j["name"])))
        if k is not None:
            kk = anim["keys"]
            tr = sample(kk[(k, 1)], t) if (k, 1) in kk else tr
            rot = sample(kk[(k, 0)], t) if (k, 0) in kk else rot
            sc = sample(kk[(k, 2)], t) if (k, 2) in kk else sc
        local.append((np.asarray(tr, float), np.asarray(rot, float), np.asarray(sc, float)))
    return local


def blend_pose(a, b, w):
    """Cross-fade two local poses the way League blends clips: lerp translation and scale, nlerp rotation."""
    out = []
    for (ta, ra, sa), (tb, rb, sb) in zip(a, b):
        rb = rb if np.dot(ra, rb) >= 0 else -rb
        q = ra * (1 - w) + rb * w
        out.append((ta * (1 - w) + tb * w, q / np.linalg.norm(q), sa * (1 - w) + sb * w))
    return out


LEG = re.compile(r"(^|_)(hip|thigh)$", re.I)
LOWER = re.compile(r"hip|thigh|cape|skirt|cloth", re.I)     # legs and what hangs down to them


def chibi(joints, local, head=1.0, legs=1.0):
    """TFM2 proportions from League's adult ones: scale the head joint, and the root of every leg,
    cape, skirt and cloth chain (meshes and child bones scale with it), so the reference already shows
    the big head and short legs of the sprite to draw instead of pulling the image model back to
    realistic proportions."""
    if head == 1.0 and legs == 1.0:
        return local
    out = []
    for j, (t, r, s) in zip(joints, local):
        parent = joints[j["parent"]]["name"] if j["parent"] >= 0 else ""
        k = head if j["name"].lower() == "head" else \
            legs if LOWER.search(j["name"]) and not LOWER.search(parent) else 1.0
        out.append((t, r, np.asarray(s, float) * k))
    return out


def leg_vertices(joints, influences, v):
    """Vertices that mostly follow a leg (a hip/thigh joint or anything below it)."""
    leg = set()
    for i in range(len(joints)):
        k = i
        while k >= 0 and not LEG.search(joints[k]["name"]):
            k = joints[k]["parent"]
        if k >= 0:
            leg.add(i)
    joint_of = np.array(influences)[v["bones"].astype(np.int64)]
    main = joint_of[np.arange(len(v)), np.argmax(v["w"], axis=1)]
    return np.isin(main, sorted(leg))


def pose(joints, anim, t):
    return globals_(joints, [trs(*p) for p in local_pose(joints, anim, t)])


def skin(v, influences, bind_inv, glob):
    mats = np.stack([glob[j] @ bind_inv[j] for j in range(len(glob))])      # joint skin matrices
    joint_of = np.array(influences)[v["bones"].astype(np.int64)]             # (n, 4)
    p = np.c_[v["pos"], np.ones(len(v))]
    out = np.zeros((len(v), 3))
    for k in range(4):
        m = mats[joint_of[:, k]]
        out += v["w"][:, k:k + 1] * np.einsum("nij,nj->ni", m, p)[:, :3]
    return out


# ----------------------------------------------------------------------------- render
def render(verts, tris, uv, tex, yaw, pitch, size, scale, ground, shift=0.0):
    cy, sy = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    v = verts @ (rx @ ry).T
    ss = 3                                                   # supersampling
    W, H = size[0] * ss, size[1] * ss
    x = (v[:, 0] * scale + size[0] * (0.5 + shift)) * ss
    y = (ground - v[:, 1] * scale) * ss
    z = v[:, 2]
    tv = v[tris]
    n = np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    light = np.array([-0.4, 0.6, 0.7])
    light /= np.linalg.norm(light)
    shade = 0.75 + 0.75 * np.abs(n @ light)            # diffuse maps are dark without the game's lighting
    tw, th = tex.size
    texa = np.asarray(tex.convert("RGB")).astype(np.float32)
    c = uv[tris].mean(1)
    px = np.clip((c[:, 0] % 1.0) * tw, 0, tw - 1).astype(int)
    py = np.clip((c[:, 1] % 1.0) * th, 0, th - 1).astype(int)
    col = np.clip(texa[py, px] * shade[:, None], 0, 255).astype(np.uint8)
    order = np.argsort(z[tris].mean(1))                     # far first (camera looks down -z)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in order:
        a, b_, c_ = tris[i]
        d.polygon([(x[a], y[a]), (x[b_], y[b_]), (x[c_], y[c_])], fill=tuple(col[i]) + (255,))
    return img.resize(size, Image.LANCZOS)


def render_hq(verts, tris, uv, tex, yaw, pitch, size, scale, ground, shift=0.0):
    """Like render(), but z-buffered and textured per pixel: faces, hair and trim stay readable."""
    cy, sy = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    v = verts @ (rx @ ry).T
    ss = 2
    W, H = size[0] * ss, size[1] * ss
    x = (v[:, 0] * scale + size[0] * (0.5 + shift)) * ss
    y = (ground - v[:, 1] * scale) * ss
    z = v[:, 2]
    tv = v[tris]
    n = np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    light = np.array([-0.35, 0.55, 0.75])
    light /= np.linalg.norm(light)
    shade = 0.8 + 0.55 * np.abs(n @ light)
    texa = np.asarray(tex.convert("RGBA")).astype(np.float32)
    th, tw = texa.shape[:2]
    uv = uv.astype(np.float64)
    img = np.zeros((H, W, 4), np.float32)
    zbuf = np.full((H, W), -np.inf)
    for i, (i0, i1, i2) in enumerate(tris):
        xs, ys = x[[i0, i1, i2]], y[[i0, i1, i2]]
        x0, x1 = max(int(xs.min()), 0), min(int(np.ceil(xs.max())), W - 1)
        y0, y1 = max(int(ys.min()), 0), min(int(np.ceil(ys.max())), H - 1)
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if x1 < x0 or y1 < y0 or abs(den) < 1e-9:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
        l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
        l2 = 1 - l0 - l1
        zz = l0 * z[i0] + l1 * z[i1] + l2 * z[i2]
        zb = zbuf[y0:y1 + 1, x0:x1 + 1]
        m = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4) & (zz > zb)
        if not m.any():
            continue
        u = (l0 * uv[i0, 0] + l1 * uv[i1, 0] + l2 * uv[i2, 0]) % 1.0
        vv = (l0 * uv[i0, 1] + l1 * uv[i1, 1] + l2 * uv[i2, 1]) % 1.0
        col = texa[np.clip((vv * th).astype(int), 0, th - 1), np.clip((u * tw).astype(int), 0, tw - 1)]
        m &= col[..., 3] >= 40                                # cut-out texels (hair tips, fringes)
        zb[m] = zz[m]
        blk = img[y0:y1 + 1, x0:x1 + 1]
        blk[m, :3] = np.clip(col[..., :3] * shade[i], 0, 255)[m]
        blk[m, 3] = 255
    return Image.fromarray(img.astype(np.uint8), "RGBA").resize(size, Image.LANCZOS)


def parse_frame(spec):
    """'clip@ms' or 'clipA@ms>clipB@ms:w' -> (clipA, seconds, clipB, seconds, w)."""
    m = re.fullmatch(r"([\w.]+)@([\d.]+)(?:>([\w.]+)@([\d.]+):([\d.]+))?", spec.strip())
    if not m:
        raise SystemExit(f"bad --frame {spec!r}: use clip@ms or clipA@ms>clipB@ms:weight")
    a, ta, b, tb, w = m.groups()
    return a, float(ta) / 1000, b, (float(tb) / 1000 if tb else 0.0), (float(w) if w else 0.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder")
    ap.add_argument("--champ", default="Garen")
    ap.add_argument("--anim", action="append", default=[], help="substring of the .anm file name (repeatable)")
    ap.add_argument("--frames", type=int, default=6)
    ap.add_argument("--t0", type=float, default=0.0, help="start of the sampled window, seconds")
    ap.add_argument("--t1", type=float, help="end of the sampled window, seconds (default: clip end)")
    ap.add_argument("--times", help="explicit frame times in ms, comma-separated (overrides --frames/--t0/--t1)")
    ap.add_argument("--bg", default="92,98,86", help="background R,G,B (arena olive; 225,225,225 for prompts)")
    ap.add_argument("--no-labels", action="store_true", help="no frame times under the cells (for image prompts)")
    ap.add_argument("--yaw", type=float, default=90.0, help="degrees; 90 = facing right")
    ap.add_argument("--pitch", type=float, default=12.0, help="degrees the camera looks down")
    ap.add_argument("--size", type=int, default=260, help="cell height in px")
    ap.add_argument("--width", type=float, default=0.9, help="cell width as a fraction of --size")
    ap.add_argument("--fit", type=float, default=0.62, help="bind-pose height as a fraction of --size")
    ap.add_argument("--shift", type=float, default=0.0, help="move the character right by this fraction of the cell")
    ap.add_argument("--ground", type=float, default=0.84, help="feet line as a fraction of the cell height")
    ap.add_argument("--mirror", action="store_true",
                    help="render the other side (yaw -> -yaw) and flip it, so a pose whose chest faces the "
                         "champion's right still shows its front while facing right (TFM2 sprites show the front)")
    ap.add_argument("--frame", action="append", default=[],
                    help="explicit frame, repeatable, in order: clip@ms, or clipA@ms>clipB@ms:w to cross-fade "
                         "(w = weight of clipB); clip = .anm name without extension. Needs --name")
    ap.add_argument("--name", help="file name (without .png) of the --frame strip")
    ap.add_argument("--hq", action="store_true", help="per-pixel textured render (clearer face and trim; slower)")
    ap.add_argument("--head", type=float, default=1.0,
                    help="scale the head (about 2 gives the big-headed TFM2 proportions)")
    ap.add_argument("--legs", type=float, default=1.0, help="scale each leg from the hip down (TFM2: about 0.8)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.frame and not args.name:
        ap.error("--frame needs --name")
    champ = args.champ
    wad_path = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions", f"{champ}.wad.client")
    w = Wad(wad_path)
    skin_bin = w.read_path(f"data/characters/{champ.lower()}/skins/skin0.bin")
    refs = lambda blob, ext: sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\." + ext, blob)))
    skn = [p for p in refs(skin_bin, rb"skn") if "/Base/" in p][0]
    skl = [p for p in refs(skin_bin, rb"skl") if "/Base/" in p][0]
    texs = [p for p in refs(skin_bin, rb"(?:tex|dds)") if "/Base/" in p and "_TX_CM" in p]
    tris, verts = read_skn(w.read_path(skn.lower()))
    joints, influences = read_skl(w.read_path(skl.lower()))
    tex = read_tex(w.read_path(texs[0].lower())) if texs else Image.new("RGB", (4, 4), (180, 180, 180))
    bind = globals_(joints, [trs(j["t"], j["r"], j["s"]) for j in joints])
    bind_inv = [np.linalg.inv(m) for m in bind]
    anims = refs(w.read_path(f"data/characters/{champ.lower()}/animations/skin0.bin"), rb"anm")
    # frame the character once, from the bind pose: height -> cell height
    rest = skin(verts, influences, bind_inv, bind)
    small = args.head != 1.0 or args.legs != 1.0
    if small:
        legv = leg_vertices(joints, influences, verts)
        tall = skin(verts, influences, bind_inv, globals_(joints, [
            trs(*p) for p in chibi(joints, [(j["t"], j["r"], j["s"]) for j in joints], args.head, args.legs)]))
        height = tall[:, 1].max() - tall[:, 1].min()
    else:
        height = rest[:, 1].max() - rest[:, 1].min()
    scale = args.size * args.fit / height
    ground = args.size * args.ground
    os.makedirs(args.out, exist_ok=True)
    draw = render_hq if args.hq else render

    def cell(local):
        pv = skin(verts, influences, bind_inv, globals_(joints, [trs(*p) for p in chibi(joints, local, args.head, args.legs)]))
        if small:   # shorter legs lift the body: put the lowest point of the legs where League has it
            adult = skin(verts, influences, bind_inv, globals_(joints, [trs(*p) for p in local]))
            pv[:, 1] += adult[legv, 1].min() - pv[legv, 1].min()
        pv[:, 1] -= rest[:, 1].min()
        size = (int(args.size * args.width), args.size)
        if args.mirror:
            return draw(pv, tris, verts["uv"], tex, -args.yaw, args.pitch, size, scale, ground,
                        -args.shift).transpose(Image.FLIP_LEFT_RIGHT)
        return draw(pv, tris, verts["uv"], tex, args.yaw, args.pitch, size, scale, ground, args.shift)

    def save(cells, labels, name):
        cw, chh = cells[0].size
        bg = tuple(int(c) for c in args.bg.split(",")) + (255,)
        sheet = Image.new("RGBA", (cw * len(cells), chh + (0 if args.no_labels else 16)), bg)
        dr = ImageDraw.Draw(sheet)
        for i, (cimg, label) in enumerate(zip(cells, labels)):
            sheet.alpha_composite(cimg, (i * cw, 0))
            if not args.no_labels:
                dr.text((i * cw + 4, chh + 2), f"{i + 1}: {label}", fill=(255, 255, 255, 255))
        out = os.path.join(args.out, f"{name}.png")
        sheet.save(out)
        return out

    if args.frame:
        by_name = {os.path.splitext(os.path.basename(a))[0].lower(): a for a in anims}
        loaded = {}

        def clip(name):
            if name.lower() not in by_name:
                raise SystemExit(f"no clip {name!r}; clips: {', '.join(sorted(by_name))}")
            if name.lower() not in loaded:
                loaded[name.lower()] = read_anim(w.read_path(by_name[name.lower()].lower()))
            return loaded[name.lower()]

        cells = []
        for spec in args.frame:
            a, ta, b, tb, wgt = parse_frame(spec)
            local = local_pose(joints, clip(a), ta)
            if b:
                local = blend_pose(local, local_pose(joints, clip(b), tb), wgt)
            cells.append(cell(local))
        print(f"{args.name}: {len(cells)} frames -> {save(cells, args.frame, args.name)}")
        return
    wanted = [a for a in anims if any(s.lower() in os.path.basename(a).lower() for s in args.anim)] or anims[:1]
    for path in wanted:
        try:
            anim = read_anim(w.read_path(path.lower()))
        except ValueError as e:
            print(f"skip {os.path.basename(path)}: {e}")
            continue
        t1 = min(args.t1 if args.t1 is not None else anim["duration"], anim["duration"])
        ts = [args.t0 + (t1 - args.t0) * i / args.frames for i in range(args.frames)]
        if args.times:
            ts = [float(x) / 1000.0 for x in args.times.split(",")]
        cells = [cell(local_pose(joints, anim, t)) for t in ts]
        name = os.path.splitext(os.path.basename(path))[0]
        out = save(cells, [f"{t * 1000:.0f} ms" for t in ts], name)
        print(f"{name}: {anim['duration']:.2f}s @ {anim['fps']:.0f} fps -> {out}")


if __name__ == "__main__":
    main()
