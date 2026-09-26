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
| Heal the ally who needs it (Soraka W) | `Targeting` + `AllyNotSelf`; the AI scores a heal by the target's missing health (champion-data "Which ally gets an ally skill") | ~ (AI choice) |
| Health cost (Soraka W) | `WithSelf` + `FixedAttack target_hp_ratio`, a short `undying` caster buff first | ~ |
| Global heal (Soraka R) | `Targeting AllyChampion` range 960000 + `RangeEffect` 960000 on `AllyChampion`; no bonus on low-health targets | ~ |
| Move faster toward low-health allies (Soraka passive) | no move direction or ally health in data: a move-speed caster buff after the ally heal | ~ |
| Passive stacks, every Nth attack | `SwitchByBuff` chain on hidden buffs | OK |
| Skill empowers next attack | ready-buff + `SwitchByBuff` in `attack` | OK |
| Mark on the target that the next attack detonates (Lux's Illumination) | `SwitchByBuff` only sees the caster's buffs and no effect removes a target's buff, so skill hits add a hidden caster ready-buff (the next attack on any enemy detonates it) and play a short mark `ViewEffect` on the hit target | ~ |
| Skillshot that stops after N targets (Lux Q: two) | `LinearProjectile` only has `penetrate` true/false; the mod SDK's `LinearProjectileEffect` has no hit-count field | ~ |
| Skillshot, then dash to the unit it hit (Lee Sin Q2, Blitz/Naut hooks) | `MoveToTarget` inside the projectile's `applied_effects` (LoL Reborn Nautilus Q); a `Delayed` there keeps the hit unit as target; no recast, it dashes by itself | ~ |
| Kick back + collision (Lee Sin R) | `Targeting`: `Attack` + `Knockback` on the target, plus a penetrating `LinearProjectile` toward it at the knockback's speed that knocks up what it passes (LoL Reborn Nautilus R) | ~ |
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
  `Spell4` (R) reuses `ashe_crit1`; Q is `Ashe_spell1_IN` then `ashe_spell1`. Newer champions
  route through logic clips: after the key hash comes the class hash (`FNV-1a` of
  `AtomicClipData`, `SequencerClipData`, `ConditionBoolClipData`, `ConditionFloatClipData`,
  `SelectorClipData`), and the non-atomic ones list other clip hashes. Lee Sin: `Idle1` = sequence
  `Idle_Active` (combat stance) then `Idle_Passive`; `Run` = `Run_Homeguard` or, by speed,
  `Run_Base.anm` (its haste branch plays the same file); `Crit` = `Attack4`; Q2 = `Spell1_B` then
  `Spell1_B_Loop`. TFM2 heroes are always fighting, so take the combat idle. Older champions have
  only atomic clips (Soraka: `Idle1`, a single `Run`, `Attack1/2`, `Spell1`-`Spell4`, `Death`),
  so there is no combat-run branch to look for.
- **Walk or run: measure it.** During stance a planted foot slides back at the clip's ground
  speed; compare it with the champion's movement speed, and look for frames where both feet are
  off the ground (a run) or one foot always down (a walk). Ashe's jog/run clips move ~305 units/s
  (her base move speed is 325) with a flight phase, so she runs; the walk (~250) is her slowed
  gait. Time the TFM2 loop from the clip's own cycle (Ashe: 1.0 s, 8 x 125 ms). Lux has a single
  `lux_run` (a 4.8 s file holding six 0.8 s cycles): both feet are off the ground for about half
  of each cycle, so she runs (8 x 100 ms). Lee Sin's `Run_Base` is a leaping run: 1.53 s for two
  strides, each with ~0.4 s in the air (8 x 192 ms).
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
  Everything below the head joint grows with it: Lee Sin's long braid (`Hair1`..`Hair12` under
  `Head`) reached the ground at 2x. `--hair 0.5` scales the hair chains back to League's length.
  Check where the hair hangs from: Soraka's ponytail chain starts at `Chest`, so it keeps League's
  length by itself. Her horn has a `horn` joint under `Head` but no skin weights of its own - it
  rides on the head and doubled with it, its tip becoming the crown. `--keep horn:4`
  (`"keep": {"horn": 4.0}` in `chibi` of a native_pose spec) binds the head vertices above that
  joint and within 4 units of it to the joint, so `--hair` holds the horn at League's size and the
  crown is measured without it (`pose_ref.keep_parts`).
- **Game size straight from League (Lee Sin: worked, one GPT round).** The native-size
  redraw needed a first GPT round only to turn League's poses into game frames.
  `tools/lol/native_pose.py <hero>/poses.json` renders the clips at game size instead: the chibi
  model through one camera, the design pose `height` px from crown to soles (hair chains not
  counted), each game pixel the mean colour of an 8x8 block of an `--hq` render, in the native
  grid, next to the same frames as the 8x render, plus `<hero>_cells.json` for
  `tools/art/import_native.py`. Per tag: `lunge` (share of League's travel kept, 0.7 for
  actions), `anchor: first` (Lee Sin's death starts 140 units in front of the unit), `flat`
  (each frame's lowest point as high above the feet line as above League's floor - a body lying
  diagonally in depth otherwise floats or sinks through the pitch); per frame `turn` degrees
  toward the camera for spins and bent-over slams that would show the back, and `head_like`
  (per tag or per frame) to turn the head the way it faces in another pose, the body untouched:
  a chibi head bowed toward the ground shows only its crown (Soraka's Q and R bows keep her face
  with `"head_like": "Soraka_Idle1@0"`). Cells can be bigger
  than 56x64 (`"cell": [64, 72]` for the braid and the flying kick). The cells table also records
  League's head joint per frame. GPT followed the poses but drew every action except idle about
  1.4x the design (heads more than bodies) and its jumps too low; `tools/art/fit_native.py`
  shrinks each strip back by the head (a 16-colour vote, still flat pixels) and puts each frame's
  blindfold on League's head joint, soles back on the line where the reference stands - check
  every strip's head against idle before importing.
- **Head tracks for the importer.** `pose_ref.py --frame <clip@ms> ... --track <hero px>
  --track-ref <idle clip@0>` prints each frame's head joint x in game px from the unit, for a
  hero that many px tall in idle, through the same camera and `--mirror` / `--head` / `--legs` as
  the references (the importers place each frame's drawn head there). The chibi skeleton moves the
  head 3-4% less than the adult one; Garen's hand-measured tracks had been 0.69x too small.
- **Official names** live in `Game/DATA/FINAL/Localized/Global.<locale>.wad.client` ->
  `data/menu/en_us/lol.stringtable` (RST v5: 38-bit xxh64 key hashes; the Chinese WADs keep the
  `en_us` path, like their voice banks). Find a string by its English text and read the same key
  in the other locale. The Tencent client has zh_CN, the Riot client here zh_MY (whose names
  differ in places: Ashe's Q is 射手的专注 in zh_CN, 专注射击 in zh_MY). For locales not
  installed, read Riot's public Data Dragon
  (`ddragon.leagueoflegends.com/cdn/<version>/data/<ja_JP|ko_KR|zh_TW>/champion/<Champ>.json`):
  Lee Sin's Japanese names (練気, 響掌/共鳴撃, 破風/縛脚) were nothing like a guess.
- Riot allows non-commercial fan content; keep extracted audio out of public repos anyway
  (re-extract with the tool) and add the disclaimer (League of Legends (c) Riot Games).
