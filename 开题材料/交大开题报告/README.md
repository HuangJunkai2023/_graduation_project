# 交大附件九：本科毕业设计（论文）开题报告

完成日期：2026-10-30。依据 `交大资料/附件九利兹学院本科毕业设计(论文)开题报告-新.docx` 原表填写，原始附件未修改。

- [开题报告 Word（可编辑）](3.2023115799_黄俊凯_开题报告.docx)
- [开题报告 PDF（打印阅览）](3.2023115799_黄俊凯_开题报告.pdf)
- [正文内容源](开题报告内容.md)
- [生成脚本](tools/build_swjtu_proposal.py)
- [校验记录与文件哈希](校验记录.json)

文件名按附件五的“序号.交大学号_姓名_材料名”示例采用 `3.2023115799_黄俊凯_开题报告`。当前PDF是直接导出的阅览版；附件四要求最终归档提供与纸质一致的**手写签字扫描PDF**，实际签署后再扫描归档。

## 填写内容与依据

| 材料 | 本次采用的要求 |
| --- | --- |
| 附件九 | 保留学校页眉、中文栏目及全部项目；题目、选题意义/国内外现状、目标内容、工作计划用英文填写。容量不足可增页；签名须手写。 |
| 附件四 | 使用英文题目及交大学号；题目、专业、选题性质在各材料间一致；导师填写意见并签字，专家组意见由答辩小组组长签署，日期按实际填写。 |
| 附件五 | 按学号、姓名、材料类别命名；保留可编辑Word和PDF。 |
| 附件一、二 | 研究目标可衡量、方案可执行、进度与工作量合理、重视过程记录和学术诚信；不把中方过程管理与英方Journal视为已自动互认。 |
| 附件六、八 | 当前文件是空白登记/分组表，没有可用于核定个人选题类型、来源、专业中文登记名或答辩日期的已填记录，不据此猜测。 |
| 已确定的ELEC3801 Proposal | 保持三个RQ、五组配置、20–30份目标语料、100题的20/80开发测试划分及版本/证据检查定义；保留周次依赖、两周春节休息和400小时预算。英方Proposal的750词限额不套用为附件九全文限额。 |

姓名填写黄俊凯，中方学号按本人2026-10-30更正填写2023115799，导师黄德青。专业采用本人此前确认的 `Electronic and Electrical Engineering`，英文题目逐字采用本人给定版本：

> A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field

研究目标、成功阈值和费用均写为计划；没有把原型联调写成正式研究结果。引用检查与人工语义评估分开；A1保留标准家族过滤，A2保留引用验证和错误处理。没有新增研究问题、正式实验组或超出既定边界的功能。

## 按要求留空的部分

- 导师职称、题目来源、毕业设计指导日志填写情况，按本人2026-10-30的回复留空；没有把已有英文Journal自动视为中方指导日志已填写。
- 选题类型保留原表的全部未勾选选项，未假定空白选题登记表已确认某种类型；项目实际工作包含软件设计与效果评估，登记口径填写时需与其他材料一致。
- 指导教师意见、专家组评审意见、双方手写签字及实际日期均留空。本报告没有复用2026-10-26英方Proposal的签字或把该审批当作附件九审批。

## 版式与实际检查

正文及学校表格共**4页**：第一页为登记信息和研究意义/现状，第二页为研究目标与方案，第三页为周次工作计划，第四页为7篇参考文献及意见/签字区。

保留原表A4、页边距、合并单元格及13项逻辑行，按栏目分页为4个外层表格。英文正文10.5磅，参考文献及嵌套进度表9.5磅；原校名标题不变。PDF嵌入实际使用的字体，Times New Roman/宋体在本机使用兼容字体呈现。原表旧符号字体中的复选框替换为真正的空框Unicode，避免字体替代误显示为已选。

已重新导出、渲染并目视检查全部4页，检查空白页、裁切、表格边界、文字重叠、分页、复选框及签字区；同时检查英文题目一致性、目标/配置、参考编号、工时、400次正式测试、预算和签字空白。结果见校验JSON。原始附件九哈希保持不变；ELEC3801 Proposal、任务CSV、Journal与问答系统代码未修改。

## 文献依据

沿用已有方案的六篇文献，补入一篇已核验的中文RAG综述，用于“国内外研究现状”的中文研究部分；这是文献补充，不是增加技术范围。按出版方记录核对题名、作者与页码，不声称综述已证明接触网问答性能。

- [Lewis等：RAG，NeurIPS 2020](https://papers.nips.cc/paper_files/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)
- [Robertson与Zaragoza：BM25，2009](https://doi.org/10.1561/1500000019)
- [Karpukhin等：Dense Passage Retrieval，EMNLP 2020](https://aclanthology.org/2020.emnlp-main.550/)
- [Ma等：Query Rewriting，EMNLP 2023](https://aclanthology.org/2023.emnlp-main.322/)
- [Shi等：Irrelevant Context，ICML 2023](https://proceedings.mlr.press/v202/shi23a.html)
- [Es等：RAGAs，EACL 2024](https://aclanthology.org/2024.eacl-demo.16/)
- [Feng等：浅谈大模型时代下的检索增强，CCL 2024](https://aclanthology.org/2024.ccl-2.9/)，使用出版方双语题名中的英文版本并注明原文为中文。

## 重新生成

在工程根目录编辑本目录的 `开题报告内容.md`，然后运行：

```bash
# 生成Word
.venv/bin/python 开题材料/交大开题报告/tools/build_swjtu_proposal.py

# 同时导出PDF（需LibreOffice）
.venv/bin/python 开题材料/交大开题报告/tools/build_swjtu_proposal.py --renderer /usr/bin/soffice
```

本轮使用用户缓存中的临时解包版LibreOffice，未安装系统软件：

```bash
.venv/bin/python 开题材料/交大开题报告/tools/build_swjtu_proposal.py \
  --renderer /home/huang/.cache/ocs-doc-renderer/lo/usr/lib/libreoffice/program/soffice.bin
```

生成后仍应检查实际PDF分页；直接手改Word后重跑脚本会覆盖派生文件，应先同步内容源或另存。当前未替本人或老师签署、未提交学校系统、未自动提交Git。
