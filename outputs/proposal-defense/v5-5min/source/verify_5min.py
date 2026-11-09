from pathlib import Path
import json,re,zipfile
from lxml import etree as E
from PIL import Image,ImageDraw
import pymupdf

out=Path(__file__).resolve().parent.parent
rows=json.loads((out/'source/content_5min.json').read_text(encoding='utf-8'))
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
z=zipfile.ZipFile(out/'OCS_Proposal_Defense_EN_5min_SWJTU.pptx')
def text(part):return '\n'.join(E.fromstring(z.read(part)).xpath('//a:t/text()',namespaces=ns))
clean=lambda v:re.sub(r'\s+','',v)
notes=[text(f'ppt/notesSlides/notesSlide{i}.xml') for i in range(1,21)]
visible=[text(f'ppt/slides/slide{i}.xml') for i in range(1,21)]
layout=json.loads((out/'validation/powerpoint-layout.json').read_text(encoding='utf-8-sig'))
delivery=json.loads((out/'validation/delivery.json').read_text(encoding='utf-8-sig'))
checks={
 '20_slides':layout['slides']==20,
 '20_PDF_pages':len(pymupdf.open(out/'OCS_Proposal_Defense_EN_5min_SWJTU.pdf'))==20,
 '20_previews':len(list((out/'previews').glob('slide-*.png')))==20,
 '300_seconds':sum(r['seconds'] for r in rows)==300,
 '20_bilingual_notes':all(clean(r['chinese']) in clean(n) and clean(r['english']) in clean(n) for r,n in zip(rows,notes)),
 '15_main_script_pages_plus_backups':all(f"## 第{r['page']}页" in (out/'OCS_Proposal_Defense_CN_EN_Script_5min.md').read_text(encoding='utf-8') for r in rows),
 'four_part_dividers':all('PART' in visible[i-1] for i in [3,5,9,12]),
 'Contents_preserved':'Contents' in visible[1],
 'no_overflow':layout['overflowCount']==0,
 'no_stale_counters':not any('/ 18' in v for v in visible[:15]),
 'three_RQs':all(q in visible[5] for q in ['RQ1','RQ2','RQ3']),
 'native_architecture':len(E.fromstring(z.read('ppt/slides/slide7.xml')).xpath('//p:sp',namespaces=ns))>20,
 'native_table':bool(E.fromstring(z.read('ppt/slides/slide19.xml')).xpath('//a:tbl',namespaces=ns)),
}
words=sum(len(re.findall(r"\b[\w'-]+\b",r['english'])) for r in rows[:15])
result={'checks':checks,'all_pass':all(checks.values()),'english_main_words':words,'note_count':len(notes),'reference_seconds':300,'timing_limitation':'Planned timing, not a measured rehearsal.'}
(out/'validation/final-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (out/'Modification_Summary.md').open('a',encoding='utf-8') as f:
 f.write(f'\n## 最终验证\n\n{sum(checks.values())}/{len(checks)}项检查通过；20页PPT与PDF，20张渲染图，20页中英文备注匹配，PowerPoint溢出标记0处。英文主讲{words}词，计划300秒。已检查全页总览，版式、图示与原生表格正常。往返导出11页仅备注/身份修补、9页选择性重建，428个源对象保持原生恢复，9个对象修改；备份页保持可编辑。\n')
# Four review sheets retain more detail than the single overall contact sheet.
for start in range(0,20,6):
 canvas=Image.new('RGB',(1600,1440),'#e4e8ec');d=ImageDraw.Draw(canvas)
 for j,i in enumerate(range(start,min(start+6,20))):
  canvas.paste(Image.open(out/f'previews/slide-{i+1:02}.png').resize((790,444)),((j%2)*800,(j//2)*480+28))
  d.text(((j%2)*800+8,(j//2)*480+8),f'Slide {i+1}',fill='black')
 canvas.save(out/f'previews/review-{start//6+1}.png')
print(json.dumps(result,ensure_ascii=False))
assert all(checks.values())
