# Supplementary measured results

Study frozen and executed on 12 November 2026. All tables use primary first attempts. The recorded review method is assistant_source_review, with Codex as the executing reviewer. Question preparation and evaluation share the same assistant workflow. Independent human or expert validation remains outstanding.

Frozen manifest SHA-256 `929f09cbd8fa1add989543488045a3fbb92fc913014b7c545ed2741120865fe6`.

Summary SHA-256 `3bb2fdff5ea84939cf19f2072dcddb29932599eda66ebecabe764a64201de632`.

## Design and populations

The corpus has 25 independently numbered documents, 3341 chunks and 3341 1024-dimensional vectors. The 20 development questions contain 16 answerable and four unanswerable items. The 80 held-out test questions contain 64 answerable and 16 unanswerable items. Their fact coverage is concentrated in six corpus documents. No verified formal edition pair was admitted.

B1 uses BM25, B2 Dense and B3 Hybrid. A1 disables edition checks while retaining standard-family filtering. A2 disables the Evidence Gate while retaining the prompt, citation validation and error handling. Every configuration has 80 primary slots. The nine invalid-citation first attempts remain in the primary analysis. Nine recovery attempts, including five displayed answers and four further citation failures, are recorded separately.

The selected Hybrid weight is 0.50 from candidates 0.25, 0.50 and 0.75. Query-wise normalised lexical and dense scores enter S = (1 − w)B + wD. The development-selected Gate accepts term coverage ≥0.20 OR raw cosine ≥0.50. Thresholds are heuristic signals. Semantic support, values, units and conditions are judged against sources.

## Overall metrics

| Metric | B1 | B2 | B3 | A1 | A2 |
| --- | --- | --- | --- | --- | --- |
| Recall@5 | 62/64 (96.88%) | 49/64 (76.56%) | 61/64 (95.31%) | 61/64 (95.31%) | 61/64 (95.31%) |
| MRR@5 | 56.6167/64 (88.46%) | 41.6167/64 (65.03%) | 56.9167/64 (88.93%) | 56.9167/64 (88.93%) | 56.9167/64 (88.93%) |
| Complete answer correctness | 59/64 (92.19%) | 45/64 (70.31%) | 57/64 (89.06%) | 58/64 (90.62%) | 58/64 (90.62%) |
| Citation support | 135/135 (100.00%) | 105/107 (98.13%) | 140/141 (99.29%) | 138/139 (99.28%) | 136/137 (99.27%) |
| Wrong-edition rate | 0/68 (0.00%) | 0/68 (0.00%) | 0/68 (0.00%) | 0/68 (0.00%) | 0/68 (0.00%) |
| Refusal recall | 14/16 (87.50%) | 15/16 (93.75%) | 14/16 (87.50%) | 14/16 (87.50%) | 14/16 (87.50%) |
| False refusal | 0/64 (0.00%) | 8/64 (12.50%) | 0/64 (0.00%) | 0/64 (0.00%) | 0/64 (0.00%) |
| Unsupported answer incidence | 0/80 (0.00%) | 2/80 (2.50%) | 1/80 (1.25%) | 1/80 (1.25%) | 1/80 (1.25%) |
| Displayed answer coverage | 64/80 (80.00%) | 55/80 (68.75%) | 64/80 (80.00%) | 65/80 (81.25%) | 64/80 (80.00%) |
| Protocol completion rate | 78/80 (97.50%) | 78/80 (97.50%) | 78/80 (97.50%) | 79/80 (98.75%) | 78/80 (97.50%) |

Recall and correctness use all 64 answerable items. Refusal recall uses all 16 unanswerable items. False refusal uses all 64 answerable items. Citation support counts displayed cited claims. Wrong-edition rate uses 68 unambiguous available-or-missing edition requests. Ambiguous requests remain in the refusal and coverage analysis. Answer coverage includes displayed substantive partial answers. Protocol completion excludes parsing/citation failures.

## Latency

All 80 first attempts per configuration are retained, including early refusals and errors. Each cell gives median / nearest-rank p95 in milliseconds.

| Configuration | Retrieval | Generation | End to end |
| --- | --- | --- | --- |
| B1 | 11.21 / 23.76 | 1239.53 / 2311.99 | 1249.37 / 2597.54 |
| B2 | 318.94 / 490.79 | 1175.28 / 2231.22 | 1563.32 / 2602.99 |
| B3 | 340.25 / 476.89 | 1266.83 / 2420.20 | 1627.40 / 2809.72 |
| A1 | 327.71 / 525.35 | 1318.92 / 2093.39 | 1646.11 / 2570.16 |
| A2 | 325.11 / 544.72 | 1307.00 / 2357.91 | 1643.80 / 2758.48 |

## Category results

| Configuration | Category | Questions | Recall@5 | Correctness | Refusal recall |
| --- | --- | --- | --- | --- | --- |
| B1 | clause | 24 | 23/24 (95.83%) | 23/24 (95.83%) | NA (0 denominator) |
| B1 | edition | 16 | 16/16 (100.00%) | 15/16 (93.75%) | NA (0 denominator) |
| B1 | follow_up | 12 | 12/12 (100.00%) | 11/12 (91.67%) | NA (0 denominator) |
| B1 | term | 12 | 11/12 (91.67%) | 10/12 (83.33%) | NA (0 denominator) |
| B1 | unanswerable | 16 | NA (0 denominator) | NA (0 denominator) | 14/16 (87.50%) |
| B2 | clause | 24 | 17/24 (70.83%) | 17/24 (70.83%) | NA (0 denominator) |
| B2 | edition | 16 | 13/16 (81.25%) | 11/16 (68.75%) | NA (0 denominator) |
| B2 | follow_up | 12 | 11/12 (91.67%) | 10/12 (83.33%) | NA (0 denominator) |
| B2 | term | 12 | 8/12 (66.67%) | 7/12 (58.33%) | NA (0 denominator) |
| B2 | unanswerable | 16 | NA (0 denominator) | NA (0 denominator) | 15/16 (93.75%) |
| B3 | clause | 24 | 23/24 (95.83%) | 23/24 (95.83%) | NA (0 denominator) |
| B3 | edition | 16 | 16/16 (100.00%) | 14/16 (87.50%) | NA (0 denominator) |
| B3 | follow_up | 12 | 12/12 (100.00%) | 11/12 (91.67%) | NA (0 denominator) |
| B3 | term | 12 | 10/12 (83.33%) | 9/12 (75.00%) | NA (0 denominator) |
| B3 | unanswerable | 16 | NA (0 denominator) | NA (0 denominator) | 14/16 (87.50%) |
| A1 | clause | 24 | 23/24 (95.83%) | 23/24 (95.83%) | NA (0 denominator) |
| A1 | edition | 16 | 16/16 (100.00%) | 14/16 (87.50%) | NA (0 denominator) |
| A1 | follow_up | 12 | 12/12 (100.00%) | 11/12 (91.67%) | NA (0 denominator) |
| A1 | term | 12 | 10/12 (83.33%) | 10/12 (83.33%) | NA (0 denominator) |
| A1 | unanswerable | 16 | NA (0 denominator) | NA (0 denominator) | 14/16 (87.50%) |
| A2 | clause | 24 | 23/24 (95.83%) | 23/24 (95.83%) | NA (0 denominator) |
| A2 | edition | 16 | 16/16 (100.00%) | 14/16 (87.50%) | NA (0 denominator) |
| A2 | follow_up | 12 | 12/12 (100.00%) | 11/12 (91.67%) | NA (0 denominator) |
| A2 | term | 12 | 10/12 (83.33%) | 10/12 (83.33%) | NA (0 denominator) |
| A2 | unanswerable | 16 | NA (0 denominator) | NA (0 denominator) | 14/16 (87.50%) |

## Version availability and failures

| Configuration | Availability class | Items | Displayed answers |
| --- | --- | --- | --- |
| B1 | available | 64 | 62 |
| B1 | missing | 4 | 0 |
| B1 | ambiguous | 4 | 2 |
| B1 | not_applicable | 8 | 0 |
| B2 | available | 64 | 54 |
| B2 | missing | 4 | 0 |
| B2 | ambiguous | 4 | 1 |
| B2 | not_applicable | 8 | 0 |
| B3 | available | 64 | 62 |
| B3 | missing | 4 | 0 |
| B3 | ambiguous | 4 | 2 |
| B3 | not_applicable | 8 | 0 |
| A1 | available | 64 | 63 |
| A1 | missing | 4 | 0 |
| A1 | ambiguous | 4 | 2 |
| A1 | not_applicable | 8 | 0 |
| A2 | available | 64 | 62 |
| A2 | missing | 4 | 0 |
| A2 | ambiguous | 4 | 2 |
| A2 | not_applicable | 8 | 0 |

Failure-type counts follow the source-judgement labels. Different labels can denote related failure behaviours.

- B1 — none 73, invalid_citation 2, incomplete_answer 2, incomplete 1, clarification_miss 2
- B2 — none 60, incomplete_answer 5, false_refusal 8, invalid_citation 2, incomplete 2, answer_mismatch 1, retrieval_miss 1, clarification_failure 1
- B3 — none 71, incomplete_answer 2, incomplete 2, invalid_citation 2, unsupported_claim 1, clarification_miss 1, clarification_failure 1
- A1 — none 72, incomplete_answer 3, incomplete 1, unsupported_claim 1, invalid_citation 1, clarification_miss 2
- A2 — none 72, incomplete 2, invalid_citation 2, unsupported_claim 1, incomplete_answer 1, clarification_failure 2

## Paired differences and uncertainty

Question groups preserve related conversations. Paired bootstrap uses 50 group_id units, seed 3801 and 2000 resamples. Differences below are absolute percentage points with 95% intervals.

| Comparison | Metric | Difference | 95% interval |
| --- | --- | --- | --- |
| B3_minus_B1 | recall_at_5 | -1.56 | [-4.35, 0.00] |
| B3_minus_B1 | mrr_at_5 | 0.47 | [-2.83, 4.79] |
| B3_minus_B1 | answer_correctness | -3.12 | [-7.04, 0.00] |
| B3_minus_B1 | citation_support | -0.71 | [-2.54, 0.00] |
| B3_minus_B1 | citation_coverage | 0.00 | [0.00, 0.00] |
| B3_minus_B1 | wrong_edition_rate | 0.00 | [0.00, 0.00] |
| B3_minus_B1 | refusal_recall | 0.00 | [0.00, 0.00] |
| B3_minus_B1 | false_refusal | 0.00 | [0.00, 0.00] |
| B3_minus_B1 | unsupported_answer_incidence | 1.25 | [0.00, 4.17] |
| B3_minus_B1 | unsupported_among_answers | 1.56 | [0.00, 5.26] |
| B3_minus_B1 | answer_coverage | 0.00 | [0.00, 0.00] |
| B3_minus_B1 | completion_rate | 0.00 | [0.00, 0.00] |
| B3_minus_B2 | recall_at_5 | 18.75 | [6.90, 32.00] |
| B3_minus_B2 | mrr_at_5 | 23.91 | [12.23, 36.39] |
| B3_minus_B2 | answer_correctness | 18.75 | [4.92, 34.05] |
| B3_minus_B2 | citation_support | 1.16 | [-1.69, 5.00] |
| B3_minus_B2 | citation_coverage | 0.00 | [0.00, 0.00] |
| B3_minus_B2 | wrong_edition_rate | 0.00 | [0.00, 0.00] |
| B3_minus_B2 | refusal_recall | -6.25 | [-15.79, 0.00] |
| B3_minus_B2 | false_refusal | -12.50 | [-26.16, -2.27] |
| B3_minus_B2 | unsupported_answer_incidence | -1.25 | [-6.41, 2.86] |
| B3_minus_B2 | unsupported_among_answers | -2.07 | [-9.62, 3.61] |
| B3_minus_B2 | answer_coverage | 11.25 | [1.54, 23.08] |
| B3_minus_B2 | completion_rate | 0.00 | [-3.19, 4.00] |
| B3_minus_A1 | recall_at_5 | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | mrr_at_5 | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | answer_correctness | -1.56 | [-4.35, 0.00] |
| B3_minus_A1 | citation_support | 0.01 | [-0.06, 0.15] |
| B3_minus_A1 | citation_coverage | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | wrong_edition_rate | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | refusal_recall | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | false_refusal | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | unsupported_answer_incidence | 0.00 | [0.00, 0.00] |
| B3_minus_A1 | unsupported_among_answers | 0.02 | [0.00, 0.11] |
| B3_minus_A1 | answer_coverage | -1.25 | [-3.53, 0.00] |
| B3_minus_A1 | completion_rate | -1.25 | [-3.53, 0.00] |
| B3_minus_A2 | recall_at_5 | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | mrr_at_5 | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | answer_correctness | -1.56 | [-8.00, 4.92] |
| B3_minus_A2 | citation_support | 0.02 | [-0.05, 0.22] |
| B3_minus_A2 | citation_coverage | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | wrong_edition_rate | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | refusal_recall | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | false_refusal | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | unsupported_answer_incidence | 0.00 | [0.00, 0.00] |
| B3_minus_A2 | unsupported_among_answers | 0.00 | [-0.13, 0.08] |
| B3_minus_A2 | answer_coverage | 0.00 | [-3.19, 4.00] |
| B3_minus_A2 | completion_rate | 0.00 | [-3.19, 4.00] |

## Planned targets and observed findings

| B3 design target | Primary observation | Assessment in this benchmark |
| --- | --- | --- |
| Recall@5 ≥0.80 | 61/64 = 0.953125 | Target met |
| Answer correctness ≥0.80 | 57/64 = 0.890625 | Target met |
| Citation support ≥0.90 | 140/141 = 0.992908 | Target met |
| False refusal ≤0.10 | 0/64 | Target met |
| 20–30 usable documents | 25 document identities | Target met |
| Two families with two formal editions each, where obtainable | No verified formal pair admitted | Scope restricted |

RQ1 receives evidence for higher Hybrid recall than Dense in this sample. BM25 has the highest observed recall. RQ2 has zero wrong-edition answers for both B3 and A1, with no observed incremental benefit. RQ3 has one unsupported answer per 80 slots for both B3 and A2, and equal refusal measures. The proposed targets were fixed design goals. The present values are recorded observations under the adjusted review protocol.

## Source-bound cases

In test-041, Dense answered with source-supported assembly torque tolerances around a 44 N m boundary. The question requested torque instrument precision, given in the source as better than ±3%. Hybrid supplied the requested fact. This illustrates how citation support and task correctness can diverge.

In test-079, Hybrid supplied values from a conductor-length table for an ambiguous follow-up. The expected action required clarification of the standard and length object. Source-supported values still failed that task.

The original source locations and question-by-question reasoning remain in the controlled local research records. These cases support diagnostic interpretation within this corpus. They do not certify engineering decisions.

## Limits and archived evidence

The shared assistant preparation and scoring workflow, six-document benchmark coverage, missing formal edition pairs, heuristic Gate and externally hosted model alias constrain interpretation. Independent scoring, wider sources and valid edition-pair comparisons remain future validation work.

The public measured JSON preserves denominators, per-category data, paired intervals and raw-result hashes. Controlled primary results, all 400 slot mappings, original-source reviews and recovery records remain locally archived. API account invoices and earlier unlogged expenditure remain outstanding. The £35 historical allocation is a reserve. The recorded chat-ledger estimate is approximately USD 0.3491.
