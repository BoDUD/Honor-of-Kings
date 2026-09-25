"""Pose Arthur's pixel parts into animation frames.

A pose is a dict of joint settings (see DEFAULT). Positions are in pixels relative to the hip
(the bottom centre of the breastplate); angles are clockwise on screen in degrees:
  limbs: 0 = hanging down, 90 = pointing back (left), -90 = pointing forward (right)
  sword: 0 = pointing up, 90 = forward (right), 180 = down, 225 = down-back
"""
import math

import px
from arthur_parts import build

FW, FH = 111, 135          # frame size (odd so the pivot pixel is the centre)
CX = FW // 2               # hip column = pivot column
GROUND = FH // 2 + 11      # last row of the soles (bottom edge = centre + 11.5)
HIP_Y = GROUND - 16        # hip row when standing

PARTS = build()

# joint positions relative to the hip in the neutral stance
J = {
    "torso": (0, 0), "tasset": (-1, 0),
    "leg_n": (-2, 5), "leg_f": (5, 5),
    "neck": (1, -8), "head": (1, -10),
    "paul_n": (-6, -8), "paul_f": (6, -8),
    "shoulder": (-7, -6),
    "shield": (10, 0),
    "cape": (-7, -8),
}

DEFAULT = dict(
    root=(0, 0),            # whole body offset (jumps, knock-back)
    hip=(0, 0),             # hip offset (crouch = +y)
    up=(0, 0),              # upper body offset relative to the hip (lean / breathing)
    head="head", head_d=(0, 0),
    leg_n=("leg_n", 0, (0, 0)), leg_f=("leg_f", 0, (0, 0)),
    arm=(0, 0),             # (upper arm angle, forearm angle)
    sword=225,
    sword_part="sword",
    shield_d=(0, 0), shield_a=0,
    cape=("cape", 0, 0),    # (part, rotation, hem sway px)
    show_sword=True,
    sword_clip=None,        # erase sword pixels below this row (blade driven into the ground)
    fx_back=None, fx_front=None,   # callables(frame, anchors) for effect pixels
)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(*vs):
    return (sum(v[0] for v in vs), sum(v[1] for v in vs))


def sway(img, amount, pivot_y):
    """Shift rows below pivot_y sideways, more toward the hem (cloth sway / wind)."""
    if not amount:
        return img
    out = px.new(img.width + 8, img.height)
    h = img.height
    for y in range(h):
        t = max(0.0, (y - pivot_y) / max(1, h - pivot_y))
        dx = int(round(amount * t * t))
        out.paste(img.crop((0, y, img.width, y + 1)), (4 + dx, y))
    return out


def pose_frame(anchors_out=None, **kw):
    P = dict(DEFAULT)
    P.update(kw)
    f = px.new(FW, FH)
    hip = add((CX, HIP_Y), P["root"], P["hip"])
    up = add(hip, P["up"])
    anchors = {"hip": hip, "up": up}

    def at(base, key, d=(0, 0)):
        return add(base, J[key], d)

    def put(name, pos, angle=0.0, flip=False):
        p = PARTS[name]
        px.place(f, p.img, p.pivot, pos[0], pos[1], angle=angle, flip=flip)

    # joint positions first, so effects drawn behind the body can use them
    ua, fa = P["arm"]
    sh = at(up, "shoulder")
    upa, fore = PARTS["upper_arm"], PARTS["forearm"]
    elbow = add(sh, rot((upa.points["elbow"][0] - upa.pivot[0], upa.points["elbow"][1] - upa.pivot[1]), ua))
    hand = add(elbow, rot((fore.points["hand"][0] - fore.pivot[0], fore.points["hand"][1] - fore.pivot[1]), fa))
    anchors.update(shoulder=sh, elbow=elbow, hand=hand)
    sw = PARTS[P["sword_part"]]
    anchors["tip"] = add(hand, rot((sw.points["tip"][0] - sw.pivot[0], sw.points["tip"][1] - sw.pivot[1]), P["sword"]))

    if P["fx_back"]:
        P["fx_back"](f, anchors)

    # cape (behind everything), hangs from behind the near shoulder
    cname, crot, csway = P["cape"]
    cp = PARTS[cname]
    cimg = sway(cp.img, csway, 4) if csway else cp.img
    cpiv = (cp.pivot[0] + (4 if csway else 0), cp.pivot[1])
    px.place(f, cimg, cpiv, *at(up, "cape"), angle=crot)

    # legs
    for key in ("leg_f", "leg_n"):
        name, ang, d = P[key]
        put(name, at(hip, key, d), ang)

    put("torso", at(up, "torso"))
    put("tasset", at(hip, "tasset", (P["up"][0] // 2, 0)))
    put("paul_f", at(up, "paul_f"))
    put("shield", at(up, "shield", P["shield_d"]), P["shield_a"])
    put(P["head"], at(up, "head", P["head_d"]))

    # sword arm: shoulder -> elbow -> hand -> sword
    put("upper_arm", sh, ua)
    put("paul_n", at(up, "paul_n"))
    if P["show_sword"]:
        if P["sword_clip"] is None:
            put(P["sword_part"], hand, P["sword"])
        else:
            f.alpha_composite(sword_only(hand, P["sword"], P["sword_clip"]))
    put("forearm", elbow, fa)

    if P["fx_front"]:
        P["fx_front"](f, anchors)
    if anchors_out is not None:
        anchors_out.update(anchors)
    return f


def sword_only(hand, angle, clip=None):
    """Just the sword, gripped at `hand`; `clip` hides the part below that row (stuck in the ground)."""
    f = px.new(FW, FH)
    p = PARTS["sword"]
    px.place(f, p.img, p.pivot, hand[0], hand[1], angle=angle)
    if clip is not None:
        f.paste((0, 0, 0, 0), (0, int(clip) + 1, FW, FH))
    return f
