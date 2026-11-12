"""One entry point for the proposal's gated research workflow."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

from .config import APP_ROOT, Settings
from .store import Store
from .study import load_questions, validate_questions, freeze_study

ROOT = APP_ROOT / 'runtime/research'


def selected_store(db, calibration=None, freeze=None):
    settings = Settings.load(db)
    if freeze:
        data = json.loads((Path(freeze) / 'manifest.json').read_text(encoding='utf-8'))
        settings = replace(settings, **data['config'])
    elif calibration:
        data = json.loads(Path(calibration).read_text(encoding='utf-8'))
        settings = replace(settings, **data['selected'])
    return Store(settings)


def readiness(store, dataset):
    rows = load_questions(dataset)
    with store.connect() as db:
        docs = db.execute('SELECT COUNT(*) FROM documents').fetchone()[0]
        chunks = db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]
        vectors = db.execute('SELECT COUNT(*) FROM vectors WHERE identity=?',
                             (store.settings.embedding_identity,)).fetchone()[0]
    approved = [q for q in rows if q.get('review_status') == 'approved']
    return {
        'documents': docs, 'chunks': chunks, 'vectors_current_model': vectors,
        'questions': len(rows), 'approved_questions': len(approved),
        'approved_development': sum(q.get('split') == 'dev' for q in approved),
        'approved_test': sum(q.get('split') == 'test' for q in approved),
        'structural_validation': validate_questions(rows, store, require_full=True),
        'freeze_validation': validate_questions(rows, store, require_full=True, require_approved=True),
        'note': 'Machine source matching is not human semantic verification. No formal run is started by status.'}


def main():
    parser = argparse.ArgumentParser(description='开题计划研究流程：核查→开发校准→冻结→五组测试→人工评分')
    parser.add_argument('--db', default=str(ROOT / 'kb.sqlite3'))
    parser.add_argument('--dataset', default=str(ROOT / 'benchmark/candidates.jsonl'))
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('status')
    embed = sub.add_parser('embed', help='调用已配置的Embedding服务；仅处理已允许在线处理的资料')
    embed.add_argument('--batch-size', type=int, default=16)
    prepare = sub.add_parser('prepare', help='20道开发题人工通过后，准备开发候选段落')
    prepare.add_argument('--output', required=True)
    select = sub.add_parser('select', help='候选段落人工通过后，按预先固定规则选阈值')
    select.add_argument('--prepared', required=True)
    select.add_argument('--output', required=True)
    freeze = sub.add_parser('freeze', help='全部题目通过后，新建不可覆盖的研究快照')
    freeze.add_argument('--calibration', required=True)
    freeze.add_argument('--output', required=True)
    run = sub.add_parser('run', help='冻结后执行或续跑400个首次测试槽位')
    run.add_argument('--freeze', required=True)
    run.add_argument('--budget', required=True)
    run.add_argument('--output', default=str(ROOT / 'results'))
    score = sub.add_parser('summarize', help='人工盲评完整后汇总实测结果')
    score.add_argument('--runs', default=str(ROOT / 'results'))
    score.add_argument('--grades', default=str(ROOT / 'scoring/grades.jsonl'))
    score.add_argument('--output', required=True)
    report = sub.add_parser('report', help='从完整人工评分汇总生成英文补充实验报告')
    report.add_argument('--results', required=True)
    report.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.action == 'report':
        from .reporting import render_report
        result = render_report(args.results, args.output)
    elif args.action == 'summarize':
        from .study_run import summarize_scored
        result = summarize_scored(args.runs, args.grades, args.output)
    else:
        store = selected_store(args.db, getattr(args, 'calibration', None), getattr(args, 'freeze', None))
        if args.action == 'status':
            result = readiness(store, args.dataset)
        elif args.action == 'embed':
            from .api import ModelClient
            result = store.embed_pending(ModelClient(store.settings), args.batch_size)
        elif args.action == 'prepare':
            from .calibration import prepare_calibration
            result = prepare_calibration(args.dataset, store, args.output)
        elif args.action == 'select':
            from .calibration import select_gate
            result = select_gate(args.prepared, args.dataset, store, args.output)
        elif args.action == 'freeze':
            result = freeze_study(args.dataset, store, args.calibration, args.output)
        elif args.action == 'run':
            from .study_run import run_frozen
            result = run_frozen(args.freeze, store, args.output, args.budget)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
