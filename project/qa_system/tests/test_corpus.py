"""Source identity and collection boundaries must fail closed before ingestion."""
from pathlib import Path
import hashlib
import json
import pymupdf
import pytest

from ocs_qa import corpus
from ocs_qa.config import Settings


def test_collection_only_splits_independently_numbered_formal_covers(tmp_path, monkeypatch):
    monkeypatch.setattr(corpus, 'REPO_ROOT', tmp_path)
    source=tmp_path/'QCR979.1～2-2023 接触网.pdf'
    with pymupdf.open() as doc:
        for part in [1,2]:
            page=doc.new_page()
            page.insert_text((50,50),f'Q/CR 979.{part}-2023')
            page.insert_text((50,80),'正式标准 发布 实施',fontname='china-s')
            doc.new_page().insert_text((50,50),'Supporting body text.')
        doc.set_toc([[1,'QCR979.1-2023 接触网 第1部分',1],[1,'6.5 A chapter, not a separate standard',2],[1,'QCR979.2-2023 接触网 第2部分',3]])
        doc.save(source)
    files,provenance=corpus.split_formal_collections([source],tmp_path/'runtime')
    assert len(files)==2
    rows=list(provenance.values())
    assert [r['parent_pdf_pages'] for r in rows]==[[1,2],[3,4]]
    assert [r['derived_pdf_page_offset_to_parent'] for r in rows]==[0,2]
    assert all(r['cover_identity_matched'] for r in rows)
    assert all(len(pymupdf.open(p))==2 for p in files)


def test_cover_must_match_the_bookmark_before_split(tmp_path, monkeypatch):
    monkeypatch.setattr(corpus,'REPO_ROOT',tmp_path)
    source=tmp_path/'QCR979.1～2-2023 接触网.pdf'
    with pymupdf.open() as doc:
        for part in [1,3]:
            page=doc.new_page();page.insert_text((50,50),f'Q/CR 979.{part}-2023')
            page.insert_text((50,80),'正式标准 发布 实施',fontname='china-s')
        doc.set_toc([[1,'QCR979.1-2023 接触网 第1部分',1],[1,'QCR979.2-2023 接触网 第2部分',2]])
        doc.save(source)
    files,rows=corpus.split_formal_collections([source],tmp_path/'runtime')
    assert len(files)==1
    assert next(iter(rows.values()))['independent_standard']=='QCR979.1'


@pytest.mark.parametrize('placeholder',['JXXX-2010','2010—xx—xx 发布'])
def test_front_matter_publication_placeholder_is_not_formal_evidence(tmp_path,monkeypatch,placeholder):
    monkeypatch.setattr(corpus,'REPO_ROOT',tmp_path)
    source=tmp_path/'TB 10758-2010 接触网.pdf';source.write_bytes(b'fixture')
    document={'id':'test','standard':'TB10758','year':'2010','size_bytes':7,'warnings':[],'publication_status':'unverified'}
    chunks=[{'text':'TB10758-2010 '+placeholder+' '+'接触网技术要求。'*60,'location':'PDF第1页'}, {'text':'接触线试验条件。'*60,'location':'PDF第2页'}]
    monkeypatch.setattr(corpus,'parse_file',lambda *a,**kw:(document,chunks))
    row,_,_=corpus.audit_source(source,Settings())
    assert row['status']=='excluded'
    assert row['reason']=='unresolved_publication_registration_or_date_placeholder_in_front_matter'


def test_manifest_verification_detects_changed_source_bytes(tmp_path,monkeypatch):
    monkeypatch.setattr(corpus,'REPO_ROOT',tmp_path)
    source=tmp_path/'source.pdf';source.write_bytes(b'original')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    row={'document_id':digest,'path':'source.pdf','standard':'TBT1','edition':'2020','extracted_chunks':1}
    manifest=tmp_path/'manifest.json';manifest.write_text(json.dumps({'documents':[row],'counts':{'selected_chunks':1}}))
    class FixtureStore:
        def documents(self):return [{'id':digest,'standard':'TBT1','year':'2020'}]
        def records(self):return [{'document_id':digest}]
    assert corpus.verify_manifest(manifest,FixtureStore())['valid']
    source.write_bytes(b'changed')
    check=corpus.verify_manifest(manifest,FixtureStore())
    assert not check['valid']
    assert 'Source hash mismatch' in check['errors'][0]


def test_manifest_verification_rejects_wrong_derived_page_offset(tmp_path,monkeypatch):
    monkeypatch.setattr(corpus,'REPO_ROOT',tmp_path)
    parent=tmp_path/'parent.pdf';derived=tmp_path/'derived.pdf'
    with pymupdf.open() as pdf:
        pdf.new_page().insert_text((50,50),'Cover')
        pdf.new_page().insert_text((50,50),'Independent standard')
        pdf.save(parent)
        with pymupdf.open() as part:
            part.insert_pdf(pdf,from_page=1,to_page=1);part.save(derived)
    digest=hashlib.sha256(derived.read_bytes()).hexdigest()
    row={'document_id':digest,'path':'derived.pdf','standard':'TBT1','edition':'2020','extracted_chunks':1,
         'provenance':{'parent_path':'parent.pdf','parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
                       'parent_pdf_pages':[2,2],'derived_pdf_page_offset_to_parent':0,'derived_sha256':digest}}
    manifest=tmp_path/'manifest.json';manifest.write_text(json.dumps({'documents':[row],'counts':{'selected_chunks':1}}))
    class FixtureStore:
        def documents(self):return [{'id':digest,'standard':'TBT1','year':'2020'}]
        def records(self):return [{'document_id':digest}]
    check=corpus.verify_manifest(manifest,FixtureStore())
    assert not check['valid']
    assert any('Invalid page-offset' in e for e in check['errors'])
