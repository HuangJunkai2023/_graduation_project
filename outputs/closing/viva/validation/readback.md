# OCS_Viva_EN

- Source: `OCS_Viva_EN.pptx`
- Total slides: 18

## Slide 1

![Slide 1 Image 1](readback_files/image4.png)

A Study on a Large-Model-Based Intelligent
Question-Answering System for the
Overhead Contact System Field

![Slide 1 Image 2](readback_files/image2.jpeg)

![Slide 1 Image 3](readback_files/image3.png)

Junkai Huang | Leeds SID 201804121
SWJTU ID 2023115799 | Supervisor Prof. Deqing Huang

SWJTU-Leeds Joint School | Undergraduate Project Viva

### Speaker Notes

中文逐字稿

各位老师好，我是黄俊凯，指导教师是黄德青教授。下面汇报接触网标准问答系统的实现、受控实验以及研究结论。

English Script

Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. I will present the implemented OCS standards assistant, its controlled evaluation and the conclusions supported by this study.

## Slide 2

![Slide 2 Image 4](readback_files/image6.jpeg)

Contents

PRESENTATION OUTLINE

01 System and scope

![Slide 2 Image 5](readback_files/image5.png)

02 Study design

03 Results and limitations

04 Conclusions and discussion

### Speaker Notes

中文逐字稿

汇报分为系统与范围、实验设计、结果与局限，以及结论四部分。

English Script

The presentation covers the system, the study design, the measured results and the conclusions.

## Slide 3

PART

System and
scope

01

![Slide 3 Image 6](readback_files/image7.jpeg)

Standards consultation
Evidence and edition labels
Local working system

### Speaker Notes

中文逐字稿

首先介绍问题场景和已经实现的系统。

English Script

First, the problem context and the implemented system.

## Slide 4

Standards consultation

![D:\\_graduation_project\\outputs\\proposal-defense\\v2\\source\\assets\\overhead-lines-railway.jpg](readback_files/image8.jpg)

Find the requirement

Technical requirements and test methods

may appear in different documents.

Check the edition

The answer must preserve the requested

edition, units and applicable conditions.

Examples from the selected corpus

TB/T 2073-2020: fittings requirements

TB/T 2074-2020: test methods

For learning and consultation. Engineering approval and operational decisions remain outside scope.

Overhead-line context

04 / 15

Proposal pp.1–2. Photo: AlexHe34, Wikimedia Commons, CC BY-SA 3.0

### Speaker Notes

中文逐字稿

接触网部件的技术要求、试验方法和适用条件分散在标准文件中。查询时既要找到相关条文，也要保留用户指定的年份、数值和条件。系统面向资料学习与查询，使用者可以从答案返回原始文件位置。

English Script

Technical requirements, test methods and applicable conditions are distributed across OCS standards. A useful answer must retrieve the relevant evidence and preserve the requested edition, numerical values and conditions. The system supports learning and document consultation, with a route back to the original source.

## Slide 5

The implemented local interface

![Slide 5 Image 8](readback_files/image_fed2e90c698d5a2d.png)

Choose a

retriever

Inspect the

evidence

Open the

source page

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

这是真实运行的本地界面。用户选择检索方式后输入问题，系统展示带引用的回答、原文片段和文件位置。界面也展示缺失版本、证据不足或接口异常，便于区分返回状态。

English Script

This is the working local interface. The user selects a retriever and asks a question. The answer is accompanied by cited excerpts and source locations. Missing editions, insufficient evidence and interface errors have explicit return states, so the user can inspect what happened.

## Slide 6

PART

![Slide 6 Image 9](readback_files/image9.jpeg)

Study
design

02

Three research questions
Frozen data and configuration
Controlled comparisons

### Speaker Notes

中文逐字稿

下面介绍研究设计，以及怎样保证各组结果可以比较。

English Script

Next, the study design and the controlled comparisons.

## Slide 7

From source documents to traceable answers

PDF / DOCX

Chunks

Retrieval

→

→

Parse and locate

Metadata and indexes

BM25 / Dense / Hybrid

↓

Evidence Gate

DeepSeek

Streamlit

→

→

Coverage or cosine

Structured claims

Answer and sources

Family and edition filters precede ranking. Cited excerpts are checked before display.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

文档解析时保留PDF文件页码或者DOCX段落位置，再建立词项和向量索引。查询经过标准系列与年份检查后检索候选，Evidence Gate根据启发式信号筛选，再交给DeepSeek生成结构化陈述。展示前验证引用编号与摘录，最后把答案和来源一起返回。

English Script

Parsing preserves PDF file pages or DOCX paragraph locations. The system builds lexical and dense indexes, applies standard-family and edition constraints, and retrieves candidate passages. The heuristic Evidence Gate filters evidence before DeepSeek generates structured claims. Citation identifiers and literal excerpts are validated before the answer and sources are displayed.

## Slide 8

A fixed benchmark and five configurations

20 development questions

80 held-out test questions

16 answerable + 4 unanswerable

64 answerable + 16 unanswerable

Weight and threshold selection

80 × 5 = 400 primary slots

B1

B2

B3

A1

A2

BM25

Dense

Hybrid

Edition checks off

Gate off

25 source documents · 3341 chunks · BAAI/bge-m3 vectors

Two-pass assistant source review. Author and evaluator share the same assistant system.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

基准包含二十道开发题和八十道测试题，测试集有六十四道可答与十六道不可答题。五组配置保持相同语料和生成设置。A1只关闭版本检查，仍保留标准系列过滤；A2只关闭检索门槛，仍保留提示词、引用校验和错误处理。题目与输出由助手对照原文核查，报告保留这一评价方式的偏差限制。

English Script

The benchmark has twenty development and eighty held-out test questions. The test set contains sixty-four answerable and sixteen unanswerable items. Five configurations share the corpus and generation settings. A1 removes edition checks while keeping family filtering. A2 removes the retrieval gate while keeping the prompt, citation validation and error handling. Source review was performed by the assistant, and the report retains the resulting evaluation limitations.

## Slide 9

PART

![Slide 9 Image 10](readback_files/image10.jpeg)

Results and
limitations

03

Measured comparisons
Source-bound failure analysis
Uncertainty and study limits

### Speaker Notes

中文逐字稿

接下来介绍冻结测试的实际观察。

English Script

I will now present the measured observations from the frozen test.

## Slide 10

Measured test results across five configurations

B1

B2

B3

A1

A2

Recall@5

96.9%

76.6%

95.3%

95.3%

95.3%

Answer correctness

92.2%

70.3%

89.1%

90.6%

90.6%

Citation support

100.0%

98.1%

99.3%

99.3%

99.3%

Wrong-edition rate

0.0%

0.0%

0.0%

0.0%

0.0%

Refusal recall

87.5%

93.8%

87.5%

87.5%

87.5%

False refusal

0.0%

12.5%

0.0%

0.0%

0.0%

Measured first-attempt observations. Denominators and paired uncertainty are retained in the report.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

表中是五组配置的实际首次运行结果。Hybrid的Recall@5为95.3%，完整正确率为89.1%。引用支持、错版本与拒答指标需要结合分母共同解释。报告保留了相同题目的成对差值、按group_id重采样的区间和全部失败记录。

English Script

These are the measured first-attempt results for the five configurations. Hybrid achieved Recall at five of 95.3% and complete answer correctness of 89.1%. Citation support, edition errors and refusal measures must be interpreted with their denominators. The report retains paired differences, group-bootstrap intervals and all failed slots.

## Slide 11

Inspect the failure at its original source

Case test-041

Dense returned assembly torque tolerances of +/-1.0 and +/-1.5 N m around a

44 N m boundary. The question asked for the torque instrument precision,

which the original clause specifies as better than +/-3 percent. Hybrid

answered that requested fact correctly.

Source locations

TBT2074-2020 / PDF file page 10

TBT2074-2020 / PDF file page 9

TBT2074-2020 / PDF file page 6

Check required facts, cited evidence, units, conditions and requested edition together.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

这里展示已评分的test-041案例。判断时同时核对问题所需事实、答案陈述和整组引文。引用能够定位到原文后，还需要继续判断数值、单位、条件和版本是否真正支持答案。案例的具体失败依据保留在实验记录和报告中。

English Script

This slide follows scored case test-041 back to its source. The review considers the required facts, answer claims and the complete citation set together. Once an excerpt can be located, its numerical values, units, conditions and edition still require semantic checking. The case-specific reasoning is retained in the experiment record and report.

## Slide 12

PART

Conclusions and
discussion

![Slide 12 Image 11](readback_files/image11.jpeg)

04

Three research questions
Scope and limitations
Delivered system and evidence

### Speaker Notes

中文逐字稿

最后总结研究问题、限制和项目成果。

English Script

Finally, the research questions, limitations and project outcomes.

## Slide 13

Observed findings for the three questions

RQ1 Retrieval

Recall@5 B1 96.9% · B2 76.6% · B3 95.3%

Hybrid exceeded Dense. BM25 retained the highest observed recall.

RQ2 Editions

Wrong-edition rate B3 0.0% · A1 0.0%

No observed reduction in wrong editions in this limited comparison.

RQ3 Evidence Gate

Unsupported answers B3 1/80 · A2 1/80

The test showed the same unsupported-answer and refusal rates.

Interpretation is limited to this corpus, benchmark and assistant-reviewed scoring protocol.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

RQ1的观察是Hybrid超过Dense，BM25仍有最高的证据召回。RQ2中各组错版本均为零，因此本次比较没有证实版本过滤带来的改进，真实双版本资料不足也限制了结论。RQ3中完整Hybrid与关闭Gate配置的无依据回答和拒答率相同，本次没有观察到门槛的增量收益。差值和不确定性在报告中展开。

English Script

For RQ1, Hybrid exceeded Dense, while BM25 retained the highest observed evidence recall. For RQ2, all configurations had zero wrong-edition answers, so this comparison did not establish an improvement from edition filtering. Verified formal edition pairs were also unavailable. For RQ3, complete Hybrid and the Gate-off configuration had the same unsupported-answer and refusal rates. This test therefore showed no incremental benefit from the selected gate.

## Slide 14

Delivered outcomes and remaining limits

Delivered

Study limits

Working local QA system

No verified formal edition pairs

Source-reviewed 100-question benchmark

Benchmark facts drawn from six

Frozen five-configuration experiment

documents

Reproducible records and report

Shared assistant author and evaluator

Heuristic signals can accept or

reject incorrectly

Future work should add independently checked facts and verified edition pairs,

then repeat the frozen comparison under the same scoring definitions.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

项目交付了本地系统、题集、冻结实验和复现材料。目前同系列双正式版本不足，题目来源集中于六份文档，核查也由同一助手体系完成。这些因素限制了结论的推广。后续最有价值的工作是扩大独立核查和真实版本覆盖，再重复同样的受控比较。

English Script

The project delivers the local system, benchmark, frozen experiment and reproducibility material. Formal edition pairs are unavailable, the question facts come from six documents, and review was conducted within the same assistant system. These factors limit generalisation. The next useful step is independently checked coverage and verified edition pairs, followed by the same controlled comparison.

## Slide 15

![Slide 15 Image 12](readback_files/image4.png)

Thank you

![Slide 15 Image 13](readback_files/image2.jpeg)

![Slide 15 Image 14](readback_files/image3.png)

Evidence-traceable OCS standards consultation
Frozen comparisons and recorded findings

Questions and discussion

### Speaker Notes

中文逐字稿

我的汇报到这里，谢谢各位老师，欢迎提问。

English Script

Thank you for your attention. I welcome your questions and discussion.

## Slide 16

References

\[1\] Lewis et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020.

\[2\] Robertson and Zaragoza. The Probabilistic Relevance Framework. 2009. doi 10.1561/1500000019.

\[3\] Karpukhin et al. Dense Passage Retrieval. EMNLP, 2020. doi 10.18653/v1/2020.emnlp-main.550.

\[4\] Ma et al. Query Rewriting in Retrieval-Augmented Large Language Models. EMNLP, 2023.

\[5\] Shi et al. Large Language Models Can Be Easily Distracted by Irrelevant Context. ICML, 2023.

\[6\] Es et al. RAGAs. EACL Demonstrations, 2024. doi 10.18653/v1/2024.eacl-demo.16.

\[7\] Chen et al. BGE M3-Embedding. 2024. arXiv 2402.03216.

Primary literature and project source records

### Speaker Notes

中文逐字稿

此页列出主要参考文献。

English Script

This page lists the principal references.

## Slide 17

Frozen retrieval and Evidence Gate parameters

S(q,c) = (1 − w) B(q,c) + w D(q,c)

Selected w = 0.50

Query-wise min–max normalisation over eligible chunks

BM25 k1 = 1.5 and b = 0.75 · Top-K = 5

Gate accepts coverage ≥ 0.20 OR raw cosine ≥ 0.50

Shared jieba tokenisation and fixed domain dictionary

Standard identifiers and fixed stopwords excluded from coverage

Parameters selected on development data before the study freeze

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

权重和门槛只使用开发集选择，词项覆盖率与原始余弦是启发式信号。

English Script

Weights and thresholds were selected on development data. Coverage and raw cosine are heuristic signals.

## Slide 18

Scoring populations and ablation definitions

Recall and correctness

64 answerable questions

Refusal recall

16 unanswerable questions

False refusal

64 answerable questions

Citation support

Displayed cited claims

Wrong-edition rate

All unambiguous available or missing edition

requests

A1 keeps family filtering. A2 keeps prompts, citation validation and errors.

All first-attempt failures remain in their predeclared populations.

Frozen OCS study | Review against original sources

### Speaker Notes

中文逐字稿

分母按预先定义保留。错误版本率同时包含请求版本已收录和缺失两类明确版本请求。

English Script

The predeclared denominators are retained. Wrong-edition rate includes unambiguous requests for both available and missing editions.
