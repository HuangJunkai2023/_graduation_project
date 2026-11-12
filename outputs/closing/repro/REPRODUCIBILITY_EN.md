# OCS project reproduction and handover

This guide accompanies Junkai Huang's overhead contact system document question-answering project. Run commands from the extracted project root in Windows PowerShell. The recorded environment uses Python 3.12.7.

## Install the recorded environment

```powershell
py -3.12 -m venv project/qa_system/.venv-win
Push-Location project/qa_system
& ./.venv-win/Scripts/python.exe -m pip install -r requirements-lock-windows.txt
Pop-Location
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 outputs/closing/repro/build_delivery.py check
```

`requirements-lock-windows.txt` records installed package versions and installs the local application in editable mode. The package includes `pyproject.toml`, native Python source, resource dictionaries, automated checks, Streamlit applications and Windows launch scripts.

## Configure and open the application

On a fresh extraction, copy `project/qa_system/.env.example` to `project/qa_system/.env`. Enter the appropriate account keys locally. The research configuration uses DeepSeek `deepseek-flash` and SiliconFlow `BAAI/bge-m3` at the endpoints below.

```dotenv
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3
VECTOR_WEIGHT=0.50
MIN_LEXICAL_COVERAGE=0.20
MIN_COSINE_SIMILARITY=0.50
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/qa_system/start_windows.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File project/qa_system/start_windows.ps1 -Review
```

The question-answering page opens at `http://127.0.0.1:8501` and the review workspace at `http://127.0.0.1:8502`. The application can import permitted PDF/DOCX files and perform local BM25 retrieval. Dense/Hybrid query embedding and answer generation use their configured remote services. Source permissions are selected in the knowledge-base page.

## Check the software

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m pytest project/qa_system/tests -q
```

Tests use isolated fixtures and mocked service responses. The actual interface and research runs have separate dated receipts. The final test count and commit should be read from the accompanying delivery receipt.

## Restore the controlled research snapshot

The controlled package contains the selected source files, a consistent SQLite backup, the frozen benchmark/configuration, primary results, review grades and measured summary. Obtain it through the project's authorised local handover. Extract the archive into an accessible directory and retain that location because the restored knowledge base points to the extracted source files.

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 outputs/closing/repro/build_delivery.py restore --snapshot 'D:/OCS_Controlled_Research' --output-db project/qa_system/runtime/restored/kb.sqlite3
```

The restore command checks every snapshot file against its SHA-256 manifest, copies the SQLite database, updates source paths by stable document ID, and verifies the freeze against the recorded code, runtime, corpus, numerical vectors and model settings. It performs zero external model requests. Choose a new output database path for each restore check.

To use the restored knowledge base in the application, set `OCS_DB_PATH` in the local `.env` to its absolute path. The closing-v1 selected weight is 0.50, the lexical coverage threshold is 0.20, and the raw cosine threshold is 0.50. These values are recorded in `freeze/calibration.json` and `freeze/manifest.json` and included in the configuration block above. Set them locally before restarting the application.

## Recompute statistics from the retained outputs

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research summarize --runs 'D:/OCS_Controlled_Research/results' --grades 'D:/OCS_Controlled_Research/grades.jsonl' --output project/qa_system/runtime/restored/recomputed_summary.json
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research report --results project/qa_system/runtime/restored/recomputed_summary.json --output project/qa_system/runtime/restored/Recomputed_Experiment_Report_EN.md
```

These commands reuse the retained primary outputs and source-review decisions. They compute metric numerators/denominators, category estimates, paired group-bootstrap differences using seed 3801 and 2000 replicates, and a supplementary Markdown report. Zero-denominator metrics retain `null` or N/A. Freeze and run-file hashes bind the reported observations to their source records.

For a separately authorised live repeat, use the `research run` command with a new result directory and a current budget record. Account usage, provider availability and remote model versions affect such a repeat. The primary study retains its original first-attempt outcomes and separately records recovery attempts.

## Review method and study boundaries

The closing benchmark and output checks use `assistant_source_review`, with the actual executing assistant recorded as Codex. The work includes two source-review passes on candidate questions and configuration-blinded review of displayed answers and their evidence. The same assistant workflow contributed to benchmark refinement and output grading, which introduces a reviewer-dependence limitation. The experimental record retains the method adjustment from the Proposal's planned human checking.

The selected corpus is fixed to available permitted files. Formal edition-pair availability and the mixture of observed historical and hypothetical missing-year requests are described in the measured report. Use the project for document learning and query support, with its evidence and stated study boundaries.

## Build and verify the handover archives

Run after the primary experiment and scoring summary have completed.

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 outputs/closing/repro/build_delivery.py public --version closing-v1
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 outputs/closing/repro/build_delivery.py controlled --version closing-v1
```

The default freeze is `runtime/research/freezes/closing-v1`, with primary results in `runtime/research/results`, the summary in `runtime/research/measured_results.json`, and grades in `runtime/research/scoring/grades.jsonl`. Explicit command options select a different accepted run version.

The public archive and receipt are written under `outputs/closing/repro/`. The controlled archive and receipt are written under `project/qa_system/runtime/closing_delivery/closing-v1/`. The public code archive uses an explicit source allowlist and checks that configured API keys are absent. The controlled archive retains the private research material and is handled through the authorised handover. Each archive receives a SHA-256 digest and ZIP integrity check. The controlled build also verifies a restored database with relocated source paths.
