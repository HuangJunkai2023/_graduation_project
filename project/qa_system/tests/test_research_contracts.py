from dataclasses import replace
import httpx
import pytest
from docx import Document
from ocs_qa.config import Settings
from ocs_qa.store import Store
from ocs_qa.pipeline import Pipeline
from ocs_qa.retrieval import Retriever,normalize
from ocs_qa.preprocessing import tokens,content_terms,lexical_coverage,preprocessing_identity
from ocs_qa.api import ModelClient

def test_same_tokenizer_keeps_numbers_units_and_identifier():
    ts=tokens('TB/T 2073-2020 接触网承力索 25.5 kN')
    assert {'tbt2073','2020','接触网','承力索','25.5','kn'}<=set(ts)
    assert tokens('TB∕T2073—2020')==tokens('TB/T 2073-2020')
    assert '0.42.1' in preprocessing_identity()

def test_gate_uses_distinct_exact_tokens_and_empty_is_zero():
    assert content_terms('请问 TB/T 2073-2020 有什么要求？')==set()
    assert lexical_coverage('TB/T 2073-2020 有什么要求','任何文本')==0
    assert lexical_coverage('接触网 接触网 承力索','接触网')==.5
    assert lexical_coverage('承力索','索')==0

def make_store(tmp_path):
    s=Settings(db_path=tmp_path/'kb.sqlite3')
    st=Store(s)
    for name,text in [('TBT2073-2020.docx','接触网零部件表面应光洁。'),('TBT2073-2010.docx','接触网零部件表面要求保留。'),('TBT2074-2020.docx','接触网零部件表面要求保留。')]:
        doc=Document();doc.add_paragraph(text);path=tmp_path/name;doc.save(path);st.ingest(path)
    return st

def test_a1_retains_family_but_disables_year_missing_ambiguity(tmp_path):
    st=make_store(tmp_path);r=Retriever(st,None)
    a1=r.search('TB/T2073-1990 表面',edition_filter=False)
    assert a1['status']=='retrieved'
    assert {s['document']['standard'] for s in a1['sources']}=={'TBT2073'}
    assert {s['document']['year'] for s in a1['sources']}=={'2010','2020'}
    assert r.search('TB/T2073-1990 表面')['status']=='missing_edition'
    assert r.search('TB/T2073 表面')['status']=='clarify_edition'
    assert r.search('TB/T9999-2020 表面',edition_filter=False)['sources']==[]

def test_a2_still_blocks_invalid_citations(tmp_path):
    st=make_store(tmp_path)
    class Fake:
        def chat(self,*args):return {'status':'answered','claims':[{'text':'任意回答','citations':[{'source':99,'quote':'这不是来源中的连续原文'}]}]},{}
    result=Pipeline(st,Fake()).answer('TB/T2073-2020 表面',generate=True,evidence_check=False)
    # Existing documents must be explicitly permitted before any generated answer.
    assert result['status']=='cloud_permission_required'
    st.set_cloud_permission([d['id'] for d in st.documents()],True)
    result=Pipeline(st,Fake()).answer('TB/T2073-2020 表面',generate=True,evidence_check=False)
    assert result['status']=='invalid_citation'

def test_normalization_constant_rules():
    assert normalize({0:3,1:3})=={0:1.,1:1.}
    assert normalize({0:0,1:0})=={0:0.,1:0.}
    assert normalize({0:-1,1:-1})=={0:0.,1:0.}
    assert normalize({0:2,1:4})=={0:0.,1:1.}
    assert normalize({0:1.,1:1.+1e-10})=={0:0.,1:1.}

def test_metadata_records_usage_without_key_or_prompt(tmp_path):
    import json
    s=Settings(db_path=tmp_path/'x.sqlite3',chat_key='secret-api-key')
    body={'model':'returned-model','usage':{'total_tokens':8},'choices':[{'message':{'content':'{"status":"insufficient"}'},'finish_reason':'stop'}]}
    client=ModelClient(s,httpx.MockTransport(lambda req:httpx.Response(200,json=body)),event_sink=tmp_path/'usage.jsonl')
    client.chat('private-system','private-prompt')
    raw=(tmp_path/'usage.jsonl').read_text(encoding='utf-8')
    assert all(secret not in raw for secret in ['secret-api-key','private-system','private-prompt'])
    assert json.loads(raw)['returned_model']=='returned-model'
    assert json.loads(raw)['usage']['total_tokens']==8
