#!/usr/bin/env python3
"""Preview images for Soraka, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_soraka.py [--out docs/preview]

  league_soraka_frames.png    every animation, frame by frame, 3x on the arena colour
  league_soraka_effects.png   every effect animation, 3x
  league_soraka_showcase.gif  a scripted fight, timed like the kit: Soraka runs in behind Garen, a
                              starlight bolt, Q Starcall on two mirrored Lee Sins (Rejuvenation on her,
                              then the Equinox field that roots them 1.5 s later), W Astral Infusion on
                              Garen, R Wish landing on both of them, 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_leesin import Foe  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_soraka")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_soraka_fx", "league_soraka_zone", "league_soraka_r")}


def showcase(out, z=3, step=40):
    sor = load(CHAMP)
    garen, lee = load(os.path.join(LEAGUE, "champions", "league_garen")), load(os.path.join(LEAGUE, "champions", "league_leesin"))
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 320, 150
    gy = 118                                          # pivot row (the Wish pillar rises ~110 px)
    sx, ally_x = 40, 92                               # Soraka, Garen in front of her
    foes = [Foe(lee, 214, gy), Foe(lee, 244, gy)]
    ally = frames_of(garen, "idle")
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, x0=None, x1=None):
        nonlocal t
        an = Anim(frames_of(sor, tag), t, sx if x0 is None else x0, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=x1)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, x, ground=False):
        (under if ground else over).append(Anim(frames_of(fx[sprite], tag), at, x, gy, z=-1 if ground else 1))

    # run in (move_speed 1000 ~ 1 px a tick)
    a("run", 720, loop=True, x0=sx - 44, x1=sx)
    a("idle", 300, loop=True)
    # basic attack: the bolt leaves at tick 15 and flies 5500 a tick (5.5 px) to the first Lee Sin
    start = t
    a("attack")
    leave = start + tick(15)
    arrive = leave + tick((foes[0].x - 6 - (sx + 10)) / 5.5)
    over.append(Anim(frames_of(fx["league_soraka_fx"], "bolt"), leave, sx + 10, gy - 4, loop=True,
                     until=arrive, x1=foes[0].x - 6, y1=gy - 4, z=1))
    fx_at("league_soraka_fx", "hit", arrive, foes[0].x - 4)
    foes[0].flinches.append(arrive)
    a("idle", 250, loop=True)
    # Q: the star is called at tick 16 and lands 24 ticks later between the two Lee Sins; the
    # Equinox field opens where it landed after its 10 live ticks and roots them 90 ticks later
    start = t
    a("skill")
    spot = (foes[0].x + foes[1].x) // 2
    call = start + tick(16)
    fx_at("league_soraka_zone", "q_star", call, spot)
    land = call + tick(24)
    for fo in foes:
        fo.flinches.append(land)
    fx_at("league_soraka_fx", "rejuv", land, sx)
    field = call + tick(34)
    fx_at("league_soraka_zone", "e_field", field, spot, ground=True)
    root = field + tick(90)
    for fo in foes:
        fx_at("league_soraka_fx", "e_bind", root, fo.x)
        fo.flinches.append(root)
    a("idle", 350, loop=True)
    # W on Garen at tick 13
    start = t
    a("skill2")
    fx_at("league_soraka_fx", "w_heal", start + tick(13), ally_x)
    a("idle", 500, loop=True)
    # R: the wish at tick 16, a pillar on every allied champion
    start = t
    a("ult")
    wish = start + tick(16)
    fx_at("league_soraka_r", "cast", wish, sx)
    for x in (sx, ally_x):
        fx_at("league_soraka_r", "heal", wish, x)
    a("idle", 1200, loop=True)
    end = max(t, root + 1000)

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    ally_total = sum(ms for _, ms in ally)
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:                              # ground effects under the units
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        place(img, Foe.pick(ally, tt % ally_total), ally_x, gy)
        for fo in foes:
            place(img, fo.frame(tt), *fo.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
                break
        for an in over:
            f = an.frame(tt)
            if f is not None:
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_soraka_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_soraka_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_soraka_showcase.gif")))


if __name__ == "__main__":
    main()
