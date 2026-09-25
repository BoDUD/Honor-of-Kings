> 入库说明：`garen_run.png` 已替换 `assets/source/garen/` 里的同名文件（第四轮的跑步），其余源图不变。交付包里的 `references/`（英雄联盟模型的渲染）没有入库，用 `tools/lol/pose_ref.py` 按 PROMPTS.md 第五轮的命令重新生成；`garen_ref_v3.png` 已在仓库里。导入：8 帧 × 117 ms（0.936 秒一个循环），缩放和待机相同（tall 250），头部位置取英雄联盟 Run 在同样 8 个时间点的骨骼数据。

# 盖伦第五轮：8 帧走路

交付 `garen_run.png`：一行 8 帧，移动动作改为直立、抬头、沉稳迈步；游戏资源名称仍保留 run。
使用用户提供的 PROMPTS_round5.md，第一张输入是 garen_ref_v3.png（造型、比例），第二张是 garen_pose_walk.png（8 帧动作）。实际生成提示词保存于 garen_run.prompt.txt。

原图尺寸：2172 × 724，已验证真实 RGBA 透明通道。文件保留 GPT 原始输出，没有脚本裁切、缩放、重排或改像素。

## 交给 Claude

将 garen_run.png 作为 garen 分支 assets/source/garen/ 的同名移动动画源图。按可见的 8 帧分割，整理等大画布、脚底和调色板。原生长条画布可能含额外透明留白，并非严格的 8:1 方格条。
在游戏尺寸下核对头部、肩甲、躯干和腿部比例；不要只按含剑的外接框高度缩放。原图尚未经过游戏内播放验证。
参考目标循环约 0.93 秒，8 帧平均约 116 毫秒/帧；本轮只生成 PNG，没有改播放时序或游戏代码。

preview.html 可并排查看造型、姿势参考和生成长条。manifest.json 包含尺寸、哈希和参考对应。
