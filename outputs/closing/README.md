# 接触网问答项目结题交付包

2026 年 11 月 23 日提交前审阅版。以已签署的 Proposal 和 ELEC3801 要求为依据。学生为 Junkai Huang，导师为 Prof. Deqing Huang。

## 报告与答辩

| 文件 | 内容 |
| --- | --- |
| [英文技术报告 PDF](source/generated/OCS_Final_Report_EN.pdf)与[可编辑 Word](source/generated/OCS_Final_Report_EN.docx) | 学校模板 6 页，含系统流程、实测召回差值、扭矩仪案例、Reflection 和 16 项 LO 证据表。 |
| [学校审阅合并稿](source/generated/OCS_Submission_Review_Draft.pdf) | 9 页，包含封面、待签声明、技术报告和 Portfolio 证据状态。 |
| [英文 Viva PPTX](viva/OCS_Viva_EN.pptx)与[PDF](viva/OCS_Viva_EN.pdf) | 交大模板，15 页主讲、3 页备份，18 页中英对照备注。主讲约 7 分 16 秒。 |
| [Viva 中英讲稿](viva/OCS_Viva_CN_EN_Script.md)与[双语问答](viva/OCS_Viva_QA_CN_EN.md) | 讲稿与实际页码对应，问答覆盖方法、实测结果、失败案例和研究限制。 |
| [Viva 总览](viva/overview.png)和[报告总览](source/generated/render-OCS_Final_Report_EN-v4b/overview.png) | 所有页面已本机渲染检查。继承的模板字体仍需在目标电脑确认。 |
| [实测补充分析](Results_Supplement_EN.md) | 总体与分层结果、分母、覆盖率、延时、成对置信区间及计划目标对照。 |

报告与 PPT 构建源分别位于[source](source/)和[viva/source](viva/source/)。最终文件及 SHA-256 见[验收记录](DELIVERY_VALIDATION.json)和[交付清单](DELIVERY_MANIFEST.json)。

## 演示

- [4 分钟合成旁白审阅预览](video/OCS_Demo_EN_Synthetic_Voice_Preview.mp4)保留实际系统录屏，加入实测召回差值图与英文字幕。1280×720、30 fps、6.21 MB，已完整解码并在 Chrome 播放至结束。画面全程标注合成旁白。[播放及音轨回执](video/qa/synthetic-preview/validation.json)与[抽帧总览](video/qa/synthetic-preview/contact-sheet.png)
- [无旁白画面稿](video/OCS_Demo_EN_Visual_Draft.mp4)可用于接入本人录音。[中英对照讲稿](video/OCS_Demo_CN_EN_Script.md)与[英文字幕](video/OCS_Demo_EN.srt)
- 本人录音可保存于本机项目 runtime/closing_delivery 目录。构建脚本的 --narration 可接入配合讲稿时标的录音，最终音画与院系访问需在正式版本中复验。

## 系统、复现与结论

问答入口为 <http://127.0.0.1:8501>，核查入口为 <http://127.0.0.1:8502>。[工程说明](../../project/qa_system/README.md)

| 文件 | 核验 |
| --- | --- |
| [修订工程 ZIP](repro/OCS_Public_Code_submission-v2.zip)与[Windows 测试回执](repro/windows_recheck_receipt.json) | 新目录解压后确认加载归档源码，Windows 默认编码与 UTF-8 模式各通过 109 项测试。 |
| [复现说明](repro/REPRODUCIBILITY_EN.md)与[验证结果](repro/VALIDATION_RESULT_CN.md) | 受控快照恢复 25 份来源，核对冻结身份。按保存的首次输出与评分复算指标，结果完全一致，使用 0 次模型 API。受限原文、摘录和密钥保留于本机。 |
| [遮蔽复核](repro/SUBMISSION_RECHECK.md) | 24 道分层测试题的 48 条 B1/B3 输出，适用判断均与原评分一致。复核由同一助手工作流完成。 |
| [实测 JSON](../research/closing-experiment/measured_results.json)与[研究状态](../research/STATUS_CN.md) | 400 个正式首次槽位，296 个匿名输出元组评分，9 次恢复尝试单列。 |

Hybrid 的 Recall@5 为 95.3%，完整回答正确率为 89.1%。Hybrid 比 Dense 的 Recall@5 高 18.75 个百分点，BM25 在本基准的 Recall@5 为 96.9%，为当前语料的首选默认方案。版本过滤与 Evidence Gate 在本轮未观察到增量收益。题目事实集中于 6 份来源，缺少同系列正式版本对和独立人工评分验证。账户真实费用需按账单核对，跨电脑依赖与字体需按目标环境核验。

## 正式提交依赖

本机已有 6 份 Journal 草稿，10 份 Review Documents 的真实文档与认可依据仍待入库。正式包还需要 assessor 姓名、本人签署及演示音轨、学校账号可访问的 OneDrive 链接。实际发布、参加课程活动及提交回执按学校平台记录。[Portfolio 证据、缺项及本地组装](portfolio/Portfolio_Evidence_Status.md)
