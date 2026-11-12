# 接触网问答项目结题交付包

整理日期为2026年11月12日。研究依据为签署Proposal及ELEC3801要求，学生为Junkai Huang／黄俊凯，导师为Prof. Deqing Huang／黄德青。

系统、基准核查、开发校准、正式实验、结果分析和技术结题材料均已完成当前验收。学校认可及本人参与事项按下方实际缺项继续完成。

## 报告与答辩

| 文件 | 用途与状态 |
| --- | --- |
| [英文技术报告PDF](source/generated/OCS_Final_Report_EN.pdf)／[可编辑Word](source/generated/OCS_Final_Report_EN.docx) | 学校模板，标题至参考文献共5页，含Reflection与16项LO证据表；供本人及导师审阅 |
| [学校审阅合并稿](source/generated/OCS_Submission_Review_Draft.pdf) | 封面、待本人完成声明、5页报告、实际Portfolio缺项，共8页 |
| [英文Viva PPTX](viva/OCS_Viva_EN.pptx)／[PDF](viva/OCS_Viva_EN.pdf) | 交大模板，15页主讲、3页备份；每页中英对照备注，主讲约7分16秒 |
| [Viva中英讲稿](viva/OCS_Viva_CN_EN_Script.md)／[16组双语问答](viva/OCS_Viva_QA_CN_EN.md) | 与实际页码对应，覆盖方法、真实结果、失败案例和研究限制 |
| [PPT总览](viva/overview.png)／[逐页预览](viva/previews/) | 18页逐页检查完成；跨电脑字体可用性待目标电脑核验 |
| [实测补充分析](Results_Supplement_EN.md)／[实测图表](figures/) | 完整分母、类别结果、覆盖率、延迟、成对置信区间和计划目标对照 |

报告生成源在[source](source/)，PPT可编辑SVG、备注及构建源在[viva/source](viva/source/)。学校原模板保留在本机原位置。

[最终交付验收](DELIVERY_VALIDATION.json)记录实际页数、备注、实验及服务健康状态，[文件清单](DELIVERY_MANIFEST.json)保存本机交付文件的SHA-256。

## 演示视频

- [4分钟画面及字幕稿](video/OCS_Demo_EN_Visual_Draft.mp4)为实际系统录屏，1280×720、30fps、约4.7MB，已完整解码并播放至结束。
- [中英对照讲稿](video/OCS_Demo_CN_EN_Script.md)含469个英文词，[英文字幕](video/OCS_Demo_EN.srt)随画面提供。当前画面稿没有本人英文音轨。
- 请将本人录音保存到`project/qa_system/runtime/closing_delivery/student_narration.wav`或`.m4a`。构建脚本支持`--narration`接入录音，接入后需复核全片音画与时长。
- [视频验收回执](video/qa/validation.json)和[抽帧总览](video/qa/contact-sheet.png)对应当前画面稿的SHA-256。

## 系统与复现

本机问答入口为<http://127.0.0.1:8501>，核查入口为<http://127.0.0.1:8502>。启动命令及配置见[工程README](../../project/qa_system/README.md)。研究库包含25份文档、3341个文本块及向量，当前Hybrid采用开发集所选参数。

| 资料 | 验证情况 |
| --- | --- |
| [公开工程ZIP与回执](repro/) | 白名单源码、资源、测试、示例配置及启动脚本；实际解压后109项测试通过 |
| 本机受控研究ZIP | 位于`project/qa_system/runtime/closing_delivery/closing-v1/OCS_Controlled_Research.zip`；包含获许可来源、研究库、冻结及原始研究记录，继续仅本机保存 |
| [复现说明](repro/REPRODUCIBILITY_EN.md)／[验证结果](repro/VALIDATION_RESULT_CN.md) | 实际恢复来源、校验冻结并复算全部指标，结果完全一致，复算0次API调用 |
| [研究状态](../research/STATUS_CN.md)／[实测JSON](../research/closing-experiment/measured_results.json) | 400个首次槽位、296个匿名输出元组评分；9个恢复尝试独立汇总 |

复现验证使用既有Python 3.12.7环境。另一台电脑上的依赖安装、云端模型未来别名对应关系及字体显示仍需按目标环境核验。受限标准和密钥保留在本机。

## 研究结论与限制

Hybrid的Recall@5为95.3%，完整回答正确率为89.1%。它相对Dense提高召回18.75个百分点，BM25本轮召回为96.9%。版本过滤和Evidence Gate的增量收益在本轮未获观测支持。

100题及输出评分采用记录执行者和依据的助手原文核查，方法调整已在报告披露。独立人工／专家核查尚未开展，制题与评分共享助手工作流。题目事实集中于6份来源，未取得同系列正式版本对。结论范围限定于当前语料与基准。

账单前的历史项目费用仍未知。£35历史预留与£5.60剩余调用预留属于预算分配；已记录台账的聊天费用估算约USD 0.3491，实际费用需账户账单核对。

## 真实待办

1. 本人英文录音，接入视频后的最终播放检查及学校账号访问链接。
2. 10份Review Documents的真实资料及导师认可依据，现有3份本地Journal草稿的实际发布记录。
3. Symposium资料、assessor信息、本人声明、导师最终审阅及实际学校提交回执。

[Portfolio证据清单](portfolio/Portfolio_Evidence_Status.md)记录现有资料与缺项。已生成材料均保留其审阅或草稿状态，最终课程认可按真实记录完成喵~
