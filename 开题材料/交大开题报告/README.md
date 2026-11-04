# 交大本科毕业设计（论文）开题报告

更新：2026-11-04。按老师指定的 `交大资料/开题报告模板.pdf` 重排研究正文和版式；与 `交大资料/附件九利兹学院本科毕业设计(论文)开题报告-新.docx` 冲突时，以附件九为准。两个原文件均未修改。

- [可编辑 Word](3.2023115799_黄俊凯_开题报告.docx)
- [阅览、打印 PDF](3.2023115799_黄俊凯_开题报告.pdf)
- [正文内容源](开题报告内容.md)
- [生成脚本](tools/build_swjtu_proposal.py)
- [流程图可编辑源](figures/planned_workflow.dot) / [图片](figures/planned_workflow.png)
- [最终检查与本轮修改记录](最终检查记录.md)
- [校验记录及文件哈希](校验记录.json)

## 模板采用与冲突处理

| 项目 | 本稿处理 |
| --- | --- |
| 示例的正文组织 | 采用编号式“1. Background and Significance / 2. Review of Related Research / 3. Research Aim and Objectives / 4. Research Content and Methods”，补充分级小标题。随后为周次工作计划、参考文献和意见签署区。 |
| 示例的呈现方式 | 使用窄栏中文栏目名、英文段落首行缩进、分阶段进度说明和计划系统流程图。先按内容确定实际分页，再生成每页独立且外框闭合的表格，不强制照搬旧稿四页篇幅。 |
| 示例中文正文与附件九英文要求冲突 | 按附件九使用英文题目和研究正文，中文栏目保留。 |
| 示例校名与校外导师栏 | 按附件九保留“西南交通大学-利兹学院”标题、原校徽页眉和校内导师字段；不套用示例的电气工程学院校名或添加附件九没有的校外导师栏目。 |
| 示例没有题目来源、资料情况比附件九多两项 | 保留附件九的题目来源及指导日志项；不增加设计任务书、外文翻译完成勾选，不复制示例中的已完成状态。 |
| 示例他人信息、题目、勾选、图和文献 | 均不复制。流程图为本项目的计划方法示意，不是实验结果。 |
| 附件九签署说明 | 保留全部13项逻辑行及填写说明，容量不足可增页；签名手写，意见和日期由相应人员实际填写。 |

本稿保留黄俊凯、2023115799、Electronic and Electrical Engineering、黄德青、教授，以及已确认英文题目。专业使用本人确认的英文名称，没有猜测新的中文登记专业。英文题目为：

> A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field

## 研究方案与当前状态

三个RQ、O1–O5、五组配置、100题的20/80划分、开发集调参、指标口径、400小时和£50预算保持不变。对原有论证作结构化展开，不新增功能、模型训练或实验组。保留原型可行性与正式实验的区别，Embedding和正式评测仍写为尚未验证。7篇文献沿用旧稿已核验记录，不声称本轮新增了文献研究或模型测试。

最终为**6页**：第1–2页为登记信息、背景、研究现状及研究目标开头；第3–4页续目标、研究方法、流程图和评测设计；第4–5页续周次工作计划及资源；第6页为全部参考文献及意见签署区。正文10.5磅、主要标题12磅、图注9.5磅；保留附件九的A4、页边距、登记栏合并关系、学校页眉和原签字区。研究长栏目按段落组排版，左栏合并、内部不加横线；先实际导出确定各组所属页面，再按页拆表并补齐上下边框，避免隐藏内部横线同时造成续页外框缺口。续页左栏留白，仍保留原13项逻辑栏目和44个排版行，不强制照搬示例的11页篇幅。

## 仍需实际填写的项目

- 选题类型、题目来源：由黄老师确认勾选，并与正式登记一致。
- 中方毕业设计指导日志填写情况：按真实情况填写；英文Journal不自动等同于该项。
- 指导教师意见、签字及实际日期：由黄老师填写。
- 专家组评审意见、组长签字及实际日期：由实际评审人员填写。

本稿适合送老师再次审核；上述栏目留空不表示审批已经完成。附件四要求最终归档提供与纸质一致的手写签字扫描PDF，本目录直接导出的PDF不能冒充签署扫描件。文件名沿用附件五的 `3.学号_姓名_开题报告` 规则。

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

从工程根目录运行，先编辑 `开题报告内容.md`。Word/PDF为派生文件，直接修改Word后重跑会被覆盖，应先同步内容源。

```bash
# 可编辑流程图有改动时重绘；否则可跳过
dot -Tpng -Gdpi=180 开题材料/交大开题报告/figures/planned_workflow.dot -o 开题材料/交大开题报告/figures/planned_workflow.png

# 生成Word和PDF；本机缓存中的LibreOffice，无需安装系统软件
.venv/bin/python 开题材料/交大开题报告/tools/build_swjtu_proposal.py \
  --renderer /home/huang/.cache/ocs-doc-renderer/lo/usr/lib/libreoffice/program/soffice.bin
```

有系统LibreOffice时可改用 `--renderer /usr/bin/soffice`；完整生成必须提供该参数；Word与PDF均经过实际分页后的边框定稿，避免仅导出中间Word布局。脚本检查题目/身份字段、64个正文标题/段落/图注、7篇文献、未勾选框、页面及图片边界、每页表格上下边框闭合和源文件哈希。重新生成后 `visual_review` 自动回到false，仍须渲染并实际检查全部页面，不能沿用上一次检查结论。

独立复查PDF外框：

```bash
.venv/bin/python 开题材料/交大开题报告/tools/check_table_frames.py 开题材料/交大开题报告/3.2023115799_黄俊凯_开题报告.pdf
```

2026-11-04补充修复：此前只检查页面边界，漏检了续页表格横边框。本次检查直接读取PDF矢量线段，可在旧版第2页复现缺口，并在修复后的全部6页通过。
