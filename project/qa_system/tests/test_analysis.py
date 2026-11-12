"""Synthetic arithmetic tests; no project benchmark labels or measured outcomes."""
from copy import deepcopy
from ocs_qa.analysis import paired_analysis


def fixture_rows():
    rows = []
    for i in range(4):
        rows.append({'question_id': str(i), 'group_id': str(i//2), 'category': 'clause',
            'answerable': True, 'requested_edition': '', 'edition_stratum': 'not_applicable',
            'metrics': {'recall_at_5': 1., 'mrr_at_5': 1.},
            'result': {'status': 'answered', 'claims': [{'citations': [{'source': 1}]}]}})
    groups = {label: deepcopy(rows) for label in ['B1', 'B2', 'B3', 'A1', 'A2']}
    lookup = {(f'{label}.jsonl', row['question_id']): {'correct': True, 'claim_support': [True],
              'wrong_edition': None, 'false_refusal': False, 'justified_refusal': None}
              for label, data in groups.items() for row in data}
    return groups, lookup


def test_identical_paired_groups_zero_interval_and_missing_denominator():
    groups, lookup = fixture_rows()
    result = paired_analysis(groups, lookup)
    assert result['groups'] == 2 and result['replicates'] == 2000
    metrics = result['paired_comparisons']['B3_minus_B1']
    assert metrics['answer_correctness']['absolute_difference'] == 0
    assert metrics['answer_correctness']['ci_95'] == [0., 0.]
    assert metrics['refusal_recall']['absolute_difference'] is None
    assert metrics['refusal_recall']['ci_95'] is None


def test_pooled_citation_ratio_and_absolute_difference_reproducible():
    groups, lookup = fixture_rows()
    for row in groups['B1']:
        lookup[('B1.jsonl', row['question_id'])]['correct'] = False
    groups['B3'][0]['result']['claims'].append({'citations': [{'source': 1}]})
    lookup[('B3.jsonl', '0')]['claim_support'] = [True, False]
    result = paired_analysis(groups, lookup)
    assert result == paired_analysis(groups, lookup)
    support = result['categories']['B3']['clause']['metrics']['citation_support']
    assert support['numerator'] == 4 and support['denominator'] == 5
    assert result['paired_comparisons']['B3_minus_B1']['answer_correctness']['ci_95'] == [1., 1.]
