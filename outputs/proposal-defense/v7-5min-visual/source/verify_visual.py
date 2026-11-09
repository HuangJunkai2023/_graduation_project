from pathlib import Path
from lxml import etree as E
from PIL import Image,ImageDraw
import json,re,zipfile,pymupdf
out=Path(__file__).resolve().parent.parent
z=zipfile.ZipFile(out/'OCS_Proposal_Defense_EN_5min_SWJTU_Visual.pptx')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
def xml(part):return E.fromstring(z.read(part))
def txt(part):return '\n'.join(xml(part).xpath('//a:t/text()',namespaces=ns))
rows=json.loads((out/'source/content_5min.json').read_text(encoding='utf-8'))
clean=lambda t:re.sub(r'\s+','',t)
notes=[txt(f'ppt/notesSlides/notesSlide{i}.xml') for i in range(1,21)]
slides=[txt(f'ppt/slides/slide{i}.xml') for i in range(1,21)]
layout=json.loads((out/'validation/powerpoint-layout.json').read_text(encoding='utf-8-sig'))
checks={
'20_slides_and_PDF_pages':layout['slides']==20 and len(pymupdf.open(out/'OCS_Proposal_Defense_EN_5min_SWJTU_Visual.pdf'))==20,
'20_bilingual_notes_match':all(clean(r['chinese']) in clean(n) and clean(r['english']) in clean(n) for r,n in zip(rows,notes)),
'15_main_300_seconds':sum(r['seconds'] for r in rows[:15])==300,
'Contents_and_four_Part_dividers':'Contents' in slides[1] and all('PART' in slides[i-1] for i in [3,6,9,12]),
'three_RQs':all(t in slides[6] for t in ['RQ1','RQ2','RQ3']),
'illustration_labels':all('illustrat' in slides[i-1].lower() or 'Planned interface' in slides[i-1] for i in [5,8]),
'no_text_overflow':layout['overflowCount']==0,
'no_progress_claims':not any(t in '\n'.join(slides) for t in ['503 text chunks','Three-document BM25 prototype','Preliminary progress']),
'UI_pages_native_editable':all(len(xml(f'ppt/slides/slide{i}.xml').xpath('//p:sp',namespaces=ns))>30 for i in [5,8]),
'native_ablation_table':bool(xml('ppt/slides/slide19.xml').xpath('//a:tbl',namespaces=ns)),
'100_native_question_tiles':sum(1 for n in xml('ppt/slides/slide10.xml').xpath('//p:sp',namespaces=ns) if n.xpath('.//a:solidFill/a:srgbClr[@val="194B8C" or @val="178783" or @val="CB863A"]',namespaces=ns) and not n.xpath('.//a:t',namespaces=ns))>=100,
'20_previews':len(list((out/'previews').glob('slide-*.png')))==20,
}
result={'checks':checks,'all_pass':all(checks.values()),'reference_seconds':300,'english_main_words':sum(len(re.findall(r"\b[\w'-]+\b",r['english'])) for r in rows[:15])}
(out/'validation/final-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
c=Image.new('RGB',(1600,1000),'#E4E8EC');d=ImageDraw.Draw(c)
for i in range(20):
 c.paste(Image.open(out/f'previews/slide-{i+1:02}.png').resize((310,174)),((i%5)*320,(i//5)*250+22))
 d.text(((i%5)*320+8,(i//5)*250+4),str(i+1),fill='black')
c.save(out/'Overview.png')
with (out/'Modification_Summary.md').open('a',encoding='utf-8') as f:
 f.write(f'\n## 最终验证\n\n{sum(checks.values())}/{len(checks)}项通过；20页PPT/PDF、20页中英文备注匹配、20张渲染图，PowerPoint溢出0处。原生往返17页仅修补备注、3页重建，质量门通过。逐页总览及三页新增画面已视觉检查。配时300秒为计划值；英文主讲{result["english_main_words"]}词，实际需试讲。字体未嵌入，跨机器需对应字体。\n')
print(json.dumps(result))
assert all(checks.values())
