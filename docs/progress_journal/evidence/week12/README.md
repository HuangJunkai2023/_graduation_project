# Week 12 advance-preparation evidence

Prepared on 17 November 2026. Scheduled Week 12 covers 23–29 November under the existing autumn week mapping. This package records completed earlier work and the current preparation check, with their actual dates. Additional activity during the scheduled week should be appended when it occurs.

| ID | Source and observation | Scope |
| --- | --- | --- |
| E12-01 | [Preparation checks](preparation_checks.json) confirm the existing BAAI/bge-m3 identity and 3,341 finite, non-zero 1,024-dimensional document vectors. The index fingerprint matches the 12 November freeze. | Vector consistency checked on 17 November. No new embedding construction. |
| E12-02 | Cached Dense replay of 16 answerable development queries recovered the reference evidence at Top-5 for all 16. Sixteen top-result cosine calculations matched independent NumPy calculations within 1e-12. Reinitialising the read-only store and query cache reproduced one question's top-five order. | Existing-cache consistency. This did not restart the deployed application or contact the live provider. No API requests or formal test-set access. |
| E12-03 | [Benchmark verification](../../../../outputs/research/closing-review/benchmark_verification.json), dated 12 November, records 20 development and 80 test items, with 16 and 64 answerable items. Existing schema and review fields were inspected during preparation. | Historical benchmark preparation. Its recorded method is `assistant_source_review`, with zero independent human reviewers. No new annotation or invented student annotation time. |

The preparation check was executed by Codex. The first-person journal remains a Draft pending student review and actual publication. No meeting, supervisor feedback, working hours or course submission is inferred.

## Recheck

Run [verify_journal_basis.py](../week11/verify_journal_basis.py) using the command in the [Week 11 evidence package](../week11/README.md). It reads local records and existing cached query vectors. The new output retains its real execution time.

## Minerva-ready summary

| Check dated 17 November | Observation |
| --- | --- |
| Compatible document vectors | 3,341 at 1,024 dimensions |
| Cached development queries | 16 answerable items |
| Independent cosine calculations | 16/16 agree within tolerance |
| Dense reference evidence at Top-5 | 16/16 |
| Reinitialised cache/store ordering | Same top five for the checked question |

These are preparation observations from the current date. The 100-question benchmark and original calibration retain their 12 November identity.
