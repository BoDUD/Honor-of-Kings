"""Pixel parts for Arthur (亚瑟). Each part is an ASCII grid; one character = one pixel.

Palette keys are shared by every part. '.' is transparent. The external 1px outline is added
automatically after compositing, so parts only contain fill colours and interior lines.
"""

PALETTE = {
    "K": (20, 18, 32),      # outline / deepest line
    # hair (blond)
    "h": (255, 244, 176), "i": (243, 201, 79), "j": (207, 150, 46), "k": (138, 90, 32),
    # skin
    "s": (247, 212, 180), "t": (225, 166, 133), "u": (178, 112, 86),
    # eye
    "E": (40, 72, 150), "w": (255, 255, 255),
    # silver armour
    "a": (244, 246, 251), "b": (204, 212, 226), "c": (150, 161, 184), "d": (94, 102, 128),
    # gold trim
    "G": (255, 240, 160), "g": (239, 192, 73), "f": (195, 135, 43), "e": (122, 75, 27),
    # red accents
    "R": (224, 70, 61), "r": (156, 35, 50),
    # navy undersuit / shield face
    "N": (75, 92, 146), "n": (41, 49, 90),
    # holy blade
    "B": (238, 242, 255), "V": (133, 148, 230), "v": (74, 79, 164),
    # boots / grip leather
    "L": (122, 74, 44), "l": (74, 42, 26),
}

# anchor = (x, y) inside the grid that is attached to the parent's socket
# 3/4 face looking right: near eye 2x2 (lash row + iris/glint), far eye 1px, stern brows,
# nose bump on the silhouette, mouth, ear on the back side, shaded jaw.
HEAD = dict(anchor=(7, 13), grid=[
    ".....h..i.h....",
    "...hiihiihih...",
    "..hiiihiiiiih..",
    ".jiiiihiiiiiiih",
    ".jiiiiiihiiiiij",
    "jjiijiiiijiiiij",
    "kjjjjisjjsijjij",
    "kjjtsskkksssks.",
    "kjjtssKKsssKss.",
    "kjuttsEwsssEst.",
    "kjuttssssssssst",
    ".kjutsssssuusst",
    "..kjutsssssssu.",
    "...kuuttttttu..",
])

TORSO = dict(anchor=(7, 0), grid=[
    "....dcbbbc....",
    "..fgcbaabbgf..",
    ".fgGcbaaabbGgf",
    ".egfdcbgGbcfge",
    "..edcbgRRgbcd.",
    "..ddcbggggbcd.",
    "...dccbbbccd..",
    "...efggggfge..",
    "...rRRRrRRRr..",
    "....rRRrRRr...",
])

LEGS = {
    "stand": dict(anchor=(7, 0), grid=[
        "....nNNNNNn...",
        "....nNNnNNn...",
        "...dcbn.ncbd..",
        "...dcb...dcb..",
        "...dcb...dcb..",
        "...gfb...gfb..",
        "...dcb...dcb..",
        "...dcb...dcb..",
        "..ddcb..ddcb..",
        "..dcbba.dcbba.",
        ".ddccba.dccbba",
        ".llllll.llllll",
    ]),
    "stride_a": dict(anchor=(7, 0), grid=[
        "....nNNNNNn...",
        "...nNNNnNNNn..",
        "..dcbn...ncbd.",
        "..dcb.....dcb.",
        ".dcb.......dcb",
        ".gfb.......gfb",
        "dcb.........dc",
        "dcb........dcb",
        "dcbba......dcb",
        "llll......dcbba",
        "..........llll.",
        "...............",
    ]),
    "stride_b": dict(anchor=(7, 0), grid=[
        "....nNNNNNn...",
        "....nNNnNNn...",
        "....dcbncbd...",
        "....dcb.dcb...",
        "...dcb..dcb...",
        "...gfb...gfb..",
        "...dcb...dcb..",
        "..dcb.....dcb.",
        "..dcbba...dcbb",
        "..llll....llll",
        "..............",
        "..............",
    ]),
    "crouch": dict(anchor=(7, 0), grid=[
        "...nNNNNNNn...",
        "..nNNNnNNNNn..",
        ".dcbn....ncbd.",
        "dcb.......gfb.",
        "gfb........dcb",
        "dcb........dcb",
        "dcbba.....dcbba",
        "llll......lllll",
    ]),
    "tuck": dict(anchor=(7, 0), grid=[
        "...nNNNNNNn...",
        "..nNNNnNNNNn..",
        "..dcbn..ncbd..",
        "...gfb.gfbd...",
        "....dcbdcb....",
        "....dcbba.....",
        "....llll......",
    ]),
}

CAPE = {
    "still": dict(anchor=(12, 0), grid=[
        "...rrRRRRr..",
        "..rrRRRRRr..",
        ".rrRRRRRr...",
        ".rRRRRRr....",
        "rrRRRRr.....",
        "rRRRRr......",
        "rrRRr.......",
        ".rrr........",
    ]),
    "flow": dict(anchor=(12, 0), grid=[
        "....rrRRRRr.",
        "..rrRRRRRRr.",
        "rrRRRRRRRr..",
        "rRRRRRRRr...",
        ".rRRRRRr....",
        "..rrRRr.....",
        "....rr......",
        "............",
    ]),
}

# Tower shield: navy face, gold rim, gold lion head with red eyes (Arthur's signature)
SHIELD = dict(anchor=(1, 3), grid=[
    "..egggge..",
    ".egGGGGge.",
    "egGnNNnGge",
    "egnfggfnge",
    "egNgRgRNge",
    "egNggGgNge",
    "egNfgggfge",
    "egnNfgfNge",
    "egnNNfNNge",
    "egnNNNNNge",
    "egnnNNNnge",
    ".egnnNnge.",
    ".egnnnnge.",
    "..egnnge..",
    "...egge...",
    "....ee....",
])

GAUNTLET = dict(anchor=(1, 1), grid=[
    "bcd",
    "gfd",
    "cdd",
])
