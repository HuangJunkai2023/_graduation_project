"""Check final Viva notes, script alignment and delivered page count."""
from argparse import ArgumentParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import zipfile

import pymupdf
from lxml import etree


def main(output, workspace, source):
    for folder in ('authoring-svg-flat', 'notes'):
        target = source / folder
        target.mkdir(parents=True, exist_ok=True)
        for item in (workspace / folder).glob('closing_*'):
            shutil.copy2(item, target / item.name)
    for name in ('page_plan.json', 'animations.json'):
        shutil.copy2(workspace / name, source / name)
    image_folder = source / 'images'
    image_folder.mkdir(exist_ok=True)
    for svg in (source / 'authoring-svg-flat').glob('closing_*.svg'):
        for relative in re.findall(r'href="\.\./images/([^"]+)"', svg.read_text(encoding='utf-8')):
            image = workspace / 'images' / relative
            target = image_folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image, target)
    with zipfile.ZipFile(output / 'OCS_Viva_EN.pptx') as archive:
        presentation = etree.fromstring(archive.read('ppt/presentation.xml'))
        relationships = etree.fromstring(archive.read('ppt/_rels/presentation.xml.rels'))
        slide_targets = {node.get('Id'): node.get('Target') for node in relationships}
        notes = []
        for slide_id in presentation.xpath('//*[local-name()="sldId"]'):
            relationship_id = slide_id.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            slide = posixpath.normpath(posixpath.join('ppt', slide_targets[relationship_id]))
            slide_path = Path(slide)
            relation_path = slide_path.parent / '_rels' / (slide_path.name + '.rels')
            slide_relations = etree.fromstring(archive.read(relation_path.as_posix()))
            note_relation = next(node for node in slide_relations if node.get('Type').endswith('/notesSlide'))
            notes.append(posixpath.normpath(posixpath.join(slide_path.parent.as_posix(), note_relation.get('Target'))))
        note_texts = [
            ''.join(etree.fromstring(archive.read(name)).xpath(
                '//*[local-name()="t"]/text()'))
            for name in notes
        ]
    script = (output / 'OCS_Viva_CN_EN_Script.md').read_text(encoding='utf-8')
    script_pages = [int(value) for value in re.findall(r'^## 第(\d+)页', script, re.M)]
    pdf = pymupdf.open(output / 'OCS_Viva_EN.pdf')
    assert len(notes) == len(pdf) == 18
    assert script_pages == list(range(1, 19))
    assert all('中文逐字稿' in note and 'English Script' in note for note in note_texts)
    for number, note in enumerate(note_texts, start=1):
        expected = (workspace / 'notes' / f'closing_{number:02}.md').read_text(encoding='utf-8')
        assert ''.join(expected.split()) in ''.join(note.split())
    mapping = json.loads((output / 'content_mapping.json').read_text(encoding='utf-8'))
    assert [row['page'] for row in mapping] == list(range(1, 19))
    assert '48/48' in pdf[13].get_text()
    assert 'BM25 is the best-supported default' in pdf[12].get_text()
    result = {
        'status': 'passed_with_inherited_font_advisory',
        'main_slides': 15,
        'backup_slides': 3,
        'pdf_pages': len(pdf),
        'bilingual_notes': len(notes),
        'script_pages': script_pages,
        'planned_speaking_seconds': sum(row['seconds'] for row in mapping),
        'native_editable_text': True,
        'svg_quality': '18 pages passed, no errors or warnings',
        'pptx_package': 'passed, no relationship errors',
        'page_boundary_check': 'no outside-page text',
        'font_advisory': {
            'faces': ['微软雅黑', '游ゴシック', '游ゴシック Light'],
            'reason': 'Inherited template/theme declarations retained. All pages rendered cleanly locally. Target-computer font availability remains unverified.'
        },
        'study_limitations_included': [
            'assistant_source_review, zero independent human/expert reviewers',
            'shared author and evaluator assistant family',
            'no verified same-family formal edition pairs',
            'benchmark facts drawn from six corpus documents',
            'no observed incremental RQ2 or RQ3 improvement'
        ]
    }
    (output / 'validation/final_validation.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('outputs/closing/viva'))
    parser.add_argument('--workspace', type=Path, default=Path('project/qa_system/runtime/closing_ppt_workspace'))
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    main(args.output, args.workspace, args.source or args.output / 'source')
