"""Preview images for the README / workshop page: every frame, and a skill showcase GIF.

    python tools/art/showcase.py            # writes docs/preview/*
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import arthur_anim  # noqa: E402
import arthur_fx  # noqa: E402
import px  # noqa: E402
from preview import ARENA, contact  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "docs", "preview")

DUMMY = [  # straw training dummy (the target in the showcase)
    "....5555....",
    "...544445...",
    "...543345...",
    "...544445...",
    "....5445....",
    ".5444444445.",
    "54433333344.",
    ".5.544445.5.",
    "...5ssss5...",
    "...5s11s5...",
    "...5ssss5...",
    "...544445...",
    "....5445....",
    ".....55.....",
    ".....55.....",
    ".....55.....",
    "...555555...",
]


def dummy_frame(shake=0):
    img = px.outline(px.grid(DUMMY), grow_canvas=True)
    f = px.new(41, 41)
    px.paste(f, img, 20 - img.width // 2 + shake, 20 + 11 - (img.height - 1))
    return f


class Stage:
    """Units are drawn with their frame centre on (x, y) = pivot, like the game."""

    def __init__(self, w=210, h=124):
        self.w, self.h = w, h
        self.frames = []

    def shot(self, layers, ms):
        img = Image.new("RGBA", (self.w, self.h), ARENA)
        for layer, x, y in layers:
            px.paste(img, layer, x - layer.width // 2, y - layer.height // 2)
        self.frames.append((img, ms))

    def save_gif(self, path, scale=3):
        seq = [px.zoom(im, scale, ARENA).convert("RGB") for im, _ in self.frames]
        seq[0].save(px.lp(path), save_all=True, append_images=seq[1:],
                    duration=[ms for _, ms in self.frames], loop=0, disposal=2)


def main():
    os.makedirs(px.lp(OUT), exist_ok=True)
    anims = dict(arthur_anim.build())
    fx = {name: dict(tags) for name, tags in arthur_fx.build().items()}
    contact(list(anims.items()), os.path.join(OUT, "arthur_frames.png"))

    s = Stage()
    Y = 80
    DX = 150                 # dummy
    MX = DX - 28             # melee spot next to the dummy
    dummy = dummy_frame()

    def body(tag, i):
        return anims[tag][i][0]

    def loop_fx(name, tag, k):
        seq = fx[name][tag]
        return seq[k % len(seq)][0]

    # idle
    for im, ms in anims["idle"]:
        s.shot([(dummy, DX, Y), (im, MX, Y)], ms)
    # two basic attacks, the yellow-white hit flash on the dummy when the swing lands
    for _ in range(2):
        hit = 0
        for i, (im, ms) in enumerate(anims["attack"]):
            layers = [(dummy_frame(1 if i == 4 else 0), DX, Y), (im, MX, Y)]
            if i >= 3 and hit < len(fx["hok_arthur_slash"]["spark"]):
                layers.append((fx["hok_arthur_slash"]["spark"][hit][0], DX, Y))
                hit += 1
            s.shot(layers, ms)
    # skill 1: back off, dash in, golden cross slash, oath aura
    for i, (im, ms) in enumerate(anims["run"]):
        s.shot([(dummy, DX, Y), (im.transpose(Image.FLIP_LEFT_RIGHT), MX - i * 6, Y)], ms)
    x = MX - 48
    for i, (im, ms) in enumerate(anims["skill"]):
        if i in (1, 2, 3):
            x += 16
        layers = [(dummy_frame(1 if i >= 4 else 0), DX, Y), (im, x, Y)]
        s.shot(layers, ms)
    for k, (fr, ms) in enumerate(fx["hok_arthur_slash"]["hit"]):
        s.shot([(dummy_frame(1 if k < 3 else 0), DX, Y), (loop_fx("hok_arthur_oath", "loop", k), x, Y),
                (body("idle", k % 6), x, Y), (fr, DX, Y)], ms)
    # skill 2: raise the sword, three flaming shields orbit
    for i, (im, ms) in enumerate(anims["skill2"]):
        layers = [(dummy, DX, Y), (im, x, Y)]
        if i >= 2:
            layers.append((loop_fx("hok_arthur_whirl", "loop", i), x, Y))
        s.shot(layers, ms)
    for k in range(20):
        s.shot([(dummy_frame(k % 4 == 0), DX, Y), (body("idle", (k // 2) % 6), x, Y),
                (loop_fx("hok_arthur_whirl", "loop", k), x, Y)], 50)
    # ult: leap onto the dummy, blade of light, holy seal
    for i, (im, ms) in enumerate(anims["run"][:4]):
        s.shot([(dummy, DX, Y), (im.transpose(Image.FLIP_LEFT_RIGHT), x - i * 10, Y)], ms)
    x0 = x = x - 40
    impact = 0
    for i, (im, ms) in enumerate(anims["ult"]):
        if i in (1, 2, 3):
            x += (MX - x0) / 3
        layers = []
        if i >= 4:
            layers.append((loop_fx("hok_arthur_seal", "loop", i), DX, Y))
        layers += [(dummy_frame(1 if i in (4, 5) else 0), DX, Y), (im, int(x), Y)]
        if i >= 4 and impact < len(fx["hok_arthur_ult_impact"]["impact"]):
            layers.append((fx["hok_arthur_ult_impact"]["impact"][impact][0], DX, Y))
            impact += 1
        s.shot(layers, ms)
    for k in range(18):
        layers = [(loop_fx("hok_arthur_seal", "loop", k), DX, Y), (dummy_frame(k % 6 == 0), DX, Y),
                  (body("idle", (k // 2) % 6), int(x), Y)]
        if impact < len(fx["hok_arthur_ult_impact"]["impact"]):
            layers.append((fx["hok_arthur_ult_impact"]["impact"][impact][0], DX, Y))
            impact += 1
        s.shot(layers, 90)
    s.save_gif(os.path.join(OUT, "arthur_showcase.gif"))
    print("wrote", OUT, len(s.frames), "showcase frames")


if __name__ == "__main__":
    main()
