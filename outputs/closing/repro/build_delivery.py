"""Package public code and a separately controlled local research snapshot."""
from argparse import ArgumentParser
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile


REPO = Path(__file__).resolve().parents[3]
APP = REPO / 'project/qa_system'
RESEARCH = APP / 'runtime/research'
DESTINATION = APP / 'runtime/closing_delivery'
LABELS = ('B1', 'B2', 'B3', 'A1', 'A2')


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def current_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        manifest = REPO / 'PUBLIC_MANIFEST.json'
        if manifest.is_file():
            return json.loads(manifest.read_text(encoding='utf-8'))['git_commit']
        return None


def environment_check():
    packages = {name: importlib.metadata.version(name) for name in
                ['numpy', 'pymupdf', 'python-docx', 'python-dotenv', 'httpx', 'streamlit', 'jieba', 'pytest']}
    return {'python': sys.version.split()[0], 'packages': packages,
            'git_commit': current_commit(), 'checked_at': datetime.now(timezone.utc).isoformat()}


def public_files():
    """Use an explicit source allowlist, independent of local Git-ignore state."""
    app_names = ['ocs_qa', 'tests', 'tools', '.streamlit']
    files = []
    for name in app_names:
        files.extend(p for p in (APP / name).rglob('*') if p.is_file())
    files.extend(p for p in APP.iterdir() if p.is_file())
    files.extend(Path(__file__).parent / name for name in
                 ['build_delivery.py', 'REPRODUCIBILITY_EN.md', 'DELIVERY_CHECKLIST_CN.md'])
    files.append(REPO / 'README.md')
    approved_suffixes = {'.py', '.md', '.txt', '.toml', '.ps1', '.cmd', '.example'}
    selected = []
    for path in sorted(set(files)):
        relative = path.relative_to(REPO)
        if '__pycache__' in relative.parts or '.pytest_cache' in relative.parts:
            continue
        if path.suffix.lower() not in approved_suffixes:
            continue
        if path.name == 'secrets.toml' or (path.name.startswith('.env') and path.name != '.env.example'):
            continue
        selected.append(path)
    return selected


def ensure_new(path):
    if Path(path).exists():
        raise ValueError(f'Output exists, choose a new delivery version: {path}')


def version_directory(version):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', version):
        raise ValueError('Version must be a single directory name.')
    directory = (DESTINATION / version).resolve()
    if not directory.is_relative_to(DESTINATION.resolve()):
        raise ValueError('Delivery path escapes the local controlled directory.')
    return directory


def write_public(version):
    version_directory(version)
    destination = Path(__file__).parent / f'OCS_Public_Code_{version}.zip'
    ensure_new(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = public_files()
    from dotenv import dotenv_values
    configured_keys = [value.encode() for key, value in dotenv_values(APP / '.env').items()
                       if key.endswith('_API_KEY') and value and len(value) > 8]
    if any(secret in path.read_bytes() for path in files for secret in configured_keys):
        raise ValueError('A configured API key was found in an allowed source file.')
    documentation = [REPO / 'README.md', APP / 'README.md']
    documentation_snapshot = []
    for path in documentation:
        try:
            changed = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', str(path.relative_to(REPO))],
                                     cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        except FileNotFoundError:
            changed = None
        documentation_snapshot.append({'path': path.relative_to(REPO).as_posix(), 'sha256': digest(path),
                                       'working_tree_update': None if changed is None else changed == 1})
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'git_commit': current_commit(),
                'snapshot_current_docs': documentation_snapshot,
                'environment': environment_check(),
                'files': [{'path': p.relative_to(REPO).as_posix(), 'bytes': p.stat().st_size,
                           'sha256': digest(p)} for p in files]}
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(REPO).as_posix())
        archive.writestr('PUBLIC_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        forbidden = [name for name in archive.namelist() if any(
            token in Path(name).parts for token in ['runtime', '.venv', '.venv-win', 'task1', 'task2'])]
        if forbidden:
            raise ValueError('Unexpected private path in public archive.')
    receipt = {'path': str(destination), 'sha256': digest(destination), 'files': len(files),
               'bytes': destination.stat().st_size, 'archive_integrity': 'passed',
               'configured_api_key_scan': 'passed'}
    (destination.parent / f'public_receipt_{version}.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    return receipt


def completed_inputs(freeze, results, summary, grades):
    paths = [freeze / 'manifest.json', freeze / 'questions.jsonl', freeze / 'calibration.json', summary, grades]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise ValueError('Research artefacts are still pending: ' + ', '.join(missing))
    for label in LABELS:
        path = results / f'{label}.jsonl'
        if not path.is_file() or len(read_rows(path)) != 80:
            raise ValueError(f'Expected 80 actual primary results in {label}.jsonl')
    data = json.loads(summary.read_text(encoding='utf-8'))
    if data.get('status') not in {'human_scored', 'source_reviewed', 'scored'}:
        raise ValueError('A completed reviewed metric summary is required.')
    from ocs_qa.study import canonical_hash
    freeze_manifest = json.loads((freeze / 'manifest.json').read_text(encoding='utf-8'))
    if canonical_hash(freeze_manifest) != data['freeze_sha256']:
        raise ValueError('Measured summary belongs to a different freeze.')
    if canonical_hash(read_rows(grades)) != data['grades_sha256']:
        raise ValueError('Reviewed grades changed after metric computation.')
    for filename, expected in data['run_files_sha256'].items():
        if digest(results / filename) != expected:
            raise ValueError('Measured result file has changed: ' + filename)
    return data


def sqlite_backup(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as original, sqlite3.connect(destination) as copied:
        original.backup(copied)
        if copied.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('SQLite backup integrity failed.')


def write_controlled(version, freeze, results, summary, grades):
    measured = completed_inputs(freeze, results, summary, grades)
    destination = version_directory(version) / 'controlled_research'
    ensure_new(destination)
    destination.mkdir(parents=True)
    shutil.copytree(freeze, destination / 'freeze')
    shutil.copytree(results, destination / 'results', ignore=shutil.ignore_patterns('execution.lock', 'inflight.json'))
    shutil.copy2(summary, destination / 'measured_results.json')
    shutil.copy2(grades, destination / 'grades.jsonl')
    calibration = json.loads((freeze / 'calibration.json').read_text(encoding='utf-8'))
    selection_evidence = Path(calibration['selection_evidence'])
    if not selection_evidence.is_absolute():
        selection_evidence = freeze / selection_evidence
    if selection_evidence.is_file():
        shutil.copytree(selection_evidence.parent, destination / 'development_calibration')
    for name in ['api_usage.jsonl', 'budget_review.json']:
        source = RESEARCH / name
        if source.is_file():
            shutil.copy2(source, destination / name)
    sqlite_backup(RESEARCH / 'kb.sqlite3', destination / 'kb.sqlite3')
    with sqlite3.connect(destination / 'kb.sqlite3') as database:
        documents = [json.loads(row[0]) for row in database.execute('SELECT payload FROM documents')]
    source_map = []
    for document in documents:
        original = Path(document['path'])
        if digest(original) != document['id']:
            raise ValueError('Source hash changed: ' + document['name'])
        relative = Path('source_files') / document['id'] / original.name
        copied = destination / relative
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, copied)
        source_map.append({'document_id': document['id'], 'path': relative.as_posix()})
    (destination / 'source_map.json').write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding='utf-8')
    for relative in ['benchmark/candidates.jsonl', 'benchmark/candidates.reviews.jsonl']:
        source = RESEARCH / relative
        if source.is_file():
            copied = destination / relative
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, copied)
    restore_database = destination.parent / 'restore_check.sqlite3'
    sqlite_backup(destination / 'kb.sqlite3', restore_database)
    with sqlite3.connect(restore_database) as database:
        for row in source_map:
            record = database.execute('SELECT payload FROM documents WHERE id=?', (row['document_id'],)).fetchone()
            document = json.loads(record[0])
            document['path'] = str((destination / row['path']).resolve())
            database.execute('UPDATE documents SET payload=? WHERE id=?', (json.dumps(document, ensure_ascii=False), document['id']))
    from ocs_qa.config import Settings
    from ocs_qa.store import Store
    from ocs_qa.study_run import verify_freeze
    manifest = json.loads((destination / 'freeze/manifest.json').read_text(encoding='utf-8'))
    restored = Store(replace(Settings.load(restore_database), **manifest['config']))
    verify_freeze(destination / 'freeze', restored)
    for document in restored.documents():
        if digest(document['path']) != document['id']:
            raise ValueError('Restored source mapping failed.')
    snapshot_manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'git_commit': current_commit(),
        'freeze_sha256': measured['freeze_sha256'], 'restore_verification': 'passed',
        'documents': len(documents), 'test_slots': 400,
        'files': [{'path': p.relative_to(destination).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)}
                  for p in sorted(destination.rglob('*')) if p.is_file()]}
    (destination / 'SNAPSHOT_MANIFEST.json').write_text(json.dumps(snapshot_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    archive = destination.parent / 'OCS_Controlled_Research.zip'
    ensure_new(archive)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for path in destination.rglob('*'):
            if path.is_file():
                output.write(path, path.relative_to(destination).as_posix())
    with zipfile.ZipFile(archive) as output:
        if output.testzip() is not None:
            raise ValueError('Controlled archive CRC check failed.')
    receipt = {'path': str(archive), 'bytes': archive.stat().st_size, 'sha256': digest(archive),
               'restore_verification': 'passed', 'source_files_checked': len(documents),
               'public_distribution': False}
    (archive.parent / 'controlled_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    return receipt


def restore_snapshot(snapshot, output_database):
    snapshot = Path(snapshot).resolve()
    output_database = Path(output_database).resolve()
    ensure_new(output_database)
    index = json.loads((snapshot / 'SNAPSHOT_MANIFEST.json').read_text(encoding='utf-8'))
    for row in index['files']:
        path = (snapshot / row['path']).resolve()
        if not path.is_relative_to(snapshot) or digest(path) != row['sha256']:
            raise ValueError('Controlled snapshot content changed: ' + row['path'])
    sqlite_backup(snapshot / 'kb.sqlite3', output_database)
    with sqlite3.connect(output_database) as database:
        for row in json.loads((snapshot / 'source_map.json').read_text(encoding='utf-8')):
            path = (snapshot / row['path']).resolve()
            if not path.is_relative_to(snapshot) or digest(path) != row['document_id']:
                raise ValueError('Selected source hash mismatch.')
            payload = database.execute('SELECT payload FROM documents WHERE id=?', (row['document_id'],)).fetchone()
            document = json.loads(payload[0])
            document['path'] = str(path)
            database.execute('UPDATE documents SET payload=? WHERE id=?', (json.dumps(document, ensure_ascii=False), row['document_id']))
    from ocs_qa.config import Settings
    from ocs_qa.store import Store
    from ocs_qa.study_run import verify_freeze
    freeze = snapshot / 'freeze'
    manifest = json.loads((freeze / 'manifest.json').read_text(encoding='utf-8'))
    restored = Store(replace(Settings.load(output_database), **manifest['config']))
    verify_freeze(freeze, restored)
    return {'restored_database': str(output_database), 'source_documents': len(restored.documents()),
            'snapshot_file_hashes': 'passed', 'freeze_verification': 'passed', 'api_requests': 0}


def main():
    parser = ArgumentParser(description='Build reproducible OCS closing packages')
    parser.add_argument('action', choices=['check', 'public', 'controlled', 'restore'])
    parser.add_argument('--version', default='closing-v1')
    parser.add_argument('--freeze', type=Path, default=RESEARCH / 'freezes/closing-v1')
    parser.add_argument('--results', type=Path, default=RESEARCH / 'results')
    parser.add_argument('--summary', type=Path, default=RESEARCH / 'measured_results.json')
    parser.add_argument('--grades', type=Path, default=RESEARCH / 'scoring/grades.jsonl')
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--output-db', type=Path)
    args = parser.parse_args()
    if args.action == 'check':
        result = environment_check()
        result['public_source_files'] = len(public_files())
    elif args.action == 'public':
        result = write_public(args.version)
    elif args.action == 'restore':
        if not args.snapshot or not args.output_db:
            parser.error('restore requires --snapshot and --output-db')
        result = restore_snapshot(args.snapshot, args.output_db)
    else:
        result = write_controlled(args.version, args.freeze, args.results, args.summary, args.grades)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
