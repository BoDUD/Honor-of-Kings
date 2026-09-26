"""Pull Lee Sin's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_leesin.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/LeeSin.wad.client and LeeSin.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Resonating Strike has no hit event of its own: its landing uses the Sonic Wave mark's
OnBuffDeactivate (the mark is consumed when Lee Sin arrives), the Dragon's Rage collision a heavy
basic-attack hit.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/leesin/skins/base/leesin_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/leesin/skins/base/leesin_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_leesin_sfx_attack_hit": ("Play_sfx_LeeSin_LeeSinBasicAttack_OnHit", 1160187, 0.4, -6),
    "league_leesin_sfx_q_cast": ("Play_sfx_LeeSin_LeeSinQOne_OnCast", 120515603, 0.8, -4),
    "league_leesin_sfx_q_hit": ("Play_sfx_LeeSin_LeeSinQOne_OnHit", 989874514, 1.0, -4),
    "league_leesin_sfx_q2_cast": ("Play_sfx_LeeSin_LeeSinQTwo_OnCast", 774945029, 0.8, -4),
    "league_leesin_sfx_q2_hit": ("Play_sfx_LeeSin_LeeSinQOne_OnBuffDeactivate", 263375444, 0.9, -3),
    "league_leesin_sfx_e_cast": ("Play_sfx_LeeSin_LeeSinEOne_OnCast", 178665385, 0.5, -4),
    "league_leesin_sfx_e_hit": ("Play_sfx_LeeSin_LeeSinEOne_OnHitLocation", 801900457, 1.0, -3),
    "league_leesin_sfx_w_shield": ("Play_sfx_LeeSin_LeeSinWOneShield_OnBuffActivate", 475985419, 1.0, -6),
    "league_leesin_sfx_r_cast": ("Play_sfx_LeeSin_LeeSinR_OnCast", 196445596, 1.0, -4),
    "league_leesin_sfx_r_hit": ("Play_sfx_LeeSin_LeeSinR_OnHit", 693210799, 1.2, -2),
    "league_leesin_sfx_r_collide": ("Play_sfx_LeeSin_LeeSinBasicAttack_OnHit", 638593539, 0.6, -4),
    "league_leesin_vo_q": ("Play_vo_LeeSin_LeeSinQOne_cast3D", 483785425, 1.2, -2),
    "league_leesin_vo_q2": ("Play_vo_LeeSin_LeeSinQTwo_cast3D", 1039328162, 1.2, -2),
    "league_leesin_vo_e": ("Play_vo_LeeSin_LeeSinEOne_cast3D", 794885007, 1.3, -2),
    "league_leesin_vo_r": ("Play_vo_LeeSin_LeeSinR_cast3D", 713387656, 1.3, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (W Safeguard / Iron Will is folded into the E slot)
    "league_leesin_skill": "ASSETS/Characters/LeeSin/HUD/Icons2D/LeeSinQ1.dds",
    "league_leesin_skill2": "ASSETS/Characters/LeeSin/HUD/Icons2D/LeeSinE1.dds",
    "league_leesin_ult": "ASSETS/Characters/LeeSin/HUD/Icons2D/LeeSinR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "LeeSin.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"LeeSin.{args.lang}.wad.client"))
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
