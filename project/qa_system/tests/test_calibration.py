from dataclasses import replace
from pathlib import Path
import json
import pytest
from docx import Document
from ocs_qa.config import Settings
from ocs_qa.store import Store
from ocs_qa.study import QUOTAS,load_questions,save_passage_label,utc_now
from ocs_qa.calibration import prepare_calibration,select_gate,CachedEmbeddingClient

class FakeEmbedding:
    def __init__(self,settings):self.settings=settings;self.calls=0
    def embed(self,texts):self.calls+=1;return [[1.,.1] for text in texts]

@pytest.fixture
def development(tmp_path):
    settings=Settings(db_path=tmp_path/'kb.sqlite3',embedding_url='https://example.test/v1',embedding_model='fixture')
    store=Store(settings)
    doc=Document();doc.add_paragraph('这是合成试验资料，接触网零部件表面应清洁。不是真实标准。')
    source=tmp_path/'TBT2073-2020.docx';doc.save(source);store.ingest(source,allow_cloud=True)
    client=FakeEmbedding(settings);store.embed_pending(client)
    record=store.records()[0];rows=[]
    for category,count in QUOTAS['dev'].items():
        for j in range(count):
            yes=category!='unanswerable';qid=f'dev-{len(rows)+1:03}'
            rows.append({'question_id':qid,'split':'dev','category':category,'group_id':qid,
                'question':'接触网零部件表面有什么要求？' if yes else '为什么今天下雨？',
                'history':[],'answerable':yes,'reference_answer':'表面应清洁' if yes else '',
                'required_facts':['表面应清洁'] if yes else [],'evidence_units':[{'document_id':record['document_id'],'location':record['location'],'quote':'接触网零部件表面应清洁'}] if yes else [],
                'unanswerable_reason':'' if yes else '合成库未含天气资料','review_status':'approved','reviewer':'fixture-human','reviewed_at':utc_now(),
                'unanswerable_type':'' if yes else ('missing_edition','out_of_corpus','unrelated','ambiguous')[j%4],
                'requested_standard':'','requested_edition':'','edition_stratum':'not_applicable','expected_action':'answer' if yes else 'refuse'})
    dataset=tmp_path/'questions.jsonl';dataset.write_text(''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in rows),encoding='utf-8')
    return store,client,dataset

def test_requires_manual_development_review(development,tmp_path):
    store,client,dataset=development;rows=load_questions(dataset);rows[0]['review_status']='unreviewed'
    dataset.write_text(''.join(json.dumps(q)+'\n' for q in rows),encoding='utf-8')
    with pytest.raises(ValueError):prepare_calibration(dataset,store,tmp_path/'calibration',client)

def test_cache_separates_model_and_avoids_repeat_calls(development,tmp_path):
    store,client,dataset=development;cached=CachedEmbeddingClient(client,tmp_path/'cache')
    cached.embed(['identical']);calls=client.calls;cached.embed(['identical']);assert client.calls==calls
    client.settings=replace(client.settings,embedding_model='other')
    cached.embed(['identical']);assert client.calls==calls+1

def test_selection_retains_cosine_and_blocks_unreviewed_labels(development,tmp_path):
    store,client,dataset=development;directory=tmp_path/'calibration'
    prepared=prepare_calibration(dataset,store,directory,client)
    assert prepared['selected_weight']==.5
    labels=load_questions(directory/'passage_labels.jsonl')
    assert labels and all(r['relevant'] is None for r in labels)
    for label in labels:
        if 'dense' in label['modes']:assert label['source']['vector_score'] is not None
    with pytest.raises(ValueError):select_gate(directory/'selection_prepared.json',dataset,store,tmp_path/'chosen.json')
    for label in labels:
        save_passage_label(directory/'passage_labels.jsonl',label['label_id'],reviewer='fixture-human',relevant=label['proposed_relevant'])
    selected=select_gate(directory/'selection_prepared.json',dataset,store,tmp_path/'chosen.json')
    assert selected['status']=='validated' and selected['selected']['vector_weight']==.5
    assert Path(selected['selection_evidence']).exists()
