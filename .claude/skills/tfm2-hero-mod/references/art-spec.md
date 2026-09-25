# Art spec: sprites, VFX, icons

The goal every successful pack states the same way: custom sprites that "do not stray too far
from the base game aesthetic" (oppi). The numbers below are measured, not eyeballed:
**base** = all 78 base champion sprites (from `bundle.game_data`); **oppi** = the 12 hand-made
`.aseprite` champions in LoL Reborn (Nocturne, Jax, Lulu, Lux, Vi, Jinx, Caitlyn, Swain, Sion,
Alistar, K'Sante, Galio). The Dota 2 Heroes pack (Axe, Zeus, Huskar, Shadow Fiend, Elder Titan)
uses the same hand and rules. Re-measure anything with `scripts/tfm2_ase.py metrics`.

## Numbers

| Property | Base game | oppi packs | Rule for new heroes |
|---|---|---|---|
| Character height (idle, feet to top) | median 35 px, IQR 34-37, big units 41-45 | 33-39, tanks 44-51 | 34-38 px; bruisers/tanks up to ~45 |
| Facing / view | right, 3/4 side | right, 3/4 side | always face right |
| Proportions | chibi, ~3 heads tall | ~3 heads, less deformed | big head, readable hands, oversized signature prop |
| Silhouette outline | 1 px near-black on 100% of edge (median) | 93-100% | 1 px #000000-#0a0a0a around the whole silhouette |
| Interior near-black pixels | 15% median (1-51) | 20-45% | use black for inner lines and deepest shadow |
| Colours per idle set | median 25 (IQR 21-29, max 39) | 49-120 | 25-120; >160 means painted/downscaled art |
| Semi-transparent body pixels | 0 | 0 | 0 - no anti-aliasing, no soft shading |
| Shading | 2-3 hard steps | 3-4 hard steps, darker overall | hard cel steps, light from upper front |
| Palette | muted, earthy | muted base + 1-2 saturated signature colours | pick 1-2 signature colours per hero |

oppi's look in one line: base-game proportions and outline, but darker, denser rendering and
more colours - dark heroes (Nocturne, Shadow Fiend) are near-black bodies with glowing accents.

## Animation tags and timing

| Tag | Base (median frames @ ms) | oppi | Notes |
|---|---|---|---|
| idle | 4 @ 140-200 | 7 @ 100 | breathing / weapon sway |
| run | 8 @ 80 | 6-9 @ 75-100 | |
| attack | 5 @ 80 | 6-8 @ 75-85 | anticipation -> hit frame -> recovery |
| skill / skill1, skill2, ult | 5 @ 80 | 6-13 @ 80-100 | any name, but it must equal the action's `action_name` |
| hit | 1 @ 100 | often omitted | recommended |
| dead | 10 @ 100 | 6 @ 100 (often omitted) | recommended |
| extras | `ult_dash`, `ult_pre`, `ult_loop`, `skill2_attack`, `*_projectile`, `*_effect` | `attack_enhanced`, `ult_cast`, `ult_dash` | used by `CasterAnimation` or view bindings |

The hit frame of `attack` should land around the action's `start_timing` (e.g. attack
`duration` 20-24 ticks = 0.33-0.4 s, hit at tick 13-15).

## Canvas and anchoring

- Base exported frames are cropped with odd sizes so the pivot pixel sits in the middle; the
  **feet (bottom edge) are 11.5 px below the frame centre** in essentially all 78 sprites, and
  `champion_view` offsets (face y ~ -34, center y ~ -12) are measured up from the feet.
- oppi's `.aseprite` canvases (70x70 to 139x109) keep the body horizontally centred with the
  **feet 17-20 px below the canvas centre** (tanks further down).
- Nobody has documented the engine's exact rule for `.aseprite` canvases. Pick one convention
  per pack, keep it identical for every frame, and verify in-game by standing the hero next to a
  base champion; adjust the canvas (not the art) until the feet line up.
- Never let the character drift between frames: keep the feet row fixed in idle/attack/skills.

## Aseprite file conventions (what the game loads)

- RGBA colour mode. One file per hero: `champions/<hero>.aseprite`, every animation a tag.
- Layers used by oppi: `body`, `body2`, `effect`, `effect2`; hidden reference layers stay in
  the shipped files, so hidden layers are evidently not rendered *(inferred)*.
- Tag names are the animation names. Frame durations come from Aseprite's per-frame duration.
- Effects: one `.aseprite` per effect in `effects/`, `fx/` (projectiles) or `buffs/`, each with
  its own tag(s) (`loop`, `hit`, `impact`, `skill2`...).
- The engine also reads exported `#sheet.png` + `#anim.fanim` pairs (base format).

## VFX spec (oppi)

- Saturated, bright, often a white-hot core with 2-3 step colour ramps (blue->cyan->white,
  gold->pale gold->white, crimson->pink->white). **No black outline** - the opposite of bodies.
- Mostly opaque pixels; semi-transparency only for fades, shields, ghostly clones.
- 5-10 frames @ 65-125 ms; impact frames can flash white silhouettes.
- Sizes: projectiles 25-75 px, impacts 100-250 px wide, ground zones drawn with `z: -1/-2`.
- Area rings: the base game draws them as **true circles centred on the frame centre / unit
  pivot** (knight and shield_bearer `skill2_effect`, 74-128 px), not squashed ellipses. Radius
  in px ~ data radius / 1000 (LoL-pack zones: 34000 -> 29.5 px, 40000 -> 38.5 px).
- `z` in view bindings: the LoL pack uses -3..10; negative draws behind the unit, positive in
  front *(inferred from usage)*. A buff that should orbit *around* the hero (in front and
  behind) can stay in front and cut out the hero's body box from the back half of the orbit.
- Reuse base effects when they fit (`bundle_tool.py list --grep skill_effect/`).

## Skill icons

Two accepted styles:
- **Base game:** 24x24 pixel-art glyphs on a transparent background - one saturated hue in 2-3
  shades plus white highlights, a single bold symbol (slash, arrow, flame, mask), no outline.
  Packed in an atlas (`UI_aseprite/skill_icon#sheet.png` + `#data.sprite_sheet`, 355 icons).
- **oppi packs:** 64x64 PNG, square, full-bleed, the **official ability art of the source game
  downscaled** (500-900 colours) - instantly recognisable to fans of that game.

Either way three per hero: `<hero>_skill`, `<hero>_skill2`, `<hero>_ult` in `skill_icons`
(or one atlas + 3 tags via `skill_icon`).

## Reference-first workflow

The base game itself keeps high-res chibi concept art for its newest champions
(`asset/base/aseprite_resources/champions/reference/*` ~1024x1536). Work the same way:

1. Collect official art of the hero (splash, model turnaround, skill icons).
2. Make a chibi reference: ~3 heads, 3/4 facing right, signature prop exaggerated.
3. Block the silhouette at 35 px height; check readability at 1x on the arena colour.
4. Outline, flat colours from a 20-40 colour palette, then 3-4 step hard shading.
5. Animate idle -> run -> attack -> skills -> ult -> hit -> dead.
6. `python scripts/tfm2_ase.py metrics champions/<hero>.aseprite` and
   `python scripts/tfm2_ase.py render champions/<hero>.aseprite --out preview.png` to review.

Automatic downscaling of HD art almost always fails the checks (hundreds of colours, soft edges,
no outline); it can serve as a sketch layer, not as the final sprite. Text-to-image pixel
models (SDXL + pixel-art LoRA) were tried for hok_arthur and rejected by the user: the output
is ~128 px tall "RPG chibi", off-model, and cannot be animated consistently.

What worked for hok_arthur (this repo, `tools/art/`), without Aseprite:
- every body part is a hand-written pixel grid in a 30-40 colour palette (`arthur_parts.py`),
  auto-outlined, with a pivot at its joint; far-side limbs are the same grid one shade darker;
- a small rig places the parts per pose (hip, lean, leg angles, 2-bone sword arm, cape sway)
  and rotates weapons/limbs with RotSprite (Scale2x x3, rotate, sample) so lines stay crisp;
- swing smears, dash streaks and sword light are drawn into the body frames as solid shapes
  with hard colour ramps; the view effects use the same primitives (`fx_lib.py`);
- design from the in-game model as well as the splash: players recognise the model's colours
  (for Arthur: red cape, gold plate, silver sword), not the splash's details.

## QA checklist

- [ ] `metrics` passes: height, outline, 0 semi-alpha, colour count
- [ ] `idle`, `run`, plus every `action_name` and `CasterAnimation` name exists as a tag
      (`lint_mod.py` checks this against the data); `hit` and `dead` recommended
- [ ] feet stay on the same row in all frames; hero stands level with base champions in-game
- [ ] readable at 1x on the olive-grey arena; signature colour visible
- [ ] VFX visible on both light and dark map areas; no black outline on VFX
- [ ] three icons per hero, one consistent style across the pack (24x24 glyph or 64x64 art)
