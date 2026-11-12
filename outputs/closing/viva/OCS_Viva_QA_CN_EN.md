# OCS Viva 中英文问答

## 1. 为什么DeepSeek不能直接回答？

Why use retrieved evidence with DeepSeek?

技术标准查询需要核对具体版本、原文位置、数值和条件。检索把可检查的来源放进上下文，用户还能打开原文核查。

Standards queries require a specific edition, source location, numerical values and conditions. Retrieval supplies inspectable source passages, and the user can open the original document.

## 2. 为什么选择RAG？

Why was RAG selected?

研究目标是对许可资料进行可追溯查询。RAG可以把解析、索引、版本约束和来源展示连成可检查流程，适合本项目的数据与计算资源。

The aim is traceable consultation of permitted documents. RAG connects parsing, indexing, edition constraints and source display in an inspectable workflow suited to the available data and computing resources.

## 3. 项目的技术贡献是什么？

What is the technical contribution?

贡献集中在接触网标准场景的工程实现与受控评估，包括标准系列和年份处理、可定位的证据、启发式门控，以及五配置的比较记录。BM25、Dense与RAG沿用已有研究。

The contribution is the domain-specific implementation and controlled evaluation, including standard-family and year handling, source-located evidence, a heuristic gate and five recorded comparisons. BM25, dense retrieval and RAG build on established research.

## 4. BM25、Dense和Hybrid有什么区别？

How do BM25, Dense and Hybrid differ?

BM25按词项匹配排序，Dense按嵌入余弦相似度排序，Hybrid对候选分数归一化后加权融合。三者使用同一语料和版本约束，便于比较。

BM25 ranks lexical matches. Dense retrieval ranks embedding cosine similarity. Hybrid combines normalised scores using a selected weight. The comparison uses the same corpus and edition constraints.

## 5. 为什么Hybrid不一定更好？

Why can Hybrid fail to improve retrieval?

语义相似可能引入同主题但不支持问题的段落，归一化和权重也影响排序。效果需要按冻结题目和正确证据判断，并结合差值区间解释。

Semantic similarity can introduce passages on the same topic that do not support the question. Normalisation and weighting also change ranking. The frozen questions, evidence labels and paired intervals determine the observed effect.

## 6. Evidence Gate怎样工作？

How does the Evidence Gate work?

候选的词项覆盖率达到0.20，或者原始余弦达到0.50时通过。这些阈值仅用开发集选择，含义是启发式证据筛选。

A candidate passes when lexical coverage reaches 0.20 or raw cosine reaches 0.50. These development-selected thresholds provide heuristic evidence screening.

## 7. 门控能消除幻觉吗？

Can the gate eliminate unsupported answers?

启发式信号可能接受无关证据，也可能拒绝有效证据。因此评价同时保留无依据回答、拒答召回、误拒答和回答覆盖率，并逐条核查语义支持。

Heuristic signals can accept irrelevant evidence or reject useful evidence. Evaluation therefore includes unsupported answers, refusal recall, false refusal and answer coverage, alongside claim-level semantic review.

## 8. 怎样验证版本正确？

How is edition handling evaluated?

从文档元数据和请求中提取标准系列与年份。明确版本缺失时系统提前返回。A1关闭年份相关检查而保留系列过滤，再比较明确版本请求中的错版本行为。

The system extracts the standard family and year from metadata and the request. A missing explicit edition triggers an early return. A1 removes year-related checks while retaining family filtering, enabling a comparison on unambiguous edition requests.

## 9. 没有两个正式版本怎么办？

What follows from the missing formal edition pairs?

本次结论限定在选定语料中的已有版本和未收录年份请求。真实旧版与假设输入分别记录。扩展到多个正式版本之间的选择，需要补充可用文档并重新做冻结比较。

The conclusions cover available editions and unavailable-year requests in this corpus. Verified historical editions and hypothetical inputs are recorded separately. Evaluating selection between multiple formal editions requires additional usable documents and a repeated frozen comparison.

## 10. 100道题是否足够？

What can a 100-question benchmark establish?

这个规模支持本科项目的固定语料比较。测试集只有80题，题目事实集中在六份文档，因而报告保留分组重采样区间、分类样本数和覆盖限制。

The size supports a fixed-corpus undergraduate comparison. The test set contains eighty items and the question facts come from six documents. Group-bootstrap intervals, category counts and coverage limitations are therefore retained.

## 11. 五组实验怎样保证公平？

How are the five configurations controlled?

各组共享语料、分块、生成设置、Top-K和评分规则。A1保留系列过滤，A2保留提示词和引用校验。所有首次失败记录保留，恢复尝试独立登记。

The configurations share the corpus, chunks, generation settings, Top-K and scoring rules. A1 retains family filtering, and A2 retains prompts and citation validation. First-attempt failures remain recorded and recoveries have separate attempt identities.

## 12. 答案由谁评分？

Who reviewed the benchmark and answers?

按本次修订安排，由Codex助手对照原文核查，保存执行者、时间、方式和理由。题目由同一助手体系准备和评价，独立人工或领域专家验证仍是后续需要补充的工作。

Under the amended arrangement, the Codex assistant reviewed the original sources and retained the executor, time, method and reasoning. Benchmark preparation and evaluation used the same assistant system. Independent human or domain-expert validation remains further work.

## 13. 正式结果是什么？

What are the principal measured observations?

B3的Recall@5为95.3%，完整正确率为89.1%。B3与A1错版本率分别为0.0%和0.0%，解释时结合分母和成对区间。

B3 has Recall at five of 95.3% and complete answer correctness of 89.1%. Wrong-edition rates for B3 and A1 are 0.0% and 0.0%. Interpretation includes the denominators and paired intervals.

## 14. 怎样复现实验？

How can the experiment be reproduced?

使用冻结题集、语料和向量指纹、代码与环境记录，并保持相同模型设置。已保存首次输出和评分记录，可以离线重新计算指标，在线重新生成可能受到外部模型变化影响。

Use the frozen questions, corpus and vector fingerprints, code, environment and model settings. Saved first-attempt outputs and grades permit offline metric recomputation. New online generations can be affected by changes in the external model service.

## 15. Embedding接口不能使用怎么办？

What happens if the embedding service fails?

已保存的文档向量仍保留在本机，BM25可以继续查询。Dense与Hybrid需要当前模型的查询向量，接口失败会明确记录，重新恢复的运行有独立身份。

Stored document vectors remain local and BM25 remains available. Dense and Hybrid require query vectors from the configured model. Service failures are recorded explicitly and recovered runs retain separate identities.

## 16. 文档与外部API有哪些注意事项？

How are documents and external API processing handled?

项目使用已获准处理的本地资料，只有获准片段会发送至配置的服务。密钥与完整标准保存在本机受控目录，公开交付使用代码、方法和允许的来源信息。

The project uses local documents authorised for processing. Approved excerpts are sent to the configured services. Credentials and complete standards remain in controlled local storage, while public delivery uses code, methods and permitted source information.
