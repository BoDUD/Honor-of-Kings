"""Arthur (Honor of Kings, default skin) as hand-placed pixel parts for the TFM2 rig.

Reference: official splash + in-game model. Golden blond swept-back hair, blue eyes, gold plate with
big gold pauldrons and silver inner plates, red cape and red tabard, navy underlayer, gold lion-head
shield (red eyes, navy field), silver longsword with a winged gold guard, red gem, violet fuller.

Every grid is the *fill* of a part; px.outline() adds the 1 px near-black outline, so all pivots
and points below are in fill coordinates and get +1 when the part is outlined.
Palette characters are defined in px.PAL.
"""
from px import Part, grid, outline

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
TASSET = [  # gold skirt plates over the hips, red tabard in front
    "DCBACDsDCABCD",
    "EDCCDtstDCCDE",
    ".EDCDtstDCDE.",
    "..EDttsttDE..",
    ".....utu.....",
]
# Legs: every pose is drawn, not rotated (rotating 5 px limbs breaks them). Pivot = hip joint at
# the top; the top rows hide under the tasset. Same grids and colours for the near and far leg.
LEGS = {
    "S": ([  # standing
        "ZyxyZ.",
        "ZyxyZ.",
        "ZyxyZ.",
        "ZyxyZ.",
        "DCBBC.",
        "DBAAB.",
        "EDCCD.",
        "ZyxxZ.",
        "ZyxyZ.",
        "DCBBC.",
        "DCBBBC",
        "EDDDDE",
    ], (2, 0)),
    "F": ([  # front leg of a stride / lunge: thigh forward, shin upright
        "ZyxyZ...",
        ".ZyxyZ..",
        "..ZyxyZ.",
        "..DCBBC.",
        "..DBAAB.",
        "..EDCCD.",
        "..ZyxxZ.",
        "..ZyxyZ.",
        "..DCBBC.",
        "..DCBBBC",
        "..EDDDDE",
    ], (2, 0)),
    "B": ([  # back leg of a stride / lunge: straight, reaching back
        "....ZyxyZ",
        "...ZyxyZ.",
        "...ZyxyZ.",
        "..DCBBC..",
        "..DBAAB..",
        ".EDCCD...",
        ".ZyxxZ...",
        "ZyxyZ....",
        "DCBBC....",
        "DCBBBC...",
        "EDDDDE...",
    ], (6, 0)),
    "P": ([  # passing / lifted leg
        "ZyxyZ..",
        "ZyxyZ..",
        ".DCBBC.",
        ".DBAAB.",
        ".EDCCD.",
        ".ZyxxZ.",
        "ZyxyZ..",
        "DCBBC..",
        "EDDDDE.",
    ], (2, 0)),
    "C": ([  # crouch: knee forward, foot under the body
        "ZyxyZ...",
        ".ZyxyZ..",
        "..DCBBC.",
        "..DBAAB.",
        "..EDCCD.",
        ".ZyxxZ..",
        ".ZyxyZ..",
        "DCBBC...",
        "DCBBBC..",
        "EDDDDE..",
    ], (2, 0)),
    "K": ([  # kneel: knee on the ground, shin lying back
        "....ZyxyZ",
        "....ZyxyZ",
        "....ZyxyZ",
        "....DCBBC",
        "DZzyyDBAAB",
        "EDZzzEDCCD",
    ], (6, 0)),
    "T": ([  # tucked in the air
        "ZyxyZ...",
        ".ZyxyyZ.",
        "..DCBBC.",
        "..DBAAB.",
        "..EDCCD.",
        ".ZyxZ...",
        "DCBBC...",
        "EDDDE...",
    ], (2, 0)),
}
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


def part(rows, pivot, points=None):
    """Outlined Part from fill rows; pivot/points given in fill coordinates.

    Near and far limbs share grids and colours; the outline alone separates them.
    """
    img = outline(grid(rows), grow_canvas=True)
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
        **{"leg_" + k: part(rows, pivot) for k, (rows, pivot) in LEGS.items()},
        "paul_n": part(PAUL_N, (4, 2)),
        "paul_f": part(PAUL_F, (3, 2)),
        "upper_arm": part(UPPER_ARM, (1, 0), {"elbow": (1, 3)}),
        "forearm": part(FOREARM, (1, 0), {"hand": (1, 4)}),
        "sword": part(SWORD, SWORD_GRIP, {"tip": SWORD_TIP}),
        "shield": part(SHIELD, (5, 6)),
        "cape": part(CAPE, CAPE_ATTACH),
    }
