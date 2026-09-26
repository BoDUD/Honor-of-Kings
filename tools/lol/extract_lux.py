"""Pull Lux's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_lux.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Lux.wad.client and Lux.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

The champion bin lists some event names with a stray digit glued on (Play_sfx_Lux_LuxLightBinding_OnCast1);
the banks know them without it.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/lux/skins/base/lux_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/lux/skins/base/lux_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_lux_sfx_attack_shot": ("Play_sfx_Lux_LuxBasicAttack_OnCast", 39682869, 0.6, -5),
    "league_lux_sfx_attack_hit": ("Play_sfx_Lux_LuxBasicAttack_OnHit", 29363137, 0.6, -6),
    "league_lux_sfx_passive_hit": ("Play_sfx_Lux_LuxIlluminationPassive_hit", 575879865, 0.9, -3),
    "league_lux_sfx_q_cast": ("Play_sfx_Lux_LuxLightBinding_OnCast", 683874540, 1.0, -3),
    "league_lux_sfx_q_hit": ("Play_sfx_Lux_LuxLightBindingMis_OnBuffActivate", 618792157, 1.2, -4),
    "league_lux_sfx_w_shield": ("Play_sfx_Lux_LuxPrismaticWaveShieldSelf_buffactivate", 423630636, 0.9, -5),
    "league_lux_sfx_e_cast": ("Play_sfx_Lux_LuxLightStrikeKugel_OnCast", 113441182, 1.0, -4),
    "league_lux_sfx_e_zone": ("Play_sfx_Lux_LuxLightStrikeKugel_buffactivate", 386229644, 1.0, -6),
    "league_lux_sfx_e_hit": ("Play_sfx_Lux_LuxLightStrikeKugel_hit", 979274182, 1.0, -2),
    "league_lux_sfx_r_cast": ("Play_sfx_Lux_LuxR_OnCast", 82083908, 0.8, -3),
    "league_lux_sfx_r_fire": ("Play_sfx_Lux_LuxRBeam_beammiddle", 266892436, 1.5, -1),
    "league_lux_vo_q": ("Play_vo_Lux_LuxLightBinding_cast3D", 2135987821, 1.2, -2),
    "league_lux_vo_e": ("Play_vo_Lux_LuxLightStrikeKugel_cast3D", 1765227626, 1.2, -2),
    "league_lux_vo_r": ("Play_vo_Lux_LuxR_cast3D", 89080532, 2.0, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (W Prismatic Barrier is folded into the Q slot)
    "league_lux_skill": "ASSETS/Characters/Lux/HUD/Icons2D/LuxCrashingBlitz2.dds",
    "league_lux_skill2": "ASSETS/Characters/Lux/HUD/Icons2D/LuxLightStrikeKugel.dds",
    "league_lux_ult": "ASSETS/Characters/Lux/HUD/Icons2D/LuxFinaleFunkeln.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Lux.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Lux.{args.lang}.wad.client"))
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
