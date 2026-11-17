# Week 11 evidence

Prepared on 17 November 2026 for the current Week 11 draft. The original corpus construction and research freeze were completed on 12 November. The observations below describe a new, read-only consistency check. Actual student working hours and Minerva publication remain unconfirmed.

| ID | Method and actual observation | Scope |
| --- | --- | --- |
| E11-01 | [Verification](verification.json) read the SQLite database in `mode=ro`, checked all 25 source-file hashes, and matched corpus/vector fingerprints to the 12 November freeze. It found 3,341 chunks and 3,341 compatible 1,024-dimensional, finite, non-zero vectors. | Current index integrity and source identity. Original construction remains dated 12 November. Processing permissions were recorded for all 25 documents. This check does not provide independent copyright or standard-validity certification. |
| E11-02 | Existing BM25 was replayed against the 16 answerable development questions. All reference evidence was recovered within Top-5. Shared tokenisation and edition-before-ranking logic were inspected in the existing source. | A development consistency check after the completed study. No new answer generation, test-set access or formal performance experiment. |
| E11-03 | [Corpus review](../../../../outputs/research/corpus/review_summary.md) and [source observations](../../../../outputs/research/corpus/cover_observations.json) retain the formal-version assessment. The admitted corpus has no verified same-family formal edition pair. | The document count meets the planned range. The edition-pair objective remains unmet and constrains M2/RQ2. |

## Reproduce the checks

From the repository root, using the existing project environment and local research records, run the following command.

```powershell
& project/qa_system/.venv-win/Scripts/python.exe -X utf8 docs/progress_journal/evidence/week11/verify_journal_basis.py
```

The script also writes the dated preparation checks used by Weeks 12 and 13. It opens SQLite read-only and uses existing query-vector cache files. A missing cache file fails locally. The script has no HTTP client or model-generation path. It leaves the frozen package, selected parameters and formal results intact.

The actual executor of the check was Codex. First-person journal prose is a student-review draft. The evidence records preserve this provenance, the actual activity date and zero API requests. Source texts and private question wording remain in the ignored research directory.

## Minerva-ready summary

| Item checked on 17 November | Observation |
| --- | --- |
| Source identities | 25/25 file hashes match |
| Corpus and vector fingerprints | Match the 12 November freeze |
| Index | 3,341 chunks and 3,341 vectors |
| BM25 development evidence retrieval | 16/16 answerable items at Top-5 |
| Formal same-family edition pairs | 0 admitted |

The summary can accompany the journal text after student review. Publication and supervisor endorsement require their actual records.
