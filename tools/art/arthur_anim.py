"""Arthur's animations: poses per frame, in-sprite effects (sword smears, glows), sheet export.

    python tools/art/arthur_anim.py [--preview out_dir]

Writes hok/champions/hok_arthur#sheet.png + #anim.fanim. Timings follow the champion data:
attack 22 ticks (hit at 13), skill 30 (dash from 8), skill2 20 (cast at 6), ult 40 (leap from 10).
The basic attack follows Arthur's HoK attack: sword raised upright at his side, then a diagonal
slash down in front of him with a lunge (checked frame by frame on gameplay footage).
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_lib as fx  # noqa: E402
import px  # noqa: E402
from arthur_rig import FH, FW, GROUND, STAND_LEGS, pose_frame, sword_only  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

# lower-body poses: (near leg, far leg), each (drawn pose, x offset, plant | hang)
STAND = STAND_LEGS
LUNGE = (("B", -5, "plant"), ("F", 4, "plant"))       # back leg reaching back, front knee forward
WIDE = (("B", -4, "plant"), ("S", 3, "plant"))
CROUCH = (("C", -4, "plant"), ("C", 2, "plant"))
KNEEL = (("K", -3, "plant"), ("C", 3, "plant"))
AIR = (("T", -3, "hang"), ("T", 2, "hang"))
FALLING = (("P", -3, "hang"), ("S", 2, "hang"))


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
        fx.burst(f, an["tip"][0], an["ground"] - 1, 2, r, 9, fx.HOLY, seed=seed, ry_scale=0.45)
    return draw


# ----------------------------------------------------------------------------- animations
def idle():
    breath = [0, 0, 1, 1, 1, 0]
    hem = [0, -1, -2, -2, -1, 0]
    return [(pose_frame(breath=breath[i], cape=("cape", 0, hem[i])), 120) for i in range(6)]


def run():
    legs = [
        (("F", 2, "plant"), ("B", 0, "plant")),    # contact: near foot ahead, far foot behind
        (("F", 2, "plant"), ("B", 0, "plant")),    # down
        (("S", -2, "plant"), ("P", 3, "hang")),    # passing: far leg swings through
        (("B", -2, "plant"), ("F", 3, "plant")),   # contact: far foot ahead, near foot behind
        (("B", -2, "plant"), ("F", 3, "plant")),   # down
        (("P", -2, "hang"), ("S", 2, "plant")),    # passing: near leg swings through
    ]
    hip = [(1, 1), (1, 2), (1, 0), (1, 1), (1, 2), (1, 0)]
    arm = [6, 3, 0, -6, -3, 0]
    flap = [0, 2, 3, 0, 2, 3]
    return [(pose_frame(legs=legs[i], hip=hip[i], arm=(arm[i], arm[i] + 10), sword=238 + arm[i],
                        shield_d=(1, 0), cape=("cape", 38 + flap[i] * 2, flap[i])), 85) for i in range(6)]


def attack():
    """HoK Arthur: sword raised upright at his side, diagonal slash down in front, lunge."""
    return [
        (pose_frame(hip=(-1, 0), arm=(165, 180), sword=-8, cape=("cape", 2, -1)), 80),
        (pose_frame(hip=(-1, 0), legs=WIDE, arm=(155, 170), sword=-28, cape=("cape", 4, -2)), 70),
        (pose_frame(hip=(1, 0), legs=WIDE, arm=(225, 250), sword=62, cape=("cape", 10, 1),
                    fx_back=smear(-100, -25, 5, r=22, dx=1)), 50),
        (pose_frame(hip=(2, 1), legs=LUNGE, arm=(300, 292), sword=128, head="head_shout", shield_d=(-1, 0),
                    cape=("cape", 18, 2), fx_front=smear(-95, 55, 7, r=23, dx=2, dy=1)), 70),
        (pose_frame(hip=(2, 1), legs=LUNGE, arm=(318, 328), sword=158, cape=("cape", 14, 1),
                    fx_front=smear(5, 70, 3, r=23, dx=2, dy=1, ramp=fx.GOLD[1:])), 60),
        (pose_frame(hip=(1, 0), legs=WIDE, arm=(345, 350), sword=200, cape=("cape", 6, 0)), 40),
    ]


def skill():
    """Valiant Charge: brace behind the shield, charge, hop and chop down on the target."""
    dash = [(("B", -4, "plant"), ("P", 3, "hang")), (("P", -2, "hang"), ("F", 3, "plant")),
            (("B", -4, "plant"), ("P", 3, "hang"))]
    frames = [(pose_frame(hip=(0, 2), legs=CROUCH, head="head_shout", arm=(60, 40), sword=250,
                          shield_d=(1, -1), cape=("cape", 6, -1)), 70)]
    for k, ms in enumerate((60, 70, 70)):
        frames.append((pose_frame(hip=(3, 1), legs=dash[k], head="head_shout", arm=(70, 55), sword=262,
                                  shield_d=(3, -1), cape=("cape", 52 + 3 * k, 2 + k),
                                  fx_back=speed_lines(k + 1)), ms))
    frames += [
        (pose_frame(root=(1, -3), legs=AIR, head="head_shout", arm=(175, 185), sword=-5, shield_d=(1, 0),
                    cape=("cape", 20, 2), fx_front=tip_sparkle(2)), 60),
        (pose_frame(hip=(2, 1), legs=LUNGE, head="head_shout", arm=(305, 298), sword=135, cape=("cape", 24, 2),
                    fx_front=smear(-95, 60, 8, r=24, dx=2, dy=1, ramp=fx.HOLY)), 90),
        (pose_frame(hip=(1, 0), legs=WIDE, arm=(335, 340), sword=190, cape=("cape", 8, 0)), 80),
    ]
    return frames


def skill2():
    up = dict(head="head_shout", arm=(180, 180), sword=0, hip=(0, -1))
    return [
        (pose_frame(**up, cape=("cape", 4, -1), fx_front=tip_sparkle(2)), 60),
        (pose_frame(**up, cape=("cape", 6, -2), fx_back=excalibur(22, 5), fx_front=tip_sparkle(3)), 70),
        (pose_frame(arm=(265, 270), sword=90, hip=(1, 0), legs=WIDE, head="head_shout", cape=("cape", 20, 2),
                    fx_front=smear(-200, 20, 6, r=22, ry=0.45, dy=8)), 70),
        (pose_frame(arm=(300, 310), sword=150, hip=(1, 0), legs=WIDE, cape=("cape", 12, 1),
                    fx_front=smear(-60, 60, 3, r=22, ry=0.45, dy=8, ramp=fx.GOLD[1:])), 60),
        (pose_frame(arm=(20, 30), sword=220, cape=("cape", 4, 0)), 73),
    ]


def ult():
    raised = dict(arm=(180, 182), sword=2, head="head_shout")
    slam = dict(root=(3, 0), hip=(0, 4), legs=KNEEL, head="head_shout", arm=(320, 350), sword=178,
                sword_clip=GROUND + 1)
    return [
        (pose_frame(hip=(0, 2), legs=CROUCH, head="head_shout", arm=(75, 60), sword=245, cape=("cape", 4, -2)), 80),
        (pose_frame(root=(0, -8), legs=AIR, **raised, cape=("cape", -18, 3), fx_front=excalibur(24, 5, 2)), 80),
        (pose_frame(root=(1, -13), legs=AIR, **raised, cape=("cape", -26, 4), fx_front=excalibur(34, 7, 3)), 80),
        (pose_frame(root=(2, -7), legs=FALLING, arm=(250, 240), sword=70, head="head_shout", cape=("cape", -10, 2),
                    fx_front=combo(smear(-110, -10, 6, r=22, ramp=fx.HOLY), excalibur(30, 6))), 60),
        (pose_frame(**slam, cape=("cape", 10, 2),
                    fx_front=combo(smear(-40, 70, 5, r=22, ramp=fx.HOLY), ground_flash(14, 1))), 80),
        (pose_frame(**slam, cape=("cape", 6, 1), fx_front=ground_flash(9, 2)), 110),
        (pose_frame(root=(2, 0), hip=(0, 2), legs=CROUCH, arm=(330, 345), sword=190, cape=("cape", 3, 0)), 90),
        (pose_frame(root=(1, 0), arm=(10, 15), sword=215), 87),
    ]


def hit():
    return [(pose_frame(hip=(-1, 0), legs=WIDE, head="head_hurt", arm=(25, 30), sword=232, shield_d=(-1, 0),
                        cape=("cape", -4, 1)), 100)]


def dead():
    an = {}
    kneel_pose = dict(hip=(-1, 4), legs=KNEEL, head="head_hurt", arm=(-10, -5), sword=175)
    kneel = pose_frame(anchors_out=an, **kneel_pose, sword_clip=GROUND + 1, cape=("cape", 6, 1))
    planted = sword_only(an["hand"], 175, GROUND + 1)
    frames = [
        (hit()[0][0], 100),
        (pose_frame(hip=(-2, 1), legs=(("B", -5, "plant"), ("C", 2, "plant")), head="head_hurt", arm=(40, 30),
                    sword=225, shield_d=(-1, 1), cape=("cape", -6, 1)), 100),
        (kneel, 120),
        (kneel, 140),
    ]
    # topple backwards about the back knee, then lie flat on the back (head to the left);
    # the sword stays planted where he knelt
    pivot = (FW // 2 - 6, GROUND)
    body = pose_frame(**kneel_pose, show_sword=False)
    for ang in (-35, -65):
        img, pv = px.rotsprite(body, ang, pivot)
        f = px.new(FW, FH)
        px.paste(f, img, pivot[0] - pv[0], pivot[1] - pv[1])
        f = _settle(f)
        f.alpha_composite(planted)
        frames.append((f, 100))
    flat = pose_frame(head="head_hurt", arm=(20, 10), show_sword=False, cape=("cape", 0, 0))
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
