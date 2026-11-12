"""Frozen first-attempt experiment execution, resumable per slot, and scored metrics."""
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import statistics
from .config import Settings,APP_ROOT
from .api import ModelClient
from .pipeline import Pipeline,SYSTEM,compact
from .evaluation import retrieval_metrics
from .study import (canonical_hash,corpus_fingerprint,vector_fingerprint,runtime_identity,load_questions,
                    validate_questions,blind_tasks,utc_now,_atomic_jsonl,review_methods,development_hash)

def verify_freeze(freeze_dir,store):
    freeze_dir=Path(freeze_dir)
    manifest=json.loads((freeze_dir/'manifest.json').read_text(encoding='utf-8'))
    rows=load_questions(freeze_dir/'questions.jsonl')
    if canonical_hash(rows)!=manifest['dataset_sha256']:raise ValueError('冻结题集已改变。')
    if corpus_fingerprint(store)!=manifest['corpus_sha256']:raise ValueError('冻结语料已改变。')
    if vector_fingerprint(store)!=manifest['vectors_sha256']:raise ValueError('冻结向量索引已改变。')
    if runtime_identity()!=manifest['runtime_identity']:raise ValueError('Python或依赖环境与冻结记录不一致。')
    if hashlib.sha256(SYSTEM.encode()).hexdigest()!=manifest['prompt_sha256']:raise ValueError('提示词已改变。')
    calibration=json.loads((freeze_dir/'calibration.json').read_text(encoding='utf-8'))
    if canonical_hash(calibration)!=manifest['calibration_sha256']:raise ValueError('冻结校准文件已改变。')
    for relative,digest in manifest['code_sha256'].items():
        path=APP_ROOT/relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError(f'冻结代码已改变：{relative}')
    for key,value in manifest['config'].items():
        if getattr(store.settings,key)!=value:raise ValueError(f'配置与冻结记录不一致：{key}')
    check=validate_questions(rows,store,require_full=True,require_approved=True)
    if not check['valid']:raise ValueError('冻结题目未通过审核/配额/原文校验。')
    if any(r['vector_identity']!=store.settings.embedding_identity for r in store.records()):raise ValueError('冻结语料向量不完整。')
    return manifest,rows

def _budget_review(path):
    row=json.loads(Path(path).read_text(encoding='utf-8'))
    if row.get('status')!='approved' or not row.get('reviewed_by') or not row.get('reviewed_at') or not row.get('pricing_sources'):
        raise ValueError('正式批次前需要核对实际费用及当前API价格。')
    historical_unknown = row.get('historical_cost_unknown', True)
    spent_key = 'historical_cost_reserve_gbp' if historical_unknown else 'spent_gbp'
    for key in [spent_key, 'conservative_remaining_run_gbp']:
        if type(row.get(key)) not in (int,float) or not math.isfinite(row[key]) or row[key]<0:raise ValueError('预算审计缺少有效金额。')
    if historical_unknown and (not row.get('reserve_basis') or not row.get('cost_evidence')):
        raise ValueError('历史费用未知时须记录预算预留依据及已取得的费用证据。')
    projected = row[spent_key] + row['conservative_remaining_run_gbp']
    if projected>50 or row[spent_key]>=50:raise ValueError('将超出Proposal的£50总预算。')
    if projected>=40 and row.get('threshold_40_reviewed') is not True:raise ValueError('达到£40复核阈值，须明确记录复核。')
    return row

@contextmanager
def _exclusive_run(output_dir):
    """The OS releases this byte lock after a crash; no stale PID guessing."""
    path=Path(output_dir)/'execution.lock'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as handle:
        if handle.tell()==0:handle.write(b'0');handle.flush()
        handle.seek(0)
        if os.name=='nt':
            import msvcrt
            try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
            except OSError as exc:raise ValueError('该实验目录已有运行进程，不能同时执行。') from exc
        else:
            import fcntl
            try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except OSError as exc:raise ValueError('该实验目录已有运行进程，不能同时执行。') from exc
        try:yield
        finally:
            handle.seek(0)
            if os.name=='nt':msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(handle,fcntl.LOCK_UN)

def _result_row(q,result,label,identity,attempt_id=1):
    raw=result.get('retrieved_sources',result['sources'])
    return {'question_id':q['question_id'],'split':q['split'],'category':q['category'],
            'answerable':q['answerable'],'reference_answer':q['reference_answer'],
            'required_facts':q['required_facts'],'requested_standard':q['requested_standard'],
            'requested_edition':q['requested_edition'],'edition_stratum':q['edition_stratum'],
            'expected_action':q['expected_action'],'question_snapshot':q,
            'configuration':label,'attempt_id':attempt_id,'freeze_sha256':identity,
            'created_at':utc_now(),'result':result,'metrics':retrieval_metrics(raw,q['evidence_units'])}

def _append_result(path,row):
    with Path(path).open('a',encoding='utf-8') as handle:
        handle.write(json.dumps(row,ensure_ascii=False)+'\n');handle.flush();os.fsync(handle.fileno())

def run_frozen(freeze_dir,store,output_dir,budget_path,client=None):
    with _exclusive_run(output_dir):
        return _run_frozen_locked(freeze_dir,store,output_dir,budget_path,client)

def _run_frozen_locked(freeze_dir,store,output_dir,budget_path,client=None):
    manifest,questions=verify_freeze(freeze_dir,store)
    return _execute_slots(manifest, [q for q in questions if q['split']=='test'], store,
                          output_dir, budget_path, client)


def _execute_slots(manifest, tests, store, output_dir, budget_path, client=None, attempt_id=1, eligible=None):
    budget=_budget_review(budget_path)
    byid={q['question_id']:q for q in tests}
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    identity=canonical_hash(manifest)
    context=output_dir/'run_context.json'
    if context.exists():
        if json.loads(context.read_text(encoding='utf-8'))['freeze_sha256']!=identity:raise ValueError('该运行目录属于另一冻结版本。')
    else:context.write_text(json.dumps({'freeze_sha256':identity,'created_at':utc_now(),'budget_review_sha256':canonical_hash(budget)},indent=2),encoding='utf-8')
    client=client or ModelClient(store.settings)
    paths=[]
    completed={}
    # Validate every resumed file before making another paid request.
    for label,configuration in manifest['configurations'].items():
        path=output_dir/f'{label}.jsonl';paths.append(path)
        existing=load_questions(path);counts=Counter(r.get('question_id') for r in existing)
        if any(n!=1 or qid not in byid for qid,n in counts.items()):raise ValueError('已有结果包含重复或未知槽位。')
        if any(r.get('freeze_sha256')!=identity or r.get('configuration')!=label or r.get('attempt_id')!=attempt_id for r in existing):raise ValueError('已有结果身份不符合冻结配置。')
        if eligible is not None and any(r['question_id'] not in eligible[label] for r in existing):
            raise ValueError('恢复结果包含非失败槽位。')
        if any(canonical_hash(r.get('question_snapshot'))!=canonical_hash(byid[r['question_id']]) for r in existing):raise ValueError('已有结果的题目快照与冻结题集不一致。')
        completed[label]=counts
    inflight=output_dir/'inflight.json'
    if inflight.exists():
        interrupted=json.loads(inflight.read_text(encoding='utf-8'))
        label=interrupted.get('configuration');qid=interrupted.get('question_id')
        if interrupted.get('freeze_sha256')!=identity or label not in completed or qid not in byid:raise ValueError('中断标记与冻结实验不一致，须人工核对。')
        if qid not in completed[label]:
            # A request may already have been charged. Preserve an unknown first
            # outcome as a failure instead of silently paying for a replacement.
            result={'status':'interrupted_error','answer':'首次运行中断，返回结果未能持久化；不自动重发。',
                    'sources':[],'claims':[],'usage':{},'timings':{},
                    'error_code':'interrupted_outcome_unknown','started_at':interrupted.get('started_at'),
                    'outcome_note':'Request completion, cost and retrieval outcome are unknown; retained as a first-attempt failure.'}
            _append_result(output_dir/f'{label}.jsonl',_result_row(byid[qid],result,label,identity,attempt_id))
            completed[label][qid]=1
        inflight.unlink()
    for label,configuration in manifest['configurations'].items():
        path=output_dir/f'{label}.jsonl'
        counts=completed[label]
        pipeline=Pipeline(store,client)
        for q in tests:
            if q['question_id'] in counts:continue
            if eligible is not None and q['question_id'] not in eligible[label]:
                continue
            with inflight.open('x',encoding='utf-8') as handle:
                json.dump({'configuration':label,'question_id':q['question_id'],
                           'freeze_sha256':identity,'started_at':utc_now()},handle)
                handle.flush();os.fsync(handle.fileno())
            result=pipeline.answer(q['question'],history=q.get('history',[]),generate=True,top_k=5,**configuration)
            # Never replace a paid/failed first attempt with a preferred retry.
            _append_result(path,_result_row(q,result,label,identity,attempt_id))
            inflight.unlink()
    tasks=blind_tasks(paths)
    _atomic_jsonl(output_dir/'private'/'blind_tasks.jsonl',tasks)
    counts={p.stem:len(load_questions(p)) for p in paths}
    summary={'status':'awaiting_source_grades','slots_by_configuration':counts,
             'total_slots':sum(counts.values()),'blind_tasks':len(tasks),'freeze_sha256':identity,
             'primary_attempt':attempt_id,'split':tests[0]['split'],
             'paid_calls_note':'Run slots include early refusals and are not equal to generation requests.'}
    (output_dir/'execution_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary


def run_development(dataset_path, store, output_dir, budget_path, client=None):
    """Run one complete development-only five-configuration integration pass."""
    from .calibration import _development
    rows = load_questions(dataset_path)
    development = _development(rows, store)
    configurations = {
        'B1': {'mode': 'bm25', 'edition_filter': True, 'evidence_check': True},
        'B2': {'mode': 'dense', 'edition_filter': True, 'evidence_check': True},
        'B3': {'mode': 'hybrid', 'edition_filter': True, 'evidence_check': True},
        'A1': {'mode': 'hybrid', 'edition_filter': False, 'evidence_check': True},
        'A2': {'mode': 'hybrid', 'edition_filter': True, 'evidence_check': False},
    }
    settings = store.settings
    manifest = {
        'schema': 'ocs-development-run.v1',
        'development_dataset_sha256': development_hash(rows),
        'corpus_sha256': corpus_fingerprint(store),
        'vectors_sha256': vector_fingerprint(store),
        'prompt_sha256': hashlib.sha256(SYSTEM.encode()).hexdigest(),
        'config': {key: getattr(settings, key) for key in [
            'chat_url', 'chat_model', 'embedding_url', 'embedding_model',
            'top_k', 'vector_weight', 'min_coverage', 'min_cosine']},
        'runtime_identity': runtime_identity(),
        'code_sha256': {str(path.relative_to(APP_ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in sorted((APP_ROOT / 'ocs_qa').rglob('*.py'))},
        'configurations': configurations,
    }
    with _exclusive_run(output_dir):
        manifest_path = Path(output_dir) / 'development_manifest.json'
        if manifest_path.exists():
            previous = json.loads(manifest_path.read_text(encoding='utf-8'))
            if canonical_hash(previous) != canonical_hash(manifest):
                raise ValueError('开发运行的代码、题目或配置已改变，请使用新的运行目录。')
        else:
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        summary = _execute_slots(manifest, development, store, output_dir, budget_path, client)
        summary['status'] = 'development_complete'
        summary['formal_test_slots'] = 0
        (Path(output_dir) / 'execution_summary.json').write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary


def run_recovery(freeze_dir, store, primary_dir, budget_path, attempt_id=2, client=None):
    """Recover only failed primary slots into a separate attempt directory."""
    if type(attempt_id) is not int or attempt_id < 2:
        raise ValueError('恢复运行的attempt_id必须至少为2。')
    manifest, questions = verify_freeze(freeze_dir, store)
    identity = canonical_hash(manifest)
    tests = [q for q in questions if q['split'] == 'test']
    failures = {'api_error', 'invalid_response', 'invalid_citation', 'interrupted_error'}
    eligible = {}
    primary_dir = Path(primary_dir)
    for label in manifest['configurations']:
        rows = load_questions(primary_dir / f'{label}.jsonl')
        if len(rows) != 80 or len({row['question_id'] for row in rows}) != 80:
            raise ValueError('恢复前必须保留完整的80题首次结果。')
        if any(row.get('freeze_sha256') != identity or row.get('attempt_id') != 1 for row in rows):
            raise ValueError('恢复来源与冻结版本或首次尝试身份不一致。')
        eligible[label] = {row['question_id'] for row in rows if row['result']['status'] in failures}
    output = primary_dir / 'recovery' / f'attempt-{attempt_id:02d}'
    with _exclusive_run(output):
        return _execute_slots(manifest, tests, store, output, budget_path, client,
                              attempt_id=attempt_id, eligible=eligible)

def _ratio(numerator,denominator):
    return {'numerator':numerator,'denominator':denominator,'value':numerator/denominator if denominator else None}

def _latency(rows,key='total_ms'):
    values=[r['result'].get('timings',{}).get(key) for r in rows]
    values=sorted(v for v in values if type(v) in (int,float) and math.isfinite(v) and v>=0)
    return {'observations':len(values),'mean_ms':statistics.mean(values) if values else None,
            'median_ms':statistics.median(values) if values else None,
            'p95_ms':values[math.ceil(.95*len(values))-1] if values else None,
            'p95_method':'nearest_rank','includes_early_refusals_and_errors':True}

def _citation_counts(rows):
    claims=cited=references=resolved=0
    for row in rows:
        result=row['result']
        if result['status'] not in ['answered','partial']:continue
        sources={s.get('source'):s for s in result.get('sources',[])}
        for claim in result.get('claims',[]):
            claims+=1
            citations=claim.get('citations',[])
            if citations:cited+=1
            for cite in citations:
                references+=1
                source=sources.get(cite.get('source')) if isinstance(cite,dict) and type(cite.get('source')) is int else None
                quote=cite.get('quote') if isinstance(cite,dict) else None
                if (source and source.get('document_id') and source.get('location')
                        and isinstance(quote,str) and len(compact(quote))>=8
                        and compact(quote) in compact(source.get('text',''))):resolved+=1
    return claims,cited,references,resolved

def summarize_scored(run_dir,grade_path,output_path):
    run_dir=Path(run_dir);grades=load_questions(grade_path);lookup={}
    labels=['B1','B2','B3','A1','A2']
    tasks={t['blind_id']:t for t in blind_tasks([run_dir/f'{label}.jsonl' for label in labels])}
    for grade in grades:
        if not grade.get('reviewer') or not grade.get('reviewed_at') or not grade.get('reason'):raise ValueError('人工评分缺少审核身份、时间或依据。')
        task=tasks.get(grade.get('blind_id'))
        slots=lambda rows:{(s['run_file'],s['question_id']) for s in rows}
        if (task is None or grade.get('question_id')!=task['question_id']
                or slots(grade['run_slots'])!=slots(task['run_slots'])
                or len(grade['run_slots'])!=len(task['run_slots'])):
            raise ValueError('人工评分与当前答案/证据盲任务不一致，不能复用过期评分。')
        for slot in grade['run_slots']:
            key=(slot['run_file'],slot['question_id'])
            if key in lookup:raise ValueError('人工评分槽位重复。')
            lookup[key]=grade
    groups={};loaded_rows_by_label={}
    expected_questions=None
    for label in labels:
        rows=load_questions(run_dir/f'{label}.jsonl')
        loaded_rows_by_label[label]=rows
        if len(rows)!=80 or len({r['question_id'] for r in rows})!=80:raise ValueError(f'{label}主要槽位不是80个。')
        if sum(r['answerable'] for r in rows)!=64:raise ValueError('主要测试题须64可回答、16不可回答。')
        if any(not isinstance(r.get('question_snapshot'),dict) or r['question_snapshot'].get('question_id')!=r['question_id'] for r in rows):raise ValueError('正式结果缺少匹配题号的冻结题目快照。')
        question_identity={r['question_id']:canonical_hash({k:r.get(k) for k in ['question_snapshot','split','category','answerable','reference_answer','required_facts','requested_standard','requested_edition','edition_stratum','expected_action','freeze_sha256']}) for r in rows}
        if expected_questions is None:expected_questions=question_identity
        elif question_identity!=expected_questions:raise ValueError('五组测试的题目或冻结版本不一致。')
        for r in rows:
            if (f'{label}.jsonl',r['question_id']) not in lookup:raise ValueError('人工评分尚未覆盖全部400槽位。')
        answerable=[r for r in rows if r['answerable']];unanswerable=[r for r in rows if not r['answerable']]
        grade=lambda r:lookup[(f'{label}.jsonl',r['question_id'])]
        for r in rows:
            g=grade(r);claims=r['result'].get('claims',[])
            if len(g['claim_support'])!=len(claims) or any(type(x) is not bool for x in g['claim_support']):raise ValueError('claim评分与实际已展示claims不一致。')
            if r['answerable'] and any(type(g.get(k)) is not bool for k in ['correct','false_refusal']):raise ValueError('可回答题评分不完整。')
            if not r['answerable'] and type(g.get('justified_refusal')) is not bool:raise ValueError('不可回答题评分不完整。')
            status=r['result']['status']
            if g.get('correct') and status not in ['answered','partial']:
                raise ValueError('未展示有效作答的槽位不能标为正确。')
            if g.get('correct') and g.get('wrong_edition'):
                raise ValueError('错误版本的答案不能标为完整正确。')
            if (g.get('justified_refusal') or g.get('false_refusal')) and status not in ['missing_edition','clarify_edition','clarify_context','insufficient_evidence']:
                raise ValueError('非拒答状态（含接口/格式/引用错误）不能标为合理拒答或误拒答。')
        edition=[r for r in rows if r['edition_stratum'] in ['available','missing'] and r['requested_edition']]
        if any(type(grade(r).get('wrong_edition')) is not bool for r in edition):raise ValueError('指定版本题缺少版本评分。')
        support=[supported for r in rows if r['result']['status'] in ['answered','partial'] for claim,supported in zip(r['result'].get('claims',[]),grade(r)['claim_support']) if claim.get('citations')]
        claim_count,cited_count,citation_count,resolved_count=_citation_counts(rows)
        answered=[r for r in rows if r['result']['status'] in ['answered','partial']]
        unsupported=sum(any(not v for v in grade(r)['claim_support']) for r in answered)
        groups[label]={
            'recall_at_5':_ratio(sum(r['metrics']['recall_at_5'] or 0 for r in answerable),64),
            'mrr_at_5':_ratio(sum(r['metrics']['mrr_at_5'] or 0 for r in answerable),64),
            'answer_correctness':_ratio(sum(grade(r)['correct'] for r in answerable),64),
            'citation_support':_ratio(sum(support),len(support)),
            'citation_coverage':_ratio(cited_count,claim_count),
            'citation_resolvability':_ratio(resolved_count,citation_count),
            'wrong_edition_rate':_ratio(sum(grade(r)['wrong_edition'] for r in edition),len(edition)),
            'refusal_recall':_ratio(sum(grade(r)['justified_refusal'] for r in unanswerable),16),
            'false_refusal':_ratio(sum(grade(r)['false_refusal'] for r in answerable),64),
            'unsupported_answer_incidence':_ratio(unsupported,80),
            'unsupported_among_answers':_ratio(unsupported,len(answered)),
            'api_errors':sum(r['result']['status']=='api_error' for r in rows),
            'interrupted_unknown_outcomes':sum(r['result']['status']=='interrupted_error' for r in rows),
            'total_latency':_latency(rows),
            'retrieval_latency':_latency(rows,'retrieval_ms'),
            'generation_latency':_latency(rows,'generation_ms'),
            'answer_coverage':_ratio(sum(r['result']['status'] in ['answered','partial'] for r in rows),80),
            'completion_rate':_ratio(sum(r['result']['status'] in ['answered','partial','missing_edition','clarify_edition','clarify_context','insufficient_evidence'] for r in rows),80),
            'failure_types':dict(Counter(grade(r)['failure_type'] for r in rows)),
            'edition_availability':{state:{'items':sum(r['edition_stratum']==state for r in rows),
                'answered':sum(r['edition_stratum']==state and r['result']['status'] in ['answered','partial'] for r in rows)} for state in ['available','missing','ambiguous','not_applicable']}}
    methods = review_methods(grades)
    source_reviewed = 'assistant_source_review' in methods
    result={'status':'source_reviewed' if source_reviewed else 'human_scored',
            'review_methods':methods,'configurations':groups,'grades_sha256':canonical_hash(grades),
            'freeze_sha256':loaded_rows_by_label['B1'][0]['freeze_sha256'],
            'run_files_sha256':{f'{label}.jsonl':hashlib.sha256((run_dir/f'{label}.jsonl').read_bytes()).hexdigest() for label in labels},
            'citation_counting_note':'Coverage and resolvability use displayed structured claims and retrieved sources. Semantic support and atomic-fact adequacy use the recorded source-review method.',
            'note':'Measured observations; planned thresholds do not determine whether results are reported.'}
    from .analysis import paired_analysis
    result['analysis']=paired_analysis(loaded_rows_by_label,lookup)
    Path(output_path).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

def main():
    parser=argparse.ArgumentParser(description='冻结后的五组主要实验与人工评分汇总')
    sub=parser.add_subparsers(dest='action',required=True)
    run=sub.add_parser('run');run.add_argument('--freeze',required=True);run.add_argument('--db',required=True);run.add_argument('--output',required=True);run.add_argument('--budget',required=True)
    score=sub.add_parser('summarize');score.add_argument('--runs',required=True);score.add_argument('--grades',required=True);score.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.action=='run':
        from .store import Store
        manifest=json.loads((Path(args.freeze)/'manifest.json').read_text(encoding='utf-8'))
        store=Store(replace(Settings.load(args.db),**manifest['config']))
        result=run_frozen(args.freeze,store,args.output,args.budget)
    else:result=summarize_scored(args.runs,args.grades,args.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
