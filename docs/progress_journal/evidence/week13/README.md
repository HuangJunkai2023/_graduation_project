# Week 13 advance-preparation evidence

Prepared on 17 November 2026. Scheduled Week 13 covers 30 November–6 December under the existing autumn mapping. The draft uses an actual current replay and clearly dated prior calibration. The weekly plan retains its original task and milestone dates.

| ID | Source and observation | Scope |
| --- | --- | --- |
| E13-01 | [Preparation checks](preparation_checks.json) retain chunk-ID rankings for the same 16 answerable development queries under BM25, Dense and Hybrid. All methods had Recall@5 and MRR@5 of 1.0. Their five-result lists differed on all 16 questions. | Development replay on 17 November, after the original study. The source passages and private question text are excluded. No new independent RQ1 conclusion. |
| E13-02 | The current replay independently recomputed all 80 returned Hybrid scores at w=0.50, matching `(1-w)B+wD` within 1e-12. Four normalisation cases passed, covering empty, constant-positive, zero and variable inputs. | Arithmetic and edge-case checks. Source inspection confirmed candidate-set min–max and stable chunk-ID tie ordering. These checks do not establish answer correctness. |
| E13-03 | [Original selection evidence](../../../../outputs/research/closing-experiment/selection_evidence.json) records 0.25, 0.50 and 0.75 tied on development Recall@5 and MRR@5. The predefined tie rule chose 0.50. [Calibration](../../../../outputs/research/closing-experiment/calibration.json) is dated 12 November. | Historical early completion of a task planned for Week 17. No new tuning, parameter activation or test-result-based choice took place in this journal preparation. |

The check was executed by Codex using read-only SQLite and existing query caches. The first-person journal remains subject to student review. Independent human annotation, personal study time, new supervisor feedback and publication are not established by this preparation.

## Recheck

Use [verify_journal_basis.py](../week11/verify_journal_basis.py) as described in the [Week 11 evidence package](../week11/README.md). Its current output includes provenance, fingerprint and zero-API fields. The package does not modify research code or formal results.

## Minerva-ready summary

| Development check | Observation |
| --- | --- |
| Same-query comparison | 16 questions × 3 methods |
| Top-5 evidence recall | 1.0 for each method |
| Queries with different five-result lists | 16 |
| Hybrid formula checks | 80/80 passed |
| Normalisation edge cases | 4/4 passed |
| Existing selected weight | 0.50, selected on 12 November |

The evidence supports a review of fusion mechanics and tuning limits. Scheduled Week 13 activity can be added with its actual date before publication.
