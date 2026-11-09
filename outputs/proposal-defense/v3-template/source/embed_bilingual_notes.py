"""Add page-aligned bilingual notes while preserving every visible slide part."""
from pathlib import Path
import json,runpy,zipfile,hashlib
from lxml import etree as E

out=Path(__file__).resolve().parent.parent
values=runpy.run_path(str(out/'source/build_bilingual_script.py'))
english=values['english']+[
 'Backup slide, outside the main presentation time. These references support the method design; they do not establish that this project has achieved its performance targets. The bibliography follows the proposal. No new literature or performance transfer across domains is claimed.',
 'Backup: normalise B and D separately using min-max scores over the eligible chunks for each query. Constant positive scores map to one; other constant scores map to zero. Select w from 0.25, 0.50 and 0.75 by development Recall@5, then MRR@5. If still tied, favour 0.50. Top-K remains five. Freeze consistent Chinese tokenisation, the domain dictionary and stopwords before testing. Do not use test outcomes for parameter selection.',
 'Backup: lexical coverage matches distinct query content tokens using the same segmenter for passages. Exclude standard identifiers and frozen stopwords; an empty denominator scores zero. Accept if coverage or raw cosine exceeds its development-selected threshold. The formal proposal gives no numerical thresholds, so prototype defaults must not be described as tuned values. Automatically check identifiers and excerpts. Human scoring assesses semantic support, values, units and conditions. API and format failures are errors, not justified refusals. Clarification is justified only for items pre-labelled as ambiguous.',
 'Backup: A1 disables only year restrictions and edition availability or ambiguity checks, while retaining standard-family filtering. A2 disables only the retrieval Evidence Gate, retaining prompts, citation validation and error handling. Retrieval, correctness and false refusal use all 64 answerable test items. Refusal recall uses 16 unanswerable items. Wrong-edition Rate uses all unambiguous edition requests, including missing editions. Citation Support uses cited claims, with each claim’s citations judged jointly. Unsupported-answer incidence uses all 80 test items. Report N/A for zero denominators.',
 'Backup: target 20–30 permitted documents and seek two standard families with two formal editions each. Deduplicate by hash and verify edition identity and source locations against document content and metadata. Do not count scans, drafts or failed extraction as usable editions. If edition pairs remain insufficient, retain A1 and limit RQ2 to supported cases. If Embedding access fails, record the failure and resolve access. Local retrieval remains a limited deliverable; it does not validate Dense, Hybrid or online QA. If a provider changes, document it and rerun all affected comparisons consistently rather than combining favourable outputs. Check permission before sending text externally, and protect credentials and test labels. Weeks 22–23 are a planned break; Weeks 25–27 cover viva preparation and examination.'
]
data=json.loads((out/'source/content.json').read_text(encoding='utf-8'))
assert len(english)==len(data)==18
src=out/'OCS_Proposal_Defense_EN_v3_SWJTU_Template.pptx'
dest=out/'OCS_Proposal_Defense_EN_v3_SWJTU_Template_Bilingual_Notes.pptx'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
A='{'+ns['a']+'}'
records=[]
with zipfile.ZipFile(src) as z,zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as target:
    replacements={}
    for i,(d,en) in enumerate(zip(data,english),1):
        name=f'ppt/notesSlides/notesSlide{i}.xml'
        element=E.fromstring(z.read(name))
        body=element.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=ns)
        assert len(body)==1,(i,len(body))
        body=body[0]
        for p in list(body):
            if p.tag==A+'p':body.remove(p)
        timing=f"主讲参考时长 / Reference time: {d['seconds']} s" if i<=13 else '备份页，不计入主讲时间 / Backup slide, outside the main talk'
        lines=[f'第{i}页 / Slide {i}: {d["title"]}',timing,'','中文逐字稿',d['script'],'','English Script',en,'','来源 / Sources',d['source']]
        for line in lines:
            p=E.SubElement(body,A+'p')
            pp=E.SubElement(p,A+'pPr',{'algn':'l'})
            spacing=E.SubElement(pp,A+'spcAft');E.SubElement(spacing,A+'spcPts',{'val':'400'})
            if line:
                run=E.SubElement(p,A+'r')
                attrs={'lang':'zh-CN','sz':'1200'}
                if line in ['中文逐字稿','English Script','来源 / Sources'] or line.startswith(f'第{i}页 / Slide {i}:'):attrs['b']='1'
                rp=E.SubElement(run,A+'rPr',attrs)
                E.SubElement(rp,A+'latin',{'typeface':'Arial'})
                E.SubElement(rp,A+'ea',{'typeface':'Microsoft YaHei'})
                E.SubElement(rp,A+'cs',{'typeface':'Arial'})
                E.SubElement(run,A+'t').text=line
            E.SubElement(p,A+'endParaRPr',{'lang':'zh-CN','sz':'1200'})
        replacements[name]=E.tostring(element,encoding='UTF-8',xml_declaration=True,standalone=True)
        records.append(dict(page=i,chinese=d['script'],english=en,seconds=d['seconds']))
    for entry in z.infolist():target.writestr(entry,replacements.get(entry.filename,z.read(entry.filename)))

clean=lambda s:''.join(s.split())
with zipfile.ZipFile(src) as old,zipfile.ZipFile(dest) as new:
    unchanged=[n for n in old.namelist() if not n.startswith('ppt/notesSlides/notesSlide')]
    assert all(old.read(n)==new.read(n) for n in unchanged)
    assert set(old.namelist())==set(new.namelist())
    for i,record in enumerate(records,1):
        el=E.fromstring(new.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        text=''.join(el.xpath('//a:t/text()',namespaces=ns))
        assert clean(record['chinese']) in clean(text)
        assert clean(record['english']) in clean(text)
        assert f'第{i}页 / Slide {i}:' in text
(out/'source/bilingual_notes.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'validation/bilingual-notes-checks.json').write_text(json.dumps(dict(pages=18,main=13,backup=5,both_languages_verified_on_all_pages=True,all_non_note_parts_byte_identical=True,source_unchanged=True,input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2),encoding='utf-8')
print('Wrote bilingual notes for all 18 slides. All visible slide parts are byte-identical.')
print(dest)
