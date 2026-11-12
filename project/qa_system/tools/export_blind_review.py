"""Export source-bound review tasks with configuration metadata withheld."""
import argparse
from pathlib import Path
from ocs_qa.study import blind_tasks, _atomic_jsonl


def export_tasks(run_dir, output_dir, parts):
    run_dir = Path(run_dir)
    tasks = blind_tasks([run_dir / f'{label}.jsonl' for label in ['B1', 'B2', 'B3', 'A1', 'A2']])
    exported = []
    for task in tasks:
        result = task['result']
        sources = []
        for source in result.get('sources', []):
            record = {key: source.get(key) for key in ['source', 'id', 'document_id', 'location', 'page', 'text']}
            document = source.get('document', {})
            record['document'] = {key: document.get(key) for key in ['id', 'name', 'path', 'standard', 'year']}
            sources.append(record)
        exported.append({'blind_id': task['blind_id'], 'question_id': task['question_id'],
                         'question_snapshot': task.get('question_snapshot'), 'answerable': task['answerable'],
                         'result': {'answer': result.get('answer'), 'status': result.get('status'),
                                    'claims': result.get('claims', []), 'sources': sources}})
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for i in range(parts):
        _atomic_jsonl(output_dir / f'part-{i + 1:02}.jsonl', exported[i::parts])
    _atomic_jsonl(output_dir / 'private-slot-map.jsonl', tasks)
    return {'blind_tasks': len(tasks), 'parts': parts, 'slots': sum(len(t['run_slots']) for t in tasks)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--parts', type=int, default=2)
    args = parser.parse_args()
    if args.parts < 1:
        parser.error('parts must be positive')
    print(export_tasks(args.runs, args.output, args.parts))
