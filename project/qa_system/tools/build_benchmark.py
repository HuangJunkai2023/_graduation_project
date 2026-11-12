"""Build unreviewed source-bound candidates from a local annotation specification.

The specification and reference excerpts stay in ignored runtime storage. No
answer is approved by this script. It requires one inspected source anchor for
each answerable item and validates every extracted quote against an indexed
chunk before exporting a human-review queue.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib,json,re,sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
APP=ROOT/'project/qa_system'
compact=lambda value:re.sub(r'\s+','',value)

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def source_quote(record,needle):
    """Keep the exact source bytes, including extraction defects for review."""
    text=record['text'];chars=[(i,c) for i,c in enumerate(text) if not c.isspace()]
    normal=''.join(c for _,c in chars);start=normal.index(compact(needle))
    begin=chars[max(0,start-45)][0]
    end=chars[min(len(chars)-1,start+len(compact(needle))+170)][0]+1
    # Quotes remain contained within one indexed chunk. Human review can narrow
    # or replace them; do not silently fix OCR-like extraction errors.
    return text[begin:end].strip()

def build(db_path,spec_path,destination,public_dir):
    dest=Path(destination)
    # Candidate regeneration must never erase human decisions or audit trails.
    # Use a new destination for revisions, then explicitly migrate reviewed work.
    if dest.exists():
        previous=[json.loads(line) for line in dest.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
        if any(r.get('review_status') != 'unreviewed' or r.get('reviewer') or r.get('reviewed_at') for r in previous) or dest.with_suffix('.reviews.jsonl').exists():
            raise ValueError('Existing candidate file contains human review history; use a new destination.')
    db=sqlite3.connect(f'file:{Path(db_path).as_posix()}?mode=ro',uri=True)
    docs={row[0]:json.loads(row[1]) for row in db.execute('select id,payload from documents')}
    records=[json.loads(row[0]) for row in db.execute('select payload from chunks')]
    db.close()
    specs=json.loads(Path(spec_path).read_text(encoding='utf-8'))
    rows=[];counts=Counter();groups={};locations=defaultdict(set)
    for spec in specs:
        split,category=spec['split'],spec['category'];counts[split]+=1
        qid=f'{split}-{counts[split]:03}'
        row=dict(question_id=qid,split=split,category=category,group_id='',question=spec['question'],history=spec.get('history',[]),answerable=category!='unanswerable',reference_answer=spec.get('answer',''),required_facts=spec.get('facts',[spec['answer']] if spec.get('answer') else []),evidence_units=[],unanswerable_reason=spec.get('reason',''),review_status='unreviewed',requested_standard=spec.get('standard',''),requested_edition=spec.get('year',''),edition_stratum=spec.get('stratum','available' if category!='unanswerable' else 'not_applicable'),expected_action=spec.get('expected_action','answer' if category!='unanswerable' else 'refuse'))
        row['unanswerable_type']=spec.get('unanswerable_type','')
        if row['answerable']:
            candidates=[r for r in records if docs[r['document_id']]['standard']==spec['standard'] and docs[r['document_id']]['year']==spec['year'] and r['location']==spec['location'] and compact(spec['needle']) in compact(r['text'])]
            if not candidates:raise ValueError(f'{qid}: source anchor absent: {spec["standard"]} {spec["location"]} {spec["needle"]}')
            # Prefer the complete occurrence when chunks overlap.
            source=max(candidates,key=lambda r:len(r['text']))
            quote=source_quote(source,spec['needle'])
            assert compact(quote) in compact(source['text'])
            row['evidence_units']=[{'document_id':source['document_id'],'location':source['location'],'quote':quote}]
            row['group_id']=spec.get('group_id',source['document_id']+':'+source['location'])
            row['source_review_note']='Candidate only: compare extraction and reference answer with the original source; no manual verification has been recorded.'
            locations[split].add((source['document_id'],source['location']))
        else:
            row['group_id']=spec['group_id']
            if row['edition_stratum']=='missing':
                assert not any(d['standard']==row['requested_standard'] and d['year']==row['requested_edition'] for d in docs.values()),f'{qid}: requested missing edition actually exists'
        if row['group_id'] in groups and groups[row['group_id']]!=split:raise ValueError('Related source group crosses splits')
        groups[row['group_id']]=split
        rows.append(row)
    expected={('dev','clause'):6,('dev','term'):3,('dev','edition'):4,('dev','follow_up'):3,('dev','unanswerable'):4,('test','clause'):24,('test','term'):12,('test','edition'):16,('test','follow_up'):12,('test','unanswerable'):16}
    actual=Counter((r['split'],r['category']) for r in rows)
    if dict(actual)!=expected:raise ValueError(f'Quota mismatch: {dict(actual)}')
    subtypes=Counter((r['split'],r['unanswerable_type']) for r in rows if not r['answerable'])
    expected_subtypes={(split,subtype):(1 if split=='dev' else 4) for split in ['dev','test'] for subtype in ['missing_edition','out_of_corpus','unrelated','ambiguous']}
    if dict(subtypes)!=expected_subtypes:raise ValueError(f'Unanswerable quota mismatch: {dict(subtypes)}')
    if locations['dev']&locations['test']:raise ValueError('Source page/paragraph crosses splits')
    if len({r['question'] for r in rows})!=100:raise ValueError('Duplicate question text')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    pilot=[r['question_id'] for r in rows if r['split']=='dev'][:10]
    write_json(dest.with_name('pilot.json'),{'status':'awaiting_human_review','question_ids':pilot,'instructions':'Review these ten development items first. Do not run formal tests or infer approval from source matching.'})
    public=Path(public_dir)
    safe=[{k:r[k] for k in ['question_id','split','category','group_id','question','answerable','unanswerable_type','requested_standard','requested_edition','edition_stratum','expected_action','review_status']} for r in rows]
    write_json(public/'question_catalog.json',safe)
    summary={'status':'awaiting_human_review','total':len(rows),'approved':0,'dev':20,'test':80,'answerable':80,'unanswerable':20,'quotas':{f'{a}/{b}':v for (a,b),v in actual.items()},'source_documents':len({u['document_id'] for r in rows for u in r['evidence_units']}),'source_locations':{k:len(v) for k,v in locations.items()},'source_groups_cross_split':False,'candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'pilot_question_ids':pilot,'gold_status':'not_frozen_not_manually_verified','limitations':['Exact source-anchor matches check provenance, not semantic correctness.','Draft questions and answers require human review including extracted numbers, units and conditions.','Missing-edition labels are relative to this selected corpus; no invented edition is treated as a real standard.']}
    summary['unanswerable_quotas']={f'{split}/{subtype}':n for (split,subtype),n in sorted(subtypes.items())}
    write_json(public/'summary.json',summary)
    lines=['# 基准候选题人工核查入口','','状态：100道候选，全部未审核；不是正式gold或测试结果。','','先审核开发集前10题：'+', '.join(pilot)+'。','','完整问题、参考答案与标准摘录仅保存在本机 `runtime/research/benchmark/candidates.jsonl`，不随Git公开。启动独立核查页面后，对照原始PDF/DOCX确认每题的答案、数值、单位、条件、版本和证据；不合格题标为需要修改。','','候选配额：开发20题（16可答、4不可答），测试80题（64可答、16不可答）；同一来源页/段落不跨划分。此分组不能代替人工检查近义事实是否泄漏。','','机器仅验证来源摘录确实存在；没有将源文匹配或自动生成标为人工核验。100题审核及开发集校准完成前，禁止正式冻结与400次测试。','']
    (public/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--db',type=Path,default=APP/'runtime/research/kb.sqlite3');p.add_argument('--spec',type=Path,default=APP/'runtime/research/benchmark/authoring_spec.json');p.add_argument('--output',type=Path,default=APP/'runtime/research/benchmark/candidates.jsonl');p.add_argument('--public',type=Path,default=ROOT/'outputs/research/benchmark');a=p.parse_args();print(json.dumps(build(a.db,a.spec,a.output,a.public),ensure_ascii=False))
