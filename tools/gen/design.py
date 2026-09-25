"""Generate Arthur character-design candidates with SDXL + pixel-art LoRA.

    D:\\hok_ai\\venv\\Scripts\\python tools/gen/design.py --out D:\\hok_ai\\out\\design --n 8

Writes full-size renders, 1/8 pixel versions (the LoRA's native pixel grid) and a contact sheet.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from sd_common import ARTHUR, NEGATIVE, block_downsample, key_out, load_txt2img  # noqa: E402

BG = (150, 150, 150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--lora", type=float, default=1.1)
    ap.add_argument("--extra", default="", help="extra prompt text")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pipe = load_txt2img(args.lora)
    prompt = ARTHUR + ", plain flat gray background" + (", " + args.extra if args.extra else "")
    tiles = []
    for k in range(args.n):
        seed = args.seed + k
        g = torch.Generator("cuda").manual_seed(seed)
        img = pipe(prompt=prompt, negative_prompt=NEGATIVE, width=1024, height=1024, num_inference_steps=args.steps,
                   guidance_scale=args.cfg, generator=g).images[0]
        img.save(os.path.join(args.out, f"design_{seed}.png"))
        px = block_downsample(img, 8)
        px.save(os.path.join(args.out, f"design_{seed}_px.png"))
        cut = key_out(px, px.getpixel((0, 0)), tol=36)
        cut.save(os.path.join(args.out, f"design_{seed}_cut.png"))
        tile = Image.new("RGB", (128 * 3, 128 * 3 + 16), (30, 30, 30))
        tile.paste(px.resize((128 * 3, 128 * 3), Image.NEAREST), (0, 16))
        ImageDraw.Draw(tile).text((4, 2), f"seed {seed}", fill=(255, 255, 255))
        tiles.append(tile)
        print("done", seed, flush=True)
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tiles[0].width, rows * tiles[0].height), (0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * t.width, (i // cols) * t.height))
    sheet.save(os.path.join(args.out, "contact.png"))
    print("contact sheet", sheet.size)


if __name__ == "__main__":
    main()
