# 生成提示词记录

原始规格见 PROMPTS.md。以下记录各图片最近一次候选生成使用的提示词；最终 PNG 经目视筛选，可能采用较早候选。参考图按原文另加真实透明通道要求。所有角色动画均指定同一 garen_ref.png 作为实际图片输入。

## garen_idle.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: IDLE, 6 frames, seamless loop. He stands with the greatsword resting on his right shoulder; subtle breathing (chest and shoulders rise and fall 1-2 pixels), the cape hem sways gently. Feet stay planted.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 6 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 6:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 6 square cells whose side is canvas_width/6, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_run.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: RUN to the right, 6 frames, seamless loop: body leaning forward, greatsword held low in his right hand trailing behind, cape streaming back, clear alternating leg strides (contact, passing, contact, passing), slight up-down bounce. The legs keep the same length and shape in every frame.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 6 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 6:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 6 square cells whose side is canvas_width/6, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_attack.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: BASIC ATTACK, 6 frames: 1 guard stance; 2 swings the greatsword up and back over his shoulder; 3 powerful diagonal slash forward and down, drawn with a bright silver-white arc smear; 4 impact, sword low in front, body leaning into the blow; 5 follow-through; 6 back to guard. Feet stay on the ground line.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the sword may reach toward the cell edges but must stay inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 6 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 6:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 6 square cells whose side is canvas_width/6, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_q_attack.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: DECISIVE STRIKE, a leaping overhead blow, 7 frames: 1 crouches low; 2 leaps up and forward with the greatsword raised high over his head in both hands, the blade glowing gold; 3 top of the leap; 4 comes down swinging; 5 IMPACT: the sword slammed down in front of him with a bright gold flash at the blade; 6 kneeling recovery; 7 stands back up in guard. The ground line is the same in every cell (he is in the air in frames 2-4).
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height when standing, ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 7 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 7:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 7 square cells whose side is canvas_width/7, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_skill.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: BATTLE CRY, 4 frames: 1 raises the greatsword toward the sky; 2 shouts, mouth open, the blade flashing gold; 3 holds the pose, cape blown back; 4 lowers the sword into a forward charging stance.
Layout: one horizontal row of 4 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 4 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 4:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 4 square cells whose side is canvas_width/4, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_spin.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: JUDGMENT SPIN, 8 frames, seamless loop: he spins in place holding the greatsword straight out at waist height with both hands, one full 360-degree turn over the 8 frames (facing right, front-right, front, front-left, left, back-left, back, back-right), cape swirling around him. Feet stay on the ground line.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the extended sword must stay inside its cell. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 8 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 8:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 8 square cells whose side is canvas_width/8, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_ult.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: DEMACIAN JUSTICE, calling down a giant sword, 8 frames: 1-2 lifts the greatsword high, pointing at the sky; 3 the blade blazes with golden light; 4 holds; 5-6 brings the sword down and points it forward at the enemy, commanding the strike; 7 holds; 8 back to guard.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 8 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 8:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 8 square cells whose side is canvas_width/8, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_hit.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: HIT REACTION, 2 frames: 1 flinches backward from a blow, grimacing, sword lowered; 2 recovering. Feet stay on the ground line.
Layout: one horizontal row of 2 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 2 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 2:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 2 square cells whose side is canvas_width/2, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_dead.png

```text
First open and inspect the local master reference using view_image: C:/Users/OWNER/Documents/Codex/2026-09-25/your-turn-generate-16-images-with/outputs/garen/garen_ref.png . You MUST attach this exact image as an input reference to the image_generation tool when generating this animation, using referenced_image_paths or the tool's equivalent reference input. Do not merely describe it from memory. Same character, same colors and proportions as the attached reference. This file is reference input only; do not edit it.

Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: DEATH, 7 frames: 1 staggers; 2 drops to one knee; 3 plants the greatsword in the ground to hold himself up; 4 holds, head bowed; 5 slumps; 6 falls onto his side; 7 lies still on the ground, sword beside him.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. Same character scale in every cell (about 60% of the cell height when standing), ground line at 88% of the cell height. Transparent background (if not possible: solid #FF00FF magenta).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 7 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing priority: the complete sword, cape and entire body in EACH frame must have transparent clearance from both neighboring frames and from the outer canvas edges. If the canvas cannot be 7:1, do NOT scale figures up to fill its height. Instead imagine a centered horizontal band of 7 square cells whose side is canvas_width/7, leave extra transparent space above and below that band, and scale the figures to fit those virtual square cells. Each standing BODY height is about 55-60 percent of that square cell side, not 60 percent of the full canvas height. Keep the whole sword inside each square cell with at least 5 percent clear margin. Never crop the first cape or last sword.
```

## garen_fx_hit.png

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright white-hot core with a silver-blue and gold color ramp (#FFFFFF, #E8F4FF, #8FC6FF, #FFD65A, #F0A028).
Effect: a sword hit spark, 4 frames: 1 small white flash; 2 sharp silver-white slash spark with a few gold sparks; 3 shrinking spark, sparks flying outward; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, effect centered at the same point in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 4 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell.
```

## garen_fx_q_hit.png

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright white-hot core with Demacian gold and blue color ramps (#FFFFFF, #FFF6C8, #FFD65A, #F0A028, #E8F4FF, #8FC6FF, #3A7BE0).
Effect: DECISIVE STRIKE impact, 6 frames: 1 a heavy vertical downward slash of white-gold light appears; 2 bright flash where it lands, blue-white shock burst; 3 largest burst with gold sparks; 4 burst fading, a small grey-blue swirl (a "silenced" mark) appears above the impact point; 5 swirl turning, sparks falling; 6 swirl fading out.
Layout: one horizontal row of 6 equal square cells, the impact point at the same spot in every cell (center of the cell), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 6 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell.
```

## garen_fx_q_ready.png

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden color ramp (#FFFFFF, #FFF6C8, #FFD65A, #F0A028).
Effect: an empowered aura, 6 frames, seamless loop: small golden light motes and short golden streaks rising upward around an EMPTY character-sized space in the middle (a person will stand there), plus a thin glowing golden ring on the ground at the bottom (flat ellipse). Subtle, not covering the center.
Layout: one horizontal row of 6 equal square cells, same position in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 6 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell.
```

## garen_fx_courage.png

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, white-gold and pale blue color ramp (#FFFFFF, #FFF6C8, #FFD65A, #E8F4FF, #8FC6FF).
Effect: a protective shield bubble, 6 frames, seamless loop: the OUTLINE of a round barrier (a circle of white-gold light, 2-3 pixels thick) around an EMPTY center where a character stands, with a few small sparkles moving around the ring and a brighter glint sliding along it.
Layout: one horizontal row of 6 equal square cells, the ring centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 6 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
```

## garen_fx_spin.png

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, steel-blue and white color ramp with a little gold (#FFFFFF, #E8F4FF, #B8D8FF, #8FC6FF, #5A8FD8, #FFD65A).
Effect: JUDGMENT whirlwind, 8 frames, seamless loop: a flat ring of steel-blue and white sword-slash trails circling around an EMPTY center (a spinning knight stands there), seen from a 3/4 top-down angle so the ring is an ellipse about twice as wide as it is tall, with small sparks flying off; the slash trails rotate clockwise from frame to frame.
Layout: one horizontal row of 8 equal square cells, the ring centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 8 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
Framing: every effect, spark and ring must fit inside the middle 75 percent of its own frame's horizontal width, with transparent margins on both sides. No two adjacent effects may touch or overlap. The very first and very last effect must be completely visible with generous transparent canvas edge margins. For the spin effect each ellipse must remain twice as wide as tall.
```

## garen_fx_r.png

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright white-hot core with Demacian gold and blue color ramps (#FFFFFF, #FFF6C8, #FFD65A, #F0A028, #E8F4FF, #8FC6FF, #3A7BE0).
Effect: DEMACIAN JUSTICE, 9 frames: 1 a giant glowing golden-blue broadsword of light (Demacia style, winged gold crossguard) appears high in the sky, pointing down; 2 it plunges down with a light trail; 3 the tip hits the ground with a huge white-gold flash; 4 golden-blue explosion, a flat elliptical shockwave on the ground and a pillar of light, the sword stuck in the ground glowing; 5-6 the sword and pillar fade while the shockwave ring expands; 7-9 sparks and light fading away.
Layout: one horizontal row of 9 equal TALL cells (width:height = 1:2), the ground impact point at the same spot in every cell, near the bottom (about 85% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).

Production requirements: actual transparent RGBA PNG, not a painted checkerboard. Exactly 9 animation frames in a SINGLE horizontal row; never wrap to multiple rows. All frame cells must have identical dimensions. No numbering, text or grid lines. Keep every complete silhouette inside its own cell. Save the original image produced by the image_generation tool unchanged. Do not crop, slice, resize, rearrange, remove background, or otherwise modify its pixels with scripts: the user wants original GPT images and Claude will do the final slicing and normalization. If the generator cannot honor the extreme aspect ratio, keep exactly the specified number of separate poses in one horizontal row on its supported canvas.
```
