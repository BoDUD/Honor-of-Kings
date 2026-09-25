# Porting heroes from another MOBA (Honor of Kings, LoL, Dota 2, ...)

The two principles every successful pack writes in its description:

1. Kits are "rebalanced and readjusted towards TFM2 data availability" - keep the hero's
   *fantasy* (what fans recognise) and rebuild the numbers inside base-game ranges.
2. "Will only be making heroes that is currently possible" - skip heroes whose identity depends
   on something the data format cannot express.

## Slot mapping

| Source game | TFM2 |
|---|---|
| Honor of Kings: passive + skill 1 + skill 2 + ultimate | `attack` (+passive via buffs) / `skill` / `skill2` / `ult` - maps 1:1 |
| League of Legends: passive + Q W E R | drop or merge one basic ability; R -> `ult` |
| Dota 2: 3 basics + ultimate (+ facets/aghs) | pick the 2 most iconic basics |

Roles: tank / fighter -> `Melee` (tags `Tank`, `CC`), assassin -> `Assassin`,
mage -> `Magician`, marksman -> `Range`, support -> `Util`.

TFM2 is auto-battled: the AI decides when to cast. Design every skill so that casting it
whenever a valid target is in `range` is reasonable; mechanics that rely on player timing
(combos, cancels, precise recasts, positioning tricks) must become automatic.

## Mechanic -> effect mapping

OK = direct, ~ = approximate, X = not possible in data-only mods.

| Source mechanic | TFM2 implementation | |
|---|---|---|
| Line skillshot | `LinearProjectile` (penetrate true/false) | OK |
| Targeted missile | `TargetProjectile` | OK |
| Ground AoE with delay / lob | `RangeProjectile`, `ParabolicProjectile`, `Delayed`+`RangeEffect` | OK |
| Lingering field (blizzard, fire rain) | `RangePeriodProjectile` | OK |
| Aura around self | `ApplyInProjectile follow_caster` | OK |
| Dash / blink / leap to target / charge | `MoveTo`, `DirTeleport`, `MoveToTarget`, `RushTime` | OK |
| Stun, knock-up, root, slow, silence, disarm, fear, charm, taunt, knockback, pull | `Stun`, `Airborne`, `Bind`, buff `move_speed_mult`, `BlockSkill`, `BlockAttack`, `Fear`, `Charm`, `Taunt`, `Knockback`, `Pull` | OK |
| Shield, heal, lifesteal, burn/poison | `Shield`, `Heal`, buff `vamp`, `AddCasted` | OK |
| Passive stacks, every Nth attack | `SwitchByBuff` chain on hidden buffs | OK |
| Skill empowers next attack | ready-buff + `SwitchByBuff` in `attack` | OK |
| Stealth | `Invisible` / `CasterInvisible` | OK |
| 2-3 stage recast | `cooltime_use_count` or recast buff + `SwitchByBuff` | ~ (AI timing) |
| Untargetable / invulnerable | `Invisible` on self + `cc_immune` / `damaged_reduce` buff | ~ |
| Execute / missing-HP scaling | `FixedAttack target_hp_ratio`, flat bonus | ~ |
| Effect scaling with distance / charge time | fixed middle value | ~ |
| Summons, clones, turrets | zones/projectiles that deal the damage (LoL Reborn's Azir) | ~ |
| Transformation / stance | form buff + `SwitchByBuff` + long `CasterAnimation`; one sprite file per hero, so the "other form" must live as tags in the same `.aseprite` | ~ |
| Terrain / walls, global map mechanics, vision games | - | X |
| Resource bars (energy, rage, ammo) | stack buffs, or drop | ~ / X |
| Items, summoner spells, runes | - | X (ignore) |

If more than one core identity mechanic lands in the X column, choose another hero.

## Choosing the next hero (score 1-5 each, pick the highest total)

- **Recognition** - would a fan name the hero from a 35 px silhouette?
- **Kit fit** - share of the kit in the OK column above.
- **Sprite cost** - humanoid with one signature prop is cheap; mounts, huge creatures,
  transformations and summons cost 2-3x.
- **Roster gap** - fills a TFM2 category/role the pack lacks.
- **Showcase** - one signature VFX that sells the update GIF (a sun arrow, a sword storm).

## Numbers

Start from the base ranges in `champion-data.md` section 2 for the hero's category, then
translate relative strengths: if the source hero's skill is its main damage, give it the
larger ratio; long source cooldowns stay long relative to the hero's other skills. Ultimates
sit at 2400-3600 ticks. Never copy raw numbers from the source game.

## Honor of Kings specifics

- Kits are passive + 2 skills + ultimate: the cleanest 1:1 mapping of any big MOBA.
- Ids: `hok_<pinyin>` (e.g. `hok_libai`, `hok_houyi`); the mod_id doubles as namespace.
- Text: zh-hans uses the official Chinese names/skill names; `en` uses the official global
  (Honor of Kings, 2024) names; zh-hant uses the traditional-script forms.
- Many HoK kits have multi-stage recasts, dashes and brief untargetable windows (common in
  assassins/fighters) - see the ~ rows above; marksmen and mages are usually the most direct ports.
- Recognition lives in default skins and official art: sprite from the default skin, icons from
  the official skill icons (oppi style), thumbnail from the official splash.
- Add the fan-mod disclaimer the packs use: non-commercial, characters belong to their owner
  (Honor of Kings (c) Tencent / TiMi Studio Group).
