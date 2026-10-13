# RAG 参考文献清单

> 本清单面向本科生毕业设计，围绕"检索增强生成（RAG）"由基础到进阶分类整理。
> 每条给出**出处 / 编号 / 一句话贡献 / 与本文的关联**，可直接用于论文的"相关技术/相关工作"章节。
>
> ⚠️ 提交前请用 Google Scholar / DBLP / arXiv 复核每条的 arXiv 编号与发表年份、会议。
> 本清单中的文献均为该领域公开的经典/高被引工作，可靠但版本信息仍建议自行核对一次。

---

## 一、RAG 起源与基础架构

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 1 | Lewis et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* | NeurIPS 2020, arXiv:2005.11401 | **首次提出 RAG**，把参数化记忆（生成模型）与非参数化记忆（向量检索）结合 | 全文的立论基础，绪论必引 |
| 2 | Guu et al. *REALM: Retrieval-Augmented Language Model Pre-Training* | ICML 2020, arXiv:2002.08909 | 在**预训练阶段**引入可学习的知识检索器 | 说明"检索何时介入"的两条技术路线 |
| 3 | Izacard & Grave. *Leveraging Passage Retrieval with Generative Models for ODQA* | EACL 2021, arXiv:2007.01282 | **Fusion-in-Decoder (FiD)**，多段证据融合生成 | 多来源上下文融合策略 |
| 4 | Borgeaud et al. *Improving LMs by Retrieving from Trillions of Tokens* | ICML 2022, arXiv:2112.04426 | **RETRO**，面向超大语料库的检索增强语言模型 | 大库检索架构参考 |
| 5 | Karpukhin et al. *Dense Passage Retrieval for Open-Domain QA* | EMNLP 2020, arXiv:2004.04906 | **DPR**，双塔稠密检索的开山之作 | 稠密向量检索的直接依据 |

---

## 二、稀疏检索 / BM25（本文检索的一大分支）

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 6 | Robertson & Walker. *Some simple effective approximations to the 2-Poisson model…* | SIGIR 1994 | **BM25 公式来源** | 本文 BM25 实现的公式依据 |
| 7 | Robertson & Zaragoza. *The Probabilistic Relevance Framework: BM25 and Beyond* | FnTIR 3(4):333–389, 2009 | BM25 系统化整理与变体 | BM25 参数（k1、b）取值的依据 |
| 8 | Trotman, Puurula & Burgess. *Improvements to BM25 and Language Models Examined* | ADCS 2014 | BM25 各变体对比实验 | 参数调优的参考 |
| 9 | Formal et al. *SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking* | SIGIR 2021, arXiv:2107.05720 | 稀疏扩展检索，兼顾关键词与语义 | 稀疏检索进阶方向 |

---

## 三、稠密检索与语义表示

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 10 | Reimers & Gurevych. *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks* | EMNLP 2019, arXiv:1908.10084 | **双塔句向量**，语义相似度计算范式 | 在线 embedding 的表示思想 |
| 11 | Khattab & Zaharia. *ColBERT: …Late Interaction over BERT* | SIGIR 2020, arXiv:2004.12832 | **后期交互**，兼顾效率与精度 | 检索与重排的折中方案 |
| 12 | Gao et al. *Precise Zero-Shot Dense Retrieval without Relevance Labels* | ACL 2023, arXiv:2212.10496 | **HyDE**：先生成假设文档再检索 | 查询增强的经典思路 |

---

## 四、混合检索与重排

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 13 | Nogueira & Cho. *Passage Re-ranking with BERT* | arXiv:1901.04085, 2019 | **交叉编码器重排（rerank）** | 本文"可扩展方向"：引入 reranker |
| 14 | Nogueira, Cho & Lin. *Document Ranking with a Pretrained Seq2Seq Model* | arXiv:2003.06713, 2020 | **monoT5** 重排 | 重排模型的另一种选择 |
| 15 | Cormack, Clarke & Buettcher. *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods* | SIGIR 2009 | **RRF**，多路检索结果融合的经典方法 | 本文"加权融合"的对照方案 |

---

## 五、向量索引与近似最近邻（ANN）搜索

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 16 | Malkov & Yashunin. *Efficient and robust ANN search using HNSW graphs* | IEEE TPAMI 2018, arXiv:1603.09320 | **HNSW** 图索引 | 大规模向量库的索引基础 |
| 17 | Johnson, Douze & Jégou. *Billion-scale similarity search with GPUs* | IEEE Trans. Big Data 2019, arXiv:1702.08734 | **FAISS** 向量检索库 | 工程选型参考 |
| 18 | Guo et al. *Accelerating Large-Scale Inference with Anisotropic Vector Quantization* | ICML 2020, arXiv:1908.10396 | **ScaNN** 量化检索 | 工程选型参考 |
| 19 | Wang et al. *Milvus: A Purpose-Built Vector Data Management System* | SIGMOD 2021 | 分布式向量数据库 **Milvus** | 与本项目《向量数据库选型与迁移调研》呼应 |

---

## 六、自适应 / 主动检索与自我反思

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 20 | Jiang et al. *Active Retrieval Augmented Generation* (FLARE) | EMNLP 2023, arXiv:2305.06983 | 生成过程中**按需触发检索** | "何时检索"的进阶方案 |
| 21 | Asai et al. *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* | ICLR 2024, arXiv:2310.11511 | 模型**自我反思**决定是否检索、答案是否可信 | 低置信度拦截的高级形态 |
| 22 | Shao et al. *Enhancing RAG with Iterative Retrieval-Generation Synergy* | EMNLP Findings 2023, arXiv:2305.15294 | **迭代式**检索-生成协同 | 多跳/多轮问答参考 |
| 23 | Ma et al. *Query Rewriting for Retrieval-Augmented Large Language Models* | EMNLP 2023, arXiv:2305.14283 | **改写再检索**（Rewrite-Retrieve-Read） | 本文短追问补全的思路来源 |

---

## 七、上下文组织与生成质量

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 24 | Liu et al. *Lost in the Middle: How Language Models Use Long Contexts* | TACL 2024, arXiv:2307.03172 | 长上下文中**中间位置信息易被忽略** | 解释"Top-K 证据排序"为何重要 |
| 25 | Shi et al. *Large Language Models Can Be Easily Distracted by Irrelevant Context* | ICML 2023, arXiv:2302.00093 | **无关上下文会显著降低准确率** | 支撑"低置信度拦截"设计 |
| 26 | Yu et al. *Generate rather than Retrieve: LLMs are Strong Context Generators* | ICLR 2023, arXiv:2209.10063 | **GenRead**，用生成替代检索 | 对照方案 |

---

## 八、评估与基准

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 27 | Es et al. *RAGAS: Automated Evaluation of Retrieval Augmented Generation* | EACL 2024 (Demo), arXiv:2309.15217 | **RAG 自动化评估指标**（忠实度、答案相关性等） | 本文实验评价指标来源 |
| 28 | Petroni et al. *KILT: a Benchmark for Knowledge Intensive Language Tasks* | NAACL 2021, arXiv:2009.02252 | 知识密集型任务统一基准 | 评测设计参考 |
| 29 | Tang & Yang. *MultiHop-RAG: Benchmarking RAG for Multi-Hop Queries* | arXiv:2401.15391, 2024 | **多跳**查询 RAG 基准 | 复杂问答评测 |
| 30 | Chen et al. *Benchmarking Large Language Models in Retrieval-Augmented Generation* | AAAI 2024, arXiv:2309.01431 | **RGB** 基准：噪声鲁棒性 / 拒答 / 信息整合 / 反事实 | 直接对应本文"低置信度不硬答"的评测 |

---

## 九、综述与中文/领域相关

| # | 文献 | 出处 | 贡献 | 与本文关联 |
| --- | --- | --- | --- | --- |
| 31 | Gao et al. *Retrieval-Augmented Generation for Large Language Models: A Survey* | arXiv:2312.10997, 2023 | **最常引用的 RAG 综述**（Naive/Advanced/Modular） | 综述章节首选 |
| 32 | Fan et al. *A Survey on RAG Meeting LLMs* | KDD 2024, arXiv:2405.06211 | RAG 与 LLM 结合的系统综述 | 相关工作补充 |
| 33 | Zhao et al. *A Survey of Large Language Models* | arXiv:2303.18223, 2023 | 大语言模型综述 | 背景章节 |
| 34 | Xiao et al. *C-Pack: Packed Resources For General Chinese Embeddings* | SIGIR 2024, arXiv:2309.07597 | **中文向量模型 BGE 系列** | 原项目 `BAAI/bge-small-zh` 的出处 |
| 35 | Du et al. *GLM: General Language Model Pretraining with Autoregressive Blank Infilling* | ACL 2022, arXiv:2103.10360 | **GLM 模型家族** | 本文所调用的在线模型家族 |
| 36 | Devlin et al. *BERT* | NAACL 2019, arXiv:1810.04805 | 双向预训练语言模型 | 语义表示基础 |
| 37 | Vaswani et al. *Attention Is All You Need* | NeurIPS 2017, arXiv:1706.03762 | **Transformer** | 一切现代模型的底座 |
| 38 | Brown et al. *Language Models are Few-Shot Learners* (GPT-3) | NeurIPS 2020, arXiv:2005.14165 | 大模型**提示学习/上下文学习** | 提示词工程的理论依据 |

---

## 十、工程文档与资料（非论文，但写系统实现时常用）

- 智谱开放平台 API 文档：https://open.bigmodel.cn/dev/api
- LangChain 文档（RecursiveCharacterTextSplitter、Retriever 抽象）：https://python.langchain.com/
- LlamaIndex 文档（RAG 全流程组件）：https://docs.llamaindex.ai/
- ChromaDB 文档：https://docs.trychroma.com/
- Milvus 文档：https://milvus.io/docs
- Anthropic, *Introducing Contextual Retrieval* (2024)：https://www.anthropic.com/news/contextual-retrieval
- Cohere, *Rerank* 文档：https://docs.cohere.com/docs/rerank-overview

---

## 十一、按论文结构的使用建议

| 论文章节 | 建议引用 |
| --- | --- |
| 绪论（研究背景与意义） | 1、31、29 |
| 相关技术综述 | 2、3、5、6、7、10、24、25、31、33 |
| 系统设计（检索模块） | 5、6、10、11、13、16、17、19 |
| 系统设计（生成模块） | 1、3、4、24、25、35、38 |
| 查询增强 / 多轮 | 12、20、21、22、23 |
| 实验与评测 | 27、28、29、30 |
| 中文语料与向量化 | 34、35 |
