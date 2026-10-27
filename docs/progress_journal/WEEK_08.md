---
title: "Progress – Week 8"
course: "ELEC3801 Individual Engineering Project, 2026–27"
student: "Junkai Huang, 201804121"
supervisor: "Deqing Huang"
course_week: 8
period_start: "2026-10-26"
period_end: "2026-11-01"
prepared_on: "2026-10-27"
recorded_through: "2026-10-27"
status: "Draft"
published_at: null
proposal_tasks: ["T04", "T16"]
evidence_ids: ["E08-01", "E08-02", "E08-03", "E08-04"]
---

<!-- Copy the title and seven sections below into Minerva. Metadata is for local maintenance. -->

# Progress – Week 8

## Objectives

I aimed to complete the Proposal review under T04 and organise the research workflow under T16. My project will evaluate evidence-based question answering for overhead contact system standards.

## Technical Progress

I completed the final review of the research design, Gantt chart, resources, ethics, safety and risks. Deqing Huang accepted the Proposal, and we both signed it on 26 October. I checked it against the assessment criteria before submission.

I confirmed five planned configurations: B1 BM25, B2 Dense and B3 Hybrid address RQ1 by comparing exact-term and semantic retrieval. A1 removes edition checks while retaining standard-family filtering for RQ2; A2 removes the retrieval gate while retaining citation validation for RQ3. These ablations isolate wrong-edition handling and the gate’s effect on unsupported answers and false refusals.

I checked the metric definitions: Recall@5 and MRR@5 use pre-gate rankings for 64 answerable test items; correctness uses the same items; refusal recall uses 16 unanswerable items. Citation support is assessed per cited claim, wrong-edition rate uses unambiguously edition-specified questions, and false refusal uses answerable items. API failures remain errors rather than justified refusals.

## Problems and Approaches

The feasibility review identifies unverified embedding access and limited usable edition pairs. I retained API verification and corpus auditing before M2, with a limited edition case study if necessary. Performance thresholds remain planning targets; I have no formal evaluation results to report.

## Engineering Decisions

I retained the plan to source-check 100 questions, split into 20 development and 80 fixed test items, keeping related facts and dialogues together. Parameter selection will use development data only. Automatic citation checks will remain separate from manual assessment of semantic support, values, units and conditions.

## Reflection

Finalising the plan clarified that a working prototype does not establish research effectiveness. I need reproducible comparisons and distinct records of retrieval failures, software errors and justified refusals; otherwise favourable-looking metrics could conceal weaknesses.

## Plan for Next Week

For T05 and T06, I will verify the environment and separate embedding endpoint with permitted pilot inputs, record model identity, dimensions, failures and usage, and begin document and permission checks. T02 reading will inform these choices.

## Evidence

These records support planning and review, not measured performance.

| ID | Source and recorded outcome |
| --- | --- |
| E08-01 | Proposal pp. 2–3: RQ1–3, five configurations, metric definitions and development/test separation. |
| E08-02 | Proposal pp. 4–6: M2 Week 11, integration Week 16, freeze Week 17; resources and budget. |
| E08-03 | Handbook rubric and my confirmed pre-submission check: objectives, planning, ethics and risks. |
| E08-04 | My confirmation recorded on 27 October: supervisor acceptance and both signatures completed on 26 October 2026. |
