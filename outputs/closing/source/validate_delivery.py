"""Check delivered artifacts against their receipts and current study identity."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import posixpath
import re
import subprocess
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
CLOSING = ROOT / 'outputs/closing'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_markdown_links(path):
    missing = []
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if target.startswith(('http:', 'https:', '#')):
            continue
        if not (path.parent / target.split('#')[0]).exists():
            missing.append(target)
    assert not missing, (str(path), missing)


def main():
    measured = read_json(ROOT / 'outputs/research/closing-experiment/measured_results.json')
    assert measured['status'] == 'source_reviewed'
    assert measured['review_methods'] == {'assistant_source_review': 296}
    assert measured['configurations']['B3']['recall_at_5']['numerator'] == 61
    assert measured['configurations']['B3']['answer_correctness']['numerator'] == 57
    report = read_json(CLOSING / 'source/generated/Final_Report_QA.json')
    assert [row['pages'] for row in report['artifacts']] == [5, 8]
    for row in report['artifacts']:
        for extension in ['docx', 'pdf']:
            assert digest(CLOSING / 'source/generated' / (row['artifact'] + '.' + extension)) == row[extension + '_sha256']
    viva = read_json(CLOSING / 'viva/validation/final_validation.json')
    assert (viva['main_slides'], viva['backup_slides'], viva['bilingual_notes']) == (15, 3, 18)
    namespace = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    with zipfile.ZipFile(CLOSING / 'viva/OCS_Viva_EN.pptx') as archive:
        assert archive.testzip() is None
        slides = [name for name in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)]
        notes = []
        for slide in slides:
            relationship_path = posixpath.join(posixpath.dirname(slide), '_rels', posixpath.basename(slide) + '.rels')
            relationships = ET.fromstring(archive.read(relationship_path))
            target = next(node.get('Target') for node in relationships if node.get('Type').endswith('/notesSlide'))
            notes.append(posixpath.normpath(posixpath.join(posixpath.dirname(slide), target)))
        assert len(slides) == len(notes) == 18
        for name in notes:
            text = ' '.join(node.text or '' for node in ET.fromstring(archive.read(name)).findall('.//a:t', namespace))
            assert re.search(r'[\u4e00-\u9fff]', text) and 'English' in text
    video = read_json(CLOSING / 'video/qa/validation.json')
    assert digest(CLOSING / 'video' / video['video']) == video['video_sha256']
    assert video['full_decode_exit_code'] == 0 and not video['decode_errors']
    assert video['browser_playback']['ended'] and video['browser_playback']['duration'] == 240
    assert video['browser_playback']['width'] == 1280 and video['browser_playback']['height'] == 720
    assert not video['student_narration_present'] and not video['audio_stream_present']
    repro = read_json(CLOSING / 'repro/verification_receipt.json')
    assert repro['recomputed_summary_identical'] and repro['api_requests'] == 0
    assert repro['extracted_source_tests']['passed'] == 109
    public_zip = CLOSING / 'repro/OCS_Public_Code_closing-v1.zip'
    assert digest(public_zip) == repro['public_zip_sha256']
    for path in [CLOSING / 'README.md', ROOT / 'outputs/research/STATUS_CN.md']:
        check_markdown_links(path)
    services = {}
    for port in [8501, 8502]:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=10) as response:
            services[str(port)] = response.read().decode().strip()
        assert services[str(port)] == 'ok'
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'technical_delivery_review_ready',
        'freeze_sha256': measured['freeze_sha256'],
        'primary_slots': 400,
        'scored_blind_tuples': 296,
        'recovery_slots_separate': 9,
        'program_tests_passed': 109,
        'report_pages': 5,
        'combined_review_pages': 8,
        'viva_pages_and_bilingual_notes': 18,
        'visual_demo_seconds': 240,
        'service_health': services,
        'pending': ['Student English audio and final audio-video review',
                    'Actual Portfolio Review Documents and supervisor approvals',
                    'Assessor details, personal declaration and course activity evidence',
                    'Institution-accessible video link and actual submission',
                    'Account invoice reconciliation for unlogged historical spending'],
        'verification_scope': 'This Windows computer and existing Python environment; target-computer fonts and fresh dependency installation unverified',
    }
    (CLOSING / 'DELIVERY_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    listed = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z',
                                     'outputs/closing'], cwd=ROOT).decode('utf-8').split('\0')
    files = sorted({ROOT / name for name in listed if name and not name.endswith('DELIVERY_MANIFEST.json')})
    manifest = {'created_at': result['checked_at'],
                'hash_scope': 'Local delivery bytes; Git checkout line-ending conversion may change text-file bytes',
                'files': [
        {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'sha256': digest(path)}
        for path in files if path.is_file()]}
    (CLOSING / 'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
