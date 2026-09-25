"""Pull Garen's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_garen.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Reads (never writes) Game/DATA/FINAL/Champions/Garen.wad.client and Garen.<lang>.wad.client,
resolves the base-skin Wwise events below to their media, decodes them with vgmstream and writes
mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability
icons to league/icons/. Voice language: zh_CN (Chinese voice, from the Tencent client) by default.
"""
import argparse
import io
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "league")
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/garen/skins/base/garen_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/garen/skins/base/garen_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_garen_sfx_attack_hit": ("Play_sfx_Garen_GarenBasicAttack_OnHit", 63889480, 0.9, -3),
    "league_garen_sfx_q_cast": ("Play_sfx_Garen_GarenQ_OnCast", 787993323, 1.6, -3),
    "league_garen_sfx_q_hit": ("Play_sfx_Garen_GarenQAttack_OnCast", 381621008, 1.5, -2),
    "league_garen_sfx_w": ("Play_sfx_Garen_GarenW_OnCast", 365103885, 1.6, -4),
    "league_garen_sfx_e_cast": ("Play_sfx_Garen_GarenE_OnCast", 754874955, 1.2, -4),
    "league_garen_sfx_e_spin": ("Play_sfx_Garen_GarenE_OnBuffActivate", 244591647, 3.2, -3),
    "league_garen_sfx_e_hit": ("Play_sfx_Garen_GarenE_hit", 417478327, 0.9, -6),
    "league_garen_sfx_r_cast": ("Play_sfx_Garen_GarenR_OnCast", 668691324, 2.4, -3),
    "league_garen_sfx_r_hit": ("Play_sfx_Garen_GarenR_OnHit", 99117749, 2.8, -1),
    "league_garen_vo_q": ("Play_vo_Garen_GarenQ_cast3D", 285237030, 2.0, -2),
    "league_garen_vo_q_hit": ("Play_vo_Garen_GarenQAttack_cast3D", 1486823820, 2.0, -2),
    "league_garen_vo_e": ("Play_vo_Garen_GarenE_cast3D", 1881896344, 2.0, -2),
    "league_garen_vo_r": ("Play_vo_Garen_GarenR_cast3D", 1924380092, 2.5, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_garen_skill": "ASSETS/Characters/Garen/HUD/Icons2D/Garen_Q.dds",
    "league_garen_skill2": "ASSETS/Characters/Garen/HUD/Icons2D/Garen_E1.dds",
    "league_garen_ult": "ASSETS/Characters/Garen/HUD/Icons2D/Garen_R.dds",
}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def decode(wem, vgmstream):
    """WEM bytes -> (sample rate, mono float32 samples) via vgmstream."""
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, "a.wem"), os.path.join(tmp, "a.wav")
        with open(src, "wb") as f:
            f.write(wem)
        subprocess.run([vgmstream, "-o", dst, src], check=True, capture_output=True)
        with wave.open(dst) as w:
            sr, ch = w.getframerate(), w.getnchannels()
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).mean(1)
    return sr, x.astype(np.float32) / 32768


def finish(x, sr, max_s, peak_db):
    """Trim leading silence, cap the length with a fade, normalise the peak."""
    idx = np.nonzero(np.abs(x) > 0.01)[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.005 * sr)):]
    x = x[:int(max_s * sr)].copy()
    fade = min(len(x), int(0.08 * sr))
    x[-fade:] *= np.linspace(1, 0, fade)
    x *= (10 ** (peak_db / 20)) / max(1e-6, float(np.abs(x).max()))
    return (np.clip(x, -1, 1) * 32767).astype(np.int16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", required=True)
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Garen.wad.client"))
    vo_wad = Wad(os.path.join(champs, f"Garen.{args.lang}.wad.client"))
    sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
    media = dict(bnk_media(sfx_audio))
    media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
    banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                        vo_wad.read_path(VO_BANK + "events.bnk")], media)

    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    for name, (event, mid, max_s, peak) in CLIPS.items():
        variants = banks.event_media(event)
        if mid not in variants:
            sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
        sr, x = decode(media[mid], args.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
