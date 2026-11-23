# OCS Viva 中英文对照讲稿

主讲15页，预计7.3分钟。备份3页按提问使用。

## 第1页 Project viva

预计讲述18秒。

中文

各位老师好，我是黄俊凯，指导教师是黄德青教授。下面汇报接触网标准问答系统的实现、受控实验以及研究结论。

English

Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. I will present the implemented OCS standards assistant, its controlled evaluation and the conclusions supported by this study.

## 第2页 Contents

预计讲述10秒。

中文

汇报分为系统与范围、实验设计、结果与局限，以及结论四部分。

English

The presentation covers the system, the study design, the measured results and the conclusions.

## 第3页 System and scope

预计讲述4秒。

中文

首先介绍问题场景和已经实现的系统。

English

First, the problem context and the implemented system.

## 第4页 Standards consultation

预计讲述40秒。

中文

接触网部件的技术要求、试验方法和适用条件分散在标准文件中。查询时既要找到相关条文，也要保留用户指定的年份、数值和条件。系统面向资料学习与查询，使用者可以从答案返回原始文件位置。

English

Technical requirements, test methods and applicable conditions are distributed across OCS standards. A useful answer must retrieve the relevant evidence and preserve the requested edition, numerical values and conditions. The system supports learning and document consultation, with a route back to the original source.

## 第5页 Working interface

预计讲述42秒。

中文

这是真实运行的本地界面。用户选择检索方式后输入问题，系统展示带引用的回答、原文片段和文件位置。界面也展示缺失版本、证据不足或接口异常，便于区分返回状态。

English

This is the working local interface. The user selects a retriever and asks a question. The answer is accompanied by cited excerpts and source locations. Missing editions, insufficient evidence and interface errors have explicit return states, so the user can inspect what happened.

## 第6页 Study design

预计讲述4秒。

中文

下面介绍研究设计，以及怎样保证各组结果可以比较。

English

Next, the study design and the controlled comparisons.

## 第7页 System architecture

预计讲述45秒。

中文

文档解析时保留PDF文件页码或者DOCX段落位置，再建立词项和向量索引。查询经过标准系列与年份检查后检索候选，Evidence Gate根据启发式信号筛选，再交给DeepSeek生成结构化陈述。展示前验证引用编号与摘录，最后把答案和来源一起返回。

English

Parsing preserves PDF file pages or DOCX paragraph locations. The system builds lexical and dense indexes, applies standard-family and edition constraints, and retrieves candidate passages. The heuristic Evidence Gate filters evidence before DeepSeek generates structured claims. Citation identifiers and literal excerpts are validated before the answer and sources are displayed.

## 第8页 Benchmark and comparisons

预计讲述50秒。

中文

基准包含二十道开发题和八十道测试题，测试集有六十四道可答与十六道不可答题。五组配置保持相同语料和生成设置。A1只关闭版本检查，仍保留标准系列过滤；A2只关闭检索门槛，仍保留提示词、引用校验和错误处理。题目与输出由助手对照原文核查，报告保留这一评价方式的偏差限制。

English

The benchmark has twenty development and eighty held-out test questions. The test set contains sixty-four answerable and sixteen unanswerable items. Five configurations share the corpus and generation settings. A1 removes edition checks while keeping family filtering. A2 removes the retrieval gate while keeping the prompt, citation validation and error handling. Source review was performed by the assistant, and the report retains the resulting evaluation limitations.

## 第9页 Results and limitations

预计讲述4秒。

中文

接下来介绍冻结测试的实际观察。

English

I will now present the measured observations from the frozen test.

## 第10页 Measured results

预计讲述65秒。

中文

表中是五组配置的实际首次运行结果。Hybrid的Recall@5为95.3%，完整正确率为89.1%。引用支持、错版本与拒答指标需要结合分母共同解释。报告保留了相同题目的成对差值、按group_id重采样的区间和全部失败记录。

English

These are the measured first-attempt results for the five configurations. Hybrid achieved Recall at five of 95.3% and complete answer correctness of 89.1%. Citation support, edition errors and refusal measures must be interpreted with their denominators. The report retains paired differences, group-bootstrap intervals and all failed slots.

## 第11页 Failure analysis

预计讲述48秒。

中文

在test-041中，题目问扭矩仪精度。Dense找到了有出处的装配力矩公差，但对象不同。Hybrid命中PDF文件第10页的仪器精度要求，能沿出处回查。这个案例说明引用支撑与整题正确性需要分别判断。

English

In test-041, the question asked for torque instrument precision. Dense cited a documented tolerance for assembly torque. Hybrid found the instrument precision requirement on PDF file page ten. The source trace shows exactly where the two requirements diverge and why citation support and complete correctness are scored separately.

## 第12页 Conclusions and discussion

预计讲述4秒。

中文

最后总结研究问题、限制和项目成果。

English

Finally, the research questions, limitations and project outcomes.

## 第13页 RQ conclusions

预计讲述52秒。

中文

Hybrid比Dense的Recall@5高18.75个百分点。BM25在同一语料上的召回和正确率最高，因此建议在标准号或部件明确时优先选BM25。RQ2缺少真实正式版本对，各组都没有出现错版本。RQ3两组各有一条无支撑答案，拒答指标相同。零宽度区间反映当前样本的重采样结果。

English

Hybrid exceeded Dense by 18.75 percentage points on Recall at five. BM25 had the highest measured recall and correctness, supporting its use for queries with known standard numbers or terms. Version filtering showed no measured improvement and the corpus lacked verified formal edition pairs. With the gate on or off, one output was unsupported and refusal rates matched. The zero-width intervals reflect the observed sample.

## 第14页 Outcomes and limitations

预计讲述38秒。

中文

项目交付了本地系统、题集和冻结实验。遮蔽配置与原评分后，抽查二十四题共48条输出，48条的适用字段全部一致。两轮复核共享助手工作流。保存的首次输出和评分可以在本机离线复算。真实版本对和独立领域专家复核仍是后续工作。

English

The project delivers a local system, benchmark and frozen experiment. The masked review of twenty-four questions matched the original judgement on all applicable fields for 48 of 48 outputs. Both passes share the assistant workflow. Saved first attempts and grades allow offline recomputation. Independent domain review and verified edition pairs remain priorities.

## 第15页 Questions and discussion

预计讲述12秒。

中文

我的汇报到这里，谢谢各位老师，欢迎提问。

English

Thank you for your attention. I welcome your questions and discussion.

## 第16页 References

预计讲述0秒。

中文

此页列出主要参考文献。

English

This page lists the principal references.

## 第17页 Parameter details

预计讲述0秒。

中文

权重和门槛只使用开发集选择，词项覆盖率与原始余弦是启发式信号。

English

Weights and thresholds were selected on development data. Coverage and raw cosine are heuristic signals.

## 第18页 Metric definitions

预计讲述0秒。

中文

分母按预先定义保留。错误版本率同时包含请求版本已收录和缺失两类明确版本请求。

English

The predeclared denominators are retained. Wrong-edition rate includes unambiguous requests for both available and missing editions.
