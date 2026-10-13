# ELEC3801 Project Proposal — Working Draft

Academic year: 2026–27. Prepared: 13 October 2026.

Status: draft for student revision and supervisor discussion; not submitted or approved. Planned work and proposed targets below are not completed results.

Name and SID: [TO BE COMPLETED BY STUDENT]

Degree programme: [TO BE COMPLETED BY STUDENT]

Supervisor: [TO BE COMPLETED BY STUDENT]

Project title: A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field

## Section 1: Project Description

### Background and problem

Overhead contact system information in the supplied project collection is distributed across technical standards, specifications and multiple document versions. This project addresses the difficulty of locating relevant clauses and checking which document supports an answer. Its intended users are students and engineers consulting Chinese-language standards. The prototype will support document consultation; it will not certify compliance or replace engineering judgement.

Retrieval-augmented generation (RAG) combines retrieved evidence with language generation [1]. BM25 provides a lexical retrieval baseline [2], while dense retrieval provides a complementary representation-based approach [3]. However, the effectiveness of these methods on this particular collection remains to be measured. Query rewriting motivates resolving short follow-up questions before retrieval [4]. Research on irrelevant context [5] and multidimensional RAG evaluation [6] motivates testing evidence quality as well as answer quality. These studies inform the design; they do not establish its effectiveness for railway standards.

### Aim and research questions

The aim is to develop and evaluate a traceable question-answering prototype for a curated collection of overhead contact system standards. RQ1 asks whether hybrid retrieval improves evidence retrieval over BM25-only and dense-only retrieval. RQ2 asks whether explicit standard identifiers and edition years reduce wrong-version citations. RQ3 asks whether evidence checks reduce unsupported answers without excessive refusal of answerable questions.

### Objectives and proposed success criteria

O1 — By Week 11, curate 20–30 usable, non-duplicate documents with file identifiers, standard/edition metadata, extraction reports and source locations. The initial 25-file audit is a candidate pool, not a completed corpus; unsuitable files will be replaced. All selected documents must have a recorded use-permission decision before external processing.

O2 — By Week 15, implement ingestion, retrieval, generation, source display and simple follow-up handling. Every displayed citation must resolve to a stored passage and document location. PDF citations will use file-page numbers; DOCX citations will use paragraph or table locations. Missing requested editions must not silently fall back to another edition.

O3 — Construct 100 manually checked questions, reserving 20 for development and 80 for testing, with reference answers and evidence locations for answerable questions. Linked follow-ups and paraphrases will remain in the same split. Freeze the corpus, labels and configuration before final evaluation.

O4 — By Week 19, compare the three retrieval modes and ablate edition handling and evidence checks. Proposed targets are Recall@5 of at least 0.80, answer correctness of at least 0.80, citation support of at least 0.90, refusal recall of at least 0.80 on unanswerable questions, and false refusal of at most 0.10 on answerable questions. Report denominators, errors and uncertainty. Targets are provisional design goals, not expected findings; negative results will be reported.

O5 — Deliver reproducible configurations, evaluation outputs, a local demonstration, the assessed report and a demonstration video by Week 24. Record retrieval, generation and total latency, including API failures, without promising an unmeasured response-time target.

### Integrated technical approach and boundaries

The offline pipeline will parse text-based PDF/DOCX files, retain provenance, split text into passages, obtain online embeddings and build a local index. The online pipeline will resolve simple follow-up context, interpret standard/edition constraints, retrieve passages with BM25 and/or vector similarity, check evidence, then request a cited answer or explain insufficient evidence. Interfaces will pass passage text, stable identifiers, source locations and scores; the response will expose answer status, citations and timings. A local demonstration interface and batch evaluator will share the same pipeline.

The supplied Python reference implementation will remain identifiable as the baseline. My planned contribution is corpus curation, edition-aware retrieval, evidence checking and controlled evaluation. Training a foundation model, drawing interpretation, production deployment and multi-user access are excluded. Knowledge gaps include extraction quality, retrieval calibration, assessment consistency and API cost estimation. Early feasibility checks, development-only tuning and a documented annotation rubric will address these gaps.

### References

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” in Advances in Neural Information Processing Systems, vol. 33, 2020. [Publisher record](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html).

[2] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009, doi: 10.1561/1500000019. [Publisher full text](https://www.nowpublishers.com/article/DownloadEBook/INR-019).

[3] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” in Proceedings of EMNLP, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550. [Publisher record](https://aclanthology.org/2020.emnlp-main.550/).

[4] X. Ma, Y. Gong, P. He, H. Zhao, and N. Duan, “Query Rewriting in Retrieval-Augmented Large Language Models,” in Proceedings of EMNLP, 2023, pp. 5303–5315, doi: 10.18653/v1/2023.emnlp-main.322. [Publisher record](https://aclanthology.org/2023.emnlp-main.322/).

[5] F. Shi et al., “Large Language Models Can Be Easily Distracted by Irrelevant Context,” in Proceedings of ICML, PMLR, vol. 202, 2023, pp. 31210–31227. [Publisher record](https://proceedings.mlr.press/v202/shi23a.html).

[6] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” in Proceedings of EACL: System Demonstrations, 2024, pp. 150–158, doi: 10.18653/v1/2024.eacl-demo.16. [Publisher record](https://aclanthology.org/2024.eacl-demo.16/).

## Section 2: Gantt Chart

Use the accompanying Gantt chart and task/dependency table. The schedule uses course weeks, not ISO calendar weeks. Week 5 is the planning anchor; the student's current course week is to be confirmed. Holidays and examination weeks must be reconciled with the module calendar. Final submission is Thursday of Week 24 at 14:00 UK time; viva preparation continues to Weeks 25–27.

![Project schedule](figures/gantt.png)

Milestones: M1 proposal reviewed for Week 7 submission; M2 curated corpus and baseline by Week 11; M3 enhancements integrated by Week 15; M4 evaluation completed by Week 19; M5 report draft by Week 22; M6 final submission by Week 24. Approvals and completion will be recorded only when they occur.

The detailed dependency table and effort allocations are maintained in `进度计划.csv`. Weekly journals, meeting records, risk updates and ten Review Documents run throughout the project.

## Section 3: Preliminary Resources Estimate

| Resource | Choice and justification | Estimated incremental cost / lead time | Limitation or alternative |
| --- | --- | --- | --- |
| Existing computer and storage | Use the existing computer for parsing and a small local index; no model training is planned. | £0 new hardware planned; available, capacity still to be measured. | A larger corpus could exceed memory; start with the curated subset. |
| Python environment and libraries | Reuse the supplied implementation and isolate dependencies; retain attribution and check licences before distribution. | £0 software purchase planned; allow one working day for setup. | Dependency compatibility and extraction quality require tests. |
| Online embedding and chat APIs | Avoid local model deployment; select compatible services after availability and permitted-use checks. | Proposed total spending ceiling £50, not a supplier quote or approved purchase; allow up to one week for account/access checks. | Provider and prices are not fixed. Estimate calls and token costs before use; cache embeddings and run small pilots. |
| Local standards collection | Select 20–30 usable documents, record versions and permissions, then manually check answer evidence. | No new acquisition cost assumed; allocate two weeks for selection and permission checks. | Possession does not establish permission to upload or redistribute; use an authorised substitute if necessary. |
| Versioning and backup | Keep code/configuration history and an approved separate backup of working documents. | £0 if existing storage suffices; set up during Week 5. | Do not place restricted source documents or credentials in a public repository. |

Budget assumption: the £50 API ceiling is a draft planning allowance requiring student/supervisor agreement before expenditure. No purchase or API call has been made as part of this preparation.

Workshop/access answers, based on the current software-only scope: allocated laboratory bench — No; Mechanical Workshop — No; Electronics Workshop — No; special IT support — No currently anticipated, revisit if network or service access fails; special electronic components — No.

## Section 4: Professional Practice, Risk, and Compliance

### Societal and environmental considerations

Intended benefit: help users find and inspect relevant evidence efficiently. Incorrect numerical requirements, omitted conditions or wrong editions could mislead users. Answers will therefore display their source and edition, identify insufficient evidence, and be presented as consultation support rather than engineering approval. Evaluation will assess factual correctness and source support; no reduction in real engineering incidents is claimed.

Inclusion and accessibility: use readable Chinese text, clear labels, selectable source passages, keyboard-accessible controls and status messages that do not rely on colour alone. Evaluate both standard terminology and paraphrased questions. English-language retrieval and universal accessibility are outside the first evaluation and will be stated as limitations.

Environment: reuse existing hardware, avoid model training, cache unchanged embeddings and bound document size and repeated API runs. Record request/token counts where available as resource-use indicators; do not claim measured carbon savings without a defensible method.

### Ethics

The planned evaluation uses technical documents and researcher-prepared questions. No participant recruitment, personal-data collection or user study is currently planned. Check document confidentiality, copyright, permitted cloud processing and provider retention conditions before external calls. Do not upload engineering drawings in this phase. Preserve acknowledgement of the supplied reference code and cited literature; maintain a truthful account of original work and assistance.

Ethics declaration: [STUDENT AND SUPERVISOR TO CONFIRM THE APPLICABLE OPTION]. Neither official checkbox is selected in this draft. If the scope changes to involve participants or personal data, discuss the required review before that work begins.

### Risk Register

Likelihood and impact use qualitative Low / Medium / High ratings at proposal stage; these are estimates to be reviewed at supervision meetings.

| Risk | Likelihood | Impact | Mitigation and schedule consequence |
| --- | --- | --- | --- |
| Scanned or poorly extracted documents | High | High | Audit candidates before building the corpus; prefer verified text-bearing counterparts; replace unusable files in Weeks 8–10. OCR remains outside the first implementation. |
| Incorrect edition metadata or duplicate documents | High | High | Verify identifiers against document pages, record hashes and retain explicit edition labels; test missing-edition cases before Week 15. |
| Unsupported answers or misleading citations | Medium | High | Require evidence display, add refusal and citation checks, and evaluate wrong-version and insufficient-evidence cases. |
| API outage, access failure or spending overrun | Medium | High | Run a small permitted pilot, record usage, cache embeddings and retain an offline retrieval demonstration; allow integration buffer in Weeks 14–15. Offline retrieval does not count as completed online QA validation. |
| Annotation errors or development/test leakage | Medium | High | Use a written rubric, group related questions before splitting, recheck labels and freeze the test set before final comparisons. |
| Data processing permission not established | Medium | High | Resolve during corpus selection; exclude affected files from external processing and use authorised substitutes. |
| Schedule slippage or scope expansion | Medium | High | Prioritise text QA and evaluation; exclude drawing interpretation and training; retain Weeks 23–24 for final checks. |
| Loss of code, labels or report drafts | Low | High | Maintain version history and an approved independent backup; verify that a recent snapshot can be restored. |

Risk owner: student; status: open at proposal stage. Review risk changes with the supervisor and record actions in the journal.

### Security

Keep API keys outside source control and redact them from logs. Bind the demonstration to the local machine; do not publish a network service. Treat document text as untrusted evidence, not instructions: it must not change system rules or trigger tools. Restrict input formats and file sizes, isolate malformed-file errors, and avoid execution of embedded content. Verify that citations refer to retrieved passages. Store only necessary evaluation logs and use approved storage for any restricted documents.

### Safety

Specialist laboratory required: No under the current scope; all work is desktop software and document analysis. Follow applicable workstation and electrical safety procedures. Whether existing risk assessments cover the work: [TO BE CONFIRMED WITH SUPERVISOR].

Safety briefing attendance, student signature and date: [TO BE COMPLETED BY STUDENT; NOT ASSERTED BY THIS DRAFT].

Supervisor approval, date and means: [PENDING; TO BE RECORDED AFTER REVIEW].
