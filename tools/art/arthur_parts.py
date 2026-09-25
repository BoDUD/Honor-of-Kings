"""Arthur (Honor of Kings, default skin) as hand-placed pixel parts for the TFM2 rig.

Reference: official splash + in-game model. Golden blond swept-back hair, blue eyes, gold plate with
big gold pauldrons and silver inner plates, red cape and red tabard, navy underlayer, gold lion-head
shield (red eyes, navy field), silver longsword with a winged gold guard, red gem, violet fuller.

Every grid is the *fill* of a part; px.outline() adds the 1 px near-black outline, so all pivots
and points below are in fill coordinates and get +1 when the part is outlined.
Palette characters are defined in px.PAL.
"""
from px import Part, outline, grid, recolor

HEAD = [
    "......1221....",
    "....3222211...",
    "..443322222111",
    ".4433332222221",
    "44333333222k2.",
    "4443333baa2...",
    "44443k55aa5...",
    "4444bbqqaaq...",
    ".444cbweaae...",
    ".45cbbbaaba...",
    "..55cbbaaca...",
    "...5kcbbba....",
    ".....kccb.....",
]
HEAD_HURT = [  # eyes squeezed (hit / dead)
    "......1221....",
    "....3222211...",
    "..443322222111",
    ".4433332222221",
    "44333333222k2.",
    "4443333baa2...",
    "44443k55aa5...",
    "4444bbaaaaa...",
    ".444cbqqaaq...",
    ".45cbbbaaba...",
    "..55cbbacca...",
    "...5kcbbba....",
    ".....kccb.....",
]
HEAD_SHOUT = [  # battle cry (skills, ult)
    "......1221....",
    "....3222211...",
    "..443322222111",
    ".4433332222221",
    "44333333222k2.",
    "4443333baa2...",
    "44443k5k5a5...",
    "4444bbqqaaq...",
    ".444cbweaae...",
    ".45cbbbaaba...",
    "..55cbbakka...",
    "...5kcbbka....",
    ".....kccb.....",
]
TORSO = [
    "..EDCBCDE..",
    ".ZyxxCxxyZ.",
    "Zyxxxgxxxyz",
    "ZyxxCBCxxyz",
    "ZzyxxCxxyyz",
    "ZzyyxxxyyzZ",
    "EDCCBBBCCDE",
    "otmmCBCmmto",
    "oommDCDmmoo",
]
TASSET = [
    "DCBBCDsDCBBCD",
    "DCBACDsDCABCD",
    "EDCCDtstDCCDE",
    ".EDCDtstDCDE.",
    "..EDttsttDE..",
    ".....utu.....",
]
LEG = [
    "ZyxyZ.",
    "ZyxyZ.",
    "DCBBC.",
    "DBAAB.",
    "EDCCD.",
    "ZyxxZ.",
    "ZyxyZ.",
    "ZzyyZ.",
    "DCBBC.",
    "DCBBBC",
    "EDDDDE",
]
LEG_BENT = [  # knee forward (run passing pose, crouch)
    "ZyxyZ..",
    "ZyxyZZ.",
    ".DCBBC.",
    ".DBAAB.",
    ".EDCCDZ",
    "..ZyxxZ",
    ".ZyxyZ.",
    ".ZzyZ..",
    "DCBBC..",
    "DCBBBC.",
    "EDDDDE.",
]
LEG_KNEEL = [  # shin on the ground, pointing back (left)
    "ZyxyZ....",
    "ZyxyZ....",
    "DCBBC....",
    "DBAAB....",
    "EDCCDyyzZ",
    ".EZyxxyzZ",
    "EDCZzzzZ.",
]
PAUL_N = [
    "..DCCBB..",
    ".DCBBAAB.",
    "DCCBBABBB",
    "DDCCBBBBC",
    "EZzyxxxyZ",
    ".EZzyyyZ.",
]
PAUL_F = [
    ".DCCBB.",
    "DCBBAAB",
    "DDCCBBC",
    "EZzyyyZ",
    ".EZzzZ.",
]
UPPER_ARM = [  # hangs down from the shoulder pivot (top centre)
    "Zyz",
    "Zyx",
    "Zyx",
    "Zzy",
]
FOREARM = [  # gold vambrace + gauntlet, pivot at the elbow (top centre), hand at the bottom
    ".DB.",
    "DCBC",
    "DCBA",
    "DCBB",
    "EDCD",
    ".ED.",
]
SWORD = [
    "..w..",
    ".wx..",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wxy.",
    ".wpy.",
    ".xpz.",
    "BxpzB",
    "BCgCB",
    ".DBD.",
    "..o..",
    "..m..",
    "..o..",
    ".CBC.",
]
SWORD_GRIP = (2, 20)   # where the hand holds it
SWORD_TIP = (2, 0)
SHIELD = [
    "DCBBBBBBBCD",
    "CBAAAAAAABC",
    "CBmmBBBmmBC",
    "CBmBCBCBmBC",
    "CBBCgBgCBBC",
    "CBmBCACBmBC",
    "CBmmBCBmmBC",
    "CBmmmBmmmBC",
    ".CBmmBmmBC.",
    ".CBmmmmmBC.",
    "..CBmmmBC..",
    "..DCmmmCD..",
    "...DCmCD...",
    "....DCD....",
    ".....E.....",
]
CAPE = [
    ".......ssss.",
    "......tsrss.",
    ".....tssrss.",
    ".....tsstss.",
    "....utsstss.",
    "....utsstss.",
    "...uutsstss.",
    "...uutsstss.",
    "...uttsttss.",
    "..uutssttss.",
    "..uutssttss.",
    "..uutsttsss.",
    ".uuttsttsss.",
    ".uuttsttsss.",
    "vuuttsttsss.",
    "vuutttsssst.",
    "vvuuttsstuu.",
    ".vvuuutttuv.",
    "..vvvuuuvv..",
]
CAPE_ATTACH = (10, 0)  # top right of the cape, sits behind the near shoulder

# far-side parts sit in shadow: one step darker, gold stays gold
FAR = {"x": "y", "y": "z", "z": "Z", "A": "B", "B": "C", "C": "D", "n": "m", "m": "o", "s": "t", "t": "u"}


def part(rows, pivot, points=None, darken=False):
    """Outlined Part from fill rows; pivot/points given in fill coordinates."""
    img = outline(grid(rows), grow_canvas=True)
    if darken:
        img = recolor(img, FAR)
    p = Part.__new__(Part)
    p.img = img
    p.pivot = (pivot[0] + 1, pivot[1] + 1)
    p.points = {k: (v[0] + 1, v[1] + 1) for k, v in (points or {}).items()}
    return p


def build():
    """All rig parts, outlined, with pivots at their joints."""
    return {
        "head": part(HEAD, (7, 12)),
        "head_hurt": part(HEAD_HURT, (7, 12)),
        "head_shout": part(HEAD_SHOUT, (7, 12)),
        "torso": part(TORSO, (5, 8), {"neck": (6, 0), "sh_n": (1, 1), "sh_f": (9, 1)}),
        "tasset": part(TASSET, (6, 0)),
        "leg_n": part(LEG, (2, 0)),
        "leg_f": part(LEG, (2, 0), darken=True),
        "leg_n_bent": part(LEG_BENT, (2, 0)),
        "leg_f_bent": part(LEG_BENT, (2, 0), darken=True),
        "leg_n_kneel": part(LEG_KNEEL, (2, 0)),
        "leg_f_kneel": part(LEG_KNEEL, (2, 0), darken=True),
        "paul_n": part(PAUL_N, (4, 2)),
        "paul_f": part(PAUL_F, (3, 2)),
        "upper_arm": part(UPPER_ARM, (1, 0), {"elbow": (1, 3)}),
        "forearm": part(FOREARM, (1, 0), {"hand": (1, 4)}),
        "sword": part(SWORD, SWORD_GRIP, {"tip": SWORD_TIP}),
        "shield": part(SHIELD, (5, 6)),
        "cape": part(CAPE, CAPE_ATTACH),
    }
