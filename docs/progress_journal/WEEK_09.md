---
title: "Progress – Week 9"
course: "ELEC3801 Individual Engineering Project, 2026–27"
student: "Junkai Huang, 201804121"
supervisor: "Deqing Huang"
course_week: 9
period_start: "2026-11-02"
period_end: "2026-11-08"
prepared_on: "2026-11-04"
recorded_through: "2026-11-04"
status: "Draft"
published_at: null
word_count_rendered_whitespace: 382
word_count_lexical: 387
proposal_tasks: ["T05", "T06", "T02", "T16"]
research_questions: ["RQ1", "RQ2"]
evidence_ids: ["E09-01", "E09-02", "E09-03", "E09-04", "E09-05"]
---

<!-- Copy only the title and seven sections below into Minerva. This draft covers actual work through 4 November, not the remaining days of Week 9. -->

# Progress – Week 9

## Objectives

I focused on T05 environment and embedding-interface readiness for RQ1, with an initial T06 corpus check and T02 clarification of the research design.

## Technical Progress

I established a dedicated Python 3.10.12 environment, recorded package versions, imported five pipeline modules and ran 12 existing interface-related tests. All passed using synthetic data and mock clients; this was not a research benchmark.

The embedding key, endpoint and model were absent. The client returned `embedding_not_configured` before dispatch. Seven synthetic response checks accepted reordered valid vectors and rejected malformed vectors. No live model request was made, so provider identity, dimensions and usage remain unverified.

I inventoried nine PDFs, finding eight unique hashes. The 2010 candidates yielded no extractable text. A read-only database check found 503 chunks and zero vectors. I also revised the research explanation and diagrams following my supervisor’s feedback.

## Problems and Approaches

The shared environment reported seven dependency conflicts. A new virtual environment still inherited ROS packages, so I used Python’s isolated mode (`-I`). The isolated dependency check passed. Missing embedding configuration remains an open T05 dependency; it is not evidence that a provider failed.

## Engineering Decisions

I retained local BM25 while withholding bulk embedding and Dense/Hybrid performance claims. I saved versions, hashes and synthetic results without credentials or standard text. I treated duplicate files, extraction quality and permission status separately rather than counting filenames as usable editions.

## Reflection

I learned to distinguish an importable application, a valid response contract and an available live service. Mock success cannot establish retrieval quality. Recording the configuration gap now is more useful than assuming that the historical Chat API check also validates embeddings.

## Plan for Next Week

Under T06, I will compare PDF/DOCX extraction with source pages, paragraphs and tables, checking values, units and chunk boundaries. I will carry forward T05: configure a permitted embedding service and verify its identity, dimensions, ordering, failures and usage before building vectors.

## Evidence

Checks dated 4 November 2026; these are readiness observations, not formal evaluation results.

| ID | Recorded observation |
| --- | --- |
| E09-01 | Shared dependencies: seven conflicts; isolated project check: passed. |
| E09-02 | Twelve existing functional tests passed; 23 deselected. |
| E09-03 | Seven mock vector checks passed; embedding unconfigured; zero live requests. |
| E09-04 | Nine candidate files, eight hashes; database: 503 chunks, zero vectors. |
| E09-05 | Research explanation and diagrams revised following supervisor feedback. |
