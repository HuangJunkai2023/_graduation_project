"""Validate the rendered closing reports without changing their source packages."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import re
from shutil import copyfile
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn
from lxml import etree
from pypdf import PdfReader

from build_final_report import TEMPLATE


OUTPUT = Path(__file__).parent / 'generated'


def validate(output, render_tag):
    receipt = json.loads((output / 'build_receipt.json').read_text(encoding='utf-8'))
    assert sha256(TEMPLATE.read_bytes()).hexdigest() == receipt['template_sha256']
    qa_path = output / 'Final_Report_QA.json'
    prior = json.loads(qa_path.read_text(encoding='utf-8')) if qa_path.is_file() else {}
    checks = []
    report_pages = None
    for name in ['OCS_Final_Report_EN', 'OCS_Submission_Review_Draft']:
        path = output / f'{name}.docx'
        render = output / f'render-{name}-{render_tag}'
        delivered_pdf = output / f'{name}.pdf'
        rendered_pdf = render / delivered_pdf.name
        pdf_path = rendered_pdf if rendered_pdf.is_file() else delivered_pdf
        reader = PdfReader(pdf_path)
        pages = len(reader.pages)
        assert len(list(render.glob('page-*.png'))) == pages
        if report_pages is None:
            report_pages = pages
            assert 6 <= report_pages <= 7
            assert 'REFERENCES' in reader.pages[-1].extract_text().upper()
        else:
            assert pages == report_pages + 3
            assert 'Declaration of Academic Integrity' in reader.pages[1].extract_text()
            assert 'PORTFOLIO EVIDENCE STATUS' in reader.pages[-1].extract_text().upper()
        with ZipFile(TEMPLATE) as before, ZipFile(path) as after:
            added = set(after.namelist()) - set(before.namelist())
            assert set(before.namelist()) <= set(after.namelist())
            assert sorted(added) == receipt['added_package_parts'] and len(added) == 2
            assert all(part.startswith('word/media/') and part.endswith('.png') for part in added)
            changed = [part for part in before.namelist() if before.read(part) != after.read(part)]
            assert changed == receipt['modified_package_parts']
            assert set(changed) <= {'word/document.xml', 'word/_rels/document.xml.rels', '[Content_Types].xml'}
            rel = 'word/_rels/document.xml.rels'
            old = {node.get('Id'): dict(node.attrib) for node in etree.fromstring(before.read(rel))}
            revised = {node.get('Id'): dict(node.attrib) for node in etree.fromstring(after.read(rel))}
            assert all(revised[key] == value for key, value in old.items())
            assert {f"word/{row['Target']}" for key, row in revised.items() if key not in old} == added
            root = etree.fromstring(after.read('word/document.xml'))
        text = '\n'.join(root.itertext())
        pdf_text = '\n'.join(page.extract_text() for page in reader.pages)
        for token in ['Feynman', 'Bose-Einstein', 'Sadegh']:
            assert token not in text
        assert 'assistant_source_review' in pdf_text
        assert '400' in pdf_text and '3341' in pdf_text
        assert all(re.search(rf'\bLO{number}\b', pdf_text) for number in range(1, 17))
        assert '18.75' in pdf_text
        assert '68' in pdf_text
        assert 'no measured incremental benefit' in ' '.join(pdf_text.split())
        assert 'VersionRAG' in pdf_text and 'Fig. 1.' in pdf_text and 'Fig. 2.' in pdf_text
        assert '48 of 48' in ' '.join(pdf_text.split()) and '84 of 84' in ' '.join(pdf_text.split())
        assert 'REFERENCES' in pdf_text.upper()
        document = Document(path)
        sections = []
        for section in document.sections:
            assert section.page_width.twips == 12240
            assert section.page_height.twips == 15840
            assert section.top_margin.twips == 1008
            assert section.bottom_margin.twips == 1008
            assert section.left_margin.twips == 936
            assert section.right_margin.twips == 936
            cols = section._sectPr.find(qn('w:cols'))
            sections.append(cols.get(qn('w:num'), '1'))
        assert '2' in sections
        if pdf_path != delivered_pdf:
            copyfile(pdf_path, delivered_pdf)
        checks.append({'artifact': name, 'pages': pages,
                       'docx_sha256': sha256(path.read_bytes()).hexdigest(),
                       'pdf_sha256': sha256(pdf_path.read_bytes()).hexdigest(),
                       'modified_template_parts': changed, 'added_figure_parts': sorted(added),
                       'rendered_page_images': pages})
    result = {'status': 'review_ready', 'technical_report_page_limit': 7,
              'word_count_including_tables_and_references': receipt['word_count'],
              'rendering': 'LibreOffice 25.8.7.3, source geometry and styles retained',
              'artifacts': checks,
              'source_review_method': 'assistant_source_review',
              'research_limitations': ['No independent human scoring validation',
                                       'No admitted same-family formal edition pair',
                                       'Hybrid did not improve Recall@5 over BM25',
                                       'No observed incremental RQ2 or RQ3 benefit'],
              'institutional_items_pending': receipt['institutional_items_pending']}
    if prior.get('artifacts') == checks and 'visual_review' in prior:
        result['visual_review'] = prior['visual_review']
    qa_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUTPUT)
    parser.add_argument('--render-tag', default='v4b')
    args = parser.parse_args()
    validate(args.output_dir, args.render_tag)
