# 盖伦 GPT 原始素材交接

共 16 张 PNG：1 张参考图、9 张角色动画、6 张特效。文件名来自 garen 分支 assets/source/garen/PROMPTS.md。
提示词版本：5e7bd7413e9504c9865cc0374fd941e6d2dc1625。

先生成 garen_ref.png；9 张角色动画均要求实际附带该参考图。使用 GPT 图片生成，经本机 gpt-image-bridge 调用；内置端点当时返回 HTTP 404。
所有交付 PNG 都有实际 RGBA 透明通道，已读取验证；不是把棋盘格或黑底绘制进图片。

用户明确选择“保留 GPT 原图，交给 Claude 整理”。因此这些是生成源图，未进行脚本切分、补边、重排、缩放、调色板处理或像素修改。
这次只交付素材，没有修改仓库、技能接线或 PR 审核状态。

## 导入前需要处理

- 每张动画均按单行生成，目视核对了指定帧数。参考图之外共 93 个动画/特效帧。
- 实际画布比例不等于 PROMPTS.md 的最终方格/高格比例。不要直接把原图高度当作帧宽；按可见内容定位帧，再重排到统一帧格。
- 每帧脚底、角色比例和间距仍需校准；Q 跃斩的空中帧需要保留跳跃高度，死亡动作需保留倒地姿态。
- 部分剑柄、剑尖和发光边缘较贴近帧或画布边缘；Q 跃斩、战吼、死亡以及 R 特效的相邻内容需人工确认分界。不要把相邻帧内容带入同一帧。
- 源图有抗锯齿、半透明碎边和较多颜色，尚不是最终 40 px 游戏像素资源。请统一调色板、清理 alpha 边缘、补 1 px 黑描边，并检查武器轮廓及各动作缩小后的可读性。
- 特效保留透明通道，护盾和旋转特效中心留空。R 特效最终应排成 9 个宽高 1:2 的高格，并对齐落点到格高约 85%。
- 这些检查只覆盖源图内容/格式，不等于游戏运行、动画循环或 UI 裁切验证通过。

## 文件清单

| 文件 | 帧数 | 原图像素尺寸 | 对应用途 |
|---|---:|---|---|
| `garen_ref.png` | 1 | 1254 × 1254 | `造型参考，不进入游戏` |
| `garen_idle.png` | 6 | 2172 × 724 | `idle` |
| `garen_run.png` | 6 | 2172 × 724 | `run` |
| `garen_attack.png` | 6 | 2172 × 724 | `attack` |
| `garen_q_attack.png` | 7 | 2172 × 724 | `q_attack / CasterAnimation` |
| `garen_skill.png` | 4 | 2172 × 724 | `skill / Q 施放` |
| `garen_spin.png` | 8 | 2164 × 727 | `spin / E 循环` |
| `garen_ult.png` | 8 | 2172 × 724 | `ult` |
| `garen_hit.png` | 2 | 1774 × 887 | `hit` |
| `garen_dead.png` | 7 | 2194 × 717 | `dead` |
| `garen_fx_hit.png` | 4 | 2172 × 724 | `league_garen_hits:spark` |
| `garen_fx_q_hit.png` | 6 | 2172 × 724 | `league_garen_hits:q` |
| `garen_fx_q_ready.png` | 6 | 2172 × 724 | `league_garen_buffs:decisive` |
| `garen_fx_courage.png` | 6 | 2172 × 724 | `league_garen_buffs:courage` |
| `garen_fx_spin.png` | 8 | 2172 × 724 | `league_garen_spin:loop` |
| `garen_fx_r.png` | 9 | 1881 × 836 | `league_garen_r:impact` |

PROMPTS.md 保留仓库原始提示词，GENERATION_PROMPTS.md 记录生成时增加的参考图、透明通道和留白约束。
manifest.json 记录尺寸、透明度和 SHA-256，便于复制后核对文件。

将这 16 张 PNG 复制到仓库 garen 分支的 assets/source/garen/ 后，按原 PROMPTS.md 的对应关系处理、接线和验证。
