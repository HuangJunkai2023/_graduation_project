"""Create editable ELEC3801 report copies from the retained university template."""
from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

import report_content as prose

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / '@26-27新版资料/3.Final report template_ELEC3801_Final_Report_Template.docx'
NAMESPACE = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def percentage(value):
    return 'N/A' if value is None else f'{100 * value:.1f}%'


def decimal(value):
    return 'N/A' if value is None else f'{value:.3f}'


def metric(data, label, key):
    return data['configurations'][label][key]['value']


def paired(data, comparison, key):
    row = data['analysis']['paired_comparisons'][comparison][key]
    if row['ci_95'] is None:
        return 'N/A', 'N/A'
    return f"{100 * row['absolute_difference']:+.1f}", f"[{100 * row['ci_95'][0]:+.1f}, {100 * row['ci_95'][1]:+.1f}]"


def paragraph(source, text):
    element = deepcopy(source._p)
    properties = element.find(qn('w:pPr'))
    for child in list(element):
        if child is not properties:
            element.remove(child)
    run = OxmlElement('w:r')
    first_properties = source._p.find('.//' + qn('w:rPr'))
    if first_properties is not None:
        run.append(deepcopy(first_properties))
    for index, line in enumerate(text.split('\n')):
        if index:
            run.append(OxmlElement('w:br'))
        content = OxmlElement('w:t')
        content.set(qn('xml:space'), 'preserve')
        content.text = line
        run.append(content)
    element.append(run)
    return element


def keep_table_together(element):
    rows = element.findall(qn('w:tr'))
    for index, row in enumerate(rows):
        properties = row.find(qn('w:trPr'))
        if properties is None:
            properties = OxmlElement('w:trPr')
            row.insert(0, properties)
        properties.append(OxmlElement('w:cantSplit'))
        if index == 0 and properties.find(qn('w:tblHeader')) is None:
            properties.append(OxmlElement('w:tblHeader'))
        for p in row.findall('.//' + qn('w:p')):
            ppr = p.find(qn('w:pPr'))
            if ppr is None:
                ppr = OxmlElement('w:pPr')
                p.insert(0, ppr)
            if index < len(rows) - 1 and ppr.find(qn('w:keepNext')) is None:
                ppr.append(OxmlElement('w:keepNext'))


def table(rows, widths, normal):
    element = OxmlElement('w:tbl')
    properties = OxmlElement('w:tblPr')
    width = OxmlElement('w:tblW')
    width.set(qn('w:w'), str(sum(widths)))
    width.set(qn('w:type'), 'dxa')
    properties.append(width)
    borders = OxmlElement('w:tblBorders')
    for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement('w:' + edge)
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:color'), '000000')
        borders.append(border)
    properties.append(borders)
    element.append(properties)
    grid = OxmlElement('w:tblGrid')
    for size in widths:
        column = OxmlElement('w:gridCol')
        column.set(qn('w:w'), str(size))
        grid.append(column)
    element.append(grid)
    for index, values in enumerate(rows):
        row = OxmlElement('w:tr')
        if index == 0:
            row_properties = OxmlElement('w:trPr')
            row_properties.append(OxmlElement('w:tblHeader'))
            row.append(row_properties)
        for text, size in zip(values, widths):
            cell = OxmlElement('w:tc')
            cell_properties = OxmlElement('w:tcPr')
            cell_width = OxmlElement('w:tcW')
            cell_width.set(qn('w:w'), str(size))
            cell_width.set(qn('w:type'), 'dxa')
            cell_properties.append(cell_width)
            cell.append(cell_properties)
            p = paragraph(normal, str(text))
            p_properties = p.find(qn('w:pPr'))
            if p_properties is None:
                p_properties = OxmlElement('w:pPr')
                p.insert(0, p_properties)
            for old in list(p_properties):
                if old.tag in [qn('w:spacing'), qn('w:ind')]:
                    p_properties.remove(old)
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:before'), '0')
            spacing.set(qn('w:after'), '0')
            p_properties.append(spacing)
            indents = OxmlElement('w:ind')
            indents.set(qn('w:firstLine'), '0')
            p_properties.append(indents)
            cell.append(p)
            row.append(cell)
        element.append(row)
    keep_table_together(element)
    return element


def report_blocks(data, selected, cases):
    groups = data['configurations']
    full = groups['B3']
    blocks = []
    abstract = (
        'Abstract — This project develops a traceable retrieval-augmented question-answering system for Chinese overhead contact system standards. '
        'The local collection contains 25 documents and 3341 text chunks. A 100-question benchmark uses 20 development and 80 test questions. '
        'BM25, Dense and Hybrid retrieval are compared with edition-filter and Evidence Gate ablations across 400 primary test slots. '
        f"Hybrid obtains Recall@5 of {percentage(metric(data, 'B3', 'recall_at_5'))}, answer correctness of {percentage(metric(data, 'B3', 'answer_correctness'))} "
        f"and citation support of {percentage(metric(data, 'B3', 'citation_support'))}. Its false-refusal rate is {percentage(metric(data, 'B3', 'false_refusal'))}. "
        'All figures retain the predeclared denominators and first-attempt failures. The assistant reviewed references, passages and outputs against sources, '
        'revising the planned human-annotation procedure. Formal edition pairs were unavailable, so the edition study concerns available and missing requested editions. '
        'The measurements support a bounded assessment of evidence recall, source traceability and refusal trade-offs within this corpus.')
    blocks += [('abstract', abstract), ('p', 'Index Terms — Evidence assessment, hybrid retrieval, overhead contact systems, question answering, retrieval-augmented generation, standards.')]
    blocks.append(('h1', 'I. Introduction'))
    blocks.extend(('p', text) for text in prose.INTRODUCTION)
    blocks.append(('h1', 'II. System Design and Implementation'))
    blocks.extend(prose.METHOD)
    blocks.append(('h1', 'III. Experimental Design'))
    blocks.extend(prose.EVALUATION)
    parameters = selected['selected']
    blocks.append(('p', f"The selected parameters are w = {parameters['vector_weight']:.2f}, lexical coverage = {parameters['min_coverage']:.2f}, "
                   f"and raw cosine threshold = {parameters['min_cosine']:.2f}. The frozen model configuration, numeric vectors and source hashes accompany the results. "
                   'The report uses the frozen first-attempt dataset and records any recovery runs separately.'))
    blocks.append(('h1', 'IV. Performance Evaluation'))
    blocks.append(('h2', 'A. Retrieval and answer quality'))
    blocks.append(('p', f"Table I compares evidence recall and displayed answer quality. BM25 reaches Recall@5 {percentage(metric(data, 'B1', 'recall_at_5'))}, "
                   f"Dense {percentage(metric(data, 'B2', 'recall_at_5'))}, and Hybrid {percentage(metric(data, 'B3', 'recall_at_5'))}. "
                   f"Their MRR@5 values are {decimal(metric(data, 'B1', 'mrr_at_5'))}, {decimal(metric(data, 'B2', 'mrr_at_5'))}, "
                   f"and {decimal(metric(data, 'B3', 'mrr_at_5'))}, respectively. Correctness uses all 64 answerable questions, so refusal and interface failures remain visible. "
                   'Citation support pools displayed cited claims, while answer coverage uses all 80 questions.'))
    blocks.append(('caption', 'TABLE I\nRetrieval and answer quality'))
    table_one = [['Config.', 'Recall@5', 'Correct', 'Support', 'Coverage']]
    for label in ['B1', 'B2', 'B3', 'A1', 'A2']:
        table_one.append([label] + [decimal(metric(data, label, key)) for key in
                          ['recall_at_5', 'answer_correctness', 'citation_support', 'answer_coverage']])
    blocks.append(('table', table_one))
    blocks.append(('h2', 'B. Edition and evidence ablations'))
    blocks.append(('p', f"With edition checks disabled, A1 has wrong-edition rate {percentage(metric(data, 'A1', 'wrong_edition_rate'))}, "
                   f"compared with {percentage(metric(data, 'B3', 'wrong_edition_rate'))} for B3. The denominator includes requests for missing editions. "
                   'Available and missing strata are retained in the supplementary output. Because there are no admitted formal edition pairs, '
                   'this comparison addresses refusal of unavailable requests and preservation of requested-year constraints. It leaves selection between two valid formal editions untested.'))
    blocks.append(('caption', 'TABLE II\nRefusal and unsupported-answer rates'))
    table_two = [['Config.', 'Wrong ed.', 'Refusal', 'False ref.', 'Unsupp.']]
    for label in ['B1', 'B2', 'B3', 'A1', 'A2']:
        table_two.append([label] + [decimal(metric(data, label, key)) for key in
                          ['wrong_edition_rate', 'refusal_recall', 'false_refusal', 'unsupported_answer_incidence']])
    blocks.append(('table', table_two))
    blocks.append(('p', f"B3 produces unsupported-answer incidence {percentage(metric(data, 'B3', 'unsupported_answer_incidence'))}, "
                   f"while A2 produces {percentage(metric(data, 'A2', 'unsupported_answer_incidence'))}. "
                   f"B3 refusal recall is {percentage(metric(data, 'B3', 'refusal_recall'))} and false refusal is {percentage(metric(data, 'B3', 'false_refusal'))}. "
                   f"Its unsupported rate conditional on a substantive answer is {percentage(metric(data, 'B3', 'unsupported_among_answers'))}. "
                   'These measures expose the trade-off between accepting more passages and withholding answers. A low unsupported count accompanied by reduced answer coverage requires cautious interpretation.'))
    targets = [('recall_at_5', 'Recall@5', 0.80, True), ('answer_correctness', 'correctness', 0.80, True),
               ('citation_support', 'citation support', 0.90, True), ('refusal_recall', 'refusal recall', 0.80, True),
               ('false_refusal', 'false refusal', 0.10, False)]
    assessments = []
    for key, title, target, higher in targets:
        observed = metric(data, 'B3', key)
        achieved = observed is not None and (observed >= target if higher else observed <= target)
        assessments.append(f"The {title} target of {'at least' if higher else 'at most'} {percentage(target)} "
                           f"was {'met' if achieved else 'unmet'}, with observed {percentage(observed)}.")
    blocks.append(('p', ' '.join(assessments)))
    blocks.append(('h2', 'C. Paired uncertainty and operational behaviour'))
    blocks.append(('caption', 'TABLE III\nPaired differences in percentage points'))
    comparison_table = [['Comparison and metric', 'Difference', '95% interval']]
    for comparison, key, title in [
        ('B3_minus_B1', 'recall_at_5', 'B3 − B1 Recall@5'),
        ('B3_minus_B2', 'recall_at_5', 'B3 − B2 Recall@5'),
        ('B3_minus_A1', 'wrong_edition_rate', 'B3 − A1 wrong edition'),
        ('B3_minus_A2', 'unsupported_answer_incidence', 'B3 − A2 unsupported'),
    ]:
        difference, interval = paired(data, comparison, key)
        comparison_table.append([title, difference, interval])
    blocks.append(('table_wide', comparison_table))
    timing = full['total_latency']
    blocks.append(('p', f"The grouped analysis contains {data['analysis']['groups']} resampling groups. Table III reports absolute differences and uncertainty, "
                   'preserving the same sampled questions for both configurations. The category tables in the supplementary record show the corresponding sample counts. '
                   f"For B3, median end-to-end time is {timing['median_ms']:.0f} ms and P95 is {timing['p95_ms']:.0f} ms. "
                   f"The five configurations record {sum(row['api_errors'] for row in groups.values())} API errors and "
                   f"{sum(row['interrupted_unknown_outcomes'] for row in groups.values())} unknown interrupted outcomes. "
                   'Timings describe these sequential runs on the local machine and include early refusals when timings are known.'))
    for case in cases[:2]:
        locations = [re.sub(r'PDF第(\d+)页', r'PDF p. \1', text) for text in case.get('source_locations', [])]
        blocks.append(('p', f"A source-review example is {case['question_id']}. {case.get('analysis', case.get('grade_reason', ''))} "
                       f"The reference locations include {', '.join(locations[:2])}."))
    blocks.append(('h2', 'D. Interpretation and limitations'))
    blocks.append(('p', 'RQ1 is assessed from pre-gate Recall@5 and its paired B3–B1 and B3–B2 differences. RQ2 is assessed from the B3–A1 edition behaviour under the documented corpus limitation. '
                   'RQ3 is assessed jointly from unsupported answers, false refusals and coverage in B3–A2. These comparisons isolate the declared components while keeping generation and citation checks fixed. '
                   'Their scope remains bounded by the available sources, small grouped benchmark, heuristic evidence signals and assistant-based scoring. '
                   'String-valid citations can omit a necessary condition, and a high similarity score can accompany an irrelevant requirement. Operational railway decisions require qualified review of applicable standards.'))
    blocks.append(('h1', 'V. Conclusion'))
    blocks.append(('p', 'RQ1 shows a bounded retrieval benefit over Dense. Hybrid recall exceeds Dense by 18.75 percentage points, '
                   'with a grouped 95% interval of 6.90 to 32.00 points. BM25 records the highest recall and correctness in this benchmark. '
                   'The Hybrid-minus-BM25 recall difference is −1.56 points, with interval −4.35 to 0.00 points. '
                   'RQ2 yields zero observed wrong-edition answers in all five configurations over 68 specified-edition items. '
                   'RQ3 yields the same unsupported-answer incidence of 1/80, refusal recall of 14/16 and false-refusal rate of 0/64 for B3 and A2. '
                   'These observations provide no measured incremental benefit for the edition check or gate under this frozen benchmark. '
                   'Source-review limitations and the absent formal edition pairs constrain the interpretation.'))
    blocks.extend(prose.REFLECTION)
    blocks.append(('caption', 'TABLE IV\nLearning outcome evidence map'))
    blocks.append(('lo_table', prose.LO_EVIDENCE))
    blocks.append(('h1', 'Acknowledgment'))
    blocks.append(('p', 'The project acknowledges Prof. Deqing Huang as supervisor and attributes the external model services, research literature and supplied reference implementation. '
                   'The assistant supported implementation, source review, experiment processing and drafting under the student\'s instructions. '
                   'The student must critically review the submitted account and complete the required personal declaration and academic assessment activities.'))
    blocks.append(('h1', 'References'))
    blocks.extend(('reference', f'[{index}] {text}') for index, text in enumerate(prose.REFERENCES, 1))
    return blocks


def write_package(path, document_xml):
    with ZipFile(TEMPLATE) as source, ZipFile(path, 'w') as destination:
        for item in source.infolist():
            payload = document_xml if item.filename == 'word/document.xml' else source.read(item.filename)
            destination.writestr(item, payload)


def replace_cell(cell, text):
    source = cell.paragraphs[0]
    replacement = paragraph(source, text)
    for child in list(cell._tc):
        if child.tag != qn('w:tcPr'):
            cell._tc.remove(child)
    cell._tc.append(replacement)


def submission_copy(doc, report_elements, output):
    replace_cell(doc.tables[1].cell(0, 0), prose.TITLE)
    replace_cell(doc.tables[2].cell(0, 0), 'Student Name  Junkai Huang')
    replace_cell(doc.tables[2].cell(0, 1), 'SID  201804121')
    replace_cell(doc.tables[2].cell(1, 0), 'Supervisor  Prof. Deqing Huang')
    replace_cell(doc.tables[2].cell(1, 1), 'Assessor')
    replace_cell(doc.tables[3].cell(0, 0), 'OneDrive video link pending personal recording and upload')
    for row in doc.tables[3].rows[2:]:
        replace_cell(row.cells[1], 'Pending actual approval record')
    replace_cell(doc.tables[4].cell(2, 0), 'Student name  Junkai Huang')
    root = etree.fromstring(ZipFile(TEMPLATE).read('word/document.xml'))
    body = root.find(qn('w:body'))
    for child in list(body):
        body.remove(child)
    title_element = doc.paragraphs[11]._p
    for child in doc._element.body:
        if child is title_element:
            break
        body.append(deepcopy(child))
    for element in report_elements:
        body.append(deepcopy(element))
    boundary = paragraph(doc.paragraphs[95], '')
    body.append(boundary)
    body.append(paragraph(doc.paragraphs[22], 'Portfolio Evidence Status'))
    for text in [
        'Review draft prepared from the available project records on 12 November 2026. The technical report precedes this section. The cover, personal declaration, video link and Portfolio approvals require the corresponding actual completion records before institutional submission.',
        'Available reflective material comprises local Draft Progress Journal entries for Weeks 8, 9 and 10. The supervision log records the student-confirmed English Proposal review and signing on 26 October 2026 and the Chinese-side report feedback and signing confirmation recorded on 4 November 2026.',
        'The local register contains no confirmed approved Review Documents 1–10. Original meeting notes, actual Teams sharing records and supervisor approval means and dates are required to assemble that component. No numbered meeting or approval is inferred from a proposal signature.',
        'The final video requires the student\'s own English recording and a verified University of Leeds access link. Symposium participation, final submission and Viva remain associated with the actual course activities and their records.',
    ]:
        body.append(paragraph(doc.paragraphs[27], text))
    portfolio_section = deepcopy(doc.sections[5]._sectPr)
    section_type = portfolio_section.find(qn('w:type'))
    if section_type is None:
        section_type = OxmlElement('w:type')
        portfolio_section.insert(0, section_type)
    section_type.set(qn('w:val'), 'nextPage')
    body.append(portfolio_section)
    write_package(output / 'OCS_Submission_Review_Draft.docx', etree.tostring(
        root, xml_declaration=True, encoding='UTF-8', standalone=True))


def build(args):
    data = json.loads(Path(args.summary).read_text(encoding='utf-8'))
    selected = json.loads(Path(args.calibration).read_text(encoding='utf-8'))
    protocol = Path(args.protocol).read_text(encoding='utf-8')
    cases_data = json.loads(Path(args.cases).read_text(encoding='utf-8')) if args.cases else []
    cases = cases_data.get('cases', []) if isinstance(cases_data, dict) else cases_data
    if data.get('status') not in {'source_reviewed', 'human_scored'}:
        raise ValueError('Complete scored observations are required for the final report.')
    if set(data.get('configurations', {})) != {'B1', 'B2', 'B3', 'A1', 'A2'}:
        raise ValueError('The report requires all five predeclared configurations.')
    if selected.get('status') != 'validated' or not protocol.strip():
        raise ValueError('Validated calibration and protocol record are required.')
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    doc = Document(TEMPLATE)
    sources = {'p': doc.paragraphs[27], 'h1': doc.paragraphs[22], 'h2': doc.paragraphs[35],
               'abstract': doc.paragraphs[15], 'caption': doc.paragraphs[85], 'reference': doc.paragraphs[93]}
    blocks = report_blocks(data, selected, cases)
    report_elements = [paragraph(doc.paragraphs[11], prose.TITLE),
                       paragraph(doc.paragraphs[13], 'Junkai Huang, SID 201804121, Prof. Deqing Huang (Supervisor)')]
    title_end = deepcopy(doc.paragraphs[14]._p)
    for reference in doc.sections[0]._sectPr.findall(qn('w:headerReference')):
        title_end.find('.//' + qn('w:sectPr')).insert(0, deepcopy(reference))
    report_elements.append(title_end)
    markdown = ['# ' + prose.TITLE, '', 'Junkai Huang · SID 201804121 · Supervisor Prof. Deqing Huang', '']
    for kind, value in blocks:
        if kind in {'table', 'table_wide'}:
            widths = [800, 1060, 1060, 1060, 1060] if kind == 'table' else [1900, 1200, 1940]
            report_elements.append(table(value, widths, sources['p']))
            markdown.extend(['| ' + ' | '.join(row) + ' |' for row in value] + [''])
        elif kind == 'lo_table':
            original = deepcopy(doc.tables[6]._tbl)
            for row, values in zip(original.findall(qn('w:tr'))[1:], value):
                for cell, text in zip(row.findall(qn('w:tc')), values):
                    p = cell.find(qn('w:p'))
                    for child in list(cell):
                        if child is not cell.find(qn('w:tcPr')):
                            cell.remove(child)
                    # Source table-cell properties and source text properties are retained.
                    replacement = deepcopy(p)
                    for child in list(replacement):
                        if child.tag != qn('w:pPr'):
                            replacement.remove(child)
                    run = OxmlElement('w:r')
                    rpr = p.find('.//' + qn('w:rPr'))
                    if rpr is not None:
                        run.append(deepcopy(rpr))
                    t = OxmlElement('w:t')
                    t.text = text
                    run.append(t)
                    replacement.append(run)
                    cell.append(replacement)
            keep_table_together(original)
            report_elements.append(original)
            markdown.extend(['| ' + ' | '.join(row) + ' |' for row in value] + [''])
        else:
            element = paragraph(sources[kind], value)
            if kind == 'reference':
                for numbering in element.findall('./w:pPr/w:numPr', NAMESPACE):
                    numbering.getparent().remove(numbering)
            if kind == 'caption':
                properties = element.find(qn('w:pPr'))
                if properties is None:
                    properties = OxmlElement('w:pPr')
                    element.insert(0, properties)
                properties.append(OxmlElement('w:keepNext'))
            report_elements.append(element)
            markdown.extend([('## ' if kind == 'h1' else '### ' if kind == 'h2' else '') + value, ''])
    root = etree.fromstring(ZipFile(TEMPLATE).read('word/document.xml'))
    body = root.find(qn('w:body'))
    for child in list(body):
        body.remove(child)
    for element in report_elements:
        body.append(deepcopy(element))
    body.append(deepcopy(doc.sections[3]._sectPr))
    path = output / 'OCS_Final_Report_EN.docx'
    write_package(path, etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True))
    submission_copy(doc, report_elements, output)
    (output / 'OCS_Final_Report_EN.md').write_text('\n'.join(markdown), encoding='utf-8')
    with ZipFile(TEMPLATE) as before, ZipFile(path) as after:
        changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
    text = '\n'.join(markdown)
    receipt = {'template_sha256': sha256(TEMPLATE.read_bytes()).hexdigest(),
               'report_sha256': sha256(path.read_bytes()).hexdigest(),
               'word_count': len(re.findall(r'\b[\w−-]+\b', text)),
               'modified_package_parts': changed, 'source_review_status': data['status'],
               'result_freeze_sha256': data.get('freeze_sha256'), 'render_required': True,
               'institutional_items_pending': ['assessor details', 'personal declaration', 'Review Document approvals',
                                               'student audio', 'OneDrive access link', 'actual submission'],
               'font_and_geometry': 'Source template retained without font-size or margin changes.'}
    (output / 'build_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--summary', required=True)
    parser.add_argument('--calibration', required=True)
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--cases')
    parser.add_argument('--output-dir', default=str(Path(__file__).parent / 'generated'))
    build(parser.parse_args())
