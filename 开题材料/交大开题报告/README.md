# 交大本科毕业设计（论文）开题报告

更新：2026-11-04。本人已确认黄老师完成签字；具体签字日期未提供，签字件未在本轮检查中读取。本目录保留补充内容、图示及两端对齐后的**9页可编辑源稿与直接导出PDF**，实际签名以本人持有的签署文件为准。采用 `交大资料/开题报告模板.pdf` 的章节结构；与附件九冲突时，仍以附件九为准。

- [开题报告 Word（可编辑）](3.2023115799_黄俊凯_开题报告.docx)
- [开题报告 PDF（阅览、打印）](3.2023115799_黄俊凯_开题报告.pdf)
- [正文内容源](开题报告内容.md)
- [生成脚本](tools/build_swjtu_proposal.py)
- [本轮修改与最终检查](最终检查记录.md)
- [校验记录、字数与文件哈希](校验记录.json)

## 本轮落实的意见

1. 正文采用两端对齐，保留首行缩进；标题左对齐、图与图注居中、参考文献左对齐。
2. 扩充研究对象、意义、领域难点、七篇文献的方法比较与适用边界，以及实验公平性、标注和复现记录说明。
3. 增加领域问题图与受控实验研究框架图，放大原系统流程图；三张图均为本项目自绘的计划示意，不是实验结果。
4. 精简风险和进度文字，保留全部课程里程碑、预算及过程记录要求。

| 图 | 作用 | 可编辑源 |
| --- | --- | --- |
| Fig. 1-1 | 领域问题与RQ1–RQ3的对应关系 | [DOT](figures/domain_challenges.dot) / [PNG](figures/domain_challenges.png) |
| Fig. 4-1 | 本地检索、证据门控、在线生成与来源展示 | [DOT](figures/planned_workflow.dot) / [PNG](figures/planned_workflow.png) |
| Fig. 4-2 | 开发集调参、冻结及五组受控实验 | [DOT](figures/research_framework.dot) / [PNG](figures/research_framework.png) |

研究问题、O1–O5和五组配置保持不变：20–30份文档、100题的20/80划分、400次正式执行、400小时和£50均为计划。Embedding和正式评价没有写成已验证。保留“a RAG system with local document retrieval”和“A2 Hybrid without the Evidence Gate”的准确表述。

## 表格、语言与登记字段

保留附件九的学校标题、页眉、A4、页边距、登记栏合并关系、全部13项逻辑栏目与意见签署区。正文按附件九使用英文，没有改成示例的中文，也未添加其校外导师、任务书或外文翻译勾选。首页仍为黄俊凯、2023115799、Electronic and Electrical Engineering、黄德青、教授及已确认英文题目。

英文正文10.5磅、主要标题12磅、图注9.5磅，没有为限制页数缩小字号。第1–4页为背景、意义、现状和目标；第5–7页为研究方法和两张方法图；第8页为精简进度；第9页为全部参考文献及意见签署区。

长栏目先按段落组排版，再依据实际PDF分页生成逐页独立表格，显式补齐首尾横边框；续页左栏留白。当前为54个排版行，仍属原13项逻辑栏目。已修复长栏目起始标题在页末挤出或裁切的情形。

按空白分词、计入小标题及图注，正文2574词、参考文献202词，合计2776词；不计首页登记信息、中文栏目及图内标签。这不是英方Proposal的Section I统计，英方750词限制不套用到附件九全文。

## 仍需实际填写

- 选题类型、题目来源：由黄老师确认勾选，并与正式登记一致。
- 中方指导日志状态：按真实情况填写，英文Journal不自动等同于该项。
- 指导教师意见、签字及实际日期：由黄老师填写。
- 专家组评审意见、组长签字及实际日期：由实际评审人员填写。

当前适合送老师再次审核，未伪造审批。按附件四，最后归档须为与纸质一致的手写签字扫描PDF；直接导出的PDF不能冒充签署扫描件。文件名沿用附件五的 `3.学号_姓名_开题报告`。

## 重新生成与检查

编辑内容源；修改图示后先重绘对应PNG，例如：

```bash
dot -Tpng -Gdpi=220 开题材料/交大开题报告/figures/domain_challenges.dot -o 开题材料/交大开题报告/figures/domain_challenges.png
dot -Tpng -Gdpi=220 开题材料/交大开题报告/figures/research_framework.dot -o 开题材料/交大开题报告/figures/research_framework.png

.venv/bin/python 开题材料/交大开题报告/tools/build_swjtu_proposal.py \
  --renderer /home/huang/.cache/ocs-doc-renderer/lo/usr/lib/libreoffice/program/soffice.bin

.venv/bin/python 开题材料/交大开题报告/tools/check_table_frames.py 开题材料/交大开题报告/3.2023115799_黄俊凯_开题报告.pdf
```

有系统LibreOffice时可使用 `--renderer /usr/bin/soffice`。完整生成必须提供渲染器：先取得实际分页，再同时定稿Word和PDF边框。直接手改Word后重跑会被覆盖，应先同步内容源。

脚本检查正文完整性、7篇参考文献、身份字段、11个未勾选框、文本/图片边界及每页表格外框。当前75个正文块完整；已渲染并查看全部9页，另实际核验41段正文的Word两端对齐属性。重建后 `visual_review` 自动回到false，须重新检查，不能沿用旧记录。

本轮文献核对与本地标准来源见[修改记录](最终检查记录.md)。学校原文件、英方Proposal、原任务CSV、Journal与问答系统代码没有修改。
