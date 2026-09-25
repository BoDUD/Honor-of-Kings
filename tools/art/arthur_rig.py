"""Pose Arthur's pixel parts into animation frames.

A pose is a dict of settings (see DEFAULT). Positions are in pixels; angles are clockwise on
screen in degrees:
  arm:   0 = hanging down, 90 = pointing back (left), 180 = up, 270 = pointing forward (right)
  sword: 0 = pointing up, 90 = forward (right), 180 = down, 225 = down-back

The body is locked together at the waist: `hip` moves the whole upper body *and* the tasset, so
the torso never slides over the hips. Legs keep one shape and length: a leg is given by where its
joint sits under the hip and where its foot stands, and is slanted to connect the two
(arthur_parts.slanted_leg), so the knee is always visible and legs never shrink or bend out of
shape. Keep hip y at 0 except for kneeling (the kneel has its own leg drawings).
"""
import math

import px
from arthur_parts import build, slanted_leg

FW, FH = 111, 135          # frame size (odd so the pivot pixel is the centre)
CX = FW // 2               # hip column = pivot column
GROUND = FH // 2 + 11      # outline row under the soles (bottom edge = centre + 11.5)
HIP_Y = GROUND - 16        # hip row when standing (bottom row of the breastplate)
TASSET_BOTTOM = 6          # last tasset fill row, relative to the hip

PARTS = build()

# attachment points relative to the hip
J = {
    "torso": (0, 0), "tasset": (-1, 2),
    "head": (1, -10),
    "paul_n": (-6, -8), "paul_f": (6, -8),
    "shoulder": (-7, -6),
    "shield": (10, 0),
    "cape": (-7, -8),
}
HANG_Y = 4                 # hanging legs: joint this far below the hip
# a leg: (kind, joint x from the hip, foot x from the standing hip, lift)
#   kind "S": the one leg shape, slanted from joint to foot; lift = px the foot is off the ground,
#             or "hang" (airborne: joint follows the hip, foot x is then relative to the joint)
#   kind "kneel_back" / "kneel_front": kneeling drawings, placed at the joint, sole on the ground
STAND_LEGS = (("S", -3, -3, 0), ("S", 3, 3, 0))

DEFAULT = dict(
    root=(0, 0),            # whole-body offset, ground included (jumps use hanging legs)
    hip=(0, 0),             # hip offset: lean (x) and crouch (+y); upper body + tasset follow
    breath=0,               # shoulders, head, arm, shield and cape only (idle breathing)
    head="head", head_d=(0, 0),
    legs=STAND_LEGS,        # (near, far), see STAND_LEGS
    arm=(0, 0),             # (upper arm angle, forearm angle)
    sword=230,
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
    base = add((CX, HIP_Y), P["root"])          # standing hip (feet reference)
    hip = add(base, P["hip"])
    ground = GROUND + P["root"][1]
    up = add(hip, (0, P["breath"]))             # things that breathe
    anchors = {"hip": hip, "base": base, "ground": ground}

    def at(origin, key, d=(0, 0)):
        return add(origin, J[key], d)

    def put(name, pos, angle=0.0):
        p = PARTS[name]
        px.place(f, p.img, p.pivot, pos[0], pos[1], angle=angle)

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

    # legs: far first, near in front
    for kind, jdx, fdx, lift in reversed(P["legs"]):
        if kind == "S" and lift == "hang":
            img, pv = slanted_leg(fdx)
            px.paste(f, img, hip[0] + jdx - pv[0], hip[1] + HANG_Y - pv[1])
            continue
        if kind == "S":
            img, pv = slanted_leg((base[0] + fdx) - (hip[0] + jdx), drop=lift)
            x = hip[0] + jdx - pv[0]
        else:
            p = PARTS["leg_" + kind]
            img, pv, lift = p.img, p.pivot, 0
            x = hip[0] + jdx - pv[0]
        y = ground - lift - (img.height - 1)
        assert y + 1 <= hip[1] + TASSET_BOTTOM + 1, f"leg {kind} leaves a gap under the tasset"
        px.paste(f, img, x, y)

    put("tasset", at(hip, "tasset"))
    put("torso", at(hip, "torso"))
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
