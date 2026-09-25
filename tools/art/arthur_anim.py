"""Arthur's animations: poses per frame, in-sprite effects (sword smears, glows), sheet export.

    python tools/art/arthur_anim.py [--preview out_dir]

Writes hok/champions/hok_arthur#sheet.png + #anim.fanim. Timings follow the champion data:
attack 22 ticks (hit at 13), skill 30 (dash from 8), skill2 20 (cast at 6), ult 40 (leap from 10).
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_lib as fx  # noqa: E402
import px  # noqa: E402
from arthur_rig import FH, FW, GROUND, pose_frame, sword_only  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

STAND = dict(leg_n=("leg_n", 4, (0, 0)), leg_f=("leg_f", -6, (0, 0)))


def P(**kw):
    d = dict(STAND)
    d.update(kw)
    return pose_frame(**d)


# ----------------------------------------------------------------------------- effects
def smear(a0, a1, thick, r=19, ramp=fx.GOLD, dx=0, dy=0, ry=1.0):
    """Sword smear around the shoulder, from a0 (trailing) to a1 (leading)."""
    def draw(f, an):
        cx, cy = an["shoulder"]
        fx.crescent(f, cx + dx, cy + dy, r, a0, a1, thick, ramp, ry_scale=ry)
    return draw


def combo(*fns):
    def draw(f, an):
        for fn in fns:
            if fn:
                fn(f, an)
    return draw


def tip_sparkle(size=2):
    def draw(f, an):
        if "tip" in an:
            fx.sparkle(f, an["tip"][0], an["tip"][1], size)
    return draw


def excalibur(length, width, sparkle=0):
    """Blade of light along the sword: behind it as an aura (skill 2), or giant in front (ult)."""
    def draw(f, an):
        hx, hy = an["hand"]
        tx, ty = an["tip"]
        ang = math.degrees(math.atan2(ty - hy, tx - hx))
        fx.light_blade(f, hx, hy, ang, length, width)
        if sparkle:
            ex, ey = hx + math.cos(math.radians(ang)) * length, hy + math.sin(math.radians(ang)) * length
            fx.sparkle(f, ex, ey, sparkle)
    return draw


def speed_lines(seed):
    def draw(f, an):
        hx, hy = an["hip"]
        fx.streaks(f, hx - 30, hx - 12, [hy - 14, hy - 9, hy - 3, hy + 3, hy + 9], fx.GOLD, seed=seed)
    return draw


def ground_flash(r, seed=0):
    def draw(f, an):
        fx.burst(f, an["tip"][0], GROUND - 1, 2, r, 9, fx.HOLY, seed=seed, ry_scale=0.45)
    return draw


# ----------------------------------------------------------------------------- animations
def idle():
    frames = []
    bob = [0, 0, 1, 1, 1, 0]
    hem = [0, -1, -2, -2, -1, 0]
    for i in range(6):
        frames.append((P(up=(0, bob[i]), cape=("cape", 0, hem[i])), 120))
    return frames


def run():
    near = [(-26, "leg_n"), (-12, "leg_n"), (2, "leg_n"), (16, "leg_n"), (28, "leg_n"), (8, "leg_n_bent"), (-14, "leg_n_bent"), (-24, "leg_n")]
    far = [(26, "leg_f"), (6, "leg_f_bent"), (-16, "leg_f_bent"), (-24, "leg_f"), (-26, "leg_f"), (-12, "leg_f"), (2, "leg_f"), (16, "leg_f")]
    hip_dy = [1, 0, -1, 0, 1, 0, -1, 0]
    flap = [0, 2, 3, 1, 0, 2, 3, 1]
    arm = [8, 4, 0, -4, -8, -4, 0, 4]
    frames = []
    for i in range(8):
        frames.append((pose_frame(
            hip=(0, hip_dy[i]), up=(1, 0),
            leg_n=(near[i][1], near[i][0], (0, 0)), leg_f=(far[i][1], far[i][0], (0, 0)),
            arm=(arm[i], arm[i] + 10), sword=238 + arm[i],
            shield_d=(1, 0), cape=("cape", 38 + flap[i] * 2, flap[i]),
        ), 80))
    return frames


def attack():
    return [
        (P(up=(-1, 0), arm=(140, 165), sword=300, leg_n=("leg_n", 10, (0, 0)), leg_f=("leg_f", -12, (0, 0)),
           cape=("cape", 4, -1)), 70),
        (P(up=(-2, 0), arm=(160, 185), sword=285, leg_n=("leg_n", 12, (0, 0)), leg_f=("leg_f", -14, (0, 0)),
           cape=("cape", 6, -2)), 70),
        (P(up=(1, 0), arm=(230, 250), sword=45, leg_n=("leg_n", 14, (0, 0)), leg_f=("leg_f", -18, (0, 0)),
           cape=("cape", 14, 1), fx_back=smear(-160, -55, 5, r=20)), 50),
        (P(up=(3, 1), arm=(290, 280), sword=118, head="head_shout", leg_n=("leg_n", 18, (0, 0)),
           leg_f=("leg_f", -24, (0, 0)), shield_d=(-1, 0), cape=("cape", 22, 2),
           fx_front=smear(-120, 40, 6, r=22, dx=3, dy=2)), 60),
        (P(up=(2, 1), arm=(310, 300), sword=140, leg_n=("leg_n", 16, (0, 0)), leg_f=("leg_f", -22, (0, 0)),
           cape=("cape", 16, 1), fx_front=smear(-20, 55, 3, r=22, dx=3, dy=2, ramp=fx.GOLD[1:])), 60),
        (P(up=(1, 0), arm=(340, 330), sword=170, cape=("cape", 8, 0)), 60),
    ]


def skill():
    dash = dict(hip=(2, 1), up=(3, 1), head="head_shout",
                leg_n=("leg_n", 38, (0, 0)), leg_f=("leg_f_bent", -30, (0, 0)),
                arm=(70, 55), sword=262, shield_d=(3, -1))
    return [
        (P(hip=(0, 2), up=(-1, 1), head="head_shout", leg_n=("leg_n_bent", 8, (0, 0)), leg_f=("leg_f_bent", -8, (0, 0)),
           arm=(60, 40), sword=250, shield_d=(1, -1), cape=("cape", 6, -1)), 70),
        (pose_frame(**dash, cape=("cape", 52, 2), fx_back=speed_lines(1)), 60),
        (pose_frame(**dash, cape=("cape", 58, 4), fx_back=speed_lines(2)), 80),
        (pose_frame(**dash, cape=("cape", 54, 2), fx_back=speed_lines(3)), 80),
        (P(up=(3, 0), head="head_shout", arm=(235, 215), sword=55, leg_n=("leg_n", 20, (0, 0)), leg_f=("leg_f", -22, (0, 0)),
           shield_d=(1, 0), cape=("cape", 30, 2), fx_front=smear(150, 300, 7, r=21)), 70),
        (P(up=(2, 0), arm=(200, 190), sword=25, leg_n=("leg_n", 14, (0, 0)), leg_f=("leg_f", -18, (0, 0)),
           cape=("cape", 16, 1), fx_front=smear(215, 305, 3, r=21, ramp=fx.GOLD[1:])), 70),
        (P(up=(1, 0), arm=(60, 50), sword=230, cape=("cape", 6, 0)), 70),
    ]


def skill2():
    up = dict(head="head_shout", arm=(180, 180), sword=0, up=(0, -1))
    return [
        (P(**up, cape=("cape", 4, -1), fx_front=tip_sparkle(2)), 60),
        (P(**up, cape=("cape", 6, -2), fx_back=excalibur(22, 5), fx_front=tip_sparkle(3)), 70),
        (P(arm=(265, 270), sword=90, up=(1, 0), head="head_shout", leg_n=("leg_n", 12, (0, 0)), leg_f=("leg_f", -14, (0, 0)),
           cape=("cape", 20, 2), fx_front=smear(-200, 20, 6, r=22, ry=0.45, dy=8)), 70),
        (P(arm=(300, 310), sword=150, up=(1, 0), cape=("cape", 12, 1),
           fx_front=smear(-60, 60, 3, r=22, ry=0.45, dy=8, ramp=fx.GOLD[1:])), 60),
        (P(arm=(20, 30), sword=220, cape=("cape", 4, 0)), 73),
    ]


def ult():
    tuck = dict(leg_n=("leg_n_bent", -20, (0, 0)), leg_f=("leg_f_bent", -30, (0, 0)))
    raised = dict(arm=(180, 182), sword=2, head="head_shout")
    return [
        (P(hip=(0, 3), up=(-1, 1), head="head_shout", leg_n=("leg_n_bent", 14, (0, 0)), leg_f=("leg_f_bent", -10, (0, 0)),
           arm=(75, 60), sword=245, cape=("cape", 4, -2)), 80),
        (pose_frame(root=(0, -8), **tuck, **raised, cape=("cape", -18, 3), fx_front=excalibur(24, 5, 2)), 80),
        (pose_frame(root=(1, -13), **tuck, **raised, cape=("cape", -26, 4), fx_front=excalibur(34, 7, 3)), 80),
        (pose_frame(root=(2, -7), up=(2, 0), leg_n=("leg_n_bent", -10, (0, 0)), leg_f=("leg_f", -20, (0, 0)),
                    arm=(250, 240), sword=70, head="head_shout", cape=("cape", -10, 2),
                    fx_front=combo(smear(-110, -10, 6, r=22, ramp=fx.HOLY), excalibur(30, 6))), 60),
        (P(root=(3, 0), hip=(0, 4), up=(2, 2), head="head_shout", leg_n=("leg_n_kneel", 0, (0, -1)),
           leg_f=("leg_f_bent", -18, (0, 0)), arm=(320, 350), sword=178, sword_clip=GROUND + 1, cape=("cape", 10, 2),
           fx_front=combo(smear(-40, 70, 5, r=22, ramp=fx.HOLY), ground_flash(14, 1))), 80),
        (P(root=(3, 0), hip=(0, 4), up=(2, 2), head="head_shout", leg_n=("leg_n_kneel", 0, (0, -1)),
           leg_f=("leg_f_bent", -18, (0, 0)), arm=(320, 350), sword=178, sword_clip=GROUND + 1, cape=("cape", 6, 1),
           fx_front=ground_flash(9, 2)), 110),
        (P(root=(2, 0), hip=(0, 2), up=(1, 1), leg_n=("leg_n_bent", 6, (0, 0)), leg_f=("leg_f_bent", -10, (0, 0)),
           arm=(330, 345), sword=190, cape=("cape", 3, 0)), 90),
        (P(root=(1, 0), arm=(10, 15), sword=215), 87),
    ]


def hit():
    return [(P(up=(-2, 0), head="head_hurt", arm=(25, 30), sword=232, shield_d=(-1, 0),
               leg_n=("leg_n", 12, (0, 0)), cape=("cape", -4, 1)), 100)]


def dead():
    an = {}
    kneel = pose_frame(anchors_out=an, hip=(0, 4), up=(-1, 2), head="head_hurt", leg_n=("leg_n_kneel", 0, (0, -1)),
                       leg_f=("leg_f_bent", -14, (0, 0)), arm=(-10, -5), sword=175, sword_clip=GROUND + 1,
                       cape=("cape", 6, 1))
    planted = sword_only(an["hand"], 175, GROUND + 1)
    frames = [
        (P(up=(-2, 0), head="head_hurt", arm=(25, 30), sword=232, shield_d=(-1, 0), leg_n=("leg_n", 12, (0, 0))), 100),
        (P(hip=(-1, 1), up=(-3, 1), head="head_hurt", leg_n=("leg_n_bent", 16, (0, 0)), leg_f=("leg_f", -8, (0, 0)),
           arm=(40, 30), sword=225, shield_d=(-1, 1), cape=("cape", -6, 1)), 100),
        (kneel, 120),
        (kneel, 140),
    ]
    # topple backwards about the back knee, then lie flat on the back (head to the left)
    pivot = (FW // 2 - 6, GROUND)
    body = pose_frame(hip=(0, 4), up=(-1, 2), head="head_hurt", leg_n=("leg_n_kneel", 0, (0, -1)),
                      leg_f=("leg_f_bent", -14, (0, 0)), arm=(-10, -5), sword=175, show_sword=False)
    for ang in (-35, -65):
        img, pv = px.rotsprite(body, ang, pivot)
        f = px.new(FW, FH)
        px.paste(f, img, pivot[0] - pv[0], pivot[1] - pv[1])
        f = _settle(f)
        f.alpha_composite(planted)
        frames.append((f, 100))
    flat = pose_frame(head="head_hurt", leg_n=("leg_n", 6, (0, 0)), leg_f=("leg_f", -4, (0, 0)),
                      arm=(20, 10), sword=200, show_sword=False, cape=("cape", 0, 0))
    img, pv = px.rotsprite(flat, -90, (FW // 2, GROUND))
    lying = px.new(FW, FH)
    px.paste(lying, img, FW // 2 + 4 - pv[0], GROUND - pv[1])
    lying = _settle(lying)
    lying.alpha_composite(planted)
    frames.append((lying, 160))
    frames.append((lying, 300))
    return frames


def _settle(f):
    """Drop a toppled body so its lowest pixel rests on the ground row."""
    bb = f.getbbox()
    if not bb:
        return f
    return px.shift(f, 0, GROUND - (bb[3] - 1))


ANIMS = [("idle", idle), ("run", run), ("attack", attack), ("skill", skill), ("skill2", skill2),
         ("ult", ult), ("hit", hit), ("dead", dead)]


def build():
    return [(name, fn()) for name, fn in ANIMS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="folder for contact sheet + GIFs")
    args = ap.parse_args()
    tags = build()
    sheet, fanim = px.sheet_and_fanim(tags, FW, FH)
    out = os.path.join(ROOT, "hok", "champions", "hok_arthur")
    px.save_png(sheet, out + "#sheet.png")
    px.save_json(fanim, out + "#anim.fanim")
    print("sheet", sheet.size, "frames", sum(len(f) for _, f in tags))
    if args.preview:
        from preview import contact, gifs
        contact(tags, os.path.join(args.preview, "arthur_frames.png"))
        gifs(tags, args.preview, "arthur")


if __name__ == "__main__":
    main()
