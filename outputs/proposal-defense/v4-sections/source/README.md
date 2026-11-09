# Contents与Part分节版构建源

1. 在仓库根目录运行 `python outputs/proposal-defense/v4-sections/source/prepare_sections.py`，生成23页映射、双语备注、讲稿和重新编号的问答。
2. 运行 `powershell -NoProfile -ExecutionPolicy Bypass -File outputs/proposal-defense/v4-sections/source/build_sections.ps1`，使用Windows PowerPoint复用原生模板目录/Part页，写入双语备注，导出PPTX、PDF及PNG。
3. 运行 `python outputs/proposal-defense/v4-sections/source/validate_sections.py`。

依赖：项目原模板 `docs/交大ppt模板-1.pptx`、v3双语备注PPT、v3的 `bilingual_notes.json` 和 `content.json`、PowerPoint、Python包lxml和pymupdf。原模板和旧版保留在原位置，不重新绘制图片。

新增目录使用原模板第3页；四张Part页使用第4–7页。新页码、分节和讲述参考时长统一维护在 `sections_content.json` 中，该JSON由Python源生成。架构、表格、公式及正文均延续旧版原生可编辑对象。

`SectionProperties` 写入6个PowerPoint原生分节。主讲18页包含目录和4个过渡页，另有5页备份。新增过渡只提示下一个Part，不增加研究内容。

源脚本和验证以本项目路径为默认，可通过PowerShell脚本的 `Root` 参数调整项目位置。不要用旧版讲稿页码配合本版演示。
