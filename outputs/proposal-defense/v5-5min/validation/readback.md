# OCS_Proposal_Defense_EN_5min_SWJTU

- Source: `OCS_Proposal_Defense_EN_5min_SWJTU.pptx`
- Total slides: 20

## Slide 1

![Slide 1 Image 1](readback_files/image4.png)

A Study on a Large-Model-Based Intelligent
Question-Answering System for the
Overhead Contact System Field

![Slide 1 Image 2](readback_files/image2.jpeg)

![Slide 1 Image 3](readback_files/image3.png)

Junkai Huang | Student ID: 2023115799
Supervisor: Prof. Deqing Huang

SWJTU-Leeds Joint School | Undergraduate Project Proposal Defense

### Speaker Notes

第1页 / Slide 1: Title

中文逐字稿

各位老师好，我是黄俊凯，指导老师是黄德青教授。我的课题是基于大模型的接触网领域智能问答系统研究。下面用五分钟介绍研究方案。

English Script

Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. My project studies a large-model-based question-answering system for the Overhead Contact System field.

## Slide 2

![Slide 2 Image 4](readback_files/image6.jpeg)

Contents

PRESENTATION OUTLINE

01 Background and Motivation

![Slide 2 Image 5](readback_files/image5.png)

02 Research Questions and Methods

03 Evaluation Plan

04 Feasibility and Schedule

### Speaker Notes

第2页 / Slide 2: Contents

中文逐字稿

汇报分为背景动机、研究方法、实验评价，以及可行性与进度四部分。

English Script

I will cover motivation, research methods, evaluation, and feasibility.

## Slide 3

PART

Background and
Motivation

01

![Slide 3 Image 6](readback_files/image7.jpeg)

Standards consultation
Illustrative query
Evidence-traceable RAG

### Speaker Notes

第3页 / Slide 3: Part 01: Background and Motivation

中文逐字稿

首先介绍研究动机。

English Script

First, the motivation.

## Slide 4

An edition-specific query

Which test requirements apply to fitting X in edition A?

Question

UNCHECKED ANSWER: POSSIBLE FAILURE

TARGET SYSTEM: CHECKED RESPONSE PATH

An edition-B requirement appears

without a traceable source.

Edition available + sufficient evidence

Answer with the document edition

and PDF page / DOCX location.

Illustrative failure scenario.

Not an observed model output.

Missing edition / weak evidence

Refuse explicitly. Clarify an ambiguous edition.

04 / 15

Design illustration only. Fictional Standard S, editions A/B and fitting X. No real clause or value.

### Speaker Notes

第4页 / Slide 4: Motivating example: an edition-specific query

中文逐字稿

接触网技术文档查询不仅要找到答案，还要核对标准版本并追溯原文。本页是示意案例，不代表真实标准条款。用户指定某一版本时，普通模型可能混用版本，也可能在没有证据时作答。RAG把文档检索接入生成过程，目标是返回指定版本的证据和位置；证据不足时明确拒答。

English Script

Standards consultation requires both an answer and its source edition. This is an illustrative example, not an actual standard clause. A model may mix editions or answer without evidence. RAG retrieves documents before generation. Our goal is to provide evidence from the requested edition, locate its source, and refuse when evidence is insufficient.

## Slide 5

PART

![Slide 5 Image 7](readback_files/image8.jpeg)

Research Questions
and Methods

02

Three research questions
System architecture
Retrieval and evidence checks

### Speaker Notes

第5页 / Slide 5: Part 02: Research Questions and Methods

中文逐字稿

下面介绍研究问题与方法。

English Script

Next, the research questions and methods.

## Slide 6

Research aim and questions

Aim: evidence-based QA for Chinese OCS standards

RQ1

Retrieval

BM25 / Dense / Hybrid

Does Hybrid retrieval improve evidence recall compared

with BM25-only and Dense-only retrieval?

RQ2

Standard editions

Identifier + edition filtering

Does edition filtering reduce answers using

a non-requested edition?

RQ3

Evidence sufficiency

Evidence Gate + refusal

Does an Evidence Gate reduce unsupported answers

without excessive refusal?

06 / 15

Proposal pp.4–5, §3. RQs are hypotheses to evaluate.

### Speaker Notes

第6页 / Slide 6: Research aim and three questions

中文逐字稿

本项目不训练新的大模型，而是研究证据可追溯的RAG系统，服务技术文档学习和查询。三个问题分别是：RQ1，Hybrid是否比BM25和Dense提高证据召回；RQ2，版本过滤能否减少非指定版本答案；RQ3，Evidence Gate能否减少无依据回答，同时避免过度拒答。它们都需要通过实验验证，目前不是结论。

English Script

This project develops an evidence-traceable RAG system for document learning and consultation; it does not train a new foundation model. RQ1 asks whether Hybrid improves evidence recall over BM25 and Dense. RQ2 asks whether edition filtering reduces answers from a non-requested edition. RQ3 asks whether an Evidence Gate reduces unsupported answers without excessive refusal. These are research questions, not established conclusions.

## Slide 7

System architecture

PDF / DOCX

Parse + chunk

Metadata

SQLite + indexes

Permitted documents

Units + locations

Identifier, year, hash

Eligible chunks

Rule-based follow-ups

Pass

Query

Retrieve

Evidence Gate

DeepSeek

Family + edition

3 retrieval modes

Coverage OR raw cosine

Citation / excerpt checks

Below thresholds

Missing / ambiguous edition

Refuse / clarify

Streamlit

Missing edition or weak evidence

Answer + source locations

PDF page / DOCX location

07 / 15

Proposal pp.5–7, §§4.1–4.4. Planned workflow. Only permitted text may leave the device.

### Speaker Notes

第7页 / Slide 7: System architecture

中文逐字稿

整体流程从许可使用的PDF和DOCX开始。解析分块时保存标准编号、版本和来源位置，再建立关键词与向量索引。用户提问后，先按标准系列和指定版本限定范围，再检索证据。BM25匹配关键词，Dense匹配语义，Hybrid组合归一化得分。证据通过Gate后交给DeepSeek组织回答，由Streamlit展示引用和原文位置；不通过则拒答。

English Script

The pipeline starts with licensed PDF and DOCX files. Parsing and chunking preserve the standard identifier, edition, and source location. We build keyword and vector indexes. A query is filtered by standard family and requested edition before retrieval. BM25 matches terms; Dense captures semantic similarity; Hybrid combines normalized scores. Evidence passing the gate is sent to DeepSeek, and Streamlit displays the answer with citations and source locations. Otherwise, the system refuses.

## Slide 8

RQ2 and RQ3: edition and evidence checks

RQ2 Standard editions

RQ3 Evidence sufficiency

Request edition A

Candidate passages

Only edition B is available

Below both evidence thresholds

Explicit refusal

Explicit refusal

No silent substitution of edition B

Avoid generating from weak context

Ambiguous editions require clarification.

Family filtering remains active in A1.

High scores can still lack semantic support.

Human scoring checks facts and conditions.

Measure both unsupported answers and false refusals

08 / 15

Proposal p.6, §§4.3–4.4. Illustrative scenarios, not standard clauses or observed outputs.

### Speaker Notes

第8页 / Slide 8: RQ2 and RQ3: two safeguards

中文逐字稿

这两个检查分别对应RQ2和RQ3。版本检查依据文档元数据，不让非指定版本进入回答证据。Evidence Gate使用词项覆盖率或原始余弦相似度阈值。它只是启发式筛选，不证明证据语义正确，也不能宣称消除幻觉。证据是否支持答案，以及数值、单位和适用条件是否正确，仍由人工评分。

English Script

Edition checks use document metadata to exclude evidence from an unrequested edition. The Evidence Gate uses term coverage or raw cosine-similarity thresholds. These are heuristic signals, not proof of semantic correctness or a guarantee against hallucination. Human scoring checks whether evidence supports the answer, including numerical values, units, and applicability conditions.

## Slide 9

PART

![Slide 9 Image 8](readback_files/image9.jpeg)

Evaluation Plan

03

Benchmark and data split
Five controlled configurations
Metrics and planned targets

### Speaker Notes

第9页 / Slide 9: Part 03: Evaluation Plan

中文逐字稿

下面说明实验评价。

English Script

Next, the evaluation plan.

## Slide 10

Benchmark and controlled experiments

100 manually checked questions

20 development

80 fixed test

16 answerable + 4 unanswerable

Select weights and thresholds

64 answerable + 16 unanswerable

Evaluate once under frozen settings

B1

B2

B3

A1

A2

BM25

Dense

Hybrid

Hybrid

No edition checks

Hybrid

Gate off

A1 retains family filtering. A2 retains prompts, citation checks and error handling.

80 × 5 = 400 main test executions after data and configuration freeze

10 / 15

Proposal pp.4–7, O3–O4 and §4.5. All counts are planned. Strict ablation definitions: backup B4.

### Speaker Notes

第10页 / Slide 10: Benchmark and controlled experiments

中文逐字稿

计划收集二十到三十份可用文档，尽可能覆盖两个标准系列，每个系列两个正式版本。人工校核一百道题：二十道开发题，其中十六道可回答、四道不可回答；八十道测试题，其中六十四道可回答、十六道不可回答。五组配置是B1 BM25、B2 Dense、B3 Hybrid，以及关闭版本检查的A1和关闭Gate的A2。A1仍保留标准系列过滤；A2仍保留提示词、引用校验和错误处理。测试前冻结数据和设置，计划执行八十乘五，共四百次。

English Script

We plan to collect twenty to thirty usable documents, ideally two standard families with two formal editions each. One hundred manually checked questions are split into twenty development questions, sixteen answerable and four unanswerable, and eighty test questions, sixty-four answerable and sixteen unanswerable. We compare B1 BM25, B2 Dense, B3 Hybrid, A1 without edition checks, and A2 without the gate. A1 retains family filtering; A2 retains prompts, citation validation, and error handling. Data and settings are frozen before the planned four hundred test runs.

## Slide 11

Evaluation metrics and planned targets

Recall@5

≥ 0.80

Wrong-edition Rate

B3 vs A1

64 answerable items, pre-gate rankings

All unambiguous edition requests, including missing editions

Answer Correctness

≥ 0.80

Refusal Recall

≥ 0.80

Fully correct answers / 64

Justified non-answering / 16

Citation Support

≥ 0.90

False Refusal

≤ 0.10

Supported cited claims / all cited claims

Refusals or unnecessary clarifications / 64

Planned targets only. Formal test results are pending.

11 / 15

Proposal pp.6–7, §4.5. Counts, coverage, paired differences, uncertainty and failures will be reported.

### Speaker Notes

第11页 / Slide 11: Evaluation metrics and planned targets

中文逐字稿

评价同时检查检索和回答。Recall@5看前五条是否召回证据；Answer Correctness和Citation Support由人工判断；Wrong-edition Rate检查版本错误。Refusal Recall和False Refusal分别衡量该拒答时是否拒答，以及可回答时是否误拒。页面中的零点八、零点九等数值都是计划目标，没有现有测试结果支撑。

English Script

Recall at five evaluates evidence retrieval. Human scoring evaluates answer correctness and citation support. Wrong-edition rate measures edition errors. Refusal recall measures appropriate refusal, while false refusal measures rejected answerable questions. Values such as point eight and point nine are planned targets, not measured results.

## Slide 12

PART

Feasibility
and Schedule

![Slide 12 Image 9](readback_files/image10.jpeg)

04

Recorded progress
Risks and fallback scope
Milestones and expected outputs

### Speaker Notes

第12页 / Slide 12: Part 04: Feasibility and Schedule

中文逐字稿

最后介绍进度与可行性。

English Script

Finally, progress and feasibility.

## Slide 13

Preliminary progress and feasibility

RECORDED BY 4 NOV 2026

TO BE VERIFIED

Three-document BM25 prototype

503 text chunks, 0 vectors

DeepSeek checks with synthetic evidence

Live Embedding access and model identity

Dense / Hybrid effectiveness

Formal benchmark and manual scoring

Risk 1: usable edition pairs

Risk 2: heuristic evidence signals

Seek permitted alternatives.

Limit RQ2 to available formal editions.

Heuristics can accept unsupported evidence.

Report errors and false refusals.

13 / 15

Sources: Week 9 evidence E09-03/E09-04, 4 Nov 2026. Proposal §4.6. Historical snapshot only.

### Speaker Notes

第13页 / Slide 13: Preliminary progress and feasibility

中文逐字稿

根据十一月四日已记录快照，已有三文档BM25原型，记录五百零三个文本块、零个向量，并完成合成证据下的DeepSeek接口检查。实际Embedding访问、Dense和Hybrid效果，以及正式基准测试尚未确认完成。两个主要风险是正式版本不足，以及Gate误接受或误拒绝。前者必要时缩小RQ2结论范围；后者通过开发集选阈值、人工核查和消融实验评估，不能承诺消除。

English Script

The recorded November fourth snapshot contains a three-document BM25 prototype, five hundred and three chunks, and zero vectors. DeepSeek was checked using synthetic evidence. Live embedding access, Dense and Hybrid performance, and the formal benchmark remain unverified. The main risks are insufficient formal editions and incorrect gate acceptance or refusal. We will narrow the scope of RQ2 if editions are insufficient, and evaluate gate errors through development-set calibration, human review, and ablation experiments.

## Slide 14

Schedule and expected outcomes

W9

W11

W13

W16

W17

W18

W20

W21

W24

Planned task

Corpus + baseline

Benchmark + checks

Integration

Configuration freeze

Evaluation

Report + video

Final checks / submit

M2 W11 M3 W16 M4 W17 M5 W20 M7 W24

Expected outputs

QA system

Checked benchmark

Experiment report

W18 Symposium. W22–23 planned break. Budget: 400 hours and GBP 50.

14 / 15

Proposal p.8 and task CSV. Planning weeks, not completed work or a confirmed institutional calendar.

### Speaker Notes

第14页 / Slide 14: Schedule and expected outcomes

中文逐字稿

进度安排按正式开题报告推进：Week 11完成语料准备，Week 16完成系统集成，Week 17冻结评估设置，Week 20完成实验分析，Week 24完成提交。预期交付可编辑维护的问答原型、人工校核基准和实验报告。系统用于学习查询，不用于铁路工程认证或实际运营决策。

English Script

The proposal milestones are corpus preparation by Week eleven, integration by Week sixteen, evaluation freeze in Week seventeen, experiment analysis by Week twenty, and submission in Week twenty-four. Outputs are a maintainable prototype, a manually checked benchmark, and an experimental report. The system supports learning and consultation, not engineering certification or operational decisions.

## Slide 15

![Slide 15 Image 10](readback_files/image4.png)

Thank you

![Slide 15 Image 11](readback_files/image2.jpeg)

![Slide 15 Image 12](readback_files/image3.png)

Traceable answers to standards queries
Edition checks and evidence-based refusal

Questions and discussion

### Speaker Notes

第15页 / Slide 15: Conclusion and Q&A

中文逐字稿

本研究的核心是让接触网文档问答有版本依据、有可追溯证据，并知道何时拒答。感谢各位老师，请批评指正。

English Script

The aim is traceable evidence, explicit edition control, and refusal when evidence is insufficient. Thank you. I welcome your questions.

## Slide 16

References

\[1\] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” Advances in Neural Information Processing Systems, vol.33, pp.9459–9474, 2020.

\[2\] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Foundations and Trends in Information Retrieval, vol.3, no.4, pp.333–389, 2009. doi: 10.1561/1500000019.

\[3\] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” EMNLP, pp.6769–6781, 2020. doi: 10.18653/v1/2020.emnlp-main.550.

\[4\] X. Ma, Y. Gong, P. He, H. Zhao, and N. Duan, “Query Rewriting in Retrieval-Augmented Large Language Models,” EMNLP, pp.5303–5315, 2023. doi: 10.18653/v1/2023.emnlp-main.322.

\[5\] F. Shi et al., “Large Language Models Can Be Easily Distracted by Irrelevant Context,” ICML, PMLR, vol.202, pp.31210–31227, 2023.

\[6\] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” EACL: System Demonstrations, pp.150–158, 2024. doi: 10.18653/v1/2024.eacl-demo.16.

\[7\] Z. Feng, K. Zhu, W. Ma, L. Huang, B. Qin, T. Liu, and X. Feng, “Enhancing Large Language Models with Retrieval-Augmented Techniques: Trends, Challenges, and Prospects,” 23rd Chinese National Conference on Computational Linguistics (Vol.2: Frontier Forum), pp.151–168, 2024 (in Chinese). https://aclanthology.org/2024.ccl-2.9/

B1 / 5

References reproduced from the supplied formal report, p.9. No new literature performance claims.

### Speaker Notes

第16页 / Slide 16: Backup: full references

中文逐字稿

备用页，不计入主讲时间。文献支撑方法设计，不能作为本项目达到性能目标的证据。参考文献沿用报告，不新增文献或跨领域性能推断。

English Script

Backup slide, outside the main presentation time. These references support the method design; they do not establish that this project has achieved its performance targets. The bibliography follows the proposal. No new literature or performance transfer across domains is claimed.

## Slide 17

Hybrid scoring and selection

S(q, c) = (1 - w)B(q, c) + wD(q, c)

Per-query normalisation

Constant-score rule

Min-max normalise BM25 and cosine scores

over eligible chunks for each query.

Constant positive scores map to 1.

Other constant scores map to 0.

w ∈ {0.25, 0.50, 0.75}

Select by development Recall@5, then MRR@5. Ties favour 0.50.

Freeze Chinese tokenisation, domain dictionary, stopwords, chunking,

corpus, models, prompts, thresholds and weight before testing.

B2 / 5

Proposal p.6, §4.2. Top-K = 5. No parameter selection on the test set.

### Speaker Notes

第17页 / Slide 17: Backup: Hybrid scoring and selection

中文逐字稿

备用页：B 和 D 对每个查询的 eligible chunks 分别作 min-max 归一化。常数正分数映射为一，其余常数映射为零。w 在 0.25、0.50、0.75 中按开发集 Recall@5 选择，再按 MRR@5，仍并列时优先 0.50。Top-K 固定为五。统一中文分词、小词典和停用词在测试前冻结，不使用测试结果调参。

English Script

Backup: normalise B and D separately using min-max scores over the eligible chunks for each query. Constant positive scores map to one; other constant scores map to zero. Select w from 0.25, 0.50 and 0.75 by development Recall@5, then MRR@5. If still tied, favour 0.50. Top-K remains five. Freeze consistent Chinese tokenisation, the domain dictionary and stopwords before testing. Do not use test outcomes for parameter selection.

## Slide 18

Evidence Gate and human scoring

Accept if coverage > τlex OR raw cosine > τcos

Coverage definition

Fixed preprocessing

Matched distinct query content tokens /

all distinct query content tokens.

Exclude IDs and fixed stopwords.

Same segmenter. Empty sets score 0.

Automatic checks

Human scoring

Metadata, citation identifiers

and literal excerpts.

Semantic support, facts, values,

units and applicable conditions.

No numerical threshold is claimed as tuned. Similarity is not semantic proof.

API/format failures are errors. Clarification is justified only for labelled ambiguity.

B3 / 5

Proposal pp.6–7, §§4.4–4.5. Numerical thresholds remain to be selected on development data.

### Speaker Notes

第18页 / Slide 18: Backup: Evidence Gate and human scoring

中文逐字稿

备用页：coverage 使用统一分词后的不同内容词集合匹配，排除标准编号和冻结停用词；分母为空记零。coverage 或原始 cosine 高于各自开发集选定门槛即可接受。正式报告未给出数值阈值，因此不能将原型默认值描述为已优化参数。自动核对编号与摘录，人工判断证据语义支持、数值、单位和条件；API 错误与格式失败不算合理拒答。只有预标注的歧义题可以用澄清作为合理不作答。

English Script

Backup: lexical coverage matches distinct query content tokens using the same segmenter for passages. Exclude standard identifiers and frozen stopwords; an empty denominator scores zero. Accept if coverage or raw cosine exceeds its development-selected threshold. The formal proposal gives no numerical thresholds, so prototype defaults must not be described as tuned values. Automatically check identifiers and excerpts. Human scoring assesses semantic support, values, units and conditions. API and format failures are errors, not justified refusals. Clarification is justified only for items pre-labelled as ambiguous.

## Slide 19

Ablation definitions and denominators

A1: remove edition checks

Disable year restrictions and edition availability/ambiguity checks.

Retain standard-family filtering.

A2: remove the retrieval gate

Retain prompts, citation validation and error handling.

This measures only the gate's incremental effect.

| Metric | Scoring population / denominator |
| --- | --- |
| Retrieval, correctness, false refusal | 64 answerable items. Retrieval uses pre-gate rankings. |
| Refusal recall / unsupported answers | 16 unanswerable / all 80 test items, respectively. |
| Wrong-edition rate | All unambiguous edition requests, including missing ones. |
| Citation support | All cited claims. Judge each claim's citations jointly. |

B4 / 5

Proposal pp.5–7 and readable ELEC3801 Proposal. Report citation/answer coverage. Zero denominators: N/A.

### Speaker Notes

第19页 / Slide 19: Backup: ablation contracts and denominators

中文逐字稿

备用页：A1 只关闭年份限制以及版本可用性、歧义检查，仍保留系列过滤。A2 只关闭检索 Evidence Gate，保留提示词、引用校验和错误处理。检索与正确率、误拒答的分母是六十四道可回答题，合理拒答召回分母是十六道不可回答题；Wrong-edition Rate 分母含缺版的全部无歧义指定版次题。Citation Support 按 cited claims 计，并联合判断同一声明的引用。Unsupported-answer incidence 的分母是全部八十题，零分母记 N/A。

English Script

Backup: A1 disables only year restrictions and edition availability or ambiguity checks, while retaining standard-family filtering. A2 disables only the retrieval Evidence Gate, retaining prompts, citation validation and error handling. Retrieval, correctness and false refusal use all 64 answerable test items. Refusal recall uses 16 unanswerable items. Wrong-edition Rate uses all unambiguous edition requests, including missing editions. Citation Support uses cited claims, with each claim’s citations judged jointly. Unsupported-answer incidence uses all 80 test items. Report N/A for zero denominators.

## Slide 20

Data risks and fallback scope

Corpus target: 20–30 usable documents

Seek 2 families × 2 formal editions. Verify provenance, permissions, hashes,

identifier/year, extraction quality and PDF/DOCX source locations.

Insufficient formal edition pairs

Embedding service unavailable

Seek permitted alternatives.

Keep A1 and limit RQ2 to available editions.

Resolve access or document replacement.

BM25 alone cannot validate Dense/Hybrid.

Rights and scope

Only permitted text goes online. Protect keys and test labels.

Exclude scans/drafts, training, OCR, agents, drawings, hardware and deployment.

Budget: GBP 35 generation + 10 embeddings + 5 reserve. Review at GBP 40.

372 h through W24 + 28 h viva. W22–23 break, W25–27 viva, subject to official notices.

B5 / 5

Proposal O1, §4.6 and schedule. Replacement-provider comparisons must use one consistent configuration.

### Speaker Notes

第20页 / Slide 20: Backup: data risks and fallback scope

中文逐字稿

备用页：目标为二十至三十份许可使用的文档，尽可能取得两个系列、各两个正式版本。用哈希去重，用正文与元数据核对版本及位置；扫描件、草稿和不合格抽取不充数。若版对不足，保持 A1 并把 RQ2 限于可支持的案例。若 Embedding 不可用，记录失败、解决接口，保留本地检索作为有限交付；若换提供商，记录变更并统一重做受影响比较，不能混合有利输出。外发文本先核对许可，保护凭据与测试标签。Week 22–23 为计划休息，Week 25–27 准备 viva。

English Script

Backup: target 20–30 permitted documents and seek two standard families with two formal editions each. Deduplicate by hash and verify edition identity and source locations against document content and metadata. Do not count scans, drafts or failed extraction as usable editions. If edition pairs remain insufficient, retain A1 and limit RQ2 to supported cases. If Embedding access fails, record the failure and resolve access. Local retrieval remains a limited deliverable; it does not validate Dense, Hybrid or online QA. If a provider changes, document it and rerun all affected comparisons consistently rather than combining favourable outputs. Check permission before sending text externally, and protect credentials and test labels. Weeks 22–23 are a planned break; Weeks 25–27 cover viva preparation and examination.
