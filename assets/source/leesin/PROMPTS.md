# 李青：给 GPT 的生图提示词（直接按游戏原尺寸画）

一共 19 张图：
- 1 张原尺寸造型图；
- 9 张原尺寸动作图；
- 9 张特效图。

生成的 PNG 和 Codex 的交接说明放进一个文件夹，然后告诉 Claude。Claude 按 8×8 方块逐格读色，放回每帧的锚点，接到技能上（`tools/art/import_native.py`）。

这一轮直接走原尺寸，不再先画一轮高清动作条（拉克丝、艾希的原尺寸重画见 [`../NATIVE_REDRAW.md`](../NATIVE_REDRAW.md)）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「疾风骤雨」 | 出拳；施放技能后接下来 2 次普攻加攻速 | `leesin_attack` · `leesin_fx_hit` |
| 技能 1 | Q「天音波」打出音波，命中后自动「回音击」飞踢冲过去 | `leesin_skill` · `leesin_q2` · `leesin_fx_q_wave` · `leesin_fx_q_mark` · `leesin_fx_q2_hit` |
| 技能 2 | E「天雷破」跃起捶地、震波减速；合并 W「金钟罩 / 铁布衫」：护盾和吸血 | `leesin_skill2` · `leesin_fx_e_wave` · `leesin_fx_shield` |
| 大招 | R「猛龙摆尾」回旋踢把目标踢飞，撞到的敌人被击飞 | `leesin_ult` · `leesin_fx_r_kick` · `leesin_fx_r_dragon` · `leesin_fx_knockup` |
| 其他 | 待机、跑步、受击、死亡 | `leesin_idle` · `leesin_run` · `leesin_hit` · `leesin_dead` |

## 这一轮的做法

拉克丝、艾希第一次都是先画高清像素画，再压到 34 px，结果在游戏里发糊，只好按原尺寸重画第二遍。李青一开始就按原尺寸画。

1. **原尺寸姿势参考**：`tools/lol/native_pose.py` 把英雄联盟客户端里李青的真实动作，直接渲染成游戏尺寸。
   - 大头比例：头 2 倍、腿 0.8 倍，辫子保持原版长度。
   - 待机时头顶到脚底 34 px。
   - 每个游戏像素取 8×8 方块的平均色，放大 8 倍显示（`leesin_native_*.png`）。
   - 姿势、大小、每帧在格子里的位置都已经算好：头部轨迹、前冲（保留原版的 70%）、跃起高度、死亡击飞（65%）。
2. **高清对照**：同一批帧的高清渲染（`leesin_pose_*.png`），格子和位置完全一样。缩小图看不清姿势时看它。
3. **每帧锚点**：记在 `leesin_cells.json` 里。新图画在同样的格子里，按同一个锚点切出来，就站在参考图那一帧的位置上。

这条路线（不经过高清第一轮）当时还没验证过；结果是走通了，但动作画大了，导入前要按头缩回（见文末「结果」）。

## 生成顺序（重要）

1. **先只生成造型图 `leesin_native.png`**（第 1 条），附四张图（见提示词）。
2. 检查造型图（放大看方块）：
   - 从光头头顶到脚底正好约 34 个方块（272 px），辫子另外高出头顶；
   - 所有方块都是 8×8、对齐同一个网格，没有半个方块、没有模糊边；
   - 颜色不超过 20 种，没有杂色点，大块平涂；
   - **脸**：头约占身高 1/3；红色蒙眼布是一条横过脸的红带，约 2 个方块高，遮住眼睛，**不画眼睛**；上面是光头，下面露出脸颊和 1 格嘴；缩到 1 倍一眼能认出"光头 + 红蒙眼布"；
   - 辫子是一条 1 格宽的深色线，带几格红色缠绳，末端是金环；
   - 服装配色和 `leesin_model_chibi.png` 一致：赤膊，红色护手缠布，浅灰腰带和金扣，长红前襟，深蓝灯笼裤，红色绑腿；
   - 3/4 正面朝右，看得到脸和胸口。

   **不对就重画这一张，不要带着错的造型图往下做。**
3. 9 张动作图**同一批**生成，每张附三张图：
   - 第一张：新造型图 `leesin_native.png`；
   - 第二张：对应的 `leesin_native_<动作>.png`（原尺寸姿势参考）；
   - 第三张：对应的 `leesin_pose_<动作>.png`（同一批帧的高清渲染）。
4. 输出排版和第二张附图完全一样：几列几行、每格多大（64×72 个方块）、每帧在第几格。
5. 9 张特效图不附图，可以和动作图同时生成。
6. **交给 Claude 之前请 Codex 整理**（和上次 `native/` 那批一样）：
   - 每个像素都是严格对齐的 8×8 纯色块，透明度只有全透明和不透明；
   - 全部角色图共用造型图的调色板，不超过 20 色，去掉孤立的杂色点；
   - **待机 6 帧用同一个头**（从造型图取），只随身体上下移动，这样循环不会抖；其他动作的头保持同样大小和颜色；
   - 每帧留在它的格子里、画在哪就是哪，**不要按包围框重新居中**（锚点记在 `leesin_cells.json`）；
   - 附交接说明 `HANDOFF.md`、逐帧记录 `MANIFEST.json`（文件哈希、每帧的包围框）和实际用的提示词。
7. 以后要改造型，全部动作图用新造型图整批重画，不和旧批次混用。

## 附图（压缩包里有）

Riot 模型渲染和原版游戏截图只在本地用，不提交到仓库。

| 文件 | 内容 | 用在 |
|---|---|---|
| `leesin_native_design.png` | 原版战斗待机第 0 帧，直接渲染成游戏尺寸（34 px），8 倍显示，128×128 方块画布 | 造型图 |
| `tfm2_style_ref_martial.png` | 团战经理 2 原版的格斗家、武僧、忍者、剑士、猎人、骑士，上排待机、下排攻击，8 倍 | 造型图 |
| `leesin_model_chibi.png` | 英雄联盟游戏内模型的正面、侧面、背面，大头比例 | 造型图 |
| `pack_native_ref.png` | 本包按原尺寸重画后的拉克丝、艾希，8 倍 | 造型图 |
| `leesin_native_<动作>.png` | 原版动作渲染成游戏尺寸，8 倍，按格子排好 | 各自的动作图 |
| `leesin_pose_<动作>.png` | 同一批帧的高清渲染，格子和位置完全相同 | 各自的动作图 |
| `leesin_cells.json` | 每帧锚点在格子里的位置和帧时长（给 Codex 核对位置用） | 整理 |

## 所有角色图的规则

- **像素尺寸（最重要）**：
  - 角色是游戏里的小精灵，站着时从光头头顶到脚底 34 像素高；
  - 按真正的低分辨率像素画来画，再整体放大 8 倍输出；
  - 每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格；
  - 没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **干净，不要细节**：
  - 整个精灵最多 20 种颜色，每种材质 2–3 个平涂色阶；
  - 不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；
  - 1 个方块宽的近黑色描边。
- **脸（按蒙眼布调整）**：
  - 头约占身高 1/3，光头 2–3 个肤色色阶；
  - 红色蒙眼布是约 2 个方块高的红带，横过眼睛，后脑打结，飘出两条短布尾；
  - 李青是盲僧，**不画眼睛**；蒙眼布下面露出脸颊和 1 格嘴。
- **辫子**：
  - 从头顶发髻（1 格金色发箍）长出，1 格宽，深蓝黑色，有几格红色缠绳，末端是 2×2 的金环；
  - 随动作甩动，和参考图一致；
  - 不超出自己的格子。
- **朝向**：3/4 正面朝右，看得到脸和胸口。转身、弯腰时也把胸口转向观众，不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 角色图只画角色本身。音波、震波、护盾、龙等都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把 "Lee Sin" / "League of Legends" 删掉，只保留外观描述。

## 所有特效图的规则

- 没有黑描边。
- 颜色用李青的"气"：白色核心 → 淡金 → 金黄 → 橙 → 深橙红。
- 飞行道具一律**朝右**画，游戏会按飞行方向旋转；命中类特效居中画。
- 背景透明（做不到时用纯黑 `#000000`）。

---

## 角色（10 张）

### 1. `leesin_native.png`：造型图

附四张图：`leesin_native_design.png`、`tfm2_style_ref_martial.png`、`leesin_model_chibi.png`、`pack_native_ref.png`。

```text
Four attached images. FIRST: League of Legends' Lee Sin rendered at our game's exact sprite size and shown enlarged 8x - every game pixel is an 8x8 block. Its size, pose and place are right, but it is a blurry downscaled 3D render: too many colors, no outline, details that do not read. SECOND: official heroes of the game Teamfight Manager 2 (martial artists: a bare-chested brawler, a bald monk, a ninja, a swordsman...), top row idle, bottom row attacking, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, a 1-pixel dark outline, bold readable heads. THIRD: Lee Sin's in-game model with chibi proportions, front, side and back - use it for his costume, colors, blindfold and braid, not for the level of detail. FOURTH: two heroes of this pack drawn at this exact size - match their pixel size, outline and cleanliness.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall from the top of his bald head to his soles (his braid rises a little above that), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow.
Lee Sin from League of Legends (default skin), chibi: a bald young martial-arts monk with tanned skin; a red cloth blindfold wrapped around his eyes and knotted at the back of his head, two short tails fluttering behind; a long dark braid growing from a small gold-cuffed topknot on his crown, wrapped with red bands, ending in a gold ring, hanging behind his shoulder; a bare muscular chest; red cloth wraps with a light pattern on his hands and forearms; a light grey sash with a round gold buckle; a long red loincloth hanging in front down to his knees, edged in gold; dark navy baggy pants; red wraps on his shins; dark shoes.
Pixel rules (most important): at most 20 colors in total; every material 2-3 flat shades (light, base, shadow); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Keep only details that read at this size: the blindfold a solid red band 2 squares tall across the face with 2-3 red squares for its tails; the braid a 1-square dark line with 2-3 red squares along it and a 2x2 gold ring at its end, a 1-square gold cuff at its root; the chest skin in 3 flat shades with one or two darker squares for the muscles; the hand and forearm wraps flat red with 1-2 light squares; the sash one light grey row with a 2x2 gold buckle; the loincloth flat red with a 1-square gold edge; the pants 2 navy shades; the shin wraps red; the shoes dark. Drop every other trim, tattoo and pattern.
Face: the head is one third of his height; the bald crown in 2-3 skin shades with a highlight; the red blindfold band covers his eyes completely - he is blind, draw NO eyes; under the band 2-3 rows of skin (cheeks, nose) and a 1-square mouth. At game size the head must read at once as "bald head with a red band across the eyes".
Pose, size and place: exactly as in the FIRST image - the same fighting stance (a wide horse stance, fists raised in front of him), the same height, feet on the same line 28 squares (224 px) above the bottom of the image, the character horizontally centered. 3/4 FRONT view facing right: we see his face and chest.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: he is 34 squares tall without the braid, all squares 8x8 on one grid, at most 20 colors, the blindfold is a clear red band across the face and no eyes are drawn.
```

9 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

### 2. `leesin_idle.png`：待机，6 帧，3 列 × 2 行

附 `leesin_native.png` + `leesin_native_idle.png` + `leesin_pose_idle.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: IDLE, 6 frames, a seamless loop, as in the SECOND image: his fighting stance - a wide horse stance, fists raised in front of him - bouncing once: he sinks 2-3 squares in frames 2-3 and rises back by frame 6; the braid sways. The head is exactly the same drawing in all 6 frames, it only moves up and down with the body; the feet stay planted.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 64x72 squares (512x576 px), image 1536x1152; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 3. `leesin_run.png`：跑步，8 帧，4 列 × 2 行

附 `leesin_native.png` + `leesin_native_run.png` + `leesin_pose_run.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: RUN loop, 8 frames, as in the SECOND image: a low, forward-leaning run with long leaping strides - both feet off the ground in frames 2, 3, 6 and 7, one foot pushing off the ground in frames 1, 4, 5 and 8; his arms swing back; the braid streams straight out behind him. The body height and lean as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 64x72 squares (512x576 px), image 2048x1152; frame N in the same cell as in the SECOND image, at the same place, feet (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 4. `leesin_attack.png`：普攻，6 帧，3 列 × 2 行

附 `leesin_native.png` + `leesin_native_attack.png` + `leesin_pose_attack.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: BASIC ATTACK, a lunging punch, 6 frames, as in the SECOND image: 1 leaving his stance; 2-3 he draws back, turning his shoulders, fists up; 4 THE HIT: a deep lunge, one fist punched straight out to the right, arm fully extended; 5 follow-through, still low; 6 back toward his stance. Draw no effect.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 64x72 squares (512x576 px), image 1536x1152; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 5. `leesin_skill.png`：Q「天音波」发招，7 帧，4 列 × 2 行（最后一格空）

附 `leesin_native.png` + `leesin_native_skill.png` + `leesin_pose_skill.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: SONIC WAVE, 7 frames, as in the SECOND image: 1 leaving his stance; 2-3 he spreads his arms and raises his hands in a wide stance; 4 he crouches and coils; 5 THE RELEASE: a deep forward lunge, his open palm thrust straight out to the right; 6 he holds the low palm-strike stance; 7 he rises back into his horse stance. Draw no wave and no glow - the sonic wave is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x72 squares (512x576 px), image 2048x1152; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 6. `leesin_q2.png`：Q「回音击」飞踢，7 帧，4 列 × 2 行（最后一格空）

附 `leesin_native.png` + `leesin_native_q2.png` + `leesin_pose_q2.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: RESONATING STRIKE, a flying kick, 7 frames, as in the SECOND image: 1-2 he springs off and tucks into a forward roll in the air; 3-5 he unfolds into a flying kick, one leg stretched straight out to the right, his body almost horizontal, high above the ground as in the SECOND image, the braid streaming behind him; 6-7 he lands on both feet in his stance. Draw no effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x72 squares (512x576 px), image 2048x1152; frame N in the same cell as in the SECOND image, at the same place and the same height above the cell's ground line (10 squares above the bottom of the cell) - he is in the air in frames 1-5. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 7. `leesin_skill2.png`：E「天雷破」，7 帧，4 列 × 2 行（最后一格空）

附 `leesin_native.png` + `leesin_native_skill2.png` + `leesin_pose_skill2.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: TEMPEST, a ground slam, 7 frames, as in the SECOND image: 1 he crouches; 2 he springs straight up; 3 in the air, his right fist raised high; 4 THE IMPACT: he lands on one knee and punches the ground in front of him - his head is down, but his chest and the blindfold still face the viewer; 5-6 he rises from the crouch; 7 back toward his stance. Draw no shockwave and no dust - they are a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x72 squares (512x576 px), image 2048x1152; frame N in the same cell as in the SECOND image, at the same place and height, feet (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 8. `leesin_ult.png`：R「猛龙摆尾」，8 帧，4 列 × 2 行

附 `leesin_native.png` + `leesin_native_ult.png` + `leesin_pose_ult.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, swinging as in the SECOND image and staying inside its cell. 3/4 FRONT view facing right; never draw his back - when he spins or bends over, keep his chest turned toward the viewer.
Animation: DRAGON'S RAGE, a spinning roundhouse kick, 8 frames, as in the SECOND image: 1 leaving his stance; 2-3 he jumps and tucks into a spin in the air; 4 he unfolds with his arms spread; 5 THE KICK: a huge roundhouse kick, one leg stretched straight out to the right at chest height; 6 follow-through, the leg still high; 7 he lands in a crouch; 8 he rises into his stance. Keep his chest toward the viewer while he spins. Draw no effect - the dragon is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 64x72 squares (512x576 px), image 2048x1152; frame N in the same cell as in the SECOND image, at the same place and the same height above the cell's ground line (10 squares above the bottom of the cell) - he is in the air in frames 2-6. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 9. `leesin_hit.png`：受击，2 帧，2 列 × 1 行

附 `leesin_native.png` + `leesin_native_hit.png` + `leesin_pose_hit.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep his head as in the FIRST image and the same size in every frame: the bald head, the red blindfold band across the eyes, no eyes. Keep the braid a 1-square dark line with red bands and its gold ring, staying inside its cell. 3/4 FRONT view facing right, never his back.
Animation: HIT, 2 frames, as in the SECOND image: 1 he flinches from a blow - head and shoulders jolted back, arms thrown out; 2 recovering toward his stance.
Layout: exactly like the SECOND image - a grid of 2 columns x 1 row of cells, each cell 64x72 squares (512x576 px), image 1024x576; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 10. `leesin_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）

附 `leesin_native.png` + `leesin_native_dead.png` + `leesin_pose_dead.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Lee Sin at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Lee Sin rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall without the braid, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. The head stays the same size in every frame, with the red blindfold band across the eyes. Keep the braid a 1-square dark line with its gold ring, staying inside its cell. The same camera as the FIRST image.
Animation: DEATH, 7 frames, as in the SECOND image: 1 standing, struck; 2 thrown backward into the air; 3 flying backward, almost horizontal; 4 tumbling backward, legs up; 5 landing on his back; 6-7 lying still on his back, knees up. He lies on the ground line in frames 5-7, exactly as high as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x72 squares (512x576 px), image 2048x1152; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 技能特效（9 张）

9 张特效的提示词都以同一段画风和配色开头。

### 11. `leesin_fx_hit.png`：普攻命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12).
Effect: a PUNCH hit, 5 frames: 1 a small white flash; 2 a burst of short golden rays with a thin golden ring; 3 the ring widens and sparks fly out; 4 the sparks shrink; 5 the last sparks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the burst at most 40% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `leesin_fx_q_wave.png`：Q 天音波（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12).
Effect: SONIC WAVE in flight, 4 frames, seamless loop: a wave of sound energy flying to the RIGHT - a bright, thick curved crescent of golden light with a white core (its convex side facing right, like the front of a ripple), two thinner concentric crescents trailing behind it (to the left) and a few sparks; the crescents pulse and the trailing ones flicker from frame to frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 1024x128; the front crescent at the same spot near the right side of every cell, the crescent about 70% of the cell height, the whole wave about 70% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `leesin_fx_q_mark.png`：Q 音波印记（敌人身上），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12).
Effect: SONIC WAVE mark on an enemy, 6 frames: 1 a golden spark appears at the center; 2 it opens into a glowing golden circle with a bright dot in the middle; 3-5 rings of sound ripple outward from it and fade while new ones start, with tiny sparks (frames 2-5 form a seamless loop); 6 the mark fades.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the mark centered in every cell, the largest ring at most 50% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `leesin_fx_q2_hit.png`：Q 回音击命中，6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12).
Effect: RESONATING STRIKE impact, 6 frames: 1 a bright white flash; 2 a big star-shaped burst of golden light with a thick shock ring; 3 the ring expands and breaks into curved sound-wave arcs flying outward; 4-5 arcs and sparks spreading and fading; 6 the last sparks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact point at the center of every cell, the burst at most 80% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `leesin_fx_e_wave.png`：E 天雷破震波（地面），7 帧

原版的地面范围特效是正圆或略扁的圆（宽高比约 1–1.35），这张也照这个比例画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12) plus dusty browns for debris (#C9A27A, #8A6A4A).
Effect: TEMPEST, a shockwave along the ground, 7 frames, seen from the same slightly top-down game camera: 1 a small blinding flash on the ground at the center with short cracks; 2 a golden shock ring bursts out along the ground - a slightly flattened circle about 1.3 times wider than tall - with chunks of dust and small rocks thrown up; 3-4 the ring expands until it fills 90% of the cell width, orange-gold energy with a white rim, dust rising along it; 5-6 the ring fades into drifting dust and sparks; 7 the last dust.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the center of the ring at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `leesin_fx_shield.png`：W 金钟罩护盾（套在自己和友方身上），8 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A).
Effect: SAFEGUARD, a golden shield on a fighter, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person, and keep the inside of the shield empty and transparent. 1 golden sparks gather around the space; 2 a glowing golden oval shield outline appears around the whole space, with a brighter band of light around its middle like a monk's prayer ring; 3-6 the shield shimmers: short white highlight arcs slide along its outline, a few sparks drift up (frames 3-6 form a seamless loop); 7 the shield breaks into golden flakes; 8 the last flakes fade.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the shield about 75% of the cell height and 50% of the cell width, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `leesin_fx_r_kick.png`：R 猛龙摆尾踢中，7 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12).
Effect: DRAGON'S RAGE kick impact, 7 frames: 1 a blinding white-gold flash at the center; 2 the head of a golden Chinese dragon bursts out of the flash toward the RIGHT, jaws open, made of golden flame (orange-gold with a white core, flame wisps for its mane); 3 the dragon head roars at full size, a shock ring behind it; 4 it rushes further right and begins to dissolve into flames; 5-6 flames and sparks scatter; 7 the last embers.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the flash at the center of every cell, the dragon head reaching at most the right edge of its cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 18. `leesin_fx_r_dragon.png`：R 金龙（追着被踢飞的敌人飞），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A, #B83A12).
Effect: a golden DRAGON spirit rushing forward, 4 frames, seamless loop: a serpentine Chinese dragon made of golden fire flying to the RIGHT - its head at the right end of the cell with open jaws and swept-back whiskers, its body a wavy trail of golden flame thinning out to the left, embers along it; the body waves a little further every frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 2048x256; the dragon's head at the same spot near the right side of every cell, the whole dragon about 90% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 19. `leesin_fx_knockup.png`：R 撞击击飞，6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden chi color ramp (#FFFFFF, #FFF3C4, #FFD452, #FFA526, #F06A1A) plus dusty browns (#C9A27A, #8A6A4A).
Effect: KNOCK-UP impact on an enemy hit by a flying body, 6 frames: 1 a small white impact flash at the center; 2 a burst of dust and small golden sparks with a short upward swoosh of golden light; 3-4 the dust puffs outward and the swoosh rises; 5-6 the dust fades.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact point at the center of every cell, the effect at most 60% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧时长已写进 `native/leesin_cells.json`，出手帧对齐数据里的出手时刻；导入时按画面再微调。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `leesin_idle.png` | 6 | `idle` | 130/100/130/170/130/70（0.73 秒一次下沉，原版约 0.75 秒弹一次） |
| `leesin_run.png` | 8 | `run` | 8 × 192（原版 `Run_Base` 1.53 秒两步） |
| `leesin_attack.png` | 6 | `attack` | 60/60/70/80/50/40，第 4 帧出拳（tick 12） |
| `leesin_skill.png` | 7 | `skill`（Q1） | 60/70/80/60/90/180/170，第 5 帧出掌放音波（tick 16） |
| `leesin_q2.png` | 7 | `q2`（回音击冲刺时 `CasterAnimation`，31 tick） | 60/60/70/90/80/80/80 |
| `leesin_skill2.png` | 7 | `skill2`（E + W） | 80/100/110/120/100/80/80，第 4 帧捶地（tick 17） |
| `leesin_ult.png` | 8 | `ult`（R） | 70/70/70/80/130/100/100/100，第 5 帧踢中（tick 18） |
| `leesin_hit.png` | 2 | `hit` | 120/120 |
| `leesin_dead.png` | 7 | `dead` | 100/100/100/120/120/200/400 |
| `leesin_fx_hit.png` | 5 | 特效 `league_leesin_hit` | 5 × 60 |
| `leesin_fx_q_wave.png` | 4 | 飞行道具 `league_leesin_q_wave` | 4 × 60 循环 |
| `leesin_fx_q_mark.png` | 6 | 特效 `league_leesin_q_mark`（跟随目标，命中到李青冲到之间） | 1、2–5、6 |
| `leesin_fx_q2_hit.png` | 6 | 特效 `league_leesin_q2_hit` | 6 × 70 |
| `leesin_fx_e_wave.png` | 7 | 特效 `league_leesin_e_wave`（地面，半径 32 px） | 7 × 70 |
| `leesin_fx_shield.png` | 8 | 特效 `league_leesin_shield`（跟随，护盾 2 秒） | 1–2、3–6 两遍、7–8 |
| `leesin_fx_r_kick.png` | 7 | 特效 `league_leesin_r_kick`（踢中的位置） | 7 × 70 |
| `leesin_fx_r_dragon.png` | 4 | 飞行道具 `league_leesin_r_dragon`（跟在被踢飞的敌人后面） | 4 × 70 循环 |
| `leesin_fx_knockup.png` | 6 | 特效 `league_leesin_knockup`（被撞到的敌人） | 6 × 70 |

`leesin_native.png` 只用来保持造型一致，不进游戏。

## 姿势参考：英雄联盟原版动作

**客户端动画图**（`animations/skin0.bin`）：
- 待机 `Idle1` 依次播 `Idle_Active`、`Idle_Passive`。团战里一直在打，用战斗架势 `Idle_Active`。
- 移动 `Run` 在普通速度下播 `Run_Base`，加速时是同一个文件（`Run_Haste`）。
- 普攻 `Attack1`–`Attack4`，暴击用 `Attack4`。
- Q 一段 `Spell1_cast`；二段 `Spell1B` = `Spell1_B` + `Spell1_B_Loop`。
- E `Spell3_Cast`；R `Spell4A`，之后接 `Spell4_toIdle`。
- 死亡 `Death`。

**测量结果**：
- **跑步是跑，不是走**：`Run_Base` 1.53 秒两步，每步约 0.4 秒双脚离地，大步腾跃、上身前倾。
- **待机**：约每 0.75 秒下沉弹跳一次，每次深浅不一（3.2、1.6、2.3、1.8 px）。所以只取第一次弹跳做成 0.73 秒的循环，最后一帧和第一帧各半混合，辫子也能接上。
- **出手时刻**：Q1 约 320–370 ms 推掌；E 约 330 ms 捶地；R 约 300 ms 回旋踢伸直。普攻用 `Attack3`（弓步冲拳），约 333 ms 出拳。

**渲染设置**：
- **镜头**：李青和盖伦、拉克丝一样，胸口朝向自己的右侧，所以加 `--mirror`（从另一侧渲染再翻转），全部动作同一侧。
- **辫子**：李青的长辫子挂在头部骨骼下面。`--head 2.0` 会把辫子也放大一倍，拖到地上。`pose_ref.py` 为此加了 `--hair`：0.5 抵消头部放大，辫子保持原版长度。
- **格子**：飞踢时辫子水平拖在身后，大招跃起时辫子高过头顶，所以格子是 64×72 方块（拉克丝、艾希是 56×64）。
- **转身帧**：弯腰和转身的几帧看得到后背。E 捶地前后、R 踢中的几帧把人朝镜头转 15–30 度（`turn`），镜头不动。动画里常这样处理，保证正面朝向观众。
- **死亡**：原版死亡开头身体在单位前方 140 单位，击飞距离按第一帧算（保留 65%）。每帧的最低点按离地高度贴在脚底线上，否则斜躺在不同深度的身体会浮起或陷下去。
- **受击**：原版没有受击动作，用待机和死亡 200 ms（身体后仰）按 0.3、0.12 混合。

帧的清单在 [`poses.json`](poses.json)，锚点表在 [`../native/leesin_cells.json`](../native/leesin_cells.json)。重新生成：

```bash
python tools/lol/native_pose.py assets/source/leesin/poses.json --out <文件夹>
python tools/art/native_refs.py --out <文件夹> --style --pack lux --pack ashe
```

第二条写出 `tfm2_style_ref_martial.png` 和 `pack_native_ref.png`。原版英雄对照图从游戏的 `bundle.game_data` 读取，只在本地用。

三视图 `leesin_model_chibi.png`：待机第 0 帧 `Idle_Active@0`，`--yaw 40`、`100`、`200` 各渲染一张，横向拼接：

```bash
python tools/lol/pose_ref.py --champ LeeSin --hq --head 2.0 --legs 0.8 --hair 0.5 --mirror --yaw 40 --pitch 10 --size 800 --width 0.75 --fit 0.8 --ground 0.92 --bg 225,225,225 --no-labels --out <文件夹> --name view_40 --frame Idle_Active@0
```

## 结果（2026-09-26 导入）

**生成**：Codex 一共交了 19 张主图，交接记录在 [`codex/`](codex/)（交接说明、逐帧记录、对接表、色板、实际提交的提示词）。
- 先交原尺寸造型图（第二版通过：16 色，头顶到脚底 34 格，两行红蒙眼布，不画眼睛）。
- 确认后同一批画 9 张动作和 9 张特效。动作整批重画过一次，天雷破、护盾两张特效也重画过。
- 全部整理成严格的 8×8 纯色块。
- 待机是 Codex 用确认过的造型图分层重组的：同一个头，脚固定，上半身按 0/2/2/1/0/0 px 起伏。

**问题：除了待机，动作都画大了**：
- 跑步、普攻、Q1、E、R、受击的头约是造型图的 1.4 倍（蒙眼布 7–10 格长、3 行厚，造型图 6 格、2 行）；
- 死亡约 1.35 倍；Q2 飞踢帧大小正确，落地两帧约 1.18 倍；
- 跳跃也不够高，R 和 Q2 的腾空帧贴近地面。

参考图里大小和位置都是对的，GPT 照着姿势画了，但个头放大了。直接导入的话，李青一出招就会变大。

**修正**（`tools/art/fit_native.py`，不再生图）：
1. **缩放**：每张动作按头的大小缩回造型图的比例，比例是和待机并排目测定的：跑步、普攻、Q1 1.4；E 1.34；R、受击 1.38；死亡 1.35；Q2 飞踢 1.0、落地 1.18。缩小时每个像素取覆盖面积最大的颜色（按 16 色投票，描边、蒙眼布、金色加权），仍是纯色像素。
2. **对位**：每帧的蒙眼布中心对到参考图里原版头部骨骼的位置（`leesin_cells.json` 的 `head`，偏移量用待机第 1 帧校准）。参考图里着地的帧，脚底压回地面线。跑步的蒙眼布锁在同一列。
3. **缩放后的大小**：按身体面积和参考轮廓比，各动作和待机相差大多在 ±5% 以内。

**导入**（`import_native.py`）：
- 58 帧，16 色，和右边像素同色的比例 37%（原版英雄 18%–46%）；
- 待机 6 帧的头在同一列：参考图第 3、4 帧的锚点差 1 px，已对齐；
- 找待机的头时从光头头顶开始，跳过竖起的辫子（只对李青这样做，拉克丝、艾希的导入结果逐像素不变）；
- 头像截取点 (0, −34)。

**特效**（`tools/art/import_leesin.py`）：每个 8×8 方块读成一个像素。
- 天雷破震波、金钟罩护盾放大 2 倍：震波圈约 56 px 宽，覆盖 32000 的半径；护盾约 48 px 高，包住人；
- 其余 1 倍：命中、印记、回音击、踢击放在胸口，震波圈中心在脚底线，音波和金龙按弹头定位；
- 印记第 2–5 帧放两遍（约 0.6 秒，覆盖到回音击落地）；护盾第 3–6 帧放三遍（共 2 秒）。

**检查**：`lint_mod.py` 0 错误 0 警告；`tfm2_ase.py metrics` 高 42 px（含辫子，头顶到脚底 34 px），没有半透明像素，描边覆盖 76%（拉克丝 85%、艾希 63%）。

**待进游戏确认**：Q 命中后的自动飞踢、R 的击退方向，以及金龙会不会追上被踢飞的目标。
