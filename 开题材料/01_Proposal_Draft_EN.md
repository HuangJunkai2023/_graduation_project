# ELEC3801 Project Proposal — IEEE Two-Column Review Version

Academic year: 2026–27. Prepared: 13 October 2026.

Status: complete technical proposal for student verification and supervisor review; personal declarations remain pending. Not submitted or approved. Future objectives and targets are not completed results.

Name and SID: [TO BE COMPLETED BY STUDENT]

Degree programme: [TO BE COMPLETED BY STUDENT]

Supervisor: [TO BE COMPLETED BY STUDENT]

Project title: A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field

## Section 1: Project Description

### Background and problem

Chinese overhead contact system standards contain specialised terminology, numerical limits and edition-dependent requirements. In the supplied collection, relevant information is distributed across PDF and DOCX files. A useful answer must identify the applicable document and preserve conditions and units. Fluent but unsupported answers, particularly from the wrong edition, could mislead students and engineers consulting these documents.

Retrieval-augmented generation (RAG) connects retrieval with language generation [1]. BM25 offers lexical matching [2]; dense retrieval represents semantic similarity [3]. Neither establishes which edition is appropriate or guarantees that retrieved text supports a claim. Query rewriting [4] motivates resolving follow-ups before retrieval, but this project initially uses explicit context rules rather than a trained rewriter. Findings on irrelevant context [5] motivate testing distractors; their arithmetic-task results do not establish performance on railway standards. RAGAs [6] motivates separating retrieval and answer evaluation; manual evidence checking will remain primary here.

### Aim and research questions

The aim is to develop and evaluate an evidence-based question-answering system for a curated collection of Chinese overhead contact system standards. RQ1: Does hybrid retrieval improve evidence recall over BM25-only and dense-only retrieval? RQ2: Does explicit standard-and-year handling reduce wrong-edition answers? RQ3: Do evidence checks reduce unsupported answers without excessive refusal?

### Objectives and success criteria

O1 — By Week 11, curate 20–30 usable, non-duplicate documents. Record each file's hash, provenance, standard identifier, year, extraction quality and processing permission. Check metadata against document pages; a filename alone cannot establish current validity. Register unusable scans and replace them where possible.

O2 — By Week 16, integrate ingestion, three retrieval modes, DeepSeek generation, simple follow-ups and source display. All displayed citations must resolve to retrieved evidence: PDF file-page numbers or DOCX paragraph/table locations. All mandatory missing-edition tests must avoid silently substituting another version. Parsing and API failures must remain distinguishable from evidence-based refusals.

O3 — By Week 17, freeze 100 manually checked questions: 20 development and 80 test items. Cover clauses, terminology, versions, follow-ups and unanswerable questions. Annotate required facts and evidence locations; keep related questions in one split. Select weights and thresholds using development data only.

O4 — By Week 20, compare BM25, dense and hybrid retrieval, then separately remove edition filtering and the retrieval evidence gate. Hold other settings constant. Measure Recall@5, MRR@5, answer correctness, citation support, wrong-edition rate, refusal recall, false refusal and stage latency. Proposed targets are Recall@5 ≥0.80, answer correctness ≥0.80, citation support ≥0.90, refusal recall ≥0.80 and false refusal ≤0.10. These are provisional engineering goals, not measured findings. Report sample counts, paired differences, uncertainty and negative results; API failures do not count as correct refusals.

O5 — By Week 24, deliver the reproducible system, evaluation records, IEEE report, Portfolio and demonstration video. Present progress at the compulsory Week 18 Symposium and prepare for the Weeks 25–27 viva.

### Integrated approach, feasibility and boundaries

The ingestion module will parse and chunk documents, preserve source locations and store records in SQLite. A separate online embedding service will populate vectors. The retriever will apply standard/year constraints and combine normalised BM25 and cosine scores. After evidence screening, the generation client will send permitted passages to DeepSeek and validate returned JSON, citation identifiers and verbatim excerpts. Matching an excerpt is not proof of semantic support. The local Streamlit interface and batch evaluator will share structured records containing evidence, answer status and timings.

A preliminary three-document prototype already supports BM25 retrieval and cited DeepSeek answers; live API checks have succeeded. Embedding integration and formal evaluation remain outstanding. This establishes feasibility, not accuracy. The supplied reference implementation is preserved; the current implementation is separate. Planned contributions are corpus curation, version handling, evidence checks and controlled analysis, with reference-code and AI assistance acknowledged.

The scope excludes model training, drawing interpretation, OCR development, multi-user access and production deployment. The system supports consultation, not engineering approval. Knowledge gaps in extraction, retrieval calibration, annotation consistency and API budgeting will be addressed through literature study, development-set trials and documented scoring rules.

### References

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” in Advances in Neural Information Processing Systems, vol. 33, 2020. [Publisher record](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html).

[2] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009, doi: 10.1561/1500000019. [Publisher full text](https://www.nowpublishers.com/article/DownloadEBook/INR-019).

[3] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” in Proceedings of EMNLP, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550. [Publisher record](https://aclanthology.org/2020.emnlp-main.550/).

[4] X. Ma, Y. Gong, P. He, H. Zhao, and N. Duan, “Query Rewriting in Retrieval-Augmented Large Language Models,” in Proceedings of EMNLP, 2023, pp. 5303–5315, doi: 10.18653/v1/2023.emnlp-main.322. [Publisher record](https://aclanthology.org/2023.emnlp-main.322/).

[5] F. Shi et al., “Large Language Models Can Be Easily Distracted by Irrelevant Context,” in Proceedings of ICML, PMLR, vol. 202, 2023, pp. 31210–31227. [Publisher record](https://proceedings.mlr.press/v202/shi23a.html).

[6] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” in Proceedings of EACL: System Demonstrations, 2024, pp. 150–158, doi: 10.18653/v1/2024.eacl-demo.16. [Publisher record](https://aclanthology.org/2024.eacl-demo.16/).

## Section 2: Gantt Chart

The Gantt chart labels every interval as Week X. Week 12–13 is provisionally reserved for a two-week Chinese New Year break, with no scheduled project work. Its position must be confirmed against the course timetable; it is not a calendar-date conversion. No task bars cross the break. Planned effort remains 400 hours to Week 24 plus 28 for the viva; these are not recorded actual hours. Early prototyping is recorded separately.

![Project schedule](figures/gantt.png)

Milestones: M1 Proposal (Week 7); M2 corpus/baseline (Week 11); M3 integration (Week 16); M4 frozen benchmark/configuration (Week 17); MS compulsory Symposium (Week 18); M5 evaluation (Week 20); M6 report draft (Week 22); M7 submission (Week 24). Week 7 and Week 24 deadlines: Thursday, 14:00 UK time.

Critical sequence: T03 → T06 → T07 → T11 → T12 → T13 → T15; integration also gates T11. Predecessors show dependencies. T16 resumes after the break and covers journals, ten Review Documents and supervision; T18 includes Symposium feedback. Confirm holiday journal obligations with the course; the work break does not itself waive submission requirements. Reassess risks and remaining effort at each meeting. Weeks 23–24 provide revision/contingency time; resolve data and API risks earlier (R1/R4/R6). Attendance and approvals remain unconfirmed until they occur.

## Section 3: Preliminary Resources Estimate

| Resource | Choice and justification | Cost / lead time | Limitation and alternative |
| --- | --- | --- | --- |
| Existing computer and storage | CPU parsing and a small local index; existing machine already runs the prototype. No training GPU needed. | £0 new hardware planned; available. | Measure memory and disk use on the selected corpus; reduce batch size if necessary. |
| Python, PyMuPDF, python-docx, NumPy, SQLite and Streamlit | Inspectable parsing, scoring and persistence; a local interface and evaluator share the pipeline. | £0 software purchase planned; environment working. | Complex layouts need manual checks. Review library licences before distribution. A larger vector database is unnecessary for this small corpus. |
| DeepSeek chat and a separate embedding API | Reuse verified chat access; online vectors avoid local model deployment. | Proposed combined ceiling £50; chat access verified, allow one week to verify embedding access. | Chat access does not provide a configured embedding service. Record model identifiers, cost units and availability before full runs. No guaranteed price or service continuity. |
| Standards and literature | Select 20–30 usable documents from local candidates; use six initial papers to justify design and assessment. | No new acquisition cost assumed; selection/permissions in Weeks 8–11. | Replace unusable or unauthorised files. Reserve T07's 28 hours for drafting and checking questions. |
| Git and separate backup | Track code, labels and report changes; keep an independent approved backup. | £0 if existing storage suffices; Git already initialised. | Local Git alone is not a backup. Keep keys and restricted source documents out of published history. |

Budget basis: at most 500 generation requests for one pass over all 100 questions and five configurations, plus a provisional 100-call development/recovery allowance; the fixed test comparison itself is 80 × 5 = 400 runs. Embedding cost includes one corpus build and applicable query vectors, with caching. Estimate tokens using a permitted pilot and actual provider usage, not Chinese character counts. Allocate provisionally £35 to generation, £10 to embeddings and £5 contingency; this is a planning cap, not a quotation, funding approval or observed cost. Small live chat checks have already occurred; cumulative expenditure must be taken from the account ledger. Reassess the plan at 80% of the cap, retaining the fixed test set and all five comparisons before optional repeat runs. Confirm institutional funding arrangements separately; reimbursement is not assumed.

Workshop/access: allocated laboratory bench — No; Mechanical Workshop — No; Electronics Workshop — No; special IT support — No currently anticipated; purchase of special electronic components — No. This is desktop software work. If hardware scope changes, consult the School's purchasing/manufacturing process before ordering and account for its lead times.

## Section 4: Professional Practice, Risk, and Compliance

### Societal and environmental considerations

User benefit is easier access to inspectable clauses. Wrong editions, numerical errors and omitted conditions could mislead users; the interface will show evidence and version labels and distinguish insufficient evidence from a supported answer. It will not certify compliance. No measured productivity or safety benefit is claimed.

Inclusion: provide readable Chinese text, labelled keyboard-operable controls, selectable evidence and status messages independent of colour. Test specialist terms and ordinary-language paraphrases. This first study does not establish English-language coverage or universal accessibility.

Sustainability: reuse hardware, avoid model training, cache unchanged vectors and limit unnecessary API reruns. Log available request/token counts as resource-use indicators; do not equate them with measured carbon emissions. Preserve configuration and documentation so the prototype can be maintained without rebuilding unchanged data.

### Ethics

Use technical documents and researcher-prepared questions; no participant recruitment or personal-data study is planned. Record provenance, confidentiality and permission for cloud processing before sending each document. A local permission toggle records a decision but does not establish legal permission. Exclude restricted material and engineering drawings from external processing in this phase. Check service retention conditions for permitted data.

Acknowledge the supplied reference implementation, literature and AI assistance in code and writing; keep development records. Do not present generated annotations, planned improvements or test targets as measured results. The applicable assessment brief governs permitted assistance. Neither ethics checkbox is selected here: the student and supervisor must determine the applicable option. Any later participant study requires review before recruitment.

### Risk Register

Likelihood/impact: L = Low, M = Medium, H = High. Initial ratings are planning judgements. The student owns all risks and will review triggers, actions and residual risk at each supervision meeting.

| ID / risk | L / I | Trigger, mitigation and affected tasks |
| --- | --- | --- |
| R1 Extraction failure | H / H | Scans, broken tables or lost units: audit pages, replace unsuitable files and log exclusions; no silent ingestion. T03/T06, before M2. |
| R2 Wrong edition or duplicates | H / H | Metadata conflicts: verify document pages and hashes, preserve years and test missing editions. T06/T08, before M3. |
| R3 Unsupported answers | M / H | Claims lack support or omit conditions: evidence gate, excerpt checks and manual semantic scoring; report false refusals. T09/T12. |
| R4 API/cost/model changes | M / H | Access fails, model changes or 80% cap reached: pilot early, cache vectors, log failures, freeze model identifiers and retain local retrieval. Verify embedding access in T05; integration buffer T10. |
| R5 Annotation/leakage | M / H | Ambiguous labels or related facts cross splits: grouped split, separate label recheck and immutable freeze before testing; mask configuration during scoring. T07/T11/T12. |
| R6 Data permissions | M / H | Cloud rights unresolved: keep affected files local and select authorised replacements before corpus freeze. T03/T06. |
| R7 Schedule/scope | M / H | Milestone slips: protect the Week 12–13 holiday; prioritise five comparisons, defer OCR/drawings and use Weeks 23–24 buffer. T11–T15; preserve Symposium attendance. |
| R8 Data loss | L / H | Missing/corrupt files: version code and labels, back up to separate approved storage and test restoration. T16, throughout. |

If an alternative provider becomes necessary, repeat all affected comparisons with the same replacement configuration; do not mix favourable outputs from different models. A local retrieval demo is a fallback deliverable, not evidence that online QA or hybrid evaluation has passed.

### Security

Protect API credentials, permitted document content and evaluation labels. Keep keys in an ignored local environment file and out of exports; rotate any exposed key. Bind the demo to localhost. Treat retrieved text as untrusted data: it cannot change system rules or execute tools. Limit upload type/size, isolate parser errors and validate citation identifiers and excerpts. Keep the test set and experiment configurations versioned; minimise logs and back up restricted files only to approved storage.

### Safety

Specialist laboratory required: No. Work is desktop software and document analysis; there are no live railway, high-voltage, workshop or field experiments. Follow workstation ergonomics and normal computer electrical-safety procedures. Existing risk-assessment coverage / whether a new assessment is required: [TO BE CONFIRMED WITH SUPERVISOR].

Safety briefing attendance: [TO BE COMPLETED BY STUDENT]. The official declaration and signature fields remain for personal confirmation; no attendance is asserted by this document.

Supervisor approval, date and means: [PENDING; TO BE RECORDED AFTER REVIEW].
