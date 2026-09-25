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

Plain downscaling of HD art fails the checks (hundreds of colours, soft edges, no outline).
Generated art passes them only through the import below.

## Generated art (image-model strips)

The route used for Garen in TFM2-League-Heroes: prompts in `assets/source/<hero>/PROMPTS.md`,
16 generated PNGs (1 reference, 9 animations, 6 effects), `tools/art/import_<hero>.py` built on
`scripts/strips.py`. What mattered:

- **Prompts.** One row of N frames per animation, real transparent background, feet on the same
  line in every cell, 3/4 view facing right. Generate a reference sheet first and attach it to
  every character prompt, or the hero drifts between animations.
- **Pose references from the source game.** Without one the model invents the motion: Garen's
  first run trailed the sword and his idle rested it on the shoulder, while in League both hold
  it forward at the waist - the user spotted it at once. Render the real clips (for LoL:
  `tools/lol/pose_ref.py` in TFM2-League-Heroes, reads SKN/SKL/ANM from the local client) and
  attach them as a second image: "copy each frame's pose, draw it like the first image". Keep
  such renders local; they show the game's model. Effects: separate strips,
  centred or with a fixed impact point, no outline, empty centre for rings around the hero.
- **Frames are not on a grid.** The model shifts the body inside its cell to fit a long weapon,
  and the spacing drifts (Garen: the body moved up to 13 px at game scale, the spacing
  drifted about 0.5 px per frame). Split
  at empty columns and keep connected blobs whole (`split_strip`); never place frames by cell.
- **Scale per strip.** Measure hair-to-soles on a standing frame of each strip. 36 px suits a big
  human (base humans ~31 px, the ogre ~38); 42 px looked like a giant next to base champions.
- **Horizontal pivot per frame.** Line the lowest ~12 px of legs up with idle frame 0
  (`leg_band` + `best_shift`); loops that turn or run (spin, run) are pinned by the head. A sword
  tip, smear or burst touching the ground gets matched as a foot: place those frames by the drawn
  spacing, corrected like their aligned neighbours, then nudge so one foot stays planted.
  Airborne frames keep their height above the strip's ground line.
- **Pixels.** Premultiplied area downscale, alpha cut 0.5, one median-cut palette for all body
  frames (64 colours), then a 1 px near-black edge except on glowing pixels, then drop lonely
  pixels. Effects: alpha cut 0.4 plus tiny-spark keeping, own 32-colour palette, no outline.
- **Effect anchors.** Effect and buff frames are drawn centred on the unit's pivot, 11.5 px above
  the feet (base: `levelup_effect` ring at +9..+16, `shield_receive_effect` bubble -22..+13).
  Ground rings at about +10, hits and shields at -3..-6, overhead marks around -25. Time the
  impact frame to the damage tick (wrap the `ViewEffect` in `Delayed`).
- **Review before shipping.** Per-strip sheets with the idle silhouette overlaid, `metrics`,
  a side-by-side with base champions at 1x and 3x, and a scripted showcase against a dummy.

## QA checklist

- [ ] `metrics` passes: height, outline, 0 semi-alpha, colour count
- [ ] `idle`, `run`, plus every `action_name` and `CasterAnimation` name exists as a tag
      (`lint_mod.py` checks this against the data); `hit` and `dead` recommended
- [ ] feet stay on the same row in all frames; hero stands level with base champions in-game
- [ ] readable at 1x on the olive-grey arena; signature colour visible
- [ ] VFX visible on both light and dark map areas; no black outline on VFX
- [ ] three icons per hero, one consistent style across the pack (24x24 glyph or 64x64 art)
