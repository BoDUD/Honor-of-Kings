# .data_champion reference

Schema, units, enums and the effect catalogue, compiled from the 8 base `.data_champion` files,
the base `champion_info` sheet (68 champions), 52 champions in two large Workshop packs, and
strings in the game binary. Anything marked *(inferred)* was deduced from usage, not documented.

Contents
1. Top-level fields
2. Units and balance ranges
3. Actions (attack / skill / skill2 / ult)
4. Effect catalogue
5. buff_state
6. View bindings (how things become visible)
7. Patterns that work (copy these)
8. Gotchas

## 1. Top-level fields

| Field | Notes |
|---|---|
| `id` | Unique, namespaced (`league_garen`). Also the key for text and champion_view. |
| `category` | `Melee` \| `Range` \| `Magician` \| `Util` \| `Assassin` (drives UI filter + AI role) |
| `tags` | Free strings used in packs: `AD` `AP` `Melee` `Range` `Tank` `CC` `Magic` `Heal` `Shield` `Dot` |
| `sprite` | `asset/<mod_id>/champions/<hero>` (no extension) |
| `anim_prefix` | `""` in every pack |
| `skill_icons` | 3 paths: skill, skill2, ult (64x64 PNG) - or `skill_icon: {source, tags}` atlas |
| `stat` / `growth` | 9 keys each: `attack magic_power hp defence magic_resistance move_speed hp_regen stack crit_chance` |
| `attack` `skill` `skill2` `ult` | the four actions (section 3) |
| `view_projectiles` `view_effects` `view_buffs` | bindings from effect names to animations (section 6) |

The engine struct also has `passive`, `passive_skill2`, `passive_ult`, `stack_skill_index` and
`name`; no shipped file uses them - format unknown, so build passives with buffs instead (section 7).

## 2. Units and balance ranges

- **Time: 60 ticks = 1 second.** (Aatrox's 600-tick buff is described in-game as 10.0 s.)
  `duration`, `cooltime`, `start_timing`, buff `tick`, `Stun.duration`, `Delayed.tick` are ticks.
- **Distance:** melee attack range 23000-30000, ranged 40000-80000, typical AoE radius
  25000-40000, projectile speed 3000-7000. Roughly 1000 units per sprite pixel *(inferred)*.
- **Ratios are percentages:** `attack_ratio: 120` = 120% AD.
- `move_speed` 900-1200; `*_mult` buff fields are percentages (`move_speed_mult: -30` = 30% slow).

Base game ranges (median [IQR] (min-max), 68 champions) - rebalance ported heroes into these:

| Category (n) | attack | growth | magic_power | growth | hp | growth | defence | mr | move | attack range | atk cooltime |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Melee (20) | 95 [80-100] | 19 | 0 | 0 | 1000 [950-1100] | 100 | 30 [30-40] | 25 | 1000 | 25000 | 65 |
| Range (11) | 100 | 20 | 0 | 0 | 900 | 90 | 20 | 15 | 900 | 60000 [50k-60k] | 60 |
| Magician (15) | 80 | 6 | 40 | 20 | 900 | 100 | 20 | 20 | 900 | 60000 | 90 |
| Assassin (10) | 120 | 30 | 0 | 0 | 900 | 80 | 25 | 15 | 1100 | 23000 | 50 |
| Util (12) | 80 | 6 | 30 | 15 | 900 | 100 | 20 | 20 | 1000 | 60000 [25k-60k] | 90 |

Growth for defence is ~7-9, magic_resistance ~3-5, move_speed ~9-14.

Cooldowns (ticks, median [IQR]): skill 240-420, skill2 300-480, ult 2400-3600 (almost always
3000). Attack `duration` ~20-30 with `start_timing` ~13-18.

## 3. Actions

```json
"skill": {
  "action_name": "skill",            // sprite tag played for this action (must exist!)
  "description": "#asset/base/text/champion?description.<id>.skill",
  "duration": 20,                    // ticks the caster is busy
  "cooltime": 300,                   // ticks
  "cooltime_use_count": 3,           // optional: charges / recasts (base Nightmare)
  "start_timing": 8,                 // tick at which `effect` fires (<= duration)
  "cancelable": false,
  "range": 50000,                    // AI casts when a valid target is within range
  "casting_type": "Direction",       // Targeting | Direction | Position | None
  "casting_target": "EnemyWithoutTower",
  "attack_type": "Skill",            // BaseAttack for `attack`, Skill otherwise
  "can_use_with_move": true,         // optional
  "effect": { ... }                  // effect tree (section 4)
}
```

- `casting_target`: `Enemy`, `EnemyWithoutTower`, `EnemyChampion`, `EnemyChampionInCC`,
  `EnemyChampionRecentlyAttacked`, `AllyOnlySelf`, `AllyChampion`, `AllyNotSelf`,
  `AllyChampionInCC`, `BothWithoutTower`, `BothChampion` (the engine also has `Ally`, `Both`, `None`).
- **Which ally gets an ally skill** *(read from the mod SDK's compiled `game_core`, not yet seen
  in game)*: `AllyNotSelf` is an allied champion other than the caster (no minions), `AllyChampion`
  includes the caster, `Ally` is any allied unit (`CastingTarget::check`). The battle AI makes one
  candidate per valid ally for skill, skill2 and ult (`utils::battle_ally_action`) and scores it;
  a heal is worth `min(heal, target max HP - HP)` on that target (`Effect::expected_heal_target`),
  so heals should go to the most injured ally and a full-health ally is worth 0. No casting target
  means "lowest health": base Priest's ult finds that ally in hard-coded logic
  (`lowest_hp_ally_in_range`). Heal, RangeEffect, Combine, Delayed, WithSelf and the projectiles
  all report their expected heal, so a heal nested in them still counts.
- Self-buffs that should fire "in combat" work best as `casting_type: None` +
  `casting_target: EnemyChampion` + a `range` (cast when an enemy champion is that close) - this
  is how Nocturne's shroud is wired. `AllyOnlySelf` + range 0 also exists (Aatrox ult).
- `action_name` may be any tag: `ult_cast`, `skill2_dash`... Base uses this heavily.
- `can_use_with_move` lets the unit cast without stopping. No base skill uses it (LoL Reborn
  does), and it does not let the unit walk during a `CasterAnimation`.
- `patch_type_name` only appears in base data (patch notes); skip it.

## 4. Effect catalogue

Every effect is `{"type": "<Type>", ...fields}`. Counts = uses across base + 52 pack champions.

**Flow**
| Type | Fields | Meaning |
|---|---|---|
| Combine | effects[] | run all, in order |
| Delayed | tick, effects[] | run after `tick` |
| WithSelf | effects[] | apply to the caster *(inferred)* |
| SwitchByBuff | buff_name, effect_buff, effect_none | branch on whether the **caster** has the buff |
| SwitchByLevel3 | effect_start, effect_level3 | level-based branch, seen once *(semantics unverified)* |
| RandomTarget | range, casting_target, from_projectile, effects[] | pick a random valid unit in range, apply effects to it |
| RangeEffect | shape, target, apply_type:"AroundCaster", effects[] | instant area around the caster |

**Damage and sustain**
| Type | Fields | Meaning |
|---|---|---|
| Attack | damage, attack_ratio, hp_ratio, target_hp_ratio, attack_effect_type:"Target" | physical: damage + ratio% AD (+% max-HP parts) |
| ApAttack | damage, attack_ratio, hp_ratio, target_hp_ratio | magic: damage + attack_ratio% **AP** |
| FixedAttack | damage, attack_ratio, target_hp_ratio | true/fixed damage (e.g. 10% target max HP) *(inferred)* |
| Heal | amount, attack_ratio, ap_ratio, heal_type: Caster\|Ally\|Any | heal (`Caster` heals the caster even inside a projectile that hit an enemy; `Ally` the allied target). No field scales with the target's missing health |
| Shield | amount, attack_ratio, ap_ratio, hp_ratio, tick | shield for `tick` |
| AddCasted | casted_type: Fire\|Poison, duration, period, effects[] | damage-over-time: run effects every `period` |

`attack_effect_type` on the three attack effects: `Target` (every pack writes it) hits the
effect's own target with no team check, so `WithSelf` + `FixedAttack` damages the caster;
the engine's other kinds are `EnemyTarget` (skips the caster's team) and `EnemyAll {..}`.
`FixedAttack` with only `target_hp_ratio` has an expected damage of 0 for the AI (it is
estimated from the caster's stats), which keeps a health cost out of the skill's score.

**Buffs** - `AddBuff {buff_state}` (on target), `AddCasterBuff {buff_state, only_to_enemy}`
(on caster), `RemoveCasterBuff {name}`. See section 5.

**Crowd control / states** (durations in ticks)
`Stun {duration}`, `Airborne {duration}`, `Bind {duration}` (root), `Taunt {duration}`,
`Banish {duration, end_effect_name?, lock_effect_name?}` (removed from play),
`Charm {tick}`, `Fear {tick}`, `Knockback {speed, tick}`, `Pull {speed, tick}`, `Grab {speed, tick}`,
`BlockAttack {tick}` (disarm), `BlockSkill {tick}` (silence), `BlockMoveSkill {tick}` (no dashes),
`Invisible {tick}` (target cannot be seen/targeted - Nocturne ult applies it to allies),
`CasterInvisible {tick}` (base Nightmare).

**Movement**
| Type | Fields | Meaning |
|---|---|---|
| MoveTo | speed, range, end_effects[] | dash in cast direction/position, then end_effects |
| MoveToTarget | speed, range, end_effects[] | dash onto the target, then end_effects |
| MoveBack | speed, tick | hop backwards |
| RushTime | speed, tick, range, casting_target, penetrate, applied_effects[] | charge for `tick`, hitting units passed |
| RushMoveToBack | speed, applied_effects[] | dash to behind the target *(inferred)* |
| DirTeleport | moved | blink `moved` units in the cast direction |
| Teleport | - | teleport to target *(inferred)* |

**Projectiles and zones** (all take `name` -> bound in `view_projectiles`; `applied_effects` items are `{"casting_type": "Targeting", "effect": {...}}`)
| Type | Extra fields | Meaning |
|---|---|---|
| TargetProjectile | speed, y_offset, applied_target | homing on the target |
| AutoTargetProjectile | speed, range | seeks targets itself |
| TargetSplashProjectile | speed, range, y_offset | homing, then splash |
| LinearProjectile | speed, range, shape, penetrate, end_effects, y_offset | skillshot |
| BackToCasterLinearProjectile | speed, range, shape, penetrate, end_effects | boomerang |
| ParabolicProjectile | travel_time, range, shape, range_effect_name, end_effects | lobbed to a spot |
| LineRangeProjectile | width, length, delay, apply | line/rectangle telegraph, hits after `delay` |
| RangeProjectile | shape, delay, apply, end_effects | circle at target spot after `delay` |
| RangePeriodProjectile | shape, tick, period, first_delay, end_effects | persistent zone ticking every `period` |
| ApplyInProjectile | shape, tick, follow_caster | aura / zone that can follow the caster |

`applied_target`: `Enemy`, `EnemyWithoutTower`, `EnemyChampion`, `EnemyChampionInCC`, `Ally`,
`AllyChampion`. Shapes: `{"Circle": {"radius": N}}`, `{"Rect": {...}}` (rare).
RangeEffect `target` also accepts `AllyOnlySelf`, `AllyNotSelf`.

**Presentation**
`ViewEffect {name}` (play a `view_effects` animation on the target/point),
`CasterViewEffect {name}` (on the caster), `CasterAnimation {name, tick}` (force a sprite tag on
the caster for `tick`; the caster stays in place meanwhile, so move it from the effect tree with
`MoveToTarget` / `MoveTo` / `RushTime`), `RemoveCasterAnimation {name}`, `Sfx {name}` (at caster),
`TargetSfx {name}` (at target). Base `ViewEffect` entries sometimes carry `range/speed/time/radius`.

**Base only - do not use in mods:** `Native` (calls hard-coded logic via `effect_ref`),
`ShrinkingBarrier`, `AddStatScaledBuff`, `Rush`.

## 5. buff_state

```json
{"name": "league_garen_q_haste", "duration": {"Time": {"tick": 90}}, "move_speed_mult": 35}
```

`duration`: `{"Time": {"tick": N}}` | `"Permanent"` | `"WithShield"` (lasts while the shield
holds). Some pack buffs omit it - set it explicitly.

`hp_regen` is health per second (the base UI: "HP Regen per Second"). `undying: true` keeps the
unit alive while the buff lasts (Touhou Mokou's ult, LoL Reborn Sion's R).

Fields seen (count across packs): `range` (attack range bonus, 278), `move_speed_mult` (235),
`attack_speed_mult` (160), `magic_power_mult` (122), `attack_mult` (115), `hp_mult` (115),
`base_attack_enemy_max_hp_damage` (on-hit % max HP, 111), `skill_cooldown_mult` (110),
`damaged_reduce` (% less damage taken, 74), `defence_mult` (72), `magic_resistance_mult` (70),
`vamp` (lifesteal %, 66), `toughness` (tenacity, 58), `damage_reflect` (56), `cc_immune` (bool),
`is_hidden` (bool, hide from UI), `radius_mult`, `can_stack` + `max_stack`, flat `attack`
`defence` `magic_resistance` `hp` `magic_power` `crit_chance` `hp_regen`, `ignore_wall`,
`undying`, `damaged_amplify`, `ult_cooldown_mult`, `defence_penetration`, `heal_reduce`.

## 6. View bindings

Effects only simulate; nothing is drawn unless a view entry with the **same name** exists in
the same champion file.

```json
"view_projectiles": [{"type": "Animated", "name": "league_garen_wave", "anim": "asset/league/fx/league_garen_wave", "tag": "fly", "repeat": true, "z": 0}],
"view_effects":     [{"type": "Animation", "name": "league_garen_q_hit", "anim": "asset/league/effects/league_garen_hits", "tag": "q", "z": -1, "is_follow": true}],
"view_buffs":       [{"type": "Animated", "name": "league_garen_judgment", "anim": "asset/league/effects/league_garen_spin", "tag": "loop", "z": 1}]
```

- `view_projectiles` <- the `name` of any projectile/zone effect. Also `{"type": "Sprite", "name", "sprite"}` for a static image.
- `view_effects` <- `ViewEffect` / `CasterViewEffect` names (and `range_effect_name`).
- `view_buffs` <- `buff_state.name`. `{"type": "ThreePhase", "pre_tag", "loop_tag", "remove_tag"}` gives an intro/loop/outro buff.
- `z` < 0 draws under units (ground decals, zones); `is_follow` makes an effect follow its unit.
- Every `anim` + `tag` must exist. Name typos fail silently - LoL Reborn's Nocturne binds
  `nocturne_attack_hits` while the effect is `nocturne_attack_hit`, so that hit never shows.

## 7. Patterns that work

**Every Nth basic attack is empowered (passive).** Chain `SwitchByBuff` on hidden stack buffs
(template `templates/mymod/champion/hero.data_champion` does 3 hits; Nocturne does 6):
```json
{"type": "SwitchByBuff", "buff_name": "x_stack_2",
 "effect_buff": {"type": "Combine", "effects": [ <empowered hit>, {"type": "RemoveCasterBuff", "name": "x_stack_2"} ]},
 "effect_none": {"type": "SwitchByBuff", "buff_name": "x_stack_1",
   "effect_buff": {"type": "Combine", "effects": [ <normal hit>, {"type": "RemoveCasterBuff", "name": "x_stack_1"},
                   {"type": "AddCasterBuff", "buff_state": {"name": "x_stack_2", "duration": "Permanent", "is_hidden": true}} ]},
   "effect_none": {"type": "Combine", "effects": [ <normal hit>,
                   {"type": "AddCasterBuff", "buff_state": {"name": "x_stack_1", "duration": "Permanent", "is_hidden": true}} ]}}}
```

**Skill empowers the next attack.** The skill adds `x_ready` (Time buff); `attack` starts with
`SwitchByBuff x_ready` -> empowered effect + `RemoveCasterBuff x_ready`.

**Recast / charges.** `cooltime_use_count: N` on the action (base Nightmare fires 3 shards).
For different 1st/2nd casts, add a short `x_recast` buff on first cast and `SwitchByBuff` on it.

**Dash then hit.** `MoveTo` (direction) or `MoveToTarget` (unit) with `end_effects:
[ViewEffect, RangeEffect{Attack, Stun}]`. Add `CasterAnimation` with a dash tag for the travel.

**Telegraphed AoE.** `RangeProjectile {delay, apply}` / `LineRangeProjectile {width, length,
delay, apply}` / `ParabolicProjectile {travel_time}`; or `ViewEffect warning` + `Delayed {tick}
RangeEffect`. `apply` is how many ticks the area stays live after `delay`; each unit is hit once
(base spellbreaker Q: delay 8, apply 3, one hit per its tooltip).

**Cone / fan (Ashe W).** No projectile takes an angle, but `LineRangeProjectile` in a
`casting_type: Direction` action is a rectangle from the caster toward the target, and its view
sprite is centred on the rectangle and turned to the cast direction: drawn pointing right from
x = -length/2 to +length/2 (measured on LoL Reborn's Swain Q fan, Lux R and Jhin W sprites). So a
fan sprite with its apex at x = -length/2 starts at the caster. The hit area stays a rectangle;
draw the fan a little wider than `width` (oppi's Swain does). league_ashe W: width 45000, length
80000, delay 14, apply 3, 9 arrows over +-28 deg, 7 frames x 40 ms, view `repeat: false`.

**Zone / aura.** `RangePeriodProjectile {tick, period}` for a placed field;
`ApplyInProjectile {follow_caster: true, tick}` for an aura around the hero.

**Delayed detonation (Gragas Q, Lux E).** A `RangePeriodProjectile` whose `period` is longer than
its `tick` hits once, at `first_delay`; its view (`repeat: false`) carries the fuse and the
explosion, timed so the blast frame lands on `first_delay` (LoL Reborn Gragas: a
`ParabolicProjectile` whose `end_effects` hold the zone with tick 106, first_delay 75, a 1.75 s
view). A second zone with a short `period` and a short slow buff is the slow field
(league_lux E: field tick 60 / period 10 / 15-tick slow, blast tick 84 / first_delay 60). Pack
authors match a zone's view length to its lifetime (Gragas 1767/1750 ms, Utsuho 1500/1500, Aatrox
633/640), so a view appears to end with its projectile *(inferred)* - draw the blast inside it.

**Long laser with a telegraph (Marisa, Lux R).** Split the look from the damage: one
`LineRangeProjectile` with empty `applied_effects` and a long `delay` carries the view (thin
line, charge, beam, fade), a second one with the same shape and a shorter `delay` deals the damage
(Touhou Marisa: visual delay 120; league_lux R: visual delay 55, damage delay 28, 240000 x 16000).
The view is drawn at the unit's pivot height and turned to the cast direction, so keep the beam
centred vertically in its canvas (an offset would flip when she fires to the left) *(inferred)*.

**Burn / poison.** `AddCasted {casted_type: Fire, duration, period, effects: [ApAttack]}`.

**Untargetable window.** `RangeEffect` on `AllyOnlySelf` applying `Invisible {tick}`, plus a
caster buff with `cc_immune` / `damaged_reduce` if needed.

**Channel with its own animation.** `CasterAnimation {name, tick}` + `Delayed` hits +
`RemoveCasterAnimation` at the end (Nocturne ult, Marisa laser).

**Spin that keeps chasing.** The forced animation holds the caster still (seen in-game: a 3 s
spin with only `can_use_with_move` stood in place), so give every `Delayed` pulse a short dash next
to its `RangeEffect`: `RandomTarget {range: 60000, casting_target: EnemyChampion, effects:
[MoveToTarget {speed: 1400, range: 60000, end_effects: []}]}`. Re-pick the target on every pulse:
chasing only the cast target left Garen spinning in place once it died - at once when it was a
minion. Cast it with `casting_target: EnemyChampion` so it opens on champions; minions still take
the spin damage. See league_garen E.
Once the dashes worked, the user saw Garen chase *without* turning: one 180-tick `CasterAnimation`
issued at the start did not survive the dashes. Base Nightmare plays its forced animation from the
dash's `end_effects`, so league_garen E now re-issues `CasterAnimation spin` on every pulse (after
its `RandomTarget`) and in each `MoveToTarget`'s `end_effects`, each lasting until the next pulse
*(inferred: a dash ending drops the forced animation; not yet confirmed in-game)*.

**`MoveToTarget` needs a target.** It dashes to the action's target, so use it in `Targeting`
actions (Nocturne R, Gragas E). Under `casting_type: None` there is none and nothing moves (seen
in-game); LoL Reborn Jax Q wraps it in `RandomTarget {casting_target, range}` instead.

**Multi-hit on random enemies.** Several `Delayed` blocks each holding a `RandomTarget`.

**Projectiles at random enemies.** `RandomTarget {range, casting_target, effects:
[TargetProjectile]}` fires from the caster at the picked unit (LoL Reborn Ezreal E). A unit can be
picked more than once. league_ashe W started this way (one arrow at the target plus four random
ones); the user saw homing arrows, not League's cone, so it became the fan above.

**Dash to whoever the skillshot hit (league_leesin Q2).** A projectile's `applied_effects` run
with the hit unit as target, so a `MoveToTarget` there dashes the caster to it (LoL Reborn
Nautilus Q pulls itself in this way). Lee Sin wraps it in `Delayed {tick: 12}` (the mark shows
first) with `Sfx`, the dash and `CasterAnimation q2` inside; the dash's `end_effects` deal the
second hit. The action's `duration` covers wind-up, flight and delay (44 ticks). *(inferred
from the pack; not yet seen in-game)*

**Kick it back into the others (league_leesin R).** `Targeting` on an enemy champion: `Attack` and
`Knockback {speed: 3000, tick: 18}` on the target, plus a `LinearProjectile` toward it with
`penetrate: true` at the same speed (LoL Reborn Nautilus R knocks up along a line this way). The
projectile starts at the caster, a melee range behind the flying target, so it keeps that gap and
hits (`Airborne`, damage) only what the target flies past; its range stops the circle short of the
landing spot. *(inferred: Knockback pushes away from the caster at a constant speed)*

**Heal an ally at a health cost (league_soraka W).** `Targeting` + `AllyNotSelf`: `Heal
{heal_type: Ally}` on the target, then a 3-tick caster buff with `undying: true` and
`WithSelf {FixedAttack {damage: 0, target_hp_ratio: 8, attack_effect_type: Target}}` - 8% of her
own max health that can never kill her (League forbids the cast below 5% health). *(inferred from
the engine code; not yet seen in game)*

**Heal every allied champion (league_soraka R).** `Targeting` + `AllyChampion` with range 960000
(base Priest's ult range) and `RangeEffect {radius: 960000, target: AllyChampion}` around the
caster. Cast as `None` on `AllyOnlySelf` (Touhou Reimu, LoL Reborn Alistar) the AI fires it as soon
as it is ready, full health or not; a target lets the heal score above (0 at full health) decide.

**Fold an ability that has its own, longer cooldown into another (league_soraka E on Q).** The
host skill starts with `SwitchByBuff` on a hidden caster buff that lasts the folded ability's
cooldown: without it, cast the full version and add the buff; with it, cast the plain skill.
Soraka's star falls every 8 s, the Equinox field it leaves at most every 16 s (League: 8 s / 16-20 s).

**Once per cast, however many are hit (league_soraka Q's Rejuvenation).** A projectile's
`applied_effects` run once per unit hit; wrap the effect in `SwitchByBuff` on a short hidden caster
"lock" buff that the effect itself adds first, so the second and later hits of the same cast find
the lock. A separate projectile with `applied_target: EnemyChampion` and no view keeps minions from
triggering it.

**Burst where a skillshot stops.** `LinearProjectile {penetrate: false, applied_target:
EnemyChampion}` stops on the first champion; its `end_effects` run where it stopped, so a
`RangeProjectile {delay: 1, apply: 1, shape}` there is the splash (LoL Reborn Jinx R, Fizz R;
league_ashe R). It also fires at the end of the range when nothing was hit.

## 8. Gotchas

- `action_name` / `CasterAnimation.name` must be real sprite tags. Two LoL Reborn heroes use
  `action_name: "skill"` while their sprites only have `skill1`.
- `SwitchByBuff` checks the caster; the buff must be added somewhere in the same kit.
- Keep `start_timing <= duration`; long channels need a long `duration` (or `Delayed` effects).
- Use namespaced names for every buff/projectile/effect (`league_garen_*`) - names are global-ish
  and collisions with other mods are hard to debug.
- Custom sounds must be injected with override entries or `Sfx` will not find them
  (see `text-audio.md`).
- The engine plays `<champion id>_attack` on every basic attack by itself; never play that name
  from the effect tree too (see `text-audio.md`).
- A buff's view can outlive its unit: Garen died mid-spin and the whirl of his 3 s caster buff
  stayed on the body (no view_buffs option covers death). For a purely visual timed effect,
  play `CasterViewEffect` on a timer instead (one per `Delayed` pulse, `is_follow: true` in
  `view_effects`); keep buff views for states that must vanish on consumption (Q ready).
- Run `python scripts/lint_mod.py <mod>` after every edit.
