# 基于大模型的接触网领域智能问答系统研究

English title: **A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field**

当前阶段为ELEC3801 2026–27结题材料整理。2026-11-12已完成25份研究来源建库、100题两轮助手原文核查、100槽位开发联调、冻结后的400槽位正式实验及全部输出评分。Hybrid的Recall@5为61/64，完整正确回答为57/64。核查方法采用本人已授权的assistant_source_review，方法调整与评价限制随报告记录。本人确认英文Proposal于2026-10-26完成学生及导师审核签字。

- [开题材料入口](开题材料/README.md)：英文学校表格式 Proposal（2026-10-16）、修改报告、Week X 甘特图与实验方案。
- [交大开题报告](开题材料/交大开题报告/README.md)：按老师意见补充研究论证、三张图示及正文两端对齐，冲突以附件九为准；可编辑Word及9页PDF（2026-11-04）。
- [Progress Journal 工作目录](docs/progress_journal/README.md)：Week 8 英文草稿、Weeks 8–24 研究计划、模板、证据及真实导师记录。
- [问答系统入口](project/qa_system/README.md)：本地界面、DeepSeek 配置、建库及实验命令。
- [结题交付包](outputs/closing/README.md)包含5页英文报告、交大模板Viva、中英讲稿、实测图表、复现资料及4分钟演示画面稿。本人音频与真实Portfolio认可资料仍待补齐。
- [完整研究执行入口](outputs/research/WORKFLOW_CN.md)包含原文核查、开发校准、冻结、五组实验及评分汇总。[当前状态](outputs/research/STATUS_CN.md)与[实测结果](outputs/research/closing-experiment/measured_results.json)记录已完成工作。
- `@26-27新版资料/`：学校原始要求与模板。
- `毕设资料/`：提供的参考实现和技术资料，保留原貌。
- `project/task1/`：规范等领域资料；`project/task2/`：图纸资料。

公开工程包解压后的109项测试通过。受控研究包完成来源恢复、冻结校验和全部指标复算，复算结果与原汇总一致。实测Hybrid优于Dense的检索召回，BM25的召回更高。版本过滤与Evidence Gate在本轮比较中的增量收益未获观测支持。复现范围与回执见[复现验证](outputs/closing/repro/VALIDATION_RESULT_CN.md)，方法调整见[核查协议](outputs/research/PROTOCOL_ADJUSTMENT.md)。
