---
title: "Progress – Week 11"
course: "ELEC3801 Individual Engineering Project, 2026-27"
student: "Junkai Huang, 201804121"
supervisor: "Deqing Huang"
course_week: 11
period_start: "2026-11-16"
period_end: "2026-11-22"
prepared_on: "2026-11-17"
recorded_through: "2026-11-17"
status: "Draft"
published_at: null
word_count_rendered_whitespace: 416
proposal_tasks: ["T06", "T16"]
research_questions: ["RQ1", "RQ2"]
evidence_ids: ["E11-01", "E11-02", "E11-03"]
activity_basis: "Read-only recheck on 17 November; original corpus preparation on 12 November remains historical."
verification_actor: "Codex"
student_review: "Pending"
actual_student_hours: null
---

<!-- Copy the English title and seven sections after checking the draft. Technical checks were executed by Codex on 17 November. Publication and student authorship review remain pending. -->

# Progress – Week 11

## Objectives

I reviewed the existing corpus and BM25 baseline against T06 and the Week 11 M2 milestone. My focus was whether document identities, source locations, indexing and edition coverage provide a defensible basis for RQ1 and RQ2. The corpus had already been prepared on 12 November. This entry records its recheck on 17 November.

## Technical Progress

The read-only database check confirmed 25 independently identified documents, 3,341 text chunks and 3,341 stored vectors. All 25 source-file hashes matched their database identities. The corpus and numerical-vector fingerprints also matched the existing research freeze. The vectors had 1,024 dimensions and finite, non-zero values.

I reviewed how BM25 uses shared Chinese tokenisation, term frequency and document frequency to rank eligible passages. Standard-family and edition constraints establish the candidate set before ranking. The cached development replay recovered the reference evidence within the first five results for all 16 answerable development questions. These observations concern retrieval and source matching. No new generated-answer accuracy was measured.

## Problems and Approaches

The main remaining corpus limitation is the absence of a verified same-family formal edition pair. The document-count objective has been met, while the intended edition coverage remains incomplete. I retained this distinction in the M2 assessment and the RQ2 scope. Different files and separately numbered parts require their own identities, and duplicate copies cannot increase edition coverage.

## Engineering Decisions

I retained the frozen corpus and existing preprocessing for the baseline check. The new verification used read-only database access and previously cached query vectors. This preserved the experiment records and required zero external API requests. Source identities and locations remain attached to retrieved passages so that later answer checking can return to the original document.

## Reflection

The review reinforced that a complete index and a representative evaluation collection are separate achievements. Recovering evidence for every small development example provides a useful consistency check, but broader retrieval claims require the controlled evaluation. The missing edition pairs also affect the interpretation of RQ2 even when the software handles unavailable years correctly.

## Plan for Next Week

For the scheduled Week 12 review, I will examine Dense retrieval on the same corpus, check query/document vector compatibility and cosine calculations, and revisit the benchmark schema and evidence fields. I will carry the edition-pair limitation into that work.

## Evidence

| ID | Observation recorded on 17 November |
| --- | --- |
| E11-01 | 25 source hashes matched; 3,341 chunks and vectors retained. |
| E11-02 | BM25 found reference evidence for 16/16 answerable development items at Top-5. |
| E11-03 | Zero confirmed formal edition pairs; M2 edition-coverage limitation retained. |
