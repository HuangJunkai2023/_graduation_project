# A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field

Junkai Huang · SID 201804121 · Supervisor Prof. Deqing Huang

Abstract — This project develops a traceable retrieval-augmented question-answering system for Chinese overhead contact system standards. The local collection contains 25 documents and 3341 text chunks. A 100-question benchmark uses 20 development and 80 test questions. BM25, Dense and Hybrid retrieval are compared with edition-filter and Evidence Gate ablations across 400 primary test slots. Hybrid obtains Recall@5 of 95.3%, answer correctness of 89.1% and citation support of 99.3%. Its false-refusal rate is 0.0%. All figures retain the predeclared denominators and first-attempt failures. The assistant reviewed references, passages and outputs against sources, revising the planned human-annotation procedure. Formal edition pairs were unavailable, so the edition study concerns available and missing requested editions. The measurements support a bounded assessment of evidence recall, source traceability and refusal trade-offs within this corpus.

Index Terms — Evidence assessment, hybrid retrieval, overhead contact systems, question answering, retrieval-augmented generation, standards.

## I. Introduction

Railway overhead contact systems (OCS) depend on technical requirements distributed across standards for components, interfaces, inspection and construction. A useful document query must identify the relevant provision and preserve its numerical value, unit, qualification and edition. A fluent explanation can still be unsuitable when it combines requirements from different documents or omits the condition under which a value applies. The engineering problem addressed here is therefore the traceability of a retrieved answer within a selected document collection.

Retrieval-augmented generation (RAG) combines an external evidence collection with language generation [1]. BM25 supplies a lexical baseline weighted by matching terms [2]. Dense retrieval represents query and passage meaning in a vector space [3]. Their rankings can differ for component names, identifiers, paraphrases and conditions. Combining scores is a testable choice whose benefit depends on the corpus and questions.

Query rewriting can help express an information need [4]. This project uses rules for topic inheritance in simple follow-ups. Distractor studies motivate testing evidence sufficiency [5]. RAGAs separates retrieval and answer assessment [6]. Here, correctness and semantic support are assessed against source documents through a recorded assistant review procedure.

The project develops an OCS document-learning and consultation system around DeepSeek generation, BAAI/bge-m3 embeddings, external application programming interfaces (APIs) and a local Streamlit interface. Its research contribution is a controlled comparison of retrieval, edition constraints and a heuristic Evidence Gate within an auditable pipeline. The research questions are whether Hybrid improves evidence recall over BM25 and Dense, whether edition filtering reduces answers based on a non-requested edition, and whether the Evidence Gate reduces unsupported answers while maintaining acceptable refusal behaviour.

## II. System Design and Implementation

### A. Corpus and evidence provenance

The study collection contains 25 independently numbered documents and 3341 text chunks. Source hashes, standard identifiers, years and file locations accompany each document. Eleven documents are individually numbered parts extracted from a bound collection. Their original page ranges and offsets are recorded, and their derived pages were compared with the corresponding parent pages. This permits a citation in a derived file to be traced back to the source collection. The count follows independently numbered document identities.

PDF documents are parsed by file-page and DOCX material by paragraph or table row. The chunking setting is 600 characters with an 80-character overlap, while local source units are retained in the stored provenance. Exact file hashing prevents duplicate imports. Scanned, unusable or draft-like material was excluded during screening. Text extraction preserves evidence for inspection but may introduce spacing or character errors. The benchmark review therefore checks numerical tokens, units, inequality signs and surrounding conditions against the original document.

The intended two-family, two-formal-edition collection was unavailable. A file labelled as a 2018 edition contained unresolved date placeholders and was conservatively excluded. No formal edition pair was admitted to the final collection. RQ2 therefore evaluates the behaviour for available and absent requested editions within this corpus. A question requesting an absent year expresses an input condition and does not establish that a formal standard with that year exists.

### B. Retrieval and edition constraints

Indexing, query processing and lexical evidence checks share jieba precise tokenisation with HMM disabled, a small frozen domain dictionary and fixed stopwords. Standard identifiers, technical terms, numbers and units remain available for indexing. BM25 uses k1 = 1.5 and b = 0.75. Dense retrieval uses raw cosine similarity between 1024-dimensional BAAI/bge-m3 query and chunk vectors [7]. The vector endpoint and model identity are stored, and a model change invalidates the corresponding index.

Hybrid combines separately normalised BM25 and Dense scores over the eligible candidate set. For a query, min–max normalisation maps a variable score range to zero through one. A constant positive score maps to one and any other constant score maps to zero. The combined score is S = (1 − w)B + wD, where B and D are the normalised scores. Stable chunk identifiers break ranking ties. All three retrieval methods return at most five passages, allowing the same Recall@5 criterion to be applied.

Before ranking, explicit standard-family and year requirements constrain the candidate set. An unavailable requested year produces an explicit non-answer and an available-year list. A family with several available years requires clarification if no year is specified. Conflicting explicit and bare edition cues also require clarification. For simple follow-ups, the previous resolved user question supplies the topic when the current question uses a referential expression. An explicit new standard replaces that topic. Model responses are excluded from the factual evidence used for this resolution.

### C. Evidence Gate and answer validation

The Evidence Gate retains a passage when either its lexical coverage or its raw cosine similarity reaches the selected threshold. Lexical coverage is the number of distinct query content tokens found in the passage divided by all distinct query content tokens. Standard identifiers and fixed stopwords are removed for this calculation, and an empty content-token set scores zero. BM25 uses the lexical signal because it does not request a query embedding. The signals estimate surface correspondence and retrieval similarity, while semantic sufficiency remains a source-review judgement.

Only retained evidence is sent to DeepSeek. The prompt requests structured atomic claims with source numbers and continuous quoted spans, preserves requested editions and instructs the model to explain missing evidence. Temperature is zero and the configured maximum output length is fixed before evaluation. Output parsing verifies that every displayed claim has a citation, the source number belongs to the supplied evidence, and the quoted span occurs in that source. Failed parsing, unsupported citation identifiers and mismatched excerpts produce explicit error states. These checks support traceability while allowing a fluent, correctly quoted claim to remain semantically wrong.

SQLite stores documents, chunks and vectors transactionally. Streamlit displays answers, evidence and PDF pages. Online-processing permissions and API errors are recorded. Vector batches and first-attempt slots persist individually. Interrupted requests with unavailable results remain unknown failed outcomes, retaining their place in the primary analysis.

## III. Experimental Design

### A. Benchmark and review procedure

The benchmark contains 100 questions. Development uses 20 questions, comprising 16 answerable and four unanswerable items. The held-out test uses 80 questions, comprising 64 answerable and 16 unanswerable items. Development category counts are six clause queries, three terminology queries, four edition queries, three follow-ups and four unanswerable queries. The corresponding test counts are 24, 12, 16, 12 and 16. Unanswerable items equally represent absent editions, out-of-corpus domain information, unrelated requests and ambiguity.

Each answerable record contains a reference answer, one to three required facts and source evidence units identified by document, location and continuous excerpt. Unanswerable records state their reason and expected refusal or clarification. Related facts and conversations are grouped within one split. Review covers the actual source wording and the compatibility of the question, necessary facts and expected action. Exact source matching and quota checks supplement this review. The question set remains concentrated in a subset of the collection, which limits its representativeness.

The student authorised the assistant to complete question, passage and output review. Records identify this procedure as assistant_source_review and preserve the actual execution times and source-based reasons. Two source-review passes were recorded for the questions. This changes the proposal's planned human annotation. Independent student, expert and inter-rater validation remain unmeasured. Shared assistance in benchmark construction and scoring may create correlated errors, so the resulting quality scores should be interpreted as corpus-bound, assistant-reviewed measurements.

### B. Configuration selection and controlled runs

Only development data select parameters. The candidate weights are 0.25, 0.50 and 0.75, ordered by Recall@5 and then MRR@5 on the 16 answerable development items. Remaining ties favour 0.50, then 0.25, then 0.75. Gate calibration considers lexical thresholds 0.05, 0.10 and 0.20 and cosine thresholds 0.20, 0.30, 0.40 and 0.50. The selection maximises mean passage F1 across the three retrieval modes, followed by fewer question-level false refusals, higher precision and the fixed grid order.

The five configurations are B1 BM25, B2 Dense, B3 Hybrid, A1 Hybrid with edition checks disabled, and A2 Hybrid with the retrieval gate disabled. A1 retains standard-family filtering. A2 retains prompts, model refusal, citation validation and error handling. A development integration pass precedes freezing. The formal evaluation then allocates 80 fixed questions to each configuration, giving 400 primary first-attempt slots. A slot may terminate before generation through a version or evidence check. Recovery attempts, where required, are stored separately.

### C. Measures and uncertainty

Recall@5 and mean reciprocal rank (MRR@5) use the pre-gate ranking over all 64 answerable test questions. Recall is the macro-average proportion of each question's gold evidence units covered in the top five. MRR averages the reciprocal rank of its first correct evidence hit, with zero for no hit. A gold match requires document identity, location and excerpt coverage. Full answer correctness also uses 64 as its denominator, retaining errors and refusals as failures. Citation support counts supported cited claims over all displayed cited claims, judging the citation set jointly. Citation coverage and resolvability are reported separately. Wrong-edition rate uses all unambiguous specified-edition items, including missing editions. Refusal recall uses the 16 unanswerable items, and false refusal uses the 64 answerable items.

Unsupported-answer incidence uses all 80 test items and is accompanied by its conditional rate among substantive answers and by answer coverage. API, format and citation errors are reported separately from justified refusals. Zero denominators remain unavailable. Retrieval, generation and end-to-end timing are summarised by median and nearest-rank 95th percentile (P95). Paired differences use group_id resampling with seed 3801 and 2000 bootstrap draws. Questions in a sampled group remain together on both sides of each comparison. The small number of source groups limits the stability and generalisation of these intervals.

The selected parameters are w = 0.50, lexical coverage = 0.20, and raw cosine threshold = 0.50. The frozen model configuration, numeric vectors and source hashes accompany the results. The report uses the frozen first-attempt dataset and records any recovery runs separately.

## IV. Performance Evaluation

### A. Retrieval and answer quality

Table I compares evidence recall and displayed answer quality. BM25 reaches Recall@5 96.9%, Dense 76.6%, and Hybrid 95.3%. Their MRR@5 values are 0.885, 0.650, and 0.889, respectively. Correctness uses all 64 answerable questions, so refusal and interface failures remain visible. Citation support pools displayed cited claims, while answer coverage uses all 80 questions.

TABLE I
Retrieval and answer quality

| Config. | Recall@5 | Correct | Support | Coverage |
| B1 | 0.969 | 0.922 | 1.000 | 0.800 |
| B2 | 0.766 | 0.703 | 0.981 | 0.688 |
| B3 | 0.953 | 0.891 | 0.993 | 0.800 |
| A1 | 0.953 | 0.906 | 0.993 | 0.812 |
| A2 | 0.953 | 0.906 | 0.993 | 0.800 |

### B. Edition and evidence ablations

With edition checks disabled, A1 has wrong-edition rate 0.0%, compared with 0.0% for B3. The denominator includes requests for missing editions. Available and missing strata are retained in the supplementary output. Because there are no admitted formal edition pairs, this comparison addresses refusal of unavailable requests and preservation of requested-year constraints. It leaves selection between two valid formal editions untested.

TABLE II
Refusal and unsupported-answer rates

| Config. | Wrong ed. | Refusal | False ref. | Unsupp. |
| B1 | 0.000 | 0.875 | 0.000 | 0.000 |
| B2 | 0.000 | 0.938 | 0.125 | 0.025 |
| B3 | 0.000 | 0.875 | 0.000 | 0.013 |
| A1 | 0.000 | 0.875 | 0.000 | 0.013 |
| A2 | 0.000 | 0.875 | 0.000 | 0.013 |

B3 produces unsupported-answer incidence 1.2%, while A2 produces 1.2%. B3 refusal recall is 87.5% and false refusal is 0.0%. Its unsupported rate conditional on a substantive answer is 1.6%. These measures expose the trade-off between accepting more passages and withholding answers. A low unsupported count accompanied by reduced answer coverage requires cautious interpretation.

The Recall@5 target of at least 80.0% was met, with observed 95.3%. The correctness target of at least 80.0% was met, with observed 89.1%. The citation support target of at least 90.0% was met, with observed 99.3%. The refusal recall target of at least 80.0% was met, with observed 87.5%. The false refusal target of at most 10.0% was met, with observed 0.0%.

### C. Paired uncertainty and operational behaviour

TABLE III
Paired differences in percentage points

| Comparison and metric | Difference | 95% interval |
| B3 − B1 Recall@5 | -1.6 | [-4.3, +0.0] |
| B3 − B2 Recall@5 | +18.8 | [+6.9, +32.0] |
| B3 − A1 wrong edition | +0.0 | [+0.0, +0.0] |
| B3 − A2 unsupported | +0.0 | [+0.0, +0.0] |

The grouped analysis contains 50 resampling groups. Table III reports absolute differences and uncertainty, preserving the same sampled questions for both configurations. The category tables in the supplementary record show the corresponding sample counts. For B3, median end-to-end time is 1627 ms and P95 is 2810 ms. The five configurations record 0 API errors and 0 unknown interrupted outcomes. Timings describe these sequential runs on the local machine and include early refusals when timings are known.

A source-review example is test-041. Dense returned assembly torque tolerances of +/-1.0 and +/-1.5 N m around a 44 N m boundary. The question asked for the torque instrument precision, which the original clause specifies as better than +/-3 percent. Hybrid answered that requested fact correctly. This case demonstrates a task mismatch despite source-supported claims. The reference locations include TBT2074-2020 / PDF p. 10, TBT2074-2020 / PDF p. 9.

A source-review example is test-079. The follow-up leaves both the standard and the length object unclear. Hybrid supplied source-supported values from the GB/T 32578 table and added a qualification. The frozen expected action required clarification before supplying substantive values. The answer therefore failed the clarification task. The reference locations include TBT2073-2020 / PDF p. 4, GBT32578-2016 / PDF p. 64.

### D. Interpretation and limitations

RQ1 is assessed from pre-gate Recall@5 and its paired B3–B1 and B3–B2 differences. RQ2 is assessed from the B3–A1 edition behaviour under the documented corpus limitation. RQ3 is assessed jointly from unsupported answers, false refusals and coverage in B3–A2. These comparisons isolate the declared components while keeping generation and citation checks fixed. Their scope remains bounded by the available sources, small grouped benchmark, heuristic evidence signals and assistant-based scoring. String-valid citations can omit a necessary condition, and a high similarity score can accompany an irrelevant requirement. Operational railway decisions require qualified review of applicable standards.

## V. Conclusion

RQ1 shows a bounded retrieval benefit over Dense. Hybrid recall exceeds Dense by 18.75 percentage points, with a grouped 95% interval of 6.90 to 32.00 points. BM25 records the highest recall and correctness in this benchmark. The Hybrid-minus-BM25 recall difference is −1.56 points, with interval −4.35 to 0.00 points. RQ2 yields zero observed wrong-edition answers in all five configurations over 68 specified-edition items. RQ3 yields the same unsupported-answer incidence of 1/80, refusal recall of 14/16 and false-refusal rate of 0/64 for B3 and A2. These observations provide no measured incremental benefit for the edition check or gate under this frozen benchmark. Source-review limitations and the absent formal edition pairs constrain the interpretation.

### A. Achievement against objectives

O1 delivered the planned document count, hashes and searchable index, while the formal edition-pair target remains unmet. The version limitation constrains RQ2. O2 delivered the integrated document-to-answer pipeline, source navigation and explicit failure handling. O3 delivered the prescribed question counts and fixed split with recorded source review, with the annotation method revised to assistant review. O4 produced the five controlled comparisons and their traceable first-attempt records. O5 produced technical report and reproducibility materials, while the Portfolio approvals, personal recording and institutional submission require their actual completion records.

### B. Significant technical achievement

The most significant technical achievement is the consistent evidence contract across retrieval, refusal, generation and evaluation. The same document identities and locations connect stored text to ranked passages, displayed claims, score records and the final analysis. Edition filtering and the Evidence Gate are separately switchable, while prompt and citation handling remain controlled. Frozen numeric vectors, tokenisation resources, runtime versions and code hashes make changes observable. This supports locating the stage and evidence involved in an answer failure.

### C. Future work

The highest-priority extension is a broader benchmark reviewed by railway-domain readers with independently checked formal edition pairs. That extension would test whether the current missing-edition behaviour generalises to choosing between valid editions. More complex tables and cross-page provisions should be evaluated before considering OCR or diagram understanding. A stronger semantic evidence model could then be compared under the same refusal and answer-coverage measures, with additional cost and error analysis. These extensions follow observed scope limitations and preserve a tractable evaluation design.

### D. Reflection

The project demonstrates how much research quality depends on data identity and evaluation discipline. A running interface established feasibility, but the evidential work required checking source editions, separating prototype settings from selected parameters and retaining unsuccessful runs. Development review exposed a long-follow-up resolution defect, which was corrected before the formal freeze. Excluding date-placeholder material reduced the breadth of the edition study while improving the defensibility of its claims. These decisions show the value of resolving data and protocol assumptions before interpreting performance.

Assistant-supported implementation and scoring require attribution, student review and supervisor scrutiny. The learning-outcome map points to inspectable evidence and assessment limits. Future repetitions should obtain formal editions and independent annotation earlier. Real supervision, reflective records and personal explanation remain necessary to demonstrate professional development.

TABLE IV
Learning outcome evidence map

| LO1 | Apply principles | Section II applies lexical ranking, vector similarity and transactional persistence. |
| LO2 | Analyse problems | Sections I and III define edition, evidence and refusal failure modes. |
| LO3 | Computational techniques | Sections II–IV document retrieval, calibration and paired bootstrap. |
| LO4 | Evaluate literature | Section I compares RAG, BM25, Dense and evidence-assessment literature. |
| LO5 | Design with constraints | Sections II–III address document permissions, fixed scope and API budget. |
| LO6 | Systems approach | Section II links parsing, indexing, retrieval, generation and provenance. |
| LO7 | Environmental/Societal impact | Section V limits operational use and prioritises bounded API processing. |
| LO8 | Ethical concerns | Section III records assistant review and source-use conditions. |
| LO9 | Risk management | Sections II and V address missing editions and heuristic-gate errors. |
| LO10 | Security risks | Section II uses local secrets, processing permissions and output validation. |
| LO11 | Inclusion & EDI | Streamlit exposes readable evidence, explicit statuses and source navigation. |
| LO12 | Practical/Lab skills | Software integration and API verification are evidenced, with hardware outside scope. |
| LO13 | Materials/Technologies | Section II evaluates PDF/DOCX, SQLite, Streamlit and model APIs. |
| LO14 | Engineering Management | Frozen manifests, budget records and Git changes support project control. |
| LO15 | Communication | This report and demonstration materials explain the system and its limits. |
| LO16 | Lifelong Learning/CPD | Section V and available Journal drafts support reflection, approvals remain pending. |

## Acknowledgment

The project acknowledges Prof. Deqing Huang as supervisor and attributes the external model services, research literature and supplied reference implementation. The assistant supported implementation, source review, experiment processing and drafting under the student's instructions. The student must critically review the submitted account and complete the required personal declaration and academic assessment activities.

## References

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” Advances in Neural Information Processing Systems, vol. 33, pp. 9459–9474, 2020.

[2] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Foundations and Trends in Information Retrieval, 2009, doi 10.1561/1500000019.

[3] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” Proceedings of EMNLP, pp. 6769–6781, 2020, doi 10.18653/v1/2020.emnlp-main.550.

[4] X. Ma, Y. Gong, P. He, H. Zhao, and N. Duan, “Query Rewriting in Retrieval-Augmented Large Language Models,” Proceedings of EMNLP, pp. 5303–5315, 2023, doi 10.18653/v1/2023.emnlp-main.322.

[5] F. Shi et al., “Large Language Models Can Be Easily Distracted by Irrelevant Context,” Proceedings of ICML, PMLR, vol. 202, pp. 31210–31227, 2023.

[6] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” Proceedings of EACL System Demonstrations, pp. 150–158, 2024, doi 10.18653/v1/2024.eacl-demo.16.

[7] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, “BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” arXiv:2402.03216, 2024.
