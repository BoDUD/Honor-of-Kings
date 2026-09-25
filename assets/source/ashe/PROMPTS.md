# 艾希：给 GPT 的生图提示词

一共 16 张图：1 张造型参考、9 张角色动作、6 张特效。生成的 PNG 放进仓库 `ashe` 分支的 `assets/source/ashe/`，或者任意一个文件夹，然后告诉 Claude。
Claude 负责切帧、缩到游戏尺寸（身高约 34 px）、统一调色板、补 1 px 黑描边、对齐脚底，再接到技能上（`tools/art/import_ashe.py`，导入时再写）。

## 生成顺序（重要）

1. **先只生成 `ashe_ref.png`**（第 1 条），附三张图：`ashe_model.png`（英雄联盟游戏内模型的正面、侧面、背面渲染，定造型和配色）、`ashe_pose_ref.png`（待机姿势）、`garen_ref_v3.png`（本包已通过的盖伦，定画风和大小，在 `assets/source/garen/`）。
2. 看一眼 `ashe_ref.png`：脸和胸口朝向画面，弓在画面右侧那只手（她的左手）里，颜色和 `ashe_model.png` 一致。不对就重画这一张，**不要带着错的参考图往下做**。
3. 其余 9 张角色图**同一批**生成，每张都附两张图：第一张 `ashe_ref.png`（造型和大小），第二张对应的姿势参考图（动作）。受击没有英雄联盟原版动作，只附第一张。
4. 6 张特效图不附图。
5. 如果以后要改造型，所有角色图用新的参考图整批重画，不混用不同批次的图。

姿势参考图（`ashe_model.png`、`ashe_pose_*.png`）是从本地英雄联盟客户端渲染的 Riot 模型，**只在本地用，不提交到仓库**。压缩包里已经有；需要重新生成时用本文末尾的命令。

## 这次避开盖伦踩过的坑

| 盖伦的问题 | 艾希的做法 |
|---|---|
| 第一轮凭文字想象动作，待机、普攻和英雄联盟不一样 | 每个动作都从英雄联盟原版动画渲染姿势参考，每一帧对应原版的一个时间点（见文末表格） |
| 参考图从错误的一侧渲染，画出来只有背影 | 所有参考图都在同一侧渲染，已逐张检查能看到脸和胸口（艾希不用 `--mirror`）。提示词写明 3/4 FRONT view、never show her back |
| 移动动作写成 run，其实英雄联盟里盖伦是走 | 查过客户端数据：艾希正常移速下是**跑**（有双脚离地的瞬间），1.0 秒一个循环，8 帧 × 125 ms。提示词写明 RUN，并写清身体前倾、弓平端在胸前指向前方、披风向后飘 |
| 普攻不像原版（扭身下劈） | 普攻按原版：弓竖直举在身前，拉弦到脸侧，松弦后右手向后甩开。提示词写明是射箭、不是挥砍 |
| 各轮画出的比例不同，施法时忽大忽小 | 所有角色图用同一张 `ashe_ref.png`、同一批生成 |
| 动作开头和结尾跳变 | 每个动作的第一帧和最后一帧是英雄联盟里「待机 ↔ 动作」的过渡混合姿势，动作从待机开始、回到待机 |
| — | 弓始终在同一只手（画面右侧、远侧的左手），箭袋在背后，所有参考图同一侧，不会换手 |

## 所有图的规则

- 每张图是**一行**，排着 N 个一样大的格子，每格一帧。格子之间不要留缝、边框、文字或编号。
- **背景透明**。做不到透明时：角色图用纯品红 `#FF00FF`，特效图用纯黑 `#000000`。
- 同一张图里每一帧的大小、位置都一致。角色图的脚底在每一格的同一高度。
- 角色图只画角色本身和弓上的光。飞出去的箭、命中特效都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把提示词里的 "Ashe" / "League of Legends" 删掉，只保留外观描述。

## 角色（10 张）

### 1. `ashe_ref.png`：造型参考，1 帧（附 `ashe_model.png`、`ashe_pose_ref.png`、`garen_ref_v3.png`）

```text
Three attached images. FIRST: 3D renders of Ashe's in-game model from League of Legends (default skin), seen from the front, the side and the back - copy her costume, colors and the shape of her bow from it. SECOND: the idle pose to draw. THIRD: another hero of the same game pack (Garen), already approved - match its pixel-art style, outline, shading, level of detail and scale exactly; Ashe is a slimmer woman, about 90% of his height including her pointed hood.
Ashe from League of Legends (default skin) as a 2D pixel art game sprite: a slim young woman archer. Black pointed hood with gold trim and a small gold emblem on its front; long silver-white hair with a faint lavender tint, bangs sweeping across her face; pale skin, ice-blue eyes, dark lavender lips. Angular gold pauldrons with black edges; a black halter top with a small gold crest, bare midriff, a cream sash at the waist; a short black skirt with vertical gold stripes; gold armbands on her upper arms; black fingerless gloves with gold cuffs; black thigh-high boots with gold zigzag trim and large gold greaves over the shins; black shoes. A long black cape with a wide gold border hangs behind her down to her ankles. A bronze quiver on her back, ice-blue crystal-tipped arrows sticking up behind her right shoulder. Her signature weapon: a large glowing ice-blue crystal recurve bow with jagged crystal spikes along its limbs and a dark grip, almost as tall as she is, with a thin blue string - draw it big and clearly readable.
Style: pixel art sprite for a small tactics / auto-battler game like Teamfight Manager 2, exactly like the THIRD image: chunky square pixels, hard edges, a 1-pixel black outline around the whole character, flat cel shading with 3-4 tones per color, no anti-aliasing, no gradients, no glow except the bow's own ice-blue light, about 32-40 colors, the same moderately chibi proportions as the third image. 3/4 FRONT view facing right: we see her face, her chest and the front of her body; the cape hangs behind her. Never show her back.
Pose: standing idle exactly as in the SECOND image: feet apart, torso toward the viewer, head turned slightly to the right. She holds the bow in her LEFT hand, the hand on the right side of the image, low and diagonally across the front of her body: the upper limb rises past her right shoulder, the lower limb points down to the right; an ice-blue arrow is nocked and points down at the ground in front of her, her right hand resting at the nock near her belly.
Layout: one single square image, the character centered, feet on an invisible ground line at 88% of the image height, the character (with the hood) about 60% of the image height. Transparent background (if not possible: solid #FF00FF magenta). No text, no border, no shadow.
```

### 2. `ashe_idle.png`：待机，6 帧循环（附 `ashe_ref.png` + `ashe_pose_idle.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game idle from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms and where the bow and arrow point. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: IDLE, 6 frames, seamless loop, as in the pose reference: she stands relaxed but ready, feet apart, torso toward the viewer, head turned slightly right. The bow is held LOW and diagonally across the front of her body in her left hand near her left hip, the upper limb past her right shoulder; the nocked arrow points down at the ground in front of her, her right hand at the nock. Only subtle breathing: chest and shoulders rise and fall 1 pixel, the cape hem sways slightly. Feet stay planted. Do NOT raise, draw or aim the bow, and do NOT put it on her back or shoulder.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 3. `ashe_run.png`：跑步，8 帧循环（附 `ashe_ref.png` + `ashe_pose_run.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape streams behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game movement animation from League of Legends, seen from the front, 8 frames left to right - one full cycle. Copy each frame's leg and arm positions exactly. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RUN to the right, 8 frames, seamless loop, as in the pose reference. This is a RUN, not a walk: a light, springy stride with a moment where BOTH feet are off the ground (frames 3 and 7), knees lifting, torso leaning forward a little, head up, looking ahead. She carries the bow LEVEL in front of her chest, turned flat and pointing FORWARD in the running direction exactly like the reference, the arrow nocked and pointing forward - the bow never trails behind her and is never on her back. The long cape streams out behind her and flutters. The legs keep the same length and shape in every frame; the body bobs up and down 2-3 pixels.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when upright about 60% of the cell height; the ground line at 88% of the cell height in every cell (the feet leave it in the airborne frames); body horizontally centered; the whole bow and cape stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 4. `ashe_attack.png`：普攻，6 帧（附 `ashe_ref.png` + `ashe_pose_attack.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game basic attack from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - stance, arms, where the bow points and where her drawing hand is. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: BASIC ATTACK, a bow shot, 6 frames, as in the pose reference: 1 from the idle stance of the first image she swings the bow up in front of her, turning it upright, her right hand going to the string; 2 FULL DRAW: the bow held upright at arm's length toward the right in her left hand, her right hand pulling the string back to her cheek, an ice-blue arrow nocked and aimed to the right, torso toward the viewer, head turned to the target; 3 RELEASE: the string snaps forward, the arrow is gone, her right hand flies back open beside her head, a tiny ice-blue spark at the bow; 4 follow-through: the bow still up at arm's length, right hand held back high; 5 recovery: right hand coming down, bow still upright; 6 lowering the bow back toward the idle stance of the first image. Feet stay planted. This is a bow shot: never swing the bow like a melee weapon, and do not draw the flying arrow.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole upright bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 5. `ashe_q_attack.png`：Q「射手的专注」强化普攻（连射），6 帧（附 `ashe_ref.png` + `ashe_pose_q_attack.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game Ranger's Focus flurry from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - the wide stance, the legs, the arms and the flat bow. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RANGER'S FOCUS FLURRY, a rapid empowered shot, 6 frames, as in the pose reference: 1 from the idle stance of the first image she steps into a WIDE, LOW stance, feet far apart, knees bent, and turns the bow FLAT (horizontal); 2 in the wide stance, the flat bow held at chest height pointing to the right, the string drawn to her chest, several ice-blue arrows nocked together; 3 RELEASE: the string snaps, her right hand jerks back, a small burst of ice-blue sparks at the bow; 4 a second quick release, hand back again; 5 holding the wide stance, hand returning to the string; 6 rising back toward the idle stance of the first image. In frames 2-5 the bow glows a brighter ice-blue. Do not draw the flying arrows.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the wide stance and the whole bow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 6. `ashe_skill.png`：Q「射手的专注」发动，6 帧（附 `ashe_ref.png` + `ashe_pose_skill.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game move into her Ranger's Focus stance from League of Legends, seen from the front, 6 frames left to right. Copy each frame's pose exactly - legs, arms and where the bow points. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: RANGER'S FOCUS activation, 6 frames, as in the pose reference: 1 the idle stance of the first image; 2 she swings the bow up to the left across her body; 3 the bow sweeps over to lie flat at shoulder height, her hair and cape lifting; 4 she drops into a WIDE, LOW stance, the flat bow held in front of her chest pointing right; 5 holding the focus stance, eyes narrowed on the target, the bow flaring bright ice-blue with a few frost sparkles around it; 6 rising back toward the idle stance of the first image, the glow fading.
Layout: one horizontal row of 6 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: when standing about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 7. `ashe_skill2.png`：W「万箭齐发」，7 帧（附 `ashe_ref.png` + `ashe_pose_skill2.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game Volley from League of Legends, seen from the front, 7 frames left to right. Copy each frame's pose exactly - stance, arms and how the flat bow is held. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: VOLLEY, 7 frames, as in the pose reference: 1 from the idle stance of the first image she raises the bow in front of her and turns it FLAT (horizontal); 2 standing square to the viewer, the flat bow held at chest height pointing right, her right hand drawing a fan of several ice-blue arrows; 3 full draw; 4 RELEASE: the string snaps, her right hand flies back beside her head, a burst of ice-blue sparks at the bow; 5 follow-through, the bow dipping forward and down; 6 recovery, right hand held up and back; 7 lowering the bow back toward the idle stance of the first image. Feet stay planted. Do not draw the flying arrows.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 8. `ashe_ult.png`：R「魔法水晶箭」，8 帧（附 `ashe_ref.png` + `ashe_pose_ult.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game Enchanted Crystal Arrow cast from League of Legends, seen from the front, 8 frames left to right. Copy each frame's pose exactly - stance, arms, where the bow points and where her drawing hand is. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look).
Animation: ENCHANTED CRYSTAL ARROW, 8 frames, as in the pose reference: 1 from the idle stance of the first image she swings the bow up upright; 2 FULL DRAW like a basic attack, but the nocked arrow is a large crystal of ice glowing white-blue; 3 holding the draw, frost light and small ice crystals gathering around the arrowhead; 4 holding, the crystal arrow at its brightest, her cape and hair lifted by a cold wind; 5 RELEASE: a bright white-blue flash at the bow, the crystal arrow is gone, her right hand thrown back high; 6 follow-through, bow still up, frost sparks fading; 7 right hand coming down; 8 lowering the bow back toward the idle stance of the first image. Feet stay planted. Draw only the glow on the bow and arrowhead, not the flying arrow.
Layout: one horizontal row of 8 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole upright bow and its glow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 9. `ashe_hit.png`：受击，2 帧（只附 `ashe_ref.png`）

```text
Same character as the ATTACHED image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the attached image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view facing right: we see her face and chest; the cape hangs behind her. Never show her back.
Animation: HIT REACTION, 2 frames, based on the idle stance of the attached image: 1 flinches from a blow: upper body jolted back and to the left, eyes squeezed shut, the bow still held low in her left hand, feet planted; 2 recovering, almost back in the idle stance of the attached image.
Layout: one horizontal row of 2 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the attached image: about 60% of the cell height; feet on an invisible ground line at 88% of the cell height; body horizontally centered; the whole bow stays inside its own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

### 10. `ashe_dead.png`：死亡，7 帧（附 `ashe_ref.png` + `ashe_pose_dead.png`）

```text
Same character as the FIRST attached image (Ashe, League of Legends) - copy her exact design, colors, proportions and size: slim archer in a black pointed hood with gold trim, silver-white hair, gold pauldrons, black top and skirt with gold trim, bare midriff, black thigh-high boots with gold greaves, long black cape with a gold border, bronze quiver with ice-blue arrows, and a large glowing ice-blue crystal bow held in her LEFT hand (the hand on the right side of the image).
Style: pixel art sprite like Teamfight Manager 2, exactly like the first image: chunky square pixels, hard edges, 1-pixel black outline, flat cel shading 3-4 tones, no anti-aliasing, no gradients, about 32-40 colors. 3/4 FRONT view, same camera as the first image.
Pose reference: the SECOND attached image is a 3D render of Ashe's real in-game death from League of Legends, seen from the front, 7 frames left to right. Copy each frame's pose exactly, including how high she is in the air. Take only the poses from it: draw the character like the first image, in the same pixel-art style, not like the render (ignore its colors, lighting and 3D look). Ignore the loose arrow lying on the ground in the render - do not draw it.
Animation: DEATH, 7 frames, as in the pose reference: 1 the idle stance of the first image; 2 struck: she staggers back, arms flung apart, the bow swinging away from her body; 3 leaning far back, knees giving way, the arm with the bow thrown up; 4 falling backward, feet leaving the ground, cape flaring; 5 falling almost horizontally toward the left, cape flying up; 6 landing on her back, the bow falling beside her feet; 7 lying still on the ground, head to the left, the bow on the ground by her feet.
Layout: one horizontal row of 7 equal square cells, no gaps, no borders, no labels. The character is exactly as big as in the first image (about 60% of the cell height when standing); the ground line at 88% of the cell height in every cell (she is in the air in frames 4-5); the whole body, cape and bow stay inside their own cell. Transparent background (if not possible: solid #FF00FF magenta).
```

## 技能特效（6 张）

特效不附参考图。飞行道具（箭）一律**朝右**画，游戏会按飞行方向旋转；命中和光环类特效居中画，中心要空出来的写在提示词里。

### 11. `ashe_fx_arrow.png`：普攻 / W 的冰霜箭（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp (#FFFFFF, #E6FBFF, #9BE8FF, #42B8F0, #1F6FC8).
Effect: FROST SHOT arrow in flight, 4 frames, seamless loop: a slim arrow flying to the RIGHT, perfectly horizontal - a pale ice-blue shaft, a pointed crystal arrowhead glowing white-blue at the right end, small crystal fletching at the left end - followed by a short trail of frost sparkles and cold mist that flickers from frame to frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), the arrow at the same position in every cell, about 70% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `ashe_fx_hit.png`：冰霜命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp (#FFFFFF, #E6FBFF, #9BE8FF, #42B8F0, #1F6FC8).
Effect: FROST SHOT hit, 5 frames: 1 a small white-blue flash; 2 a burst of sharp ice shards spraying outward from the center; 3 the shards scatter, a few snowflake sparkles; 4 shards falling and shrinking, a puff of cold mist; 5 the last sparkles fading.
Layout: one horizontal row of 5 equal square cells, the impact point at the center of every cell, the burst at most half the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `ashe_fx_flurry.png`：Q 连射（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp (#FFFFFF, #E6FBFF, #9BE8FF, #42B8F0, #1F6FC8).
Effect: RANGER'S FOCUS flurry in flight, 4 frames, seamless loop: a tight volley of five glowing ice-blue arrows flying to the RIGHT together, slightly fanned (their tips spread over about a third of the cell height), bright white-blue streaks behind them and frost sparkles; the arrows jitter a little from frame to frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), the volley at the same position in every cell, about 70% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `ashe_fx_focus.png`：Q 专注光环（绕着艾希），6 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp (#FFFFFF, #E6FBFF, #9BE8FF, #42B8F0, #1F6FC8).
Effect: RANGER'S FOCUS aura, 6 frames, seamless loop: small icy-blue light motes, tiny snowflakes and short frosty streaks rising upward around an EMPTY character-sized space in the middle (a person stands there), plus a thin glowing ice-blue ring on the ground at the bottom (a flat ellipse). Subtle, not covering the center.
Layout: one horizontal row of 6 equal square cells, the ring centered at the bottom of every cell (at about 80% of the cell height), the empty space above it about half the cell high, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `ashe_fx_crystal.png`：R 魔法水晶箭（飞行），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp with a white-hot core (#FFFFFF, #E6FBFF, #BDF3FF, #9BE8FF, #42B8F0, #1F6FC8, #123E8C).
Effect: ENCHANTED CRYSTAL ARROW in flight, 4 frames, seamless loop: a huge arrow made of glowing ice crystal flying to the RIGHT, horizontal: a big jagged crystal arrowhead with a white-hot core at the right end, a crystalline shaft, and behind it a long trail of swirling frost, ice shards and cold mist about as long as the arrow; the shards and sparkles shift every frame.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), the arrowhead at the same spot near the right side of every cell, the whole arrow and trail about 90% of the cell width, vertically centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `ashe_fx_r_hit.png`：R 命中 + 冰冻，9 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, icy color ramp with a white-hot core (#FFFFFF, #E6FBFF, #BDF3FF, #9BE8FF, #42B8F0, #1F6FC8, #123E8C).
Effect: ENCHANTED CRYSTAL ARROW impact and freeze, 9 frames: 1 a bright white-blue flash at the center; 2 a big star-shaped burst of ice shards; 3 jagged blue ice crystals shoot up around an EMPTY center where the enemy stands, forming a block of ice around them; 4-6 the ice holds and glitters, frost mist drifting, a frosty ring on the ground (a flat ellipse); 7 cracks spread through the ice; 8 the ice shatters into shards flying outward; 9 the last shards and mist fading.
Layout: one horizontal row of 9 equal square cells, the enemy's feet (the bottom center of the ice) at the same spot in every cell, at about 80% of the cell height, the ice block about half the cell high, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## Claude 导入时的对应关系（给 Claude 看）

帧时长是计划值，导入时按实际画面微调；普攻、技能的出手帧对齐数据里的出手时刻。

| 文件 | 帧数 | 游戏里的用途 | 计划帧时长 |
|---|---:|---|---|
| `ashe_idle.png` | 6 | 精灵图 tag `idle` | 6 × 267 ms（英雄联盟的呼吸循环 1.6 秒） |
| `ashe_run.png` | 8 | `run` | 8 × 125 ms（英雄联盟的跑步循环 1.0 秒） |
| `ashe_attack.png` | 6 | `attack` | 50/100/60/60/65/65，第 3 帧出箭（tick 9） |
| `ashe_q_attack.png` | 6 | `q_attack`（Q 期间的强化普攻，`CasterAnimation`） | 50/80/60/70/70/70，第 3 帧出箭 |
| `ashe_skill.png` | 6 | `skill`（Q 发动） | 6 × 67 ms |
| `ashe_skill2.png` | 7 | `skill2`（W） | 60/70/70/60/70/90/80，第 4 帧出箭（tick 12） |
| `ashe_ult.png` | 8 | `ult`（R） | 60/100/100/100/70/90/100/80，第 5 帧出箭（tick 22） |
| `ashe_hit.png` | 2 | `hit` | 2 × 120 ms |
| `ashe_dead.png` | 7 | `dead` | 100/120/120/120/150/200/400 |
| `ashe_fx_arrow.png` | 4 | 飞行道具 `league_ashe_arrow`（普攻、W） | 4 × 70 ms 循环 |
| `ashe_fx_hit.png` | 5 | 特效 `league_ashe_hit` | 5 × 60 ms |
| `ashe_fx_flurry.png` | 4 | 飞行道具 `league_ashe_flurry`（Q 强化普攻） | 4 × 70 ms 循环 |
| `ashe_fx_focus.png` | 6 | 特效 `league_ashe_focus`（Q 期间每 0.5 秒播一次） | 6 × 83 ms |
| `ashe_fx_crystal.png` | 4 | 飞行道具 `league_ashe_crystal`（R） | 4 × 70 ms 循环 |
| `ashe_fx_r_hit.png` | 9 | 特效 `league_ashe_r_hit`（R 命中，跟随目标，约 1.8 秒） | 80/80/100/250/250/250/250/250/250 |

`ashe_ref.png` 只用来保持造型一致，不进游戏。

## 姿势参考图：英雄联盟原版动作和时间点

客户端里艾希的动作：待机 `ashe_idle1`（前 5 秒是 1.6 秒一次的呼吸循环）；移动 `Run`/`Run2`/`Run3` = `ashe_run_walk`/`ashe_run_jog`/`ashe_run`。`ashe_run_walk` 是慢速时的潜行走路（脚底移动速度约 250），`ashe_run_jog` 和 `ashe_run` 腿部动作相同，是正常移速的跑步（约 305，接近艾希的基础移速 325），有双脚离地的瞬间，所以移动动作用 `ashe_run_jog`。普攻 `ashe_attack1`（开头就是满弓，约 333 ms 松弦）；Q `Ashe_spell1_IN`（进入连射姿势）+ `ashe_spell1`（连射）；W `ashe_spell2`（约 333 ms 松弦）；R 在客户端里用的是暴击动作 `ashe_crit1`（约 333 ms 松弦）；死亡 `ashe_death`。

`A>B:0.5` 表示两个动作各一半的混合姿势，英雄联盟切换动作时就是这样过渡的，用来让每个动作从待机开始、回到待机结束。

| 参考图 | 帧（动作@毫秒） |
|---|---|
| `ashe_pose_ref.png` | idle1@0 |
| `ashe_pose_idle.png` | idle1@0, 267, 533, 800, 1067, 1333 |
| `ashe_pose_run.png` | run_jog@0, 125, 250, 375, 500, 625, 750, 875 |
| `ashe_pose_attack.png` | idle1@0>attack1@0:0.5, attack1@0, 367, 533, 800, attack1@800>idle1@0:0.5 |
| `ashe_pose_q_attack.png` | idle1@0>spell1@0:0.5, spell1@0, 67, 267, 500, spell1@600>idle1@0:0.5 |
| `ashe_pose_skill.png` | idle1@0, spell1_in@83, 167, 250, 333, spell1_in@333>idle1@0:0.5 |
| `ashe_pose_skill2.png` | idle1@0>spell2@0:0.5, spell2@0, 267, 333, 450, 700, spell2@700>idle1@0:0.5 |
| `ashe_pose_ult.png` | idle1@0>crit1@0:0.5, crit1@0, 200, 300, 367, 500, 700, crit1@900>idle1@0:0.5 |
| `ashe_pose_dead.png` | death@0, 500, 700, 900, 1100, 1300, 1900 |

表里省略了动作名前缀 `ashe_`。重新生成的命令（`--hq` 逐像素贴图，比盖伦用的平面三角形清楚；艾希在英雄联盟坐标里胸口朝向镜头，所以**不加** `--mirror`，所有动作同一侧，弓不会换手）：

```bash
C="--champ Ashe --hq --yaw 55 --pitch 25 --size 360 --width 1.0 --fit 0.62 --ground 0.86 --shift -0.02 --bg 225,225,225 --no-labels --out ref"
python tools/lol/pose_ref.py $C --name ashe_pose_idle --frame ashe_idle1@0 --frame ashe_idle1@267 --frame ashe_idle1@533 --frame ashe_idle1@800 --frame ashe_idle1@1067 --frame ashe_idle1@1333
python tools/lol/pose_ref.py $C --name ashe_pose_run --frame ashe_run_jog@0 --frame ashe_run_jog@125 --frame ashe_run_jog@250 --frame ashe_run_jog@375 --frame ashe_run_jog@500 --frame ashe_run_jog@625 --frame ashe_run_jog@750 --frame ashe_run_jog@875
python tools/lol/pose_ref.py $C --name ashe_pose_attack --frame "ashe_idle1@0>ashe_attack1@0:0.5" --frame ashe_attack1@0 --frame ashe_attack1@367 --frame ashe_attack1@533 --frame ashe_attack1@800 --frame "ashe_attack1@800>ashe_idle1@0:0.5"
python tools/lol/pose_ref.py $C --name ashe_pose_q_attack --frame "ashe_idle1@0>ashe_spell1@0:0.5" --frame ashe_spell1@0 --frame ashe_spell1@67 --frame ashe_spell1@267 --frame ashe_spell1@500 --frame "ashe_spell1@600>ashe_idle1@0:0.5"
python tools/lol/pose_ref.py $C --name ashe_pose_skill --frame ashe_idle1@0 --frame ashe_spell1_in@83 --frame ashe_spell1_in@167 --frame ashe_spell1_in@250 --frame ashe_spell1_in@333 --frame "ashe_spell1_in@333>ashe_idle1@0:0.5"
python tools/lol/pose_ref.py $C --name ashe_pose_skill2 --frame "ashe_idle1@0>ashe_spell2@0:0.5" --frame ashe_spell2@0 --frame ashe_spell2@267 --frame ashe_spell2@333 --frame ashe_spell2@450 --frame ashe_spell2@700 --frame "ashe_spell2@700>ashe_idle1@0:0.5"
python tools/lol/pose_ref.py $C --name ashe_pose_ult --frame "ashe_idle1@0>ashe_crit1@0:0.5" --frame ashe_crit1@0 --frame ashe_crit1@200 --frame ashe_crit1@300 --frame ashe_crit1@367 --frame ashe_crit1@500 --frame ashe_crit1@700 --frame "ashe_crit1@900>ashe_idle1@0:0.5"
python tools/lol/pose_ref.py --champ Ashe --hq --yaw 55 --pitch 25 --size 360 --width 1.0 --fit 0.52 --ground 0.86 --shift 0.2 --bg 225,225,225 --no-labels --out ref --name ashe_pose_dead --frame ashe_death@0 --frame ashe_death@500 --frame ashe_death@700 --frame ashe_death@900 --frame ashe_death@1100 --frame ashe_death@1300 --frame ashe_death@1900
python tools/lol/pose_ref.py --champ Ashe --hq --yaw 55 --pitch 25 --size 720 --width 0.9 --fit 0.62 --ground 0.9 --bg 225,225,225 --no-labels --out ref --name ashe_pose_ref --frame ashe_idle1@0
```

`ashe_model.png` 是同一待机姿势（`ashe_idle1@0`）从三个角度的 `--hq` 渲染并排拼在一起：`--yaw 40`（正面）、`--yaw 100`（侧面）、`--yaw 200`（背面），都用 `--pitch 10 --size 800 --width 0.75 --fit 0.8 --ground 0.92`。
