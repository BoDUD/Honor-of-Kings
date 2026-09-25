# Mod structure, loading and publishing

Everything here was read from the shipped game (bundle, uploader, config) and from working
Workshop packs. "Inferred" marks conclusions drawn from behaviour rather than documentation.

## Where things live

| What | Path |
|---|---|
| Game install | `<Steam>/steamapps/common/Teamfight Manager2/` |
| All base assets (uncompressed archive) | `<game>/bundle.game_data` - browse with `scripts/bundle_tool.py` |
| Official uploader | `<game>/TFM2ModUploader.exe` |
| Local / dev mods | `<game>/mods/<folder>/` |
| Enabled mods + order | `<game>/config/game/mods.json` (`enabled_mods`, `known_workshop_mods`, ...) |
| Subscribed Workshop mods | `<Steam>/steamapps/workshop/content/3009300/<publishedfileid>/` |

TFM2's Steam app id is **3009300**. A folder is a mod when it has `mod.mod_info` at its root
(the loader also accepts it one folder level down). If a player reports "mod.info not found",
resetting `config/game/mods.json` (enabled list / order) is the known fix.

## Recommended layout (what the benchmark packs converge on)

```
<mod_id>/
  mod.mod_info                     manifest (required)
  mod.override_info                what you inject into the base namespace
  thumbnail.png  (or preview.png)  Workshop preview image, square
  champion/<hero>.data_champion    one JSON per hero (auto-discovered)
  champions/<hero>.aseprite        hero sprite (all animations as tags)
  effects/ fx/ buffs/              VFX sprites (.aseprite, one effect per file)
  icons/<hero>_skill.png ...       64x64 skill icons (3 per hero)
  text/champion.i18n               names, tooltips, skill names (merged)
  style/champion_view.champion_view  face/center offsets (merged)
  sound/sfx/<name>.sound_info + <clip>.mp3|.wav
  (optional) BanPickIllust/<hero>.png  splash art for the Pick Ban Plus mod
```

`champion/` files need no manifest entry - every `*.data_champion` in the mod is loaded
(inferred: neither pack lists them anywhere).

## mod.mod_info

```json
{
  "author": "you",
  "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}],
  "description": "One line shown in the in-game mod list.",
  "last_updated": "2026-09-25",
  "mod_id": "hok",
  "name": "Honor of Kings Heroes",
  "version": "0.1.0"
}
```

- `mod_id` is the asset namespace: files are addressed as `asset/<mod_id>/<relative path>`.
  Use lowercase snake_case. `base` is reserved.
- Never change `mod_id` after release - saves reference champion ids. (LoL Reborn kept
  Silverbear's old `test_mod` id for exactly this reason and told players to reset their DB.)
- Bump `version` and `last_updated` on every upload.

## mod.override_info

Maps a **base** asset path to one of **your** files:

```json
{
  "asset/base/text/champion":        {"remapping": "asset/hok/text/champion",        "type": "merge"},
  "asset/base/style/champion_view":  {"remapping": "asset/hok/style/champion_view",  "type": "merge"},
  "asset/base/sound/sfx/hok_libai_skill_cast":      {"remapping": "asset/hok/sound/sfx/hok_libai_skill_cast",      "type": "override"},
  "asset/base/sound/sfx/hok_libai_skill_cast_clip": {"remapping": "asset/hok/sound/sfx/hok_libai_skill_cast_clip", "type": "override"}
}
```

- `merge` deep-merges JSON-like resources: use it for `text/champion` (and `text/ui`) and
  `style/champion_view`. **Never `override` these** - it would delete every base champion's text.
- `override` replaces an asset: custom sounds, reskins of base sprites
  (`asset/base/aseprite_resources/ingame/blue_tower#sheet` + `#anim`), UI images, layouts, and
  Pick Ban Plus splash art (`asset/base/ui/banpick/illust/<champion_id>`).
- Your own namespaced sprites/icons/effects need **no** entry; they are referenced directly by
  `asset/<mod_id>/...` paths from the champion JSON.
- The remapping must point inside your namespace and must exist. A real shipped bug: the Touhou
  pack has `"remapping": "asset/\\/BanPickIllust/flandre"` (broken namespace) for 10 heroes.
  `scripts/lint_mod.py` catches this.

## Asset path rules

- No file extension in paths. The engine resolves `name.aseprite` or the exported pair
  `name#sheet.png` + `name#anim.fanim`; PNG icons from `name.png`.
- Icon atlases: `name#sheet.png` + `name#data.sprite_sheet`
  (`{"images": {"<tag>": {"x":0.0,"y":0.0,"w":0.055,"h":1.0}}}` - normalised UV rects), used via
  `"skill_icon": {"source": "asset/<mod_id>/.../name", "tags": [3 tags]}`.
- You may reference base assets directly: effects such as
  `asset/base/aseprite_resources/skill_effect/swordman_effect` (tags `skill`, `skill_projectile`,
  `ult`), `.../stun_effect` (`stun`), `.../shield_receive_effect` (`shield_receive`), and base
  sound names in `Sfx` (`fighter_attack`, `necromancer_skill`, ...). List them with
  `python scripts/bundle_tool.py list --grep skill_effect/` and `python scripts/bundle_tool.py sfx`.

## .fanim (exported animation) format

```json
{"anims": {"idle": {"frames": [{"duration": 0.12, "data": {"x": 128, "y": 0, "w": 64, "h": 64}}]}}}
```

Duration is in **seconds**; each frame is a rect in `#sheet.png`. Frames are drawn centred on the
unit, so trimmed frames must stay symmetric around the pivot (base frames all have odd sizes for
this reason). The engine binary also knows `frame_offsets` and `overlay_anchor` keys, but no
shipped file uses them - format unverified. Prefer shipping `.aseprite` directly (oppi does).

## Local test loop

1. Copy (or junction) the mod folder into `<game>/mods/<mod_id>/`.
2. Run `python scripts/lint_mod.py <game>/mods/<mod_id>` until there are no errors.
3. Start the game, enable the mod in the Mods menu (writes `config/game/mods.json`), start a
   custom match with the hero, and check: every action animates, projectiles/effects are
   visible, sounds play, tooltips show text in your language, the hero stands at the same
   height as base champions next to it.
4. When a save was made with an older version of the pack, test on a fresh save too.

## Publishing with TFM2ModUploader.exe (official)

Strings in the uploader describe the flow:

- "Choose a mod or database pack folder, check the details, then publish it to Steam Workshop."
  The folder must contain exactly one manifest (`mod.mod_info` for mods, `database_pack.info` for
  database packs).
- Preview: "Add preview.png or thumbnail.png to show an image in Workshop."
- Data-only mods: "This mod has no Cargo.toml or src/lib.rs, so no build step is needed."
- It asks "What changed in this version?" (the change note) and a visibility:
  Public / Friends only / Private / Unlisted. First upload creates the Workshop item; later uploads
  update it. You must have accepted the Steam Workshop legal agreement.
- `base` cannot be published.

Code mods (Rust DLLs built against the mod SDK) exist; the uploader tags them
`tfm2_contains_code` and players get a "[Code Mod Notice]" prompt. Everything in this skill is
data-only on purpose - it needs no build, triggers no warning, and survives game updates better.
