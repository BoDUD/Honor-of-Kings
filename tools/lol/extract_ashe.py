"""Pull Ashe's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ashe.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Ashe.wad.client and Ashe.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default;
her R has no voice line in that bank, so R uses sound effects only.

Several of these media loop (the attack sounds repeat every ~0.7 s when decoded); finish() keeps
the first max_s seconds after the onset, which is one shot.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ashe/skins/base/ashe_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ashe/skins/base/ashe_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_ashe_sfx_attack_shot": ("Play_sfx_Ashe_AsheBasicAttack_OnMissileLaunch", 106727677, 0.6, -4),
    "league_ashe_sfx_attack_hit": ("Play_sfx_Ashe_AsheBasicAttack_OnHit", 147327516, 0.6, -5),
    "league_ashe_sfx_q_cast": ("Play_sfx_Ashe_AsheQAttack_OnBuffCast", 786956351, 1.2, -3),
    "league_ashe_sfx_q_shot": ("Play_sfx_Ashe_AsheQAttack_OnMissileLaunch", 818926381, 0.6, -4),
    "league_ashe_sfx_q_hit": ("Play_sfx_Ashe_AsheQAttack_OnHit", 1038118816, 0.8, -5),
    "league_ashe_sfx_w_cast": ("Play_sfx_Ashe_VolleyAttack_OnCast", 657160488, 1.2, -3),
    "league_ashe_sfx_w_hit": ("Play_sfx_Ashe_VolleyAttack_OnHit", 572389194, 0.6, -6),
    "league_ashe_sfx_r_cast": ("Play_sfx_Ashe_EnchantedCrystalArrow_OnMissileLaunch", 869964286, 2.0, -2),
    "league_ashe_sfx_r_hit": ("Play_sfx_Ashe_EnchantedCrystalArrow_hit", 952373565, 2.0, -1),
    "league_ashe_vo_q": ("Play_vo_Ashe_AsheQ_cast3D", 981568607, 1.6, -2),
    "league_ashe_vo_w": ("Play_vo_Ashe_Volley_cast3D", 3667150708, 1.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_ashe_skill": "ASSETS/Characters/Ashe/HUD/Icons2D/Ashe_Q.dds",
    "league_ashe_skill2": "ASSETS/Characters/Ashe/HUD/Icons2D/Ashe_W.dds",
    "league_ashe_ult": "ASSETS/Characters/Ashe/HUD/Icons2D/Ashe_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ashe.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ashe.{args.lang}.wad.client"))
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
