---
title: "Progress – Week 13"
course: "ELEC3801 Individual Engineering Project, 2026-27"
student: "Junkai Huang, 201804121"
supervisor: "Deqing Huang"
course_week: 13
period_start: "2026-11-30"
period_end: "2026-12-06"
prepared_on: "2026-11-17"
recorded_through: "2026-11-17"
status: "Draft"
entry_basis: "Advance preparation using completed work and a dated current recheck; scheduled week has not begun."
published_at: null
word_count_rendered_whitespace: 434
proposal_tasks: ["T07", "T08", "T09", "T16"]
research_questions: ["RQ1", "RQ2", "RQ3"]
evidence_ids: ["E13-01", "E13-02", "E13-03"]
verification_actor: "Codex"
student_review: "Pending"
actual_student_hours: null
---

<!-- Prepared in advance on 17 November. Existing calibration is dated 12 November. Keep actual activity dates and review this draft during scheduled Week 13 before publication. -->

# Progress – Week 13

## Objectives

I prepared this entry ahead of scheduled Week 13 from the Hybrid retrieval review completed on 17 November. The focus is RQ1 and the T07 benchmark work, alongside T08 and T09 boundary checks. I examined the existing fusion implementation and development-only selection record, preserving their original dates.

## Technical Progress

Hybrid combines separately normalised BM25 and Dense scores using S = (1 − w)B + wD. Each query uses the same eligible chunks for both score distributions. The implementation applies min–max normalisation, maps constant positive scores to one and other constant scores to zero, and resolves ranking ties with stable chunk identifiers.

The current replay checked 16 answerable development queries across all three retrieval methods. Each method recovered the reference evidence at rank one, although their five-result lists differed for all 16 queries. Eighty returned Hybrid scores matched the fusion formula at w = 0.50. Four normalisation checks covered empty input, a constant positive score, a zero score and a variable score range.

I revisited the 12 November calibration record. The prescribed weights 0.25, 0.50 and 0.75 tied on development Recall@5 and MRR@5, so the predefined tie rule selected 0.50. The scheduled plan places final calibration in Week 17. The existing project completed this activity early, and the review retained that actual chronology.

## Problems and Approaches

The development questions provide little discrimination between the weight candidates. Their equal retrieval scores leave uncertainty about behaviour on more varied questions. Differences in lower-ranked passages may also change the context supplied to generation. I retained the existing parameter choice and kept formal test results outside this parameter review.

## Engineering Decisions

I preserved the five declared configurations. A1 retains standard-family filtering while disabling edition checks. A2 disables the retrieval Evidence Gate and retains prompt, citation validation and error handling. The new replay used cached vectors and left the frozen corpus, selected parameters and formal result files intact.

## Reflection

The review showed that adding semantic scores does not establish a retrieval improvement by itself. A defensible comparison needs consistent candidate sets, traceable score transformations and evidence-based outcome measures. Saturated development performance also limits the confidence that can be placed in a tuning decision.

## Plan for Next Week

For scheduled Week 14, I will focus the next review on available and missing editions, conflicting year cues and follow-up changes of edition. I will retain the formal-edition-pair limitation when interpreting RQ2.

## Evidence

| ID | Dated preparation evidence |
| --- | --- |
| E13-01 | 17 November replay of 16 queries across BM25, Dense and Hybrid. |
| E13-02 | 80 formula checks and four normalisation checks passed. |
| E13-03 | 12 November weight trials tied; predefined rule selected 0.50. |
