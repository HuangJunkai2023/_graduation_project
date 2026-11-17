# Journal Evidence Index

Established: 2026-10-27, Week 8. Evidence is classified by **when the work happened**, what was inspected and what the evidence can support. An artifact reviewed this week does not turn its original development or experiment into this week's work.

## Week 8 — planning and review evidence

| ID | Activity / evidence date | Evidence and provenance | Supports / limits | Minerva-ready presentation |
| --- | --- | --- | --- | --- |
| **E08-01** | Final review/check: Week 8, confirmed by student; readable text predates this week | [Proposal PDF](../../开题材料/Proposal_English_Final.pdf) pp. 2–3 and [content source](../../开题材料/01_Proposal_Draft_EN.md). RQs, objectives, configurations and evaluation rules are directly inspectable. | Supports the final research design reviewed this week; not new implementation, annotation or experimental results. | Paste the journal's rationale for RQ1–3 and five configurations. Caption: “Final research design: three retrieval baselines and two mechanism-specific Hybrid ablations; all performance thresholds are planned targets.” |
| **E08-02** | Plan reviewed in Week 8; schedule artifact from earlier Proposal preparation | Proposal pp. 4–6, [Gantt image](../../开题材料/figures/gantt.png), [task CSV](../../开题材料/进度计划.csv), [break configuration](../../开题材料/假期配置.json). | Supports task dependencies, resource planning, M2/M3/M4/M5/M6/M7 and the work break; task budgets are not actual hours. | Embed the Gantt image if useful, with caption: “Proposal schedule: M2 Week 11; M3 Week 16; M4 Week 17; controlled evaluation Weeks 18–20; report/video by Week 21; final checks Week 24.” The journal already embeds a compact milestone table. |
| **E08-03** | Pre-submission check in Week 8, confirmed by student; requirements re-read 2026-10-27 during draft preparation | [Handbook](../../@26-27新版资料/1.Handbook_ELEC3801_Handbook_2026-27.docx), Sections 2–3 and Appendix 2; [Journal Guide](../../@26-27新版资料/5.Progress%20Journal%20Guides_ELEC3801_How_to_Keep_Your_Progress_Journal.docx), Sections 1–7. | Confirms the applicable criteria and the student's reported check, not any awarded mark, safety attendance record or submission receipt. Proposal rubric: aims/scope 40%; societal/environmental/ethical 20%; planning/risk 40%. | Paste the specific checked content: objectives/RQs, Gantt and dependencies, resources, ethics, safety and risk register. Do not claim an assessor grade. |
| **E08-04** | Both signatures completed **2026-10-26**; recorded from student's message **2026-10-27** | Explicit student confirmation that Deqing Huang reviewed and accepted the Proposal and that student/supervisor signatures were completed on 26 October. See [SUPERVISION_LOG.md](SUPERVISION_LOG.md). | Supports review acceptance and signing. A separate signed scan was not found; the inspected local PDF has blank signature lines. No formal meeting number, detailed supervisor comments, review-document approval or submission is inferred. | “My supervisor reviewed and accepted the Proposal, and we both signed it on 26 October 2026.” This is student-confirmed evidence, not a claim of independent signature inspection. |
| **E08-05** | **2026-10-27** | This directory's README, weekly plan, template, current draft and source/code cross-check notes. Prepared with assistant support for student review. | Supports establishing the journal workflow now and identifying future verification tasks. It is not evidence that the student has already run those tests or completed future weeks. | Optional short note about organising future validation around the Proposal, after the student has reviewed and adopted the workflow. Not required to expand the current journal. |

For E08-01–03, exact personal review times/hours were not supplied; none are invented. The signed Proposal is the authoritative plan as confirmed by the student. The local readable artifacts provide its working content; if a signed copy with differing content becomes available, record and reconcile the difference rather than silently changing the plan.

### Inline design facts for Week 8

These are **plans**, not measured results, and can be pasted without requiring readers to open local files.

| Research element | Fixed planning decision | Reason / limitation |
| --- | --- | --- |
| RQ1 | B1 BM25; B2 Dense; B3 Hybrid; same corpus and questions | Compare exact terminology with semantic paraphrases. No performance advantage is claimed yet. |
| RQ2 | A1 versus B3: disable edition/year checks, retain standard-family filtering | Isolate wrong-edition handling; sufficient usable formal edition pairs remain a feasibility risk. |
| RQ3 | A2 versus B3: disable retrieval Evidence Gate, retain citation validation | Assess unsupported answers and false refusals; lexical/excerpt matching cannot establish semantic support. |
| Data split | 20 development + 80 fixed test questions; related fact/dialogue groups stay together | Choose parameters on development data only; test set is for final comparison. |
| Evaluation size | 80 × 5 = 400 planned main executions | 100 development executions are additional; not 400 + 500. Failed/refused items remain recorded. |
| Resources | £35 generation + £10 embeddings + £5 reserve = £50 ceiling | A budget estimate, not actual spending or confirmed prices. |

## Historical baseline evidence — do not re-date as Week 8 progress

| ID | Original date / source | What is actually supported | Appropriate later use |
| --- | --- | --- | --- |
| **H06-01** | Git `c4c62a1`, 2026-10-13; [application modules](../../project/qa_system/ocs_qa/) and [README](../../project/qa_system/README.md) | Existing implementation of the RAG pipeline and interfaces. Source presence alone does not establish Proposal conformity or live performance. | Use as the object of new, dated verification in Weeks 9–16. Report only tests actually run then. |
| **H06-02** | [VERIFICATION.md](../../project/qa_system/VERIFICATION.md), recorded 2026-10-13 | Historical browser/local BM25 checks and limited live DeepSeek checks using synthetic evidence; mock API tests are distinguished. Formal benchmark and live embeddings were not verified by this record. | Background when planning interface and regression tests. Do not reuse its latency as a new measurement or railway QA performance. Raw ignored runtime artifacts must be checked for availability before citing them. |
| **H06-03** | [Initial audit](../../开题材料/数据核查/核查记录.md), 2026-10-13; [edition audit](../../开题材料/数据核查/版本语料抽查_20261014.json), 2026-10-14 | Historical candidate checks and sample extraction limitations, including 2010 candidates without usable text. Candidate count, duplicate files and usable editions are different concepts; cloud permissions were unresolved. | Plan corpus and version checks, then retain new audit evidence. The existing audit does not certify the final corpus or permissions. |
| **H07-01** | Git `ad30c78` (2026-10-19), `076400c`, `b11da5a`, `86c894f` (2026-10-20) | Earlier Proposal text, names/title and risk-selection revisions. Local repository HEAD before this workflow was `86c894fc95397a745f03d7458fb9eae6c53457f6`. | Trace the document lineage without moving these edits into Week 8. Signing and final review are separately supported by E08-04 and E08-03. |

No code commit dated Week 8 was present when this directory was created on 27 October. This does not negate non-code review/signing work. No new system tests, API requests or benchmark runs were executed during that initial 27 October preparation; the new Week 9 checks are recorded separately below.

## Draft preparation checks — 2026-10-27

- All six requested Markdown files were created; only `WEEK_08.md` is a completed weekly draft, and its status is `Draft`, not `Published`.
- The revised Week 8 Minerva body has seven requested sections and 424 words including the title, headings and evidence table, excluding maintenance metadata (English alphanumeric lexical count: 426). Its four Evidence IDs match the YAML metadata and E08-01–04 above; no claim of Minerva upload has been added.
- The weekly plan covers each Week 8–24 once, preserves the Proposal's 400-hour task budget and retains the original three RQs/five formal configurations. Benchmark authoring remains in Weeks 12–16, with tuning/freeze in Week 17.
- All 26 local Markdown link targets checked at preparation time existed. The source Proposal files and application code were not changed; no future entries, fabricated meeting records or new test results were created.

## Source fingerprints

The fingerprints below identify the readable material inspected on 2026-10-27; they are **not** fingerprints of an independently inspected signed scan.

| Local source | SHA-256 |
| --- | --- |
| `开题材料/Proposal_English_Final.pdf` | `f46ce266761ea6bed4ac383a9ce0133d7d8dac5d4c16903466022c95650b9ca1` |
| `开题材料/01_Proposal_Draft_EN.md` | `035e2f32450b020c6fe2fa5aad9e7e6dc8cccfb59e83c9826dd7cd36e661f258` |
| `开题材料/进度计划.csv` | `ff04716329cf0bbddfa055b4e2ae0f3c19784797e5cda97da36d2c53579379af` |
| `@26-27新版资料/5.Progress Journal Guides_ELEC3801_How_to_Keep_Your_Progress_Journal.docx` | `832abe807d61c48c144c8c6d49baed52b21ea47975fb19a6128e98e863ea8454` |
| `@26-27新版资料/1.Handbook_ELEC3801_Handbook_2026-27.docx` | `b212e4fa612286e5799891f427605362b5730fcbaf6b5cad1d69468308e0070f` |

## Future evidence: append only when activity actually occurs

At the 10 November checkpoint, Weeks 11–24 were future plans and the Week 10 draft recorded work only through that date. The dated 17 November additions below record current checks and clearly identified advance preparation. Keep permitted raw runs under the application's ignored `runtime/` or `outputs/`; store shareable summaries/plots with their actual activity dates. Register a hash/configuration so ignored local evidence remains traceable, and use an approved independent backup for ignored files.

Append a record with the following fields, not invented values:

| Field | Required information |
| --- | --- |
| ID / actual activity date / recorded date | `E[week]-[number]`; do not infer a date from file mtime. |
| Proposal task / RQ / question | What this activity was meant to establish. |
| Actor / method | Student activity, assistant/tool assistance, command or inspection method; distinguish static reading from execution. |
| Input / configuration | Document provenance/permission, dataset and corpus hashes, revision, model identity, prompt/config, relevant parameters. |
| Actual observations | Counts, status, numerical output, failure and scope; missing usage or measurements explicitly marked unavailable. |
| Evidence / immutable record | Real path and revision/hash, with availability/access noted. Do not expose `.env`, tokens or unauthorised source text. |
| Interpretation / decision | What follows, what does not, next action; personal proposal versus supervisor-agreed decision. |
| Minerva content | Small table/plot/screenshot plus date, method and caption; a path alone is insufficient. |
| Actual time / cost | Only recorded values; otherwise not recorded. Never copy task budgets as actuals. |

## Journal release register

Week 10新增：[WEEK_10.md](WEEK_10.md)，recorded_through为2026-11-10，状态Draft，Minerva发布未确认。下方Week 8/9记录保持原状态。

| Week | Local file | Recorded through | Status | Minerva publication |
| --- | --- | --- | --- | --- |
| 8 | [WEEK_08.md](WEEK_08.md) | 2026-10-27 | Draft, for student review | Not confirmed |
| 9 | [WEEK_09.md](WEEK_09.md) | 2026-11-04 | Draft, for student review | Not confirmed |
| 10 | [WEEK_10.md](WEEK_10.md) | 2026-11-10 | Draft, for student review | Not confirmed |
| 11 | [WEEK_11.md](WEEK_11.md) | 2026-11-17 | Draft, current-week recheck | Not confirmed |
| 12 | [WEEK_12.md](WEEK_12.md) | 2026-11-17 | Draft, advance preparation for 23–29 November | Not confirmed |
| 13 | [WEEK_13.md](WEEK_13.md) | 2026-11-17 | Draft, advance preparation for 30 November–6 December | Not confirmed |

Add future rows only with the corresponding actual draft/activity. Student approval of wording is `Approved for posting`; actual posting confirmed by the student permits `Published` and an actual date. Neither a generated file nor a Git commit establishes publication.

## Week 9 — readiness checks through 4 November 2026

All new checks below were executed with assistant/tool support on 4 November. They do not re-date the October implementation. Actual student working hours were not recorded. The readable English Proposal hash still matches the Week 8 fingerprint; T05 remains Weeks 9–10 and T06 Weeks 9–11.

| ID | Actual activity / evidence | Observed outcome and limits | Minerva-ready evidence |
| --- | --- | --- | --- |
| **E09-01** | 2026-11-04; [environment snapshot](evidence/week09/environment.json), [isolation comparison](evidence/week09/isolation_comparison.json) | Shared environment: seven dependency conflicts. New dedicated environment with `-I`: clean dependency check; five modules import. Without `-I`, ambient ROS packages remain visible. Exact installed versions and pyproject hash retained. This does not prove a live API or cross-machine reproducibility. | “Python 3.10.12; isolated project dependency check passed; shared environment had seven conflicts.” |
| **E09-02** | 2026-11-04; [12 existing test cases](evidence/week09/targeted_tests.json), [actual transcript](evidence/week09/targeted_tests.txt) | 12 passed, 23 deselected, pytest-reported 0.78 s. Existing tests with fakes/mocks cover API contract/errors and vector-store safeguards. No new algorithm or formal benchmark performance claimed. | “12 existing functional tests passed; synthetic/mock inputs, no live service verification.” |
| **E09-03** | 2026-11-04; [interface checks](evidence/week09/interface_checks.json), [executed check script](evidence/week09/verify_week09.py) | Three embedding fields absent. Actual configuration returns `embedding_not_configured` with zero HTTP dispatches. Seven mock fixtures pass (one accepted/reordered, six rejected). Zero real model API requests; live identity, dimension, usage and billing unavailable. Chat key presence is only a configuration observation. | “7 synthetic vector-response checks passed; missing embedding configuration blocks the live pilot.” |
| **E09-04** | 2026-11-04; [candidate CSV](evidence/week09/candidate_inventory.csv), [read-only database snapshot](evidence/week09/kb_snapshot.json) | 9 PDFs, 8 unique hashes in TB/T 2073/2074 candidates; three 2010 entries have no extracted alphanumeric characters, including one duplicate copy. Existing database: 3 documents, 503 chunks, 0 vectors. Text-layer detection is not full extraction-quality checking or permission confirmation. No OCR/ingestion performed. | “9 candidate files / 8 hashes; existing database: 503 chunks / 0 vectors; usable edition pairs not established.” |
| **E09-05** | Feedback and signing confirmed by student in the 2026-11-04 conversation; [Chinese-side revision record](../../开题材料/交大开题报告/最终检查记录.md), Git `eb7ed4f` | Student supplied requests for justified prose, fuller research content and diagrams. Revision addressed these while preserving RQs/configurations; subsequent student message confirmed teacher signing. Actual feedback/signing dates and meeting number not supplied; no signed scan or Review Document approval inspected. Separate from E08-04 English Proposal signing. | “Research explanation and diagrams revised following supervisor feedback.” |

The first-person draft has 382 rendered whitespace-delimited words (387 English/numeric lexical words), including the title, seven headings and evidence table, excluding YAML, the maintenance comment and Markdown formatting. The unstripped source has 413 whitespace tokens. All five Evidence IDs agree between metadata, the inline table and this index. It remains Draft and records progress only through 4 November; no Minerva upload or later-week work is claimed.

Source code, tests, English Proposal and task CSV were unchanged. No formal retrieval/QA experiments, live model calls or performance improvements were recorded. The local independent virtual environment and editable-install metadata are ignored by Git. Raw standard text and credentials are absent from this evidence package.

## Week 10 — defence preparation through 10 November 2026

This entry covers 9–10 November only. Existing October and Week 9 system checks are background, not new technical achievements. Assistant-supported preparation is subject to the student's review. Actual effort, costs, defence attendance, supervision feedback and publication have not been newly confirmed.

| ID | Actual activity / evidence | Observation and limit | Journal use |
| --- | --- | --- | --- |
| **E10-01** | 9 November; Git `f1ebd28`, [visual presentation and scripts](../../outputs/proposal-defense/v7-5min-visual/Modification_Summary.md) | 15 main slides and five backups using the university template; editable interface illustrations show edition selection, citations, evidence inspection and refusal. Not live outputs or application performance. | Communication and design explanation; three RQs and five configurations retained. |
| **E10-02** | Retained 9 November checks; 10 November [read-only audit](evidence/week10/artifact_audit.json), [audit script](evidence/week10/verify_week10.py) | Existing report: 12/12 delivery checks, zero overflow flags. Fresh inspection: 20 slide parts, 20 note parts, 19/20 exact bilingual matches. Slide 5 English opening is abbreviated relative to JSON. Deck unchanged; hashes retained. Allocated duration is 300 seconds, not a rehearsal measurement. | Presentation QA with a newly recorded text discrepancy; no claim of a new system test. |
| **E10-03** | 10 November conversation and [Week 10 evidence scope](evidence/week10/README.md) | Student requested a plain-language explanation for defence preparation. Assistant explained RAG, RQ1–3, controlled comparisons, refusal trade-offs and research limits using supplied materials. No mastery assessment or supervisor discussion inferred. | Reflective preparation; no new literature-reading or experiment claim. |

The [Week 10 draft](WEEK_10.md) retains seven first-person English sections and an inline evidence table. The planned T05 live embedding pilot and T06 source/extraction audit remain unverified in this reporting window. No API, corpus, benchmark or signed Proposal was changed, and no Minerva post, Teams message or Git submission was made by this journal update.


## 10 November clarification — revised journal basis

- **E10-04:** The student explicitly confirmed that the project is largely complete and asked for a journal organised around `Proposal_English_Final.pdf`, rather than inferred from repository files. This supports the broad completion context, not specific test figures or dates of past implementation.
- **E10-05:** Proposal pp.2–5 and 7 were reviewed on 10 November. T05 covers Weeks 9–10, T06 Weeks 9–11, and M2 is Week 11. [proposal_alignment.json](proposal_alignment.json) retains the source fingerprint and mapping.
- The revised Week 10 body reviews document processing, chunking, source tracing and edition metadata against that plan. It does not describe all components as newly implemented this week. The earlier assertion that presentation work displaced unfinished engineering is withdrawn: missing repository evidence does not establish non-completion.
- E10-01–03 and the presentation audit remain supporting preparation records. Presentation checks and the slide-5 note discrepancy are not the technical focus of the revised journal.
- The added Week 10 deviation checkpoint was removed from WEEKLY_PLAN.md; the original schedule is retained. No milestone, Proposal or prior-week journal was changed.

## Week 11 — corpus and baseline recheck on 17 November 2026

The existing corpus and freeze date to 12 November. The current-week activity is their read-only recheck and journal preparation on 17 November, executed by Codex. Student review and actual working hours remain unconfirmed.

| ID | Evidence and actual activity | Observation and journal scope |
| --- | --- | --- |
| E11-01 | [Current verification](evidence/week11/verification.json), [executed script](evidence/week11/verify_journal_basis.py) | 25 source hashes match. The database retains 3,341 chunks and compatible, finite, non-zero 1,024-dimensional vectors. Corpus and numerical-vector fingerprints match the existing freeze. |
| E11-02 | Same read-only check, using the 16 answerable development items and existing BM25 | Reference evidence was recovered at Top-5 for all 16. No generated answers or formal test questions were used. |
| E11-03 | [Corpus review](../../outputs/research/corpus/review_summary.md) and [Week 11 scope](evidence/week11/README.md) | No verified same-family formal edition pair admitted. Document count and edition coverage are assessed separately for M2/RQ2. |

The [Week 11 draft](WEEK_11.md) has seven English sections and 416 rendered whitespace-delimited words including the title and evidence table. It records work through 17 November, with source preparation dated 12 November kept as background. The new check used zero external API requests and left the frozen study intact. Status remains Draft and Minerva publication is unconfirmed.

## Week 12 — Dense retrieval advance preparation on 17 November 2026

Scheduled Week 12 covers 23–29 November. The complete local draft was prepared early from existing research records and the shared 17 November check. This preparation is dated to its actual occurrence. No activity during the future reporting period is claimed.

| ID | Evidence and actual activity | Observation and journal scope |
| --- | --- | --- |
| E12-01 | [Preparation checks](evidence/week12/preparation_checks.json), executed by the shared [check script](evidence/week11/verify_journal_basis.py) on 17 November | All 3,341 vectors have compatible BAAI/bge-m3 identity, 1,024 dimensions, finite values and non-zero norms. |
| E12-02 | Same cached development replay | Dense recovered the reference evidence at Top-5 for 16/16 answerable development items. Sixteen independently calculated top-result cosine scores agreed within 1e-12. One reinitialised cache/store check reproduced its top-five ordering. |
| E12-03 | [Existing benchmark verification](../../outputs/research/closing-review/benchmark_verification.json), originally dated 12 November; schema reviewed on 17 November | Existing split is 20 development / 80 test, with 16 / 64 answerable items. The original review method and absence of independent human reviewers remain recorded. No fresh annotation or annotation time is claimed. |

The [Week 12 draft](WEEK_12.md) contains seven English sections and 421 rendered whitespace-delimited words including the title and inline evidence. Its opening and metadata state the advance-preparation basis. The student should update any actual Week 12 activity before publication. The check executor was Codex, with zero API requests. Student review, publication and supervision feedback remain unconfirmed.

## Week 13 — Hybrid retrieval advance preparation on 17 November 2026

Scheduled Week 13 covers 30 November–6 December. Its complete draft was prepared on 17 November and draws on the same current recheck as Weeks 11 and 12. The three thematic entries share this activity. Its execution is counted once.

| ID | Evidence and actual activity | Observation and journal scope |
| --- | --- | --- |
| E13-01 | [Preparation checks](evidence/week13/preparation_checks.json), from the shared 17 November script | Same 16 answerable development queries compared across BM25, Dense and Hybrid. Every method had Recall@5 and MRR@5 of 1.0, while all 16 queries had different five-result lists between methods. |
| E13-02 | Same replay and source inspection | 80 returned Hybrid scores agreed with `(1-w)B+wD` at w=0.50 within 1e-12. Four normalisation edge cases passed. Eligible-set min–max and stable-ID tie ordering remain in the existing implementation. |
| E13-03 | [Selection record](../../outputs/research/closing-experiment/selection_evidence.json) and [calibration](../../outputs/research/closing-experiment/calibration.json), dated 12 November | Weights 0.25/0.50/0.75 tied on development Recall@5 and MRR@5. The predefined rule selected 0.50. Calibration was completed ahead of the planned Week 17 and is retained with that actual date. |

The [Week 13 draft](WEEK_13.md) has seven English sections and 434 rendered whitespace-delimited words including its title and evidence. No new weight selection or formal experiment was undertaken during journal preparation. The current check used zero API requests, accessed no formal test questions and preserved the selected parameters and research results. The check executor was Codex. The draft awaits student review, actual-week updates and publication confirmation.

The signed Proposal, WEEKLY_PLAN.md, Weeks 8–10 journals and SUPERVISION_LOG.md were unchanged by the 17 November journal preparation. No new meeting, supervisor approval or actual working hours were added.
