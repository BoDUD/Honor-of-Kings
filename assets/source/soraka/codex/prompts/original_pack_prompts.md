# 索拉卡：给 GPT 的生图提示词（直接按游戏原尺寸画）

一共 18 张图：
- 1 张原尺寸造型图；
- 8 张原尺寸动作图；
- 9 张特效图。

生成的 PNG 和 Codex 的交接说明放进一个文件夹，然后告诉 Claude。Claude 按 8×8 方块逐格读色，放回每帧的锚点，接到技能上（`tools/art/import_native.py`）。

走李青验证过的路线：直接按原尺寸画，不先画高清动作条。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 法杖射出星光弹 | `soraka_attack` · `soraka_fx_bolt` · `soraka_fx_hit` |
| 技能 1 | Q「流星坠落」：星星砸向目标位置，伤害并减速；命中敌方英雄时「活力焕发」回血加速。合并 E「星体结界」：每 16 秒最多一次，落点留下结界，沉默圈内敌人，1.5 秒后定身 | `soraka_skill` · `soraka_fx_q_star` · `soraka_fx_rejuv` · `soraka_fx_e_field` · `soraka_fx_e_bind` |
| 技能 2 | W「星之灌注」：扣自己的血治疗一名其他友方英雄；合并被动「拯救」：放完后加移速 | `soraka_skill2` · `soraka_fx_w_heal` |
| 大招 | R「祈愿」：治疗全图所有友方英雄 | `soraka_ult` · `soraka_fx_r_cast` · `soraka_fx_r_heal` |
| 其他 | 待机、跑步、受击、死亡 | `soraka_idle` · `soraka_run` · `soraka_hit` · `soraka_dead` |

## 这一轮的做法

1. **原尺寸姿势参考**：`tools/lol/native_pose.py` 把英雄联盟客户端里索拉卡的真实动作，直接渲染成游戏尺寸。
   - Q 版比例：头 2 倍、腿 0.8 倍。头从头顶到下巴约 11 px，占身高 1/3。
   - 长马尾挂在胸部骨骼下，不随头放大，保持原长。
   - 角：模型里角是头部网格的一部分，放大 2 倍后比头顶高出近半个头。渲染时把角的顶点绑到 `horn` 骨骼上，用 hair 参数保持原长（`"keep": {"horn": 4.0}`）。
   - 待机时头顶到蹄底 34 px（不算角尖），每个游戏像素取 8×8 方块的平均色，放大 8 倍显示（`soraka_native_*.png`）。
   - 姿势、大小、每帧在格子里的位置都已经算好：前冲保留原版的 70%，死亡保留 65%。
2. **高清对照**：同一批帧的高清渲染（`soraka_pose_*.png`），格子和位置完全一样。缩小图看不清姿势时看它。
3. **每帧锚点**：记在 `soraka_cells.json` 里。新图画在同样的格子里，按同一个锚点切出来，就站在参考图那一帧的位置上。

李青那一轮 GPT 把动作都画大了约 1.4 倍，导入前只能按头缩回（`tools/art/fit_native.py`）。所以这次的动作提示词里写明：**头和造型图一样大，按方块数一样**。

## 生成顺序（重要）

1. **先只生成造型图 `soraka_native.png`**（第 1 条），附四张图（见提示词）。
2. 检查造型图（放大看方块，也放到深色背景上看）：
   - 从头顶（白发）到蹄底正好约 34 个方块（272 px）；额头的角只高出头顶 1–2 格；
   - 所有方块都是 8×8、对齐同一个网格，没有半个方块、没有模糊边；
   - 颜色不超过 20 种，没有杂色点，大块平涂；
   - **脸**：头约占身高 1/3；两只黄色眼睛各 2×2 方块，清楚可见，白色刘海不遮眼；嘴 1 格；嘴鼻位置没有多余的深色竖线；缩到 1 倍一眼能认出"蓝脸、白发、额头一只角"；
   - **头的轮廓**：头顶和脸侧是弧形，不是一条直边。英雄卡片的背景接近黑色，描边看不见，只剩白发和蓝脸的色块轮廓；
   - 大尖耳：外侧蓝紫色，内侧红色；
   - 服装配色和 `soraka_model_chibi.png` 一致：黄色上衣，红色披风，棕色腰带和橙色宝石，身前一条橙红长布，腿上浅色绷带，黑色羊蹄；
   - **法杖**：细长的金棕色杖身，顶端一个大金色月牙，底端一个橙色圆球；杖身和手、脚之间有描边或颜色隔开，月牙、圆球不和头、脚粘成一团；
   - 3/4 正面朝右，看得到脸和胸口。

   **不对就重画这一张，不要带着错的造型图往下做。**
3. 8 张动作图**同一批**生成，每张附三张图：
   - 第一张：新造型图 `soraka_native.png`；
   - 第二张：对应的 `soraka_native_<动作>.png`（原尺寸姿势参考）；
   - 第三张：对应的 `soraka_pose_<动作>.png`（同一批帧的高清渲染）。
4. 输出排版和第二张附图完全一样：几列几行、每格多大（72×72 个方块）、每帧在第几格。
5. 9 张特效图不附图，可以和动作图同时生成。
6. **交给 Claude 之前请 Codex 整理**（和李青那批一样）：
   - 每个像素都是严格对齐的 8×8 纯色块，透明度只有全透明和不透明；
   - 全部角色图共用造型图的调色板，不超过 20 色，去掉孤立的杂色点；
   - **每一帧的头和造型图一样大**（按方块数一样），交付前逐张对比；
   - **待机 6 帧用同一个头**（从造型图取），只随身体上下移动，这样循环不会抖；起伏是"高、高、低、低、低、高"，每次只差 1 格；
   - 跑步 8 帧的头也保持同一列，不要左右跳 1–2 格；
   - 每帧留在它的格子里、画在哪就是哪，**不要按包围框重新居中**（锚点记在 `soraka_cells.json`）；
   - 附交接说明 `HANDOFF.md`、逐帧记录 `MANIFEST.json`（文件哈希、每帧的包围框、每帧头的大小）和实际用的提示词。
7. 以后要改造型，全部动作图用新造型图整批重画，不和旧批次混用。

## 附图（压缩包里有）

Riot 模型渲染和原版游戏截图只在本地用，不提交到仓库。

| 文件 | 内容 | 用在 |
|---|---|---|
| `soraka_native_design.png` | 原版待机第 0 帧，直接渲染成游戏尺寸（34 px），8 倍显示，128×128 方块画布 | 造型图 |
| `tfm2_style_ref_healer.png` | 团战经理 2 原版的白魔导士、牧师、德鲁伊、附魔师、结界法师、风法师（持杖的施法者），上排待机、下排攻击，8 倍 | 造型图 |
| `soraka_model_chibi.png` | 英雄联盟游戏内模型的正面、侧面、背面，Q 版比例（角保持原长） | 造型图 |
| `pack_native_ref.png` | 本包按原尺寸画的拉克丝、艾希、李青，8 倍 | 造型图 |
| `soraka_native_<动作>.png` | 原版动作渲染成游戏尺寸，8 倍，按格子排好 | 各自的动作图 |
| `soraka_pose_<动作>.png` | 同一批帧的高清渲染，格子和位置完全相同 | 各自的动作图 |
| `soraka_cells.json` | 每帧锚点在格子里的位置和帧时长（给 Codex 核对位置用） | 整理 |

## 所有角色图的规则

- **像素尺寸（最重要）**：
  - 角色是游戏里的小精灵，站着时从头顶（白发）到蹄底 34 像素高，角尖只多出 1–2 像素；
  - 按真正的低分辨率像素画来画，再整体放大 8 倍输出；
  - 每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格；
  - 没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **干净，不要细节**：
  - 整个精灵最多 20 种颜色，每种材质 2–3 个平涂色阶；
  - 不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；
  - 1 个方块宽的近黑色描边。
- **脸**：
  - 头约占身高 1/3，每一帧都和造型图一样大；
  - 蓝紫色皮肤 2–3 个色阶；两只眼睛各 2×2 方块，黄色虹膜加一格深色瞳孔；嘴 1 格；
  - 白色刘海盖住额头两侧，但不遮眼；嘴鼻附近不要画深色竖线。
- **头发、角、耳朵**：
  - 白发 2–3 个浅灰色阶；脑后一条粗马尾，用一个白色发团扎住，垂到小腿，随动作甩动；
  - 额头正中一只向上弯的金棕色角，约 3 格高、1 格宽；
  - 大尖耳朝两侧斜上，外侧蓝紫、内侧红色。
- **法杖**：
  - 细长杖身 1 格宽，金棕色；顶端大金色月牙（约 5×6 格），底端 2×2 橙色圆球；
  - 和手、脚、头之间有描边或颜色隔开，月牙和圆球不和身体粘成一团；
  - 按参考图的位置握杖，不能换到另一只手。
- **朝向**：3/4 正面朝右，看得到脸和胸口。转身、弯腰时也把脸和胸口转向观众，不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 角色图只画角色本身。星星、光、治疗闪光都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把 "Soraka" / "League of Legends" 删掉，只保留外观描述。

## 所有特效图的规则

- 没有黑描边。
- 颜色用索拉卡的星光：
  - 星光：白色核心 → 奶油黄 → 淡金 → 金 → 琥珀（`#FFFFFF`、`#FFF7D6`、`#FFE88A`、`#FFC940`、`#F29A2E`）；
  - 夜空（结界和祈愿的点缀）：`#E8F0FF`、`#A8C8FF`、`#6E8BF0`、`#6A4FC8`；
  - 治疗：`#F2FFE0`、`#BDF28A`、`#6FD06A`、`#2F9A52`。
- 飞行道具一律**朝右**画，游戏会按飞行方向旋转；命中类特效居中画。
- 套在人身上的特效：格子中间留出一个空的人形位置（人高约占格子 60%，脚在格子高度 88% 处），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。

---

## 角色（9 张）

### 1. `soraka_native.png`：造型图

附四张图：`soraka_native_design.png`、`tfm2_style_ref_healer.png`、`soraka_model_chibi.png`、`pack_native_ref.png`。

```text
Four attached images. FIRST: League of Legends' Soraka rendered at our game's exact sprite size and shown enlarged 8x - every game pixel is an 8x8 block. Its size, pose and place are right, but it is a blurry downscaled 3D render: too many colors, no outline, details that do not read. SECOND: official heroes of the game Teamfight Manager 2 (casters with staffs: a white-haired mage, a priestess, a druid, an enchantress...), top row idle, bottom row attacking, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, a 1-pixel dark outline, bold readable heads with clear eyes. THIRD: Soraka's in-game model with chibi proportions, front, side and back - use it for her costume, colors, horn, ears, hair and staff, not for the level of detail. FOURTH: three heroes of this pack drawn at this exact size - match their pixel size, outline and cleanliness.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall from the top of her white hair to the bottom of her hooves (the tip of her horn rises 1-2 pixels above that), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow.
Soraka from League of Legends (default skin), chibi: a gentle celestial healer with blue-violet skin and light blue swirl markings on her arms; white-silver hair with a fringe over her forehead and a long thick ponytail tied with a round white bun at the nape, hanging down her back to her calves; one curved golden-brown horn rising from the middle of her forehead; big pointed elf ears slanting up and out, blue-violet outside and red inside; golden-yellow eyes; a golden-yellow sleeveless top; a red cape hanging from her shoulders down her back; a brown belt with a round orange gem at the front; a long orange-red cloth hanging in front of her legs; pale bandage wraps on her lower legs; dark goat hooves. She holds a long thin golden-brown staff upright in front of her: a big golden crescent moon on top, a round orange orb at the bottom end.
Pixel rules (most important): at most 20 colors in total; every material 2-3 flat shades (light, base, shadow); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Keep only details that read at this size: the hair 2-3 light grey shades, the ponytail a thick white shape with a round bun at its top; the horn about 3 squares tall and 1 square wide; the ears 3-4 squares long with 1-2 red squares inside; the top flat yellow; the cape flat red; the gem one orange square on a brown belt row; the front cloth flat orange-red; the leg wraps pale; the hooves dark. The staff a 1-square golden-brown line, the crescent about 5x6 squares of gold with a lighter edge, the orb a 2x2 orange ball. Keep a dark outline or a different color between the staff and her hands, legs and head, so the crescent and the orb never merge with her body. Drop every other trim, marking and pattern.
Face: the head is one third of her height; blue-violet skin in 2-3 shades; two clearly visible eyes, each 2x2 squares (a bright yellow iris with one dark pupil square); a 1-square mouth; no dark vertical lines around the nose and mouth; the fringe covers the sides of her forehead but never her eyes. The outline of her head is rounded - the crown and the side of her face are curves, never one long straight edge. At game size the head must read at once as "blue face, white hair, one horn".
Pose, size and place: exactly as in the FIRST image - the same relaxed stance holding the staff upright in front of her, the same height, hooves on the same line 28 squares (224 px) above the bottom of the image, the character horizontally centered. 3/4 FRONT view facing right: we see her face and chest.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: she is 34 squares tall from the top of her hair to her hooves, all squares 8x8 on one grid, at most 20 colors, both 2x2 eyes are clearly visible, the horn is small and the staff is separated from her body by an outline.
```

8 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

### 2. `soraka_idle.png`：待机，6 帧，3 列 × 2 行

附 `soraka_native.png` + `soraka_native_idle.png` + `soraka_pose_idle.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame - do not draw it bigger; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb, separated from her hands and hooves by an outline, in the hand shown in the SECOND image. 3/4 FRONT view facing right; never draw her back - when she turns or bends over, keep her face and chest turned toward the viewer.
Animation: IDLE, 6 frames, a seamless gentle loop, as in the SECOND image: she stands calmly holding her staff upright in front of her and breathes slowly - her body (not the hooves) is up in frames 1, 2 and 6 and exactly one square lower in frames 3, 4 and 5; the staff moves with her hand; the ponytail and the cape sway a little. The head is exactly the same drawing in all 6 frames, it only moves up and down with the body; the hooves stay planted.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 72x72 squares (576x576 px), image 1728x1152; frame N in the same cell as in the SECOND image, at the same place, hooves on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 3. `soraka_run.png`：跑步，8 帧，4 列 × 2 行

附 `soraka_native.png` + `soraka_native_run.png` + `soraka_pose_run.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame - do not draw it bigger; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb, separated from her hands and hooves by an outline, in the hand shown in the SECOND image. 3/4 FRONT view facing right; never draw her back - when she turns or bends over, keep her face and chest turned toward the viewer.
Animation: RUN loop, 8 frames, as in the SECOND image: a light, bounding run on her hooves, leaning forward; she carries the staff horizontally in front of her at chest height, the crescent end forward (to the right) and the orb end behind her; one hoof on the ground in frames 1, 2, 5 and 6, both hooves off the ground in frames 3, 4, 7 and 8; the ponytail and the cape stream out behind her. Keep her head in the same column in every frame, as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 72x72 squares (576x576 px), image 2304x1152; frame N in the same cell as in the SECOND image, at the same place and height, hooves (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 4. `soraka_attack.png`：普攻，7 帧，4 列 × 2 行（最后一格空）

附 `soraka_native.png` + `soraka_native_attack.png` + `soraka_pose_attack.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame - do not draw it bigger; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb, separated from her hands and hooves by an outline, in the hand shown in the SECOND image. 3/4 FRONT view facing right; never draw her back - when she turns or bends over, keep her face and chest turned toward the viewer.
Animation: BASIC ATTACK, a staff swing, 7 frames, as in the SECOND image: 1 leaving her stance; 2 she lifts the staff; 3 the staff is swung back over her shoulder, the crescent behind her head; 4 she swings it forward; 5 THE RELEASE: the staff held out horizontally to the right, the crescent end pointing at the enemy; 6 follow-through, the staff swung on past; 7 back toward her stance with the staff upright. She faces the viewer through the swing. Draw no projectile and no glow.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 72x72 squares (576x576 px), image 2304x1152; frame N in the same cell as in the SECOND image, at the same place, hooves on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 5. `soraka_skill.png`：Q「流星坠落」，7 帧，4 列 × 2 行（最后一格空）

附 `soraka_native.png` + `soraka_native_skill.png` + `soraka_pose_skill.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame - do not draw it bigger; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb, separated from her hands and hooves by an outline, in the hand shown in the SECOND image. 3/4 FRONT view facing right; never draw her back - when she turns or bends over, keep her face and chest turned toward the viewer.
Animation: STARCALL, 7 frames, as in the SECOND image: 1 leaving her stance; 2-3 she raises her staff straight up to the sky, the crescent high above her head, and looks up at it; 4 she swings the staff down in front of her; 5-6 she bows low over it, the staff pointing forward and down at the ground in front of her, calling a star down - her head is lowered, but her face still shows toward the viewer as in the SECOND image; 7 she rises back toward her stance. Draw no star and no glow - they are a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 72x72 squares (576x576 px), image 2304x1152; frame N in the same cell as in the SECOND image, at the same place, hooves on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 6. `soraka_skill2.png`：W「星之灌注」，7 帧，4 列 × 2 行（最后一格空）

附 `soraka_native.png` + `soraka_native_skill2.png` + `soraka_pose_skill2.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame - do not draw it bigger; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb, separated from her hands and hooves by an outline, in the hand shown in the SECOND image. 3/4 FRONT view facing right; never draw her back - when she turns or bends over, keep her face and chest turned toward the viewer.
Animation: ASTRAL INFUSION, a healing spell, 7 frames, as in the SECOND image: 1 leaving her stance; 2 she turns a little and lifts the staff; 3-5 she holds the staff high up and forward, the crescent above and ahead of her, her free hand stretched back, looking up - she sends starlight to an ally; 6 she lowers the staff; 7 back toward her stance. Draw no light - the heal is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 72x72 squares (576x576 px), image 2304x1152; frame N in the same cell as in the SECOND image, at the same place, hooves on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 7. `soraka_ult.png`：R「祈愿」，8 帧，4 列 × 2 行

附 `soraka_native.png` + `soraka_native_ult.png` + `soraka_pose_ult.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame - do not draw it bigger; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb, separated from her hands and hooves by an outline, in the hand shown in the SECOND image. 3/4 FRONT view facing right; never draw her back - when she turns or bends over, keep her face and chest turned toward the viewer.
Animation: WISH, a prayer to the stars, 8 frames, as in the SECOND image: 1 leaving her stance; 2 she raises the staff high above her head; 3-5 she bows deeply forward, the staff held out low in front of her, her ponytail flipping up over her back - her head is lowered, but her face still shows toward the viewer as in the SECOND image; 6 she rises; 7-8 she straightens up with the staff held out in front of her and returns to her stance. Draw no light - the wish is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 72x72 squares (576x576 px), image 2304x1152; frame N in the same cell as in the SECOND image, at the same place, hooves on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 8. `soraka_hit.png`：受击，2 帧，2 列 × 1 行

附 `soraka_native.png` + `soraka_native_hit.png` + `soraka_pose_hit.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in both frames; the same face with two 2x2 yellow eyes, the white fringe, the small horn. Keep the staff with its golden crescent and orange orb, separated from her body by an outline. 3/4 FRONT view facing right, never her back.
Animation: HIT, 2 frames, as in the SECOND image: 1 she flinches from a blow - hunching forward a little, head dipped, the staff tilting; 2 recovering toward her stance.
Layout: exactly like the SECOND image - a grid of 2 columns x 1 row of cells, each cell 72x72 squares (576x576 px), image 1152x576; frame N in the same cell as in the SECOND image, at the same place, hooves on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 9. `soraka_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）

附 `soraka_native.png` + `soraka_native_dead.png` + `soraka_pose_dead.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Soraka at 8x (every pixel an 8x8 block) - copy her colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Soraka rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing she is 34 pixels tall from the top of her hair to her hooves, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Her head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame. Keep the staff a 1-square golden-brown line with its golden crescent and orange orb. The same camera as the FIRST image.
Animation: DEATH, 7 frames, as in the SECOND image: 1 struck, she crumples and lets go of her staff, which falls away to her right; 2-3 she staggers, the staff lying on the ground beside her; 4 she lifts her head one last time, face toward the viewer; 5 she falls forward; 6-7 she lies face down on the ground, her ponytail over her back, the staff lying next to her. Draw the staff exactly where the SECOND image has it, inside the cell. She lies on the ground line in frames 6-7, exactly as high as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 72x72 squares (576x576 px), image 2304x1152; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 技能特效（9 张）

9 张特效的提示词都以同一段画风开头。

### 10. `soraka_fx_bolt.png`：普攻星光弹（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden starlight color ramp (#FFFFFF, #FFF7D6, #FFE88A, #FFC940, #F29A2E) with a few pale blue sparks (#E8F0FF, #A8C8FF).
Effect: a small bolt of starlight flying to the RIGHT, 4 frames, seamless loop: a bright little golden crescent moon (its convex side facing right) with a white core, a short tapering trail of golden light behind it (to the left) and two or three tiny four-pointed sparkles; the crescent spins a quarter turn and the sparkles twinkle from frame to frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 1024x128; the crescent at the same spot near the right side of every cell, about 45% of the cell height, the whole bolt about 60% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `soraka_fx_hit.png`：普攻命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden starlight color ramp (#FFFFFF, #FFF7D6, #FFE88A, #FFC940, #F29A2E) with a few pale blue sparks (#E8F0FF, #A8C8FF).
Effect: a STARLIGHT hit, 5 frames: 1 a small white flash; 2 a bright four-pointed star burst with a thin golden ring; 3 the ring widens and tiny sparkles fly out; 4 the sparkles shrink; 5 the last sparkles fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the burst at most 40% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `soraka_fx_q_star.png`：Q 流星坠落（从天而降 + 落地），8 帧

落点在每格底部往上 12% 处（游戏按这个点放在地上）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden starlight color ramp (#FFFFFF, #FFF7D6, #FFE88A, #FFC940, #F29A2E) with night-sky blue sparks (#E8F0FF, #A8C8FF, #6E8BF0).
Effect: STARCALL, a star falling from the sky onto a spot on the ground, seen from the same slightly top-down game camera, 8 frames. The landing point is at the horizontal center of every cell, 12% of the cell height above the bottom edge. 1 a bright star appears at the top of the cell, a little to the left; 2-4 it falls steeply toward the landing point, growing brighter: a big white-core golden four-pointed star with a long tapering tail of golden and pale blue light behind it (up and to the left); 5 THE IMPACT: a blinding white-gold flash at the landing point; 6 a starburst on the ground - a slightly flattened golden ring about 1.3 times wider than tall, rays and sparkles thrown up; 7 the ring widens to 90% of the cell width and thins, sparkles drifting up; 8 the last sparkles fading.
Layout: one horizontal row of 8 equal cells, each twice as tall as wide (1:2), image size 2048x512; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `soraka_fx_rejuv.png`：活力焕发（索拉卡身上），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a healing color ramp (#F2FFE0, #BDF28A, #6FD06A, #2F9A52) with golden starlight (#FFFFFF, #FFE88A, #FFC940).
Effect: REJUVENATION on a healer, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a few green and gold sparkles appear at the feet; 2-4 they rise around the space in a gentle spiral, small four-pointed golden stars and green plus-shaped glints; 5 a soft green glow flickers at chest height; 6 the last sparkles fade above the head.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `soraka_fx_e_field.png`：E 星体结界（地面），8 帧

原版的地面范围特效是正圆或略扁的圆（宽高比约 1–1.35），这张也照这个比例画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, night-sky colors (#E8F0FF, #A8C8FF, #6E8BF0, #6A4FC8) with golden starlight (#FFFFFF, #FFF7D6, #FFE88A, #FFC940).
Effect: EQUINOX, a circle of starlight on the ground, seen from the same slightly top-down game camera, 8 frames. The circle is a slightly flattened ellipse about 1.3 times wider than tall, filling 90% of the cell width, its center at the center of every cell. 1 a thin golden ring flashes open; 2 the ring is complete: a double golden border with small star glyphs around it, the inside a translucent-looking deep blue field (drawn as flat blue and violet shapes, not transparency) scattered with tiny twinkling stars; 3-6 the field shimmers: the stars twinkle and the glyphs along the border glow one after another (frames 3-6 form a seamless loop); 7 the ring snaps inward with a bright golden flash along the border (the field closes); 8 the last golden sparks fade.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `soraka_fx_e_bind.png`：E 定身（敌人脚下），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden starlight (#FFFFFF, #FFF7D6, #FFE88A, #FFC940, #F29A2E) with night-sky blue (#A8C8FF, #6E8BF0).
Effect: STAR ROOT on an enemy, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 golden sparks gather at the feet; 2 two glowing golden rings of starlight snap shut around the ankles and lower legs, with a small crescent moon glyph floating in front; 3-5 the rings pulse and small stars circle along them (frames 3-5 form a seamless loop); 6 the rings break into sparks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the rings about 45% of the cell wide, around the lower part of the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `soraka_fx_w_heal.png`：W 星之灌注（友方身上），7 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a healing color ramp (#F2FFE0, #BDF28A, #6FD06A, #2F9A52) with golden starlight (#FFFFFF, #FFF7D6, #FFE88A, #FFC940).
Effect: ASTRAL INFUSION, a heal landing on an ally, 7 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a small golden crescent glyph shines above the head of the space; 2 a shower of golden stars and green glints pours down from it over the space; 3 a bright green-white flash at chest height; 4-5 a soft green ring rises from the feet to the chest, green plus-shaped glints and tiny stars floating up; 6-7 the glints fade upward.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `soraka_fx_r_cast.png`：R 祈愿（索拉卡头顶），7 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden starlight (#FFFFFF, #FFF7D6, #FFE88A, #FFC940, #F29A2E) with night-sky blue (#E8F0FF, #A8C8FF, #6E8BF0).
Effect: WISH, a star of hope rising above a healer, 7 frames. In the lower middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height stands there, feet at 92% of the cell height) - never draw the person. 1 sparkles gather above the head of the space; 2-3 they form a big bright four-pointed star with a white core and long thin rays, hovering above the head; 4 the star flares, a ring of light pulses out from it; 5-6 the star shoots straight up out of the cell, leaving a column of sparkles; 7 the last sparkles.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the star centered above the empty space, at most 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 18. `soraka_fx_r_heal.png`：R 祈愿落在每个友方身上，8 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden starlight (#FFFFFF, #FFF7D6, #FFE88A, #FFC940) with a healing green (#F2FFE0, #BDF28A, #6FD06A) and night-sky blue (#A8C8FF, #6E8BF0).
Effect: WISH answered - a pillar of starlight healing an ally, 8 frames. In the lower part of every cell there is an EMPTY person-sized space (a person about 30% of the cell height stands there, feet at 94% of the cell height) - never draw the person. 1 a small star appears at the top of the cell; 2 a narrow beam of golden-white starlight shoots down from it to the feet of the space; 3 the beam widens into a pillar about as wide as the space, a bright green-white flash and a flattened golden ring on the ground at the feet; 4-5 the pillar glows, green glints and tiny stars floating up inside it; 6 the pillar thins; 7-8 it fades from the top down, leaving a few sparkles around the space.
Layout: one horizontal row of 8 equal cells, each twice as tall as wide (1:2), image size 2048x512; the pillar centered on the empty space, at most 60% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧时长已写进 `native/soraka_cells.json`，出手帧对齐数据里的出手时刻；导入时按画面再微调。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `soraka_idle.png` | 6 | `idle` | 6 × 250（原版 2 秒一次呼吸，这里 1.5 秒） |
| `soraka_run.png` | 8 | `run` | 8 × 100（原版 `Run` 1.0 秒两步） |
| `soraka_attack.png` | 7 | `attack` | 60/60/70/60/90/80/80，第 5 帧出手（tick 15） |
| `soraka_skill.png` | 7 | `skill`（Q + E） | 60/60/80/60/100/90/100，第 5 帧召唤星星（tick 16） |
| `soraka_skill2.png` | 7 | `skill2`（W） | 60/80/80/100/100/80/80，第 4 帧治疗（tick 13） |
| `soraka_ult.png` | 8 | `ult`（R） | 70/100/100/150/150/100/100/100，第 4 帧祈愿（tick 16） |
| `soraka_hit.png` | 2 | `hit` | 120/120 |
| `soraka_dead.png` | 7 | `dead` | 100/100/120/120/120/200/400 |
| `soraka_fx_bolt.png` | 4 | 飞行道具 `league_soraka_bolt` | 4 × 60 循环 |
| `soraka_fx_hit.png` | 5 | 特效 `league_soraka_hit` | 5 × 60 |
| `soraka_fx_q_star.png` | 8 | 范围投射物 `league_soraka_q_star`（落点 = 投射物位置，延迟 24 + 生效 10 tick） | 4 × 100 下落，之后 4 帧共约 170 |
| `soraka_fx_rejuv.png` | 6 | 特效 `league_soraka_rejuv`（跟随索拉卡） | 6 × 80 |
| `soraka_fx_e_field.png` | 8 | 区域 `league_soraka_e_field`（地面，90 tick） | 1–2、3–6 循环、7–8，合计 1.5 秒 |
| `soraka_fx_e_bind.png` | 6 | 特效 `league_soraka_e_bind`（跟随，定身 1 秒） | 1–2、3–5 两遍、6 |
| `soraka_fx_w_heal.png` | 7 | 特效 `league_soraka_w_heal`（跟随被治疗的友方） | 7 × 80 |
| `soraka_fx_r_cast.png` | 7 | 特效 `league_soraka_r_cast`（跟随索拉卡） | 7 × 90 |
| `soraka_fx_r_heal.png` | 8 | 特效 `league_soraka_r_heal`（跟随每个友方） | 8 × 90 |

`soraka_native.png` 只用来保持造型一致，不进游戏。

## 姿势参考：英雄联盟原版动作

**客户端动画图**（`animations/skin0.bin`）：
- 索拉卡是老英雄，动画图里全是单文件片段，没有条件分支。
- 待机 `Idle1` 循环；`Idle2`–`Idle4` 是闲置小动作，团战里不用。
- 移动只有 `Run` 一个片段，没有战斗中移动的分支（李青那种 `Run_In` / `Run_combatOut` 这里没有）。
- 普攻 `Attack1`、`Attack2`，暴击 `Crit` 也是 `Attack2`；Q、W、E、R 分别是 `Spell1`–`Spell4`；死亡 `Death`。

**测量结果**：
- **跑步是跑，不是走**：`Run` 1.0 秒两步，每步约 0.27 秒双脚离地，是蹄子着地的轻快蹦跳。
- **待机**：2 秒一次缓慢呼吸，头的起伏换算到游戏尺寸不到 1 px；动作图里要求画成 1 格的起伏。
- **出手时刻**：普攻 `Attack1` 约 300 ms 法杖横指前方（月牙朝敌人）；Q 约 330 ms 弯腰把法杖指向地面；W 约 320–560 ms 法杖高举；R 约 400–700 ms 深鞠躬。
- 普攻选 `Attack1`：她全程正面朝向镜头，把法杖从肩后抡到身前。`Attack2` 更偏侧面，出手后手伸向前、法杖收在身后。

**渲染设置**：
- **镜头**：yaw 55、pitch 25，**不镜像**。不镜像时待机看得到脸，月牙法杖立在身前；镜像后普攻会变成背影。全部动作同一侧。
- **比例**：`--head 2.0 --legs 0.8`。长马尾挂在胸部骨骼（`Chest`）下，自然保持原长；角没有自己的蒙皮权重（挂在 `Head` 上），用 `"keep": {"horn": 4.0}` 把 `horn` 骨骼周围 4 个单位内的 45 个顶点绑到它上面，再用 hair 0.5 保持原长。量"头顶到蹄底 34 px"时不算角。
- **格子**：死亡时法杖甩到身体右边躺在地上，整帧宽 60 多格，所以格子是 72×72 方块。
- **弯腰帧**：Q 的第 4–7 帧、R 的第 3–6 帧朝镜头转 15–30 度（`turn`），并把头转成待机时的朝向（`head_like`，逐帧设置）。原版这几帧低头，只看得到头顶。
- **死亡**：保留 65% 的前冲，每帧的最低点按离地高度贴在地面线上。
- **受击**：原版没有受击动作，用待机和死亡 150 ms（身体前屈）按 0.3、0.12 混合。

帧的清单在 [`poses.json`](poses.json)，锚点表在 [`../native/soraka_cells.json`](../native/soraka_cells.json)。重新生成：

```bash
python tools/lol/native_pose.py assets/source/soraka/poses.json --out <文件夹>
python tools/art/native_refs.py --out <文件夹> --style --pack lux --pack ashe --pack leesin
```

第二条写出 `tfm2_style_ref_healer.png` 和 `pack_native_ref.png`（还有其他几张风格图，用不到可以删）。原版英雄对照图从游戏的 `bundle.game_data` 读取，只在本地用。

三视图 `soraka_model_chibi.png`：待机第 0 帧 `Soraka_Idle1@0`，`--yaw 40`、`100`、`200` 各渲染一张，横向拼接：

```bash
python tools/lol/pose_ref.py --champ Soraka --hq --head 2.0 --legs 0.8 --hair 0.5 --keep horn:4 --yaw 40 --pitch 10 --size 800 --width 0.75 --fit 0.8 --ground 0.92 --bg 225,225,225 --no-labels --out <文件夹> --name view_40 --frame soraka_idle1@0
```
