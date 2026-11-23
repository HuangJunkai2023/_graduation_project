"""Prepare and compare a masked recheck of frozen first-attempt answers."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random

from ocs_qa.config import Settings
from ocs_qa.store import Store
from ocs_qa.study import canonical_hash, load_questions
from ocs_qa.study_run import summarize_scored, verify_freeze

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / 'project/qa_system/runtime/research'
PRIVATE = RESEARCH / 'submission_recheck'
SEED = 3801
QUOTAS = {'clause': 4, 'term': 4, 'edition': 4, 'follow_up': 4, 'ambiguous': 2,
          'missing_edition': 2, 'out_of_corpus': 2, 'unrelated': 2}
FIELDS = ('correct', 'claim_support', 'wrong_edition', 'justified_refusal', 'false_refusal')


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def prepare():
    store = Store(Settings.load(RESEARCH / 'kb.sqlite3'))
    manifest, questions = verify_freeze(RESEARCH / 'freezes/closing-v1', store)
    original = read(RESEARCH / 'measured_results.json')
    identity = canonical_hash(manifest)
    if identity != original['freeze_sha256']:
        raise ValueError('Frozen manifest does not match the original result summary')
    rng = random.Random(SEED)
    tests = sorted((q for q in questions if q['split'] == 'test'), key=lambda q: q['question_id'])
    selected = []
    for stratum, count in QUOTAS.items():
        eligible = [q for q in tests if (q['category'] if q['answerable'] else q['unanswerable_type']) == stratum]
        selected.extend(rng.sample(eligible, count))
    runs = {}
    for label in ('B1', 'B3'):
        path = RESEARCH / f'results/{label}.jsonl'
        if file_hash(path) != original['run_files_sha256'][path.name]:
            raise ValueError(f'Run file changed: {path.name}')
        runs[label] = {row['question_id']: row for row in load_questions(path)}
    documents = {doc['id']: doc for doc in store.documents()}
    doc_ids = set()
    tasks, mapping = [], {}
    for question in sorted(selected, key=lambda q: q['question_id']):
        question_id = question['question_id']
        labels = ['B1', 'B3']
        rng.shuffle(labels)
        answers = []
        for letter, label in zip(('x', 'y'), labels):
            row = runs[label][question_id]
            if row['attempt_id'] != 1 or row['freeze_sha256'] != identity:
                raise ValueError('Review requires frozen first attempts')
            result = row['result']
            task_id = f'{question_id}-{letter}'
            mapping[task_id] = {'question_id': question_id, 'run_file': f'{label}.jsonl'}
            sources = [{key: source[key] for key in ('source', 'document_id', 'location', 'text')}
                       for source in result['sources']]
            doc_ids.update(source['document_id'] for source in sources)
            answers.append({'id': task_id, 'status': result['status'], 'answer': result['answer'],
                            'claims': result['claims'], 'sources': sources})
        doc_ids.update(unit['document_id'] for unit in question['evidence_units'])
        fields = ('question_id', 'question', 'history', 'answerable', 'reference_answer', 'required_facts',
                  'expected_action', 'edition_stratum', 'requested_edition', 'unanswerable_type', 'evidence_units')
        tasks.append({**{key: question.get(key) for key in fields}, 'answers': answers})
    for document_id in doc_ids:
        if file_hash(Path(documents[document_id]['path'])) != document_id:
            raise ValueError(f'Original source hash changed: {document_id}')
    PRIVATE.mkdir(parents=True, exist_ok=True)
    write(PRIVATE / 'masked_tasks.json', {'freeze_sha256': identity, 'seed': SEED, 'quotas': QUOTAS,
          'sources': {key: documents[key]['path'] for key in sorted(doc_ids)}, 'questions': tasks})
    write(PRIVATE / 'mapping.json', mapping)
    recomputed = summarize_scored(RESEARCH / 'results', RESEARCH / 'scoring/grades.jsonl', PRIVATE / 'recomputed.json')
    if recomputed != original:
        raise ValueError('Formal metric recomputation differed from the archived summary')
    print(f'Prepared {len(tasks)} questions and {len(mapping)} masked outputs. Archived statistics reproduced.')


def compare(decisions_path, output_path):
    bundle = read(PRIVATE / 'masked_tasks.json')
    mapping = read(PRIVATE / 'mapping.json')
    previous = {(slot['run_file'], slot['question_id']): grade
                for grade in load_questions(RESEARCH / 'scoring/grades.jsonl') for slot in grade['run_slots']}
    decisions = read(decisions_path)
    if set(decisions) != set(mapping) or len(decisions) != 48:
        raise ValueError('Exactly 48 distinct masked judgements are required')
    counts, changes = Counter(), []
    statuses = Counter()
    for question in bundle['questions']:
        for answer in question['answers']:
            task_id = answer['id']
            judgement = decisions[task_id]
            slot = mapping[task_id]
            statuses[answer['status']] += 1
            before = previous[(slot['run_file'], slot['question_id'])]
            expected = {'correct': question['answerable'],
                        'wrong_edition': question['edition_stratum'] in ('available', 'missing') and bool(question['requested_edition']),
                        'justified_refusal': not question['answerable'], 'false_refusal': question['answerable']}
            valid_flags = all(type(judgement[field]) is bool if applicable else judgement[field] is None
                              for field, applicable in expected.items())
            if (not judgement['reason'].strip() or len(judgement['claim_support']) != len(answer['claims'])
                    or any(type(value) is not bool for value in judgement['claim_support'])
                    or not valid_flags):
                raise ValueError(f'Incomplete judgement {task_id}')
            discordant = []
            for field in FIELDS:
                counts[field + '_compared'] += len(judgement[field]) if field == 'claim_support' else int(expected[field])
                differences = (sum(a != b for a, b in zip(before[field], judgement[field]))
                               if field == 'claim_support' else int(expected[field] and before[field] != judgement[field]))
                counts[field + '_different'] += differences
                if differences:
                    discordant.append(field)
            if discordant:
                changes.append({'question_id': slot['question_id'], 'run_file': slot['run_file'], 'fields': discordant})
    write(output_path, {'review_method': 'assistant_source_review', 'reviewer': 'Codex',
          'scope': 'Masked recheck by the same assistant family; original formal grades retained.',
          'freeze_sha256': bundle['freeze_sha256'], 'seed': SEED, 'strata': QUOTAS,
          'sampled_question_ids': [row['question_id'] for row in bundle['questions']], 'outputs': len(mapping),
          'statuses': dict(statuses), 'reviewed_at': max(row['reviewed_at'] for row in decisions.values()),
          'outputs_agreeing_on_all_applicable_fields': len(mapping) - len(changes),
          'field_counts': dict(counts), 'differences': changes, 'private_decisions_sha256': file_hash(decisions_path),
          'formal_metrics_recomputed_identically': True, 'api_requests': 0})
    print(f'{len(mapping) - len(changes)}/{len(mapping)} outputs agree on every applicable field.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest='action', required=True)
    subcommands.add_parser('prepare')
    comparison = subcommands.add_parser('compare')
    comparison.add_argument('decisions', type=Path)
    comparison.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else compare(args.decisions, args.output)
