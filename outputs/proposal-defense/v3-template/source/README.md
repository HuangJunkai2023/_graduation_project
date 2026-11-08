# 交大原模板迁移源

本版不再使用v2自定义封面和页眉。实际从 `docs/交大ppt模板-1.pptx` 复制原生幻灯片：第1页用于封面、第9页用于第13页致谢，第8页用于其余16页。

`inputs/` 保留迁移所用的v2及模板副本，便于独立重建。它们与项目原文件相同，原文件未覆盖。原v2的完整JS内容生成器仍在 `outputs/proposal-defense/v2/source/`。

## 执行顺序

Windows、Microsoft PowerPoint、Python（lxml、pymupdf）可用时：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File source/migrate_to_template.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File source/render_and_validate.ps1 -Candidate .build/template-candidate.pptx -OutputDir .
python source/validate_migration.py
```

在本文件的上一级输出目录运行这些命令。`migrate_to_template.ps1` 默认从本文件旁的 inputs 读取文件，并写入上一级 `.build`。输出文件名为 `OCS_Proposal_Defense_EN_v3_SWJTU_Template`。

迁移器复制v2的原生正文对象、表格、连线与图像，不把整页变成图片。仅移除自定义页眉，替换为原模板标题占位符；缩短标题以适配模板校徽区。封面和致谢页保留原模板图片、装饰与Logo。复制全部中文备注。

质检器检查16页正文对象文本及类型与v2一致、18份备注一致、讲稿内容与时长一致、模板原图复用、文字溢出、文本框非预期重叠及PDF页数。模板封面/致谢的原生装饰有意交叠，不误报为正文遮挡。

照片授权延用v2：AlexHe34，Overhead-lines-railway.JPG，CC BY-SA 3.0。完整作者、来源和许可链接在第2页备注及本次完整包的 `source/asset_credits.json` 中。
