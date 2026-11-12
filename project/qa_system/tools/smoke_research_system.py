"""Live interface smoke checks, explicitly separate from the formal benchmark."""
from datetime import datetime, timezone
import json
from ocs_qa.config import APP_ROOT, Settings
from ocs_qa.store import Store
from ocs_qa.api import ModelClient
from ocs_qa.pipeline import Pipeline


def main():
    store = Store(Settings.load(APP_ROOT / 'runtime/research/kb.sqlite3'))
    pipeline = Pipeline(store, ModelClient(store.settings))
    question = 'TB/T 2073-2020 对铸件的外观和表面质量有哪些要求？'
    checks = []
    raw = []
    for mode in ['bm25', 'dense', 'hybrid']:
        result = pipeline.answer(question, mode=mode, generate=(mode == 'hybrid'))
        raw.append(result)
        checks.append({'check': mode, 'status': result['status'],
                       'source_count': len(result['sources']), 'claims': len(result['claims']),
                       'all_requested_family_and_year': all(
                           s['document']['standard'] == 'TBT2073' and s['document']['year'] == '2020'
                           for s in result['sources']), 'timings': result['timings']})
    # An intentionally absent request year, not an assertion that this edition exists.
    missing = pipeline.answer('TB/T 2073-1900 的适用范围是什么？', mode='hybrid', generate=True)
    checks.append({'check': 'intentionally_absent_year', 'status': missing['status'],
                   'source_count': len(missing['sources'])})
    if any(c['status'] in ['api_error', 'invalid_response', 'invalid_citation'] for c in checks):
        raise RuntimeError('A live interface smoke check failed; inspect the private API ledger.')
    if missing['status'] != 'missing_edition':
        raise RuntimeError('The absent-year request was not stopped before generation.')
    private = APP_ROOT / 'runtime/research/smoke_results.json'
    private.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding='utf-8')
    receipt = {'checked_at': datetime.now(timezone.utc).isoformat(), 'checks': checks,
        'documents': len(store.documents()), 'chunks': len(store.records()),
        'formal_benchmark_runs': 0,
        'interpretation': 'Live request, vector dimensionality, version routing and citation-format checks only. No manual answer correctness judgement; no formal performance claim.'}
    output = APP_ROOT.parents[1] / 'outputs/research/system_readiness.json'
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
