# 盖伦：给 GPT 的生图提示词

一共 16 张图。生成的 PNG 放进仓库的 `assets/source/garen/`（`garen` 分支），或者任意一个文件夹，然后告诉 Claude。
Claude 负责切帧、缩到游戏尺寸（身高约 36 px）、统一调色板、补 1 px 黑描边、对齐脚底，再接到技能上（`tools/art/import_garen.py`）。

## 所有图的规则

- 每张图是**一行**，排着 N 个一样大的格子，每格一帧。格子之间不要留缝、边框、文字或编号。
- **背景透明**。做不到透明时：角色图用纯品红 `#FF00FF`，特效图用纯黑 `#000000`。
- 同一张图里每一帧的大小、位置都一致。角色图的脚底在每一格的同一高度。
- **先生成 `garen_ref.png`**，之后每张角色图都把它作为参考图一起发给 GPT，并加一句
  "same character, same colors and proportions as the attached reference"，这样每个动作才是同一个人。
- 如果模型不肯画带名字的角色，把提示词开头的 "Garen from League of Legends" 删掉，只保留外观描述。

## 角色（10 张）

每段提示词都包含同一段外观、画风和排版说明，可以直接整段复制。

### 1. `garen_ref.png`：参考图，1 帧

```text
Garen from League of Legends (default skin) as a 2D pixel art game sprite: a big broad-shouldered Demacian knight in heavy plate armor, polished silver steel with royal-blue cloth and gold trim, huge rounded silver pauldrons edged in gold, a gold winged Demacia crest on the chest, a royal-blue armored skirt, heavy silver greaves and boots, short dark-brown hair, square jaw, stern face, a long royal-blue cape, and a massive silver greatsword (wide blade, dark fuller, gold winged crossguard, blue grip) about as long as he is tall.
Style: pixel art sprite for a small tactics / auto-battler game like Teamfight Manager 2: chunky square pixels, hard edges, a 1-pixel black outline around the whole character, flat cel shading with 3-4 tones per color, no anti-aliasing, no gradients, no glow, limited palette of about 32 colors, chibi proportions with the head about one third of the body height, 3/4 view facing right.
Pose: standing idle, greatsword resting on his right shoulder, cape hanging behind him.
Layout: one single square image, the character centered, feet on an invisible ground line at 88% of the image height, the character about 60% of the image height. Transparent background (if not possible: solid #FF00FF magenta). No text, no border, no shadow.
```

### 2. `garen_idle.png`：待机，6 帧循环

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: IDLE, 6 frames, seamless loop. He stands with the greatsword resting on his right shoulder; subtle breathing (chest and shoulders rise and fall 1-2 pixels), the cape hem sways gently. Feet stay planted.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).
```

### 3. `garen_run.png`：跑步，6 帧循环

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: RUN to the right, 6 frames, seamless loop: body leaning forward, greatsword held low in his right hand trailing behind, cape streaming back, clear alternating leg strides (contact, passing, contact, passing), slight up-down bounce. The legs keep the same length and shape in every frame.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).
```

### 4. `garen_attack.png`：普攻，6 帧

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: BASIC ATTACK, 6 frames: 1 guard stance; 2 swings the greatsword up and back over his shoulder; 3 powerful diagonal slash forward and down, drawn with a bright silver-white arc smear; 4 impact, sword low in front, body leaning into the blow; 5 follow-through; 6 back to guard. Feet stay on the ground line.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the sword may reach toward the cell edges but must stay inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 5. `garen_q_attack.png`：Q「致命打击」跃起重击，7 帧

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: DECISIVE STRIKE, a leaping overhead blow, 7 frames: 1 crouches low; 2 leaps up and forward with the greatsword raised high over his head in both hands, the blade glowing gold; 3 top of the leap; 4 comes down swinging; 5 IMPACT: the sword slammed down in front of him with a bright gold flash at the blade; 6 kneeling recovery; 7 stands back up in guard. The ground line is the same in every cell (he is in the air in frames 2-4).
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height when standing, ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).
```

### 6. `garen_skill.png`：Q 施放（战吼），4 帧

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: BATTLE CRY, 4 frames: 1 raises the greatsword toward the sky; 2 shouts, mouth open, the blade flashing gold; 3 holds the pose, cape blown back; 4 lowers the sword into a forward charging stance.
Layout: one horizontal row of 4 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).
```

### 7. `garen_spin.png`：E「审判」旋转，8 帧循环

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: JUDGMENT SPIN, 8 frames, seamless loop: he spins in place holding the greatsword straight out at waist height with both hands, one full 360-degree turn over the 8 frames (facing right, front-right, front, front-left, left, back-left, back, back-right), cape swirling around him. Feet stay on the ground line.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the extended sword must stay inside its cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 8. `garen_ult.png`：R「德玛西亚正义」施放，8 帧

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: DEMACIAN JUSTICE, calling down a giant sword, 8 frames: 1-2 lifts the greatsword high, pointing at the sky; 3 the blade blazes with golden light; 4 holds; 5-6 brings the sword down and points it forward at the enemy, commanding the strike; 7 holds; 8 back to guard.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).
```

### 9. `garen_hit.png`：受击，2 帧

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: HIT REACTION, 2 frames: 1 flinches backward from a blow, grimacing, sword lowered; 2 recovering. Feet stay on the ground line.
Layout: one horizontal row of 2 equal square cells, no gaps, no borders, no labels. Same character size in every cell: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered. Transparent background (if not possible: solid #FF00FF magenta).
```

### 10. `garen_dead.png`：死亡，7 帧

```text
Same character as the attached reference (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the reference.
Animation: DEATH, 7 frames: 1 staggers; 2 drops to one knee; 3 plants the greatsword in the ground to hold himself up; 4 holds, head bowed; 5 slumps; 6 falls onto his side; 7 lies still on the ground, sword beside him.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. Same character scale in every cell (about 60% of the cell height when standing), ground line at 88% of the cell height. Transparent background (if not possible: solid #FF00FF magenta).
```

## 技能特效（6 张）

特效不需要参考图。它们会在游戏里画在盖伦或目标身上，所以中心要空出来，或者效果本身居中。

### 11. `garen_fx_hit.png`：普攻命中，4 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright white-hot core with a silver-blue and gold color ramp (#FFFFFF, #E8F4FF, #8FC6FF, #FFD65A, #F0A028).
Effect: a sword hit spark, 4 frames: 1 small white flash; 2 sharp silver-white slash spark with a few gold sparks; 3 shrinking spark, sparks flying outward; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, effect centered at the same point in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `garen_fx_q_hit.png`：Q 重击命中 + 沉默，6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright white-hot core with Demacian gold and blue color ramps (#FFFFFF, #FFF6C8, #FFD65A, #F0A028, #E8F4FF, #8FC6FF, #3A7BE0).
Effect: DECISIVE STRIKE impact, 6 frames: 1 a heavy vertical downward slash of white-gold light appears; 2 bright flash where it lands, blue-white shock burst; 3 largest burst with gold sparks; 4 burst fading, a small grey-blue swirl (a "silenced" mark) appears above the impact point; 5 swirl turning, sparks falling; 6 swirl fading out.
Layout: one horizontal row of 6 equal square cells, the impact point at the same spot in every cell (center of the cell), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `garen_fx_q_ready.png`：Q 强化中（剑发光），6 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden color ramp (#FFFFFF, #FFF6C8, #FFD65A, #F0A028).
Effect: an empowered aura, 6 frames, seamless loop: small golden light motes and short golden streaks rising upward around an EMPTY character-sized space in the middle (a person will stand there), plus a thin glowing golden ring on the ground at the bottom (flat ellipse). Subtle, not covering the center.
Layout: one horizontal row of 6 equal square cells, same position in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `garen_fx_courage.png`：W「勇气」护盾，6 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, white-gold and pale blue color ramp (#FFFFFF, #FFF6C8, #FFD65A, #E8F4FF, #8FC6FF).
Effect: a protective shield bubble, 6 frames, seamless loop: the OUTLINE of a round barrier (a circle of white-gold light, 2-3 pixels thick) around an EMPTY center where a character stands, with a few small sparkles moving around the ring and a brighter glint sliding along it.
Layout: one horizontal row of 6 equal square cells, the ring centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `garen_fx_spin.png`：E 旋转剑风，8 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, steel-blue and white color ramp with a little gold (#FFFFFF, #E8F4FF, #B8D8FF, #8FC6FF, #5A8FD8, #FFD65A).
Effect: JUDGMENT whirlwind, 8 frames, seamless loop: a flat ring of steel-blue and white sword-slash trails circling around an EMPTY center (a spinning knight stands there), seen from a 3/4 top-down angle so the ring is an ellipse about twice as wide as it is tall, with small sparks flying off; the slash trails rotate clockwise from frame to frame.
Layout: one horizontal row of 8 equal square cells, the ring centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `garen_fx_r.png`：R「德玛西亚正义」天降巨剑，9 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright white-hot core with Demacian gold and blue color ramps (#FFFFFF, #FFF6C8, #FFD65A, #F0A028, #E8F4FF, #8FC6FF, #3A7BE0).
Effect: DEMACIAN JUSTICE, 9 frames: 1 a giant glowing golden-blue broadsword of light (Demacia style, winged gold crossguard) appears high in the sky, pointing down; 2 it plunges down with a light trail; 3 the tip hits the ground with a huge white-gold flash; 4 golden-blue explosion, a flat elliptical shockwave on the ground and a pillar of light, the sword stuck in the ground glowing; 5-6 the sword and pillar fade while the shockwave ring expands; 7-9 sparks and light fading away.
Layout: one horizontal row of 9 equal TALL cells (width:height = 1:2), the ground impact point at the same spot in every cell, near the bottom (about 85% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## Claude 导入时的对应关系（给 Claude 看）

| 文件 | 帧数 | 游戏里的用途 |
|---|---:|---|
| `garen_idle.png` | 6 | 精灵图 tag `idle` |
| `garen_run.png` | 6 | `run` |
| `garen_attack.png` | 6 | `attack` |
| `garen_q_attack.png` | 7 | `q_attack`（Q 强化普攻，`CasterAnimation`） |
| `garen_skill.png` | 4 | `skill`（Q 施放） |
| `garen_spin.png` | 8 | `spin`（E，循环 3 秒） |
| `garen_ult.png` | 8 | `ult` |
| `garen_hit.png` | 2 | `hit` |
| `garen_dead.png` | 7 | `dead` |
| `garen_fx_hit.png` | 4 | 特效 `league_garen_hits:spark` |
| `garen_fx_q_hit.png` | 6 | `league_garen_hits:q` |
| `garen_fx_q_ready.png` | 6 | `league_garen_buffs:decisive` |
| `garen_fx_courage.png` | 6 | `league_garen_buffs:courage` |
| `garen_fx_spin.png` | 8 | `league_garen_spin:loop` |
| `garen_fx_r.png` | 9 | `league_garen_r:impact`（高格子，落点固定） |

`garen_ref.png` 只用来保持造型一致，不进游戏。

## 第二轮：按英雄联盟原版动作重画待机、跑步、普攻（3 张）

实测后发现这三个动作和游戏里的盖伦不一样。游戏里盖伦待机和跑步时，剑都是平端在身前、指向前方，不是扛在肩上或拖在身后；普攻是扭身蓄力后从右肩上方劈下。

姿势参考图从本地客户端渲染：

```bash
python tools/lol/pose_ref.py --anim Idle1 --times 0,356,711,1067,1422,1778 --shift -0.12 --yaw 70 --pitch 15 --size 360 --width 1.3 --fit 0.5 --bg 225,225,225 --no-labels --out ref
python tools/lol/pose_ref.py --anim _Run.anm --times 0,156,311,467,622,778 --shift -0.12 --yaw 70 --pitch 15 --size 360 --width 1.3 --fit 0.5 --bg 225,225,225 --no-labels --out ref
python tools/lol/pose_ref.py --anim Attack_01 --times 0,300,333,367,400,560 --ground 0.74 --yaw 70 --pitch 15 --size 360 --width 1.3 --fit 0.5 --bg 225,225,225 --no-labels --out ref
```

渲染出来的是 Riot 的模型，只在本地用，不提交到仓库。

每张图发给 GPT 时附两张图：第一张 `garen_ref.png`（造型），第二张对应的姿势参考图（动作）。生成结果覆盖 `assets/source/garen/` 里的同名文件。

### 2b. `garen_idle.png`：待机，6 帧循环（附 `garen_pose_idle.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the first image.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game idle animation from League of Legends, 6 frames left to right. Copy each frame's pose exactly - stance, lean, legs, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the pixel-art style above, not like the render (ignore its colors, lighting and low-poly look). Do NOT put the sword on his shoulder.
Animation: IDLE, 6 frames, seamless loop, as in the pose reference: a ready combat stance, knees slightly bent, feet apart, body turned toward the right; he holds the greatsword in his right hand at waist height with the blade pointing FORWARD to the right, almost level; left fist near his belt; subtle breathing (shoulders rise and fall 1-2 pixels), cape and blue scarf sway gently. Feet stay planted.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height; place the body a little left of center so the forward-pointing sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 3b. `garen_run.png`：跑步，6 帧循环（附 `garen_pose_run.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the first image.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game run cycle from League of Legends, 6 frames left to right. Copy each frame's pose exactly - leg positions, forward lean, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the pixel-art style above, not like the render (ignore its colors, lighting and low-poly look). The sword must NOT trail behind him.
Animation: RUN to the right, 6 frames, seamless loop, as in the pose reference: body leaning forward, the greatsword held in his right hand at hip height with the blade pointing FORWARD in the running direction and slightly down, left arm swinging, cape and blue scarf streaming back, long strides (contact, passing, contact, passing), slight up-down bounce. The legs keep the same length and shape in every frame.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height; place the body a little left of center so the forward-pointing sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 4b. `garen_attack.png`：普攻，6 帧（附 `garen_pose_attack.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height), 3/4 view facing right. Same colors and proportions as the first image.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game basic attack from League of Legends, 6 frames left to right. Copy each frame's pose exactly - body twist, stance, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the pixel-art style above, not like the render (ignore its colors, lighting and low-poly look).
Animation: BASIC ATTACK, a big overhead chop, 6 frames, as in the pose reference: 1 wind-up: torso twisted away from the target, greatsword raised over his right shoulder; 2 the sword pulled far back behind his head, body coiled; 3 the sword swung up overhead, body turning forward; 4 the slash: the blade sweeps forward to the right at waist height with a bright silver-white arc smear, strong lunge; 5 impact: the blade driven down in front of him, tip near the ground, knees bent; 6 recovery: standing, sword held low in front pointing down. Feet stay on the ground line.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 55% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the whole sword and the smear must stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

帧数和文件名都不变，导入工具不用改接口；对齐参数会按新图重新校准。

## 第三轮：待机、普攻改为正面（2 张）

第二轮的待机和普攻只能看到背影。原因是英雄联盟里盖伦待机时胸口朝着他自己的右手边，我从右前方渲染参考图，看到的正好是后背。TFM2 所有英雄朝右时都露出正面，所以参考图改为从他的左侧渲染（胸口对着镜头），再水平翻转成朝右（`--mirror`）。跑步本来就是右侧面，保留第二轮的。

```bash
python tools/lol/pose_ref.py --anim Idle1 --times 0,356,711,1067,1422,1778 --shift -0.06 --yaw 55 --pitch 25 --size 360 --width 1.35 --fit 0.48 --bg 225,225,225 --no-labels --mirror --out ref
python tools/lol/pose_ref.py --anim Attack_01 --times 0,300,333,367,400,560 --ground 0.74 --shift -0.04 --yaw 55 --pitch 25 --size 360 --width 1.35 --fit 0.48 --bg 225,225,225 --no-labels --mirror --out ref
```

同样附两张图：`garen_ref.png` + 对应的姿势参考图。

### 2c. `garen_idle.png`：待机，6 帧循环，正面（附 `garen_pose_idle.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height). 3/4 FRONT view facing right: we see his face, his chest and the gold Demacia crest; the cape hangs behind him. Never show his back. Same colors and proportions as the first image.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game idle from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the pixel-art style above, not like the render (ignore its colors, lighting and low-poly look).
Animation: IDLE, 6 frames, seamless loop, as in the pose reference: a wide, solid ready stance facing the viewer and turned slightly to the right, knees bent; the greatsword held low in front of him, blade pointing down and forward to the right; subtle breathing (shoulders rise and fall 1-2 pixels), the cape sways gently behind him. Feet stay planted.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 4c. `garen_attack.png`：普攻，6 帧，正面（附 `garen_pose_attack.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends): big Demacian knight, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions (head about one third of the height). 3/4 FRONT view facing right: we see his face, his chest and the gold Demacia crest; the cape hangs behind him. Never show his back. Same colors and proportions as the first image.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game basic attack from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the pixel-art style above, not like the render (ignore its colors, lighting and low-poly look).
Animation: BASIC ATTACK, a heavy diagonal slash, 6 frames, as in the pose reference: 1 facing the viewer, the greatsword swung low behind him to the left; 2 the sword raised high up and back to the left, body coiled; 3 top of the backswing, the blade level behind his head; 4 the slash: the blade sweeps diagonally down to the right with a bright silver-white arc smear, strong lunge forward; 5 impact: the blade driven forward to the right at waist height, knees bent; 6 recovery: sword held forward to the right, lowering. Feet stay on the ground line.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. In every cell the character has exactly the same size: about 60% of the cell height, feet on an invisible ground line at 88% of the cell height, body horizontally centered; the whole sword and the smear must stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

## 第四轮：跑步和技能动作全部按第三轮的造型重画（7 张）

第三轮之后还有两个问题：
- 跑步还是第二轮从侧后方画的，一跑就露背。
- 各轮 GPT 画出的比例不同：第一轮的技能图头大肩宽，第三轮的待机头小一些，放技能时看起来忽大忽小。

所以跑步和第一轮留下的 6 个动作都重画。每张都附第三轮待机截出来的 `garen_ref_v3.png` 作为造型和大小基准，有英雄联盟原版动画的再附正面姿势参考图（从客户端渲染、翻转成朝右）。战吼和受击在英雄联盟里没有对应动画，只附造型图。

| 生成文件 | 帧数 | 第一张图 | 第二张图 |
|---|---:|---|---|
| `garen_run.png` | 6 | garen_ref_v3.png | garen_pose_run.png |
| `garen_q_attack.png` | 7 | garen_ref_v3.png | garen_pose_q_attack.png |
| `garen_skill.png` | 4 | garen_ref_v3.png | 无 |
| `garen_spin.png` | 8 | garen_ref_v3.png | garen_pose_spin.png |
| `garen_ult.png` | 8 | garen_ref_v3.png | garen_pose_ult.png |
| `garen_hit.png` | 2 | garen_ref_v3.png | 无 |
| `garen_dead.png` | 7 | garen_ref_v3.png | garen_pose_dead.png |

姿势参考图的渲染命令（都加 `--yaw 55 --pitch 25 --size 360 --width 1.35 --bg 225,225,225 --no-labels --mirror`）：

```bash
python tools/lol/pose_ref.py --anim _Run.anm --times 0,156,311,467,622,778 --fit 0.48 --shift -0.06 --out ref
python tools/lol/pose_ref.py --anim Garen_2013_spell1 --times 0,90,180,270,360,540,810 --fit 0.3 --ground 0.82 --out ref
python tools/lol/pose_ref.py --anim spell3_0 --times 0,33,67,100,133,167,200,233 --fit 0.48 --ground 0.8 --out ref
python tools/lol/pose_ref.py --anim spell4 --times 0,150,250,330,600,900,1150,1300 --fit 0.4 --ground 0.8 --out ref
python tools/lol/pose_ref.py --anim Death --times 0,260,520,780,1040,1560,2340 --fit 0.46 --ground 0.8 --out ref
```

E 在英雄联盟里转一圈 0.27 秒，每帧 45°，所以取连续 8 帧正好一圈。

### 3d. `garen_run.png`：跑步，6 帧循环

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game run cycle from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - lean, legs, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and low-poly look).
Animation: RUN to the right, 6 frames, seamless loop, as in the pose reference: body leaning forward, the greatsword held low in front of him pointing down and forward, long strides (contact, passing, contact, passing), the cape streaming behind him, slight up-down bounce. The legs keep the same length and shape in every frame.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 5d. `garen_q_attack.png`：Q「致命打击」跃起重劈，7 帧

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game Decisive Strike from League of Legends, seen from the front, 7 frames left to right. Copy each frame's pose exactly - body, legs, arms, where the sword points and how high he is in the air. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and low-poly look).
Animation: DECISIVE STRIKE, a leaping overhead blow, 7 frames, as in the pose reference: 1 leaping up, knees tucked, sword held back; 2 rising higher, the blade starting to glow gold; 3 top of the leap, sword cocked back; 4 diving down with the greatsword raised high overhead, blade glowing gold; 5 IMPACT: landing in a deep crouch, the sword slammed down in front of him with a bright gold flash and burst at the blade; 6 crouched recovery, sword in front; 7 rising back into the ready stance of the first image. The ground line is the same in every cell; he is in the air in frames 1-4.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword and the gold flash stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 6d. `garen_skill.png`：Q 施放（战吼），4 帧（只附第一张图）

```text
Same character as the ATTACHED image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Animation: BATTLE CRY, 4 frames, starting and ending in the ready stance of the attached image: 1 raises the greatsword straight up toward the sky with his right arm, feet apart; 2 shouts, mouth open, the blade flashing gold with small sparkles; 3 holds the pose, cape blown back; 4 lowers the sword back into the ready stance of the attached image. Feet stay on the ground line.
Layout: one horizontal row of 4 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the raised sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 7d. `garen_spin.png`：E「审判」旋转，8 帧循环（一整圈）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 view, same camera as the first image.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game Judgment spin from League of Legends, seen from the front, 8 frames left to right - exactly one full turn. Copy each frame's pose exactly - body turn, legs, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and low-poly look).
Animation: JUDGMENT SPIN, 8 frames, seamless loop, one full turn, as in the pose reference: he spins in place with the greatsword held out flat around waist height; from frame to frame the sword sweeps all the way around him and his body turns with it, so some frames show his side or back exactly as in the reference; the cape swirls. Feet stay on the ground line.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the extended sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 8d. `garen_ult.png`：R「德玛西亚正义」，8 帧

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game Demacian Justice from League of Legends, seen from the front, 8 frames left to right. Copy each frame's pose exactly - body, legs, arms, where the sword points and how high he jumps. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and low-poly look).
Animation: DEMACIAN JUSTICE, 8 frames, as in the pose reference: 1 standing, greatsword lowered at his side; 2 raising the sword, the blade starting to glow gold; 3 leaping up with the sword raised high, blade blazing gold; 4 slamming the sword point-down into the ground in front of him, landing in a crouch; 5 holding, crouched over the planted glowing sword; 6 holding, gold light fading; 7 pulling the sword out, rising; 8 back in the ready stance of the first image. The ground line is the same in every cell; he is in the air only in frame 3.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword and its glow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 9d. `garen_hit.png`：受击，2 帧（只附第一张图）

```text
Same character as the ATTACHED image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Animation: HIT REACTION, 2 frames, based on the ready stance of the attached image: 1 flinches from a blow: upper body jolted back, grimacing, sword lowered, feet planted; 2 recovering, almost back in the ready stance of the attached image.
Layout: one horizontal row of 2 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 10d. `garen_dead.png`：死亡，7 帧

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game death from League of Legends, seen from the front, 7 frames left to right. Copy each frame's pose exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and low-poly look).
Animation: DEATH, 7 frames, as in the pose reference: 1 staggers, sword lowered; 2 the greatsword drops from his hands and lies on the ground; 3 bends forward, sinking; 4 falls to his knees; 5 sits back, slumping; 6 collapses onto his side; 7 lies still on the ground next to his sword.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image (about 60% of the cell height when standing); ground line at 88% of the cell height in every cell; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

## 第五轮：移动动画改成走路（1 张）

第四轮的跑步上身前倾、低着头，像冲刺，一个循环只有 0.54 秒。英雄联盟里盖伦移动时上身直立、步伐稳重，一个循环约 0.93 秒，更像行军。这轮重画成 8 帧的走路。生成的文件名仍然是 `garen_run.png`（游戏里的移动动画就叫 run）。

附两张图：第一张 `garen_ref_v3.png`（造型和大小），第二张 `garen_pose_walk.png`（英雄联盟原版移动动画的正面参考，8 帧）。

```bash
python tools/lol/pose_ref.py --anim _Run.anm --times 0,117,233,350,467,583,700,817 --yaw 55 --pitch 25 --size 360 --width 1.35 --fit 0.48 --shift -0.06 --bg 225,225,225 --no-labels --mirror --out ref
```

### 3e. `garen_run.png`：走路，8 帧循环

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, proportions and size: big Demacian knight in silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest on the chest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32 colors, chibi proportions. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game movement animation from League of Legends, seen from the front, 8 frames left to right. Copy each frame's leg and arm positions exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and low-poly look).
Animation: WALK to the right, 8 frames, seamless loop: a heavy, steady armored march - this is a WALK, NOT a run or a sprint. Upright torso, chest out, head up; do NOT lean forward or hunch. Moderate steps like the reference, one foot always on the ground (contact, down, passing, up for each leg); the body rises and sinks only 1 pixel. The greatsword is held low in front of him in his hand, blade pointing down and forward, swaying slightly with each step; the other arm swings a little; the cape sways behind him. The legs keep the same length and shape in every frame.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```
