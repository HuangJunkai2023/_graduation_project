"""Local-only corpus audit and bounded, source-traceable research ingestion.

No API calls are made. Raw text stays under ignored runtime/research storage;
the shareable manifest contains metadata and audit observations only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import pymupdf

from .config import APP_ROOT, Settings
from .documents import parse_file, standards
from .store import Store

REPO_ROOT = APP_ROOT.parents[1]
EXCLUDED_NAME_MARKERS = ('报批', '送审', '讨论稿', '征求', '编制说明', '专家', '报告', '作废', '【废】')
DOMAIN_TITLE = re.compile('接触网|接触线|承力索|吊弦|接触悬挂|电连接|腕臂|汇流排|受流系统|电力牵引|牵引供电')
PERMISSION = {
    'allowed_for_project': True,
    'external_text_processing_allowed': True,
    'basis': 'Student confirmation in the project conversation on 2026-11-11: all local source documents may be used.',
    'independent_licence_verification': 'not_performed',
}
# Source-bound cover observations made from rendered source pages on 2026-11-11.
# This verifies visible identifier/year only, not extraction accuracy or validity.
VISUAL_COVERS = {
    'f8723fe69f1ceda1ff9e80cdeb3557ed5656007f35c6fbff81394ac35479095f':('QCR9658','2017',1),
    'ac196d7e9e6d19723d9f6f5e7e4d44efcd87d735ffa4098458ef9b73ab6a08a8':('TB10421','2018',1),
    'f03f6e9fbc8c24ed7f43c10e48443efeb309c6622f1421b93dd0698a92b16803':('TB10308','2020',1),
    '7a64ad779211eaba45e060df48b49204f30921e4716af429ffed7c35c42ebb81':('TBT2180','2018',1),
    'b3cbd6715c059cc40d7a2f7c04cfa017cade1cd26c4cae3f8e9aca32bf6054be':('TB10075','2000',2),
    '1bb0f47245a9fbdafdc544f9bce88a249f881a6783023833407b9142a256105a':('TBT3551','2019',1),
}


def _text_signature(text: str) -> str:
    return hashlib.sha256(re.sub(r'\s+', '', text).encode('utf-8')).hexdigest()


def split_formal_collections(files: list[Path], private_root: Path) -> tuple[list[Path], dict]:
    """Extract independently numbered formal standards, never arbitrary chapters."""
    derived=[]; provenance={}
    for path in files:
        if path.suffix.lower()!='.pdf' or not re.search(r'\d[～~]\d',path.name):continue
        parent_sha=hashlib.sha256(path.read_bytes()).hexdigest()
        with pymupdf.open(path) as source:
            headings=[]
            for level,title,start in source.get_toc():
                ids=standards(re.sub(r'\s+','',title))
                if level==1 and len(ids)==1 and ids[0][1] and ids[0][0].startswith('QCR979.'):
                    headings.append((int(start),title,ids[0]))
            headings=sorted(set(headings))
            if len(headings)<2:continue
            destination=private_root/'derived_sources'/parent_sha[:16]
            destination.mkdir(exist_ok=True,parents=True)
            for index,(start,title,identity) in enumerate(headings):
                end=headings[index+1][0]-1 if index+1<len(headings) else len(source)
                cover=source[start-1].get_text()
                cover_ids=standards(re.sub(r'\s+','',cover))
                if identity not in cover_ids:continue
                if not ('发布' in cover and ('实施' in cover or '标准' in cover)):continue
                name=re.sub(r'[<>:"/\\|?*]','_',title)+'.pdf'
                target=destination/name
                if not target.exists():
                    with pymupdf.open() as part:
                        part.insert_pdf(source,from_page=start-1,to_page=end-1)
                        part.save(target,garbage=4,deflate=True)
                derived.append(target)
                provenance[target.relative_to(REPO_ROOT).as_posix()]={
                    'kind':'independently_numbered_formal_standard_extracted_from_collection',
                    'parent_path':path.relative_to(REPO_ROOT).as_posix(),
                    'parent_sha256':parent_sha,'parent_pdf_pages':[start,end],
                    'derived_pdf_page_offset_to_parent':start-1,
                    'derived_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                    'independent_standard':identity[0],'edition':identity[1],
                    'cover_page_in_derived_pdf':1,'cover_page_in_parent_pdf':start,
                    'cover_identity_matched':True,'cover_release_and_standard_markers_present':True,
                    'bookmark_title':title,
                    'location_rule':'Derived PDF file-page + offset equals parent PDF file-page. Original page images are unchanged; no OCR was used.',
                }
    return derived,provenance


def audit_source(path: Path, settings: Settings) -> tuple[dict, dict | None, list]:
    relative = path.relative_to(REPO_ROOT).as_posix()
    row = {'path': relative, 'name': path.name, 'status': 'excluded', 'permission': PERMISSION}
    if any(marker in path.name for marker in EXCLUDED_NAME_MARKERS):
        row['reason'] = 'draft_or_nonstandard_or_obsolete_marked'
        return row, None, []
    if re.search(r'\d[～~]\d', path.name):
        row['reason'] = 'multi_standard_collection_needs_separate_identity_review'
        return row, None, []
    try:
        document, chunks = parse_file(path, settings, allow_cloud=True)
    except Exception as exc:
        row.update(reason='parse_failure', error_type=type(exc).__name__)
        return row, None, []
    row.update(document_id=document['id'], standard=document['standard'], edition=document['year'],
               size_bytes=document['size_bytes'], extracted_chunks=len(chunks),
               warning_count=len(document['warnings']), publication_status=document['publication_status'])
    if not document['standard'] or not document['year']:
        row['reason'] = 'missing_single_standard_identity_or_edition'
        return row, document, chunks
    body = '\n'.join(c['text'] for c in chunks)
    cjk_count = len(re.findall(r'[\u4e00-\u9fff]', body))
    locations = list(dict.fromkeys(c['location'] for c in chunks))
    row.update(extracted_cjk_characters=cjk_count, source_unit_count=len(locations),
               source_locations=locations, text_signature=_text_signature(body))
    row['domain_mentions'] = len(re.findall('接触网|接触线|承力索|吊弦|接触悬挂|电连接|腕臂|汇流排|受电弓',body))
    if cjk_count < 300 or len(locations) < 2:
        row['reason'] = 'insufficient_extracted_body_text_no_ocr'
        return row, document, chunks
    # Distinguish corroborated front-matter identity from filename-only hints.
    first_locations = set(locations[:30] if path.suffix.lower()=='.docx' else locations[:3])
    front = ''.join(c['text'] for c in chunks if c['location'] in first_locations)
    front_ids = standards(re.sub(r'\s+', '', front))
    identity = (document['standard'], document['year'])
    row['identity_in_front_text'] = identity in front_ids
    row['identity_verification'] = 'front_text_and_filename' if identity in front_ids else 'filename_identity_requires_review'
    row['front_text_identifiers'] = [{'standard':s, 'edition':y} for s,y in front_ids[:12]]
    if re.search(r'J\s*[XxＸｘ]{2,}',front) or re.search(r'20\d{2}\s*[-—–一.]\s*[xXｘＸ]{1,2}',front):
        row['reason']='unresolved_publication_registration_or_date_placeholder_in_front_matter'
        return row,document,chunks
    reviewed=VISUAL_COVERS.get(document['id'])
    if reviewed and reviewed[:2]==identity:
        row['identity_verification']='rendered_cover_identifier_and_year_checked'
        row['cover_observation']={'checked_on':'2026-11-11','method':'Rendered source cover inspected in the assistant session','source_sha256':document['id'],'file_page':reviewed[2],'visible_standard':reviewed[0],'visible_edition':reviewed[1],'student_review':'pending'}
    elif identity not in front_ids:
        row['reason']='front_identity_not_corroborated_requires_source_review'
        return row,document,chunks
    if identity not in front_ids and any(s.startswith(document['standard']+'.') for s,y in front_ids):
        row['reason']='multi_part_standard_collection_not_single_document_identity'
        return row,document,chunks
    # Text layers with extreme spacing can inflate fixed-character chunks and
    # detach table labels from values. Keep them for diagnostics, not research.
    if len(body)>12000 and (sum(c.isspace() for c in body)/len(body)>.55 or len(chunks)>1000):
        row['reason']='severely_fragmented_layout_or_collection_requires_review'
        return row,document,chunks
    if '接触网' not in path.name and row['domain_mentions']<3:
        row['reason']='insufficient_ocs_context_in_related_standard'
        return row,document,chunks
    row['extraction_review'] = {
        'method':'Machine text-layer audit; inspect front three PDF source units or first thirty DOCX paragraphs/table rows, plus sampled first/middle/last chunks locally.',
        'sample_locations': list(dict.fromkeys(chunks[i]['location'] for i in sorted({0,len(chunks)//2,len(chunks)-1}))),
        'numeric_unit_candidates_present': bool(re.search(r'\d\s*(?:mm|kN|MPa|℃|%|毫米|千牛)',body,re.I)),
        'human_quality_approval':'pending',
        'limitations':'Text availability is not proof that tables, formulae, values, units or conditions are faithfully extracted.',
    }
    row.update(status='eligible_candidate', reason='text_available_formal_identity_review_pending')
    return row, document, chunks


def prepare(source_root: Path, output: Path, db_path: Path, target=25) -> dict:
    if not 20 <= target <= 30:
        raise ValueError('Research target must stay within 20–30 documents.')
    source_root = source_root.resolve(); db_path=db_path.resolve(); output=output.resolve(); output.mkdir(parents=True,exist_ok=True)
    settings = Settings.load(db_path=db_path)
    files = sorted(p for p in source_root.rglob('*') if p.is_file() and p.suffix.lower() in ('.pdf','.docx'))
    # Name-based first-stage screening avoids parsing unrelated infrastructure files.
    candidates = [p for p in files if DOMAIN_TITLE.search(p.name) and standards(p.name)]
    derived,provenance=split_formal_collections(candidates,db_path.parent)
    candidates+=derived
    rows=[]; parsed={}
    for index,path in enumerate(candidates,1):
        row,document,chunks = audit_source(path,settings)
        if row['path'] in provenance:row['provenance']=provenance[row['path']]
        rows.append(row)
        if row['status']=='eligible_candidate':parsed[row['path']]=(document,chunks)
        print(f'audited {index}/{len(candidates)}: {row.get("standard", "")} {row.get("edition", "")} {row["status"]}',flush=True)
    eligible=[r for r in rows if r['status']=='eligible_candidate']
    # Prefer corroborated identities, editable text, and richer extraction; one
    # source per standard/edition even when PDF/DOCX encodings differ.
    eligible.sort(key=lambda r:('provenance' in r,not r['identity_in_front_text'],r['warning_count'], -r['extracted_cjk_characters'],r['path']))
    identities={}; unique=[]; hashes=set();texts=set()
    for row in eligible:
        identity=(row['standard'],row['edition'])
        if row['document_id'] in hashes or row['text_signature'] in texts or identity in identities:
            row.update(status='excluded',reason='duplicate_file_or_same_formal_edition',duplicate_of=identities.get(identity))
            continue
        identities[identity]=row['document_id'];hashes.add(row['document_id']);texts.add(row['text_signature']);unique.append(row)
    families=defaultdict(list)
    for row in unique:families[row['standard']].append(row)
    # Edition-pair candidates take priority without claiming they are approved.
    paired=sorted((k for k,v in families.items() if len(v)>=2))
    selected=[]
    for family in paired[:2]:selected.extend(sorted(families[family],key=lambda r:r['edition'])[-2:])
    for row in unique:
        if row not in selected and len(selected)<target:selected.append(row)
    selected_ids={r['document_id'] for r in selected}
    store=Store(settings)
    existing={d['id'] for d in store.documents()}
    # Do not erase or silently replace an already used research collection.
    unexpected=existing-selected_ids
    if unexpected:raise ValueError('Existing research DB contains other documents; use a fresh path and retain the old DB.')
    reports=[]
    for row in selected:
        doc,chunks=parsed[row['path']]
        report=store.ingest(REPO_ROOT/row['path'],allow_cloud=True)
        reports.append(report)
        if report['status'] not in ('imported','duplicate'):raise ValueError(f'Ingestion failed: {row["path"]}')
        row['status']='selected_for_research_review'
    for row in unique:
        if row['document_id'] not in selected_ids:row['status']='eligible_reserve'
    edition_pairs=[{'standard':family,'editions':sorted(r['edition'] for r in selected if r['standard']==family)} for family in paired if sum(r['standard']==family for r in selected)>=2]
    manifest={
        'schema':'ocs-qa.corpus-manifest.v1','created_at':datetime.now(timezone.utc).isoformat(),
        'scope':'Chinese overhead contact system standards; PDF/DOCX; no OCR, drafts or duplicate editions.',
        'source_root':source_root.relative_to(REPO_ROOT).as_posix(),'target_documents':target,
        'counts':{'all_pdf_docx_files':len(files),'name_screened_candidates':len(candidates),'derived_independent_formal_standards':len(derived),'selected_documents':len(selected),'selected_original_source_files':len({r.get('provenance',{}).get('parent_path',r['path']) for r in selected}),'selected_derived_formal_parts':sum('provenance' in r for r in selected),'selected_chunks':len(store.records()),'eligible_unique_editions':len(unique),'selected_edition_pair_families':len(edition_pairs),'exclusion_reasons':dict(Counter(r['reason'] for r in rows if r['status']=='excluded'))},
        'processing':{'chunk_size':settings.chunk_size,'chunk_overlap':settings.chunk_overlap,'source_locations':'PDF file-page / DOCX paragraph or table row','derived_part_location_mapping':'Original collection file-page = derived file-page + provenance.derived_pdf_page_offset_to_parent','embedding_performed':False},
        'research_database':db_path.resolve().relative_to(REPO_ROOT).as_posix(),
        'permission_declaration':PERMISSION,'edition_pairs':edition_pairs,'documents':selected,
        'acceptance':{'document_count_target_met':20<=len(selected)<=30,'two_edition_pairs_available':len(edition_pairs)>=2,'human_corpus_review_complete':False,'M2_accepted':False},
        'limits':['Formal applicability/current validity is not certified.','Source identity and sample extraction need human review.','No online request or embedding performed by this command.','If no two formal edition pairs survive review, RQ2 conclusions must remain limited; no synthetic editions enter the corpus.'],
    }
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (output/'candidate_inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    with (output/'review_summary.md').open('w',encoding='utf-8') as f:
        f.write('# 研究语料审核摘要\n\n本地机器筛查与入库结果，尚待本人复核；不代表标准现行有效性认定。\n\n')
        f.write(f'候选{len(candidates)}份；选定{len(selected)}份、{len(store.records())}个文本块；可用版对候选系列{len(edition_pairs)}组。\n\n')
        f.write('| 编号 | 版本 | 文档 | 块数 | 文本身份核对 | 待复核 |\n| --- | --- | --- | ---: | --- | --- |\n')
        for row in selected:f.write(f'| {row["standard"]} | {row["edition"]} | {row["name"]} | {row["extracted_chunks"]} | {row["identity_verification"]} | 数值、单位、条件、表格与分块边界 |\n')
        f.write('\n未达到双系列双正式版本目标时，按开题预设缩小RQ2结论范围。机器抽取不可代替人工核查。原始文档与全文不复制到本输出目录。\n')
    # Keep source-bound sample material private/local for actual review.
    sample_rows=[]
    for row in selected:
        _,chunks=parsed[row['path']]
        for i in sorted({0,len(chunks)//2,len(chunks)-1}):sample_rows.append({'document_id':row['document_id'],'name':row['name'],'location':chunks[i]['location'],'text':chunks[i]['text'],'review_status':'pending'})
    private=db_path.parent;private.mkdir(exist_ok=True,parents=True)
    (private/'extraction_samples.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sample_rows),encoding='utf-8')
    return manifest


def verify_manifest(manifest_path: Path, store: Store) -> dict:
    """Check current source bytes, derived-page mapping and DB membership locally.

    This deterministic check is deliberately separate from human content review.
    """
    manifest=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    documents=store.documents(); records=store.records(); errors=[]
    expected={row['document_id']:row for row in manifest['documents']}
    actual={row['id']:row for row in documents}
    if set(expected)!=set(actual):errors.append('Manifest and database document IDs differ.')
    counts=Counter(row['document_id'] for row in records)
    if len(records)!=manifest['counts']['selected_chunks']:errors.append('Total chunk count differs.')
    for digest,row in expected.items():
        source=REPO_ROOT/row['path']
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
            errors.append(f'Source hash mismatch: {row["path"]}');continue
        if counts[digest]!=row['extracted_chunks']:errors.append(f'Chunk count mismatch: {digest}')
        if digest in actual and (actual[digest]['standard'],actual[digest]['year'])!=(row['standard'],row['edition']):
            errors.append(f'Standard identity mismatch: {digest}')
        provenance=row.get('provenance')
        if not provenance:continue
        parent=REPO_ROOT/provenance['parent_path']
        if not parent.is_file() or hashlib.sha256(parent.read_bytes()).hexdigest()!=provenance['parent_sha256']:
            errors.append(f'Parent source hash mismatch: {digest}');continue
        start,end=provenance['parent_pdf_pages'];offset=provenance['derived_pdf_page_offset_to_parent']
        if offset!=start-1 or provenance['derived_sha256']!=digest:errors.append(f'Invalid page-offset provenance: {digest}')
        with pymupdf.open(source) as derived,pymupdf.open(parent) as original:
            if start<1 or end>len(original) or end-start+1!=len(derived):
                errors.append(f'Invalid derived page range: {digest}');continue
            for index,page in enumerate(derived):
                other=original[index+start-1]
                if page.rect!=other.rect or page.get_text()!=other.get_text():
                    errors.append(f'Derived page differs from parent: {digest}:{index+1}')
    return {'valid':not errors,'errors':errors,'checked_at':datetime.now(timezone.utc).isoformat(),
            'documents_checked':len(expected),'chunks_checked':len(records),
            'derived_sources_checked':sum(bool(r.get('provenance')) for r in expected.values()),
            'human_content_review':'pending',
            'limitations':'Byte, identity and page-text checks do not certify tables, numeric semantics or formal applicability.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=REPO_ROOT/'project/task1')
    parser.add_argument('--output',type=Path,default=REPO_ROOT/'outputs/research/corpus')
    parser.add_argument('--db',type=Path,default=APP_ROOT/'runtime/research/kb.sqlite3')
    parser.add_argument('--target',type=int,default=25)
    args=parser.parse_args()
    manifest=prepare(args.source_root,args.output,args.db,args.target)
    print(json.dumps(manifest['counts'],ensure_ascii=False))


if __name__=='__main__':main()
