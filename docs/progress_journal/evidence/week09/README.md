# Week 9 evidence — 4 November 2026

Prepared for `WEEK_09.md`, covering work actually carried out through 4 November.
These are AI-assisted checks and document revisions for student review. They do
not establish live embedding availability, formal evaluation results, student
working hours or Minerva publication.

## Observations and limits

| Evidence | Actual observation | Limit |
| --- | --- | --- |
| E09-01: [environment.json](environment.json), [isolation_comparison.json](isolation_comparison.json) | Shared environment: seven dependency-conflict messages. A dedicated `project/qa_system/.venv` was created and the application installed. Python 3.10.12 with `-I`: dependency check passes and five modules import. | The dedicated environment without `-I` still sees ROS packages from ambient paths; use isolated mode. This is a runtime inventory, not the Week 17 benchmark freeze. Other projects' packages were not changed. |
| E09-02: [targeted_tests.json](targeted_tests.json), [transcript](targeted_tests.txt) | Twelve existing tests pass, 23 deselected; pytest reports 0.78 s. Coverage includes mocked API responses/errors, vector identity/resume and partial-batch rejection. | Existing tests were rerun, not first implemented this week. Synthetic/mock checks do not measure railway QA accuracy or live API latency. |
| E09-03: [interface_checks.json](interface_checks.json), [check script](verify_week09.py) | Embedding key, base URL and model are absent; actual configuration returns `embedding_not_configured` before HTTP dispatch. Seven mock fixtures pass: valid reordered vectors plus missing/duplicate indices, unequal dimensions, zero, non-finite and empty vectors. | Live model/endpoint identity, dimension, token use and provider billing remain unavailable. Zero live model requests were made. A configured Chat key is not an embedding service. |
| E09-04: [candidate_inventory.csv](candidate_inventory.csv), [kb_snapshot.json](kb_snapshot.json) | Nine candidate PDFs in the TB/T 2073/2074 families, eight unique hashes. Three 2010 file entries have no extracted alphanumeric characters; two are duplicate copies of the same TB/T 2073 file. The existing database has 3 documents, 503 chunks and 0 vectors. | Years/status are filename-derived candidates, not validated current editions. A 40-character page threshold only indicates text-layer presence, not correct parsing. No permissions independently confirmed; no OCR, bulk ingestion or live embedding performed. Database queried with SQLite `mode=ro`. |
| E09-05: [supervisor-requested revision record](../../../../开题材料/交大开题报告/最终检查记录.md) and Git `eb7ed4f` | The Chinese-side proposal was revised with justified prose, expanded research reasoning and three diagrams; student subsequently confirmed the supervisor signed it. Original RQs/objectives and five configurations remain unchanged. | Feedback/signing are student-provided facts. Actual feedback/signing dates and a numbered meeting were not supplied; no signature scan, Minerva receipt or Review Document approval inferred. This is separate from the English Proposal signing recorded for Week 8. |

The application/test source and `pyproject.toml` were unchanged. The ignored
project virtual environment and package metadata are local setup artifacts.
The database snapshot describes the existing corpus; it is not a claim that
503 chunks were created this week or that the Week 11 corpus target is met.

## Reproduce without replacing the dated record

From the repository root, use the dedicated environment with Python isolated
mode to avoid inherited ROS paths:

```bash
project/qa_system/.venv/bin/python -I -m pip check

project/qa_system/.venv/bin/python -I docs/progress_journal/evidence/week09/verify_week09.py \
  --output-dir /tmp/ocs_week09_repeat

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 project/qa_system/.venv/bin/python -I -m pytest \
  project/qa_system/tests/test_system.py -q \
  -k 'embedding or vector_mismatch or api_errors_redacted or deepseek_wire_contract or bad_response or timeout_is_error_not_refusal or retrieval_only_requires_no_key'
```

Use a fresh output directory. The script refuses to overwrite existing result
files; a later run must retain its actual date, revision and measurements.
Package versions are in `environment.json`; a fresh installation may resolve
different versions unless the recorded versions are deliberately reproduced.

The script never sends actual model requests. It uses HTTP mocks and synthetic
inputs even if service configuration later becomes available. A live pilot is a
separate outstanding T05 action, using only synthetic or approved input and a
recorded model/endpoint identity. No missing credentials are filled or guessed.

## Student-facing next actions

- Review the draft's first-person wording and the evidence before posting.
- Configure the three independent Embedding fields locally; do not paste keys
  into the journal or chat. Continue T05 in Week 10, before claiming a live pilot.
- Under T06, compare actual PDF/DOCX text, values, units and table locations with
  originals; check formal editions and permission provenance before M2.
- Keep this week as `Draft` until posting is actually confirmed. No hours,
  meeting number or publication date has been invented.

The small evidence table in `WEEK_09.md` can be pasted into Minerva; it contains
the observations directly, so readers do not have to follow local file paths.
