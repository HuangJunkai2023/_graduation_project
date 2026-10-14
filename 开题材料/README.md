# 接触网智能问答毕设：开题材料包

当前主文件为 2026-10-14 最终技术稿，适用 ELEC3801 2026–27。个人信息、真实声明及导师批准完成后方可正式提交。

- [英文最终 PDF](Proposal_IEEE_English_Final.pdf)
- [英文最终 Word（可编辑）](Proposal_IEEE_English_Final.docx)
- [修改报告及待确认事项](Final_Revision_Report.md)
- [英文 Markdown 内容源](01_Proposal_Draft_EN.md)
- [进度 CSV](进度计划.csv)、[Week 日期对照](Week_Date_Mapping.csv)、[假期配置](假期配置.json)
- [甘特图 PNG](figures/gantt.png) / [PDF](figures/gantt.pdf)
- [实验与验收细则](03_实验与验收方案.md)
- [最终版校验记录](数据核查/IEEE最终版校验.json)

按用户补充的课堂通知：Week 1 从 2026-09-07 开始，Proposal DDL 为 Week 8 的 2026-10-29 周四，使用英文 IEEE 双栏。原手册写 Week 7，差异及依据已在修改报告说明。14:00 UK 暂沿用课程要求，待核对具体作业通知。后续周号按连续周计算，跨学期是否停计仍待确认。春节两周工作休息预留调整为 Week 22–23（2027-02-01至02-14），不代表学校已批准假期。

最终 PDF 共 5 页，正文双栏，末页甘特图及具名任务表。Section I 含一级标题和全部小标题，按空白分词为 650，按英文字母/数字词规则为 681，均低于 750；6 篇参考文献。总工时为提交前 372 + Viva 28 = 400 小时，这是项目预算口径，手册未明确 Viva 工时是否另计。

## 版本和备份

当前目录仅保留 `_Final` 提交稿及其可编辑源文件。修订版和旧修改报告已归档至唯一保留的 [修改前备份](backups/2026-10-14_before_final.zip)，内含 34 个文件及哈希清单；原版也可从 Git 提交 `a7d6fae` 恢复。重复备份、旧版 PDF/Word 和旧版校验文件已清理。

中文对照 Markdown、课程复核记录属于历史支撑资料，未作为新版同步翻译；旧周号、工时及指标以 `Final_Revision_Report.md` 和当前英文源稿为准。旧表格式稿可从 Git 提交 `7f5f3ef` 恢复。

## 更新与重新导出

内容修改在 `01_Proposal_Draft_EN.md`；任务和假期修改在 CSV/JSON。当前生成入口为 `tools/build_ieee_proposal.py`，依赖 `tools/build_documents.py` 中的共用函数；不能删除后者。直接手改Word后再运行脚本会覆盖派生Word文件，应先同步源文件或另存手改版。

```bash
# 从工程根目录生成可编辑Word和甘特图
.venv/bin/python 开题材料/tools/build_ieee_proposal.py
# 具备LibreOffice时同时导出并检查PDF
.venv/bin/python 开题材料/tools/build_ieee_proposal.py --renderer /usr/bin/soffice
```

依赖见 `tools/requirements.txt`。脚本无需API Key、不调用模型；源表修改后须重建Word与PDF。仅重新生成Word不会更新PDF，不能把旧预览当作新版。本次用临时目录中的LibreOffice7.3.7导出，未安装系统软件；PDF中Calibri以嵌入的Carlito兼容替代。正式提交前在实际Word/WPS中核对字体、计数、签名和分页。

原始课程资料、参考实现和领域文件保持原貌；系统运行入口为 [project/qa_system](../project/qa_system/README.md)。三文档本地BM25及合成证据DeepSeek联调可行性不等于正式性能评测，独立Embedding、live dense/hybrid及正式100题评估仍待开展。
