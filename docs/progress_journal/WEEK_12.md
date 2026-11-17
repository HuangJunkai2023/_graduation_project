---
title: "Progress – Week 12"
course: "ELEC3801 Individual Engineering Project, 2026-27"
student: "Junkai Huang, 201804121"
supervisor: "Deqing Huang"
course_week: 12
period_start: "2026-11-23"
period_end: "2026-11-29"
prepared_on: "2026-11-17"
recorded_through: "2026-11-17"
status: "Draft"
entry_basis: "Advance preparation using completed work and a dated current recheck; scheduled week has not begun."
published_at: null
word_count_rendered_whitespace: 421
proposal_tasks: ["T07", "T08", "T09", "T16"]
research_questions: ["RQ1", "RQ2", "RQ3"]
evidence_ids: ["E12-01", "E12-02", "E12-03"]
verification_actor: "Codex"
student_review: "Pending"
actual_student_hours: null
---

<!-- Prepared in advance on 17 November. The English opening states the actual review date. Update with any real Week 12 activity before publication. No future work, meeting or submission is recorded as completed. -->

# Progress – Week 12

## Objectives

I prepared this entry in advance of scheduled Week 12, using the Dense retrieval review completed on 17 November. The focus follows T07, with parallel T08 edition handling and T09 evidence-check preparation. I examined how semantic ranking connects to the existing corpus and benchmark, whose implementation and initial review had already progressed ahead of the schedule.

## Technical Progress

The index uses BAAI/bge-m3 with 1,024-dimensional document vectors. The check confirmed compatible model identities across all 3,341 stored vectors. Each vector contained finite values and had a non-zero norm. Query vectors were loaded from the existing identity-keyed cache.

For the 16 answerable development questions, Dense retrieval returned reference evidence within Top-5 in every case. Sixteen top-result cosine scores were independently recalculated and agreed with the retrieval output within the numerical tolerance. Reloading the stored records and query cache reproduced the first question's five-result ordering. The checks used no external API requests.

I also reviewed the existing question structure. It retains the requested standard and edition, source position, continuous evidence span, required facts and conversation history. The planned split remains 20 development and 80 test questions, with 16 and 64 answerable items respectively.

## Problems and Approaches

Semantic similarity can retrieve passages about a related component or neighbouring requirement. A high cosine score therefore requires examination of the requested fact, numerical units and applicability conditions. The development replay establishes consistency on a small sample. It does not establish general superiority over BM25. Cached retrieval also leaves current live-service availability outside this check.

## Engineering Decisions

I retained the same eligible corpus and Top-5 limit for lexical and semantic retrieval. Model identity remains part of the cache key. Edition filtering precedes ranking, and evidence sufficiency is assessed separately. These choices preserve comparability and make the source of a failure easier to inspect.

## Reflection

I found the distinction between semantic proximity and sufficient evidence central to the benchmark design. Questions must identify the required fact precisely enough for a reviewer to distinguish a relevant-looking passage from an adequate answer. Keeping source locations and necessary conditions in the record supports that judgement.

## Plan for Next Week

During scheduled Week 13, I will revisit the three-method comparison, normalisation boundaries and Hybrid weight rationale. Any additional observations will retain their actual dates, while the existing calibration and formal experiment remain identifiable.

## Evidence

| ID | Dated preparation evidence |
| --- | --- |
| E12-01 | 17 November check of 3,341 compatible, finite, non-zero vectors. |
| E12-02 | 16 cosine checks passed; Dense reference-evidence retrieval 16/16 at Top-5. |
| E12-03 | Existing benchmark schema and fixed 20/80 split reviewed. |
