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
| run | 8 @ 80 | 6-9 @ 75-100 | the move loop; may be a walk (League Garen: 8 @ 117) |
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
- **Proportions: show them, don't only name them.** TFM2 heroes are ~3 heads tall with a big,
  flat-lit face (33-36 px heroes: head 12-13 px, 2x2 px eyes). Every Garen and Ashe prompt said
  "chibi", but the attached references (League renders, then the previous design sheet) were
  adult-proportioned, and the model followed the images: heads 1/5 of the height, faces two or
  three rows of skin without eyes in game, Ashe's also shaded by her hood - the user could not
  see either face. Attach a sheet of base heroes (idle + attack, 8x) to the design prompt, render
  the pose references with a big head (`pose_ref.py --head 2.0 --legs 0.8`), ask for a face that
  stays readable at 35 px (hood and bangs off the eyes), and check the design sheet's head size
  before generating any strip. The redraw (`assets/source/CHIBI_REDRAW.md`) came back right in the
  first round. After importing, `tfm2_ase.py face <sprite> --out face.png` puts the hero next to
  base champions at 1x and zoomed: look for the eyes before shipping. Counting skin-coloured
  pixels does not replace looking - the small-headed Garen scored more "skin" in his upper body
  than most base heroes, because his gold trim has skin tones.
- **Pose references from the source game.** Without one the model invents the motion: Garen's
  first run trailed the sword and his idle rested it on the shoulder, while in League both hold
  it forward at the waist - the user spotted it at once. Render the real clips (for LoL:
  `tools/lol/pose_ref.py` in TFM2-League-Heroes, reads SKN/SKL/ANM from the local client) and
  attach them as a second image: "copy each frame's pose, draw it like the first image". Keep
  such renders local; they show the game's model. Make the first and last frame of an action a
  half-way blend with idle (`pose_ref.py --frame "idle@0>attack@0:0.5"`) so the strip starts and
  ends near the idle pose, and render every clip of a hero from the same side (Ashe:
  `ashe_pose_*` in `assets/source/ashe/PROMPTS.md`).
- **Name the gait and time it from the clip.** The move tag is called `run`, but League's Garen
  marches: upright, 0.93 s a cycle. Prompted as a run, he came out leaning into a sprint at
  0.54 s and the user saw "running, not walking". Say WALK (upright, one foot always down) when
  the clip is a walk, and take the frame times from it (Garen: 8 frames x 117 ms).
- **Render the side that shows the chest.** Every base champion faces right with its front to the
  viewer. League's Garen idles with his chest toward his own right, so a right-front camera
  shows his back - round 2 came out as a back view and the user rejected it at once. Render his
  left side and flip it (`pose_ref.py --mirror`), check the face and crest are visible, and say
  "3/4 FRONT view ... never show his back" in the prompt. Effects: separate strips,
  centred or with a fixed impact point, no outline, empty centre for rings around the hero.
- **Frames are not on a grid.** The model shifts the body inside its cell to fit a long weapon,
  and the spacing drifts (Garen: the body moved up to 13 px at game scale, the spacing
  drifted about 0.5 px per frame). Split
  at empty columns and keep connected blobs whole (`split_strip`); never place frames by cell.
- **Props that leave the body cross the cells.** Lux's Final Spark wand floats a third of a cell
  to her right, so `split_strip` handed frame 5's wand and blast to frame 6. Split such a strip by
  blobs instead: a blob holding the body's signature colour (her navy bodysuit) is a body, every
  other blob (prop, glow, sparks) joins the nearest body on its left (`split_bodies` in
  tools/art/import_lux.py).
- **Scale per strip.** Every generated strip comes at its own size (Garen round 4: the Q strip at
  half of idle's size, battle cry and hit far bigger). Pick a frame in idle's pose (the ready
  stance most strips start or end in), render it next to idle at game size at a few scales and
  choose by eye - head widths and hair-to-soles numbers were off by up to 2x on small or glowing
  frames. 36 px suits a big human (base humans ~31 px, the ogre ~38); 42 px looked like a giant.
  For chibi strips, scale by the **head**: GPT's head-to-body ratio also drifts between strips
  (Ashe's redraw: ~10%), so matching heights makes the head grow and shrink - the thing the user
  notices. Correlate idle's head (crown to chin) over each frame at a range of scales; within a
  strip the best scale agreed to 0.03 wherever the match was sure (>0.85). Where the head turns or
  bows (Garen's attack and death) the match is unsure: compare face and hair width at source size
  instead (the frame resized by 1/scale next to idle's head).
- **Lunges.** League blends back to idle over ~0.2 s; a sprite snaps back at once. Garen's attack
  head track (a 15 px lunge) made him jump back every swing, so attack, Q and R keep 65-70% of
  League's travel around idle's head, like the round the user approved. Get the tracks with
  `pose_ref.py --frame ... --track <hero px> --track-ref <idle clip@0>` (same camera, `--mirror`,
  `--head`, `--legs` as the references); it reproduces the tracks measured by hand before.
- **One look per hero.** Strips from different generation rounds disagree on proportions (round
  1 Garen: big head, broad shoulders; round 3: smaller head for the same height). No scale hides
  it - in-game he visibly grew and shrank between animations. When the look changes, regenerate
  every strip in one batch with the newest frame as design and size reference.
- **Horizontal pivot per frame.** Line the lowest ~12 px of legs up with idle frame 0
  (`leg_band` + `best_shift`); loops that turn or run (spin, run) are pinned by the head. A sword
  tip, smear or burst touching the ground gets matched as a foot: place those frames by the drawn
  spacing, corrected like their aligned neighbours, then nudge so one foot stays planted.
  Airborne frames keep their height above the strip's ground line.
- **Better, for strips drawn from a League clip:** put each frame's head where League's skeleton
  has it at the same frame time and camera (Garen's lunges and leaps then match the game).
  Re-base clips that start away from the unit (Garen's R starts 12 px behind it), and pin the
  feet's midpoint instead for a spin whose drawn lean is smaller than the clip's, or the body
  wobbles.
- **Pixels.** Premultiplied area downscale, alpha cut 0.5, one median-cut palette for all body
  frames (64 colours), then a 1 px near-black edge except on glowing pixels, then drop lonely
  pixels. Effects: alpha cut 0.4 plus tiny-spark keeping, own 32-colour palette, no outline.
- **Thin bright details need a vote, not an average.** Ashe's strips were ~12 source px per game
  px with a thin crystal bow and silver hair on a black hood: the average turned her into brown
  mud, the hair grey and the bow black (all edge, so all outline). `strips.render_vote` gives each
  game pixel the one palette colour covering most of it, times a class weight (bow blue 2.2, hair
  2.3, skin and gold 1.3); build that palette with a median cut per colour class (the lavender
  hair otherwise merges into light skin) and pass the prop's colours to `outline(keep=...)`.
  `metrics` then reports a lower outline share - it is the prop's edge, check which colours.
- **Detail density: have the body drawn at the game's size.** A vote does not save a strip drawn
  ~100 blocks tall (GPT's "pixel art") and squeezed 3:1 into 34 px: Ashe and Lux shipped at 41-42
  colours per idle frame with 15-18% of pixels matching their right neighbour (15 base heroes:
  16-33 colours, 18-46%, median 32%; Garen's big armour stayed readable at 63 and 15%), and the
  user saw both blurry in game. A second round drawn at native size fixed it (TFM2-League-Heroes
  `assets/source/NATIVE_REDRAW.md`): the current game frames at 8x in 56x64 cells as pose
  references, base heroes at 8x for style, "34 squares tall, every pixel one 8x8 square, at most
  20 colours, 2x2-square eyes", the design sheet first. The model's own output drifts off the grid
  (block pitch 7.4-8.6 px, narrowed faces); have it cleaned to exact 8x8 blocks, check that, then
  read one pixel per block - no resampling, palette or outline pass (`tools/art/import_native.py`:
  18-19 colours, 29-31%). Record where each reference frame's pivot sits in its cell when the
  references are drawn (`native_refs.py` writes `<hero>_cells.json`) so each redrawn frame lands
  where the old one stood, and steady idle and run on the head column: frames placed by their
  bounding box twitched 1-2 px in those loops.
- **Effect anchors.** Effect and buff frames are drawn centred on the unit's pivot, 11.5 px above
  the feet (base: `levelup_effect` ring at +9..+16, `shield_receive_effect` bubble -22..+13).
  Ground rings at about +10, hits and shields at -3..-6, overhead marks around -25. Time the
  impact frame to the damage tick (wrap the `ViewEffect` in `Delayed`). Find a ring by its biggest
  connected blob: by row extent, motes rising at both sides make rows above the ring look wide.
  For effects drawn in place (bursts, marks, bubbles, ground fields) anchor each frame on its
  cell: GPT centres every frame in its equal-width cell (within 8 px on all seven of Lux's), while
  a frame's own box drifts with its loose sparks - take the cell centre plus the strip's median
  offset across, and one height for the strip. A single anchor in strip coordinates puts every
  frame at its own cell's distance from the pivot (Lux's first import: the hit walked 5 cells).
  Projectiles keep a per-frame anchor on their head (arrow tip, orb).
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
