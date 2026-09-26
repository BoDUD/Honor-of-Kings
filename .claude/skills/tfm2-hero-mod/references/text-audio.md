# Text, champion_view and sound

## text/champion.i18n (merged into asset/base/text/champion)

```json
{
  "en": {
    "description": {
      "league_garen": {"name": "Garen", "attack": "...", "skill": "...", "skill2": "...", "ult": "..."}
    },
    "skill_name": {
      "league_garen": {"skill1": "...", "skill2": "...", "ult": "..."}
    }
  },
  "zh-hans": { ... }
}
```

- Language keys used by the base game: `ko en ja de vi pt-BR tr nl ru es-ES fr it zh-hans
  zh-hant pl th haw`. Always ship `en`; for a Chinese franchise also `zh-hans` and `zh-hant`.
  The Dota 2 pack ships en, pt-BR, zh-hans, zh-hant, ko, ru and fr; its comments show players
  notice missing or wrong-language text (a Russian player got Portuguese tooltips).
- Each action points at its text with
  `"description": "#asset/base/text/champion?description.<id>.<slot>"`.
- Note the key asymmetry: descriptions use `skill`/`skill2`/`ult`, `skill_name` uses
  `skill1`/`skill2`/`ult`.
- Use the franchise's **official localized names** per language (e.g. 盖伦 / 蓋倫 / Garen / 가렌 / ガレン).
- **Keep every description within the base game's longest.** Base skill texts show at most 130
  characters in zh-hans / zh-hant (median ~50-65), 147 in ja, 185 in ko and 334 in en; longer
  text is crammed together in the skill details panel. Soraka's first text (Q with E folded in,
  195 characters in zh-hans) was, so it now starts with the effect instead of repeating the skill
  name (base texts never open with it; the name has its own `skill_name` entry), drops secondary
  durations and keeps every damage, heal and crowd-control number. `lint_mod.py` warns above these
  limits (all 17 languages).

### Rich text

`<#RRGGBBAA>text<>` colours a span; `<i#asset/base/ui/banpick/champion_stat_icon:ICON>` inserts
an icon. Keep the base game's colour language (measured from base tooltips):

| Colour | Used for |
|---|---|
| `#ff9028ff` orange | physical damage, AD scaling, ability names |
| `#a974ffff` purple | magic damage, AP scaling |
| `#ffb900ff` amber | durations, counts, ranges, delays |
| `#ef5350ff` red | CC words: slow, stun, root, airborne, fear |
| `#6aff55ff` green | healing, health |
| `#e8d44dff` yellow | shields |
| `#ffffffff` white | movement speed |
| `#ceff99ff` light green | attack speed |
| `#ffdd8eff` / `#88ccffff` | armor / magic resistance |
| `#ff86c2ff` pink | attack range |
| `#f5f5f5ff` | true damage |
| `#78e85cff` | poison |

Icons (8): `ad_0`, `ap_0`, `attack_speed_0`, `speed_0`, `hp_0`, `range_0`, `armor_0`,
`magic resistance_0` (with the space). **Never translate icon ids** - LoL Reborn's Thai and
Hawaiian text has `เกราะ_0` / `pale_0`, which render nothing.

Base text also uses placeholders such as `{Damage}`, `{Coef}`, `{UseCount}`, `{Range}`,
`{Radius}`; how the engine fills them for mod data is unverified, so write the real numbers
(most pack text does) and keep them in sync with the JSON when rebalancing.

Pattern: `<#ff9028ff>Skill Name<>: what it does, <#ff9028ff>150<> + <i#...:ad_0><#ff9028ff>120% AD<> <#ff9028ff>physical damage<>, <#ef5350ff>stuns<> for <#ffb900ff>1s<>.`

## style/champion_view.champion_view (merged into asset/base/style/champion_view)

```json
{"entries": {"league_garen": {"face": {"x": 0, "y": -34}, "center": {"x": 0, "y": -12}}}}
```

Offsets in sprite pixels measured **up from the feet** (negative y = higher). `center` is the
body centre (base default y -12, where hits/health bar anchor); `face` is the head centre
(~ -(height - 2); -34 for a 35-37 px hero, -45 to -54 for giants). Base also has an optional
`banpick_center`. Adjust `face.x` when the head is not above the feet (quadrupeds, big weapons).
Measure it, don't guess: `python scripts/tfm2_ase.py face <sprite> [--view <champion_view>]`
prints the point the base game would use and `--out x.png` draws your hero next to base champions
with every face point marked. On all 68 base champions `face` sits at the **crown** - the first
row of idle frame 0 at least half as wide as the head (so buns, hat tips and pointed hoods don't
count; median 0 px below it) - and ~1.5 px ahead of the head centre. `lint_mod.py` warns when a
face point is more than 4 px above the crown, 10 below or 8 aside (62 of the 68 base champions
pass; the rest are a mount, the ogre, the werewolf, two big hats and the strongman). league_garen
shipped with -38, above his hair (the portrait showed hair and air); a small head fails this check
too, because its crown is found at the shoulders. Now: league_garen (-1, -35), league_ashe (0, -33),
league_lux (1, -31) (both re-measured after the native-size redraw), league_leesin (0, -34) (the
crown rule skips the braid standing above his head; a blindfold, not eyes, is what must read).

## Sounds (sound/sfx)

`<name>.sound_info`:
```json
{"plays": [{"delay": 0.0, "clip": "<clip_file_name_without_ext>", "volume": 0.6}]}
```

- Put the clip next to it (`sound/sfx/<clip>.mp3` or `.wav`).
- `Sfx`/`TargetSfx` look sounds up in the base namespace, so every custom sound needs **two
  override entries** (the pattern used by both big packs):
  `asset/base/sound/sfx/<name>` -> `asset/<mod_id>/sound/sfx/<name>` and
  `asset/base/sound/sfx/<clip>` -> `asset/<mod_id>/sound/sfx/<clip>`, both `"override"`.
- Name sounds `<mod>_<hero>_<slot>_<cast|hit>` so they never collide.
- **`<champion id>_attack` plays by itself.** 61 of 67 base attacks have no `Sfx` in their data,
  yet each champion has a sound named `<id>_attack`: the engine plays it on every basic attack.
  Do not also play `<id>_attack` from the attack's effect tree - it sounds twice (league_garen:
  the explicit hit landed 10 ticks after the automatic one and players heard two swings). Name
  explicit attack sounds `<id>_attack_hit` / `<id>_attack_cast` like base and the later LoL Reborn
  heroes, or rely on the automatic one when the hit comes at `start_timing`.
- Normalise loudness; packs use volume 0.4-1.0 per clip. Several `plays` entries with `delay`
  layer sounds (e.g. a cast whoosh then an impact).
- No sound yet? Reuse base ones (`python scripts/bundle_tool.py sfx`), e.g. `fighter_attack`,
  `fighter_skill_hit`, `swordman_ult`, `necromancer_skill`.
