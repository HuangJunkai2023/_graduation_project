# OCS system demonstration script

The planned video length is four minutes. Record the English passages in order at a comfortable pace, with short pauses between sections. Save the student's narration as `project/qa_system/runtime/closing_delivery/student_narration.wav` or `.m4a`. The screen recording and subtitles follow the timings below.

## 00:00–00:25 Project and purpose

**English**

This demonstration presents Junkai Huang's Overhead Contact System standards project at the SWJTU Leeds Joint School. The application helps readers locate requirements and inspect the evidence behind an answer. It combines document retrieval, standard edition checks, and a heuristic Evidence Gate with DeepSeek generation.

**中文对照**

本演示介绍西南交通大学利兹学院黄俊凯的接触网标准问答项目。应用支持查找要求并检查答案所依据的证据，结合文档检索、标准版本检查、启发式Evidence Gate和DeepSeek生成。

## 00:25–00:50 Corpus

**English**

The knowledge base contains twenty five selected documents and three thousand three hundred and forty one text chunks. Each chunk retains its document identity, standard identifier, year, and original location. The vector index uses BGE M3 embeddings. Source files and numerical statements require careful checking because document extraction can lose conditions or split a clause.

**中文对照**

知识库包含25份选定文档和3341个文本块。每个文本块都保留文档身份、标准编号、年份和原始位置。向量索引采用BGE M3。文档抽取可能遗漏条件，或将条文拆开，因此需要仔细检查原文件和数值表述。

## 00:50–01:40 Retrieval and answering

**English**

Here I select Hybrid retrieval and enable answer generation. I ask about the surface quality of cast components in the twenty twenty edition of TB slash T twenty seventy three. BM25 matches terms and numbers, while Dense retrieval uses semantic similarity. Hybrid combines their normalised scores. Edition filtering restricts the requested standard and year. The Evidence Gate then screens the retrieved passages using lexical coverage or raw cosine similarity. DeepSeek receives the selected passages and returns structured factual claims with citations. These thresholds were selected using the development set before the study was frozen.

**中文对照**

这里选择Hybrid检索并启用答案生成。我查询TB/T 2073—2020中铸件表面质量的要求。BM25匹配词语和数字，Dense检索利用语义相似性，Hybrid将两者归一化后的得分融合。版本过滤限定请求的标准和年份。Evidence Gate随后根据词项覆盖率或原始余弦相似度筛选片段。DeepSeek依据选出的片段生成带引用的事实陈述。这些阈值在研究冻结前，仅使用开发集选择。

## 01:40–02:15 Inspecting evidence

**English**

I can expand a source to read the stored passage and its location. Opening the original PDF page lets the reader compare the answer with the document. The application checks citation identifiers and literal excerpts. Semantic support still requires source review, including numerical values, units and applicable conditions. A plausible answer can contain an omission even when its citation text exists.

**中文对照**

展开来源后，可以阅读保存的片段和位置。打开原始PDF页面，就能将答案与文档对照。应用会检查引用编号与逐字摘录。语义支持仍需回看原文，包括数值、单位和适用条件。即使引用文字确实存在，看起来合理的答案也可能有所遗漏。

## 02:15–02:45 Missing editions

**English**

Next, I ask about the twenty ten edition. This edition is absent from the selected knowledge base. The system reports the missing edition and identifies the available year. This example checks whether the requested document context is preserved during a follow up. The study currently has no verified same family pair of formal editions, which limits the conclusions that can be drawn about cross edition selection.

**中文对照**

接下来追问2010版。选定知识库没有收录这个版本，系统会说明版本缺失，并列出已收录年份。这个例子检查追问过程中是否保留所请求的文档上下文。目前研究没有取得同系列的双正式版本，因此跨版本选择能力的结论范围有限。

## 02:45–03:15 Insufficient evidence

**English**

I now clear the conversation and ask a weather question. The available standards do not provide the required evidence, so the application refuses to give a standards based answer. The Gate uses heuristic signals and can accept unsuitable evidence or reject useful evidence. Its effect therefore needs to be assessed together with answer coverage and false refusals.

**中文对照**

现在清空会话，输入一个天气问题。现有标准没有所需证据，应用会拒绝给出标准依据的答案。Gate采用启发式信号，可能接受不合适的证据，也可能拒绝有用证据，因此需要结合回答覆盖率和误拒答评价其效果。

## 03:15–03:25 Evaluation setup

**English**

The study uses twenty development and eighty test questions. Five configurations yield four hundred first attempts, including failures.

**中文对照**

研究使用20道开发题和80道测试题。五组配置共400个首次运行，包含失败结果。

## 03:25–04:00 Measured results and scope

**English**

The chart shows paired differences in recall at five. Hybrid exceeded Dense by eighteen point seven five percentage points. BM25 had the highest measured recall and complete correctness. The checks on edition and evidence showed no measured incremental benefit on these questions. Scoring and the masked recheck shared the assistant workflow. The system supports document consultation. Consult the original standard and seek qualified review for engineering decisions.

**中文对照**

这张图展示Recall@5的配对差值。Hybrid比Dense高18.75个百分点，BM25的实测召回和完整正确率最高。版本检查与证据门控在本次题集上未测得额外收益。评分和遮蔽复核共享助手工作流。系统用于资料查询，实际工程决策需核对原始标准并由有资质的人员审核。
