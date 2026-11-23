# Portfolio 证据与缺项

核查日期为 2026 年 11 月 23 日。依据本地 Journal、导师记录和《ELEC3801 Handbook 2026–27》第 3.3、4 节。

| 证据 | 核查结果 |
| --- | --- |
| Week 8–10 Journal | 三份本地 Draft，覆盖开题、接口试验和文档入库。 |
| Week 11 Journal | 11 月 17 日整理，记录截至当日的语料校核与来源证据。 |
| Week 12–13 Journal | 11 月 17 日预先整理的本地 Draft，以截至当日的已有工作为依据。发布与后续活动待真实记录。 |
| 英文 Proposal 签署 | 本人确认学生与导师于 10 月 26 日完成审核签署。单独签署件及提交回执未入库。 |
| 中方开题审阅 | 11 月 4 日登记反馈和修订，本人确认导师已签署。实际会议和签署日期未供核验。 |
| Git 与研究材料 | 可追溯实测、实现及设计决定，可作为 Review Documents 的工程证据。 |

## 学校提交先决资料

| 事项 | 本机核查 |
| --- | --- |
| Review Documents 1–10 | 0 份具备可核查的实际文档及导师认可日期、方式。Proposal 和中方开题签署各有独立记录，编号文档仍待原始证据。 |
| Journal 发布与 Symposium | 现有六份本地草稿。Minerva 发布记录、Symposium 出席或反馈未入库。 |
| 封面和个人声明 | 学生及导师身份已填写。缺 assessor 姓名和本人签署声明。 |
| 演示视频 | 真实录屏、字幕及标注合成旁白的审阅预览已验证。缺本人英文录音、课程正式音轨适用性依据及学校账户可访问的 OneDrive 链接。 |
| 提交回执 | 缺实际学校提交回执。 |

[审阅合并稿](../source/generated/OCS_Submission_Review_Draft.pdf)保留封面、声明、报告和缺项页。[文件清单](Portfolio_Manifest.json)登记六份草稿和两个记录索引的 SHA-256。

## 本地组装

收到真实资料后，使用学校封面导出单页 PDF，填入实际 assessor、OneDrive 活动链接和十份批准信息。签署声明单独导出。用本地 JSON 记录 `assessor`、`access_confirmed_by`、`one_drive_url`、`cover_pdf`、`signed_declaration_pdf`、`technical_report_pdf`，可选 `supplement_pdf`。数组 `review_documents` 各项填写 `number`、`pdf`、`approval_date`（YYYY-MM-DD）和 `approval_method`。相对文件路径基于该 JSON 的目录。

```powershell
python outputs/closing/portfolio/assemble_submission.py <local-evidence.json> <final.pdf>
```

脚本检查页数、文档顺序、封面有效链接注解和输入记录完整性，输出单一 PDF 与哈希。签署和批准真实性沿用原始记录，学校账号访问按实际确认登记。
