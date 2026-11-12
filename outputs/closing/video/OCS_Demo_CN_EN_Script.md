# OCS system demonstration script

The planned video length is four minutes. Record the English passages in order at a comfortable pace, with short pauses between sections. Save the student's narration as `project/qa_system/runtime/closing_delivery/student_narration.wav` or `.m4a`. The screen recording and subtitles follow the timings below.

## 00:00–00:25 Project and purpose

**English**

Hello, I am Junkai Huang from the SWJTU Leeds Joint School. My project investigates question answering for Overhead Contact System standards. The application helps readers locate requirements and inspect the evidence behind an answer. It combines document retrieval, standard edition checks, and a heuristic Evidence Gate with DeepSeek generation.

**中文对照**

大家好，我是西南交通大学—利兹学院的黄俊凯。我的项目研究接触网标准领域的问答。这个应用帮助读者查找要求，并检查答案所依据的证据。系统将文档检索、标准版本检查、启发式Evidence Gate与DeepSeek生成结合起来。

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

## 03:15–04:00 Evaluation and scope

**English**

The evaluation uses twenty development questions and eighty held out test questions. Five configurations compare BM25, Dense and Hybrid retrieval, then remove edition checks or the Evidence Gate individually. The primary experiment contains four hundred first attempt slots, with failures retained. Source reviews and scoring follow the documented assistant review protocol. The report presents measured results, uncertainty and failure cases, including the limitations of this evaluation method. The system supports technical document learning and consultation. Readers must verify the original documents before practical engineering use. Thank you.

**中文对照**

评价使用20道开发题和80道保留测试题。五组配置比较BM25、Dense与Hybrid检索，再分别关闭版本检查或Evidence Gate。主要实验包含400个首次运行槽位，并保留失败结果。来源核查和评分采用已记录的助手核查方案。报告呈现实测结果、不确定性、失败案例，以及该评价方式的局限。系统用于技术文档学习和查询，实际工程使用前需要核实原文件。谢谢。
