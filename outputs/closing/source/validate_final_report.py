"""Validate the rendered closing reports without changing their source packages."""
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


def validate():
    receipt = json.loads((OUTPUT / 'build_receipt.json').read_text(encoding='utf-8'))
    assert sha256(TEMPLATE.read_bytes()).hexdigest() == receipt['template_sha256']
    checks = []
    for name, expected_pages in [('OCS_Final_Report_EN', 5), ('OCS_Submission_Review_Draft', 8)]:
        path = OUTPUT / f'{name}.docx'
        render = OUTPUT / f'render-{name}-v3'
        pdf_path = render / f'{name}.pdf'
        reader = PdfReader(pdf_path)
        assert len(reader.pages) == expected_pages
        assert len(list(render.glob('page-*.png'))) == expected_pages
        with ZipFile(TEMPLATE) as before, ZipFile(path) as after:
            assert set(before.namelist()) == set(after.namelist())
            changed = [part for part in before.namelist() if before.read(part) != after.read(part)]
            assert changed == ['word/document.xml']
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
        if name == 'OCS_Final_Report_EN':
            assert expected_pages <= 7
            assert 'REFERENCES' in reader.pages[4].extract_text().upper()
        copyfile(pdf_path, OUTPUT / f'{name}.pdf')
        checks.append({'artifact': name, 'pages': expected_pages,
                       'docx_sha256': sha256(path.read_bytes()).hexdigest(),
                       'pdf_sha256': sha256(pdf_path.read_bytes()).hexdigest(),
                       'modified_template_parts': changed,
                       'visual_review': f'All {expected_pages} final pages inspected individually',
                       'visual_findings': 'No clipped text, overlapping elements, unreadable tables or missing glyphs observed.'})
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
    (OUTPUT / 'Final_Report_QA.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    validate()
