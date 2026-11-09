# 五分钟开题答辩中英文对照逐字稿（背景加强版）

对应 `OCS_Proposal_Defense_EN_5min_SWJTU_Background.pptx`。第1–15页主讲，第16–20页备份。配时300秒；中文或英文择一讲述，实际时长需试讲。第4–5页背景与动机共85秒。

## 第1页：Title

预计 10 秒；累计 00:00

**中文**

各位老师好，我是黄俊凯，指导老师是黄德青教授。我的课题是基于大模型的接触网领域智能问答系统研究。下面用五分钟介绍研究方案。

**English**

Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. My project studies a large-model-based question-answering system for the Overhead Contact System field.

## 第2页：Contents

预计 5 秒；累计 00:10

**中文**

汇报分为背景动机、研究方法、实验评价，以及可行性与进度四部分。

**English**

I will cover motivation, research methods, evaluation, and feasibility.

## 第3页：Part 01: Background and Motivation

预计 2 秒；累计 00:15

**中文**

首先介绍研究动机。

**English**

First, the motivation.

## 第4页：Background: standards consultation

预计 45 秒；累计 00:17

**中文**

这张照片展示了铁路上方的接触网场景。围绕接触网部件开展学习和技术文档查询时，常常需要同时查找技术要求、试验方法和适用条件。这些信息可能分散在不同文件里，同一标准也可能存在不同版本。查询的难点因此不只是找到一句相关的话，而是确认它来自哪份文件、哪个版本，是否适用于当前问题。普通大模型即使表达流畅，也不一定能给出可核查的依据。本课题希望把文档检索与生成回答结合，让使用者能够从答案直接回到原文。本系统定位于学习与查询辅助，不用于铁路工程认证或实际运营决策。

**English**

This photograph shows the overhead-line setting above a railway. When learning about OCS components or consulting technical documents, users may need requirements, test methods, and applicability conditions from different files. A standard may also have several editions. Finding a relevant sentence is therefore only the beginning: users must establish which document and edition it comes from, and whether it applies to their question. A fluent model response does not necessarily provide that evidence. This project will connect retrieval with answer generation so users can follow an answer back to its source. Its scope is learning and consultation, not engineering certification or operational decisions.

## 第5页：Motivating example: an edition-specific query

预计 40 秒；累计 01:02

**中文**

以这一查询为例，用户问的是某个部件在指定版本下有哪些试验要求。本页仅为示意，不引用真实标准条款或数值。如果模型直接凭已有知识回答，可能引用另一版本，也可能给出没有来源的内容，这就是需要研究的问题。目标系统将先核对文档与版本，再寻找相关证据；能够回答时提供原文位置，版本缺失或证据不足时拒答或澄清。RAG的价值就在于让回答建立在可检查的文档上，而不是只看它说得是否像正确答案。但引入RAG本身不保证可靠，因此还需要后面的对照实验。

**English**

Consider this query about test requirements for a fitting in a requested edition. It is an illustration, not a quotation of real clauses or values. A model answering from its existing knowledge could use another edition or provide unsupported content. The proposed system will check the document and edition, retrieve evidence, and provide a source location when answering. If the edition is missing or evidence is insufficient, it will refuse or ask for clarification. RAG makes the document basis inspectable rather than relying on a fluent response. However, RAG alone does not guarantee reliability, so controlled experiments are still needed.

## 第6页：Part 02: Research Questions and Methods

预计 2 秒；累计 01:42

**中文**

下面介绍研究问题与方法。

**English**

Next, the research questions and methods.

## 第7页：Research aim and three questions

预计 30 秒；累计 01:44

**中文**

本研究围绕三个问题展开。RQ1：Hybrid能否比BM25和Dense提高证据召回；RQ2：版本过滤能否减少非指定版本答案；RQ3：Evidence Gate能否减少无依据回答，同时避免过度拒答。对应的是检索、版本控制和证据充分性三个层次。它们是拟验证的问题，不是已经证实的效果，也不涉及训练新的基础模型。

**English**

The study has three questions. RQ1 asks whether Hybrid improves evidence recall over BM25 and Dense. RQ2 asks whether edition filtering reduces answers from a non-requested edition. RQ3 asks whether an Evidence Gate reduces unsupported answers without excessive refusal. These address retrieval, edition control, and evidence sufficiency. They are questions to test, not established benefits, and the project does not train a new foundation model.

## 第8页：System architecture

预计 30 秒；累计 02:14

**中文**

技术路线可以概括为先找依据，再组织回答。计划解析许可使用的PDF和DOCX，分块并保存版本与来源位置。提问后限定标准系列和版本，再用BM25、Dense或Hybrid检索。Evidence Gate通过词项覆盖率或原始余弦相似度作启发式筛选；通过后交给DeepSeek生成回答，由Streamlit展示引用。Gate不能证明语义正确，数值、单位和适用条件仍需人工评分验证。

**English**

The workflow is to find evidence before generating an answer. We will parse licensed PDF and DOCX files, preserving edition metadata and source locations. Queries will be filtered by standard family and edition, then retrieved using BM25, Dense, or Hybrid. An Evidence Gate will screen passages using term coverage or raw cosine similarity. DeepSeek will generate an answer, and Streamlit will display citations. The gate is heuristic, not proof of semantic correctness; human scoring will check values, units, and applicability conditions.

## 第9页：Part 03: Evaluation Plan

预计 2 秒；累计 02:44

**中文**

下面说明实验评价。

**English**

Next, the evaluation plan.

## 第10页：Benchmark and controlled experiments

预计 45 秒；累计 02:46

**中文**

计划收集二十到三十份可用文档，尽可能覆盖两个标准系列，每个系列两个正式版本。人工校核一百道题：二十道开发题，其中十六道可回答、四道不可回答；八十道测试题，其中六十四道可回答、十六道不可回答。五组配置是B1 BM25、B2 Dense、B3 Hybrid，以及关闭版本检查的A1和关闭Gate的A2。A1仍保留标准系列过滤；A2仍保留提示词、引用校验和错误处理。测试前冻结数据和设置，计划执行八十乘五，共四百次。

**English**

We plan to collect twenty to thirty usable documents, ideally two standard families with two formal editions each. One hundred manually checked questions are split into twenty development questions, sixteen answerable and four unanswerable, and eighty test questions, sixty-four answerable and sixteen unanswerable. We compare B1 BM25, B2 Dense, B3 Hybrid, A1 without edition checks, and A2 without the gate. A1 retains family filtering; A2 retains prompts, citation validation, and error handling. Data and settings are frozen before the planned four hundred test runs.

## 第11页：Evaluation metrics and planned targets

预计 25 秒；累计 03:31

**中文**

评价同时检查检索和回答。Recall@5看前五条是否召回证据；Answer Correctness和Citation Support由人工判断；Wrong-edition Rate检查版本错误。Refusal Recall和False Refusal分别衡量该拒答时是否拒答，以及可回答时是否误拒。页面中的零点八、零点九等数值都是计划目标，没有现有测试结果支撑。

**English**

Recall at five evaluates evidence retrieval. Human scoring evaluates answer correctness and citation support. Wrong-edition rate measures edition errors. Refusal recall measures appropriate refusal, while false refusal measures rejected answerable questions. Values such as point eight and point nine are planned targets, not measured results.

## 第12页：Part 04: Feasibility and Schedule

预计 2 秒；累计 03:56

**中文**

最后介绍可行性与计划。

**English**

Finally, feasibility and the plan.

## 第13页：Feasibility and key risks

预计 20 秒；累计 03:58

**中文**

可行性上，计划采用现有RAG组件，并把范围限定在许可文档查询。主要风险是正式版本不足和Gate误判：前者必要时缩小RQ2范围，后者通过开发集与人工评估报告误接受和误拒答。这里不预设系统已经实现或达到目标。

**English**

The plan uses established RAG components within a bounded document-consultation task. The main risks are insufficient formal editions and gate errors. We will narrow RQ2 if necessary, and report false acceptance and refusal through development-set calibration and human evaluation. Implementation and target performance remain to be verified.

## 第14页：Schedule and expected outcomes

预计 32 秒；累计 04:18

**中文**

计划在Week 11完成语料准备，Week 16完成集成，Week 17冻结数据、提示词和模型设置，Week 20完成实验分析，Week 24提交。预期成果是问答系统、人工校核基准与实验报告。开发集用于选择Hybrid权重和Gate阈值，正式测试集不用于调参。所有效果都将以冻结配置后的评估为依据，不预先承诺达到目标。

**English**

The plan is corpus preparation by Week eleven, integration by Week sixteen, a freeze of data, prompts, and model settings in Week seventeen, experiment analysis by Week twenty, and submission in Week twenty-four. Outputs will be a QA system, a manually checked benchmark, and an experimental report. Hybrid weights and gate thresholds will be selected on the development set, not the test set. Performance will be established by evaluation after the configuration freeze, without assuming that targets will be met.

## 第15页：Conclusion and Q&A

预计 10 秒；累计 04:50

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
