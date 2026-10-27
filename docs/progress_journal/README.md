# ELEC3801 Progress Journal

项目：A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field。学生：Junkai Huang（黄俊凯，201804121）；导师：Deqing Huang（黄德青）。

本目录从 **2026-10-27，Week 8** 开始维护。Journal 是随研究推进形成的 CPD 记录；已有代码为验证对象，不能据代码存在与否推定研究目标已完成，也不能把过去的实现改写为未来某周首次实现。

## 依据与优先级

1. 本人确认已于 **2026-10-26** 完成学生、导师签署的 Project Proposal，尤其是 Gantt、Table 1、O1–O5 和 RQ1–RQ3。
2. [How to Keep Your Progress Journal](../../@26-27新版资料/5.Progress%20Journal%20Guides_ELEC3801_How_to_Keep_Your_Progress_Journal.docx)：第1–3节规定记录频率与真实性，第4节规定内容，第6节说明 Portfolio 对应关系。
3. [ELEC3801 Handbook](../../@26-27新版资料/1.Handbook_ELEC3801_Handbook_2026-27.docx)：Section 3、Table V 及 Appendix 2 的 Professional Conduct 评分要求。
4. 本周实际代码、测试输出、实验记录、研究笔记、Git 与本人提供的事实。

仓库可读的 [Proposal PDF](../../开题材料/Proposal_English_Final.pdf) 与[内容源](../../开题材料/01_Proposal_Draft_EN.md)用于核对方案；本次未找到单独的已签字扫描件，本地 PDF 的签名栏仍为空。**审核签字日期依据本人本次确认，不声称已检查到签字图像或收到提交回执。** 如签字稿内容与本地稿不同，以签字稿为准，在计划中记录差异，不擅自修改已签署方案。证据来源见 [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md)。

Proposal 截止为课堂确认的 **Week 8，2026-10-29，14:00 UK**，优先于手册旧 Week 7。Week 8 覆盖10月26日至11月1日；当前草稿仅记录截至10月27日的事实。后续采用课程周号，跨学期日期不从连续周算术推导为正式校历。春节项目休息按 Proposal 保留2027年2月1日至14日（规划 Week 22–23）。

## 学校要求与本项目写法

| 项目 | 执行方式 |
| --- | --- |
| 每周记录 | Week 5–24，考试周除外；清楚命名 `Progress – Week X`。本目录不补造 Weeks 5–7 的历史日志；已有真实记录可按原日期索引。 |
| substantial progress | 说明技术活动、观察、处理办法、选择理由、反思及下一步。300–500英文词是本项目建议长度，不是课程硬性字数。没有活动时如实记录并处理进度问题。 |
| 七段结构 | Objectives；Technical Progress；Problems and Approaches；Engineering Decisions；Reflection；Plan for Next Week；Evidence。第一篇简述项目目标，后续聚焦当周。 |
| 写作语言 | 第一人称英文、英国工程项目风格。Proposal 正文采用第三人称的约定不套用到反思日志。学生须核对、理解并改成自己的表述，按课程要求如实说明 AI 辅助。 |
| 证据呈现 | 在 Minerva 正文直接放文字、表格、清晰小图和图注；不只贴路径或附 Word/PDF。每项关键结论有方法、观察和来源，注意资料许可及文件大小限制。 |
| 会后摘要 | 每次真实导师会议后记录讨论、反馈和带负责人/期限的行动；不因 Proposal 签字而自动认定一次正式会议。 |
| Review Documents | 10份、每份最多2页：会议记录、一张总结 slide、两次会议间的 Journal 反思摘要。第 n 次会议后准备第 n 份，至少提前1天通过 Teams 分享给第 n+1 次会议。第10份仍须于 Week 24 截止前分享并获得认可。 |
| Portfolio | 按时间顺序收齐10份 Review Documents，放在最终报告之后；实际分享、认可日期与方式另记。Professional Conduct/Portfolio 占20%，其中进展和监督参与、Portfolio 各占该部分50%。 |
| 休息周 | 计划休息不自动豁免 Journal、会议或 Review 义务。Weeks 22–23 如实记录实际活动或无活动及计划影响，不虚构技术进展。 |
| 最终交付 | Week 18 compulsory Symposium；Week 24报告、Portfolio及≤5分钟视频；Weeks 25–27 Viva。最终报告用学校 IEEE 双栏模板、技术正文至最后参考文献最多7页，含反思及16项 LO 证据表。 |

## 文件入口

- [WEEKLY_PLAN.md](WEEKLY_PLAN.md)：Weeks 8–24 的验证、实验、写作安排，含并行任务与里程碑。
- [WEEKLY_TEMPLATE.md](WEEKLY_TEMPLATE.md)：每周草稿与当周事实采集结构。
- [WEEK_08.md](WEEK_08.md)：当前 `Draft`，Minerva 可复制正文位于 `# Progress – Week 8` 至文末；含标题、小标题和证据表共424英文词，不计本地维护元数据。
- [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md)：证据、发生时间、支持范围及后续实际工作登记方式。
- [SUPERVISION_LOG.md](SUPERVISION_LOG.md)：真实审核/会议记录、后续行动及 Review Document 索引。

## 每周维护流程

**周初**：读取 Proposal 当周任务及 [周计划](WEEKLY_PLAN.md)，核对上周未完成事项和现有验证；选定本周实际要回答的问题、方法、完成标准和证据。计划采用将来时，不生成未来周的完成日志。

**进行中**：当日把活动日期、本人/工具分别完成的内容、命令与配置、输入范围、实际输出、失败原因、技术决定及证据路径追加到证据索引。确实计时才登记实际工时；计划工时不复制成实耗。API 调用在当周验证任务开展时执行，模型与费用以届时账户/接口事实为准。保护密钥及受限文档。

**周末**：只汇总本次时间窗口内且未在上一条 Journal 计入的工作；将旧验证标为背景。对照 Gantt、RQ 和实际结果撰写七段正文，核对每个过去时、数字和会议陈述。没有运行记录就不写“测试通过”；没有正式评估就不写指标提升。参数仅开发集选择，固定测试集不能用来改参数。

**发布**：新条目始终 `Draft`。本人确认正文并实际在自己的 Minerva 账号发布后，提供发布事实/日期，再将状态改为 `Published`、登记实际发布日期；单纯确认草稿可用时记为 `Approved for posting`。本地生成和 Git 提交均不等于 Minerva 已发布。本轮没有自动发布、发送 Teams 或提交 Git。

周内可以更新尚未发布的当前草稿，明确 `recorded_through`；已发布条目的补充以新的实际日期记录，不改写原来事实，不倒签。没有过去日志时从现在如实开始，不生成貌似当时提交过的历史条目。

## 以后每周可重复使用的指令

> 生成 Week X Journal：按已签字 Proposal 和 docs/progress_journal 的周计划，核对本周实际工作与证据，更新证据及真实导师记录，写300–500词第一人称英文草稿和下周计划；不把旧实现算成本周成果，不虚构缺失结果，保留 Draft，等我确认发布。

周初也可使用：“开始 Week X：读取对应 Proposal 任务，给出本周验证清单、完成标准和需要保留的证据；先不写完成日志。”
