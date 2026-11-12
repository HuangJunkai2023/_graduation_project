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

这里展示已评分的test-041案例。判断时同时核对问题所需事实、答案陈述和整组引文。引用能够定位到原文后，还需要继续判断数值、单位、条件和版本是否真正支持答案。案例的具体失败依据保留在实验记录和报告中。

English

This slide follows scored case test-041 back to its source. The review considers the required facts, answer claims and the complete citation set together. Once an excerpt can be located, its numerical values, units, conditions and edition still require semantic checking. The case-specific reasoning is retained in the experiment record and report.

## 第12页 Conclusions and discussion

预计讲述4秒。

中文

最后总结研究问题、限制和项目成果。

English

Finally, the research questions, limitations and project outcomes.

## 第13页 RQ conclusions

预计讲述52秒。

中文

RQ1的观察是Hybrid超过Dense，BM25仍有最高的证据召回。RQ2中各组错版本均为零，因此本次比较没有证实版本过滤带来的改进，真实双版本资料不足也限制了结论。RQ3中完整Hybrid与关闭Gate配置的无依据回答和拒答率相同，本次没有观察到门槛的增量收益。差值和不确定性在报告中展开。

English

For RQ1, Hybrid exceeded Dense, while BM25 retained the highest observed evidence recall. For RQ2, all configurations had zero wrong-edition answers, so this comparison did not establish an improvement from edition filtering. Verified formal edition pairs were also unavailable. For RQ3, complete Hybrid and the Gate-off configuration had the same unsupported-answer and refusal rates. This test therefore showed no incremental benefit from the selected gate.

## 第14页 Outcomes and limitations

预计讲述38秒。

中文

项目交付了本地系统、题集、冻结实验和复现材料。目前同系列双正式版本不足，题目来源集中于六份文档，核查也由同一助手体系完成。这些因素限制了结论的推广。后续最有价值的工作是扩大独立核查和真实版本覆盖，再重复同样的受控比较。

English

The project delivers the local system, benchmark, frozen experiment and reproducibility material. Formal edition pairs are unavailable, the question facts come from six documents, and review was conducted within the same assistant system. These factors limit generalisation. The next useful step is independently checked coverage and verified edition pairs, followed by the same controlled comparison.

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
