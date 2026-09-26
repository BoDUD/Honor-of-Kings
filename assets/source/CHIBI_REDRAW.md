# 盖伦 + 艾希：按原版 Q 版比例重画（给 GPT 的生图提示词）

一共 21 张：盖伦 1 张造型参考 + 9 张动作；艾希 1 张造型参考 + 9 张动作 + 1 张 W 扇形特效。
其余特效图不变。生成的 PNG 覆盖 `assets/source/garen/`、`assets/source/ashe/` 里的同名文件（新造型图是新文件名），然后告诉 Claude。
Claude 负责切帧、缩到游戏尺寸、统一调色板、补描边、对齐，再重新校准导入参数（`tools/art/import_garen.py`、`tools/art/import_ashe.py`）。

## 为什么要重画

游戏里看不清两人的脸。对比原版英雄（`tfm2_style_ref.png`）：

| | 原版英雄 | 我们的盖伦 / 艾希 |
|---|---|---|
| 头占身高 | 约 1/3（33–36 px 的角色，头 12–13 px） | 约 1/5（盖伦头约 7 px，艾希连兜帽约 8 px） |
| 脸 | 一大块肤色，两只 2 px 的眼睛，有眉毛 | 缩小后只剩两三行肤色、没有眼睛；艾希的脸还被兜帽和刘海挡住 |

前几轮提示词里写了 "chibi proportions"，但附的参考图（英雄联盟模型渲染、上一轮造型图）都是写实比例，GPT 跟着参考图画成了小头。所以这一轮：

1. 附一张原版英雄对照图 `tfm2_style_ref.png`（上排待机、下排攻击），直接给 GPT 看比例和脸的画法。
2. 姿势参考图本身就是大头比例：渲染时头放大 2 倍、腿缩到 0.8 倍（`pose_ref.py --head 2.0 --legs 0.8`），动作和时间点与上一轮完全相同。
3. 先单独生成新的造型图，确认比例对了，再用它生成所有动作。

## 生成顺序（重要）

1. **先只生成两张造型图** `garen_ref_chibi.png`（第 1 条）和 `ashe_ref_chibi.png`（第 11 条），各附三张图（见提示词）。
2. 检查这两张：头约占身高 1/3；脸很大、眼睛清楚；正面朝右（能看到脸和胸口）；服装、配色、武器和上一轮造型一致；艾希的兜帽不遮脸、刘海不挡眼睛。**不对就重画这一张，不要带着错的造型图往下做。**
3. 每个英雄的 9 张动作图**同一批**生成，每张附两张图：第一张 = 该英雄的新造型图，第二张 = 对应的 Q 版姿势参考图。战吼（盖伦 `skill`）和受击（`hit`）在英雄联盟里没有对应动作，只附第一张。
4. `ashe_fx_volley.png` 附上一轮的 `ashe_fx_arrow.png`，箭的画法保持一致。
5. 以后如果再改造型，同一个英雄的所有动作图用新的造型图整批重画，不和旧批次混用。

## 附图（压缩包里有；Riot 模型渲染和原版游戏截图只在本地用，不提交到仓库）

| 文件 | 内容 | 用在 |
|---|---|---|
| `tfm2_style_ref.png` | 团战经理 2 原版英雄，上排待机、下排攻击，放大 8 倍 | 两张造型图 |
| `garen_ref_v3.png`、`ashe_ref.png` | 上一轮通过的造型（服装、配色、武器以它为准，**比例不要照它**） | 两张造型图 |
| `garen_model_chibi.png`、`ashe_model_chibi.png` | 英雄联盟游戏内模型的正面、侧面、背面，已经是大头比例 | 两张造型图 |
| `garen_pose_*.png`、`ashe_pose_*.png` | 英雄联盟原版动作，大头比例，每帧对应原版的一个时间点 | 各自的动作图 |
| `ashe_fx_arrow.png` | 上一轮的冰霜箭特效 | `ashe_fx_volley.png` |

## 所有角色图的规则

- 每张图是**一行**，排着 N 个一样大的格子，每格一帧。格子之间不要留缝、边框、文字或编号。
- **背景透明**。做不到透明时：角色图用纯品红 `#FF00FF`，特效图用纯黑 `#000000`。
- 同一张图里每一帧的大小、位置都一致。脚底在每一格的同一高度。
- **比例（这一轮最重要）**：头约占身高的 1/3，脸大而清楚；每一帧的头一样大。
- 朝右的 3/4 正面：看得到脸和胸口，不画背影（盖伦的旋转除外）。
- 盖伦的移动是**走路**（上身直立），艾希的移动是**跑步**（有双脚离地的帧）。
- 武器始终在同一只手：盖伦的剑在右手，艾希的弓在左手（画面右侧那只手）。
- 如果模型不肯画带名字的角色，把提示词里的 "Garen" / "Ashe" / "League of Legends" 删掉，只保留外观描述。

---

## 盖伦（10 张）

### 1. `garen_ref_chibi.png`：新造型图，1 帧（附 `garen_ref_v3.png`、`tfm2_style_ref.png`、`garen_model_chibi.png`）

```text
Three attached images. FIRST: the approved pixel-art design of Garen for this game pack - keep his costume, colors, armor shapes, greatsword and pixel-art style exactly, but NOT his proportions (his head is far too small there). SECOND: official heroes of the game Teamfight Manager 2 - copy their proportions and the way their faces are drawn. THIRD: Garen's in-game model from League of Legends, front, side and back, already with the big head - use it for the shape of his armor, scarf and sword.
Garen from League of Legends (default skin) as a 2D pixel art game sprite: a big broad-shouldered Demacian knight in polished silver plate armor with royal-blue cloth and gold trim, huge rounded silver pauldrons edged in gold, a gold winged Demacia crest on the chest, a royal-blue tabard and a royal-blue cape, heavy silver greaves and boots, short dark-brown hair, a massive silver greatsword (wide blade, gold winged crossguard, blue grip) almost as long as he is tall.
PROPORTIONS (most important), exactly like the heroes in the SECOND image: the head is about ONE THIRD of his total height (from the top of the hair to the soles) - big and round, as wide as his chest; the face is large, lit and fully visible: square jaw, thick dark eyebrows, two big dark eyes each with a 1-pixel white highlight, a short firm mouth - drawn bold and simple so it stays readable when the sprite is shrunk to 36 pixels tall; short sturdy legs, about one third of his height; a compact, broad torso; big hands; the greatsword keeps its full size.
Style: pixel art sprite for Teamfight Manager 2, exactly like the SECOND image: chunky square pixels, hard edges, a 1-pixel black outline around the whole character, flat cel shading with 3-4 tones per color, no anti-aliasing, no gradients, no glow, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back.
Pose: the same ready idle stance as the FIRST image: a wide, solid stance, knees bent, the greatsword held low in front of him in his right hand, the blade pointing down and forward to the right.
Layout: one single square image, the character centered, feet on an invisible ground line at 88% of the image height, the character about 60% of the image height. Transparent background (if not possible: solid #FF00FF magenta). No text, no border, no shadow.
```

盖伦 9 张动作图的提示词都以同一段外观、比例、画风开头，可以整段复制。

### 2. `garen_idle.png`：待机，6 帧循环（附 `garen_ref_chibi.png` + `garen_pose_idle.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game idle from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: IDLE, 6 frames, seamless loop, as in the pose reference: a wide, solid ready stance facing the viewer and turned slightly to the right, knees bent; the greatsword held low in front of him, blade pointing down and forward to the right; subtle breathing (shoulders rise and fall 1-2 pixels), the cape sways gently behind him. Feet stay planted.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 3. `garen_run.png`：走路，8 帧循环（附 `garen_ref_chibi.png` + `garen_pose_walk.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game movement animation from League of Legends, already with the big head, seen from the front, 8 frames left to right. Copy each frame's leg and arm positions exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: WALK to the right, 8 frames, seamless loop: a heavy, steady armored march - this is a WALK, NOT a run or a sprint. Upright torso, chest out, head up; do NOT lean forward or hunch. Moderate steps like the reference, one foot always on the ground (contact, down, passing, up for each leg); the body rises and sinks only 1 pixel. The greatsword is held low in front of him in his right hand, blade pointing down and forward, swaying slightly with each step; the other arm swings a little; the cape sways behind him. The short legs keep the same length and shape in every frame.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 4. `garen_attack.png`：普攻，6 帧（附 `garen_ref_chibi.png` + `garen_pose_attack.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game basic attack from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: BASIC ATTACK, a heavy diagonal slash, 6 frames, as in the pose reference: 1 facing the viewer, the greatsword swung low behind him to the left; 2 the sword raised high up and back to the left, body coiled; 3 top of the backswing, the blade level behind his head; 4 the slash: the blade sweeps diagonally down to the right with a bright silver-white arc smear, strong lunge forward; 5 impact: the blade driven forward to the right at waist height, knees bent; 6 recovery: sword held forward to the right, lowering. Feet stay on the ground line.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword and the smear stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 5. `garen_q_attack.png`：Q「致命打击」跃起重劈，7 帧（附 `garen_ref_chibi.png` + `garen_pose_q_attack.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game Decisive Strike from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly - body, legs, arms, where the sword points and how high he is in the air. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: DECISIVE STRIKE, a leaping overhead blow, 7 frames, as in the pose reference: 1 leaping up, knees tucked, sword held back; 2 rising higher, the blade starting to glow gold; 3 top of the leap, sword cocked back; 4 diving down with the greatsword raised high overhead, blade glowing gold; 5 IMPACT: landing in a deep crouch, the sword slammed down in front of him with a bright gold flash and burst at the blade; 6 crouched recovery, sword in front; 7 rising back into the ready stance of the first image. The ground line is the same in every cell; he is in the air in frames 1-4.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword and the gold flash stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 6. `garen_skill.png`：Q 施放（战吼），4 帧（只附 `garen_ref_chibi.png`）

```text
Same character as the ATTACHED image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Animation: BATTLE CRY, 4 frames, starting and ending in the ready stance of the attached image: 1 raises the greatsword straight up toward the sky with his right arm, feet apart; 2 shouts, mouth wide open, eyebrows down, the blade flashing gold with small sparkles; 3 holds the pose, cape blown back; 4 lowers the sword back into the ready stance of the attached image. Feet stay on the ground line.
Layout: one horizontal row of 4 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the raised sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 7. `garen_spin.png`：E「审判」旋转，8 帧循环，一整圈（附 `garen_ref_chibi.png` + `garen_pose_spin.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 view, same camera as the first image. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game Judgment spin from League of Legends, already with the big head, seen from the front, 8 frames left to right - exactly one full turn. Copy each frame's pose exactly - body turn, legs, arms and where the sword points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: JUDGMENT SPIN, 8 frames, seamless loop, one full 360-degree turn, as in the pose reference: he spins in place with the greatsword held out flat around waist height; from frame to frame the sword sweeps all the way around him and his WHOLE BODY TURNS with it - front, side, back, other side - so the spin is obvious: some frames show his side or his back (the cape and the back of his head) exactly as in the reference; the cape swirls. Feet stay on the ground line.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the extended sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 8. `garen_ult.png`：R「德玛西亚正义」，8 帧（附 `garen_ref_chibi.png` + `garen_pose_ult.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game Demacian Justice from League of Legends, already with the big head, seen from the front, 8 frames left to right. Copy each frame's pose exactly - body, legs, arms, where the sword points and how high he jumps. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: DEMACIAN JUSTICE, 8 frames, as in the pose reference: 1 standing, greatsword lowered at his side; 2 raising the sword, the blade starting to glow gold; 3 leaping up with the sword raised high, blade blazing gold; 4 slamming the sword point-down into the ground in front of him, landing in a crouch; 5 holding, crouched over the planted glowing sword; 6 holding, gold light fading; 7 pulling the sword out, rising; 8 back in the ready stance of the first image. The ground line is the same in every cell; he is in the air only in frame 3.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 55% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword and its glow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 9. `garen_hit.png`：受击，2 帧（只附 `garen_ref_chibi.png`）

```text
Same character as the ATTACHED image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Animation: HIT REACTION, 2 frames, based on the ready stance of the attached image: 1 flinches from a blow: upper body jolted back, eyes squeezed shut, teeth gritted, sword lowered, feet planted; 2 recovering, almost back in the ready stance of the attached image.
Layout: one horizontal row of 2 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 10. `garen_dead.png`：死亡，7 帧（附 `garen_ref_chibi.png` + `garen_pose_dead.png`）

```text
Same character as the FIRST attached image (Garen, League of Legends) - copy his exact design, colors, PROPORTIONS and size: a chibi Demacian knight with a BIG head (one third of his height) and a large, clearly visible face with big dark eyes, silver plate armor with royal-blue cloth and gold trim, huge silver pauldrons, gold Demacia crest, royal-blue cape, short brown hair, massive silver greatsword with gold crossguard.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see his face, his chest and the gold crest; the cape hangs behind him. Never show his back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Garen's real in-game death from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look). The sword lies on the ground in front of him (closer to the viewer), so it looks lower than his feet.
Animation: DEATH, 7 frames, as in the pose reference: 1 staggers, sword lowered; 2 the greatsword drops from his hands and lies on the ground; 3 bends forward, sinking; 4 falls to his knees; 5 sits back, slumping; 6 collapses onto his side; 7 lies still on the ground next to his sword.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image (about 60% of the cell height when standing); ground line at 88% of the cell height in every cell; body horizontally centered; the whole sword stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

---

## 艾希（11 张）

### 11. `ashe_ref_chibi.png`：新造型图，1 帧（附 `ashe_ref.png`、`tfm2_style_ref.png`、`ashe_model_chibi.png`）

```text
Three attached images. FIRST: the approved pixel-art design of Ashe for this game pack - keep her costume, colors, bow and pixel-art style exactly, but NOT her proportions (her head is far too small there and the hood hides her face). SECOND: official heroes of the game Teamfight Manager 2 - copy their proportions and the way their faces are drawn. THIRD: Ashe's in-game model from League of Legends, front, side and back, already with the big head - use it for the shape of her hood, cape and bow.
Ashe from League of Legends (default skin) as a 2D pixel art game sprite: a slim young woman archer. Black pointed hood with gold trim and a small gold emblem; long silver-white hair with a faint lavender tint; pale skin, ice-blue eyes, dark lavender lips. Angular gold pauldrons with black edges; a black halter top with a small gold crest, bare midriff, a cream sash at the waist; a short black skirt with vertical gold stripes; gold armbands; black fingerless gloves with gold cuffs; black thigh-high boots with gold zigzag trim and gold greaves; a black cape with a wide gold border down to her ankles; a bronze quiver with ice-blue arrows behind her shoulder. Her signature weapon: a large glowing ice-blue crystal recurve bow with jagged crystal spikes, almost as tall as she is, held in her LEFT hand (the hand on the right side of the image) - draw it big and clearly readable.
PROPORTIONS (most important), exactly like the heroes in the SECOND image: the head is about ONE THIRD of her total height (from the tip of the hood to the soles) - big and round; the FACE is large, lit and fully visible: the hood sits back on her head and frames the face without shading it, the silver bangs sweep to one side ABOVE her eyes, two big ice-blue eyes each with a dark outline and a 1-pixel white highlight, thin eyebrows, small lavender lips - drawn bold and simple so it stays readable when the sprite is shrunk to 34 pixels tall; short legs, about one third of her height; a small, slim torso; the bow keeps its full size.
Style: pixel art sprite for Teamfight Manager 2, exactly like the SECOND image: chunky square pixels, hard edges, a 1-pixel black outline around the whole character, flat cel shading with 3-4 tones per color, no anti-aliasing, no gradients, no glow except the bow's own ice-blue light, about 32-40 colors. 3/4 FRONT view facing right: we see her face, her chest and the front of her body; the cape hangs behind her. Never show her back.
Pose: the same idle stance as the FIRST image: feet apart, torso toward the viewer, head turned slightly to the right. She holds the bow low and diagonally across the front of her body in her left hand: the upper limb rises past her right shoulder, the lower limb points down to the right; an ice-blue arrow is nocked and points down at the ground in front of her, her right hand at the nock near her belly.
Layout: one single square image, the character centered, feet on an invisible ground line at 88% of the image height, the character (with the hood) about 60% of the image height. Transparent background (if not possible: solid #FF00FF magenta). No text, no border, no shadow.
```

艾希 9 张动作图的提示词都以同一段外观、比例、画风开头，可以整段复制。

### 12. `ashe_idle.png`：待机，6 帧循环（附 `ashe_ref_chibi.png` + `ashe_pose_idle.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game idle from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the bow and arrow point. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: IDLE, 6 frames, seamless loop, as in the pose reference: she stands relaxed but ready, feet apart, torso toward the viewer, head turned slightly right. The bow is held LOW and diagonally across the front of her body in her left hand, the upper limb past her right shoulder; the nocked arrow points down at the ground in front of her, her right hand at the nock. Only subtle breathing: chest and shoulders rise and fall 1 pixel, the cape hem sways slightly. Feet stay planted. Do NOT raise, draw or aim the bow, and do NOT put it on her back or shoulder.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 13. `ashe_run.png`：跑步，8 帧循环（附 `ashe_ref_chibi.png` + `ashe_pose_run.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape streams behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game movement animation from League of Legends, already with the big head, seen from the front, 8 frames left to right - one full cycle. Copy each frame's leg and arm positions exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RUN to the right, 8 frames, seamless loop, as in the pose reference. This is a RUN, not a walk: a light, springy stride with a moment where BOTH feet are off the ground (frames 3 and 7), knees lifting, torso leaning forward a little, head up, looking ahead. She carries the bow LEVEL in front of her chest, turned flat and pointing FORWARD in the running direction exactly like the reference, the arrow nocked and pointing forward - the bow never trails behind her and is never on her back. The cape streams out behind her and flutters. The short legs keep the same length and shape in every frame; the body bobs up and down 2-3 pixels.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when upright about 60% of the cell height; the ground line at 88% of the cell height in every cell (the feet leave it in the airborne frames); body horizontally centered; the whole bow and cape stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 14. `ashe_attack.png`：普攻，6 帧（附 `ashe_ref_chibi.png` + `ashe_pose_attack.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game basic attack from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms, where the bow points and where her drawing hand is. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: BASIC ATTACK, a bow shot, 6 frames, as in the pose reference: 1 from the idle stance of the first image she swings the bow up in front of her, turning it upright, her right hand going to the string; 2 FULL DRAW: the bow held upright at arm's length toward the right in her left hand, her right hand pulling the string back to her cheek, an ice-blue arrow nocked and aimed to the right, torso toward the viewer, head turned to the target; 3 RELEASE: the string snaps forward, the arrow is gone, her right hand flies back open beside her head, a tiny ice-blue spark at the bow; 4 follow-through: the bow still up at arm's length, right hand held back high; 5 recovery: right hand coming down, bow still upright; 6 lowering the bow back toward the idle stance of the first image. Feet stay planted. This is a bow shot: never swing the bow like a melee weapon, and do not draw the flying arrow.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole upright bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 15. `ashe_q_attack.png`：Q 强化普攻（连射），6 帧（附 `ashe_ref_chibi.png` + `ashe_pose_q_attack.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game Ranger's Focus flurry from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - the wide stance, the legs, the arms and the flat bow. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RANGER'S FOCUS FLURRY, a rapid empowered shot, 6 frames, as in the pose reference: 1 from the idle stance of the first image she steps into a WIDE, LOW stance, feet far apart, knees bent, and turns the bow FLAT (horizontal); 2 in the wide stance, the flat bow held at chest height pointing to the right, the string drawn to her chest, several ice-blue arrows nocked together; 3 RELEASE: the string snaps, her right hand jerks back, a small burst of ice-blue sparks at the bow; 4 a second quick release, hand back again; 5 holding the wide stance, hand returning to the string; 6 rising back toward the idle stance of the first image. In frames 2-5 the bow glows a brighter ice-blue. Do not draw the flying arrows.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the wide stance and the whole bow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 16. `ashe_skill.png`：Q「射手的专注」发动，6 帧（附 `ashe_ref_chibi.png` + `ashe_pose_skill.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game move into her Ranger's Focus stance from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - legs, arms and where the bow points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RANGER'S FOCUS activation, 6 frames, as in the pose reference: 1 the idle stance of the first image; 2 she swings the bow up to the left across her body; 3 the bow sweeps over to lie flat at shoulder height, her hair and cape lifting; 4 she drops into a WIDE, LOW stance, the flat bow held in front of her chest pointing right; 5 holding the focus stance, eyes narrowed on the target, the bow flaring bright ice-blue with a few frost sparkles around it; 6 rising back toward the idle stance of the first image, the glow fading.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 17. `ashe_skill2.png`：W「万箭齐发」，7 帧（附 `ashe_ref_chibi.png` + `ashe_pose_skill2.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game Volley from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly - stance, arms and how the flat bow is held. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: VOLLEY, 7 frames, as in the pose reference: 1 from the idle stance of the first image she raises the bow in front of her and turns it FLAT (horizontal); 2 standing square to the viewer, the flat bow held at chest height pointing right, her right hand drawing a fan of several ice-blue arrows; 3 full draw; 4 RELEASE: the string snaps, her right hand flies back beside her head, a burst of ice-blue sparks at the bow; 5 follow-through, the bow dipping forward and down; 6 recovery, right hand held up and back; 7 lowering the bow back toward the idle stance of the first image. Feet stay planted. Do not draw the flying arrows.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 18. `ashe_ult.png`：R「魔法水晶箭」，8 帧（附 `ashe_ref_chibi.png` + `ashe_pose_ult.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game Enchanted Crystal Arrow cast from League of Legends, already with the big head, seen from the front, 8 frames left to right. Copy each frame's pose exactly - stance, arms, where the bow points and where her drawing hand is. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: ENCHANTED CRYSTAL ARROW, 8 frames, as in the pose reference: 1 from the idle stance of the first image she swings the bow up upright; 2 FULL DRAW like a basic attack, but the nocked arrow is a large crystal of ice glowing white-blue; 3 holding the draw, frost light and small ice crystals gathering around the arrowhead; 4 holding, the crystal arrow at its brightest, her cape and hair lifted by a cold wind; 5 RELEASE: a bright white-blue flash at the bow, the crystal arrow is gone, her right hand thrown back high; 6 follow-through, bow still up, frost sparks fading; 7 right hand coming down; 8 lowering the bow back toward the idle stance of the first image. Feet stay planted. Draw only the glow on the bow and arrowhead, not the flying arrow.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole upright bow and its glow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 19. `ashe_hit.png`：受击，2 帧（只附 `ashe_ref_chibi.png`）

```text
Same character as the ATTACHED image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large, clearly visible face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Animation: HIT REACTION, 2 frames, based on the idle stance of the attached image: 1 flinches from a blow: upper body jolted back and to the left, eyes squeezed shut, the bow still held low in her left hand, feet planted; 2 recovering, almost back in the idle stance of the attached image.
Layout: one horizontal row of 2 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 20. `ashe_dead.png`：死亡，7 帧（附 `ashe_ref_chibi.png` + `ashe_pose_dead.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi archer with a BIG head (one third of her height) and a large face with big ice-blue eyes (the hood frames the face, the bangs stay above the eyes), black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view, same camera as the first image. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game death from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly, including how high she is in the air. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look). Ignore the loose arrow lying on the ground in the render - do not draw it.
Animation: DEATH, 7 frames, as in the pose reference: 1 the idle stance of the first image; 2 struck: she staggers back, arms flung apart, the bow swinging away from her body; 3 leaning far back, knees giving way, the arm with the bow thrown up; 4 falling backward, feet leaving the ground, cape flaring; 5 falling almost horizontally toward the left, cape flying up; 6 landing on her back, the bow falling beside her feet; 7 lying still on the ground, head to the left, the bow on the ground by her feet.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image (about 60% of the cell height when standing); the ground line at 88% of the cell height in every cell (she is in the air in frames 4-5); the whole body, cape and bow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 21. `ashe_fx_volley.png`：W「万箭齐发」扇形箭雨，7 帧（附 `ashe_fx_arrow.png`）

英雄联盟里 W 是 9 支箭同时呈扇形射出。游戏里这张图画在 W 的矩形判定范围上，Claude 导入时把扇形的起点对到艾希身上、按施放方向旋转。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp (#FFFFFF, #E6FBFF, #9BE8FF, #42B8F0, #1F6FC8). Draw every arrow exactly like the arrow in the ATTACHED image (a slim frost arrow with a glowing crystal arrowhead and small crystal fletching).
Effect: VOLLEY, 7 frames: NINE frost arrows fired at the same moment in a fan to the RIGHT. All nine start from ONE point: the middle of the LEFT edge of the cell (where the bow is). The fan is about 56 degrees wide: the middle arrow flies horizontally, the others are spread evenly 7 degrees apart above and below it, each arrow pointing straight away from the starting point along its own line. From frame to frame the arrows fly outward together, so the fan grows: the arrow TIPS are at about 20%, 32%, 44%, 56%, 68%, 80% and 92% of the cell width in frames 1-7. Every arrow keeps the same length (about 18% of the cell width) and trails a few tiny frost sparkles. Only the arrows: no bow, no character, no hit effects.
Layout: one horizontal row of 7 equal square cells, the starting point at the middle of the left edge of every cell, the whole fan inside its own cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧数、文件名、帧时长和上一轮相同，导入工具不用改接口；新图到了以后重新量每张图的 `tall`（按新造型图的高度），头部轨迹按大头骨骼重新计算，脸的截取位置（`champion_view` 的 `face`）按新的肤色区域重新定。

| 文件 | 帧数 | 游戏里的用途 |
|---|---:|---|
| `garen_idle.png` / `ashe_idle.png` | 6 / 6 | `idle` |
| `garen_run.png` / `ashe_run.png` | 8 / 8 | `run`（盖伦走路 8 × 117 ms，艾希跑步 8 × 125 ms） |
| `garen_attack.png` / `ashe_attack.png` | 6 / 6 | `attack` |
| `garen_q_attack.png` / `ashe_q_attack.png` | 7 / 6 | `q_attack`（`CasterAnimation`） |
| `garen_skill.png` / `ashe_skill.png` | 4 / 6 | `skill` |
| `garen_spin.png` | 8 | `spin`（盖伦 E） |
| `ashe_skill2.png` | 7 | `skill2`（艾希 W） |
| `garen_ult.png` / `ashe_ult.png` | 8 / 8 | `ult` |
| `garen_hit.png` / `ashe_hit.png` | 2 / 2 | `hit` |
| `garen_dead.png` / `ashe_dead.png` | 7 / 7 | `dead` |
| `ashe_fx_volley.png` | 7 | `league_ashe_fx:volley`（W 的 `LineRangeProjectile`，7 × 40 ms；起点对到矩形左端，即艾希） |

`garen_ref_chibi.png`、`ashe_ref_chibi.png` 只用来保持造型一致，不进游戏。

## 参考图的渲染命令

和上一轮相同的动作、时间点和镜头，加 `--hq --head 2.0 --legs 0.8`（头放大 2 倍、腿和披风缩到 0.8 倍；每帧按原比例姿势里腿的最低点对齐地面，跳跃高度不变）。盖伦从左侧渲染再翻转（`--mirror`），艾希不翻转。

```bash
P="python tools/lol/pose_ref.py --hq --head 2.0 --legs 0.8 --bg 225,225,225 --no-labels --out ref"
G="$P --champ Garen --yaw 55 --pitch 25 --size 360 --width 1.35 --mirror"
$G --fit 0.48 --shift -0.06 --name garen_pose_idle $(for t in 0 356 711 1067 1422 1778; do printf -- "--frame garen_2013_idle1@%s " $t; done)
$G --fit 0.48 --shift -0.06 --name garen_pose_walk $(for t in 0 117 233 350 467 583 700 817; do printf -- "--frame garen_2013_run@%s " $t; done)
$G --fit 0.48 --shift -0.04 --ground 0.74 --name garen_pose_attack $(for t in 0 300 333 367 400 560; do printf -- "--frame garen_2013_attack_01@%s " $t; done)
$G --fit 0.3 --ground 0.82 --name garen_pose_q_attack $(for t in 0 90 180 270 360 540 810; do printf -- "--frame garen_2013_spell1@%s " $t; done)
$G --fit 0.48 --ground 0.8 --name garen_pose_spin $(for t in 0 33 67 100 133 167 200 233; do printf -- "--frame garen_base_spell3_0@%s " $t; done)
$G --fit 0.4 --ground 0.8 --name garen_pose_ult $(for t in 0 150 250 330 600 900 1150 1300; do printf -- "--frame garen_2013_spell4@%s " $t; done)
$G --fit 0.46 --ground 0.8 --name garen_pose_dead $(for t in 0 260 520 780 1040 1560 2340; do printf -- "--frame garen_2013_death@%s " $t; done)
A="$P --champ Ashe --yaw 55 --pitch 25 --size 360 --width 1.0 --ground 0.86 --fit 0.62 --shift -0.02"
$A --name ashe_pose_idle $(for t in 0 267 533 800 1067 1333; do printf -- "--frame ashe_idle1@%s " $t; done)
$A --name ashe_pose_run $(for t in 0 125 250 375 500 625 750 875; do printf -- "--frame ashe_run_jog@%s " $t; done)
$A --name ashe_pose_attack --frame "ashe_idle1@0>ashe_attack1@0:0.5" --frame ashe_attack1@0 --frame ashe_attack1@367 --frame ashe_attack1@533 --frame ashe_attack1@800 --frame "ashe_attack1@800>ashe_idle1@0:0.5"
$A --name ashe_pose_q_attack --frame "ashe_idle1@0>ashe_spell1@0:0.5" --frame ashe_spell1@0 --frame ashe_spell1@67 --frame ashe_spell1@267 --frame ashe_spell1@500 --frame "ashe_spell1@600>ashe_idle1@0:0.5"
$A --name ashe_pose_skill --frame ashe_idle1@0 --frame ashe_spell1_in@83 --frame ashe_spell1_in@167 --frame ashe_spell1_in@250 --frame ashe_spell1_in@333 --frame "ashe_spell1_in@333>ashe_idle1@0:0.5"
$A --name ashe_pose_skill2 --frame "ashe_idle1@0>ashe_spell2@0:0.5" --frame ashe_spell2@0 --frame ashe_spell2@267 --frame ashe_spell2@333 --frame ashe_spell2@450 --frame ashe_spell2@700 --frame "ashe_spell2@700>ashe_idle1@0:0.5"
$A --name ashe_pose_ult --frame "ashe_idle1@0>ashe_crit1@0:0.5" --frame ashe_crit1@0 --frame ashe_crit1@200 --frame ashe_crit1@300 --frame ashe_crit1@367 --frame ashe_crit1@500 --frame ashe_crit1@700 --frame "ashe_crit1@900>ashe_idle1@0:0.5"
$P --champ Ashe --yaw 55 --pitch 25 --size 360 --width 1.0 --ground 0.86 --fit 0.52 --shift 0.2 --name ashe_pose_dead $(for t in 0 500 700 900 1100 1300 1900; do printf -- "--frame ashe_death@%s " $t; done)
```

三视图 `*_model_chibi.png`：待机第 0 帧（`garen_2013_idle1@0` 加 `--mirror`、`ashe_idle1@0`），`--yaw 40`、`100`、`200` 各渲染一张横向拼接，都用 `--pitch 10 --size 800 --width 0.75 --fit 0.8 --ground 0.92`。
`tfm2_style_ref.png`：原版 archer、crossbowman、harpooner、knight、spellbreaker、fighter、swordman、priest 的待机第 1 帧和攻击中间帧，脚底对齐，放大 8 倍（从游戏的 `bundle.game_data` 读取）。

## 结果（2026-09-26 导入）

- 20 张角色图（两张造型图 + 18 张动作）这一轮就对了（Codex 只为留白重生成过几张）：头约占身高 1/3，缩到游戏尺寸后两人都能看到眼睛。原图覆盖了同名旧图，生成记录（交接说明、清单、实际用的提示词）在 [`chibi/`](chibi/)。
- `ashe_fx_volley.png` 没有采用：每帧只有 8 支箭，箭长和位置也不符合要求（交接说明里已标注）。W 继续用导入脚本拼的扇形：上一轮的冰霜箭按 9 个角度旋转、逐帧外移，箭数、角度和箭长都准确。
- 缩放按头对齐：GPT 每张图的头身比略有出入（艾希约 10%），按身高对齐会让头忽大忽小。每张图把待机的头按不同比例做相关匹配，再在原图尺寸下并排核对。
- 头部轨迹用大头骨骼重算（`pose_ref.py --track`）。盖伦的普攻、Q、R 保留原版前冲距离的 65–70%，收招弹回待机不明显。
- 头像截取点按原版英雄的规律重定：盖伦 (−1, −35)，艾希 (1, −32)。`tfm2_ase.py face` 给出建议值，`lint_mod.py` 会检查。
