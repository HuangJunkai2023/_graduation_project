"""Development-only retrieval selection and human-reviewed passage calibration."""
from collections import Counter
from dataclasses import replace
from pathlib import Path
from tempfile import NamedTemporaryFile
import os
import shutil
import argparse
import json
import math
from .api import ModelClient
from .config import Settings, APP_ROOT
from .evaluation import retrieval_metrics
from .pipeline import resolve_query
from .retrieval import Retriever
from .study import (QUOTAS,canonical_hash,development_hash,load_questions,
                    validate_questions,utc_now,_atomic_jsonl,corpus_fingerprint,vector_fingerprint,review_methods)

WEIGHTS=(.25,.50,.75)
LEXICAL=(.05,.10,.20)
COSINE=(.20,.30,.40,.50)

class CachedEmbeddingClient:
    """Content-addressed query cache; model identity is part of every key."""
    def __init__(self,client,cache_dir):
        self.client=client;self.cache_dir=Path(cache_dir)
        self.cache_dir.mkdir(parents=True,exist_ok=True)
    def embed(self,texts):
        results=[]
        for text in texts:
            key=canonical_hash([self.client.settings.embedding_identity,text])
            path=self.cache_dir/f'{key}.json'
            if path.exists():vector=json.loads(path.read_text(encoding='utf-8'))
            else:
                vector=self.client.embed([text])[0]
                path.write_text(json.dumps(vector),encoding='utf-8')
            if not vector or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in vector) or not sum(v*v for v in vector):
                raise ValueError('查询向量缓存无效，请核对缓存文件。')
            results.append(vector)
        return results

def _development(rows,store):
    dev=[q for q in rows if q.get('split')=='dev']
    errors=validate_questions(dev,store,require_approved=True)['errors']
    if Counter(q['category'] for q in dev)!=Counter(QUOTAS['dev']):errors.append('开发集须符合20题固定配额。')
    if sum(q.get('answerable') is True for q in dev)!=16:errors.append('开发集须含16可回答、4不可回答题。')
    if errors:raise ValueError('\n'.join(errors))
    return dev

def prepare_calibration(dataset_path,store,output_dir,client=None):
    rows=load_questions(dataset_path);dev=_development(rows,store)
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    client=CachedEmbeddingClient(client or ModelClient(store.settings),store.settings.db_path.parent/'query_vectors')
    trials=[];cache={}
    # Every weight uses exactly the same reviewed 16 answerable development items.
    for weight in WEIGHTS:
        tuned=type(store)(replace(store.settings,vector_weight=weight))
        retriever=Retriever(tuned,client);metrics=[]
        for q in dev:
            query,error=resolve_query(q['question'],q.get('history',[]))
            result={'sources':[]} if error else retriever.search(query,mode='hybrid')
            cache[(weight,q['question_id'])]=result
            if q['answerable']:metrics.append(retrieval_metrics(result['sources'],q['evidence_units']))
        trials.append({'weight':weight,'recall_at_5':sum(m['recall_at_5'] for m in metrics)/16,
                       'mrr_at_5':sum(m['mrr_at_5'] for m in metrics)/16})
    order={.5:0,.25:1,.75:2}
    chosen=min(trials,key=lambda t:(-t['recall_at_5'],-t['mrr_at_5'],order[t['weight']]))
    labels={}
    tuned=type(store)(replace(store.settings,vector_weight=chosen['weight']))
    retriever=Retriever(tuned,client)
    for q in dev:
        query,error=resolve_query(q['question'],q.get('history',[]))
        for mode in ['bm25','dense','hybrid']:
            result=cache[(chosen['weight'],q['question_id'])] if mode=='hybrid' else ({'sources':[]} if error else retriever.search(query,mode=mode))
            for source in result['sources']:
                key=canonical_hash([q['question_id'],source['id']])
                if key not in labels:
                    labels[key]={'label_id':key,'question_id':q['question_id'],'question':q['question'],
                        'source':source,'modes':[],
                        'proposed_relevant':retrieval_metrics([source],q['evidence_units'])['recall_at_5'] not in (None,0),
                        'relevant':None,'review_status':'unreviewed'}
                if source.get('vector_score') is not None:
                    labels[key]['source']['vector_score']=source['vector_score']
                labels[key]['modes'].append(mode)
    label_path=output_dir/'passage_labels.jsonl'
    if label_path.exists():raise ValueError('候选证据标签已存在；请保留已审核记录，使用新的准备目录。')
    _atomic_jsonl(label_path,list(labels.values()))
    prepared={'status':'pending_passage_review','created_at':utc_now(),
        'development_dataset_sha256':development_hash(rows),'corpus_sha256':corpus_fingerprint(store),
        'vectors_sha256':vector_fingerprint(store),
        'weight_trials':trials,'selected_weight':chosen['weight'],
        'label_population_sha256':canonical_hash([{k:r[k] for k in ['label_id','question_id','source','modes']} for r in labels.values()]),
        'passage_label_count':len(labels),'candidate_labels':str(label_path.resolve())}
    (output_dir/'selection_prepared.json').write_text(json.dumps(prepared,ensure_ascii=False,indent=2),encoding='utf-8')
    return prepared

def passage_review_material(prepared_path,rows,store):
    """Resolve the exact prepared version and reject stale source/gold material."""
    prepared_path=Path(prepared_path);prepared=json.loads(prepared_path.read_text(encoding='utf-8'))
    if prepared['development_dataset_sha256']!=development_hash(rows) or prepared['corpus_sha256']!=corpus_fingerprint(store):
        raise ValueError('开发题或语料已变更，不能沿用旧候选标签。')
    if prepared['vectors_sha256']!=vector_fingerprint(store):
        raise ValueError('向量索引已变更，需重新准备开发校准。')
    path=Path(prepared['candidate_labels'])
    if not path.is_absolute():path=prepared_path.parent/path
    labels=load_questions(path)
    population=canonical_hash([{k:r[k] for k in ['label_id','question_id','source','modes']} for r in labels])
    if population!=prepared['label_population_sha256']:raise ValueError('候选证据集合已变更。')
    return prepared,path,labels


def select_gate(prepared_path,dataset_path,store,output_path):
    rows=load_questions(dataset_path);_development(rows,store)
    prepared,_,labels=passage_review_material(prepared_path,rows,store)
    if not labels or any(r.get('review_status')!='approved' or type(r.get('relevant')) is not bool or not r.get('reviewer') or not r.get('reviewed_at') for r in labels):
        raise ValueError('请先完成人工候选证据审核，不能将自动提议作为人工标签。')
    trials=[]
    for lexical in LEXICAL:
        for cosine in COSINE:
            scores=[];false_negative=0;precisions=[];false_refusals=0
            for mode in ['bm25','dense','hybrid']:
                tp=fp=fn=0
                accepted_questions=set()
                for row in labels:
                    if mode not in row['modes']:continue
                    source=row['source'];sim=source.get('vector_score')
                    accept=source['lexical_coverage']>=lexical or (mode!='bm25' and sim is not None and sim>=cosine)
                    if accept:accepted_questions.add(row['question_id'])
                    relevant=row['relevant']
                    tp+=int(accept and relevant);fp+=int(accept and not relevant);fn+=int(not accept and relevant)
                precision=tp/(tp+fp) if tp+fp else 0.
                f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.
                scores.append(f1);precisions.append(precision);false_negative+=fn
                false_refusals+=sum(q['answerable'] and q['question_id'] not in accepted_questions for q in rows if q['split']=='dev')
            trials.append({'min_coverage':lexical,'min_cosine':cosine,'mean_passage_f1':sum(scores)/3,
                           'false_negatives':false_negative,'false_refusals':false_refusals,'mean_precision':sum(precisions)/3})
    chosen=min(enumerate(trials),key=lambda it:(-it[1]['mean_passage_f1'],it[1]['false_refusals'],-it[1]['mean_precision'],it[0]))[1]
    evidence=Path(output_path).with_suffix('.selection.json')
    evidence.write_text(json.dumps({'weight_trials':prepared['weight_trials'],'gate_trials':trials,
        'reviewed_labels_sha256':canonical_hash(labels),'development_only':True},ensure_ascii=False,indent=2),encoding='utf-8')
    output={'status':'validated','validated_by':'development-calibration-runner','validated_at':utc_now(),
        'review_methods':review_methods(labels),
        'development_dataset_sha256':development_hash(rows),'corpus_sha256':corpus_fingerprint(store),
        'vectors_sha256':vector_fingerprint(store),
        'selected':{'vector_weight':prepared['selected_weight'],'min_coverage':chosen['min_coverage'],'min_cosine':chosen['min_cosine']},
        'selection_evidence':str(evidence.resolve())}
    Path(output_path).write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    return output

def activate_calibration(calibration_path, dataset_path, store):
    """Apply the verified selected parameters to subsequent local UI sessions."""
    selected = json.loads(Path(calibration_path).read_text(encoding='utf-8'))
    rows = load_questions(dataset_path)
    _development(rows, store)
    expected = {
        'development_dataset_sha256': development_hash(rows),
        'corpus_sha256': corpus_fingerprint(store),
        'vectors_sha256': vector_fingerprint(store),
    }
    if selected.get('status') != 'validated' or any(selected.get(key) != value for key, value in expected.items()):
        raise ValueError('校准记录与当前开发题、语料或向量不一致。')
    parameters = selected.get('selected', {})
    if (parameters.get('vector_weight') not in WEIGHTS or parameters.get('min_coverage') not in LEXICAL
            or parameters.get('min_cosine') not in COSINE):
        raise ValueError('校准参数不在预定网格中。')
    updates = {
        'OCS_DB_PATH': store.settings.db_path.resolve().as_posix(),
        'VECTOR_WEIGHT': str(parameters['vector_weight']),
        'MIN_LEXICAL_COVERAGE': str(parameters['min_coverage']),
        'MIN_COSINE_SIMILARITY': str(parameters['min_cosine']),
        'TOP_K': '5',
    }
    path = APP_ROOT / '.env'
    text = path.read_text(encoding='utf-8-sig') if path.exists() else ''
    backup = APP_ROOT / 'runtime/config-backups' / ('env.before-calibration-' + utc_now().replace(':', '-') + '.txt')
    backup.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, backup)
    lines = [line for line in text.splitlines() if line.partition('=')[0].strip() not in updates]
    lines.extend(f'{key}={value}' for key, value in updates.items())
    with NamedTemporaryFile('w', encoding='utf-8', dir=APP_ROOT, delete=False) as handle:
        handle.write('\n'.join(lines) + '\n')
        temporary = Path(handle.name)
    os.replace(temporary, path)
    return {'status': 'activated', 'parameters': parameters,
            'note': 'Refresh the question-answering page to load the selected settings.'}


def main():
    parser=argparse.ArgumentParser(description='仅开发集调参与证据核验准备')
    parser.add_argument('action',choices=['prepare','select'])
    parser.add_argument('--db',required=True);parser.add_argument('--dataset',required=True)
    parser.add_argument('--output',required=True);parser.add_argument('--prepared')
    args=parser.parse_args()
    from .store import Store
    store=Store(Settings.load(args.db))
    if args.action=='prepare':result=prepare_calibration(args.dataset,store,args.output)
    else:
        if not args.prepared:parser.error('select需要--prepared')
        result=select_gate(args.prepared,args.dataset,store,args.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
