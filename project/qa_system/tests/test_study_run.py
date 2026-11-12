"""Study orchestration tests use synthetic sources and never call paid services."""
import copy
import json
from dataclasses import replace

import pytest

from ocs_qa.study import blind_tasks, canonical_hash, freeze_study, load_questions
from ocs_qa.study_run import _budget_review, _exclusive_run, run_frozen, summarize_scored, verify_freeze
from test_study import study_store, full_rows, write_rows, calibration, Vectors


@pytest.fixture
def frozen(study_store, tmp_path):
    rows = full_rows(study_store)
    dataset = tmp_path/'questions.jsonl'
    write_rows(dataset, rows)
    config = tmp_path/'calibration.json'
    calibration(config, rows, study_store)
    study_store.embed_pending(Vectors())
    folder = tmp_path/'freeze'
    manifest = freeze_study(dataset, study_store, config, folder)
    return study_store, folder, manifest, rows


@pytest.fixture
def budget(tmp_path):
    path = tmp_path/'budget.json'
    path.write_text(json.dumps({
        'status':'approved', 'reviewed_by':'Fixture reviewer',
        'reviewed_at':'2026-11-12T00:00:00Z', 'pricing_sources':['https://fixture.example/pricing'],
        'spent_gbp':2., 'conservative_remaining_run_gbp':3., 'historical_cost_unknown':False,
    }), encoding='utf-8')
    return path


@pytest.mark.parametrize('change', ['dataset', 'calibration', 'prompt', 'code', 'config', 'corpus', 'vectors', 'vector_values'])
def test_freeze_tampering_rejected(frozen, monkeypatch, change):
    store, folder, _, _ = frozen
    if change == 'dataset':
        path = folder/'questions.jsonl'
        rows = load_questions(path); rows[0]['question'] = 'changed'
        write_rows(path, rows)
    elif change == 'calibration':
        (folder/'calibration.json').write_text('{}', encoding='utf-8')
    elif change == 'prompt':
        monkeypatch.setattr('ocs_qa.study_run.SYSTEM', 'changed')
    elif change == 'code':
        path = folder/'manifest.json'
        manifest = json.loads(path.read_text(encoding='utf-8'))
        manifest['code_sha256']['ocs_qa/pipeline.py'] = 'changed'
        path.write_text(json.dumps(manifest), encoding='utf-8')
    elif change == 'config':
        store.settings = replace(store.settings, top_k=3)
    elif change == 'corpus':
        with store.connect() as db:
            db.execute('DELETE FROM chunks WHERE id=(SELECT MIN(id) FROM chunks)')
    elif change == 'vector_values':
        with store.connect() as db: db.execute("UPDATE vectors SET payload='[0.0,1.0]'")
    else:
        with store.connect() as db: db.execute('DELETE FROM vectors')
    with pytest.raises(ValueError): verify_freeze(folder, store)


def test_unchanged_freeze_valid(frozen):
    store, folder, manifest, rows = frozen
    actual, actual_rows = verify_freeze(folder, store)
    assert actual == manifest
    assert actual_rows == rows


@pytest.mark.parametrize('updates', [
    {'status':'draft'}, {'reviewed_by':''}, {'historical_cost_unknown':True},
    {'spent_gbp':-1}, {'spent_gbp':float('nan')}, {'conservative_remaining_run_gbp':None},
    {'spent_gbp':49, 'conservative_remaining_run_gbp':2},
    {'spent_gbp':39, 'conservative_remaining_run_gbp':1},
    {'spent_gbp':39, 'conservative_remaining_run_gbp':1, 'threshold_40_reviewed':'false'},
])
def test_budget_fails_closed(budget, updates):
    row = json.loads(budget.read_text(encoding='utf-8')); row.update(updates)
    budget.write_text(json.dumps(row), encoding='utf-8')
    with pytest.raises(ValueError): _budget_review(budget)


def test_budget_40_review_required_but_valid_review_accepted(budget):
    row = json.loads(budget.read_text(encoding='utf-8'))
    row.update(spent_gbp=39, conservative_remaining_run_gbp=1, threshold_40_reviewed=True)
    budget.write_text(json.dumps(row), encoding='utf-8')
    assert _budget_review(budget)['spent_gbp'] == 39


class FakePipeline:
    calls = []
    fail_at = None

    def __init__(self, store, client): pass

    def answer(self, question, **configuration):
        index = len(self.calls)
        if self.fail_at == index:
            raise RuntimeError('Synthetic interruption')
        self.calls.append((question, configuration))
        return {'status':'api_error' if index == 0 else 'insufficient_evidence',
                'answer':'Synthetic output', 'sources':[], 'claims':[],
                'timings':{'total_ms':1.}}


def test_run_resumes_400_first_attempt_slots_without_repeating_failures(frozen, budget, tmp_path, monkeypatch):
    store, folder, _, _ = frozen
    FakePipeline.calls=[]; FakePipeline.fail_at=7
    monkeypatch.setattr('ocs_qa.study_run.Pipeline', FakePipeline)
    output=tmp_path/'results'
    with pytest.raises(RuntimeError, match='interruption'):
        run_frozen(folder, store, output, budget, client=object())
    first = (output/'B1.jsonl').read_bytes()
    assert len(load_questions(output/'B1.jsonl')) == 7
    FakePipeline.fail_at=None
    summary=run_frozen(folder, store, output, budget, client=object())
    assert summary['total_slots'] == 400
    assert summary['slots_by_configuration'] == dict.fromkeys(['B1','B2','B3','A1','A2'], 80)
    assert len(FakePipeline.calls) == 399
    assert (output/'B1.jsonl').read_bytes().startswith(first)
    assert load_questions(output/'B1.jsonl')[0]['result']['status'] == 'api_error'
    assert load_questions(output/'B1.jsonl')[7]['result']['status'] == 'interrupted_error'
    assert not (output/'inflight.json').exists()
    assert {r['attempt_id'] for r in load_questions(output/'B1.jsonl')} == {1}
    run_frozen(folder, store, output, budget, client=object())
    assert len(FakePipeline.calls) == 399
    assert (output/'private/blind_tasks.jsonl').exists()
    assert {p.name for p in output.glob('*.jsonl')} == {f'{x}.jsonl' for x in ['B1','B2','B3','A1','A2']}
    modes={(c['mode'],c['edition_filter'],c['evidence_check']) for _,c in FakePipeline.calls}
    assert modes == {('bm25',True,True),('dense',True,True),('hybrid',True,True),('hybrid',False,True),('hybrid',True,False)}
    assert all(c['generate'] is True and c['top_k'] == 5 for _,c in FakePipeline.calls)


def test_resume_checks_later_file_before_making_calls(frozen, budget, tmp_path, monkeypatch):
    store, folder, manifest, rows = frozen
    output=tmp_path/'results';output.mkdir()
    write_rows(output/'B2.jsonl',[{'question_id':'unknown', 'configuration':'B2', 'freeze_sha256':canonical_hash(manifest)}])
    FakePipeline.calls=[]; FakePipeline.fail_at=None
    monkeypatch.setattr('ocs_qa.study_run.Pipeline', FakePipeline)
    with pytest.raises(ValueError, match='未知'):
        run_frozen(folder, store, output, budget, client=object())
    assert FakePipeline.calls == []


def test_concurrent_run_directory_is_locked(tmp_path):
    with _exclusive_run(tmp_path):
        with pytest.raises(ValueError, match='运行进程'):
            with _exclusive_run(tmp_path): pass


@pytest.fixture
def scored(tmp_path):
    folder=tmp_path/'results';folder.mkdir()
    for label in ['B1','B2','B3','A1','A2']:
        rows=[]
        for i in range(80):
            answerable=i<64
            result={'status':'answered' if answerable else 'insufficient_evidence',
                    'answer':'Synthetic answer' if answerable else 'No evidence',
                    'sources':[{'source':1,'document_id':'fixture','location':'p1','text':'Synthetic fixture evidence'}] if answerable else [],
                    'claims':[{'text':'Synthetic fact','citations':[{'source':1,'quote':'Synthetic fixture evidence'}]}] if answerable else [],
                    'timings':{'total_ms':i+1,'retrieval_ms':i+1,'generation_ms':0.}}
            rows.append({'question_id':f'q{i:03}', 'answerable':answerable, 'category':'clause' if answerable else 'unanswerable',
                'question_snapshot':{'question_id':f'q{i:03}', 'question':'Synthetic question',
                                     'answerable':answerable, 'evidence_units':[], 'group_id':f'fixture-group-{i}'},
                'reference_answer':'Synthetic reference', 'required_facts':['Synthetic fact'] if answerable else [],
                'requested_standard':'Fixture', 'requested_edition':'2020',
                'edition_stratum':'available' if answerable else 'missing',
                'expected_action':'answer' if answerable else 'refuse','freeze_sha256':'fixture-freeze',
                'metrics':{'recall_at_5':1. if answerable else None,'mrr_at_5':.5 if answerable else None},
                'result':result})
        write_rows(folder/f'{label}.jsonl', rows)
    tasks=blind_tasks([folder/f'{label}.jsonl' for label in ['B1','B2','B3','A1','A2']])
    def grade(task):
        return {k:task[k] for k in ['blind_id','question_id','run_slots']} | {
            'reviewer':'Fixture reviewer','reviewed_at':'2026-11-12T00:00:00Z','reason':'Synthetic fixture evidence',
            'correct':True if task['answerable'] else None,
            'claim_support':[True] if task['answerable'] else [],'wrong_edition':False,
            'justified_refusal':None if task['answerable'] else True,
            'false_refusal':False if task['answerable'] else None,'failure_type':'none'}
    grades=[grade(t) for t in tasks]
    path=tmp_path/'grades.jsonl';write_rows(path,grades)
    return folder, path, grades


def test_scored_metrics_keep_predeclared_denominators(scored, tmp_path):
    folder,path,_=scored
    result=summarize_scored(folder,path,tmp_path/'summary.json')
    assert result['analysis']['seed'] == 3801
    assert result['analysis']['replicates'] == 2000
    for label,metrics in result['configurations'].items():
        assert metrics['recall_at_5'] == {'numerator':64.,'denominator':64,'value':1.}
        assert metrics['answer_correctness']['denominator'] == 64
        assert metrics['citation_support']['denominator'] == 64
        assert metrics['citation_coverage'] == {'numerator':64,'denominator':64,'value':1.}
        assert metrics['citation_resolvability'] == {'numerator':64,'denominator':64,'value':1.}
        assert metrics['wrong_edition_rate']['denominator'] == 80
        assert metrics['refusal_recall'] == {'numerator':16,'denominator':16,'value':1.}
        assert metrics['false_refusal']['denominator'] == 64
        assert metrics['answer_coverage']['denominator'] == 80
        assert metrics['total_latency']['observations'] == 80
        assert metrics['total_latency']['mean_ms'] == 40.5
        assert metrics['total_latency']['median_ms'] == 40.5
        assert metrics['total_latency']['p95_ms'] == 76
        assert metrics['retrieval_latency']['p95_ms'] == 76
        assert metrics['generation_latency']['median_ms'] == 0.


def test_missing_grade_rejected(scored, tmp_path):
    folder,path,grades=scored
    write_rows(path,grades[:-1])
    with pytest.raises(ValueError, match='覆盖全部400'):
        summarize_scored(folder,path,tmp_path/'summary.json')


def test_stale_answer_or_evidence_invalidates_old_grade(scored, tmp_path):
    folder,path,_=scored
    rows=load_questions(folder/'B1.jsonl');rows[0]['result']['answer']='Changed answer'
    write_rows(folder/'B1.jsonl',rows)
    with pytest.raises(ValueError, match='过期评分'):
        summarize_scored(folder,path,tmp_path/'summary.json')


@pytest.mark.parametrize('status,field', [('api_error','correct'),('api_error','false_refusal'),
                                       ('invalid_citation','correct'),('invalid_response','justified_refusal')])
def test_failure_states_cannot_be_scored_as_success(scored, tmp_path, status, field):
    folder,path,grades=scored
    target=0 if field!='justified_refusal' else 64
    for label in ['B1','B2','B3','A1','A2']:
        rows=load_questions(folder/f'{label}.jsonl')
        rows[target]['result']['status']=status
        write_rows(folder/f'{label}.jsonl',rows)
    tasks=blind_tasks([folder/f'{label}.jsonl' for label in ['B1','B2','B3','A1','A2']])
    byqid={t['question_id']:t for t in tasks}
    for g in grades:
        g['blind_id']=byqid[g['question_id']]['blind_id']
        if g['question_id']==f'q{target:03}':
            g['correct']=False if field!='correct' else True
            g[field]=True
    write_rows(path,grades)
    with pytest.raises(ValueError, match='不能标为'):
        summarize_scored(folder,path,tmp_path/'summary.json')


def test_groups_must_use_same_test_questions(scored, tmp_path):
    folder,path,grades=scored
    rows=load_questions(folder/'A2.jsonl');rows[0]['reference_answer']='Different gold answer'
    write_rows(folder/'A2.jsonl',rows)
    with pytest.raises(ValueError, match='题目或冻结版本不一致'):
        summarize_scored(folder,path,tmp_path/'summary.json')
