#!/usr/bin/env python3
"""Preview images for Lux, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_lux.py [--out docs/preview]

  league_lux_frames.png    every animation, frame by frame, 3x on the arena colour
  league_lux_effects.png   every effect animation, 3x
  league_lux_showcase.gif  a scripted fight against a mirrored Lux, timed like the kit (run in, a
                           light bolt, Q Light Binding + Prismatic Barrier, an Illumination
                           ignite, E Lucent Singularity, another ignite, R Final Spark, death), 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_lux")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_lux_fx", "league_lux_r")}


class Lob(Anim):
    """A projectile thrown in an arc (ParabolicProjectile): straight from (x, y) to (x1, y1) plus
    a parabola `h` px high."""

    def __init__(self, *a, h=18, **k):
        super().__init__(*a, **k)
        self.h = h

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return x, int(round(y - 4 * self.h * u * (1 - u)))


def showcase(out, z=3, step=40):
    lux = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 104
    ax, tx, gy = 40, 100, 62          # Lux, target (60 px: attack range), pivot row
    wand = (ax + 12, gy - 2)          # where bolts leave: the thrust wand tip, y_offset 2000
    body, flinch, effects, shots = [], [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(lux, tag), t, ax, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def fx_at(tag, at, x, sprite="league_lux_fx"):
        effects.append(Anim(frames_of(fx[sprite], tag), at, x, gy, z=1))

    def hurt(at):
        flinch.append(Anim(frames_of(lux, "hit"), at, tx, gy, flip=True))

    def bolt(start, ignite=False):
        """Attack: the bolt leaves at tick 13 (5000/tick ~ 5 px), a spark or the ignite on arrival."""
        a("attack")
        at = start + tick(13)
        arrive = at + tick((tx - 4 - wand[0]) / 5.0)
        shots.append(Anim(frames_of(fx["league_lux_fx"], "bolt"), at, wand[0], wand[1], loop=True,
                          until=arrive, x1=tx - 4, y1=gy - 2, z=1))
        fx_at("ignite" if ignite else "hit", arrive, tx)
        hurt(arrive)
        a("idle", tick(90 - 30), loop=True)

    run = 1000                                        # run in: move_speed 900 ~ 0.9 px a tick
    body.append(Anim(frames_of(lux, "run"), t, ax - 54, gy, loop=True, until=t + run, x1=ax))
    t += run
    a("idle", 400, loop=True)
    bolt(t)
    start = t                                         # Q: the orb at tick 13, 4200/tick; shields at cast
    a("skill")
    at = start + tick(13)
    arrive = at + tick((tx - wand[0]) / 4.2)
    shots.append(Anim(frames_of(fx["league_lux_fx"], "q_orb"), at, wand[0], wand[1], loop=True,
                      until=arrive, x1=tx, y1=gy - 2, z=1))
    fx_at("shield", at, ax)
    fx_at("q_bind", arrive, tx)
    fx_at("mark", arrive, tx)
    hurt(arrive)
    a("idle", tick(30), loop=True)
    bolt(t, ignite=True)                              # Illumination: the next attack ignites
    start = t                                         # E: lobbed at tick 16, lands 20 ticks later,
    a("skill2")                                       # blasts 60 ticks after landing
    at = start + tick(16)
    land = at + tick(20)
    shots.append(Lob(frames_of(fx["league_lux_fx"], "e_orb"), at, wand[0], wand[1], loop=True,
                     until=land, x1=tx, y1=gy + 4, z=1))
    effects.append(Anim(frames_of(fx["league_lux_fx"], "e_zone"), land, tx, gy, z=-1))
    fx_at("mark", land + tick(60), tx)
    hurt(land + tick(60))
    a("idle", land + tick(60) - t + tick(20), loop=True)
    bolt(t, ignite=True)
    start = t                                         # R: the beam's view from tick 2, damage at tick 30
    a("ult")
    effects.append(Anim(frames_of(fx["league_lux_r"], "beam"), start + tick(2), ax + 120, gy, z=1))
    fx_at("mark", start + tick(30), tx)
    hurt(start + tick(30))
    death = start + tick(34)
    a("idle", death - t + 1800, loop=True)
    end = t

    idle = frames_of(lux, "idle")
    dead = frames_of(lux, "dead")
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
        for an in effects:                            # ground effects under the units
            f = an.frame(tt)
            if f is not None and an.z < 0:
                place(img, f, *an.pos(tt))
        place(img, target_frame(tt), tx, gy)
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
                break
        for an in effects + shots:
            f = an.frame(tt)
            if f is not None and an.z >= 0:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]                              # one palette for the whole clip
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_lux_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[11:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_lux_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_lux_showcase.gif")))


if __name__ == "__main__":
    main()
