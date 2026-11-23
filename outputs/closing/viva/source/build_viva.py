"""Populate the retained SWJTU slide design with the completed OCS study."""
from argparse import ArgumentParser
from copy import deepcopy
import json
from pathlib import Path
import shutil
import textwrap
import re
from lxml import etree as E

SVG = 'http://www.w3.org/2000/svg'
NS = {'s': SVG}
BLUE = '#194B8C'
DARK = '#23364B'
TEAL = '#178783'
GRAY = '#64748B'


def element(tag, **attributes):
    return E.Element(f'{{{SVG}}}{tag}', {k.replace('_', '-'): str(v) for k, v in attributes.items()})


def text(x, y, value, size=26, color=DARK, bold=False):
    group = element('g')
    group.set('data-pptx-bounds', f'{x} {y-size} {max(30, 1235-x)} {size*1.5}')
    node = element('text', x=x, y=y, font_family='Arial', font_size=size,
                   fill=color, font_weight='bold' if bold else 'normal')
    node.text = str(value)
    group.append(node)
    return group


def lines(root, x, y, value, width=60, size=26, color=DARK, bold=False, leading=None):
    y_step = leading or size * 1.4
    for line in str(value).split('\n'):
        wrapped = textwrap.wrap(line, width=width) or ['']
        for item in wrapped:
            root.append(text(x, y, item, size, color, bold))
            y += y_step
    return y


def rectangle(root, x, y, width, height, fill='#F0F5FA', stroke='none'):
    root.append(element('rect', x=x, y=y, width=width, height=height, fill=fill, stroke=stroke))


def replace_text(group, values, size=None):
    old = group.xpath('.//s:text', namespaces=NS)
    if not old:
        return
    original = old[0]
    attributes = dict(original.attrib)
    for key in list(attributes):
        if key.startswith('data-'):
            attributes.pop(key)
    font_size = float(size or attributes.get('font-size', 28))
    attributes['font-size'] = str(font_size)
    first_y = float(attributes['y'])
    for node in old:
        node.getparent().remove(node)
    node = element('text')
    node.attrib.update(attributes)
    node.set('y', str(first_y))
    node.text = values[0]
    for value in values[1:]:
        span = element('tspan', x=attributes['x'], dy=font_size*1.2)
        span.text = value
        node.append(span)
    group.append(node)


def groups_with_text(root):
    return [g for g in root if g.xpath('.//s:text', namespaces=NS)]


def copy_page(workspace, source, title=None, footer='', blank=False):
    root = E.parse(str(workspace / f'authoring-svg-flat/slide_{source:02}.svg')).getroot()
    root = deepcopy(root)
    if blank:
        for child in list(root):
            if child.tag.endswith(('defs', 'rect')):
                continue
            identity = child.get('data-pptx-source-ref', '')
            if identity.startswith(('layout:', 'master:')):
                continue
            frame = child.get('data-pptx-frame')
            if frame and float(frame.split()[1]) < 90 and child.xpath('.//s:text', namespaces=NS):
                replace_text(child, [title])
                continue
            root.remove(child)
        root.append(text(54, 695, footer, 13, GRAY))
    return root


def metric(summary, label, key):
    return summary['configurations'][label][key]['value']


def pct(value):
    return 'N/A' if value is None else f'{100 * value:.1f}%'


def main():
    parser = ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--calibration', required=True)
    parser.add_argument('--cases', required=True)
    parser.add_argument('--screenshot', required=True)
    parser.add_argument('--recheck', default='outputs/closing/repro/submission_recheck.json')
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary = json.loads(Path(args.summary).read_text(encoding='utf-8'))
    if summary['status'] not in ['source_reviewed', 'human_scored']:
        raise ValueError('Completed scored results are required.')
    calibration = json.loads(Path(args.calibration).read_text(encoding='utf-8'))['selected']
    cases = json.loads(Path(args.cases).read_text(encoding='utf-8'))
    recheck = json.loads(Path(args.recheck).read_text(encoding='utf-8'))
    if recheck['freeze_sha256'] != summary['freeze_sha256']:
        raise ValueError('The recheck must reference the same frozen study.')
    screenshot = workspace / 'images/closing-system.png'
    shutil.copy2(args.screenshot, screenshot)
    pages = []
    notes = []

    def save(source, root, title, seconds, chinese, english, source_label):
        number = len(pages) + 1
        filename = f'closing_{number:02}.svg'
        for i, child in enumerate(root):
            if child.tag.endswith('g') and not child.get('id'):
                child.set('id', f'content-{number:02}-{i:03}')
        (workspace / 'authoring-svg-flat' / filename).write_bytes(E.tostring(root, encoding='utf-8'))
        (workspace / 'notes' / f'closing_{number:02}.md').write_text(
            f'中文逐字稿\n\n{chinese}\n\nEnglish Script\n\n{english}\n', encoding='utf-8')
        pages.append({'source_slide': source, 'svg': filename})
        notes.append({'page': number, 'title': title, 'seconds': seconds, 'chinese': chinese,
                      'english': english, 'source': source_label})

    def content(title, footer='Frozen OCS study | Review against original sources'):
        return copy_page(workspace, 10, title, footer, blank=True)

    root = copy_page(workspace, 1)
    for group in groups_with_text(root):
        value = ''.join(group.xpath('.//s:text//text()', namespaces=NS))
        if 'Junkai Huang' in value:
            replace_text(group, ['Junkai Huang | Leeds SID 201804121',
                                 'SWJTU ID 2023115799 | Supervisor Prof. Deqing Huang'], 24)
        if 'Proposal Defense' in value:
            replace_text(group, ['SWJTU-Leeds Joint School | Undergraduate Project Viva'], 22)
    save(1, root, 'Project viva', 18,
         '各位老师好，我是黄俊凯，指导教师是黄德青教授。下面汇报接触网标准问答系统的实现、受控实验以及研究结论。',
         'Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. I will present the implemented OCS standards assistant, its controlled evaluation and the conclusions supported by this study.', 'Formal title and student identity')

    root = copy_page(workspace, 2)
    headings = ['01  System and scope', '02  Study design', '03  Results and limitations', '04  Conclusions and discussion']
    for group in groups_with_text(root):
        value = ''.join(group.xpath('.//s:text//text()', namespaces=NS))
        for i in range(4):
            if value.startswith(f'{i+1:02}  '):
                replace_text(group, [headings[i]])
    save(2, root, 'Contents', 10, '汇报分为系统与范围、实验设计、结果与局限，以及结论四部分。',
         'The presentation covers the system, the study design, the measured results and the conclusions.', 'Viva structure')

    def part(source, number, title, items, chinese, english):
        root = copy_page(workspace, source)
        for group in groups_with_text(root):
            frame = group.get('data-pptx-frame', '').split()
            if len(frame) != 4:
                continue
            x, y, w, h = map(float, frame)
            value = ''.join(group.xpath('.//s:text//text()', namespaces=NS))
            if value.isdigit() and len(value) == 2:
                replace_text(group, [f'{number:02}'])
            elif x > 500 and y < 160:
                replace_text(group, title.split('\n'), 40)
            elif x > 500 and y >= 160:
                replace_text(group, items, 27)
        save(source, root, title.replace('\n', ' '), 4, chinese, english, 'SWJTU native section design')

    part(3, 1, 'System and\nscope', ['Standards consultation', 'Evidence and edition labels', 'Local working system'],
         '首先介绍问题场景和已经实现的系统。', 'First, the problem context and the implemented system.')

    root = copy_page(workspace, 4)
    for group in groups_with_text(root):
        value = ''.join(group.xpath('.//s:text//text()', namespaces=NS))
        if 'Candidate documents' in value:
            replace_text(group, ['Examples from the selected corpus'], 24)
        elif '04 / 15' in value:
            replace_text(group, ['04 / 15'], 16)
    save(4, root, 'Standards consultation', 40,
         '接触网部件的技术要求、试验方法和适用条件分散在标准文件中。查询时既要找到相关条文，也要保留用户指定的年份、数值和条件。系统面向资料学习与查询，使用者可以从答案返回原始文件位置。',
         'Technical requirements, test methods and applicable conditions are distributed across OCS standards. A useful answer must retrieve the relevant evidence and preserve the requested edition, numerical values and conditions. The system supports learning and document consultation, with a route back to the original source.', 'Proposal context and retained attributed OCS photograph')

    root = content('The implemented local interface')
    root.append(element('image', href='../images/closing-system.png', x=52, y=110,
                        width=920, height=518, preserveAspectRatio='xMidYMid meet'))
    lines(root, 1000, 175, 'Choose a\nretriever', 15, 25, BLUE, True)
    lines(root, 1000, 315, 'Inspect the\nevidence', 15, 25, BLUE, True)
    lines(root, 1000, 455, 'Open the\nsource page', 15, 25, BLUE, True)
    save(10, root, 'Working interface', 42,
         '这是真实运行的本地界面。用户选择检索方式后输入问题，系统展示带引用的回答、原文片段和文件位置。界面也展示缺失版本、证据不足或接口异常，便于区分返回状态。',
         'This is the working local interface. The user selects a retriever and asks a question. The answer is accompanied by cited excerpts and source locations. Missing editions, insufficient evidence and interface errors have explicit return states, so the user can inspect what happened.', 'Actual local Streamlit screenshot')

    part(6, 2, 'Study\ndesign', ['Three research questions', 'Frozen data and configuration', 'Controlled comparisons'],
         '下面介绍研究设计，以及怎样保证各组结果可以比较。', 'Next, the study design and the controlled comparisons.')

    root = content('From source documents to traceable answers')
    stages = [('PDF / DOCX', 'Parse and locate'), ('Chunks', 'Metadata and indexes'), ('Retrieval', 'BM25 / Dense / Hybrid'),
              ('Evidence Gate', 'Coverage or cosine'), ('DeepSeek', 'Structured claims'), ('Streamlit', 'Answer and sources')]
    for i, (title, label) in enumerate(stages):
        x = 55 + i % 3 * 410
        y = 160 + i // 3 * 225
        rectangle(root, x, y, 360, 150, '#EDF3FA')
        lines(root, x+20, y+45, title, 25, 28, BLUE, True)
        lines(root, x+20, y+100, label, 25, 24)
        if i % 3 < 2:
            root.append(text(x+368, y+80, '→', 30, TEAL, True))
    root.append(element('path', d='M 1050 310 L 1050 345 L 235 345 L 235 375',
                        fill='none', stroke=TEAL, stroke_width=2))
    root.append(text(222, 380, '↓', 26, TEAL, True))
    lines(root, 55, 630, 'Family and edition filters precede ranking. Cited excerpts are checked before display.', 110, 22, GRAY)
    save(10, root, 'System architecture', 45,
         '文档解析时保留PDF文件页码或者DOCX段落位置，再建立词项和向量索引。查询经过标准系列与年份检查后检索候选，Evidence Gate根据启发式信号筛选，再交给DeepSeek生成结构化陈述。展示前验证引用编号与摘录，最后把答案和来源一起返回。',
         'Parsing preserves PDF file pages or DOCX paragraph locations. The system builds lexical and dense indexes, applies standard-family and edition constraints, and retrieves candidate passages. The heuristic Evidence Gate filters evidence before DeepSeek generates structured claims. Citation identifiers and literal excerpts are validated before the answer and sources are displayed.', 'Frozen pipeline and configuration')

    root = content('A fixed benchmark and five configurations')
    rectangle(root, 55, 145, 560, 180)
    lines(root, 80, 190, '20 development questions', 35, 30, BLUE, True)
    lines(root, 80, 245, '16 answerable + 4 unanswerable\nWeight and threshold selection', 38, 25)
    rectangle(root, 655, 145, 560, 180, '#EDF7F6')
    lines(root, 680, 190, '80 held-out test questions', 35, 30, TEAL, True)
    lines(root, 680, 245, '64 answerable + 16 unanswerable\n80 × 5 = 400 primary slots', 38, 25)
    config = [('B1', 'BM25'), ('B2', 'Dense'), ('B3', 'Hybrid'), ('A1', 'Edition checks off'), ('A2', 'Gate off')]
    for i, (name, label) in enumerate(config):
        x = 55 + i * 237
        rectangle(root, x, 395, 215, 125)
        root.append(text(x+16, 438, name, 30, BLUE, True))
        lines(root, x+16, 480, label, 19, 22)
    lines(root, 55, 575, '25 source documents · 3341 chunks · BAAI/bge-m3 vectors\nTwo-pass assistant source review. Author and evaluator share the same assistant system.', 100, 23, GRAY)
    save(10, root, 'Benchmark and comparisons', 50,
         '基准包含二十道开发题和八十道测试题，测试集有六十四道可答与十六道不可答题。五组配置保持相同语料和生成设置。A1只关闭版本检查，仍保留标准系列过滤；A2只关闭检索门槛，仍保留提示词、引用校验和错误处理。题目与输出由助手对照原文核查，报告保留这一评价方式的偏差限制。',
         'The benchmark has twenty development and eighty held-out test questions. The test set contains sixty-four answerable and sixteen unanswerable items. Five configurations share the corpus and generation settings. A1 removes edition checks while keeping family filtering. A2 removes the retrieval gate while keeping the prompt, citation validation and error handling. Source review was performed by the assistant, and the report retains the resulting evaluation limitations.', 'Frozen benchmark, configurations and protocol amendment')

    part(9, 3, 'Results and\nlimitations', ['Measured comparisons', 'Source-bound failure analysis', 'Uncertainty and study limits'],
         '接下来介绍冻结测试的实际观察。', 'I will now present the measured observations from the frozen test.')

    root = content('Measured test results across five configurations')
    columns = [('B1', 435), ('B2', 595), ('B3', 755), ('A1', 915), ('A2', 1075)]
    for label, x in columns:
        root.append(text(x, 155, label, 28, BLUE, True))
    metrics = [('Recall@5', 'recall_at_5'), ('Answer correctness', 'answer_correctness'), ('Citation support', 'citation_support'),
               ('Wrong-edition rate', 'wrong_edition_rate'), ('Refusal recall', 'refusal_recall'), ('False refusal', 'false_refusal')]
    for i, (label, key) in enumerate(metrics):
        y = 220 + i * 61
        if i % 2 == 0:
            rectangle(root, 55, y-35, 1160, 58, '#F3F6FA')
        root.append(text(75, y, label, 25, DARK, True))
        for name, x in columns:
            root.append(text(x, y, pct(metric(summary, name, key)), 25, TEAL if name == 'B3' else DARK, name == 'B3'))
    lines(root, 55, 625, 'Measured first-attempt observations. Denominators and paired uncertainty are retained in the report.', 108, 20, GRAY)
    save(10, root, 'Measured results', 65,
         f"表中是五组配置的实际首次运行结果。Hybrid的Recall@5为{pct(metric(summary,'B3','recall_at_5'))}，完整正确率为{pct(metric(summary,'B3','answer_correctness'))}。引用支持、错版本与拒答指标需要结合分母共同解释。报告保留了相同题目的成对差值、按group_id重采样的区间和全部失败记录。",
         f"These are the measured first-attempt results for the five configurations. Hybrid achieved Recall at five of {pct(metric(summary,'B3','recall_at_5'))} and complete answer correctness of {pct(metric(summary,'B3','answer_correctness'))}. Citation support, edition errors and refusal measures must be interpreted with their denominators. The report retains paired differences, group-bootstrap intervals and all failed slots.", 'Source-reviewed measured_results.json')

    case = cases[0] if cases else None
    if not case:
        raise ValueError('A source-bound scored case is required.')
    root = content('Inspect the failure at its original source')
    case_id = case.get('question_id', '')
    lines(root, 65, 160, f"Case {case_id}", 65, 32, BLUE, True)
    explanation = case.get('analysis') or case.get('grade_reason')
    if not explanation:
        raise ValueError('Case interpretation is required.')
    case_explanation = ' '.join(re.split(r'(?<=[.!?])\s+', explanation)[:3])
    lines(root, 65, 235, textwrap.shorten(case_explanation, width=300, placeholder='…'), 75, 28)
    root.append(text(65, 470, 'Source locations', 25, BLUE, True))
    locations = case.get('source_locations', [])
    if not isinstance(locations, list):
        locations = [locations]
    locations = [re.sub(r'PDF第(\d+)页', r'PDF file page \1', str(location)) for location in locations]
    lines(root, 65, 515, '\n'.join(locations[:3]), 93, 23)
    lines(root, 65, 630, 'Check required facts, cited evidence, units, conditions and requested edition together.', 108, 22, GRAY)
    save(10, root, 'Failure analysis', 48,
         f'在{case_id}中，题目问扭矩仪精度。Dense找到了有出处的装配力矩公差，但对象不同。Hybrid命中PDF文件第10页的仪器精度要求，能沿出处回查。这个案例说明引用支撑与整题正确性需要分别判断。',
         f'In {case_id}, the question asked for torque instrument precision. Dense cited a documented tolerance for assembly torque. Hybrid found the instrument precision requirement on PDF file page ten. The source trace shows exactly where the two requirements diverge and why citation support and complete correctness are scored separately.', 'Source-bound scored case and original locations')

    part(12, 4, 'Conclusions and\ndiscussion', ['Three research questions', 'Scope and limitations', 'Delivered system and evidence'],
         '最后总结研究问题、限制和项目成果。', 'Finally, the research questions, limitations and project outcomes.')

    root = content('Observed findings for the three questions')
    descriptions = [
        ('RQ1  Retrieval', f"Recall@5  B1 {pct(metric(summary,'B1','recall_at_5'))} · B2 {pct(metric(summary,'B2','recall_at_5'))} · B3 {pct(metric(summary,'B3','recall_at_5'))}", 'BM25 is the best-supported default for this corpus. Hybrid remains selectable.'),
        ('RQ2  Editions', f"Wrong-edition rate  B3 {pct(metric(summary,'B3','wrong_edition_rate'))} · A1 {pct(metric(summary,'A1','wrong_edition_rate'))}", 'No observed reduction in wrong editions in this limited comparison.'),
        ('RQ3  Evidence Gate', f"Unsupported answers  B3 {summary['configurations']['B3']['unsupported_answer_incidence']['numerator']}/80 · A2 {summary['configurations']['A2']['unsupported_answer_incidence']['numerator']}/80", 'The test showed the same unsupported-answer and refusal rates.'),
    ]
    for i, (label, description, interpretation) in enumerate(descriptions):
        y = 150 + i * 155
        root.append(text(65, y, label, 29, BLUE, True))
        lines(root, 65, y+55, description, 83, 27)
        lines(root, 65, y+100, interpretation, 100, 22, GRAY)
    lines(root, 65, 645, 'Interpretation is limited to this corpus, benchmark and assistant-reviewed scoring protocol.', 106, 21, GRAY)
    save(10, root, 'RQ conclusions', 52,
         'Hybrid比Dense的Recall@5高18.75个百分点。BM25在同一语料上的召回和正确率最高，因此建议在标准号或部件明确时优先选BM25。RQ2缺少真实正式版本对，各组都没有出现错版本。RQ3两组各有一条无支撑答案，拒答指标相同。零宽度区间反映当前样本的重采样结果。',
         'Hybrid exceeded Dense by 18.75 percentage points on Recall at five. BM25 had the highest measured recall and correctness, supporting its use for queries with known standard numbers or terms. Version filtering showed no measured improvement and the corpus lacked verified formal edition pairs. With the gate on or off, one output was unsupported and refusal rates matched. The zero-width intervals reflect the observed sample.', 'Measured configurations and paired analysis')

    root = content('Delivered outcomes and remaining limits')
    root.append(text(65, 160, 'Delivered', 31, BLUE, True))
    agreement = recheck['outputs_agreeing_on_all_applicable_fields']
    outputs = recheck['outputs']
    lines(root, 65, 220, f'Working local QA system\nSource-reviewed 100-question benchmark\nFrozen five-configuration experiment\nMasked recheck: {agreement}/{outputs} outputs aligned', 41, 27)
    root.append(text(675, 160, 'Study limits', 31, BLUE, True))
    lines(root, 675, 220, 'No verified formal edition pairs\nBenchmark facts drawn from six documents\nShared assistant author and evaluator\nHeuristic signals can accept or reject incorrectly', 37, 27)
    lines(root, 65, 585, 'Future work should add independently checked facts and verified edition pairs,\nthen repeat the frozen comparison under the same scoring definitions.', 96, 25, GRAY)
    save(10, root, 'Outcomes and limitations', 38,
         f'项目交付了本地系统、题集和冻结实验。遮蔽配置与原评分后，抽查二十四题共{outputs}条输出，{agreement}条的适用字段全部一致。两轮复核共享助手工作流。保存的首次输出和评分可以在本机离线复算。真实版本对和独立领域专家复核仍是后续工作。',
         f'The project delivers a local system, benchmark and frozen experiment. The masked review of twenty-four questions matched the original judgement on all applicable fields for {agreement} of {outputs} outputs. Both passes share the assistant workflow. Saved first attempts and grades allow offline recomputation. Independent domain review and verified edition pairs remain priorities.', 'Corpus manifest, masked sample and reproducibility receipt')

    root = copy_page(workspace, 15)
    for group in groups_with_text(root):
        value = ''.join(group.xpath('.//s:text//text()', namespaces=NS))
        if 'Edition checks and evidence-based refusal' in value or 'Traceable answers' in value:
            replace_text(group, ['Evidence-traceable OCS standards consultation', 'Frozen comparisons and recorded findings'], 28)
    save(15, root, 'Questions and discussion', 12, '我的汇报到这里，谢谢各位老师，欢迎提问。',
         'Thank you for your attention. I welcome your questions and discussion.', 'Project conclusion')

    root = content('References', 'Primary literature and project source records')
    references = [
        '[1] Lewis et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020.',
        '[2] Robertson and Zaragoza. The Probabilistic Relevance Framework. 2009. doi 10.1561/1500000019.',
        '[3] Karpukhin et al. Dense Passage Retrieval. EMNLP, 2020. doi 10.18653/v1/2020.emnlp-main.550.',
        '[4] Ma et al. Query Rewriting in Retrieval-Augmented Large Language Models. EMNLP, 2023.',
        '[5] Shi et al. Large Language Models Can Be Easily Distracted by Irrelevant Context. ICML, 2023.',
        '[6] Es et al. RAGAs. EACL Demonstrations, 2024. doi 10.18653/v1/2024.eacl-demo.16.',
        '[7] Chen et al. BGE M3-Embedding. 2024. arXiv 2402.03216.',
        '[8] Rayo Mosquera et al. Hybrid retrieval for regulatory text. RegNLP, 2025.',
        '[9] Russo et al. Railway engineering RAG case study. 2026. arXiv 2607.01244v2.',
        '[10] Huwiler et al. VersionRAG. 2025. arXiv 2510.08109.',
    ]
    y = 150
    for reference in references:
        y = lines(root, 65, y, reference, 104, 22, leading=27) + 13
    save(10, root, 'References', 0, '此页列出主要参考文献。', 'This page lists the principal references.', 'Verified primary literature metadata')

    root = content('Frozen retrieval and Evidence Gate parameters')
    lines(root, 65, 155, 'S(q,c) = (1 − w) B(q,c) + w D(q,c)', 80, 34, BLUE, True)
    lines(root, 65, 230, f"Selected w = {calibration['vector_weight']:.2f}\nQuery-wise min–max normalisation over eligible chunks\nBM25 k1 = 1.5 and b = 0.75 · Top-K = 5", 80, 27)
    lines(root, 65, 405, f"Gate accepts coverage ≥ {calibration['min_coverage']:.2f} OR raw cosine ≥ {calibration['min_cosine']:.2f}", 80, 29, TEAL, True)
    lines(root, 65, 475, 'Shared jieba tokenisation and fixed domain dictionary\nStandard identifiers and fixed stopwords excluded from coverage\nParameters selected on development data before the study freeze', 88, 25)
    save(10, root, 'Parameter details', 0, '权重和门槛只使用开发集选择，词项覆盖率与原始余弦是启发式信号。',
         'Weights and thresholds were selected on development data. Coverage and raw cosine are heuristic signals.', 'Selected calibration and frozen preprocessing')

    root = content('Scoring populations and ablation definitions')
    rows = [('Recall and correctness', '64 answerable questions'), ('Refusal recall', '16 unanswerable questions'),
            ('False refusal', '64 answerable questions'), ('Citation support', 'Displayed cited claims'),
            ('Wrong-edition rate', 'All unambiguous available or missing edition requests')]
    y = 160
    for label, definition in rows:
        root.append(text(65, y, label, 25, BLUE, True))
        lines(root, 485, y, definition, 48, 24)
        y += 80
    lines(root, 65, 600, 'A1 keeps family filtering. A2 keeps prompts, citation validation and errors.\nAll first-attempt failures remain in their predeclared populations.', 99, 23, GRAY)
    save(10, root, 'Metric definitions', 0, '分母按预先定义保留。错误版本率同时包含请求版本已收录和缺失两类明确版本请求。',
         'The predeclared denominators are retained. Wrong-edition rate includes unambiguous requests for both available and missing editions.', 'Protocol scoring definitions')

    (workspace / 'page_plan.json').write_text(json.dumps({'schema': 'ppt-master.roundtrip-page-plan.v1', 'pages': pages}, indent=2), encoding='utf-8')
    animations = {'version': 1, 'defaults': {'transition': {'effect': 'none', 'duration': 0.0}},
                  'slides': {Path(page['svg']).stem: {'animation': {'effect': 'none'}} for page in pages}}
    (workspace / 'animations.json').write_text(json.dumps(animations, indent=2), encoding='utf-8')
    (output / 'content_mapping.json').write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding='utf-8')
    script = ['# OCS Viva 中英文对照讲稿', '', f"主讲15页，预计{sum(n['seconds'] for n in notes)/60:.1f}分钟。备份3页按提问使用。", '']
    for row in notes:
        script += [f"## 第{row['page']}页 {row['title']}", '', f"预计讲述{row['seconds']}秒。", '', '中文', '', row['chinese'], '', 'English', '', row['english'], '']
    (output / 'OCS_Viva_CN_EN_Script.md').write_text('\n'.join(script), encoding='utf-8')
    qa = [
        ('为什么DeepSeek不能直接回答？', 'Why use retrieved evidence with DeepSeek?',
         '技术标准查询需要核对具体版本、原文位置、数值和条件。检索把可检查的来源放进上下文，用户还能打开原文核查。',
         'Standards queries require a specific edition, source location, numerical values and conditions. Retrieval supplies inspectable source passages, and the user can open the original document.'),
        ('为什么选择RAG？', 'Why was RAG selected?',
         '研究目标是对许可资料进行可追溯查询。RAG可以把解析、索引、版本约束和来源展示连成可检查流程，适合本项目的数据与计算资源。',
         'The aim is traceable consultation of permitted documents. RAG connects parsing, indexing, edition constraints and source display in an inspectable workflow suited to the available data and computing resources.'),
        ('项目的技术贡献是什么？', 'What is the technical contribution?',
         '贡献集中在接触网标准场景的工程实现与受控评估，包括标准系列和年份处理、可定位的证据、启发式门控，以及五配置的比较记录。BM25、Dense与RAG沿用已有研究。',
         'The contribution is the domain-specific implementation and controlled evaluation, including standard-family and year handling, source-located evidence, a heuristic gate and five recorded comparisons. BM25, dense retrieval and RAG build on established research.'),
        ('BM25、Dense和Hybrid有什么区别？', 'How do BM25, Dense and Hybrid differ?',
         'BM25按词项匹配排序，Dense按嵌入余弦相似度排序，Hybrid对候选分数归一化后加权融合。三者使用同一语料和版本约束，便于比较。',
         'BM25 ranks lexical matches. Dense retrieval ranks embedding cosine similarity. Hybrid combines normalised scores using a selected weight. The comparison uses the same corpus and edition constraints.'),
        ('为什么Hybrid不一定更好？', 'Why can Hybrid fail to improve retrieval?',
         '语义相似可能引入同主题但不支持问题的段落，归一化和权重也影响排序。效果需要按冻结题目和正确证据判断，并结合差值区间解释。',
         'Semantic similarity can introduce passages on the same topic that do not support the question. Normalisation and weighting also change ranking. The frozen questions, evidence labels and paired intervals determine the observed effect.'),
        ('现场默认选什么？', 'Which retriever would you select by default?',
         '对这个语料和已有测试，BM25的召回与完整正确率最高，而且无需额外查询向量请求。标准号或部件已知时建议优先BM25。Hybrid保留为可选模式，后续可专门调查同义改写。',
         'BM25 produced the highest measured recall and complete correctness on this corpus and requires no query embedding request. It is the supported default for known standard numbers or component names. Hybrid remains selectable for future research on paraphrased queries.'),
        ('Evidence Gate怎样工作？', 'How does the Evidence Gate work?',
         f"候选的词项覆盖率达到{calibration['min_coverage']:.2f}，或者原始余弦达到{calibration['min_cosine']:.2f}时通过。这些阈值仅用开发集选择，含义是启发式证据筛选。",
         f"A candidate passes when lexical coverage reaches {calibration['min_coverage']:.2f} or raw cosine reaches {calibration['min_cosine']:.2f}. These development-selected thresholds provide heuristic evidence screening."),
        ('门控能消除幻觉吗？', 'Can the gate eliminate unsupported answers?',
         '启发式信号可能接受无关证据，也可能拒绝有效证据。因此评价同时保留无依据回答、拒答召回、误拒答和回答覆盖率，并逐条核查语义支持。',
         'Heuristic signals can accept irrelevant evidence or reject useful evidence. Evaluation therefore includes unsupported answers, refusal recall, false refusal and answer coverage, alongside claim-level semantic review.'),
        ('怎样验证版本正确？', 'How is edition handling evaluated?',
         '从文档元数据和请求中提取标准系列与年份。明确版本缺失时系统提前返回。A1关闭年份相关检查而保留系列过滤，再比较明确版本请求中的错版本行为。',
         'The system extracts the standard family and year from metadata and the request. A missing explicit edition triggers an early return. A1 removes year-related checks while retaining family filtering, enabling a comparison on unambiguous edition requests.'),
        ('没有两个正式版本怎么办？', 'What follows from the missing formal edition pairs?',
         '本次结论限定在选定语料中的已有版本和未收录年份请求。真实旧版与假设输入分别记录。扩展到多个正式版本之间的选择，需要补充可用文档并重新做冻结比较。',
         'The conclusions cover available editions and unavailable-year requests in this corpus. Verified historical editions and hypothetical inputs are recorded separately. Evaluating selection between multiple formal editions requires additional usable documents and a repeated frozen comparison.'),
        ('100道题是否足够？', 'What can a 100-question benchmark establish?',
         '这个规模支持本科项目的固定语料比较。测试集只有80题，题目事实集中在六份文档，因而报告保留分组重采样区间、分类样本数和覆盖限制。',
         'The size supports a fixed-corpus undergraduate comparison. The test set contains eighty items and the question facts come from six documents. Group-bootstrap intervals, category counts and coverage limitations are therefore retained.'),
        ('五组实验怎样保证公平？', 'How are the five configurations controlled?',
         '各组共享语料、分块、生成设置、Top-K和评分规则。A1保留系列过滤，A2保留提示词和引用校验。所有首次失败记录保留，恢复尝试独立登记。',
         'The configurations share the corpus, chunks, generation settings, Top-K and scoring rules. A1 retains family filtering, and A2 retains prompts and citation validation. First-attempt failures remain recorded and recoveries have separate attempt identities.'),
        ('答案由谁评分？', 'Who reviewed the benchmark and answers?',
         '按本次修订安排，由Codex助手对照原文核查，保存执行者、时间、方式和理由。题目由同一助手体系准备和评价，独立人工或领域专家验证仍是后续需要补充的工作。',
         'Under the amended arrangement, the Codex assistant reviewed the original sources and retained the executor, time, method and reasoning. Benchmark preparation and evaluation used the same assistant system. Independent human or domain-expert validation remains further work.'),
        ('正式结果是什么？', 'What are the principal measured observations?',
         f"B3的Recall@5为{pct(metric(summary,'B3','recall_at_5'))}，完整正确率为{pct(metric(summary,'B3','answer_correctness'))}。B3与A1错版本率分别为{pct(metric(summary,'B3','wrong_edition_rate'))}和{pct(metric(summary,'A1','wrong_edition_rate'))}，解释时结合分母和成对区间。",
         f"B3 has Recall at five of {pct(metric(summary,'B3','recall_at_5'))} and complete answer correctness of {pct(metric(summary,'B3','answer_correctness'))}. Wrong-edition rates for B3 and A1 are {pct(metric(summary,'B3','wrong_edition_rate'))} and {pct(metric(summary,'A1','wrong_edition_rate'))}. Interpretation includes the denominators and paired intervals."),
        ('抽样复核能说明什么？', 'What does the masked recheck establish?',
         f'从测试集分层抽24题，遮蔽配置名和原评分后复核{outputs}个保存输出，{agreement}个的适用字段一致。两轮共享助手工作流，结果表明这次抽样复核的一致性。',
         f'The recheck sampled twenty-four held-out questions. With configurations and original labels masked, all applicable judgements agreed for {agreement} of {outputs} saved outputs. Both passes used the same assistant workflow, so this measures consistency on the selected sample.'),
        ('怎样复现实验？', 'How can the experiment be reproduced?',
         '使用冻结题集、语料和向量指纹、代码与环境记录，并保持相同模型设置。已保存首次输出和评分记录，可以离线重新计算指标，在线重新生成可能受到外部模型变化影响。',
         'Use the frozen questions, corpus and vector fingerprints, code, environment and model settings. Saved first-attempt outputs and grades permit offline metric recomputation. New online generations can be affected by changes in the external model service.'),
        ('Embedding接口不能使用怎么办？', 'What happens if the embedding service fails?',
         '已保存的文档向量仍保留在本机，BM25可以继续查询。Dense与Hybrid需要当前模型的查询向量，接口失败会明确记录，重新恢复的运行有独立身份。',
         'Stored document vectors remain local and BM25 remains available. Dense and Hybrid require query vectors from the configured model. Service failures are recorded explicitly and recovered runs retain separate identities.'),
        ('文档与外部API有哪些注意事项？', 'How are documents and external API processing handled?',
         '项目使用已获准处理的本地资料，只有获准片段会发送至配置的服务。密钥与完整标准保存在本机受控目录，公开交付使用代码、方法和允许的来源信息。',
         'The project uses local documents authorised for processing. Approved excerpts are sent to the configured services. Credentials and complete standards remain in controlled local storage, while public delivery uses code, methods and permitted source information.'),
    ]
    qa_lines = ['# OCS Viva 中英文问答', '']
    for i, (question_cn, question_en, answer_cn, answer_en) in enumerate(qa, 1):
        qa_lines += [f'## {i}. {question_cn}', '', question_en, '', answer_cn, '', answer_en, '']
    (output / 'OCS_Viva_QA_CN_EN.md').write_text('\n'.join(qa_lines), encoding='utf-8')
    print(json.dumps({'slides': len(pages), 'main_seconds': sum(n['seconds'] for n in notes), 'output': str(output)}))


if __name__ == '__main__':
    main()
