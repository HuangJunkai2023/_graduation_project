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

No code commit dated Week 8 was present when this directory was created. This does not negate non-code review/signing work. No new system tests, API requests or benchmark runs were executed for the journal-writing task.

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

Future weeks currently have plans in WEEKLY_PLAN.md and no completed evidence entries. Keep permitted raw runs under the application's ignored `runtime/` or `outputs/`; store shareable summaries/plots with their actual week only when generated. Register a hash/configuration so ignored local evidence remains traceable, and use an approved independent backup rather than treating a local Git repository as a backup of ignored files.

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

| Week | Local file | Recorded through | Status | Minerva publication |
| --- | --- | --- | --- | --- |
| 8 | [WEEK_08.md](WEEK_08.md) | 2026-10-27 | Draft, for student review | Not confirmed |

Add future rows only with the corresponding actual draft/activity. Student approval of wording is `Approved for posting`; actual posting confirmed by the student permits `Published` and an actual date. Neither a generated file nor a Git commit establishes publication.
