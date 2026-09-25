#!/usr/bin/env python3
"""Preview images for Garen, built from the exported game sprites (so they also prove the
sheets load).

    python tools/art/preview_garen.py [--out docs/preview]

  league_garen_frames.png    every animation, frame by frame, 3x on the arena colour
  league_garen_effects.png   every effect animation, 3x
  league_garen_showcase.gif  a scripted fight against a mirrored Garen, timed like the kit
                             (attack, Q + W, empowered hit, E, R, death), 3x
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

ARENA = T.ARENA_BG
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_garen")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in
      ("league_garen_hits", "league_garen_buffs", "league_garen_spin", "league_garen_r")}


def load(path):
    return T.load_sprite(path)


def frames_of(sp, tag):
    return [(sp.frames[i], sp.durations[i]) for i in sp.tag_frames(tag)]


def contact(sprites, out, z=3, label_w=90):
    """sprites: [(sprite, tag, label)] -> one row per tag, cells sized to that tag's content."""
    rows = []
    for sp, tag, label in sprites:
        fr = frames_of(sp, tag)
        boxes = [f.getbbox() for f, _ in fr]
        boxes = [b for b in boxes if b]
        x0 = min(b[0] for b in boxes) - 2
        x1 = max(b[2] for b in boxes) + 2
        y0 = min(b[1] for b in boxes) - 2
        y1 = max(b[3] for b in boxes) + 2
        y1 = max(y1, sp.h // 2 + 14)                   # always show the feet line
        cw, ch = x1 - x0, y1 - y0
        row = Image.new("RGBA", (label_w + len(fr) * (cw * z + 4), ch * z + 6), (28, 28, 28, 255))
        d = ImageDraw.Draw(row)
        d.text((4, 4), label, fill=(255, 255, 255, 255))
        d.text((4, 18), f"{len(fr)}f {sum(ms for _, ms in fr)}ms", fill=(170, 170, 170, 255))
        for i, (f, _) in enumerate(fr):
            cell = Image.new("RGBA", (cw, ch), ARENA)
            cell.alpha_composite(f.crop((x0, y0, x1, y1)))
            row.paste(cell.resize((cw * z, ch * z), Image.NEAREST), (label_w + i * (cw * z + 4), 3))
        rows.append(row)
    W = max(r.width for r in rows)
    img = Image.new("RGBA", (W, sum(r.height for r in rows)), (28, 28, 28, 255))
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height
    img.save(T.long_path(out))
    return img.size


# ----------------------------------------------------------------------------- showcase
class Anim:
    """A playing animation: frames + durations (ms), optional loop, position, mirror, z."""

    def __init__(self, sp, tag, t0, x, y, loop=False, until=None, flip=False, z=0):
        self.fr = frames_of(sp, tag)
        self.t0, self.x, self.y, self.loop, self.flip, self.z = t0, x, y, loop, flip, z
        total = sum(ms for _, ms in self.fr)
        self.until = until if until is not None else (None if loop else t0 + total)
        self.total = total

    def frame(self, t):
        if t < self.t0 or (self.until is not None and t >= self.until):
            return None
        dt = t - self.t0
        if self.loop:
            dt %= self.total
        for f, ms in self.fr:
            if dt < ms:
                return f.transpose(Image.FLIP_LEFT_RIGHT) if self.flip else f
            dt -= ms
        return None


def tick(n):
    return n * 1000.0 / 60.0


def showcase(out, z=3, step=40):
    garen = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 150, 120
    gx, tx, gy = 58, 88, 78          # Garen, target (30 px apart ~ melee range), pivot row
    body, flinch, effects = [], [], []
    t = 0.0

    def g(tag, dur=None, loop=False):
        nonlocal t
        a = Anim(garen, tag, t, gx, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(a)
        t = a.until

    def hit_target(at, sprite=None, tag=None):
        flinch.append(Anim(garen, "hit", at, tx, gy, flip=True))
        if sprite:
            effects.append(Anim(fx[sprite], tag, at, tx, gy, z=1))

    g("idle", 700, loop=True)
    for _ in range(2):                                   # basic attacks: 22 ticks, hit at 13
        start = t
        g("attack")
        hit_target(start + tick(13), "league_garen_hits", "spark")
        g("idle", tick(62 - 22), loop=True)
    start = t                                            # Q + W cast
    g("skill")
    effects.append(Anim(fx["league_garen_buffs"], "courage", start + tick(4), gx, gy, loop=True,
                        until=start + tick(124), z=1))
    decisive = Anim(fx["league_garen_buffs"], "decisive", start + tick(4), gx, gy, loop=True, z=-1)
    effects.append(decisive)
    g("idle", tick(30), loop=True)
    start = t                                            # empowered attack
    body.append(Anim(garen, "attack", start, gx, gy, until=start + tick(3)))
    body.append(Anim(garen, "q_attack", start + tick(3), gx, gy))
    decisive.until = start + tick(3)
    hit_target(start + tick(16), "league_garen_hits", "q")
    t = start + tick(33)
    g("idle", tick(40), loop=True)
    start = t                                            # E: 3 s spin, 7 pulses
    body.append(Anim(garen, "spin", start, gx, gy, loop=True, until=start + tick(182)))
    effects.append(Anim(fx["league_garen_spin"], "loop", start + tick(2), gx, gy, loop=True,
                        until=start + tick(182), z=1))
    for p in (0, 26, 51, 77, 103, 129, 154):
        hit_target(start + tick(2 + p))
    t = start + tick(182)
    g("idle", tick(30), loop=True)
    start = t                                            # R: the sword lands with the damage
    g("ult")
    effects.append(Anim(fx["league_garen_r"], "impact", start + tick(20), tx, gy, z=1))
    death = start + tick(30)
    g("idle", 1400, loop=True)
    end = t

    idle = frames_of(garen, "idle")
    dead = frames_of(garen, "dead")
    mirror = {}

    def flip(f):
        if id(f) not in mirror:
            mirror[id(f)] = f.transpose(Image.FLIP_LEFT_RIGHT)
        return mirror[id(f)]

    def pick(fr, dt, hold=False):
        for f, ms in fr:
            if dt < ms:
                return f
            dt -= ms
        return fr[-1][0] if hold else None

    def target_frame(tt):
        if tt >= death:
            return flip(pick(dead, tt - death, hold=True))
        for a in flinch:
            f = a.frame(tt)
            if f is not None:
                return f
        return flip(pick(idle, tt % sum(ms for _, ms in idle)))

    def place(img, f, x, y):
        img.alpha_composite(f, (x - f.width // 2, y - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for a in effects:
            f = a.frame(tt) if a.z < 0 else None
            if f is not None:
                place(img, f, a.x, a.y)
        place(img, target_frame(tt), tx, gy)
        for a in body:
            f = a.frame(tt)
            if f is not None:
                place(img, f, gx, gy)
                break
        for a in effects:
            f = a.frame(tt) if a.z >= 0 else None
            if f is not None:
                place(img, f, a.x, a.y)
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    # one palette for the whole clip, sampled from every 8th frame
    sample = frames[::8]
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    g = load(CHAMP)
    size = contact([(g, t["name"], t["name"]) for t in g.tags], os.path.join(args.out, "league_garen_frames.png"))
    print("frames", size)
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_garen_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_garen_showcase.gif")))


if __name__ == "__main__":
    main()
