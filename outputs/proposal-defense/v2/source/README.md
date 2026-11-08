# v2 可编辑演示源文件

## 文件关系

- `build_deck.cjs`：PptxGenJS 4.0.1 版式与原生形状/连线/表格生成器。18页，其中13页主讲、5页备份。
- `prepare_content.py`：中文备注、逐字稿与20个问答的共同内容源，生成 `content.json` 和两份 Markdown。
- `content.json`：逐页的页码、时长、中文口述稿和来源。不要同时手改它和 Python 内容源；重建会从 Python 重新生成。
- `assets/`：原模板校徽和真实接触网原图。照片作者与许可见 `asset_credits.json` 和 `assets/PHOTO_LICENSE.txt`。
- `normalize_package.py`：移除本机 PptxGenJS 4.0.1 导出中指向不存在母版的冗余 Content-Type 声明，保留所有已有部件与正文；写入另一个候选文件。
- `render_and_validate.ps1`：用 Windows PowerPoint 打开候选，设置中文备注字体，另存最终PPTX/PDF，导出18张1600×900 PNG，检查正文和原生表格单元格的文字边界。
- `validate_deliverables.py`：检查18页、13+5分段、备注/讲稿一致性、580秒、20个问答、原生图示、字体、PDF页数、文本框重叠及输入哈希。
- `layout-manifest.json`：最近一次生成的元素几何信息，用于交叉检查。最终原生对象清单在 `../validation/powerpoint-objects.json`。

## 环境

Node.js；PptxGenJS 4.0.1；Python 3；Python包 `lxml`、`pymupdf`；Windows Microsoft PowerPoint（用于高保真渲染与PDF导出）。

本次使用现有 Codex 缓存中的 Node 和 PptxGenJS，没有全局安装新依赖。源代码优先解析本地 `pptxgenjs` 包，也支持 `PPTXGENJS_MODULE` 环境变量指定模块位置。代码内的本机缓存路径仅作本次环境的兜底路径。

## 重建

在保留完整源文件夹、原有 `validation/input-hashes.json` 及项目输入的情况下，从项目根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File outputs/proposal-defense/v2/source/rebuild.ps1
```

如果 Node 不在 PATH，可传 `-Node '实际的node.exe路径'`；Python可用 `-Python` 指定。脚本会更新 v2 派生文件，始终不写入 v1。`-ExecutionPolicy Bypass` 只用于该次 PowerShell 进程，不更改系统持久策略。

拆分执行时：先 `prepare_content.py`，再 `build_deck.cjs` 写 raw PPTX，然后 `normalize_package.py raw.pptx candidate.pptx`，最后 `render_and_validate.ps1 -Candidate ... -OutputDir ...` 与 `validate_deliverables.py`。

备注与讲稿的页码取自同一内容数组。调整页数、页序、口述稿时，必须同步 `prepare_content.py` 和 `build_deck.cjs`，并重新渲染。当前布局已按13+5固定设计，直接增页需要更新检查器中的页数契约。

## 可编辑性

正文、公式均为文字对象；架构、示例、版本/门控案例及甘特条形图为原生形状与连线；备份分母表为原生PowerPoint表格。仅封面校徽和第2页现场照片是图片，没有整页文本图片化。手工修改 PPTX 不会自动回写 JS，请把需要持续维护的修改同步到源代码。

## 预览与质检

`../previews/slide-01.png` 至 `slide-18.png` 为PowerPoint实际导出的完整页面。总览图位于上一级目录。不要把只通过结构检查等同于视觉检查；修改后仍需逐页查看。

本次没有更改PowerPoint加载项或应用设置，没有启动应用系统评测，也没有访问真实模型API。
