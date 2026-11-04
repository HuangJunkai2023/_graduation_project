"""Follow the supplied example's structure; Attachment 9 governs conflicting items."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent.parent
SOURCE = OUT / '开题报告内容.md'
STATS = OUT / '校验记录.json'


def target_path():
    source = SOURCE.read_text()
    student_id = re.search(r'^Student ID: (\d+)$', source, re.M)[1]
    name = re.search(r'^Student name: (.+)$', source, re.M)[1]
    return OUT / f'3.{student_id}_{name}_开题报告.docx'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(run, size=10.5, bold=False):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.font.bold = bold
    run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '宋体')


def paragraph_format(p, size=10.5, heading=False, body=False, compact=False):
    p.paragraph_format.space_before = Pt(4 if heading else 0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = Pt(14 if compact else 14.5 if body else size + 3)
    p.paragraph_format.first_line_indent = Pt(21 if body and not heading else 0)
    p.paragraph_format.keep_with_next = heading
    p.paragraph_format.keep_together = body
    p.paragraph_format.widow_control = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # The template's document grid otherwise overrides the English line spacing.
    props = p._p.get_or_add_pPr()
    snap = props.find(qn('w:snapToGrid'))
    if snap is None:
        snap = OxmlElement('w:snapToGrid')
        props.append(snap)
    snap.set(qn('w:val'), '0')


def clear_cell(cell):
    cell._tc.clear_content()
    cell.add_paragraph()


def add_text(cell, text, size=10.5, heading=False, first=False, body=False, compact=False):
    p = cell.paragraphs[0] if first else cell.add_paragraph()
    paragraph_format(p, size, heading, body, compact)
    font(p.add_run(text), size, heading)
    return p


def fill_field(cell, text, size=11):
    clear_cell(cell)
    p = add_text(cell, text, size, first=True)
    p.paragraph_format.space_after = Pt(0)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def no_split(row):
    props = row._tr.get_or_add_trPr()
    if props.find(qn('w:cantSplit')) is None:
        props.append(OxmlElement('w:cantSplit'))


def add_grid(cell, lines):
    values = [[v.strip() for v in line.strip().strip('|').split('|')]
              for line in lines if not re.match(r'^\|[\s:|\-]+\|$', line)]
    table = cell.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Cm(1.75)
    table.columns[1].width = Cm(11.2)
    props = table._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement('w:' + name)
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:color'), '777777')
        borders.append(border)
    props.append(borders)
    for i, values_row in enumerate(values):
        row = table.rows[0] if i == 0 else table.add_row()
        no_split(row)
        for j, value in enumerate(values_row):
            fill_field(row.cells[j], value, 9.5)
            row.cells[j].width = Cm(1.75 if j == 0 else 11.2)
            for p in row.cells[j].paragraphs:
                p.paragraph_format.line_spacing = Pt(11.5)
                if i == 0:
                    for run in p.runs:
                        run.bold = True
        if i == 0:
            repeat = OxmlElement('w:tblHeader')
            row._tr.get_or_add_trPr().append(repeat)
    # Word requires a paragraph following a nested table.
    p = cell.paragraphs[-1]
    paragraph_format(p)


def markdown(cell, text, references=False, compact=False):
    clear_cell(cell)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    lines = text.strip().splitlines()
    first = True
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line.startswith('|'):
            block = [line]
            while i < len(lines) and lines[i].strip().startswith('|'):
                block.append(lines[i].strip())
                i += 1
            add_grid(cell, block)
            first = False
            continue
        picture = re.fullmatch(r'!\[(.+)\]\((.+)\)', line)
        if picture:
            p = cell.paragraphs[0] if first else cell.add_paragraph()
            paragraph_format(p)
            # Exact text line heights would clip an inline illustration.
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(OUT / picture[2]), width=Cm(8.5))
            caption = add_text(cell, picture[1], 9.5)
            caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            caption.paragraph_format.line_spacing = Pt(12)
            first = False
            continue
        heading = line.startswith('### ') or line.startswith('#### ')
        major_heading = line.startswith('### ')
        text = re.sub(r'^#{3,4} ', '', line) if heading else line
        size = 12 if major_heading else 10.5
        p = add_text(cell, text, size, heading, first, body=True, compact=compact or references)
        if references:
            p.paragraph_format.first_line_indent = Pt(-15)
            p.paragraph_format.left_indent = Pt(15)
            p.paragraph_format.space_after = Pt(3)
        first = False


def paginate_field(row):
    """Split a long field into unsplittable paragraph groups with a merged label.

    LibreOffice ignores paragraph keep rules inside a row spanning many pages.
    Physical rows enforce those rules while preserving one logical form field.
    """
    paragraphs = [deepcopy(p._p) for p in row.cells[-1].paragraphs]
    groups = []
    i = 0
    while i < len(paragraphs):
        group = [paragraphs[i]]
        i += 1
        props = group[0].find(qn('w:pPr'))
        keep_next = props.find(qn('w:keepNext')) if props is not None else None
        if keep_next is not None and keep_next.get(qn('w:val'), '1') not in ['0', 'false'] and i < len(paragraphs):
            group.append(paragraphs[i])
            i += 1
            # A numbered main heading followed by a subheading needs its body too.
            props2 = group[-1].find(qn('w:pPr'))
            keep2 = props2.find(qn('w:keepNext')) if props2 is not None else None
            if keep2 is not None and keep2.get(qn('w:val'), '1') not in ['0', 'false'] and i < len(paragraphs):
                group.append(paragraphs[i])
                i += 1
        groups.append(group)
    original = row._tr
    parent = original.getparent()
    position = parent.index(original)
    for i, paragraphs in enumerate(groups):
        clone = deepcopy(original)
        cells = clone.findall(qn('w:tc'))
        merge = OxmlElement('w:vMerge')
        merge.set(qn('w:val'), 'restart' if i == 0 else 'continue')
        cells[0].find(qn('w:tcPr')).append(merge)
        if i:
            for child in list(cells[0]):
                if child.tag != qn('w:tcPr'):
                    cells[0].remove(child)
            cells[0].append(OxmlElement('w:p'))
        for child in list(cells[-1]):
            if child.tag != qn('w:tcPr'):
                cells[-1].remove(child)
        for p in paragraphs:
            cells[-1].append(p)
        # These are pagination rows, not extra form fields: hide their internal
        # horizontal edges, retaining the original outer/section/column borders.
        for cell in cells:
            cell_props = cell.find(qn('w:tcPr'))
            borders = OxmlElement('w:tcBorders')
            for name, internal in [('top', i > 0), ('bottom', i < len(groups) - 1)]:
                if internal:
                    edge = OxmlElement('w:' + name)
                    edge.set(qn('w:val'), 'nil')
                    borders.append(edge)
            cell_props.append(borders)
        props = clone.find(qn('w:trPr'))
        if props is None:
            props = OxmlElement('w:trPr')
            clone.insert(0, props)
        props.append(OxmlElement('w:cantSplit'))
        parent.insert(position, clone)
        position += 1
    parent.remove(original)


def build():
    target = target_path()
    template = next((ROOT / '交大资料').glob('附件九*.docx'))
    before = sha256(template)
    example = ROOT / '交大资料/开题报告模板.pdf'
    example_hash = sha256(example)
    source = SOURCE.read_text()
    fields = dict(re.findall(r'^([^\n:]+):([^\n]*)$', source.split('## ')[0], re.M))
    fields = {k.strip(): v.strip() for k, v in fields.items()}
    parts = re.split(r'^## ([^\n]+)\n', source, flags=re.M)
    sections = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
    doc = Document(template)
    assert len(doc.tables) == 1 and len(doc.tables[0].rows) == 13
    table = doc.tables[0]
    field_cells = {
        'Project title': (0, 2), 'Student name': (1, 2), 'Student ID': (1, 6),
        'Degree programme': (2, 2), 'Supervisor': (3, 3), 'Supervisor rank': (3, 7),
    }
    for name, (row, col) in field_cells.items():
        fill_field(table.cell(row, col), fields[name])
        for p in table.cell(row, col).paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Preserve every option, replacing legacy Wingdings boxes with real Unicode
    # empty boxes so font substitution cannot make an option appear selected.
    assert not fields['Project type'] and not fields['Topic source'] and not fields['Guidance journal']
    choices = {
        4: [['毕业论文(理论研究)', '毕业论文(应用研究)'],
            ['毕业设计(工程设计)', '毕业设计(软件设计)']],
        5: [['教师自拟', '生产实践'], ['科研课题', '学生自拟', '其他']],
        6: [['填写', '未填写']],
    }
    for index, lines in choices.items():
        cell = table.rows[index].cells[-1]
        clear_cell(cell)
        for i, values in enumerate(lines):
            p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
            paragraph_format(p)
            if index == 6:
                font(p.add_run('毕业设计指导日志    '))
            for j, value in enumerate(values):
                if j:
                    font(p.add_run('    '))
                box = p.add_run('☐ ')
                font(box)
                box.font.name = 'DejaVu Sans'
                font(p.add_run(value))
    for row in table.rows[:7]:
        seen = set()
        for cell in row.cells:
            if id(cell._tc) in seen:
                continue
            seen.add(id(cell._tc))
            for p in cell.paragraphs:
                paragraph_format(p)
                p.paragraph_format.space_after = Pt(1)
                for run in p.runs:
                    if run.font.name != 'DejaVu Sans':
                        font(run)
    for row in table.rows[:4]:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for index, heading in [(7, '选题意义和国内外研究现状分析'),
                           (8, '主要研究目标和研究内容'), (9, '工作计划及进度安排'),
                           (10, '参考文献')]:
        # Follow the example's prose schedule instead of a dense nested grid.
        markdown(table.rows[index].cells[-1], sections[heading], references=index == 10, compact=index == 9)
        table.rows[index].height = None
        table.rows[index].height_rule = WD_ROW_HEIGHT_RULE.AUTO
        # Preserve the narrow Chinese field labels and let long sections continue
        # across pages, as in the supplied example.
        label = table.rows[index].cells[0]
        # Keep the whole label at the start of a multi-page field; centring a
        # vertically merged label can strand its last character on another page.
        label.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        for p in label.paragraphs:
            paragraph_format(p)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                font(run, 10.5)
    # Keep all original Chinese form items and merged-cell geometry.
    for i, row in enumerate(table.rows):
        props = row._tr.get_or_add_trPr()
        for flag in list(props.findall(qn('w:cantSplit'))):
            props.remove(flag)
        if i not in [7, 8, 9]:
            no_split(row)
    for i in [11, 12]:
        row = table.rows[i]
        row.height = Cm(4.8)
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for p in row.cells[0].paragraphs:
            for run in p.runs:
                if run.text:
                    font(run, 10.5)
    # Keep the official filling instruction with the form, without an orphan page.
    for p in doc.paragraphs:
        if p.text.startswith('填写说明'):
            paragraph_format(p, 9)
            p.paragraph_format.space_before = Pt(3)
            for run in p.runs:
                font(run, 9)
    # Keep the original continuous form. Like the example, long fields continue
    # across pages without forced section breaks that leave almost-empty pages.
    original_opinions = [table.rows[i].cells[0].text for i in [11, 12]]
    # Seven references fit on one page with the opinion areas; keep this short
    # field intact so its narrow Chinese label cannot split across pages.
    long_fields = [table.rows[i] for i in [7, 8, 9]]
    for row in long_fields:
        paginate_field(row)
    for section in doc.sections:
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph_format(p, 9)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for value, field in [('第 ', None), ('', 'PAGE'), (' 页 / 共 ', None), ('', 'NUMPAGES'), (' 页', None)]:
            run = p.add_run(value)
            font(run, 9)
            if field:
                element = OxmlElement('w:fldSimple')
                element.set(qn('w:instr'), field)
                run._r.addnext(element)
    doc.core_properties.title = fields['Project title']
    doc.core_properties.author = '黄俊凯'
    doc.core_properties.subject = '西南交通大学-利兹学院本科毕业设计（论文）开题报告（附件九）'
    doc.core_properties.comments = 'Example-based numbered sections; Attachment 9 governs fields/language. Signatures blank.'
    OUT.mkdir(exist_ok=True)
    doc.save(target)
    assert sha256(template) == before
    # These blank official approval areas must not acquire generated comments.
    result = Document(target)
    assert len(result.tables) == 1
    for generated_row, original_text in zip(result.tables[0].rows[-2:], original_opinions):
        assert generated_row.cells[0].text == original_text
    body = '\n'.join(sections.values())
    assert not re.search(r'\b(?:I|[Ww]e|[Mm]y|[Oo]ur)\b', body)
    assert len(re.findall(r'^\[\d+\]', sections['参考文献'], re.M)) == 7
    cited = {int(n) for n in re.findall(r'\[(\d+)\]', body.split('[1] P. Lewis')[0])}
    assert cited == set(range(1, 8)), cited
    return {
        'prepared_on': fields['Prepared on'], 'template': str(template.relative_to(ROOT)),
        'template_sha256': before, 'template_unmodified': True,
        'restructured_on': '2026-11-04',
        'layout_example': str(example.relative_to(ROOT)), 'layout_example_sha256': example_hash,
        'conflict_priority': 'Attachment 9 over the supplied example',
        'example_unmodified': sha256(example) == example_hash,
        'numbered_sections': ['1. Background and Significance', '2. Review of Related Research',
                              '3. Research Aim and Objectives', '4. Research Content and Methods'],
        'planned_workflow_figure': 'figures/planned_workflow.png',
        'source_sha256': sha256(SOURCE), 'docx_sha256': sha256(target),
        'student_name': fields['Student name'], 'student_id': fields['Student ID'],
        'major': fields['Degree programme'], 'supervisor': fields['Supervisor'],
        'supervisor_rank': fields['Supervisor rank'],
        'title': fields['Project title'], 'body_language': 'English',
        'reference_count': 7, 'research_questions': 3, 'formal_configurations': 5,
        'planned_documents': '20–30', 'planned_questions': 100,
        'development_questions': 20, 'test_questions': 80,
        'formal_executions': 400, 'planned_total_hours': 400,
        'hours_through_week24': 372, 'viva_hours': 28, 'planned_api_budget_gbp': 50,
        'blank_registration_fields': [label for field, label in [
            ('Supervisor rank', '导师职称'), ('Project type', '选题类型'),
            ('Topic source', '题目来源'), ('Guidance journal', '毕业设计指导日志填写情况')
        ] if not fields[field]],
        'supervisor_opinion_blank': True, 'expert_opinion_blank': True,
        'signatures_blank': True, 'approval_dates_blank': True,
        'original_logical_fields_preserved': 13,
        'physical_table_rows': len(result.tables[0].rows), 'visual_review': False,
        'formal_approval_obtained': False, 'handwritten_archival_scan_created': False,
    }


def close_page_tables(docx_path, pdf_path):
    """Use the actual first-pass layout to give each page its own closed table.

    Paragraph-group rows are unsplittable, so each row can be assigned to a PDF
    page by its text. Splitting only at those boundaries preserves the layout
    while avoiding cell-level hidden borders suppressing the continuation frame.
    """
    import pymupdf

    normalise = lambda value: ''.join(c for c in unicodedata.normalize('NFKC', value) if c.isalnum())
    with pymupdf.open(pdf_path) as pdf:
        pages = [normalise(page.get_text(clip=pymupdf.Rect(0, 90, page.rect.width, 770))) for page in pdf]
    doc = Document(docx_path)
    table = doc.tables[0]
    rows = list(table._tbl.findall(qn('w:tr')))
    groups = [[] for _ in pages]
    cursor = 0
    for index, row in enumerate(rows):
        if index >= 7:
            content = row.findall(qn('w:tc'))[-1]
            text = normalise(''.join(t.text or '' for t in content.iter(qn('w:t'))))
            assert text, f'Empty pagination row {index}'
            matches = [i for i in range(cursor, len(pages)) if text in pages[i]]
            assert matches, f'Cannot locate row {index} in rendered PDF: {text[:60]}'
            cursor = matches[0]
        groups[cursor].append(row)
    assert all(groups), 'Unexpected page without report-table rows'

    original = table._tbl
    parent = original.getparent()
    position = parent.index(original)
    for number, page_rows in enumerate(groups):
        if number:
            p = OxmlElement('w:p')
            props = OxmlElement('w:pPr')
            for name in ['pageBreakBefore', 'keepNext']:
                props.append(OxmlElement('w:' + name))
            snap = OxmlElement('w:snapToGrid')
            snap.set(qn('w:val'), '0')
            props.append(snap)
            spacing = OxmlElement('w:spacing')
            for name, value in [('before', '0'), ('after', '0'), ('line', '1'), ('lineRule', 'exact')]:
                spacing.set(qn('w:' + name), value)
            props.append(spacing)
            p.append(props)
            parent.insert(position, p)
            position += 1
        clone = deepcopy(original)
        for row in list(clone.findall(qn('w:tr'))):
            clone.remove(row)
        for row in page_rows:
            clone.append(deepcopy(row))
        cloned_rows = clone.findall(qn('w:tr'))
        # Restart a field's vertical merge on the new page; continuation labels
        # stay blank, following the supplied example's continuation convention.
        for cell in cloned_rows[0].findall(qn('w:tc')):
            merge = cell.find(qn('w:tcPr')).find(qn('w:vMerge'))
            if merge is not None:
                merge.set(qn('w:val'), 'restart')
        for row, side in [(cloned_rows[0], 'top'), (cloned_rows[-1], 'bottom')]:
            for cell in row.findall(qn('w:tc')):
                props = cell.find(qn('w:tcPr'))
                borders = props.find(qn('w:tcBorders'))
                if borders is None:
                    borders = OxmlElement('w:tcBorders')
                    props.append(borders)
                for existing in list(borders.findall(qn('w:' + side))):
                    borders.remove(existing)
                border = OxmlElement('w:' + side)
                for key, value in [('val', 'single'), ('sz', '4'), ('color', 'auto')]:
                    border.set(qn('w:' + key), value)
                borders.append(border)
        parent.insert(position, clone)
        position += 1
    parent.remove(original)
    doc.save(docx_path)
    return [len(rows) for rows in groups]


def render(renderer, stats):
    import pymupdf
    target = target_path()
    program = Path(renderer).resolve()
    env = dict(os.environ, SAL_USE_VCLPLUGIN='svp', SAL_DISABLE_OPENCL='1', SAL_DISABLESKIA='1')
    # A locally extracted renderer is supported without a system installation.
    if program.name == 'soffice.bin' and (program.parent / 'fundamentalrc').exists():
        unpacked = program.parents[4]
        env['LD_LIBRARY_PATH'] = ':'.join([str(program.parent), str(unpacked / 'usr/lib/x86_64-linux-gnu'), env.get('LD_LIBRARY_PATH', '')])
        env['URE_BOOTSTRAP'] = 'vnd.sun.star.pathname:' + str(program.parent / 'fundamentalrc')
    def export():
        with tempfile.TemporaryDirectory(prefix='ocs_swjtu_') as directory:
            command = [str(program), f'-env:UserInstallation={Path(directory).as_uri()}/profile',
                       '--headless', '--convert-to', 'pdf', '--outdir', str(OUT), str(target)]
            process = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
            if process.returncode == 81:
                process = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
            if process.returncode:
                raise RuntimeError(process.stderr or process.stdout)
    export()
    pdf = target.with_suffix('.pdf')
    page_rows = close_page_tables(target, pdf)
    export()
    from check_table_frames import check_frames
    frames = check_frames(pdf)
    assert len(frames) == len(page_rows), 'Framing changed pagination; review page capacity'
    stats.update(docx_sha256=sha256(target), table_frames_checked=True,
                 page_table_count=len(page_rows), rows_per_page_table=page_rows,
                 table_frame_geometry=frames)
    with pymupdf.open(pdf) as doc:
        text = ' '.join(' '.join(p.get_text() for p in doc).split())
        for term in [stats['student_name'], stats['student_id'], stats['supervisor'], 'Electronic and Electrical Engineering',
                     'A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field',
                     'RQ1', 'RQ2', 'RQ3', 'O1:', 'O5:', 'B1 BM25', 'A2 Hybrid',
                     '指导教师意见', '专家组评审意见']:
            assert term in text, term
        assert '请用英文填写' not in text
        normalise = lambda value: ''.join(c for c in unicodedata.normalize('NFKC', value) if c.isalnum())
        # Ignore running headers/footers when checking paragraphs that span pages.
        pdf_text = normalise(' '.join(page.get_text(clip=pymupdf.Rect(0, 90, page.rect.width, 770)) for page in doc))
        source_blocks = []
        body = SOURCE.read_text().split('## 选题意义和国内外研究现状分析\n', 1)[1]
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith('## '):
                continue
            line = re.sub(r'^#{3,4} ', '', line)
            picture = re.fullmatch(r'!\[(.+)\]\((.+)\)', line)
            if picture:
                line = picture[1]
            assert normalise(line) in pdf_text, f'Missing source block: {line[:90]}'
            source_blocks.append(line)
        for i, page in enumerate(doc):
            assert len(page.get_text().strip()) > 100, f'Blank/orphan page {i + 1}'
            for x0, y0, x1, y1, *_ in page.get_text('blocks'):
                assert x0 >= -1 and y0 >= -1 and x1 <= page.rect.width + 1 and y1 <= page.rect.height + 1, f'Page {i + 1} bounds'
            for picture in page.get_image_info():
                assert page.rect.contains(pymupdf.Rect(picture['bbox'])), f'Page {i + 1} image bounds'
        assert text.count('☐') == 11
        assert not any(term in text for term in ['刘曦扬', '2022111802', '秦娜', '师玉娇', '上海科技大学', '3DGS', 'SLAM'])
        stats.update(pdf_sha256=sha256(pdf), pdf_pages=len(doc), pdf_page_bounds_checked=True,
                     pdf_image_bounds_checked=True, source_paragraphs_verified_in_pdf=len(source_blocks),
                     unicode_empty_checkboxes=11, blank_pages=False, example_personal_details_not_copied=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', required=True,
                        help='LibreOffice path; actual PDF pagination is required to close Word/PDF table frames')
    args = parser.parse_args()
    result = build()
    render(args.renderer, result)
    STATS.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
