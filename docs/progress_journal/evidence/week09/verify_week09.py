"""Week 9 read-only checks; synthetic HTTP fixtures never call a real model API.

Run in the isolated project environment with a fresh --output-dir. Existing
evidence is not overwritten. No credentials, prompts or document text are saved.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

import httpx
import pymupdf
from ocs_qa.api import APIError, ModelClient
from ocs_qa.config import Settings

ROOT = Path(__file__).resolve().parents[4]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checks(output):
    output.mkdir(parents=True, exist_ok=True)
    names = ['environment.json', 'interface_checks.json', 'kb_snapshot.json', 'candidate_inventory.csv']
    assert not any((output / name).exists() for name in names), 'Use a fresh output directory.'
    captured = datetime.now(timezone.utc).isoformat()
    settings = Settings.load()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    common = {'captured_at_utc': captured, 'code_revision': revision,
              'actor': 'AI-assisted command execution for student review', 'actual_effort_hours': None}

    checks = subprocess.run([sys.executable, '-I', '-m', 'pip', 'check'], capture_output=True, text=True)
    shared = subprocess.run([str(ROOT / '.venv/bin/python'), '-m', 'pip', 'check'], capture_output=True, text=True)
    versions = {name: importlib.metadata.version(name) for name in
                ['ocs-qa', 'numpy', 'PyMuPDF', 'python-docx', 'python-dotenv', 'httpx', 'streamlit', 'pytest']}
    modules = ['ocs_qa.api', 'ocs_qa.store', 'ocs_qa.retrieval', 'ocs_qa.pipeline', 'ocs_qa.evaluation']
    for module in modules:
        importlib.import_module(module)
    environment = {**common, 'python': sys.version.split()[0], 'python_isolated_mode': bool(sys.flags.isolated), 'versions': versions,
                   'imported_modules': modules,
                   'project_pip_check': {'returncode': checks.returncode, 'output': checks.stdout.strip()},
                   'shared_environment_pip_check': {'returncode': shared.returncode, 'output': shared.stdout.strip()},
                   'installed_distributions': sorted(
                       f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()),
                   'pyproject_sha256': sha(ROOT / 'project/qa_system/pyproject.toml')}
    (output / 'environment.json').write_text(json.dumps(environment, ensure_ascii=False, indent=2) + '\n')

    fields = {'key': bool(settings.embedding_key), 'url': bool(settings.embedding_url),
              'model': bool(settings.embedding_model)}
    attempted_transport_calls = []

    def should_not_send(request):
        attempted_transport_calls.append(True)
        raise AssertionError('A missing-configuration check must not send HTTP.')

    guard = {'embedding_fields_present': fields, 'chat_key_present': bool(settings.chat_key)}
    if not all(fields.values()):
        try:
            ModelClient(settings, httpx.MockTransport(should_not_send)).embed(['Synthetic input; no railway text.'])
        except APIError as error:
            guard['observed_error_code'] = error.code
        assert guard.get('observed_error_code') in ['embedding_not_configured', 'missing_key']
    else:
        guard['observed_error_code'] = None
        guard['note'] = 'Configured; this script deliberately does not perform live requests.'
    assert not attempted_transport_calls
    fixtures = [
        ('reordered_valid', [{'index': 1, 'embedding': [0, 1]}, {'index': 0, 'embedding': [1, 0]}], None),
        ('missing_vector', [{'index': 0, 'embedding': [1, 0]}], 'invalid_embedding'),
        ('duplicate_index', [{'index': 0, 'embedding': [1, 0]}, {'index': 0, 'embedding': [0, 1]}], 'invalid_embedding'),
        ('unequal_dimensions', [{'index': 0, 'embedding': [1, 0]}, {'index': 1, 'embedding': [0, 1, 2]}], 'invalid_embedding'),
        ('zero_vector', [{'index': 0, 'embedding': [0, 0]}, {'index': 1, 'embedding': [0, 1]}], 'invalid_embedding'),
        ('non_finite_vector', [{'index': 0, 'embedding': [float('inf'), 0]}, {'index': 1, 'embedding': [0, 1]}], 'invalid_embedding'),
        ('empty_vectors', [{'index': 0, 'embedding': []}, {'index': 1, 'embedding': []}], 'invalid_embedding'),
    ]
    cases = []
    fake = Settings(embedding_key='synthetic-fixture-value', embedding_url='https://embedding.example/v1',
                    embedding_model='synthetic-contract-fixture')
    for name, payload, expected in fixtures:
        # Explicit raw JSON also permits the deliberate non-finite-number fixture.
        client = ModelClient(fake, httpx.MockTransport(lambda request: httpx.Response(
            200, content=json.dumps({'data': payload}).encode())))
        try:
            vectors = client.embed(['Synthetic A', 'Synthetic B'])
            assert expected is None and vectors == [[1, 0], [0, 1]]
            observed = 'accepted_and_reordered'
        except APIError as error:
            assert error.code == expected, (name, error.code)
            observed = error.code
        cases.append({'case': name, 'transport': 'httpx.MockTransport', 'observed': observed, 'passed': True})
    interface = {**common, 'real_configuration_guard': guard, 'guard_transport_calls': 0,
                 'synthetic_vector_checks': cases, 'real_api_requests': 0,
                 'live_embedding_status': 'not_verified', 'live_model_identity': None,
                 'live_vector_dimension': None, 'provider_usage': None, 'provider_billing': None}
    (output / 'interface_checks.json').write_text(json.dumps(interface, ensure_ascii=False, indent=2) + '\n')

    snapshot = {**common, 'method': 'SQLite mode=ro; no Store constructor or schema changes'}
    if settings.db_path.exists():
        with sqlite3.connect(settings.db_path.resolve().as_uri() + '?mode=ro', uri=True) as db:
            snapshot.update(documents=db.execute('SELECT COUNT(*) FROM documents').fetchone()[0],
                            chunks=db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0],
                            vectors=db.execute('SELECT COUNT(*) FROM vectors').fetchone()[0])
    else:
        snapshot['status'] = 'database_not_present'
    (output / 'kb_snapshot.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')

    fields = ['file', 'candidate_standard', 'candidate_year', 'filename_status', 'sha256', 'pages',
              'pages_with_40plus_alnum_chars', 'total_alnum_chars', 'permission_status']
    with (output / 'candidate_inventory.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for path in sorted((ROOT / 'project/task1').rglob('*.pdf')):
            match = re.search(r'(2073|2074)[ -]+(20\d{2})', path.name)
            if not match:
                continue
            with pymupdf.open(path) as pdf:
                counts = [sum(c.isalnum() for c in page.get_text()) for page in pdf]
            writer.writerow({'file': str(path.relative_to(ROOT)), 'candidate_standard': 'TB/T ' + match[1],
                             'candidate_year': match[2],
                             'filename_status': 'draft_marked' if '报批稿' in path.name else 'obsolete_marked' if '废' in path.name else 'unconfirmed',
                             'sha256': sha(path), 'pages': len(counts),
                             'pages_with_40plus_alnum_chars': sum(c >= 40 for c in counts),
                             'total_alnum_chars': sum(counts), 'permission_status': 'not_independently_confirmed'})
    assert checks.returncode == 0, 'The isolated project environment still has dependency conflicts.'
    return {'synthetic_checks_passed': len(cases), 'live_requests': 0, 'project_dependency_check': 'passed',
            'embedding_fields_present': guard['embedding_fields_present']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_checks(args.output_dir), indent=2))
