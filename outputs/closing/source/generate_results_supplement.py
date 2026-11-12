"""Generate supplementary tables from the frozen, source-scored study summary."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE.parent / 'research/closing-experiment/measured_results.json'
data = json.loads(SOURCE.read_text(encoding='utf-8'))
labels = ['B1', 'B2', 'B3', 'A1', 'A2']


def ratio(metric):
    if metric['denominator'] == 0:
        return 'NA (0 denominator)'
    return f"{metric['numerator']:g}/{metric['denominator']} ({100 * metric['value']:.2f}%)"


lines = [
    '# Supplementary measured results', '',
    'Study frozen and executed on 12 November 2026. All tables use primary first attempts. '
    'The recorded review method is assistant_source_review, with Codex as the executing reviewer. '
    'Question preparation and evaluation share the same assistant workflow. Independent human or expert validation remains outstanding.', '',
    f"Frozen manifest SHA-256 `{data['freeze_sha256']}`.", '',
    f"Summary SHA-256 `{hashlib.sha256(SOURCE.read_bytes()).hexdigest()}`.", '',
    '## Design and populations', '',
    'The corpus has 25 independently numbered documents, 3341 chunks and 3341 1024-dimensional vectors. '
    'The 20 development questions contain 16 answerable and four unanswerable items. '
    'The 80 held-out test questions contain 64 answerable and 16 unanswerable items. '
    'Their fact coverage is concentrated in six corpus documents. No verified formal edition pair was admitted.', '',
    'B1 uses BM25, B2 Dense and B3 Hybrid. A1 disables edition checks while retaining standard-family filtering. '
    'A2 disables the Evidence Gate while retaining the prompt, citation validation and error handling. '
    'Every configuration has 80 primary slots. The nine invalid-citation first attempts remain in the primary analysis. '
    'Nine recovery attempts, including five displayed answers and four further citation failures, are recorded separately.', '',
    'The selected Hybrid weight is 0.50 from candidates 0.25, 0.50 and 0.75. '
    'Query-wise normalised lexical and dense scores enter S = (1 − w)B + wD. '
    'The development-selected Gate accepts term coverage ≥0.20 OR raw cosine ≥0.50. '
    'Thresholds are heuristic signals. Semantic support, values, units and conditions are judged against sources.', '',
    '## Overall metrics', '',
    '| Metric | ' + ' | '.join(labels) + ' |',
    '| --- | ' + ' | '.join(['---'] * 5) + ' |',
]
for metric, title in [
    ('recall_at_5', 'Recall@5'), ('mrr_at_5', 'MRR@5'),
    ('answer_correctness', 'Complete answer correctness'), ('citation_support', 'Citation support'),
    ('wrong_edition_rate', 'Wrong-edition rate'), ('refusal_recall', 'Refusal recall'),
    ('false_refusal', 'False refusal'), ('unsupported_answer_incidence', 'Unsupported answer incidence'),
    ('answer_coverage', 'Displayed answer coverage'), ('completion_rate', 'Protocol completion rate'),
]:
    lines.append('| ' + title + ' | ' + ' | '.join(ratio(data['configurations'][label][metric]) for label in labels) + ' |')
lines += ['', 'Recall and correctness use all 64 answerable items. Refusal recall uses all 16 unanswerable items. '
          'False refusal uses all 64 answerable items. Citation support counts displayed cited claims. '
          'Wrong-edition rate uses 68 unambiguous available-or-missing edition requests. '
          'Ambiguous requests remain in the refusal and coverage analysis. '
          'Answer coverage includes displayed substantive partial answers. Protocol completion excludes parsing/citation failures.', '',
          '## Latency', '',
          'All 80 first attempts per configuration are retained, including early refusals and errors. '
          'Each cell gives median / nearest-rank p95 in milliseconds.', '',
          '| Configuration | Retrieval | Generation | End to end |', '| --- | --- | --- | --- |']
for label in labels:
    row = data['configurations'][label]
    cells = [f"{row[key]['median_ms']:.2f} / {row[key]['p95_ms']:.2f}" for key in
             ['retrieval_latency', 'generation_latency', 'total_latency']]
    lines.append('| ' + label + ' | ' + ' | '.join(cells) + ' |')
lines += ['', '## Category results', '',
          '| Configuration | Category | Questions | Recall@5 | Correctness | Refusal recall |',
          '| --- | --- | --- | --- | --- | --- |']
for label in labels:
    for category, row in sorted(data['analysis']['categories'][label].items()):
        cells = [ratio(row['metrics'][key]) for key in ['recall_at_5', 'answer_correctness', 'refusal_recall']]
        lines.append(f"| {label} | {category} | {row['n']} | " + ' | '.join(cells) + ' |')
lines += ['', '## Version availability and failures', '',
          '| Configuration | Availability class | Items | Displayed answers |', '| --- | --- | --- | --- |']
for label in labels:
    for availability, row in data['configurations'][label]['edition_availability'].items():
        lines.append(f"| {label} | {availability} | {row['items']} | {row['answered']} |")
lines += ['', 'Failure-type counts follow the source-judgement labels. Different labels can denote related failure behaviours.', '']
for label in labels:
    lines.append(f"- {label} — " + ', '.join(f'{key} {count}' for key, count in data['configurations'][label]['failure_types'].items()))
lines += ['', '## Paired differences and uncertainty', '',
          'Question groups preserve related conversations. Paired bootstrap uses 50 group_id units, seed 3801 and 2000 resamples. '
          'Differences below are absolute percentage points with 95% intervals.', '',
          '| Comparison | Metric | Difference | 95% interval |', '| --- | --- | --- | --- |']
for comparison, metrics in data['analysis']['paired_comparisons'].items():
    for metric, row in metrics.items():
        if row['absolute_difference'] is None:
            continue
        interval = ', '.join(f'{100 * value:.2f}' for value in row['ci_95'])
        lines.append(f"| {comparison} | {metric} | {100 * row['absolute_difference']:.2f} | [{interval}] |")
lines += ['', '## Planned targets and observed findings', '',
          '| B3 design target | Primary observation | Assessment in this benchmark |',
          '| --- | --- | --- |',
          '| Recall@5 ≥0.80 | 61/64 = 0.953125 | Target met |',
          '| Answer correctness ≥0.80 | 57/64 = 0.890625 | Target met |',
          '| Citation support ≥0.90 | 140/141 = 0.992908 | Target met |',
          '| False refusal ≤0.10 | 0/64 | Target met |',
          '| 20–30 usable documents | 25 document identities | Target met |',
          '| Two families with two formal editions each, where obtainable | No verified formal pair admitted | Scope restricted |', '',
          'RQ1 receives evidence for higher Hybrid recall than Dense in this sample. BM25 has the highest observed recall. '
          'RQ2 has zero wrong-edition answers for both B3 and A1, with no observed incremental benefit. '
          'RQ3 has one unsupported answer per 80 slots for both B3 and A2, and equal refusal measures. '
          'The proposed targets were fixed design goals. The present values are recorded observations under the adjusted review protocol.', '',
          '## Source-bound cases', '',
          'In test-041, Dense answered with source-supported assembly torque tolerances around a 44 N m boundary. '
          'The question requested torque instrument precision, given in the source as better than ±3%. '
          'Hybrid supplied the requested fact. This illustrates how citation support and task correctness can diverge.', '',
          'In test-079, Hybrid supplied values from a conductor-length table for an ambiguous follow-up. '
          'The expected action required clarification of the standard and length object. Source-supported values still failed that task.', '',
          'The original source locations and question-by-question reasoning remain in the controlled local research records. '
          'These cases support diagnostic interpretation within this corpus. They do not certify engineering decisions.', '',
          '## Limits and archived evidence', '',
          'The shared assistant preparation and scoring workflow, six-document benchmark coverage, missing formal edition pairs, '
          'heuristic Gate and externally hosted model alias constrain interpretation. '
          'Independent scoring, wider sources and valid edition-pair comparisons remain future validation work.', '',
          'The public measured JSON preserves denominators, per-category data, paired intervals and raw-result hashes. '
          'Controlled primary results, all 400 slot mappings, original-source reviews and recovery records remain locally archived. '
          'API account invoices and earlier unlogged expenditure remain outstanding. '
          'The £35 historical allocation is a reserve. The recorded chat-ledger estimate is approximately USD 0.3491.', '']
(HERE / 'Results_Supplement_EN.md').write_text('\n'.join(lines), encoding='utf-8')
print('Wrote source-scored supplementary results.')
