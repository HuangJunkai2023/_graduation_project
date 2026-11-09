# 开题答辩逐字稿：中英文对照版

对应：`OCS_Proposal_Defense_EN_v3_SWJTU_Template.pptx`。第1–13页为主讲，第14–18页为备份。

中文沿用现有逐字稿，英文按同一含义改写为口述表达，技术缩写保留英文。每页按“中文—English”对照；现场选择一种语言讲述，不把两种语言连续读完。

中文原定时长为9分40秒（580秒）。英文正文约1141词，按每分钟120–140词估算约8.2–9.5分钟，尚需本人实际试讲校准。各页时间是原有节奏参考，不是双语合计时长或实测值。

研究目标、实验次数、性能阈值和未来里程碑均保留计划口径；已完成工作仍以2026年11月4日记录为界。本文件不修改PPT及原中文Speaker Notes。

## 第1页：封面 / Title

预计 25 秒；累计 00:00–00:25

**中文**

各位老师好，我是西南交通大学—利兹学院的黄俊凯，指导老师是黄德青教授。我的题目是“基于大模型的接触网领域智能问答系统研究”。本课题关注技术标准中的信息查询，希望回答能够追溯到正确版本和原文依据。下面我按照研究动机、技术方案、验证方法和可行性四个方面汇报。

**English**

Good morning, members of the panel. I am Junkai Huang from the SWJTU-Leeds Joint School, supervised by Professor Deqing Huang. My project is titled ‘A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field’. It focuses on standards queries, with answers traceable to the correct edition and source evidence. I will cover the motivation, method, evaluation and feasibility.

## 第2页：标准文档查询 / Standards consultation

预计 40 秒；累计 00:25–01:05

**中文**

接触网技术文档查询，不只是找到一个相关词。例如，学习者查到金具的技术要求后，可能还需要寻找相应试验方法，并确认使用的是哪个正式版本。左图仅说明接触网的真实场景，研究对象仍是文档中的信息。报告列举了 TB/T 2073-2020 和 TB/T 2074-2020 两类候选标准。关键词检索可能漏掉换一种说法的问题，而模型直接回答又可能遗漏单位、适用条件或版本信息。因此，我希望把文档检索与答案来源核对结合起来。系统用于学习和查询，不代替工程认证或运营决策。

**English**

Consulting overhead contact system documents involves more than finding a relevant term. After locating a fitting requirement, a learner may need its test method and formal edition. The photograph illustrates the physical context, while this study examines document information. The proposal identifies TB/T 2073-2020 and TB/T 2074-2020 as candidate standards. Keyword search may miss paraphrases, while direct model answers may omit units, conditions or editions. I therefore plan to combine retrieval with source checks. The system supports learning and consultation, not engineering approval or operational decisions.

## 第3页：指定版本的查询示例 / An edition-specific query

预计 50 秒；累计 01:05–01:55

**中文**

这里是一个完全示意的查询，不对应真实标准条款，也不是一次实际模型测试。假设用户问：在指定版本中，金具 X 适用哪些试验要求？如果只得到一个流畅答案，却不知道它来自哪个版本，就很难判断是否可用。目标系统首先核对标准系列和版本；如果版本可用，就检索依据，并给出文件页码或段落位置。如果请求的版本缺失，就明确拒答；如果证据不足以支持问题，也不能补写一个听起来合理的要求。这个例子说明，我要研究的是答案的证据链，而不仅是语言是否通顺。

**English**

This query is entirely illustrative. It is neither a real standard clause nor an observed model test. Suppose a user asks which test requirements apply to fitting X in a specified edition. A fluent answer is difficult to assess without knowing its edition. The proposed system first checks the standard family and edition. If available, it retrieves evidence and provides a file-page or paragraph location. If the edition is missing, it refuses. If evidence is insufficient, it must not invent a plausible requirement. The focus is the answer’s evidence chain, beyond linguistic fluency.

## 第4页：相关研究与研究切入点 / Related work and research gap

预计 35 秒；累计 01:55–02:30

**中文**

已有研究为方案提供了基础。RAG 将外部文档与生成结合，BM25 擅长精确词项匹配，Dense 检索则利用向量寻找语义接近的内容。证据相关性和 RAG 评价研究进一步提醒我们，检索相关不等于答案正确。本项目的研究切入点，是在接触网标准这个限定场景中，将检索、版本和证据充分性分开验证。这里没有声称该领域从未有人研究，也没有把文献中的结果当作本项目的效果。

**English**

Previous research provides the foundations. RAG combines external documents with generation. BM25 matches exact terms, while Dense retrieval uses vectors to find semantically similar content. Research on evidence relevance and RAG evaluation also shows why relevant retrieval does not establish answer correctness. This project will separately test retrieval, edition handling and evidence sufficiency within OCS standards. I am not claiming that this domain has never been studied, or treating published results as this project’s performance.

## 第5页：研究目标与问题 / Research aim and questions

预计 50 秒；累计 02:30–03:20

**中文**

研究目标是实现并评价一个证据可追溯的 RAG 问答系统。三个问题分别对应三个模块：RQ1 比较 BM25、Dense 和 Hybrid，检验混合检索是否提高证据召回；RQ2 检验版本过滤能否减少使用非请求版本的回答；RQ3 检验 Evidence Gate 能否减少无依据回答，同时避免过度拒答。它们都是待验证的问题，不能预先写成“Hybrid 一定更好”或“门控能够消除幻觉”。预期贡献主要是可追溯语料与题集、受控比较，以及对失败原因的分析。

**English**

The aim is to implement and evaluate a traceable RAG question-answering system. Three questions correspond to three modules. RQ1 compares BM25, Dense and Hybrid to test whether fusion improves evidence recall. RQ2 asks whether edition filtering reduces answers using a non-requested edition. RQ3 asks whether an Evidence Gate reduces unsupported answers without excessive refusal. These remain open questions: Hybrid is not assumed to perform better, and the gate cannot be assumed to eliminate hallucinations. The intended contributions are a traceable corpus and benchmark, controlled comparisons, and failure analysis.

## 第6页：系统架构 / System architecture

预计 65 秒；累计 03:20–04:25

**中文**

整体流程分为文档准备和在线查询。首先，对许可使用的 PDF、DOCX 做解析与分块，保存标准编号、年份、哈希和位置，再建立 SQLite 记录及检索索引。查询进入后，结合有限规则处理追问，并确定标准系列和版本约束。接着使用三种检索方式之一获得候选证据。Evidence Gate 根据词项覆盖率或原始余弦相似度进行筛选。通过后，才将获准发送的证据交给 DeepSeek，并进行引用编号和摘录检查；不通过则拒答。版本缺失或有歧义，也进入拒答或澄清分支。最后，Streamlit 展示回答及原文位置。自动检查主要保证结构与出处一致，语义支持仍需人工评价。

**English**

The workflow separates document preparation from online queries. Permitted PDFs and DOCX files will be parsed and chunked, retaining identifiers, years, hashes and source locations. SQLite records and retrieval indexes will then be built. Queries will use limited rules for follow-ups and establish family and edition constraints. One of the three retrieval methods will return candidate evidence. The Evidence Gate will screen it using lexical coverage or raw cosine similarity. Accepted evidence, where authorised for external processing, will go to DeepSeek, followed by citation-identifier and excerpt checks. Rejected evidence leads to refusal. Missing or ambiguous editions also trigger refusal or clarification. Finally, Streamlit will display the answer and source locations. Automatic checks address structure and provenance; semantic support still requires human assessment.

## 第7页：RQ1：混合检索 / RQ1: Hybrid retrieval

预计 40 秒；累计 04:25–05:05

**中文**

对同一个问题，BM25 侧重标准编号和专门术语的词项匹配；Dense 侧重换一种表达后的语义接近。Hybrid 将两类分数归一化后，按公式组合，尝试兼顾两种信号。它不一定优于单一方法：语义相近的段落可能并不包含需要的数值或条件，融合也可能改变原来正确的排序。因此三种方法使用相同语料、分块和问题，在 Top-K 等于五时比较。融合权重只用开发集选择，正式测试前冻结。

**English**

For the same question, BM25 emphasises standard identifiers and technical terms, while Dense retrieval addresses different wording through semantic similarity. Hybrid normalises and combines both scores. It may not outperform either method: a similar passage can omit necessary values or conditions, and fusion can disturb a correct ranking. All three methods will therefore share the corpus, chunks and questions, with Top-K fixed at five. The fusion weight will be selected only on development data and frozen before formal testing.

## 第8页：RQ2与RQ3：版本和证据检查 / RQ2 and RQ3: edition and evidence checks

预计 55 秒；累计 05:05–06:00

**中文**

这两条示意路径说明，版本正确与证据充分是不同的问题。左侧是 RQ2：即使某段话与问题高度相关，如果不是请求的版本，也不能默认替换；缺失版本要拒答，版本有歧义要澄清。右侧是 RQ3：候选证据低于两类门槛时，系统选择拒答。可是，覆盖率和相似度只是启发式信号，高分仍可能缺少关键条件，低分也可能误拒绝有效证据。因此门控不能证明语义正确，更不能保证消除幻觉。实验会同时考察无依据回答和错误拒答，人工再核对事实、数值、单位与适用条件。

**English**

These illustrative paths distinguish edition compatibility from evidence sufficiency. On the left, RQ2 prevents a relevant passage from silently replacing the requested edition. A missing edition requires refusal; ambiguity requires clarification. On the right, RQ3 refuses when evidence falls below both thresholds. However, coverage and similarity are heuristic signals. High scores can miss essential conditions, while low scores can reject valid evidence. The gate therefore cannot prove semantic correctness or guarantee the elimination of hallucinations. Evaluation will examine both unsupported answers and false refusals, with human checks of facts, values, units and conditions.

## 第9页：基准与受控实验 / Benchmark and controlled experiments

预计 65 秒；累计 06:00–07:05

**中文**

计划建立一百道人工校核题。二十道用于开发，其中十六道可回答、四道不可回答；八十道用于正式测试，其中六十四道可回答、十六道不可回答。题目记录原文证据、版本、事实和条件，相关事实或对话放在同一个划分中，避免泄漏。正式测试共有五组：B1 是 BM25，B2 是 Dense，B3 是 Hybrid；A1 在 Hybrid 上关闭版本检查，但保留标准系列过滤；A2 只关闭 Evidence Gate，保留提示词、引用校验和错误处理。所有组共享冻结的数据和生成设置，所以主要测试是八十乘五，四百次计划执行，而不是已经完成的结果。

**English**

The planned benchmark contains one hundred manually checked questions. Twenty are for development: sixteen answerable and four unanswerable. Eighty are for formal testing: sixty-four answerable and sixteen unanswerable. Records will include source evidence, editions, facts and conditions. Related facts or dialogues will stay within one split to prevent leakage. Five configurations will be tested: B1 uses BM25, B2 Dense, and B3 Hybrid. A1 disables edition checks in Hybrid but retains family filtering. A2 disables only the Evidence Gate, retaining prompts, citation validation and error handling. All groups share frozen data and generation settings. The main test therefore comprises eighty times five, or four hundred planned executions, not completed results.

## 第10页：评价指标与计划目标 / Evaluation metrics and planned targets

预计 55 秒；累计 07:05–08:00

**中文**

评价分为检索、回答与拒答。Recall@5 使用六十四道可回答测试题的门控前排名；Answer Correctness 只有完全正确才得分。Citation Support 判断被引用的声明是否得到证据支持，还要同时报告引用覆盖率。Wrong-edition Rate 统计非请求版本，并按版本是否可用分层，避免靠大量拒答掩盖问题。Refusal Recall 看不可回答题是否得到合理拒答，False Refusal 则惩罚可回答题上的拒答或不必要澄清。页面上的零点八、零点九和零点一全部是计划目标。API 或格式失败仍算错误，不能作为合理拒答；结果会同时报告计数、差异、覆盖率和不确定性。

**English**

Evaluation covers retrieval, answers and refusal. Recall at five uses pre-gate rankings for all sixty-four answerable test items. Answer Correctness credits only fully correct answers. Citation Support assesses whether cited claims are supported, alongside citation coverage. Wrong-edition Rate tracks non-requested editions and is stratified by availability, so excessive refusal cannot conceal the problem. Refusal Recall measures justified non-answering on unanswerable items; False Refusal penalises refusal or unnecessary clarification on answerable items. The displayed values of zero point eight, zero point nine and zero point one are planning targets. API and format failures remain errors, not justified refusals. Results will include counts, differences, coverage and uncertainty.

## 第11页：前期进度与可行性 / Preliminary progress and feasibility

预计 45 秒；累计 08:00–08:45

**中文**

当前只能作有限的可行性判断。依据十一月四日的记录，已有三文档 BM25 原型，数据库有五百零三个文本块、零个向量；DeepSeek 做过合成证据条件下的接口检查。这不等于真实标准问答通过。实际 Embedding 访问、Dense 和 Hybrid 效果，以及正式基准评测都还没有确认。接下来优先解决接口与语料许可，再按开发集完成验证。两个关键风险是正式版本对不足，以及门控误接受、误拒绝。前者可能限制 RQ2 的结论范围，后者需要通过对照实验和人工评分如实呈现。

**English**

Current evidence supports only limited feasibility. The fourth-of-November record shows a three-document BM25 prototype, five hundred and three chunks, and zero vectors. DeepSeek checks used synthetic evidence; they do not establish success on real standards queries. Live Embedding access, Dense and Hybrid effectiveness, and formal benchmark evaluation remain unconfirmed. Next, I will prioritise service access and corpus permissions, followed by development validation. Two key risks are insufficient formal edition pairs and incorrect gate decisions. The first may limit RQ2 conclusions; the second must be reported through controlled comparisons and human scoring.

## 第12页：进度与预期成果 / Schedule and expected outcomes

预计 40 秒；累计 08:45–09:25

**中文**

计划中，Week 11 完成语料与基线审核，Week 16 完成集成，Week 17 冻结题集和配置，Week 20 前完成受控评价，Week 24 完成最终检查和提交。测试必须先于结论与报告写作，尚未达到的里程碑不能按日期自动算完成。Week 18 还需参加 Symposium。预期交付包括可追溯的问答系统、人工校核基准，以及实验记录与报告。总预算仍为四百小时和五十英镑，后续具体日期与中方节点以正式通知为准。

**English**

The plan targets corpus and baseline review at Week eleven, integration at Week sixteen, configuration and benchmark freeze at Week seventeen, evaluation by Week twenty, and final checks and submission at Week twenty-four. Testing must precede conclusions and reporting; a milestone cannot count as complete simply because its date has arrived. The Week eighteen Symposium is also required. Expected outputs include the traceable QA system, a checked benchmark, experiment records and a report. The planned budget remains four hundred hours and fifty pounds. Later dates and Chinese-side checkpoints follow official notices.

## 第13页：致谢与问答 / Thank you / Q&A

预计 15 秒；累计 09:25–09:40

**中文**

本课题的核心，是让标准查询的答案能够核对版本、找到依据，并在证据不足时作出可评价的拒答。接下来我将通过固定基准和五组受控比较，检验各模块的作用与局限。我的汇报到此结束，谢谢各位老师，欢迎批评指正。

**English**

The core aim is to make standards answers traceable to the requested edition and supporting evidence, with measurable refusal when support is insufficient. A fixed benchmark and five controlled comparisons will test each module’s contribution and limitations. Thank you for listening. I welcome your questions and feedback.

## 备份页使用方式 / Using the backup slides

**中文**

第14页：完整参考文献；第15页：Hybrid公式与开发集选参；第16页：Evidence Gate及人工判分；第17页：消融契约和指标分母；第18页：资料、接口、许可与进度风险。按评委问题跳转，不在主讲时逐页讲解。

**English**

Slide 14 contains the full references. Slide 15 explains Hybrid scoring and development-only parameter selection. Slide 16 covers the Evidence Gate and human scoring. Slide 17 gives the strict ablation definitions and metric denominators. Slide 18 addresses data, service access, permissions and schedule risks. Use these slides in response to questions, rather than presenting them all during the main talk.
