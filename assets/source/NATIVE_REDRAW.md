# 拉克丝 + 艾希：按游戏原尺寸重画（给 GPT 的生图提示词）

一共 19 张：拉克丝 1 张造型图 + 8 张动作，艾希 1 张造型图 + 9 张动作。特效图不变，盖伦不变。
生成的 PNG 放进一个文件夹交给 Claude。Claude 按 8×8 的方块逐格取色，放回现在每一帧的位置，接回游戏（`tools/art/import_native.py`）。已完成，结果见文末「导入」和「结果」。

## 为什么要重画

游戏里拉克丝和艾希看起来是一片糊的碎色点，盖伦没有这个问题。

| | 原版英雄（15 个） | 盖伦 | 艾希 / 拉克丝 |
|---|---|---|---|
| 颜色数（待机第 1 帧） | 16–33 | 63 | 42 / 41 |
| 和右边像素同色的比例 | 18%–46%，中位 32% | 15% | 15% / 18% |
| 看起来 | 大块平涂，干净 | 大块造型，看得清 | 碎色点，看不清 |

原因在分辨率。上一轮 GPT 画的像素画，角色约 100 个"像素块"高（盖伦 100、艾希 106、拉克丝 102）。游戏里只有 34–36 px，导入时要把大约 3 个块并成 1 个像素。

- 盖伦本身是大块的铠甲、大剑，压缩后还能认出来。
- 艾希、拉克丝身材细，身上有很多发丝、饰边、宝石、细弓、细杖。压缩后这些细节成了一粒粒杂色。

只改导入方法试过了：减到 24 色、再去掉孤立杂点，只干净一点点，身体仍然是碎块。所以要让 GPT 直接按游戏尺寸画：34 像素高，每个像素是一个 8×8 的方块，大面积平涂、颜色少，小装饰按这个尺寸简化，和原版英雄一样。

## 这一轮的做法

1. 参考图直接用我们现在游戏里的精灵，放大 8 倍（`lux_now_*.png`、`ashe_now_*.png`，每个像素是 8×8 的方块）。
   - 姿势、大小、每帧在格子里的位置都已经对了，GPT 只需要按同样的格子把它画干净。
   - Claude 导入时把每帧放回现在的位置，已经调好的对齐（头部轨迹、前冲距离、R 的法杖高度、死亡击飞）全部沿用。
2. 附原版英雄 8 倍对照图（`tfm2_style_ref_mage.png` 给拉克丝、`tfm2_style_ref.png` 给艾希）。方块大小和我们要的一样，看得出原版有多"干净"。
3. 先单独生成两张造型图，检查通过后，再同一批生成全部动作。

## 生成顺序（重要）

1. **先只生成两张造型图**：`lux_native.png`（第 1 条）和 `ashe_native.png`（第 10 条），各附三张图（见提示词）。
2. 检查这两张（放大看方块）：
   - 角色正好约 34 个方块高（272 px）；
   - 所有方块都是 8×8、对齐同一个网格，没有半个方块、没有模糊边；
   - 颜色不超过 20 种，没有杂色点，大块平涂；
   - 两只眼睛清楚（每只约 2×2 个方块），刘海在眼睛上方；
   - 法杖 / 弓是一条干净的线；
   - 服装配色和第三张附图一致。

   **不对就重画这一张，不要带着错的造型图往下做。**
3. 17 张动作图**同一批**生成，每张附两张图：第一张是该英雄的新造型图，第二张是对应的 `*_now_*.png`（现在的游戏精灵，8 倍）。
4. 输出排版和第二张附图完全一样：几列几行、每格多大、每帧在第几格。

## 附图（压缩包里有；原版英雄对照图从游戏里读取，只在本地用，不提交到仓库）

| 文件 | 内容 | 用在 |
|---|---|---|
| `lux_now_design.png`、`ashe_now_design.png` | 现在游戏里的待机第 1 帧，放大 8 倍（128×128 画布 = 1024×1024） | 造型图 |
| `tfm2_style_ref_mage.png`、`tfm2_style_ref.png` | 原版英雄（法系 / 弓手、骑士等），上排待机、下排攻击，放大 8 倍 | 造型图 |
| `lux_ref.png`、`ashe_ref_chibi.png` | 上一轮的高清造型图（服装、配色、法杖 / 弓以它为准） | 造型图 |
| `lux_now_<动作>.png`、`ashe_now_<动作>.png` | 现在游戏里的每个动作，放大 8 倍，按格子排好 | 各自的动作图 |

## 所有图的规则

- **像素尺寸（最重要）**：角色是游戏里 34 像素高的精灵，按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **干净，不要细节**：整个精灵最多 20 种颜色；每种材质 2–3 个平涂色阶（亮、中、暗），大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；轮廓 1 个方块宽的近黑色描边，内部深色线条越少越好。
- **只保留这个尺寸看得出来的东西**，小装饰合并或去掉（每个英雄的清单写在提示词里）。
- **脸要看得清**：头约占身高 1/3；脸的肤色区约 6–7 个方块宽；每只眼睛约 2×2 个方块（上面一格深色眼皮，下面白色和一格彩色虹膜）；嘴 1 个方块或不画；刘海在眼睛上方。
- 3/4 正面朝右，看得到脸和胸口，不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 如果模型不肯画带名字的角色，把 "Lux" / "Ashe" / "League of Legends" 删掉，只保留外观描述。

---

## 拉克丝（9 张）

### 1. `lux_native.png`：造型图（附 `lux_now_design.png`、`tfm2_style_ref_mage.png`、`lux_ref.png`）

```text
Three attached images. FIRST: our game's current in-game sprite of Lux, shown at 8x - every game pixel is an 8x8 block. Its size and pose are right, but at game size it looks noisy and blurry: too many colors, stray single pixels, details too small to read. SECOND: official heroes of the game Teamfight Manager 2, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, bold readable faces. THIRD: the high-resolution design of Lux for this pack - use it only for her costume, colors and wand, not for the level of detail.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall (hair top to soles), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow.
Lux from League of Legends (default skin), chibi: honey-blonde hair to her shoulders with a dark brown hairband, big blue eyes, fair skin; royal-blue bodysuit and leggings; a grey breastplate; small white shoulder caps; white gloves; a gold belt; a short white skirt; grey armored boots; a long slender wand held in the hand on the right side of the image.
Pixel rules (most important): at most 20 colors in total; every material 2-3 flat shades (light, base, shadow); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Keep only details that read at this size: the hairband as a 1-square dark line; hair in 3 flat shades with a few big highlight squares; the breastplate 2 grey shades with one gold line under it; the two red collar gems as single red squares; shoulder caps 2-3 white squares each; gloves 2 white squares; the gold belt 1 square tall; the skirt 2 white shades with a 1-square gold hem; boots 2 grey shades; the wand a 1-square dark line with a few gold squares and a 3x3 glowing gold-white finial at the upper end, a 2x2 gold finial at the lower end. Drop every other trim and pattern.
Face: the head is one third of her height; the skin area about 6-7 squares wide; each eye about 2x2 squares (a dark lid square on top, below it a white square and a blue square); no mouth or a single square; the bangs stay above the eyes.
Pose, size and place: exactly as in the FIRST image - the same idle stance, the same height (34 squares = 272 px), feet on the same line 28 squares (224 px) above the bottom of the image, the character horizontally centered. 3/4 FRONT view facing right: we see her face and chest.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: she is 34 squares tall, all squares 8x8 on one grid, at most 20 colors, both eyes clearly visible, the wand a clean line.
```

8 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

### 2. `lux_idle.png`：待机，6 帧，3 列 × 2 行（附 `lux_native.png` + `lux_now_idle.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the bangs above the eyes, the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: IDLE, 6 frames, as in the SECOND image: she stands relaxed, the wand held low and diagonally across the front of her legs; only subtle breathing (1 square) between frames.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1344x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 3. `lux_run.png`：跑步，8 帧，4 列 × 2 行（附 `lux_native.png` + `lux_now_run.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the bangs above the eyes, the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: RUN loop, 8 frames, as in the SECOND image: a bouncy run, both feet off the ground in frames 1, 4, 5 and 8; the wand swings with her arm - trailing behind her in frames 1-3, upright at her side in frames 4-8.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place, feet (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 4. `lux_attack.png`：普攻，6 帧，3 列 × 2 行（附 `lux_native.png` + `lux_now_attack.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the bangs above the eyes, the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: BASIC ATTACK, 6 frames, as in the SECOND image: she swings the wand back, twists, thrusts it straight forward in frame 4 (a small 2x2 white-gold flash at the tip), follows through and returns to idle.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1344x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 5. `lux_skill.png`：Q「光之束缚」，7 帧，4 列 × 2 行（最后一格空）（附 `lux_native.png` + `lux_now_skill.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the bangs above the eyes, the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: LIGHT BINDING, 7 frames, as in the SECOND image: she raises the wand, holds it upright with a small glowing ball at the tip in frame 3, thrusts it forward with a white-gold flash at the tip in frame 4, leans forward, then returns to idle. Draw the glow and flash as solid blocky shapes in 3 shades (white, pale gold, gold), no soft glow.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 6. `lux_skill2.png`：E「透光奇点」，7 帧，4 列 × 2 行（最后一格空）（附 `lux_native.png` + `lux_now_skill2.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the bangs above the eyes, the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: LUCENT SINGULARITY, 7 frames, as in the SECOND image: a big swing of the wand - wind-up, sidearm swing, the wand whipping forward with a small white-gold flash at the tip in frame 5, held upright in front of her in frame 6, back to idle.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 7. `lux_ult.png`：R「终极闪光」，8 帧，4 列 × 2 行（附 `lux_native.png` + `lux_now_ult.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the bangs above the eyes, the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: FINAL SPARK, 8 frames, as in the SECOND image: a crouch, a leap, then she floats in the air with her arms spread while the wand hovers level in front of her at the height of her knees - the wand is SEPARATE from her hands in frames 2-7 and stays exactly where it is in the SECOND image; the wand's tip blazes in frame 5 (a round blocky flash in white, pale gold and gold), recoil, a tuck in the air (frame 7, the only frame where her face may be hidden), landing with the wand upright in frame 8.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place and the same height above the cell's ground line (10 squares above the bottom of the cell) - she is in the air in frames 2-7. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 8. `lux_hit.png`：受击，2 帧，2 列 × 1 行（附 `lux_native.png` + `lux_now_hit.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image (in frame 1 her eyes are squeezed shut: two short dark lines), the head the same size in every frame. Keep the wand a clean 1-square line with its gold finials. 3/4 FRONT view facing right, never her back.
Animation: HIT, 2 frames, as in the SECOND image: 1 she flinches from a blow, upper body jolted back; 2 recovering toward idle.
Layout: exactly like the SECOND image - a grid of 2 columns x 1 row of cells, each cell 56x64 squares (448x512 px), image 896x512; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 9. `lux_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）（附 `lux_native.png` + `lux_now_dead.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Lux at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Lux at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall when standing, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. The head stays the same size in every frame (her eyes are closed from frame 2: short dark lines). Keep the wand a clean 1-square line with its gold finials. The same camera as the FIRST image.
Animation: DEATH, 7 frames, as in the SECOND image: struck, thrown backward, falling, landing on her back, rolling to her side, lying still with the wand beside her.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place and height - she lies on the ground line 10 squares above the bottom of the cell in frames 5-7. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 艾希（10 张）

### 10. `ashe_native.png`：造型图（附 `ashe_now_design.png`、`tfm2_style_ref.png`、`ashe_ref_chibi.png`）

```text
Three attached images. FIRST: our game's current in-game sprite of Ashe, shown at 8x - every game pixel is an 8x8 block. Its size and pose are right, but at game size it looks noisy and blurry: too many colors, stray single pixels, details too small to read. SECOND: official heroes of the game Teamfight Manager 2, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, bold readable faces (see how the archers draw a bow as a clean line). THIRD: the high-resolution design of Ashe for this pack - use it only for her costume, colors and bow, not for the level of detail.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall (hood tip to soles), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow.
Ashe from League of Legends (default skin), chibi: a black pointed hood with gold trim; silver-white hair with a faint lavender tint; pale skin and ice-blue eyes; gold pauldrons; a black top and short black skirt with gold trim; black boots with gold greaves; a black cape with a gold border behind her; a large ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image), an ice-blue arrow nocked.
Pixel rules (most important): at most 20 colors in total; every material 2-3 flat shades (light, base, shadow); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Keep only details that read at this size: the hood 2 black shades with a 1-square gold edge around the face; the hair 2-3 silver-lavender shades framing the face; the pauldrons 2 gold shades; the top and skirt flat black with at most two gold stripes; boots black with a gold greave block; the cape a flat black shape with a 1-square gold border; the bow a clean 1-square line in 2 ice-blue shades with 2-3 small crystal points, the string a 1-square pale line, the arrow a 1-square pale-blue line. Drop every other trim and pattern.
Face: the head is one third of her height; the hood frames the face without shading it; the skin area about 6-7 squares wide; each eye about 2x2 squares (a dark lid square on top, below it a white square and an ice-blue square); the bangs stay above the eyes.
Pose, size and place: exactly as in the FIRST image - the same idle stance, the same height (34 squares = 272 px), feet on the same line 28 squares (224 px) above the bottom of the image, the character horizontally centered. 3/4 FRONT view facing right: we see her face and chest.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: she is 34 squares tall, all squares 8x8 on one grid, at most 20 colors, both eyes clearly visible, the bow a clean line.
```

艾希 9 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

### 11. `ashe_idle.png`：待机，6 帧，3 列 × 2 行（附 `ashe_native.png` + `ashe_now_idle.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: IDLE, 6 frames, as in the SECOND image: she stands with the bow held low across her body, the arrow nocked and pointing down; only subtle breathing (1 square) between frames.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1344x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 12. `ashe_run.png`：跑步，8 帧，4 列 × 2 行（附 `ashe_native.png` + `ashe_now_run.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: RUN loop, 8 frames, as in the SECOND image: a springy run with the bow held level in front of her chest pointing forward, the cape streaming behind; the airborne frames stay as high as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place, feet (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 13. `ashe_attack.png`：普攻，6 帧，3 列 × 2 行（附 `ashe_native.png` + `ashe_now_attack.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: BOW SHOT, 6 frames, as in the SECOND image: she raises the bow upright, draws to full, releases (the string snaps, her hand flies back), follows through and lowers the bow toward idle. Do not draw the flying arrow.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1344x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 14. `ashe_q_attack.png`：Q 连射，6 帧，3 列 × 2 行（附 `ashe_native.png` + `ashe_now_q_attack.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: RANGER'S FOCUS FLURRY, 6 frames, as in the SECOND image: a wide low stance, the bow turned flat at chest height, rapid releases with her hand jerking back, then rising toward idle. Do not draw the flying arrows.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1344x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 15. `ashe_skill.png`：Q 发动，6 帧，3 列 × 2 行（附 `ashe_native.png` + `ashe_now_skill.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: RANGER'S FOCUS activation, 6 frames, as in the SECOND image: she swings the bow up and over until it lies flat at shoulder height, drops into the wide focus stance with the bow flaring ice-blue (a few blocky frost sparkles, no soft glow), then rises toward idle.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1344x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 16. `ashe_skill2.png`：W 万箭齐发，7 帧，4 列 × 2 行（最后一格空）（附 `ashe_native.png` + `ashe_now_skill2.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: VOLLEY, 7 frames, as in the SECOND image: she turns the bow flat at chest height, draws a fan of arrows, releases (her hand flies back), follows through and lowers the bow toward idle. Do not draw the flying arrows.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 17. `ashe_ult.png`：R 魔法水晶箭，8 帧，4 列 × 2 行（附 `ashe_native.png` + `ashe_now_ult.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image: each eye about 2x2 squares, the hood and bangs never covering the eyes, the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: ENCHANTED CRYSTAL ARROW, 8 frames, as in the SECOND image: the bow raised upright, a full draw with a big crystal arrow glowing white-blue at the arrowhead (a blocky shape in 3 shades, no soft glow), the release with a blocky white-blue flash at the bow, follow-through, lowering the bow toward idle. Draw only the glow at the bow, not the flying arrow.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 18. `ashe_hit.png`：受击，2 帧，2 列 × 1 行（附 `ashe_native.png` + `ashe_now_hit.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep her face as in the FIRST image (in frame 1 her eyes are squeezed shut: two short dark lines), the head the same size in every frame. Keep the bow a clean 1-square ice-blue line held in the hand on the right side of the image. 3/4 FRONT view facing right, never her back.
Animation: HIT, 2 frames, as in the SECOND image: 1 she flinches from a blow, upper body jolted back; 2 recovering toward idle.
Layout: exactly like the SECOND image - a grid of 2 columns x 1 row of cells, each cell 56x64 squares (448x512 px), image 896x512; frame N in the same cell as in the SECOND image, at the same place, feet on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 19. `ashe_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）（附 `ashe_native.png` + `ashe_now_dead.png`）

```text
Two attached images. FIRST: the approved clean pixel-art design of Ashe at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: our current in-game animation of Ashe at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its noisy pixels.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: she is 34 pixels tall when standing, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. The head stays the same size in every frame. Keep the bow a clean 1-square ice-blue line. The same camera as the FIRST image.
Animation: DEATH, 7 frames, as in the SECOND image: she staggers back, falls backward through the air, lands on her back, lying still with the bow by her feet.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 56x64 squares (448x512 px), image 1792x1024; frame N in the same cell as in the SECOND image, at the same place and height - she is in the air in frames 4-5 and lies on the ground line 10 squares above the bottom of the cell at the end. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 导入

交回的 19 张图在 [`native/`](native/)，同一个文件夹里还有：
- Codex 的交接说明 `HANDOFF.md`；
- 逐帧记录 `MANIFEST.json`（文件哈希、每帧参考框）；
- 实际用的提示词 `PROMPTS.md`；
- 离线预览 `preview.html`。

GPT 直接出的图不在严格网格上：方块约 7.4–8.6 px，脸会变窄。Codex 做了整理：
- 每个像素是严格对齐的 8×8 纯色块，透明度只有全透明和不透明；
- 每帧的头换成验收过的造型图头部；
- 法杖和弓的线条校直。

```bash
python tools/art/import_lux.py            # 特效（角色图只在加 --body 时写第一轮的版本）
python tools/art/import_ashe.py
python tools/art/import_native.py         # 角色图：拉克丝和艾希
```

- **取色**：每个 8×8 方块读成一个游戏像素。不缩放，不重新配色，也不补描边：弓和法杖是 1 格宽的彩色线，和原版弓手的弓一样不描黑边。
- **位置**：`native_refs.py` 出参考图时记下了每帧锚点在格子里的位置和帧时长（`native/<英雄>_cells.json`）。新图画在同样的格子里，按同一个锚点切出来，就站在第一轮那一帧的位置上。头部轨迹、前冲、R 的法杖高度、死亡击飞都不变。
- **两处修正**（循环动作里 1 个像素的抖动都看得出来）：
  - 待机、跑步：每帧左右挪动，让头停在这组动作的平均位置（用待机第 1 帧的头逐像素找）。Codex 按包围框摆帧，结果拉克丝待机第 5 帧、艾希待机第 1 帧整体偏了 1 像素，艾希跑步的头来回跳 2 像素。修正后每帧最多挪 1 像素，脚仍贴地。
  - 拉克丝待机的呼吸原来是"低低低高低高"：贴头时 9.04 被四舍五入到了低位。第 5、6 帧对调，变成"低低低高高低"。
- 头像截取点重新量过：拉克丝 (1, −31)，艾希 (0, −33)。

## 结果

| | 原版英雄（15 个） | 第一轮 艾希 / 拉克丝 | 原生重画 艾希 / 拉克丝 |
|---|---|---|---|
| 颜色数（待机第 1 帧） | 16–33 | 42 / 41 | 18 / 18 |
| 颜色数（整套角色图） | | | 18 / 19 |
| 和右边像素同色的比例（待机第 1 帧） | 18%–46%，中位 32% | 15% / 18% | 31% / 29% |

前后对比（1 倍是游戏里的大小）：[`docs/preview/native_before_after.png`](../../docs/preview/native_before_after.png)。
`lint_mod.py` 0 错误 0 警告，`tfm2_ase.py metrics` 身高 34 px、没有半透明像素。

参考图用 `python tools/art/native_refs.py --out <文件夹> --hero lux --hero ashe --style` 重新生成（原版英雄对照图从游戏的 `bundle.game_data` 读取），同时写出 `<英雄>_cells.json`，要和重画的图一起提交。
