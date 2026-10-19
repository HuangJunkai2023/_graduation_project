# 接触网智能问答毕设：开题材料包

**当前文件为待签署版，使用学校 Proposal Form／示例格式，不使用 IEEE 双栏。** 首页已填写 Huang Junkai（黄俊凯）、201804121、Electronic and Electrical Engineering 和 Na Qin。伦理选项、项目安全风险评估及措施已填写；因未确认学校现有评估覆盖范围，选用提供项目专项评估的路径，交导师审核。第8页只保留学生与导师的签名、日期空栏。本人须在签名前确认原表的安全说明课出席声明属实；如学校另要求独立评估表，应按要求另交。

- [英文最终 PDF](Proposal_English_Final.pdf)
- [英文最终 Word（可编辑）](Proposal_English_Final.docx)
- [修改报告及待填写事项](Final_Revision_Report.md)
- [英文 Markdown 内容源](01_Proposal_Draft_EN.md)
- [进度 CSV](进度计划.csv)、[Week 日期对照](Week_Date_Mapping.csv)、[假期配置](假期配置.json)
- [甘特图 PNG](figures/gantt.png) / [PDF](figures/gantt.pdf)
- [实验与验收细则](03_实验与验收方案.md)
- [学校格式校验记录](数据核查/学校格式校验.json)

当前 PDF 为 8 页：学校封面、单栏项目描述及参考文献、横向甘特图与任务表、资源表、伦理/风险/安全与导师确认表。正文 Arial 10 磅，表格和参考文献 9 磅；沿用模板 A4 纸张、页边距和页码。Section 1 含章节标题、全部小标题及正文，按空白词元计 647，按英文字母/数字词规则计 678，均低于 750；参考文献仍为 6 篇。当前研究内容较示例详细，自然扩展为 8 页，不以缩小正文字号强制凑成 6 页。课程的最终报告七页限制不混用到 Proposal。

已确认的 Proposal DDL 为 2026-10-29（Week 8），封面已据此更新原模板的 Week 7；14:00 UK 沿用课程表格。Week 1 从 2026-09-07 开始，春节项目休息已按本人要求定为 2027-02-01 至 02-14，共两周，对应连续规划周 Week 22–23；后续跨学期课程周号仍待校历确认。总工时为提交前 372 + Viva 28 = 400 小时，这是项目预算口径，手册未明确 Viva 是否另计。

## 更新与重新导出

编辑 `01_Proposal_Draft_EN.md`、进度 CSV 和假期 JSON。当前生成入口是 `tools/build_form_proposal.py`；保留 `tools/build_documents.py`，因为新入口使用其中的共用路径与链接函数。

```bash
# 从工程根目录生成可编辑 Word
.venv/bin/python 开题材料/tools/build_form_proposal.py
# 同时导出 PDF（需 LibreOffice）
.venv/bin/python 开题材料/tools/build_form_proposal.py --renderer /usr/bin/soffice
```

本轮已重绘甘特图中的春节说明，总工时不变；生成器直接嵌入既有甘特图。若改动任务或假期，应先调用 `build_documents.make_schedule()` 重绘图表，再重建 Word/PDF。依赖见 `tools/requirements.txt`。本轮使用本地临时目录解包的 LibreOffice 7.3.7，未安装系统软件；PDF 嵌入 Arial 的兼容替代字体 Liberation Sans。仅生成 Word 不会更新 PDF；直接手改 Word 后再运行脚本会覆盖派生文件，应先同步源文件或另存修改版。

## 历史版本

旧 IEEE PDF/Word、生成脚本、校验记录及重复备份 ZIP 已从工作目录清理，统一由 Git 保存历史。它们均可从提交 `2acf6a0` 恢复；该提交中的 `开题材料/backups/2026-10-14_before_final.zip` 还保留更早的修订稿。当前目录只使用 `Proposal_English_Final.docx/pdf`。

中文对照 Markdown 和早期课程复核记录均为历史支撑材料，不是当前英文稿的同步译文；其中双栏、旧日期和旧工时说明以本入口及最新修改报告为准。学校原始模板与示例保持不变。

系统入口为 [project/qa_system](../project/qa_system/README.md)。三文档本地 BM25 及合成证据 DeepSeek 联调不等于正式性能评测；独立 Embedding、live dense/hybrid 和正式 100 题评估仍待开展。
