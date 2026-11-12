# 基于大模型的接触网领域智能问答系统研究

English title: **A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field**

当前阶段：ELEC3801 2026–27，已完成开题答辩，按签署Proposal推进系统验证与受控实验。2026-11-12快照：25份研究来源、3341块与3341个1024维向量已就绪，100道候选题待人工核查，正式性能测试尚未开展。本人确认开题报告已于2026-10-26完成学生及导师审核签字。研究范围：规范文档问答、证据追溯、标准版本处理与实验评估；工程图纸理解列为后续扩展。

- [开题材料入口](开题材料/README.md)：英文学校表格式 Proposal（2026-10-16）、修改报告、Week X 甘特图与实验方案。
- [交大开题报告](开题材料/交大开题报告/README.md)：按老师意见补充研究论证、三张图示及正文两端对齐，冲突以附件九为准；可编辑Word及9页PDF（2026-11-04）。
- [Progress Journal 工作目录](docs/progress_journal/README.md)：Week 8 英文草稿、Weeks 8–24 研究计划、模板、证据及真实导师记录。
- [问答系统入口](project/qa_system/README.md)：本地界面、DeepSeek 配置、建库及实验命令。
- [完整研究执行入口](outputs/research/WORKFLOW_CN.md)：人工核查、开发校准、冻结、五组实验及评分汇总；[当前状态](outputs/research/STATUS_CN.md)。
- `@26-27新版资料/`：学校原始要求与模板。
- `毕设资料/`：提供的参考实现和技术资料，保留原貌。
- `project/task1/`：规范等领域资料；`project/task2/`：图纸资料。

已验证参考实现的离线自检。新系统已通过离线功能、模拟API测试，以及25份研究库上的真实BM25、Dense、Hybrid与DeepSeek带引用问答联调；这不代表人工判定的准确率。正式实验仍须题目及候选证据人工核查、开发集校准与冻结。验证范围见 [功能验证记录](project/qa_system/VERIFICATION.md)。初始资料核查见 [核查记录](开题材料/数据核查/核查记录.md)。
