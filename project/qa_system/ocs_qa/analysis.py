"""Predeclared paired group bootstrap; only consume already validated human grades."""
from collections import defaultdict
import numpy as np

SEED = 3801
REPLICATES = 2000
COMPARISONS = [('B3', 'B1'), ('B3', 'B2'), ('B3', 'A1'), ('B3', 'A2')]


def contributions(row, grade):
    """Per-question numerator/denominator contributions for pooled metrics."""
    answerable = row['answerable']
    result = row['result']
    answered = result['status'] in ['answered', 'partial']
    edition = bool(row.get('requested_edition')) and row.get('edition_stratum') in ['available', 'missing']
    claims = result.get('claims', []) if answered else []
    cited = [i for i, claim in enumerate(claims) if claim.get('citations')]
    supported = sum(grade['claim_support'][i] for i in cited)
    unsupported = answered and any(not v for v in grade['claim_support'])
    return {
        'recall_at_5': ((row['metrics'].get('recall_at_5') or 0) if answerable else 0, int(answerable)),
        'mrr_at_5': ((row['metrics'].get('mrr_at_5') or 0) if answerable else 0, int(answerable)),
        'answer_correctness': (int(answerable and grade.get('correct') is True), int(answerable)),
        'citation_support': (supported, len(cited)),
        'citation_coverage': (len(cited), len(claims)),
        'wrong_edition_rate': (int(edition and grade.get('wrong_edition') is True), int(edition)),
        'refusal_recall': (int(not answerable and grade.get('justified_refusal') is True), int(not answerable)),
        'false_refusal': (int(answerable and grade.get('false_refusal') is True), int(answerable)),
        'unsupported_answer_incidence': (int(unsupported), 1),
        'unsupported_among_answers': (int(unsupported), int(answered)),
        'answer_coverage': (int(answered), 1),
        'completion_rate': (int(result['status'] in ['answered','partial','missing_edition','clarify_edition','clarify_context','insufficient_evidence']), 1),
    }


def _ratio_sum(values):
    totals = np.asarray(values, dtype=float).sum(axis=0)
    return {'numerator': float(totals[0]), 'denominator': int(totals[1]),
            'value': float(totals[0] / totals[1]) if totals[1] else None}


def paired_analysis(groups_rows, lookup):
    """Return category estimates and B3-minus-comparator absolute differences.

    Sample group IDs with replacement, keeping all within-group questions and
    the exact same sample on both sides. Zero-denominator replicates remain
    missing, never 0 or 100%. No significance claim is made from an interval.
    """
    labels = list(groups_rows)
    by_label = {label: {row['question_id']: row for row in rows} for label, rows in groups_rows.items()}
    ids = sorted(by_label[labels[0]])
    if any(set(by_label[label]) != set(ids) for label in labels):
        raise ValueError('成对分析要求五组使用完全相同的问题ID。')
    anchor = by_label[labels[0]]
    groups = defaultdict(list)
    for qid in ids:
        snapshot = anchor[qid].get('question_snapshot', {})
        group_id = snapshot.get('group_id') or anchor[qid].get('group_id')
        if not group_id:
            raise ValueError('成对bootstrap缺少冻结group_id。')
        groups[group_id].append(qid)
    values = {label: {qid: contributions(row, lookup[(f'{label}.jsonl', qid)])
                      for qid, row in rows.items()} for label, rows in by_label.items()}
    metric_names = list(values[labels[0]][ids[0]])
    categories = {}
    for label in labels:
        categories[label] = {}
        for category in sorted({row['category'] for row in by_label[label].values()}):
            subset = [qid for qid in ids if by_label[label][qid]['category'] == category]
            categories[label][category] = {'n': len(subset), 'metrics': {
                metric: _ratio_sum([values[label][qid][metric] for qid in subset])
                for metric in metric_names}}
    group_ids = sorted(groups)
    # Common resamples for all metrics/comparisons retain pairing and reproducibility.
    draws = np.random.default_rng(SEED).integers(0, len(group_ids), size=(REPLICATES, len(group_ids)))
    totals = {label: {metric: np.asarray([
        np.asarray([values[label][qid][metric] for qid in groups[group]], dtype=float).sum(axis=0)
        for group in group_ids]) for metric in metric_names} for label in labels}
    comparisons = {}
    for left, right in COMPARISONS:
        if left not in labels or right not in labels:
            continue
        metrics = {}
        for metric in metric_names:
            a = totals[left][metric]; b = totals[right][metric]
            point_a = a.sum(axis=0); point_b = b.sum(axis=0)
            estimate = (float(point_a[0]/point_a[1] - point_b[0]/point_b[1])
                        if point_a[1] and point_b[1] else None)
            sa = a[draws].sum(axis=1); sb = b[draws].sum(axis=1)
            valid = (sa[:, 1] > 0) & (sb[:, 1] > 0)
            differences = sa[valid, 0]/sa[valid, 1] - sb[valid, 0]/sb[valid, 1]
            metrics[metric] = {'absolute_difference': estimate,
                'ci_95': np.quantile(differences, [.025, .975]).tolist() if len(differences) else None,
                'valid_replicates': int(valid.sum()),
                'categories': {category: (
                    categories[left][category]['metrics'][metric]['value'] - categories[right][category]['metrics'][metric]['value']
                    if categories[left][category]['metrics'][metric]['value'] is not None
                    and categories[right][category]['metrics'][metric]['value'] is not None else None)
                    for category in categories[left]}}
        comparisons[f'{left}_minus_{right}'] = metrics
    return {'seed': SEED, 'replicates': REPLICATES, 'resampling_unit': 'group_id',
            'groups': len(group_ids), 'questions': len(ids), 'categories': categories,
            'paired_comparisons': comparisons,
            'interpretation': 'Absolute proportion differences, not relative percent changes. Small corpus-bound benchmark; intervals do not establish general applicability or guaranteed improvement.'}
