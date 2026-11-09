# 五分钟开题答辩中英文对照逐字稿

对应 `OCS_Proposal_Defense_EN_5min_SWJTU.pptx`。第1–15页主讲，第16–20页备份。参考配时300秒；选择中文或英文讲述，不连续朗读两种语言。需通过试讲校准实际时长。

## 第1页：Title

预计 10 秒；累计 00:00

**中文**

各位老师好，我是黄俊凯，指导老师是黄德青教授。我的课题是基于大模型的接触网领域智能问答系统研究。下面用五分钟介绍研究方案。

**English**

Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. My project studies a large-model-based question-answering system for the Overhead Contact System field.

## 第2页：Contents

预计 6 秒；累计 00:10

**中文**

汇报分为背景动机、研究方法、实验评价，以及可行性与进度四部分。

**English**

I will cover motivation, research methods, evaluation, and feasibility.

## 第3页：Part 01: Background and Motivation

预计 3 秒；累计 00:16

**中文**

首先介绍研究动机。

**English**

First, the motivation.

## 第4页：Motivating example: an edition-specific query

预计 27 秒；累计 00:19

**中文**

接触网技术文档查询不仅要找到答案，还要核对标准版本并追溯原文。本页是示意案例，不代表真实标准条款。用户指定某一版本时，普通模型可能混用版本，也可能在没有证据时作答。RAG把文档检索接入生成过程，目标是返回指定版本的证据和位置；证据不足时明确拒答。

**English**

Standards consultation requires both an answer and its source edition. This is an illustrative example, not an actual standard clause. A model may mix editions or answer without evidence. RAG retrieves documents before generation. Our goal is to provide evidence from the requested edition, locate its source, and refuse when evidence is insufficient.

## 第5页：Part 02: Research Questions and Methods

预计 3 秒；累计 00:46

**中文**

下面介绍研究问题与方法。

**English**

Next, the research questions and methods.

## 第6页：Research aim and three questions

预计 36 秒；累计 00:49

**中文**

本项目不训练新的大模型，而是研究证据可追溯的RAG系统，服务技术文档学习和查询。三个问题分别是：RQ1，Hybrid是否比BM25和Dense提高证据召回；RQ2，版本过滤能否减少非指定版本答案；RQ3，Evidence Gate能否减少无依据回答，同时避免过度拒答。它们都需要通过实验验证，目前不是结论。

**English**

This project develops an evidence-traceable RAG system for document learning and consultation; it does not train a new foundation model. RQ1 asks whether Hybrid improves evidence recall over BM25 and Dense. RQ2 asks whether edition filtering reduces answers from a non-requested edition. RQ3 asks whether an Evidence Gate reduces unsupported answers without excessive refusal. These are research questions, not established conclusions.

## 第7页：System architecture

预计 38 秒；累计 01:25

**中文**

整体流程从许可使用的PDF和DOCX开始。解析分块时保存标准编号、版本和来源位置，再建立关键词与向量索引。用户提问后，先按标准系列和指定版本限定范围，再检索证据。BM25匹配关键词，Dense匹配语义，Hybrid组合归一化得分。证据通过Gate后交给DeepSeek组织回答，由Streamlit展示引用和原文位置；不通过则拒答。

**English**

The pipeline starts with licensed PDF and DOCX files. Parsing and chunking preserve the standard identifier, edition, and source location. We build keyword and vector indexes. A query is filtered by standard family and requested edition before retrieval. BM25 matches terms; Dense captures semantic similarity; Hybrid combines normalized scores. Evidence passing the gate is sent to DeepSeek, and Streamlit displays the answer with citations and source locations. Otherwise, the system refuses.

## 第8页：RQ2 and RQ3: two safeguards

预计 26 秒；累计 02:03

**中文**

这两个检查分别对应RQ2和RQ3。版本检查依据文档元数据，不让非指定版本进入回答证据。Evidence Gate使用词项覆盖率或原始余弦相似度阈值。它只是启发式筛选，不证明证据语义正确，也不能宣称消除幻觉。证据是否支持答案，以及数值、单位和适用条件是否正确，仍由人工评分。

**English**

Edition checks use document metadata to exclude evidence from an unrequested edition. The Evidence Gate uses term coverage or raw cosine-similarity thresholds. These are heuristic signals, not proof of semantic correctness or a guarantee against hallucination. Human scoring checks whether evidence supports the answer, including numerical values, units, and applicability conditions.

## 第9页：Part 03: Evaluation Plan

预计 3 秒；累计 02:29

**中文**

下面说明实验评价。

**English**

Next, the evaluation plan.

## 第10页：Benchmark and controlled experiments

预计 42 秒；累计 02:32

**中文**

计划收集二十到三十份可用文档，尽可能覆盖两个标准系列，每个系列两个正式版本。人工校核一百道题：二十道开发题，其中十六道可回答、四道不可回答；八十道测试题，其中六十四道可回答、十六道不可回答。五组配置是B1 BM25、B2 Dense、B3 Hybrid，以及关闭版本检查的A1和关闭Gate的A2。A1仍保留标准系列过滤；A2仍保留提示词、引用校验和错误处理。测试前冻结数据和设置，计划执行八十乘五，共四百次。

**English**

We plan to collect twenty to thirty usable documents, ideally two standard families with two formal editions each. One hundred manually checked questions are split into twenty development questions, sixteen answerable and four unanswerable, and eighty test questions, sixty-four answerable and sixteen unanswerable. We compare B1 BM25, B2 Dense, B3 Hybrid, A1 without edition checks, and A2 without the gate. A1 retains family filtering; A2 retains prompts, citation validation, and error handling. Data and settings are frozen before the planned four hundred test runs.

## 第11页：Evaluation metrics and planned targets

预计 28 秒；累计 03:14

**中文**

评价同时检查检索和回答。Recall@5看前五条是否召回证据；Answer Correctness和Citation Support由人工判断；Wrong-edition Rate检查版本错误。Refusal Recall和False Refusal分别衡量该拒答时是否拒答，以及可回答时是否误拒。页面中的零点八、零点九等数值都是计划目标，没有现有测试结果支撑。

**English**

Recall at five evaluates evidence retrieval. Human scoring evaluates answer correctness and citation support. Wrong-edition rate measures edition errors. Refusal recall measures appropriate refusal, while false refusal measures rejected answerable questions. Values such as point eight and point nine are planned targets, not measured results.

## 第12页：Part 04: Feasibility and Schedule

预计 3 秒；累计 03:42

**中文**

最后介绍进度与可行性。

**English**

Finally, progress and feasibility.

## 第13页：Preliminary progress and feasibility

预计 38 秒；累计 03:45

**中文**

根据十一月四日已记录快照，已有三文档BM25原型，记录五百零三个文本块、零个向量，并完成合成证据下的DeepSeek接口检查。实际Embedding访问、Dense和Hybrid效果，以及正式基准测试尚未确认完成。两个主要风险是正式版本不足，以及Gate误接受或误拒绝。前者必要时缩小RQ2结论范围；后者通过开发集选阈值、人工核查和消融实验评估，不能承诺消除。

**English**

The recorded November fourth snapshot contains a three-document BM25 prototype, five hundred and three chunks, and zero vectors. DeepSeek was checked using synthetic evidence. Live embedding access, Dense and Hybrid performance, and the formal benchmark remain unverified. The main risks are insufficient formal editions and incorrect gate acceptance or refusal. We will narrow the scope of RQ2 if editions are insufficient, and evaluate gate errors through development-set calibration, human review, and ablation experiments.

## 第14页：Schedule and expected outcomes

预计 28 秒；累计 04:23

**中文**

进度安排按正式开题报告推进：Week 11完成语料准备，Week 16完成系统集成，Week 17冻结评估设置，Week 20完成实验分析，Week 24完成提交。预期交付可编辑维护的问答原型、人工校核基准和实验报告。系统用于学习查询，不用于铁路工程认证或实际运营决策。

**English**

The proposal milestones are corpus preparation by Week eleven, integration by Week sixteen, evaluation freeze in Week seventeen, experiment analysis by Week twenty, and submission in Week twenty-four. Outputs are a maintainable prototype, a manually checked benchmark, and an experimental report. The system supports learning and consultation, not engineering certification or operational decisions.

## 第15页：Conclusion and Q&A

预计 9 秒；累计 04:51

**中文**

本研究的核心是让接触网文档问答有版本依据、有可追溯证据，并知道何时拒答。感谢各位老师，请批评指正。

**English**

The aim is traceable evidence, explicit edition control, and refusal when evidence is insufficient. Thank you. I welcome your questions.

## 第16页：Backup: full references

备份页，不计入主讲时长。

**中文**

备用页，不计入主讲时间。文献支撑方法设计，不能作为本项目达到性能目标的证据。参考文献沿用报告，不新增文献或跨领域性能推断。

**English**

Backup slide, outside the main presentation time. These references support the method design; they do not establish that this project has achieved its performance targets. The bibliography follows the proposal. No new literature or performance transfer across domains is claimed.

## 第17页：Backup: Hybrid scoring and selection

备份页，不计入主讲时长。

**中文**

备用页：B 和 D 对每个查询的 eligible chunks 分别作 min-max 归一化。常数正分数映射为一，其余常数映射为零。w 在 0.25、0.50、0.75 中按开发集 Recall@5 选择，再按 MRR@5，仍并列时优先 0.50。Top-K 固定为五。统一中文分词、小词典和停用词在测试前冻结，不使用测试结果调参。

**English**

Backup: normalise B and D separately using min-max scores over the eligible chunks for each query. Constant positive scores map to one; other constant scores map to zero. Select w from 0.25, 0.50 and 0.75 by development Recall@5, then MRR@5. If still tied, favour 0.50. Top-K remains five. Freeze consistent Chinese tokenisation, the domain dictionary and stopwords before testing. Do not use test outcomes for parameter selection.

## 第18页：Backup: Evidence Gate and human scoring

备份页，不计入主讲时长。

**中文**

备用页：coverage 使用统一分词后的不同内容词集合匹配，排除标准编号和冻结停用词；分母为空记零。coverage 或原始 cosine 高于各自开发集选定门槛即可接受。正式报告未给出数值阈值，因此不能将原型默认值描述为已优化参数。自动核对编号与摘录，人工判断证据语义支持、数值、单位和条件；API 错误与格式失败不算合理拒答。只有预标注的歧义题可以用澄清作为合理不作答。

**English**

Backup: lexical coverage matches distinct query content tokens using the same segmenter for passages. Exclude standard identifiers and frozen stopwords; an empty denominator scores zero. Accept if coverage or raw cosine exceeds its development-selected threshold. The formal proposal gives no numerical thresholds, so prototype defaults must not be described as tuned values. Automatically check identifiers and excerpts. Human scoring assesses semantic support, values, units and conditions. API and format failures are errors, not justified refusals. Clarification is justified only for items pre-labelled as ambiguous.

## 第19页：Backup: ablation contracts and denominators

备份页，不计入主讲时长。

**中文**

备用页：A1 只关闭年份限制以及版本可用性、歧义检查，仍保留系列过滤。A2 只关闭检索 Evidence Gate，保留提示词、引用校验和错误处理。检索与正确率、误拒答的分母是六十四道可回答题，合理拒答召回分母是十六道不可回答题；Wrong-edition Rate 分母含缺版的全部无歧义指定版次题。Citation Support 按 cited claims 计，并联合判断同一声明的引用。Unsupported-answer incidence 的分母是全部八十题，零分母记 N/A。

**English**

Backup: A1 disables only year restrictions and edition availability or ambiguity checks, while retaining standard-family filtering. A2 disables only the retrieval Evidence Gate, retaining prompts, citation validation and error handling. Retrieval, correctness and false refusal use all 64 answerable test items. Refusal recall uses 16 unanswerable items. Wrong-edition Rate uses all unambiguous edition requests, including missing editions. Citation Support uses cited claims, with each claim’s citations judged jointly. Unsupported-answer incidence uses all 80 test items. Report N/A for zero denominators.

## 第20页：Backup: data risks and fallback scope

备份页，不计入主讲时长。

**中文**

备用页：目标为二十至三十份许可使用的文档，尽可能取得两个系列、各两个正式版本。用哈希去重，用正文与元数据核对版本及位置；扫描件、草稿和不合格抽取不充数。若版对不足，保持 A1 并把 RQ2 限于可支持的案例。若 Embedding 不可用，记录失败、解决接口，保留本地检索作为有限交付；若换提供商，记录变更并统一重做受影响比较，不能混合有利输出。外发文本先核对许可，保护凭据与测试标签。Week 22–23 为计划休息，Week 25–27 准备 viva。

**English**

Backup: target 20–30 permitted documents and seek two standard families with two formal editions each. Deduplicate by hash and verify edition identity and source locations against document content and metadata. Do not count scans, drafts or failed extraction as usable editions. If edition pairs remain insufficient, retain A1 and limit RQ2 to supported cases. If Embedding access fails, record the failure and resolve access. Local retrieval remains a limited deliverable; it does not validate Dense, Hybrid or online QA. If a provider changes, document it and rerun all affected comparisons consistently rather than combining favourable outputs. Check permission before sending text externally, and protect credentials and test labels. Weeks 22–23 are a planned break; Weeks 25–27 cover viva preparation and examination.
