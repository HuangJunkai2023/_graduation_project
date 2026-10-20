# ELEC3801 Project Proposal — School Proposal Form Version

Academic year: 2026–27. Prepared: 14 October 2026. Format corrected: 16 October 2026.

Status: prepared for student signature and supervisor review/signature. Not submitted or approved. Future objectives and targets are not completed results.

Name and SID: Junkai Huang, 201804121

Degree programme: Electronic and Electrical Engineering

Supervisor: Deqing Huang

Project title: A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field

## Section 1: Project Description

### Background and problem

Chinese railway overhead contact system standards contain specialised terms, numerical limits and edition-dependent requirements. Answers must preserve editions, units and conditions.

Retrieval-augmented generation (RAG) connects retrieval and generation [1]. BM25 matches terms [2]; dense retrieval represents semantic similarity [3]. Query rewriting [4] informs rule-based follow-ups. Distractor research [5] motivates irrelevant-evidence tests, without establishing railway performance. RAGAs [6] motivates separate retrieval and answer assessment; semantic scoring here is manual.

### Aim, research questions and objectives

The aim is to develop and evaluate evidence-based question answering for these standards. RQ1: Does hybrid retrieval improve recall over BM25 and dense retrieval? RQ2: Does edition filtering reduce wrong-edition answers? RQ3: Does an evidence gate reduce unsupported answers without excessive refusal?

O1 — By Week 11, curate 20–30 usable documents, recording hashes, provenance, identifiers, years, extraction quality and permissions. Distinguish duplicates from formal editions. Seek two families with two usable editions each; availability remains unconfirmed. Exclude scans and drafts.

O2 — By Week 16, integrate PDF/DOCX parsing, chunking, SQLite, retrieval, DeepSeek generation, rule-based follow-ups and Streamlit. Locate citations by PDF file-page or DOCX paragraph/table. Missing requested editions require explicit refusal; ambiguous editions require clarification.

O3 — By Week 17, freeze 100 manually checked questions: 20 development (16 answerable) and 80 test (64 answerable). Cover clauses, terms, specified/missing/conflicting editions and follow-ups. Record facts, units, conditions and evidence spans in JSONL; keep related facts/dialogues within one split.

O4 — By Week 20, compare B1 BM25, B2 dense, B3 hybrid, A1 hybrid without edition filtering, and A2 hybrid without the retrieval gate. A1 retains family filtering but disables year restrictions and edition-availability/ambiguity checks. A2 retains prompts, citation checks and error handling. A2 measures only the gate's incremental effect.

O5 — By Week 24, deliver code, evaluation records, report, Portfolio and video; attend the Week 18 Symposium and prepare for the Week 25–27 viva.

### Reproducible method and assessment

Use consistent Chinese tokenisation for indexing and queries: an existing segmenter with a small domain dictionary, preserving standard identifiers, technical terms, numbers and units. No training is required. Freeze tokenisation and stopwords before testing.

Use Top-K=5, BM25 and cosine similarity. Min–max normalise scores across eligible chunks per query; combine as (1−w)B+wD. Constant positive scores map to one; other constant scores map to zero. Select w from {0.25,0.50,0.75} by development Recall@5, then MRR@5; ties favour 0.50. Select gate thresholds using development evidence labels only. Freeze corpus, models, prompts, chunking and parameters; automatically log inputs, outputs, evidence, configurations, tokens and timings.

Lexical coverage is matched distinct query content tokens divided by all distinct query content tokens, excluding standard identifiers and frozen stopwords; empty sets score zero. Matching uses passage tokens from the same segmenter. The gate accepts coverage or raw cosine above threshold. Metadata, citation identifiers and excerpt checks are automatic; semantic support, values, units and conditions require human assessment.

Recall@5 and MRR@5 use all 64 answerable items and pre-gate rankings. Correctness is fully correct answers/64; errors and refusals score zero. Citation support is supported cited claims/all cited claims, judging each claim's citations jointly; report citation coverage. Wrong-edition rate is answers using non-requested editions/all unambiguously edition-specified items, including missing editions; report availability strata and answer coverage. Refusal recall is justified non-answering/16 unanswerable items; false refusal is refusals or unnecessary clarifications/64 answerable items. Clarification is justified only for pre-labelled ambiguous items. API/format failures are errors, never justified refusals. Zero denominators yield N/A. Unsupported-answer incidence uses all 80 items.

Planning targets, not results: Recall@5 and correctness ≥0.80, citation support ≥0.90, refusal recall ≥0.80, false refusal ≤0.10. Report counts, paired differences, uncertainty, failures and latency.

### Feasibility and boundaries

A three-document BM25 prototype exists; live DeepSeek checks used synthetic evidence. Embedding, live dense/hybrid and formal evaluation remain unverified. Attribute reused code and APIs; develop calibration and annotation skills through development trials. Exclude training, agents, OCR, drawings, knowledge graphs, hardware and deployment. The system supports consultation, not engineering approval.

### References

[1] P. Lewis et al., “[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://papers.nips.cc/paper_files/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html),” in Advances in Neural Information Processing Systems, vol. 33, pp. 9459–9474, 2020.

[2] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009, doi: [10.1561/1500000019](https://doi.org/10.1561/1500000019).

[3] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” in Proceedings of EMNLP, 2020, pp. 6769–6781, doi: [10.18653/v1/2020.emnlp-main.550](https://doi.org/10.18653/v1/2020.emnlp-main.550).

[4] X. Ma, Y. Gong, P. He, H. Zhao, and N. Duan, “Query Rewriting in Retrieval-Augmented Large Language Models,” in Proceedings of EMNLP, 2023, pp. 5303–5315, doi: [10.18653/v1/2023.emnlp-main.322](https://doi.org/10.18653/v1/2023.emnlp-main.322).

[5] F. Shi et al., “[Large Language Models Can Be Easily Distracted by Irrelevant Context](https://proceedings.mlr.press/v202/shi23a.html),” in Proceedings of ICML, PMLR, vol. 202, 2023, pp. 31210–31227.

[6] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” in Proceedings of EACL: System Demonstrations, 2024, pp. 150–158, doi: [10.18653/v1/2024.eacl-demo.16](https://doi.org/10.18653/v1/2024.eacl-demo.16).

## Section 2: Gantt Chart

Week 1 begins on 7 September 2026, as confirmed in class. The confirmed Proposal deadline is Thursday 29 October 2026 (Week 8). Presentation follows the supplied ELEC3801 Proposal Form and example. The supplied course form specifies 14:00 UK time. Later date conversions assume consecutive weeks and remain provisional pending the semester timetable.

The project plan sets 1–14 February 2027 as a two-week Chinese New Year work break, corresponding to Week 22–23 under the consecutive planning-week convention. This is the student's work schedule, not an institutional holiday approval. No task bars cross the break. Budget 400 hours overall: 372 through Week 24 and 28 for the viva. This is a planning allocation, not completed work. The handbook states approximately 400 module hours but describes a Week 4–24 working period without explicitly allocating viva hours; the inclusive total here is a project budgeting choice, not a confirmed course interpretation.

![Project schedule](figures/gantt.png)

Milestones: M1 Proposal (Week 8); M2 corpus/baseline (Week 11); M3 integration (Week 16); M4 frozen benchmark/configuration (Week 17); MS compulsory Symposium (Week 18); M5 evaluation (Week 20); M6 report draft (Week 21); M7 final submission (Week 24, Thursday 14:00 UK time, subject to the course notice). Viva: Week 25–27. Table 1 gives named tasks, active weeks, dependencies and hours. Equal predecessor-end and successor-start weeks mean an ordered handover within that week, not parallel dependency completion.

Main dependency chain: T03 → T06 → T07 → T11 → T12 → T13 → T15; integration also gates T11. Literature informs the Proposal through an initial reading checkpoint in Week 6, with the remaining T02 review continuing afterwards. T06 starts with document curation; T05 must be complete before its final embedding/index check at M2. T15 leaves 12 hours for final checks after the break; complete the report draft and video beforehand.

T16 covers ten formal supervision meetings, ten Review Documents (maximum two pages each) and weekly Progress Journal entries from Week 5 to Week 24 except examination weeks. Prepare each Review Document after its meeting and share it at least one day before the next; send Review Document 10 for approval before final submission. Hold the pre-Proposal review before Week 8. Meeting dates, approvals and holiday journal arrangements require agreement; the work break does not waive course requirements. Do not back-fill records.

## Section 3: Preliminary Resources Estimate

| Resource | Choice and justification | Cost / lead time | Limitation and alternative |
| --- | --- | --- | --- |
| Existing computer and storage | CPU parsing and a small local index; existing machine already runs the prototype. No training GPU needed. | £0 new hardware planned; available. | Measure memory and disk use on the selected corpus; reduce batch size if necessary. |
| Python, PyMuPDF, python-docx, NumPy, SQLite and Streamlit | Inspectable parsing, scoring and persistence; a local interface and evaluator share the pipeline. | £0 software purchase planned; environment working. | Complex layouts need manual checks. Review library licences before distribution. A larger vector database is unnecessary for this small corpus. |
| DeepSeek chat and a separate embedding API | Reuse verified chat access; online vectors avoid local model deployment. | Proposed combined ceiling £50; chat access verified, allow one week to verify embedding access. | Chat access does not provide a configured embedding service. Record model identifiers, cost units and availability before full runs. No guaranteed price or service continuity. |
| Standards and literature | Select 20–30 usable documents from local candidates; use six initial papers to justify design and assessment. | No new acquisition cost assumed; selection/permissions in Week 9–11. | Replace unusable or unauthorised files. Reserve 36 hours in T07 for structured questions and source checking; confirm usable edition pairs before M2. |
| Git and separate backup | Track code, labels and report changes; keep an independent approved backup. | £0 if existing storage suffices; Git already initialised. | Local Git alone is not a backup. Keep keys and restricted source documents out of published history. |

Budget basis: the main comparison contains 80 × 5 = 400 test executions, requiring at most 400 first-attempt generation calls. Early refusal/clarification can avoid generation; log actual calls separately. One development pass adds 20 × 5 = 100 executions, so one pass over all 100 questions totals at most 500 generation calls, not 400 + 500. Reserve a further 100 calls for bounded development and recovery: at most 600 planned new calls overall. Retries consume the reserve and retain their original failures; they are not extra scored test items. Retrieval-weight and gate-grid selection reuse cached development retrieval and need no generation. There is no routine repeated test sweep or LLM judge.

Embedding costs are separate: one corpus build, cached development/test query vectors and any logged rebuilds. Embedding access is planned, not verified. Estimate token use from a permitted pilot and actual provider units. Allocate £35 to generation, £10 to embeddings and £5 contingency: a £50 planning ceiling, not a verified quotation, observed charge or approved funding. Check model/pricing availability before runs and reassess at £40 (80%). Previous chat-check expenditure must be read from the account ledger. No reimbursement is assumed.

T07 allocates 36 hours: 4 hours for schema/pilot, 20 for drafting 100 narrow questions (12 minutes each), 10 for a separate source recheck (6 minutes each), and 2 for grouped splitting. T12 allocates 40 hours: 4 for automated runs/log checks, 20 for scoring 400 outputs (3 minutes each), 6 for reviewing 80 sampled/difficult outputs, 6 for analysis, and 4 contingency. Use one to three required facts per item and a shared rubric; AI may draft, but every gold answer needs human source verification. Mask configuration labels; identical answer-and-evidence tuples may reuse a checked judgement with traceable links. Pilot timings are unmeasured assumptions. If exceeded, use contingency and remove optional repeats, not source checking or difficult test items. Reuse the existing prototype and report skeleton to limit repeated setup and drafting. Preserve 36 hours for annotation, 40 for evaluation and 48 for journals, reviews and supervision within the 400-hour total, including viva.

Workshop/access: allocated laboratory bench — No; Mechanical Workshop — No; Electronics Workshop — No; special IT support — No currently anticipated; purchase of special electronic components — No. This is desktop software work. If hardware scope changes, consult the School's purchasing/manufacturing process before ordering and account for its lead times.

## Section 4: Professional Practice, Risk, and Compliance

### Societal and environmental considerations

User benefit is easier access to inspectable clauses. Wrong editions, numerical errors and omitted conditions could mislead users; the interface will show evidence and version labels and distinguish insufficient evidence from a supported answer. It will not certify compliance. No measured productivity or safety benefit is claimed.

Inclusion: provide readable Chinese text, labelled keyboard-operable controls, selectable evidence and status messages independent of colour. Test specialist terms and ordinary-language paraphrases. This first study does not establish English-language coverage or universal accessibility.

Sustainability: reuse hardware, avoid model training, cache unchanged vectors and limit unnecessary API reruns. Log available request/token counts as resource-use indicators; do not equate them with measured carbon emissions. Preserve configuration and documentation so the prototype can be maintained without rebuilding unchanged data.

### Ethics

The project will use railway technical standards and researcher-prepared questions to evaluate a document-based question-answering system. No human participants, surveys, interviews or personal-data analysis are planned. Evaluation will use a fixed question set rather than collecting user conversations.

Document provenance and permitted uses will be recorded before ingestion. Only material permitted for external processing will be sent to chat or embedding services; this includes document chunks used to build the vector index. Restricted documents, personal information and operationally sensitive railway material will be excluded. Provider retention conditions will be checked, and only the text required for each request will be transmitted. Unresolved permissions will lead to exclusion or replacement, not assumed consent. Published outputs will use permitted excerpts and source references rather than redistribute complete standards.

Incorrect editions, unsupported claims and omitted conditions could mislead readers. Answers will display source locations and edition labels, with refusal or clarification where evidence is inadequate. The system will support study and document consultation; it will not authorise maintenance, railway operation or safety-critical decisions. Readers must verify the original standard before any practical use.

Reference code, literature and permitted AI assistance will be acknowledged. Benchmark answers will be checked against source text, and all configurations, failures and measured results will be reported honestly. Any later participant study or change in data use will require renewed ethics screening before that work begins.

### Risk Register

Likelihood/impact: L = Low, M = Medium, H = High. Initial ratings are planning judgements. The student owns all risks and will review triggers, actions and residual risk at each supervision meeting.

| ID / risk | L / I | Trigger, mitigation and affected tasks |
| --- | --- | --- |
| R1 Extraction failure | H / H | Scans, broken tables or lost units: audit pages, replace unsuitable files and log exclusions; no silent ingestion. T03/T06, before M2. |
| R2 Wrong edition or duplicates | H / H | Insufficient usable editions or metadata conflicts: TB/T 2073 and 2074 have local 2010/2020 candidates, but sampled 2010 files yielded no text. Their 2020 covers identify the superseded editions. Obtain permitted text editions or choose another family; exclude drafts and duplicate encodings. If two pairs cannot be verified by M2, retain A1 and report a limited case study; synthetic fixtures test code only, not empirical edition performance. T06/T08. |
| R3 Unsupported answers | M / H | Claims lack support or omit conditions: evidence gate, excerpt checks and manual semantic scoring; report false refusals. T09/T12. |
| R4 API/cost/model changes | M / H | Access fails, model changes or 80% cap reached: pilot early, cache vectors, log failures, freeze model identifiers and retain local retrieval. Verify embedding access in T05; integration buffer T10. |
| R5 Annotation/leakage | M / H | Ambiguous labels or related facts cross splits: grouped split, separate label recheck and immutable freeze before testing; mask configuration during scoring. T07/T11/T12. |
| R6 Data permissions | M / H | Cloud rights unresolved: keep affected files local and select authorised replacements before corpus freeze. T03/T06. |
| R7 Schedule/scope | M / H | Milestone slips: protect the planned 1–14 February break (Week 22–23); prioritise five comparisons and finish report/video by Week 21, with Week 24 checks. Recheck date mapping and timed annotation/scoring pilots; keep OCR/drawings out of scope. T11–T15; preserve Symposium attendance. |
| R8 Data loss | L / H | Missing/corrupt files: version code and labels, back up to separate approved storage and test restoration. T16, throughout. |

If an alternative provider becomes necessary, repeat all affected comparisons with the same replacement configuration; do not mix favourable outputs from different models. A local retrieval demo is a fallback deliverable, not evidence that online QA or hybrid evaluation has passed.

### Security

Protect API credentials, permitted document content and evaluation labels. Keep keys in an ignored local environment file and out of exports; rotate any exposed key. Bind the demo to localhost. Treat retrieved text as untrusted data: it cannot change system rules or execute tools. Limit upload type/size, isolate parser errors and validate citation identifiers and excerpts. Keep the test set and experiment configurations versioned; minimise logs and back up restricted files only to approved storage.

### Safety

Specialist laboratory required: No. The project will involve computer-based document processing, software development and local demonstrations. It will not involve railway access, live contact systems, high-voltage equipment, workshop manufacture or hardware modification. The researcher will use an ordinary workstation and follow the School's applicable computer-use and electrical-safety procedures.

The following table identifies the hazards and precautions for the computer-based project. L/M/H denote low/medium/high likelihood and impact. Residual ratings assume that the listed controls are applied; they do not represent measured accident rates.

| Hazard / persons affected | Initial L/I | Planned precautions | Residual L/I |
| --- | --- | --- | --- |
| Prolonged screen work / researcher | M/L | Adjust seating and display position, use suitable lighting, take regular breaks and vary tasks to reduce fatigue and strain. | L/L |
| Damaged computer power equipment / researcher | L/H | Use suitable intact power supplies, keep liquids away, avoid overloaded sockets and stop using damaged or overheating equipment; report faults rather than attempt electrical repair. | L/H |
| Trailing leads or obstructed workspace / researcher and nearby users | M/M | Route cables away from walkways and keep the desk, floor and exits clear. | L/M |

The researcher will review these precautions when the workspace or project scope changes and report incidents through the School's procedures. Any move to laboratory or railway work will require a separate assessment before it starts. The supervisor will review the assessment and its controls before practical work begins. Any separately prescribed School risk-assessment form will also be completed before that work; this Proposal does not replace it.

### Declarations for signature

Student ethics assessment for the defined scope: the first option below is selected on the basis of the document-only methodology and the permission controls stated above, for supervisor review.

[x] My project does not involve human participants, personal data or other ethical issues requiring review.

[ ] My project involves human participants, personal data or other ethical issues. I have discussed this with my supervisor and will obtain ethical approval before starting that work.

My project work will not be covered by existing Risk Assessments. A new one is required. Yes [ ] / No [x].

Safety declaration (to be confirmed by the student's signature): “I have attended the Safety Briefing (included in the ELEC3801 introductory lectures) and my attendance was recorded. I am aware that full Risk Assessments relating to project work within the School have been conducted. I agree to comply with all the relevant safety policies.”

Student name: Junkai Huang. Student ID: 201804121.

Student signature: ____________________ Date: __________.

Supervisor approval (to be confirmed by signature): “My student has completed this form satisfactorily and is aware of their safety responsibilities.”

Supervisor name: Deqing Huang.

Supervisor signature or confirmation: ____________________ Date: __________.
