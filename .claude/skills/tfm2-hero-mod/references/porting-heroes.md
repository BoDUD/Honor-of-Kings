# Porting heroes from another MOBA (League of Legends, Dota 2, ...)

The two principles every successful pack writes in its description:

1. Kits are "rebalanced and readjusted towards TFM2 data availability" - keep the hero's
   *fantasy* (what fans recognise) and rebuild the numbers inside base-game ranges.
2. "Will only be making heroes that is currently possible" - skip heroes whose identity depends
   on something the data format cannot express.

## Slot mapping

| Source game | TFM2 |
|---|---|
| League of Legends: passive + Q W E R | two basics -> `skill` / `skill2`, R -> `ult`; fold the third basic and the passive in (see below) |
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
| Mark on the target that the next attack detonates (Lux's Illumination) | `SwitchByBuff` only sees the caster's buffs and no effect removes a target's buff, so skill hits add a hidden caster ready-buff (the next attack on any enemy detonates it) and play a short mark `ViewEffect` on the hit target | ~ |
| Skillshot that stops after N targets (Lux Q: two) | `LinearProjectile` only has `penetrate` true/false; the mod SDK's `LinearProjectileEffect` has no hit-count field | ~ |
| Stealth | `Invisible` / `CasterInvisible` | OK |
| 2-3 stage recast | `cooltime_use_count` or recast buff + `SwitchByBuff` | ~ (AI timing) |
| Cone / fan of projectiles (Ashe W) | no angle field on any projectile (base harpooner's fan is `Native`): a `LineRangeProjectile` rectangle cast by `Direction`, drawn as a fan sprite centred on it (champion-data "Cone / fan"); the hit area stays a rectangle | ~ |
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

## League of Legends specifics

How LoL Reborn (all 32 heroes, both authors) fits four abilities into three slots:
- `ult` is always R. `skill` / `skill2` are the two most iconic basics.
- The third basic and the passive are **folded in**, written as "Passive: ..." or as an extra
  effect of one of the two skills (Jax: E + passive stacks; Vi: Q + Blast Shield; Galio: E + W
  shield/taunt; Alistar: R + E heal). Silverbear's simpler heroes just drop them.
- Example (league_garen): Q Decisive Strike + W Courage (shield, damage reduction, tenacity) ->
  `skill`; E Judgment (`CasterAnimation spin` for 3 s, plus a short `MoveToTarget` in each of the
  7 damage pulses because the forced animation holds him still; cast as `Targeting` so the dashes
  have a target) -> `skill2`, with
  Perseverance as high `hp_regen` noted in its text; R Demacian Justice -> `ult` (true damage;
  missing-HP scaling exists only in base-only Native effects, so use `target_hp_ratio`).
- Ids: `<mod_id>_<champion>` (`league_garen`). The user's own `lol_mod` uses `lol_*`, so keep a
  different prefix for anything that may be installed next to it.
- Text: official names per language (zh-hans from the Chinese client, zh-hant, en, ko, ja).
- Assets come from the local client, read-only: `tools/lol/riot.py` reads WAD 3.x (xxh64 path
  hashes, zstd via Python 3.14 `compression.zstd`), Riot WPK packs and Wwise banks (bank version
  145: events -> actions -> sounds/containers), and resolves `Play_sfx_<Champ>_*` /
  `Play_vo_<Champ>_*` event names (plain strings in the champion `.bin` files) to .wem media;
  vgmstream decodes the .wem. Ability icons are `ASSETS/Characters/<Champ>/HUD/Icons2D/*.dds`.
- Chinese voice: `<Champ>.zh_CN.wad.client` in the Tencent (WeGame) client; inside it the banks
  keep the `vo/en_us/` path.
- Real animations as pose references: `tools/lol/pose_ref.py --anim Run --frames 6` skins the
  champion's `.skn`/`.skl` with an `.anm` clip (compressed `r3d2canm`, or uncompressed
  `r3d2anmd` v3 / v4 / v5 - most of Lux's clips are v3, her R is v4) and renders textured
  3/4-view frames. The diffuse texture is `*_TX_CM` (Garen, Ashe) or `*_CM_TX` (Lux); without
  one the model renders grey. Clip names come from
  `data/characters/<champ>/animations/skin0.bin` (Garen: `Idle1`, `Run`, `Run_Spell1`,
  `Attack_01/02`, `Crit`, `spell1/3/4`, `Death`). Attack clips are ~2 s with the swing in the
  first ~0.4 s - pick frame times with `--times`. Use `--mirror` when the pose turns the chest
  toward the champion's right (Garen's idle and Attack_01): it renders the other side and flips
  it, so the sprite still faces right with its front showing.
- **Which clip plays when.** The animation bin maps clip names to files as `FNV-1a(lowercase
  name) -> AtomicClipData { path }`; hash candidate names (`Run`, `Run2`, `Spell4`...) and read the
  path that follows. Ashe: `Run` = `ashe_run_walk`, `Run2` = `ashe_run_jog`, `Run3` = `ashe_run`;
  `Spell4` (R) reuses `ashe_crit1`; Q is `Ashe_spell1_IN` then `ashe_spell1`.
- **Walk or run: measure it.** During stance a planted foot slides back at the clip's ground
  speed; compare it with the champion's movement speed, and look for frames where both feet are
  off the ground (a run) or one foot always down (a walk). Ashe's jog/run clips move ~305 units/s
  (her base move speed is 325) with a flight phase, so she runs; the walk (~250) is her slowed
  gait. Time the TFM2 loop from the clip's own cycle (Ashe: 1.0 s, 8 x 125 ms). Lux has a single
  `lux_run` (a 4.8 s file holding six 0.8 s cycles): both feet are off the ground for about half
  of each cycle, so she runs (8 x 100 ms).
- **Render side, per champion.** Some champions show their chest from one side, some from the
  other (Garen and Lux need `--mirror`, Ashe does not) - render idle both ways and look for the face.
  Then use that same side for *every* clip of the hero: the renders appear to be mirror images of
  the game (Ashe's bow hangs off her `R_hand` joint but shows in her left hand), so switching
  sides between clips moves a one-handed prop to the other hand. TFM2 flips sprites that face
  left anyway, so the handedness itself does not matter.
- **Start and end near idle.** League cross-fades clips (about 0.2 s), and many clips start
  mid-action (Ashe's attack opens at full draw). `pose_ref.py --frame "idle@0>attack@0:0.5"`
  renders that blend, so each strip can open and close half-way to idle instead of popping.
  `--hq` textures per pixel (face and trim readable) - better pose references and a design sheet
  (three `--yaw` views of the idle frame).
- **Render them chibi.** League's adult proportions pull the image model to a small head even
  when the prompt says "chibi": Garen and Ashe came out with heads 1/5 of their height (base
  heroes: 1/3), so in-game their faces were two or three rows of skin without eyes.
  `--head 2.0 --legs 0.8` scales the head joint and every leg, cape, skirt and cloth chain and
  keeps the legs' lowest point where League has it (landings and jump heights unchanged) - the
  references then show the proportions to draw (`assets/source/CHIBI_REDRAW.md`). Use it from the
  first prompt of every new hero; the redraw of both heroes came back right in one round.
- **Head tracks for the importer.** `pose_ref.py --frame <clip@ms> ... --track <hero px>
  --track-ref <idle clip@0>` prints each frame's head joint x in game px from the unit, for a
  hero that many px tall in idle, through the same camera and `--mirror` / `--head` / `--legs` as
  the references (the importers place each frame's drawn head there). The chibi skeleton moves the
  head 3-4% less than the adult one; Garen's hand-measured tracks had been 0.69x too small.
- **Official names** live in `Game/DATA/FINAL/Localized/Global.<locale>.wad.client` ->
  `data/menu/en_us/lol.stringtable` (RST v5: 38-bit xxh64 key hashes; the Chinese WADs keep the
  `en_us` path, like their voice banks). Find a string by its English text and read the same key
  in the other locale. The Tencent client has zh_CN, the Riot client here zh_MY (whose names
  differ in places: Ashe's Q is 射手的专注 in zh_CN, 专注射击 in zh_MY).
- Riot allows non-commercial fan content; keep extracted audio out of public repos anyway
  (re-extract with the tool) and add the disclaimer (League of Legends (c) Riot Games).
