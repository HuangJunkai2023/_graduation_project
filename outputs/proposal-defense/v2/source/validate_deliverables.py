"""Inspect final editable PPTX, PDF, CN script, notes, fonts and geometry."""
from pathlib import Path
import zipfile,json,re,hashlib,itertools,sys
from lxml import etree as E
import pymupdf

out=Path(__file__).resolve().parent.parent
root=out.parents[2]
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
data=json.loads((out/'source/content.json').read_text(encoding='utf-8'))
clean=lambda s:re.sub(r'\s+','',s)
with zipfile.ZipFile(out/'OCS_Proposal_Defense_EN_v2.pptx') as z:
    texts=[];notes=[];pictures=[];shape_counts=[];native_tables=0;fonts=set();bad_geometry=[]
    for i in range(1,19):
        el=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        ne=E.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        texts.append('\n'.join(el.xpath('//a:t/text()',namespaces=ns)))
        notes.append(''.join(ne.xpath('//a:t/text()',namespaces=ns)))
        pictures.append(len(el.xpath('//p:pic',namespaces=ns)))
        shape_counts.append(len(el.xpath('//p:sp',namespaces=ns)))
        native_tables+=len(el.xpath('//a:tbl',namespaces=ns))
        fonts.update(el.xpath('//a:latin/@typeface',namespaces=ns))
        for e in el.xpath('//a:ext',namespaces=ns):
            if int(e.get('cx',0))<0 or int(e.get('cy',0))<0:bad_geometry.append(i)
    (out/'validation/v2-content-and-notes.json').write_text(json.dumps([dict(page=i+1,text=t,notes=notes[i]) for i,t in enumerate(texts)],ensure_ascii=False,indent=2),encoding='utf-8')

script=(out/'OCS_Proposal_Defense_CN_Script.md').read_text(encoding='utf-8')
note_match=[i+1 for i,d in enumerate(data) if clean(d['script']) in clean(notes[i])]
script_match=[i+1 for i,d in enumerate(data[:13]) if f"第{i+1}页" in script and d['script'] in script]
qa=(out/'OCS_Defense_QA_CN.md').read_text(encoding='utf-8')
pdf=pymupdf.open(out/'OCS_Proposal_Defense_EN_v2.pdf')
pdf_fonts=sorted({f[3] for p in pdf for f in p.get_fonts()})
pdf_text='\n'.join(p.get_text() for p in pdf)
missing_chars='\ufffd' in pdf_text
layout=json.loads((out/'validation/powerpoint-layout.json').read_text(encoding='utf-8-sig'))

# Text-box intersection excludes containers and intentional in-box diagrams.
manifest=json.loads((out/'source/layout-manifest.json').read_text(encoding='utf-8'))
overlaps=[];out_of_bounds=[]
for a in manifest:
    if a['kind']=='text' and (a['x']<0 or a['y']<0 or a['x']+a['w']>13.334 or a['y']+a['h']>7.501):out_of_bounds.append(a)
for a,b in itertools.combinations([a for a in manifest if a['kind']=='text'],2):
    if a['page']!=b['page']:continue
    ix=min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])
    iy=min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])
    if ix>.02 and iy>.02:overlaps.append(dict(page=a['page'],a=a['text'],b=b['text'],intersection=[ix,iy]))

alltext='\n'.join(texts)
checks={
'18_total_slides':len(texts)==18,
'13_main_5_backup':all(f'B{i} / 5' in texts[12+i] for i in range(1,6)),
'all_18_notes_match_content_source':len(note_match)==18,
'all_13_script_pages_match_notes':len(script_match)==13,
'script_time_580_seconds':sum(d['seconds'] for d in data)==580,
'at_least_12_QA':len(re.findall(r'^## \d+\.',qa,re.M))>=12,
'pdf_18_pages':len(pdf)==18,
'no_text_bound_overflow':layout['overflowCount']==0,
'no_textbox_overlap':not overlaps,
'no_out_of_bounds_textboxes':not out_of_bounds,
'architecture_native_and_editable':pictures[5]==0 and shape_counts[5]>=20,
'no_full_slide_text_rasterisation':pictures==[1,1]+[0]*16,
'no_negative_geometry':not bad_geometry,
'no_stale_template_text':not any(x in alltext for x in ['请输入','某某','替换标题','2019年']),
'fonts_declared_Arial':fonts=={'Arial'},
'no_pdf_replacement_glyphs':not missing_chars,
'planning_targets_explicit':'Planned targets only' in texts[9],
'progress_snapshot_explicit':'503 text chunks, 0 vectors' in texts[10],
'dataset_split_explicit':all(x in texts[8] for x in ['100 manually checked','16 answerable + 4 unanswerable','64 answerable + 16 unanswerable','400 main test executions']),
'strict_A1_A2_retained':all(x in texts[16] for x in ['Retain standard-family filtering','Retain prompts, citation validation and error handling']),
'normalisation_and_ties_explicit':all(x in texts[14] for x in ['Constant positive scores map to 1','Other constant scores map to 0','Ties favour 0.50']),
'thresholds_not_fabricated':'No numerical threshold is claimed as tuned' in texts[15],
'corpus_and_pairs_explicit':all(x in texts[17] for x in ['20–30 usable documents','2 families × 2 formal editions']),
}
saved=json.loads((out/'validation/input-hashes.json').read_text(encoding='utf-8'))
checks['v1_and_report_unchanged']=all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in saved.items())
result=dict(checks=checks,pass_count=sum(checks.values()),check_count=len(checks),all_pass=all(checks.values()),
            note_match_pages=note_match,script_match_pages=script_match,main_seconds=580,qa_count=len(re.findall(r'^## \d+\.',qa,re.M)),
            pdf_fonts=pdf_fonts,picture_count_by_slide=pictures,editable_shape_count_by_slide=shape_counts,native_tables=native_tables,
            text_box_overlap_flags=overlaps,out_of_bounds=out_of_bounds)
(out/'validation/deliverable-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'all_pass':result['all_pass'],'checks':f"{result['pass_count']}/{result['check_count']}",'failures':[k for k,v in checks.items() if not v],'overlaps':overlaps,'pdf_fonts':pdf_fonts},ensure_ascii=True))
if not result['all_pass']:sys.exit(1)
