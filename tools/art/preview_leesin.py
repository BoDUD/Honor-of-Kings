#!/usr/bin/env python3
"""Preview images for Lee Sin, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_leesin.py [--out docs/preview]

  league_leesin_frames.png    every animation, frame by frame, 3x on the arena colour
  league_leesin_effects.png   every effect animation, 3x
  league_leesin_showcase.gif  a scripted fight against two mirrored Lee Sins, timed like the kit (run
                              in, Q Sonic Wave + the Resonating Strike dash, two Flurry punches,
                              E Tempest + Safeguard, R Dragon's Rage kicking the target into the one
                              behind it, death), 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_leesin")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_leesin_fx", "league_leesin_r")}


class Foe:
    """A mirrored Lee Sin standing at x: idle, flinches, a knock-back slide, a knock-up hop, death."""

    def __init__(self, lee, x, y):
        self.idle, self.hit, self.dead = frames_of(lee, "idle"), frames_of(lee, "hit"), frames_of(lee, "dead")
        self.x, self.y = x, y
        self.flinches, self.slides, self.hops, self.death = [], [], [], None
        self.mirror = {}

    def flip(self, f):
        if id(f) not in self.mirror:
            self.mirror[id(f)] = f.transpose(Image.FLIP_LEFT_RIGHT)
        return self.mirror[id(f)]

    def pos(self, t):
        x, y = self.x, self.y
        for t0, t1, dx in self.slides:
            if t >= t0:
                x += dx * min(1.0, (t - t0) / (t1 - t0))
        for t0, t1, h in self.hops:
            if t0 <= t < t1:
                u = (t - t0) / (t1 - t0)
                y -= 4 * h * u * (1 - u)
        return int(round(x)), int(round(y))

    @staticmethod
    def pick(fr, dt, hold=False):
        for f, ms in fr:
            if dt < ms:
                return f
            dt -= ms
        return fr[-1][0] if hold else None

    def frame(self, t):
        if self.death is not None and t >= self.death:
            return self.flip(self.pick(self.dead, t - self.death, hold=True))
        for t0, t1, _ in self.slides + self.hops:
            if t0 <= t < t1:
                return self.flip(self.hit[0][0])
        for t0 in self.flinches:
            f = self.pick(self.hit, t - t0) if t >= t0 else None
            if f is not None:
                return self.flip(f)
        return self.flip(self.pick(self.idle, t % sum(ms for _, ms in self.idle)))


def showcase(out, z=3, step=40):
    lee = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 320, 104
    gy = 62                                           # pivot row
    foe, back = Foe(lee, 150, gy), Foe(lee, 200, gy)  # the target, and one behind it for the R
    body, effects, shots = [], [], []
    t = 0.0
    x = 20                                            # Lee Sin's x

    def a(tag, dur=None, loop=False, x1=None):
        nonlocal t, x
        an = Anim(frames_of(lee, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=x1)
        body.append(an)
        t = an.until
        if x1 is not None:
            x = x1

    def fx_at(tag, at, fx_x, fy=None, sprite="league_leesin_fx", z_=1, follow=None):
        effects.append(Anim(frames_of(fx[sprite], tag), at, fx_x, gy if fy is None else fy, z=z_))

    # run in (move_speed 1100 ~ 1.1 px a tick)
    body.append(Anim(frames_of(lee, "run"), t, x - 50, gy, loop=True, until=t + 760, x1=x + 30))
    t += 760
    x += 30
    a("idle", 300, loop=True)
    # Q: the wave leaves at tick 16 (4500/tick), the mark on the hit; 12 ticks later the dash (5000/tick)
    start = t
    a("skill")
    at = start + tick(16)
    arrive = at + tick((foe.x - 6 - (x + 10)) / 4.5)
    shots.append(Anim(frames_of(fx["league_leesin_fx"], "q_wave"), at, x + 10, gy - 2, loop=True,
                      until=arrive, x1=foe.x - 6, y1=gy - 2, z=1))
    fx_at("q_mark", arrive, foe.x)
    foe.flinches.append(arrive)
    dash0 = arrive + tick(12)
    dest = foe.x - 22                                  # melee range
    dash1 = dash0 + tick((dest - x) / 5.0)
    if t < dash0:
        a("idle", dash0 - t, loop=True)
    else:
        t = dash0
    body.append(Anim(frames_of(lee, "q2"), dash0, x, gy, until=dash0 + tick(31), x1=dest))
    body[-1].until_move = dash1
    fx_at("q2_hit", dash1, foe.x)
    foe.flinches.append(dash1)
    t = dash0 + tick(31)
    x = dest

    def punch():
        nonlocal t
        start = t
        a("attack")
        fx_at("hit", start + tick(12), foe.x - 4, gy - 4)
        foe.flinches.append(start + tick(12))
        a("idle", tick(36 - 20), loop=True)           # Flurry: 50-tick cooldown, 40% faster

    punch()
    punch()
    # E: the slam at tick 17 - the ring on the ground, the shield on Lee Sin
    start = t
    a("skill2")
    fx_at("e_wave", start + tick(17), x, z_=-1)
    fx_at("shield", start + tick(17), x)
    foe.flinches.append(start + tick(17))
    a("idle", 300, loop=True)
    punch()
    # R: the kick at tick 18 - 54 px knock-back in 18 ticks, the dragon behind it at the same speed
    start = t
    a("ult")
    kick = start + tick(18)
    fx_at("kick", kick, foe.x, gy - 4, sprite="league_leesin_r")
    foe.slides.append((kick, kick + tick(18), 54))
    shots.append(Anim(frames_of(fx["league_leesin_r"], "dragon"), kick, x, gy - 2, loop=True,
                      until=kick + tick(63 / 3.0), x1=x + 63, y1=gy - 2, z=1))
    hit_back = kick + tick((back.x - 14 - x) / 3.0)   # the dragon's circle reaches the one behind
    fx_at("knockup", hit_back, back.x)
    back.hops.append((hit_back, hit_back + tick(45), 12))
    foe.death = kick + tick(18)
    a("idle", tick(18) + 1600, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    def body_pos(an, tt):
        if getattr(an, "until_move", None) is None:
            return an.pos(tt)
        u = min(1.0, max(0.0, (tt - an.t0) / (an.until_move - an.t0)))
        return int(round(an.x + (an.x1 - an.x) * u)), an.y

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in effects:                            # ground effects under the units
            f = an.frame(tt)
            if f is not None and an.z < 0:
                place(img, f, *an.pos(tt))
        for fo in (back, foe):
            place(img, fo.frame(tt), *fo.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *body_pos(an, tt))
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_leesin_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_leesin_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_leesin_showcase.gif")))


if __name__ == "__main__":
    main()
