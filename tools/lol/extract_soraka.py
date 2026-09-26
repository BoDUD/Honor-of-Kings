"""Pull Soraka's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_soraka.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Soraka.wad.client and Soraka.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

The champion bins name some events with a trailing digit (SorakaBasicAttack_OnHit1,
SorakaW_OnCast6, SorakaQMissile_OnMissileLaunch4); the banks hold them without it. Soraka has a
cast line only for Wish, so Starcall borrows one of her attack-command lines.
"""
import argparse
import io
import os
import sys
import wave

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "league")
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/soraka/skins/base/soraka_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/soraka/skins/base/soraka_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_soraka_sfx_attack_shot": ("Play_sfx_Soraka_SorakaBasicAttack_OnMissileLaunch", 26639426, 0.7, -6),
    "league_soraka_sfx_attack_hit": ("Play_sfx_Soraka_SorakaBasicAttack_OnHit", 37815644, 0.5, -6),
    "league_soraka_sfx_q_cast": ("Play_sfx_Soraka_SorakaQ_OnCast", 383551799, 1.2, -4),
    "league_soraka_sfx_q_hit": ("Play_sfx_Soraka_SorakaQMissile_OnHitLocation", 493343696, 1.2, -3),
    "league_soraka_sfx_q_heal": ("Play_sfx_Soraka_SorakaQ_hit", 138839411, 1.0, -6),
    "league_soraka_sfx_w_cast": ("Play_sfx_Soraka_SorakaW_OnCast", 142778807, 1.2, -4),
    "league_soraka_sfx_e_cast": ("Play_sfx_Soraka_SorakaE_OnCast", 19021882, 0.8, -4),
    "league_soraka_sfx_e_root": ("Play_sfx_Soraka_SorakaESnare_OnBuffActivate", 352306735, 1.2, -4),
    "league_soraka_sfx_r_cast": ("Play_sfx_Soraka_SorakaR_OnCast", 600122912, 1.5, -3),
    "league_soraka_sfx_r_heal": ("Play_sfx_Soraka_Wish_hit", 215907285, 1.6, -5),
    "league_soraka_vo_q": ("Play_vo_Soraka_Attack2DGeneral", 2022130076, 1.6, -2),
    "league_soraka_vo_r": ("Play_vo_Soraka_SorakaR_cast3D", 1070538040, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Equinox rides on Starcall, Salvation on Astral Infusion)
    "league_soraka_skill": "ASSETS/Characters/Soraka/HUD/Icons2D/Soraka_Q.dds",
    "league_soraka_skill2": "ASSETS/Characters/Soraka/HUD/Icons2D/Soraka_W.dds",
    "league_soraka_ult": "ASSETS/Characters/Soraka/HUD/Icons2D/Soraka_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Soraka.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Soraka.{args.lang}.wad.client"))
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
