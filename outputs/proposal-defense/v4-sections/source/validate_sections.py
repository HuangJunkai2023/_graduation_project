from pathlib import Path
from collections import Counter
import json,re,zipfile,hashlib
from lxml import etree as E
import pymupdf

root=Path('D:/_graduation_project');out=Path(__file__).resolve().parent.parent
data=json.loads((out/'source/sections_content.json').read_text(encoding='utf-8'))
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
clean=lambda x:re.sub(r'\s+','',x)
new=zipfile.ZipFile(out/'OCS_Proposal_Defense_EN_v4_SWJTU_Sections.pptx')
old=zipfile.ZipFile(root/'outputs/proposal-defense/v3-template/OCS_Proposal_Defense_EN_v3_SWJTU_Template_Bilingual_Notes.pptx')
def slide(z,i):return E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
def text(z,i):return '\n'.join(slide(z,i).xpath('//a:t/text()',namespaces=ns))
def content(z,i):
 s=slide(z,i)
 return Counter(clean(t) for t in s.xpath('//a:t/text()',namespaces=ns) if not re.fullmatch(r'\d{2} / (13|18)',t))
body={r['page']:content(new,r['page'])==content(old,r['oldPage']) for r in data['slides'] if r['kind']=='old'}
notes={}
for r in data['slides']:
 i=r['page'];el=E.fromstring(new.read(f'ppt/notesSlides/notesSlide{i}.xml'))
 t=''.join(el.xpath('//a:t/text()',namespaces=ns))
 notes[i]=all(clean(v) in clean(t) for v in [r['chinese'],r['english'],f'第{i}页 / Slide {i}:'])
layout=json.loads((out/'validation/powerpoint-layout.json').read_text(encoding='utf-8-sig'))
script=(out/'OCS_Proposal_Defense_CN_EN_Script.md').read_text(encoding='utf-8')
pdf=pymupdf.open(out/'OCS_Proposal_Defense_EN_v4_SWJTU_Sections.pdf')
hashes=json.loads((out/'validation/input-hashes.json').read_text(encoding='utf-8'))
ct=text(new,2)
checks={
'23_slides_18_main_5_backup':layout['slides']==23 and len(pdf)==23,
'original_18_slides_preserved':all(body.values()),
'four_part_names_in_Contents':all(p['title'] in ct for p in data['parts']),
'four_native_dividers_before_each_part':all('PART' in text(new,p['start']) and p['number'] in text(new,p['start']) and p['breakTitle'].replace('\n','') in text(new,p['start']).replace('\n','') for p in data['parts']),
'23_bilingual_notes_match_pages':all(notes.values()),
'18_script_pages_match':len(re.findall(r'^## 第\d+页',script,re.M))==18 and all(r['chinese'] in script and r['english'] in script for r in data['slides'][:18]),
'600_seconds_including_transitions':sum(r['seconds'] for r in data['slides'])==600,
'six_native_PowerPoint_sections':layout['sectionCount']==6,
'no_text_overflow':layout['overflowCount']==0,
'23_previews':len(list((out/'previews').glob('slide-*.png')))==23,
'table_remains_native':len(slide(new,22).xpath('//a:tbl',namespaces=ns))==1,
'architecture_remains_editable':len(slide(new,9).xpath('//p:sp',namespaces=ns))>20,
'no_stale_placeholders':not any(s in '\n'.join(text(new,i) for i in range(1,24)) for s in ['请输入','请添加内容','请在此添加标题','某某','2019年']),
'original_template_and_v3_unchanged':all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in hashes.items()),
'PDF_no_replacement_glyphs':'\ufffd' not in ''.join(p.get_text() for p in pdf)
}
result=dict(checks=checks,all_pass=all(checks.values()),original_slide_match=body,bilingual_note_match=notes,main_seconds=600,pageMapping=data['pageMapping'])
(out/'validation/section-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pass':result['all_pass'],'checks':f'{sum(checks.values())}/{len(checks)}','failures':[k for k,v in checks.items() if not v]}))
if not result['all_pass']:raise SystemExit(1)
