from pathlib import Path
from lxml import etree as E
from collections import Counter
import zipfile,json,re,hashlib
import pymupdf

out=Path(__file__).resolve().parent.parent
root=out.parents[2]
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
clean=lambda x:re.sub(r'\s+','',x)
src=zipfile.ZipFile(out/'source/inputs/OCS_Proposal_Defense_EN_v2.pptx')
dst=zipfile.ZipFile(out/'OCS_Proposal_Defense_EN_v3_SWJTU_Template.pptx')
tpl=zipfile.ZipFile(out/'source/inputs/交大ppt模板-1.pptx')
def slide(z,i):return E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
def text(z,i):return '\n'.join(slide(z,i).xpath('//a:t/text()',namespaces=ns))
def notes(z,i):return clean(''.join(E.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')).xpath('//a:t/text()',namespaces=ns)))
def body_objects(z,i):
    objects=[]
    for s in slide(z,i).xpath('/p:sld/p:cSld/p:spTree/*',namespaces=ns):
        ys=s.xpath('.//a:off/@y',namespaces=ns)
        if ys and float(ys[0])/12700>=99.99:
            objects.append((E.QName(s).localname,clean(''.join(s.xpath('.//a:t/text()',namespaces=ns)))))
    return Counter(objects)
body_match={str(i):body_objects(src,i)==body_objects(dst,i) for i in range(2,19) if i!=13}
note_match={str(i):notes(src,i)==notes(dst,i) for i in range(1,19)}
data=json.loads((out/'source/content.json').read_text(encoding='utf-8'))
script=(out/'OCS_Proposal_Defense_CN_Script.md').read_text(encoding='utf-8')
def media(z):return {hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
common_media=media(tpl)&media(dst)
layout=json.loads((out/'validation/powerpoint-layout.json').read_text(encoding='utf-8-sig'))
pdf=pymupdf.open(out/'OCS_Proposal_Defense_EN_v3_SWJTU_Template.pdf')
alltext='\n'.join(text(dst,i) for i in range(1,19))
overlap=[]
objects=json.loads((out/'validation/powerpoint-objects.json').read_text(encoding='utf-8-sig'))
for i in range(1,19):
    if i in [1,13]:continue # Template's decorative graphics intentionally overlap.
    labels=[s for s in objects if s['page']==i and s['text'].strip()]
    for aidx,a in enumerate(labels):
        for b in labels[aidx+1:]:
            ix=min(a['x']+a['width'],b['x']+b['width'])-max(a['x'],b['x'])
            iy=min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y'])
            if ix>1.5 and iy>1.5:overlap.append(dict(page=i,a=a['name'],b=b['name']))
checks={
'18_pages_13_main_5_backup':len(pdf)==18 and len(data)==18,
'16_content_pages_preserve_all_v2_body_objects':all(body_match.values()),
'18_chinese_notes_unchanged':all(note_match.values()),
'13_script_pages_still_match':all(d['script'] in script for d in data[:13]),
'580_second_timing_unchanged':sum(d['seconds'] for d in data)==580,
'native_table_retained':len(slide(dst,17).xpath('//a:tbl',namespaces=ns))==1,
'architecture_remains_editable':len(slide(dst,6).xpath('//p:sp',namespaces=ns))>20,
'original_template_media_reused':len(common_media)>=3,
'original_template_and_v2_unchanged':all((root/a).read_bytes()==(out/b).read_bytes() for a,b in [('docs/交大ppt模板-1.pptx','source/inputs/交大ppt模板-1.pptx'),('outputs/proposal-defense/v2/OCS_Proposal_Defense_EN_v2.pptx','source/inputs/OCS_Proposal_Defense_EN_v2.pptx')]),
'no_text_overflow':layout['overflowCount']==0,
'no_nonintentional_textbox_overlap':not overlap,
'no_template_placeholder_residue':not any(t in alltext for t in ['请输入','替换标题','某某','2019年']),
'18_preview_files':len(list((out/'previews').glob('slide-*.png')))==18,
'no_pdf_missing_glyphs':'\ufffd' not in ''.join(p.get_text() for p in pdf),
}
result=dict(checks=checks,all_pass=all(checks.values()),body_match=body_match,note_match=note_match,common_template_media=len(common_media),overlap_flags=overlap,pdf_fonts=sorted({f[3] for p in pdf for f in p.get_fonts()}))
(out/'validation/migration-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pass':result['all_pass'],'checks':f'{sum(checks.values())}/{len(checks)}','failures':[k for k,v in checks.items() if not v],'template_media':len(common_media),'overlaps':overlap}))
if not result['all_pass']:raise SystemExit(1)
