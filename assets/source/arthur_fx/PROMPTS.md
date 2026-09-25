# Claude 提供的原始生图提示词

以下为本次使用的 8 组原始提示词。生成时另外强调单行、等宽分帧、固定锚点、帧内留白，以及禁止网格、文字和假透明棋盘格。第一张还明确要求 4:1 画幅；实际输出尺寸见 manifest.json。

## hit_spark.png

Sprite sheet, 4 frames in one horizontal row, equal square cells, effect centered at the same point in every cell: a small yellow-white sword-hit spark. Frame 1: tiny white flash. Frame 2: bright 8-point star burst with a short diagonal slash line. Frame 3: smaller star, a few gold sparks flying out. Frame 4: fading sparks. Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, white-hot core with gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## oath_slash.png

Sprite sheet, 5 frames in one horizontal row, equal square cells, effect centered at the same point in every cell: one golden diagonal sword slash on a target, from upper right to lower left. Frame 1: thin white line appears. Frame 2: thick golden crescent slash with white core and a small burst at the center. Frame 3: slash thinning, gold sparks. Frame 4: slash breaking into sparks. Frame 5: fading sparks. Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, white-hot core with gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## cross_slash.png

Sprite sheet, 7 frames in one horizontal row, equal square cells, effect centered at the same point in every cell: a big holy golden cross slash impact, an X made of two crescent sword slashes with a white-gold starburst in the middle. Frame 1: first slash line. Frame 2: first slash full with burst. Frame 3: second slash crosses it forming the X, largest burst and sparkles. Frames 4-5: slashes thinning, gold sparks flying outward. Frames 6-7: fading sparks. Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, white-hot core with gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## flaming_shield.png

Sprite sheet, 4 frames in one horizontal row, equal square cells, shield at the same position in every cell: a small golden heater shield with a lion head emblem (red eyes, navy blue center), wrapped in orange-gold fire, flames streaming to the left as if the shield flies to the right. The 4 frames are the same shield with flickering flames (seamless loop). Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, gold (#FFF6C8, #FFD65A, #F0A028, #C46818) and fire (#FFE26E, #FF9A2E, #E0501E). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## whirl_ring.png

Sprite sheet, 4 frames in one horizontal row, equal square cells, ring centered in every cell: a thin glowing golden energy ring, perfect circle seen from straight above, empty center, small flame wisps along the ring that move clockwise from frame to frame (seamless loop). Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## excalibur.png

Sprite sheet, 8 frames in one horizontal row, equal tall cells (width:height = 1:2), the ground impact point at the same spot near the bottom of every cell: a giant holy longsword made of golden light plunging point-down from the sky into the ground. Frame 1: glowing sword high at the top. Frame 2: descending with a light trail. Frame 3: blade tip hits the ground, huge white-gold flash. Frame 4: golden explosion, flat elliptical shockwave on the ground and a pillar of light. Frames 5-6: sword and pillar fading, shockwave ring expanding. Frames 7-8: gold sparks and dust fading. Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, white-hot core with gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## holy_seal.png

Sprite sheet, 4 frames in one horizontal row, equal square cells, seal centered in every cell: a glowing golden holy seal on the ground seen from straight above, a perfect circle with an outer ring of runes, an inner ring, and a sword-and-cross emblem in the middle, empty space between the rings. Frames pulse in brightness and the rune ring turns slightly (seamless loop). Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.

## slash_arc.png

Sprite sheet, 3 frames in one horizontal row, equal square cells, arc at the same position in every cell: a golden sword swing trail, a crescent-shaped arc smear from a downward diagonal slash, the arc opening to the left, bright white outer edge fading to gold then orange on the inside. Frame 1: short thin arc. Frame 2: full thick arc. Frame 3: thinning arc breaking into sparks. Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, white-hot core with gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.



# 质量复查后的重生成提示词

以下三张以本节重生成结果为最终交付，其他五张采用上节提示词。

## whirl_ring.png

Sprite sheet, 4 frames in one horizontal row, equal square cells, ring centered in every cell: a thin glowing golden energy ring, perfect circle seen from straight above, empty center, small flame wisps along the ring that move clockwise from frame to frame (seamless loop). Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.
STRICT PRODUCTION CONSTRAINT: generous EMPTY gutters between EVERY frame. Each effect fits inside 70 percent of its cell width, never touching neighboring frames or the image border. Absolutely NO diffuse bloom, NO colored haze, NO fog, NO soft gradients. Isolated discrete hard-edged pixel shapes on actual transparent background. Keep the silhouette small enough to leave at least 15 percent clear horizontal margin on both sides of each cell.
A THIN circular line only, thickness at most 3 percent of circle diameter. Identical exact circular size and position all four frames, wisps rotate clockwise in quarter-turn steps, interior fully empty transparent.

## excalibur.png

Sprite sheet, 8 frames in one horizontal row, equal tall cells (width:height = 1:2), the ground impact point at the same spot near the bottom of every cell: a giant holy longsword made of golden light plunging point-down from the sky into the ground. Frame 1: glowing sword high at the top. Frame 2: descending with a light trail. Frame 3: blade tip hits the ground, huge white-gold flash. Frame 4: golden explosion, flat elliptical shockwave on the ground and a pillar of light. Frames 5-6: sword and pillar fading, shockwave ring expanding. Frames 7-8: gold sparks and dust fading. Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, white-hot core with gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.
STRICT PRODUCTION CONSTRAINT: generous EMPTY gutters between EVERY frame. Each effect fits inside 70 percent of its cell width, never touching neighboring frames or the image border. Absolutely NO diffuse bloom, NO colored haze, NO fog, NO soft gradients. Isolated discrete hard-edged pixel shapes on actual transparent background. Keep the silhouette small enough to leave at least 15 percent clear horizontal margin on both sides of each cell.
Eight equal cells across the image. Each cell has a common ground anchor at x=cell center, y=80 percent of canvas height. Shockwave maximum width 65 percent of cell width. All sword positions contained in middle 60 percent of canvas height. KEEP all eight frames visibly separate: no connected ground line, no smoke bridging frames. Every sword has point DOWN, with guard above middle. Same sword design in frames 1-6.

## holy_seal.png

Sprite sheet, 4 frames in one horizontal row, equal square cells, seal centered in every cell: a glowing golden holy seal on the ground seen from straight above, a perfect circle with an outer ring of runes, an inner ring, and a sword-and-cross emblem in the middle, empty space between the rings. Frames pulse in brightness and the rune ring turns slightly (seamless loop). Pixel art game VFX, 16-bit fantasy RPG style, chunky square pixels, hard edges, no anti-aliasing, no outline, gold ramp (#FFF6C8, #FFD65A, #F0A028, #C46818). Transparent background (if impossible: pure black #000000). No text, no watermark, no border.
STRICT PRODUCTION CONSTRAINT: generous EMPTY gutters between EVERY frame. Each effect fits inside 70 percent of its cell width, never touching neighboring frames or the image border. Absolutely NO diffuse bloom, NO colored haze, NO fog, NO soft gradients. Isolated discrete hard-edged pixel shapes on actual transparent background. Keep the silhouette small enough to leave at least 15 percent clear horizontal margin on both sides of each cell.
The area between the thin rings is COMPLETELY EMPTY TRANSPARENT, not filled with a gold disc. Only rune strokes, circular lines and the central sword-cross emblem are colored. Preserve identical circle size and center in all four frames. Brightness cycle medium-bright-medium-dim, never change scale.



## 通用追加约束（原文）

Production layout constraints: exactly the requested number of frames in ONE horizontal row. Every frame has equal cell dimensions, fixed anchor and clear margins. Never use multiple rows. No drawn grid, no divider lines, no frame labels, no painted checkerboard. Use solid pure black #000000 if actual alpha transparency is unavailable. Requested file: [corresponding filename].
