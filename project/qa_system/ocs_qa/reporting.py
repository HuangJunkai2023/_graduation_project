"""Render a supplementary experiment report from complete measured results only."""
import json
from pathlib import Path

METRICS = {
    'recall_at_5': 'Recall@5', 'mrr_at_5': 'MRR@5',
    'answer_correctness': 'Answer correctness', 'citation_support': 'Citation support',
    'citation_coverage': 'Citation coverage', 'citation_resolvability': 'Citation resolvability',
    'wrong_edition_rate': 'Wrong-edition rate', 'refusal_recall': 'Refusal recall',
    'false_refusal': 'False refusal', 'unsupported_answer_incidence': 'Unsupported / all questions',
    'unsupported_among_answers': 'Unsupported / answered questions', 'answer_coverage': 'Answer coverage'}


def _number(value):
    return 'N/A' if value is None else f'{value:.3f}'


def render_report(results_path, output_path):
    data = json.loads(Path(results_path).read_text(encoding='utf-8'))
    if data.get('status') != 'human_scored' or not data.get('grades_sha256') or not data.get('run_files_sha256'):
        raise ValueError('Only a complete, provenance-bound human-scored summary can produce a measured report.')
    labels = ['B1', 'B2', 'B3', 'A1', 'A2']
    lines = ['# OCS Question-Answering: Controlled Experiment Report', '',
        'This supplementary report describes measured observations on the frozen corpus-bound benchmark. '
        'It is not the final seven-page university report and does not certify railway standards or engineering decisions.', '',
        '## Study design', '',
        'The benchmark uses 20 development questions (16 answerable, 4 unanswerable) and 80 held-out '
        'test questions (64 answerable, 16 unanswerable). Development data alone select the hybrid weight '
        'and heuristic evidence thresholds. Each of five configurations contributes 80 primary first-attempt slots. '
        'API failures and unknown interrupted outcomes remain in the relevant denominators.', '',
        '- B1: BM25 with edition filtering and Evidence Gate.',
        '- B2: Dense with edition filtering and Evidence Gate.',
        '- B3: Hybrid with edition filtering and Evidence Gate.',
        '- A1: Hybrid without edition checks; standard-family filtering remains.',
        '- A2: Hybrid without the retrieval Evidence Gate; prompts, citation validation and error handling remain.', '',
        '## Overall observations', '', '| Metric | B1 | B2 | B3 | A1 | A2 |', '| --- | --- | --- | --- | --- | --- |']
    for key, title in METRICS.items():
        cells = []
        for label in labels:
            metric = data['configurations'][label][key]
            cells.append(f"{_number(metric['value'])} ({metric['numerator']:g}/{metric['denominator']})")
        lines.append('| ' + title + ' | ' + ' | '.join(cells) + ' |')
    lines += ['', 'Citation support is a human judgement on each displayed cited claim and its complete citation set. '
        'Citation coverage and resolvability are mechanical checks of the structured output, not proofs of semantic support. '
        'N/A denotes a zero denominator. Planned targets are not substituted for measured values.', '',
        '## Paired comparisons', '',
        'Differences below are the left configuration minus the comparator in absolute proportion units. '
        'Higher is preferable for recall/correctness/support; lower is preferable for wrong editions, false refusals '
        'and unsupported answers. Group bootstrap uses seed 3801 and 2000 paired resamples; it keeps all questions '
        'within each sampled group together. A small, corpus-bound sample limits generalisation.', '',
        '| Comparison | Metric | Difference | 95% interval | Valid resamples |', '| --- | --- | --- | --- | --- |']
    for comparison, metrics in data['analysis']['paired_comparisons'].items():
        for key, metric in metrics.items():
            interval = metric['ci_95']
            ci = 'N/A' if interval is None else f'[{interval[0]:.3f}, {interval[1]:.3f}]'
            lines.append(f"| {comparison} | {METRICS[key]} | {_number(metric['absolute_difference'])} | {ci} | {metric['valid_replicates']} |")
    lines += ['', '## Category observations', '', '| Configuration | Category | n | Recall@5 | Correctness | Refusal recall |',
              '| --- | --- | --- | --- | --- | --- |']
    for label in labels:
        for category, row in data['analysis']['categories'][label].items():
            m = row['metrics']
            lines.append(f"| {label} | {category} | {row['n']} | {_number(m['recall_at_5']['value'])} | {_number(m['answer_correctness']['value'])} | {_number(m['refusal_recall']['value'])} |")
    lines += ['', '## Availability, timing and failures', '',
              '| Configuration | API errors | Unknown interruptions | Retrieval median / P95 ms | Generation median / P95 ms | End-to-end median / P95 ms |',
              '| --- | --- | --- | --- | --- | --- |']
    for label in labels:
        row = data['configurations'][label]
        latency = [f"{_number(row[key]['median_ms'])} / {_number(row[key]['p95_ms'])}" for key in ['retrieval_latency','generation_latency','total_latency']]
        lines.append(f"| {label} | {row['api_errors']} | {row['interrupted_unknown_outcomes']} | " + ' | '.join(latency) + ' |')
    lines += ['', 'Early refusals and errors are retained in timing summaries when their timings are known; '
        'unknown interrupted timings are not imputed as zero. P95 uses the nearest-rank method.', '']
    for label in labels:
        lines.append(f"- {label} failure categories: `{json.dumps(data['configurations'][label]['failure_types'], ensure_ascii=False)}`")
    lines += ['', '## Interpretation to complete from source review', '',
        '- RQ1: interpret B3–B1 and B3–B2 recall differences alongside category counts and uncertainty.',
        '- RQ2: interpret B3–A1 wrong-edition behaviour, separating available and missing requested editions. '
        'Confirm actual formal edition-pair availability from the frozen corpus manifest; missing-year requests do not establish that those editions exist.',
        '- RQ3: interpret B3–A2 unsupported-answer incidence jointly with refusal recall, false refusal and answer coverage.',
        '- Examine source-bound failure examples before making a causal or general performance claim. '
        'A heuristic Evidence Gate cannot guarantee the elimination of hallucinations.', '',
        '## Provenance', '', f"- Freeze SHA-256: `{data['freeze_sha256']}`",
        f"- Human-grade SHA-256: `{data['grades_sha256']}`", '']
    for name, digest in data['run_files_sha256'].items():
        lines.append(f'- {name}: `{digest}`')
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError('Report exists; choose a new output path to preserve the prior report.')
    destination.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return {'report': str(destination), 'status': 'measured_supplement_requires_author_interpretation'}
