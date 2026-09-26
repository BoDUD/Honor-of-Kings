# 拉克丝：给 GPT 的生图提示词

一共 19 张：1 张造型图、8 张角色动作、10 张特效。生成的 PNG 放进一个文件夹（或 `lux` 分支的 `assets/source/lux/`），然后告诉 Claude。
Claude 负责切帧、缩到游戏尺寸（身高约 34 px）、统一调色板、补 1 px 黑描边、对齐脚底，再接到技能上（`tools/art/import_lux.py`，导入时再写）。

这一轮从一开始就按盖伦、艾希 Q 版重画总结的规矩来（[`../CHIBI_REDRAW.md`](../CHIBI_REDRAW.md)）：
附原版英雄对照图、姿势参考图本身就是大头比例、先单独出造型图并检查头和脸，再同一批生成全部动作。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 法杖射出光弹。被动「光芒四射」：技能命中后，下一次普攻引爆光芒，追加魔法伤害 | `lux_attack` · `lux_fx_bolt` · `lux_fx_hit` · `lux_fx_ignite` |
| 技能 1 | Q「光之束缚」：直线光球，穿过的敌人受到魔法伤害并被定身。合并 W「曲光屏障」：施放时给自己和身边的友方英雄套护盾 | `lux_skill` · `lux_fx_q_orb` · `lux_fx_q_bind` · `lux_fx_shield` |
| 技能 2 | E「透光奇点」：抛出光球，落地后形成减速光圈，1 秒后自动引爆 | `lux_skill2` · `lux_fx_e_orb` · `lux_fx_e_zone` |
| 大招 | R「终极闪光」：跃起悬空，蓄力后发射一道极长的激光 | `lux_ult` · `lux_fx_r_beam` |
| 被动标记 | Q、E、R 命中的敌人身上出现光芒标记 | `lux_fx_mark` |

## 生成顺序（重要）

1. **先只生成造型图 `lux_ref.png`**（第 1 条），附三张图：`pack_style_ref.png`、`tfm2_style_ref_mage.png`、`lux_model_chibi.png`。
2. 检查造型图：
   - 头约占身高 1/3（头顶到下巴 ÷ 头顶到脚底 = 32%–36%）；
   - 脸大、亮，两只蓝眼睛和眉毛清楚，刘海在眼睛上方；
   - 3/4 正面朝右，看得到脸和胸口；
   - 法杖完整，握在画面右侧那只手里；
   - 服装、配色和 `lux_model_chibi.png` 一致。

   **不对就重画这一张，不要带着错的造型图往下做。**
3. 8 张动作图**同一批**生成，每张附两张图：第一张 `lux_ref.png`（造型和大小），第二张是对应的姿势参考图（动作）。受击 `lux_hit.png` 在英雄联盟里没有对应动作，只附第一张。
4. 10 张特效图不附图，可以和动作图同时生成。
5. 以后要改造型，全部动作图用新造型图整批重画，不和旧批次混用。

## 附图（压缩包里有；Riot 模型渲染只在本地用，不提交到仓库）

| 文件 | 内容 | 用在 |
|---|---|---|
| `pack_style_ref.png` | 本包已通过的盖伦、艾希 Q 版造型图（仓库里的 `garen_ref_chibi.png` + `ashe_ref_chibi.png`） | 造型图 |
| `tfm2_style_ref_mage.png` | 团战经理 2 原版的 8 个法系英雄（白魔导士、牧师、附魔师、德鲁伊、火法师、幻术师、暗法师、结界师），上排待机、下排攻击，放大 8 倍 | 造型图 |
| `lux_model_chibi.png` | 英雄联盟游戏内模型的正面、侧面、背面，已经是大头比例 | 造型图 |
| `lux_pose_*.png` | 英雄联盟原版动作，大头比例，每帧对应原版的一个时间点 | 各自的动作图 |

## 所有角色图的规则

- 每张图是**一行**，N 个一样大的正方形格子，每格一帧；格子之间不要留缝、边框、文字或编号。
- **尺寸：每格 256×256**，一行 N 格就是 N×256 宽、256 高。如果输出比例受限，在这一行的上下补透明空白，**不要裁切或压扁角色**。
- **背景透明**。做不到透明时：角色图用纯品红 `#FF00FF`。
- 同一张图里每一帧的角色一样大；脚底在每一格的同一高度（88%）。角色、整根法杖都在自己的格子里，不碰到相邻格子。
- **比例**：头约占身高的 1/3，脸大而清楚；每一帧的头一样大。
- 3/4 正面朝右：看得到脸和胸口，不画背影。
- 拉克丝的移动是**跑步**（有双脚离地的帧），0.8 秒一个循环。
- 法杖始终在同一只手里（待机时是画面右侧那只手）；只有大招里法杖离手、悬浮在她身前，落地时再接回。
- 角色图只画角色本身和法杖上的光。飞出去的光弹、光球、激光都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把提示词里的 "Lux" / "League of Legends" 删掉，只保留外观描述。

## 所有特效图的规则

- 没有黑描边；颜色用拉克丝的光系配色：白色核心 → 淡金 → 金黄，边缘带一点棱彩色（淡青、粉、淡紫）。
- 飞行道具一律**朝右**画，游戏会按飞行方向旋转；命中、标记类特效居中画，要空出人的位置的在提示词里写明。
- 背景透明（做不到时用纯黑 `#000000`）。

---

## 角色（9 张）

### 1. `lux_ref.png`：造型图，1 帧（附 `pack_style_ref.png`、`tfm2_style_ref_mage.png`、`lux_model_chibi.png`）

```text
Three attached images. FIRST: two approved heroes of this game pack (Garen and Ashe) - match their pixel-art style, 1-pixel outline, cel shading, level of detail, PROPORTIONS and size exactly, but do not copy their costumes; Lux is a petite young woman, about as tall as Ashe without the tip of Ashe's hood. SECOND: official heroes of the game Teamfight Manager 2 (mages and priests with staffs), top row idle, bottom row attacking - copy their proportions, the way their faces are drawn, and how a long staff is held and thrust at this size. THIRD: Lux's in-game model from League of Legends, front, side and back, already with the big head - use it for her hair, costume, colors and the shape of her wand.
Lux from League of Legends (default skin) as a 2D pixel art game sprite: a petite young Demacian mage girl. Thick honey-blonde hair ending just above her shoulders, big side-swept bangs, a dark brown hairband across the top of her head; big blue eyes; fair skin. A royal-blue high-collared long-sleeved bodysuit and royal-blue leggings; a gunmetal-silver breastplate with gold trim bands and two small red gems near the collar; small puffy white shoulder caps edged in gold; gunmetal forearm guards with gold rims; white gloves; a gold belt with a gold buckle; a short flared white skirt edged in gold; dark gunmetal armored knee-high boots with gold trim and small heels. Her signature weapon: a long slender wand-staff almost as tall as she is - a dark bronze shaft wrapped in a gold spiral ribbon, with ornate open golden filigree finials at both ends; the finial near her hand holds a small white-gold glow. Draw the wand clearly readable.
PROPORTIONS (most important), exactly like the heroes in the FIRST and SECOND images: the head is about ONE THIRD of her total height (from the top of the hair to the soles) - big and round; the FACE is large, lit and fully visible: the bangs sweep to the side ABOVE her eyes, two big blue eyes each with a dark outline and a 1-pixel white highlight, thin eyebrows, a small mouth - drawn bold and simple so it stays readable when the sprite is shrunk to 34 pixels tall; short legs, about one third of her height; a small, slim torso; the wand keeps its full length.
Style: pixel art sprite for Teamfight Manager 2, exactly like the FIRST image: chunky square pixels, hard edges, a 1-pixel black outline around the whole character, flat cel shading with 3-4 tones per color, no anti-aliasing, no gradients, no glow except the small light in the wand's finial, about 32-40 colors. 3/4 FRONT view facing right: we see her face, her chest and the front of her body. Never show her back.
Pose: the idle stance of the THIRD image's front view: feet apart, torso toward the viewer, head turned slightly to the right. She holds the wand in the hand on the RIGHT side of the image, near its upper end at hip height; the long shaft slants down and back across the front of her legs so its lower finial is near the ground to the LEFT of her feet. The other hand rests at her waist.
Layout: one single square image, 1024x1024, the character centered, feet on an invisible ground line at 88% of the image height, the character about 60% of the image height. Transparent background (if not possible: solid #FF00FF magenta). No text, no border, no shadow.
Before finishing, check: the head (hair top to chin) is 32-36% of the full height (hair top to soles); both eyes and eyebrows are clearly visible; the whole wand is inside the image.
```

8 张动作图的提示词都以同一段外观、比例、画风开头，可以整段复制。

### 2. `lux_idle.png`：待机，6 帧循环（附 `lux_ref.png` + `lux_pose_idle.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game idle from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the wand points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: IDLE, 6 frames, seamless loop, as in the pose reference: she stands relaxed but ready, feet apart, torso toward the viewer, head turned slightly right. The wand is held near its upper end at her hip in the hand on the right side of the image, the long shaft slanting down and back so its lower finial rests near the ground to the left of her feet. Only subtle breathing: shoulders and chest rise and fall 1 pixel, the hair sways slightly. Feet stay planted. Do not raise or swing the wand.
Layout: one horizontal row of 6 equal square cells, image size 1536x256, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole wand stays inside its own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

### 3. `lux_run.png`：跑步，8 帧循环（附 `lux_ref.png` + `lux_pose_run.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game movement animation from League of Legends, already with the big head, seen from the front, 8 frames left to right - one full cycle. Copy each frame's leg and arm positions and where the wand is exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RUN to the right, 8 frames, seamless loop, as in the pose reference. This is a RUN, not a walk: a light, bouncy, girlish stride, torso leaning forward a little, head up, looking ahead; in frames 1, 4, 5 and 8 BOTH feet are off the ground. The wand stays in the same hand as in the first image and swings with that arm: in frames 1-3 it trails low behind her, in frames 4-8 it swings forward and is held upright at her side, exactly like the reference. The hair bounces. The short legs keep the same length and shape in every frame; the body bobs up and down 2-3 pixels.
Layout: one horizontal row of 8 equal square cells, image size 2048x256, no gaps, no borders, no labels. The character is exactly as big as in the first image: when upright about 60% of the cell height; the ground line at 88% of the cell height in every cell (the feet leave it in the airborne frames); body horizontally centered; the whole wand stays inside its own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

### 4. `lux_attack.png`：普攻，6 帧（附 `lux_ref.png` + `lux_pose_attack.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game basic attack from League of Legends, already with the big head, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the wand points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: BASIC ATTACK, she fires a bolt of light from her wand, 6 frames, as in the pose reference: 1 from the idle stance of the first image she swings the wand back, level; 2 the wand drawn far back behind her to the left, her free hand pointing forward at the target; 3 she twists her body toward the right, the wand coming around low in front of her hips; 4 THRUST: she steps forward and thrusts the wand straight out to the right, level at chest height, arm fully extended, its finial flashing white-gold; 5 follow-through: she leans forward, the wand tip rising; 6 recovering toward the idle stance of the first image, the wand upright in front of her. Feet stay on the ground line. Do not draw the flying bolt.
Layout: one horizontal row of 6 equal square cells, image size 1536x256, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole wand stays inside its own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

### 5. `lux_skill.png`：Q「光之束缚」（技能 1），7 帧（附 `lux_ref.png` + `lux_pose_skill.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game Light Binding cast from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly - stance, lean, arms and where the wand points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: LIGHT BINDING, 7 frames, as in the pose reference: 1 from the idle stance of the first image she lifts the wand in front of her; 2 she raises the wand with both hands, pointing up and forward; 3 she leans back and holds the wand upright in front of her face, its finial gathering a ball of white-gold light, mouth open; 4 THRUST: she lunges and thrusts the wand forward to the right, the finial flaring bright white-gold; 5 follow-through: the wand swings down and back behind her, she leans forward; 6 still leaning forward, recovering; 7 back toward the idle stance of the first image. Feet stay on the ground line. Do not draw the flying orb.
Layout: one horizontal row of 7 equal square cells, image size 1792x256, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole wand and its glow stay inside their own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

### 6. `lux_skill2.png`：E「透光奇点」（技能 2），7 帧（附 `lux_ref.png` + `lux_pose_skill2.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game Lucent Singularity cast from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly - stance, arms and where the wand points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: LUCENT SINGULARITY, she lobs an orb of light with a big swing of the wand, 7 frames, as in the pose reference: 1 from the idle stance of the first image she swings the wand back, level; 2 wind-up: the wand raised upright behind her, arm drawn back; 3 the wand swept low behind her to the left, her free hand pointing forward at the target; 4 a sidearm swing: the wand sweeps around at hip height; 5 RELEASE: the wand whips forward, level, pointing right, its finial flashing white-gold; 6 she holds the wand upright at arm's length in front of her; 7 back toward the idle stance of the first image. Feet stay on the ground line. Do not draw the orb.
Layout: one horizontal row of 7 equal square cells, image size 1792x256, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole wand stays inside its own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

### 7. `lux_ult.png`：R「终极闪光」，8 帧（附 `lux_ref.png` + `lux_pose_ult.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game Final Spark from League of Legends, already with the big head, seen from the front, 8 frames left to right. Copy each frame's pose exactly - body, arms, legs, how high she floats, and where the floating wand is. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: FINAL SPARK, 8 frames, as in the pose reference: 1 she crouches a little, gathering herself; 2 she springs up into the air and lets go of the wand, which floats away in front of her (to the right), turning level; 3 floating in the air, arms spread wide, head tilted back, the wand hovering level in front of her at the height of her knees, pointing right, its finial glowing; 4 still floating, the wand trembling and glowing brighter white-gold with small rainbow-tinted sparkles; 5 the moment she FIRES: the wand's tip blazes with a bright white flash, her hair and skirt blown back; 6 recoil: she is pushed a little higher, face up; 7 she tucks into a ball in the air (the only frame where her face may be hidden); 8 landed on both feet, catching the wand and holding it upright. The ground line is the same in every cell; she is in the air in frames 2-7, as high as in the reference. The wand is separate from her hands in frames 2-7. Draw only the glow at the wand, not the laser beam.
Layout: one horizontal row of 8 equal square cells, image size 2048x256, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 55% of the cell height; the ground line at 88% of the cell height in every cell; the character and the floating wand stay inside their own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

### 8. `lux_hit.png`：受击，2 帧（只附 `lux_ref.png`）

```text
Same character as the ATTACHED image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large, clearly visible face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest. Never show her back. The head stays the same big size in every frame and the face is never hidden.
Animation: HIT REACTION, 2 frames, based on the idle stance of the attached image: 1 flinches from a blow: upper body jolted back and to the left, eyes squeezed shut, the wand still held in her hand, feet planted; 2 recovering, almost back in the idle stance of the attached image.
Layout: one horizontal row of 2 equal square cells, image size 512x256, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole wand stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 9. `lux_dead.png`：死亡，7 帧（附 `lux_ref.png` + `lux_pose_dead.png`）

```text
Same character as the FIRST attached image (Lux, League of Legends) - copy her exact design, colors, PROPORTIONS and size: a chibi Demacian mage girl with a BIG head (one third of her height) and a large face with big blue eyes (the bangs stay above the eyes), honey-blonde hair with a dark brown hairband, royal-blue bodysuit and leggings, gunmetal breastplate with gold trim, white gold-edged shoulder caps, short white skirt with gold trim, white gloves, dark gunmetal knee boots with gold trim, and a long slender wand-staff with a gold spiral and ornate golden finials.
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view, same camera as the first image. The head stays the same big size in every frame.
Pose reference: the SECOND attached image is a 3D render of Lux's real in-game death from League of Legends, already with the big head, seen from the front, 7 frames left to right. Copy each frame's pose exactly, including how high she is in the air. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: DEATH, 7 frames, as in the pose reference: 1 the idle stance of the first image; 2 struck: she reels, turning away, the wand swinging out; 3 thrown backward off her feet, body tilting back, arms flung; 4 falling backward through the air, almost horizontal, head to the left; 5 hitting the ground on her back; 6 rolling onto her side; 7 lying still on the ground, head to the left, the wand dropped beside her. She lies ON the ground line in frames 5-7.
Layout: one horizontal row of 7 equal square cells, image size 1792x256, no gaps, no borders, no labels. The character is exactly as big as in the first image (about 60% of the cell height when standing); the ground line at 88% of the cell height in every cell (she is in the air in frames 3-4); the whole body and the wand stay inside their own cell. If the output aspect ratio is restricted, add empty transparent space above and below the row instead of cropping or squeezing the sprites. Transparent background (if not possible: solid #FF00FF magenta).
```

---

## 技能特效（10 张）

10 张特效的提示词都以同一段画风和配色开头。

### 10. `lux_fx_bolt.png`：普攻光弹（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with a few tiny prismatic glints (#A8F0FF, #FFB8E8).
Effect: LUX BASIC ATTACK bolt in flight, 4 frames, seamless loop: a small glowing orb of white-gold light with a white-hot core flying to the RIGHT, with a short tapering tail of light and a few sparkles behind it (to the left); the tail and sparkles flicker from frame to frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 1024x128; the orb at the same spot in the right half of every cell, the whole bolt about 60% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `lux_fx_hit.png`：普攻命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with a few tiny prismatic glints (#A8F0FF, #FFB8E8).
Effect: LUX BASIC ATTACK hit, 5 frames: 1 a small white flash; 2 a burst of short golden rays and sparkles from the center; 3 the rays spread, a thin ring of light; 4 sparkles drifting outward and shrinking; 5 the last sparkles fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the burst at most half the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `lux_fx_q_orb.png`：Q 光之束缚的光球（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with pale prismatic accents (#A8F0FF, #FFB8E8, #D2B8FF).
Effect: LIGHT BINDING orb in flight, 4 frames, seamless loop: a bright sphere of white-gold light with a white-hot core and a pale-cyan rim, flying to the RIGHT, trailing two thin ribbons of light that twist around each other behind it (to the left), with small sparkles; the ribbons twist a little further every frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 1024x128; the sphere at the same spot near the right side of every cell, the sphere about 60% of the cell height, the whole effect about 80% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `lux_fx_q_bind.png`：Q 定身光环（套在敌人身上），8 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with pale prismatic accents (#A8F0FF, #FFB8E8, #D2B8FF).
Effect: LIGHT BINDING bind on an enemy, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 bright ribbons of white-gold light snap around the empty space; 2 they tighten into two glowing rings of light, one around the waist and one around the knees, each ring a flat ellipse seen slightly from above; 3-6 the rings hold and shimmer, small sparkles and short light streaks around them (frames 3-6 form a seamless loop); 7 the rings crack into shards of light; 8 the shards fade.
Layout: one horizontal row of 8 equal square cells, image size 2048x256, the empty person-sized space at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `lux_fx_shield.png`：W 曲光屏障护盾（套在友方身上），8 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, white light with prismatic rainbow edges (#FFFFFF, #FFF6D5, #A8F0FF, #FFB8E8, #D2B8FF, #FFE680).
Effect: PRISMATIC BARRIER shield on an ally, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person, and keep the inside of the shield empty and transparent. 1 prismatic sparkles gather around the space; 2 a thin glowing oval bubble outline appears around the whole space, white with rainbow-tinted edges; 3-6 the bubble shimmers: short white highlight arcs slide along its outline, a few sparkles drift (frames 3-6 form a seamless loop); 7 the bubble breaks into prismatic sparkles; 8 the last sparkles fade.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the bubble about 75% of the cell height and 50% of the cell width, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `lux_fx_e_orb.png`：E 透光奇点的光球（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with pale prismatic accents (#A8F0FF, #FFB8E8, #D2B8FF).
Effect: LUCENT SINGULARITY orb in flight, 4 frames, seamless loop: a glowing sphere of white-gold light with a bright four-pointed star in its core and a thin ring of light spinning around it at a tilt, a few sparkles around it; the ring turns a quarter further every frame.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the orb centered in every cell, about 40% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `lux_fx_e_zone.png`：E 减速光圈 + 引爆，8 帧

原版的地面范围特效是正圆或略扁的圆（宽高比约 1–1.35），这张也照这个比例画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with pale prismatic accents (#A8F0FF, #FFB8E8, #D2B8FF).
Effect: LUCENT SINGULARITY field and detonation, 8 frames, seen from the same slightly top-down game camera. Frames 1-4 (a seamless loop): a wide circle of soft golden light lies flat on the ground - a slightly flattened circle about 1.3 times wider than tall that fills 90% of the cell width - with a bright thin rim and faint star-shaped light lines inside; the singularity orb (a glowing white-gold sphere with a four-pointed star in its core) hovers just above the center of the circle and pulses; a few sparkles rise. Frame 5: DETONATION - the orb bursts in a blinding white star flash; frame 6: a big starburst explosion of white-gold light filling the whole circle, rays shooting out; frame 7: the explosion fades into a ring of sparkles along the rim; frame 8: the last sparkles fade.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the center of the circle at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `lux_fx_r_beam.png`：R 终极闪光激光，6 帧（竖排）

游戏里这张图画在大招的长条判定范围上（长 240、宽 16），激光很长，所以 6 帧**上下排成一列**，每帧是一条横向的长条。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with prismatic fringes (#A8F0FF, #FFB8E8, #D2B8FF).
Effect: FINAL SPARK, a giant laser, 6 frames stacked in ONE COLUMN, frame 1 at the top. Every frame is a very wide horizontal strip (12 times wider than tall). The laser starts near the LEFT end of the strip (where the caster's floating wand is) and runs perfectly straight and horizontal all the way to the RIGHT edge, along the middle of the strip. 1 targeting: a thin, faint white-gold line along the whole length, a small glowing spark at the left end; 2 charging: the line a little brighter, a ball of white light gathering at the left end with sparkles pulled into it; 3 ignition: a blinding white flash at the left end and the beam bursting forward, already reaching the right edge; 4 FULL BEAM: a huge thick laser along the whole strip - a pure white core, a golden layer around it and prismatic (pale cyan, pink, lavender) outer fringes, about 70% of the strip height, with crackling sparkles along its edges; 5 full beam again, its edges rippling differently; 6 fading: the beam shrinks into a narrow flickering line and breaks into sparkles.
Layout: ONE COLUMN of 6 equal rows, each row one frame, image size 2048x1024 (each row about 2048x170); the beam centered vertically in its row and starting at the same place near the left end of every row; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 18. `lux_fx_mark.png`：被动光芒标记（敌人身上），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with pale prismatic accents (#A8F0FF, #FFB8E8).
Effect: ILLUMINATION mark on an enemy, 6 frames: 1 a tiny spark appears at the center of the cell; 2 it opens into a glowing four-pointed white-gold star with a thin halo ring around it; 3-5 the star pulses and slowly turns, tiny sparkles circle it (frames 2-5 form a seamless loop); 6 the star fades.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the star centered in every cell, the star with its halo about 35% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 19. `lux_fx_ignite.png`：被动引爆（普攻命中带标记的敌人），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, radiant light-magic color ramp (#FFFFFF, #FFF6D5, #FFE680, #FFC933, #E89B1A) with a few prismatic glints (#A8F0FF, #FFB8E8, #D2B8FF).
Effect: ILLUMINATION detonation, 6 frames: 1 a bright white flash at the center; 2 a big eight-pointed starburst of white-gold light with long thin rays; 3 the rays shoot outward and a ring of light expands; 4 the ring widens and thins, sparkles scatter; 5 sparkles drifting; 6 the last sparkles fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst centered in every cell, at most 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧时长是计划值，导入时按实际画面微调；出手帧对齐数据里的出手时刻。

| 文件 | 帧数 | 游戏里的用途 | 计划帧时长 |
|---|---:|---|---|
| `lux_idle.png` | 6 | `idle` | 6 × 178 ms（英雄联盟的待机循环 1.07 秒） |
| `lux_run.png` | 8 | `run` | 8 × 100 ms（英雄联盟的跑步循环 0.8 秒） |
| `lux_attack.png` | 6 | `attack` | 70/80/60/100/100/90，第 4 帧出手（tick 13） |
| `lux_skill.png` | 7 | `skill`（Q + W） | 60/70/90/90/80/100/90，第 4 帧出手（tick 13） |
| `lux_skill2.png` | 7 | `skill2`（E） | 60/70/70/60/100/120/90，第 5 帧出手（tick 16） |
| `lux_ult.png` | 8 | `ult`（R） | 100/80/120/200/180/120/150/150，第 5 帧发射激光（tick 30）；悬空高度按激光高度下调，让悬浮的法杖落在激光里 |
| `lux_hit.png` | 2 | `hit` | 2 × 120 ms |
| `lux_dead.png` | 7 | `dead` | 100/100/120/120/150/200/400 |
| `lux_fx_bolt.png` | 4 | 飞行道具 `league_lux_bolt`（普攻） | 4 × 60 ms 循环 |
| `lux_fx_hit.png` | 5 | 特效 `league_lux_hit` | 5 × 60 ms |
| `lux_fx_q_orb.png` | 4 | 飞行道具 `league_lux_q_orb`（Q） | 4 × 70 ms 循环 |
| `lux_fx_q_bind.png` | 8 | 特效 `league_lux_q_bind`（跟随目标，定身 1.5 秒：1–2、3–6 两遍、7–8） | 80/80 + 8 × 125 + 90/90 |
| `lux_fx_shield.png` | 8 | 特效 `league_lux_shield`（跟随友方） | 80/80 + 8 × 100 + 90/90 |
| `lux_fx_e_orb.png` | 4 | 飞行道具 `league_lux_e_orb`（E 抛物线） | 4 × 80 ms 循环 |
| `lux_fx_e_zone.png` | 8 | 范围 `league_lux_e_burst`（1–4 两遍 = 1 秒光圈，5–8 = 引爆） | 8 × 125 + 4 × 100 |
| `lux_fx_r_beam.png` | 6（竖排） | `league_lux_r_beam`（`LineRangeProjectile`，拉到 240 px 长） | 200/217/60/130/130/130 |
| `lux_fx_mark.png` | 6 | 特效 `league_lux_mark`（跟随目标） | 1、2–5 两遍、6 |
| `lux_fx_ignite.png` | 6 | 特效 `league_lux_ignite` | 6 × 60 ms |

`lux_ref.png` 只用来保持造型一致，不进游戏。

## 姿势参考图：英雄联盟原版动作和时间点

客户端里拉克丝的动作：待机 `lux_idle1`（1.07 秒一个呼吸循环）；移动只有 `lux_run`（0.8 秒一步循环，一个循环里约一半时间双脚离地，是跑不是走，脚底滑动约 210 单位/秒）；普攻 `lux_attack1`（约 233 ms 向前平刺出手）；Q `lux_spell1`（约 233 ms 出手）；W `lux_spell2`（没用到：W 合并进 Q）；E `lux_spell3`（约 267 ms 甩出光球）；R `lux_spell4`（0–130 ms 下蹲，130–800 ms 跃起悬空、法杖悬在身前约腰的高度并抖动蓄力，约 870 ms 发射时被后坐力推高，1000–1600 ms 空中蜷身，1800 ms 落地）；死亡 `lux_death`（被击飞，约 530 ms 仰面落地，最后 0.3 秒沉入地下，不用）。

拉克丝的动作大多是旧格式 `r3d2anmd` v3（R 是 v4），`pose_ref.py` 这一轮加上了这两种格式。她的胸口朝向自己的右侧，所以和盖伦一样加 `--mirror`（从另一侧渲染再翻转），所有动作同一侧，法杖不会换手。

`A>B:0.5` 表示两个动作各一半的混合姿势，英雄联盟切换动作时就是这样过渡的，用来让每个动作从待机开始、回到待机结束。

| 参考图 | 帧（动作@毫秒） |
|---|---|
| `lux_pose_idle.png` | idle1@0, 178, 356, 533, 711, 889 |
| `lux_pose_run.png` | run@0, 100, 200, 300, 400, 500, 600, 700 |
| `lux_pose_attack.png` | idle1@0>attack1@67:0.5, attack1@133, 200, 233, 300, attack1@767>idle1@0:0.5 |
| `lux_pose_skill.png` | idle1@0>spell1@67:0.5, spell1@100, 167, 233, 267, 433, spell1@900>idle1@0:0.5 |
| `lux_pose_skill2.png` | idle1@0>spell3@67:0.5, spell3@100, 167, 233, 267, 433, spell3@900>idle1@0:0.5 |
| `lux_pose_ult.png` | idle1@0>spell4@67:0.5, spell4@200, 400, 600, 800, 933, 1200, 1800 |
| `lux_pose_dead.png` | death@0, 133, 267, 400, 533, 800, 1400 |

表里省略了动作名前缀 `lux_`。重新生成的命令：

```bash
P="python tools/lol/pose_ref.py --champ Lux --hq --head 2.0 --legs 0.8 --mirror --yaw 55 --size 360 --bg 225,225,225 --no-labels --out ref"
S="$P --pitch 25 --ground 0.86"
$S --width 1.0 --fit 0.62 --shift 0.04 --name lux_pose_idle $(for t in 0 178 356 533 711 889; do printf -- "--frame lux_idle1@%s " $t; done)
$S --width 1.0 --fit 0.62 --shift 0.06 --name lux_pose_run $(for t in 0 100 200 300 400 500 600 700; do printf -- "--frame lux_run@%s " $t; done)
$S --width 1.1 --fit 0.6 --name lux_pose_attack --frame "lux_idle1@0>lux_attack1@67:0.5" --frame lux_attack1@133 --frame lux_attack1@200 --frame lux_attack1@233 --frame lux_attack1@300 --frame "lux_attack1@767>lux_idle1@0:0.5"
$S --width 1.1 --fit 0.6 --name lux_pose_skill --frame "lux_idle1@0>lux_spell1@67:0.5" --frame lux_spell1@100 --frame lux_spell1@167 --frame lux_spell1@233 --frame lux_spell1@267 --frame lux_spell1@433 --frame "lux_spell1@900>lux_idle1@0:0.5"
$S --width 1.1 --fit 0.6 --name lux_pose_skill2 --frame "lux_idle1@0>lux_spell3@67:0.5" --frame lux_spell3@100 --frame lux_spell3@167 --frame lux_spell3@233 --frame lux_spell3@267 --frame lux_spell3@433 --frame "lux_spell3@900>lux_idle1@0:0.5"
$P --pitch 25 --width 1.15 --fit 0.5 --ground 0.9 --shift -0.08 --name lux_pose_ult --frame "lux_idle1@0>lux_spell4@67:0.5" --frame lux_spell4@200 --frame lux_spell4@400 --frame lux_spell4@600 --frame lux_spell4@800 --frame lux_spell4@933 --frame lux_spell4@1200 --frame lux_spell4@1800
$P --pitch 12 --width 1.3 --fit 0.5 --ground 0.86 --shift 0.16 --name lux_pose_dead $(for t in 0 133 267 400 533 800 1400; do printf -- "--frame lux_death@%s " $t; done)
```

死亡用较低的俯角（`--pitch 12`）：她被击飞时向后（离镜头远）移动约 160 单位，俯角 25 度会让躺在地上的身体看起来浮在地面上方。

三视图 `lux_model_chibi.png`：待机第 0 帧（`lux_idle1@0`，`--mirror --head 2.0 --legs 0.8 --hq`），`--yaw 40`、`100`、`200` 各渲染一张横向拼接，都用 `--pitch 10 --size 800 --width 0.75 --fit 0.8 --ground 0.92`。

`tfm2_style_ref_mage.png`：原版 white_mage、priest、enchanter、druid、pyromancer、illusionist、dark_mage、barrier_magician 的待机第 1 帧和攻击中间帧，脚底对齐，放大 8 倍（从游戏的 `bundle.game_data` 读取）。`pack_style_ref.png`：`garen/garen_ref_chibi.png` 和 `ashe/ashe_ref_chibi.png` 左右拼接。
