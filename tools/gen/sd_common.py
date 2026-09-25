"""Shared Stable Diffusion XL setup for the HoK sprite pipeline (runs in D:\\hok_ai\\venv).

Models (downloaded once into D:\\hok_ai\\hf):
  stabilityai/stable-diffusion-xl-base-1.0 (fp16), madebyollin/sdxl-vae-fp16-fix,
  nerijs/pixel-art-xl LoRA, xinsir/controlnet-union-sdxl-1.0 (promax)
"""
import os

os.environ.setdefault("HF_HOME", r"D:\hok_ai\hf")
os.environ.setdefault("HF_HUB_OFFLINE", "1")  # everything is already downloaded

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402

BASE = "stabilityai/stable-diffusion-xl-base-1.0"
VAE = "madebyollin/sdxl-vae-fp16-fix"
LORA = ("nerijs/pixel-art-xl", "pixel-art-xl.safetensors")

ARTHUR = ("pixel art, game sprite of Arthur from Honor of Kings, chibi proportions, full body, "
          "short spiky golden blond hair, young heroic knight, blue eyes, "
          "white and silver plate armor with ornate gold trim, large gold shoulder pauldrons, red cape, "
          "big golden shield with a lion head emblem held in front, longsword with a violet glowing blade, "
          "facing right, three-quarter view, clean black outline, limited palette, crisp pixels")
NEGATIVE = ("blurry, soft, 3d render, photo, realistic, painting, text, watermark, logo, signature, frame, border, "
            "multiple characters, cropped, cut off, deformed, extra limbs, extra weapons, jpeg artifacts, "
            "gradient background, scenery, shadow on ground")


def load_txt2img(lora_scale=1.0):
    from diffusers import AutoencoderKL, StableDiffusionXLPipeline
    vae = AutoencoderKL.from_pretrained(VAE, torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(BASE, vae=vae, torch_dtype=torch.float16, variant="fp16",
                                                     use_safetensors=True)
    pipe.load_lora_weights(LORA[0], weight_name=LORA[1], adapter_name="pixel")
    pipe.set_adapters(["pixel"], adapter_weights=[lora_scale])
    pipe.to("cuda")
    pipe.enable_vae_tiling()
    return pipe


def load_img2img(lora_scale=1.0):
    from diffusers import StableDiffusionXLImg2ImgPipeline
    t2i = load_txt2img(lora_scale)
    return StableDiffusionXLImg2ImgPipeline(**t2i.components)


def block_downsample(img, block):
    """Pixel-grid aware downscale: each block becomes its most common colour (keeps hard pixels)."""
    a = np.asarray(img.convert("RGB"))
    h, w = a.shape[0] // block, a.shape[1] // block
    out = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        for x in range(w):
            tile = a[y * block:(y + 1) * block, x * block:(x + 1) * block].reshape(-1, 3)
            core = tile[len(tile) // 4: -len(tile) // 4] if len(tile) > 8 else tile  # ignore block edges
            vals, counts = np.unique(core // 8, axis=0, return_counts=True)
            out[y, x] = vals[np.argmax(counts)] * 8 + 4
    return Image.fromarray(out)


def key_out(img, bg_rgb, tol=40):
    """Make pixels close to the flat background colour transparent (flood from the border)."""
    a = np.asarray(img.convert("RGB")).astype(int)
    h, w, _ = a.shape
    close = (np.abs(a - np.array(bg_rgb)).sum(axis=2) <= tol)
    mask = np.zeros((h, w), bool)
    stack = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
    while stack:
        y, x = stack.pop()
        if 0 <= y < h and 0 <= x < w and not mask[y, x] and close[y, x]:
            mask[y, x] = True
            stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    rgba = np.dstack([a.astype(np.uint8), np.where(mask, 0, 255).astype(np.uint8)])
    return Image.fromarray(rgba, "RGBA")
