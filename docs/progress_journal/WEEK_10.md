---
title: "Progress – Week 10"
course: "ELEC3801 Individual Engineering Project, 2026-27"
student: "Junkai Huang, 201804121"
supervisor: "Deqing Huang"
course_week: 10
period_start: "2026-11-09"
period_end: "2026-11-15"
prepared_on: "2026-11-10"
recorded_through: "2026-11-10"
status: "Draft"
published_at: null
word_count_rendered_whitespace: 448
proposal_tasks: ["T05", "T06", "T16"]
research_questions: ["RQ1", "RQ2"]
evidence_ids: ["E10-01", "E10-04", "E10-05"]
---

<!-- Review draft aligned with Proposal T05/T06. No unreported results or implementation dates are inferred. -->

# Progress – Week 10

## Objectives

I organised this week's review around T06 corpus preparation and indexing, alongside T05 baseline and embedding readiness. The focus was document processing and metadata, preparing for the Week 11 corpus/baseline milestone. As the overall implementation is already largely complete, this entry reviews the processing approach rather than presenting each component as newly developed this week.

## Technical Progress

I revisited the Proposal's requirements for converting PDF and DOCX standards into retrievable evidence. The workflow links extraction, chunking and indexing with document identifiers, editions and source locations. PDF citations need file-page references; DOCX citations need paragraph or table locations.

I clarified why extraction and chunking must preserve numerical values, units and applicability conditions together. A passage may contain a relevant term yet become misleading if a condition is separated from its requirement. This connects document preparation directly to retrieval quality and subsequent answer checking.

I also clarified the distinction between duplicate files and different formal editions. Hashes support duplicate detection, while standard identifiers and version information establish the edition context. This week's defence preparation helped communicate these relationships without implying that illustrative screens demonstrate validated performance.

## Problems and Approaches

The main processing risks are missing text, damaged table structure and loss of context across chunk boundaries. I treated these as review criteria rather than assuming that successful extraction guarantees usable evidence. File availability also does not establish permission for external processing. This entry does not attach new extraction counts, live API results or measured accuracy to those design considerations.

## Engineering Decisions

I retained source locations and edition metadata as part of the evidence representation, rather than storing plain text alone. The same eligible chunks and preprocessing must support BM25, Dense and Hybrid comparisons. I kept OCR and model training outside the agreed scope and retained explicit exclusion or replacement of unsuitable material.

## Reflection

Reviewing the processing workflow reinforced that answer reliability begins before generation. Better wording from DeepSeek cannot recover a missing unit or repair incorrect edition metadata. I therefore see corpus quality and traceability as prerequisites for interpreting the three research questions, rather than merely preparation for the interface.

## Plan for Next Week

For Week 11, I will organise the corpus and BM25 baseline review against M2: the 20–30-document target, permissions, duplicate handling, usable edition pairs, evidence locations and index consistency. I will summarise the existing implementation against these criteria and record any remaining limitations before the later benchmark and controlled-evaluation stages.

## Evidence

| ID | Basis and interpretation |
| --- | --- |
| E10-01 | Defence materials explain the document-to-answer workflow; illustrations are labelled. |
| E10-04 | Student confirmation on 10 November: project largely complete; no detailed test figures supplied. |
| E10-05 | Proposal pp.2?5 and 7 reviewed for T05/T06, source tracing and M2 requirements. |
