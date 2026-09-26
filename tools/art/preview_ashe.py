#!/usr/bin/env python3
"""Preview images for Ashe, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_ashe.py [--out docs/preview]

  league_ashe_frames.png    every animation, frame by frame, 3x on the arena colour
  league_ashe_effects.png   every effect animation, 3x
  league_ashe_showcase.gif  a scripted fight against a mirrored Ashe, timed like the kit (run in,
                            two frost arrows, Q + flurries, W volley, R crystal arrow + freeze,
                            death), arrows flying at the kit's projectile speeds, 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ashe")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ashe_fx", "league_ashe_r")}


def tick(n):
    return n * 1000.0 / 60.0


class Anim:
    """A playing animation (frames + ms), optionally looping, moving from (x, y) to (x1, y1)."""

    def __init__(self, fr, t0, x, y, loop=False, until=None, flip=False, z=0, x1=None, y1=None):
        self.fr, self.t0, self.x, self.y, self.loop, self.flip, self.z = fr, t0, x, y, loop, flip, z
        self.total = sum(ms for _, ms in fr)
        self.until = until if until is not None else (None if loop else t0 + self.total)
        self.x1, self.y1 = (x if x1 is None else x1), (y if y1 is None else y1)

    def pos(self, t):
        if self.until is None or self.until == self.t0:
            return self.x, self.y
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return int(round(self.x + (self.x1 - self.x) * u)), int(round(self.y + (self.y1 - self.y) * u))

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


def showcase(out, z=3, step=40):
    ashe = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 200, 100
    ax, tx, gy = 56, 136, 60          # Ashe, target (80 px: attack range), pivot row
    bow = (ax + 9, gy - 3)            # where arrows leave (crossbowman's y_offset 1200 ~ 1 px up)
    body, flinch, effects, shots = [], [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(ashe, tag), t, ax, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def shoot(at, sprite, tag, speed_px_tick, dy=0, hit=("league_ashe_fx", "hit")):
        """Fly a projectile from the bow to the target; returns the arrival time."""
        dist = (tx - 4) - bow[0]
        arrive = at + tick(dist / speed_px_tick)
        shots.append(Anim(frames_of(fx[sprite], tag), at, bow[0], bow[1] + dy, loop=True, until=arrive,
                          x1=tx - 4, y1=gy - 4 + dy, z=1))
        flinch.append(Anim(frames_of(ashe, "hit"), arrive, tx, gy, flip=True))
        if hit:
            effects.append(Anim(frames_of(fx[hit[0]], hit[1]), arrive, tx, gy, z=1))
        return arrive

    run = 1000                                         # run in: move_speed 900 ~ 0.9 px a tick
    body.append(Anim(frames_of(ashe, "run"), t, ax - 54, gy, loop=True, until=t + run, x1=ax))
    t += run
    a("idle", 400, loop=True)
    for _ in range(2):                                 # basic attacks: 24 ticks, arrow at tick 9
        start = t
        a("attack")
        shoot(start + tick(9), "league_ashe_fx", "arrow", 5.2)
        a("idle", tick(60 - 24), loop=True)
    start = t                                          # Q: focus aura every 30 ticks for 4 s
    a("skill")
    for p in range(0, 240, 30):
        effects.append(Anim(frames_of(fx["league_ashe_fx"], "focus"), start + tick(2 + p), ax, gy, z=1))
    for _ in range(3):                                 # flurries: 30% attack speed, 46-tick rhythm
        start = t
        body.append(Anim(frames_of(ashe, "attack"), start, ax, gy, until=start + tick(1)))
        body.append(Anim(frames_of(ashe, "q_attack"), start + tick(1), ax, gy))
        shoot(start + tick(8), "league_ashe_fx", "flurry", 5.2)
        t = start + tick(24)
        a("idle", tick(46 - 24), loop=True)
    start = t                                          # W: 5 arrows on the release frame (tick 12)
    a("skill2")
    for dy in (-4, -2, 0, 2, 4):
        shoot(start + tick(12), "league_ashe_fx", "arrow", 5.2, dy=dy, hit=None)
    effects.append(Anim(frames_of(fx["league_ashe_fx"], "hit"), start + tick(12 + 13), tx, gy, z=1))
    a("idle", tick(40), loop=True)
    start = t                                          # R: crystal arrow at tick 22, freeze, death
    a("ult")
    arrive = shoot(start + tick(22), "league_ashe_r", "arrow", 4.2, hit=("league_ashe_r", "hit"))
    frozen = (arrive, arrive + tick(105))
    death = frozen[1]
    a("idle", death - t + 1600, loop=True)
    end = t

    idle = frames_of(ashe, "idle")
    dead = frames_of(ashe, "dead")
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
        if frozen[0] <= tt < frozen[1]:                # stunned: holds its hit frame
            return flip(frames_of(ashe, "hit")[0][0])
        for an in flinch:
            f = an.frame(tt)
            if f is not None:
                return f
        return flip(pick(idle, tt % sum(ms for _, ms in idle)))

    def place(img, f, x, y):
        img.alpha_composite(f, (x - f.width // 2, y - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        place(img, target_frame(tt), tx, gy)
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
                break
        for an in effects + shots:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::8]                               # one palette for the whole clip
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
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_ashe_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_ashe_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ashe_showcase.gif")))


if __name__ == "__main__":
    main()
