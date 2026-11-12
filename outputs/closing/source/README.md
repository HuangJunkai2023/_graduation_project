# 结题报告构建与检查

本目录保存2026年11月12日真实结题实验对应的可编辑报告及生成器。正文报告5页，合并审阅稿8页，当前状态为review-ready。报告约3537词，计数包含表格及参考文献。

## 输入与构建

在仓库根目录使用具备python-docx、lxml和pypdf的Python运行以下命令。本次使用Codex已加载的bundled Python环境。

```powershell
python outputs/closing/source/build_final_report.py `
  --summary project/qa_system/runtime/research/measured_results.json `
  --calibration project/qa_system/runtime/research/calibration/closing-v2/selected.json `
  --protocol outputs/research/PROTOCOL_ADJUSTMENT.md `
  --cases project/qa_system/runtime/research/cases_for_report.json
```

生成器沿用学校模板的Calibri 10 pt正文、Letter纸张、原页边距、两栏正文及16项LO表。DOCX包中仅替换word/document.xml，其他部件逐字节保留。身份信息采用正式题目、Junkai Huang、Leeds SID 201804121和Prof. Deqing Huang。未知Assessor及本人签字字段保留空白。

## 渲染与验证

使用documents Skill的render_docx.py分别渲染两个DOCX。本机LibreOffice路径为project/qa_system/runtime/tooling/libreoffice/program/soffice.exe，实际版本25.8.7.3。将其所在目录和bundled Poppler目录加入当前进程PATH后执行。

```powershell
python <documents-skill>/render_docx.py `
  outputs/closing/source/generated/OCS_Final_Report_EN.docx `
  --output_dir outputs/closing/source/generated/render-OCS_Final_Report_EN-v3 --emit_pdf

python <documents-skill>/render_docx.py `
  outputs/closing/source/generated/OCS_Submission_Review_Draft.docx `
  --output_dir outputs/closing/source/generated/render-OCS_Submission_Review_Draft-v3 --emit_pdf

python outputs/closing/source/validate_final_report.py
```

当前v3目录保存最终逐页PNG及渲染PDF。早期渲染保存在本机runtime/tooling/report-render-history中。验证器检查页数、模板部件差异、纸张和页边距、LO1–LO16、关键数值及正文限制说明，并复制最终PDF至generated目录。更改报告后必须重新渲染并逐页目检，原QA记录对应现存文件哈希。

## 审阅状态

Final_Report_QA.json记录已完成的13页最终目检和自动检查。技术报告从标题到参考文献5页，符合7页上限，表格均完整保持在单栏内。修复过程包括表格跨栏分裂、参考文献重复自动编号和表题换行。

报告明确记录assistant_source_review、独立人工验证缺失及正式版本对不足。结果采用冻结数据。Hybrid相对Dense有Recall@5改善，相对BM25未取得改善。RQ2与RQ3均未观测到增量收益。

合并稿包含原封面、个人学术声明、5页报告和真实Portfolio缺项页。本人录音、最终视频访问链接、实际Review Documents及认可记录、个人声明、Assessor信息和实际提交回执仍需真实完成。Portfolio_Evidence_Status.md保存已有Journal与监督记录核查情况。
