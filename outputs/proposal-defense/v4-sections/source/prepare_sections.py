"""Remap the bilingual scripts for a native Contents page and four Part dividers."""
from pathlib import Path
import json,re,hashlib
root=Path('D:/_graduation_project')
out=Path(__file__).resolve().parent.parent
old=root/'outputs/proposal-defense/v3-template'
notes=json.loads((old/'source/bilingual_notes.json').read_text(encoding='utf-8'))
metadata=json.loads((old/'source/content.json').read_text(encoding='utf-8'))
mapping={1:1,2:4,3:5,4:6,5:8,6:9,7:10,8:11,9:13,10:14,11:16,12:17,13:18,14:19,15:20,16:21,17:22,18:23}
parts=[
 dict(number='01',title='Background and Motivation',breakTitle='Background and\nMotivation',items='Standards consultation\nIllustrative query\nRelated work and research gap',start=3,template=4,chinese='首先，介绍研究背景与动机。',english='First, the background and motivation.'),
 dict(number='02',title='Research Questions and Methods',breakTitle='Research Questions\nand Methods',items='Three research questions\nSystem architecture\nRetrieval and evidence checks',start=7,template=5,chinese='下面进入研究问题与技术方法。',english='Next, the research questions and methods.'),
 dict(number='03',title='Evaluation Plan',breakTitle='Evaluation Plan',items='Benchmark and data split\nFive controlled configurations\nMetrics and planned targets',start=12,template=6,chinese='接下来，说明如何评价研究方案。',english='Next, how will the study be evaluated?'),
 dict(number='04',title='Feasibility and Schedule',breakTitle='Feasibility\nand Schedule',items='Recorded progress\nRisks and fallback scope\nMilestones and expected outputs',start=15,template=7,chinese='最后，介绍可行性与研究进度。',english='Finally, feasibility and the project schedule.')]
sequence=[('old',1),('contents',None),('part',0),('old',2),('old',3),('old',4),('part',1),('old',5),('old',6),('old',7),('old',8),('part',2),('old',9),('old',10),('part',3),('old',11),('old',12),('old',13)]+[('old',n) for n in range(14,19)]
rows=[]
for page,(kind,index) in enumerate(sequence,1):
 if kind=='old':
  n=notes[index-1];m=metadata[index-1]
  source=re.sub(r'备份第(\d+)页',lambda x:f'备份第{mapping[int(x[1])]}页',m['source'])
  r=dict(page=page,kind=kind,oldPage=index,title=m['title'],seconds=n['seconds'],chinese=n['chinese'],english=n['english'],source=source)
 elif kind=='contents':
  r=dict(page=page,kind=kind,title='Contents',template=3,seconds=8,chinese='下面按目录中的四个部分展开，先介绍研究背景与动机。',english='The presentation has four parts. I will begin with the background and motivation.',source='交大原模板第3页目录。四部分仅重组展示顺序，不改变研究方案。')
 else:
  p=parts[index]
  r=dict(page=page,kind=kind,title='Part '+p['number']+': '+p['title'],template=p['template'],part=p,seconds=3,chinese=p['chinese'],english=p['english'],source=f"交大原模板第{p['template']}页原生分节过渡版式。")
 label=f'主讲参考时长 / Reference time: {r["seconds"]} s' if page<=18 else '备份页，不计入主讲 / Backup slide, outside the main talk'
 r['notes']=f"第{page}页 / Slide {page}: {r['title']}\n{label}\n\n中文逐字稿\n{r['chinese']}\n\nEnglish Script\n{r['english']}\n\n来源 / Sources\n{r['source']}"
 rows.append(r)
assert len(rows)==23 and sum(r['seconds'] for r in rows)==600
(out/'source/sections_content.json').write_text(json.dumps(dict(slides=rows,parts=parts,pageMapping=mapping),ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 开题答辩中英文对照逐字稿（含目录与Part过渡页）','','对应 `OCS_Proposal_Defense_EN_v4_SWJTU_Sections.pptx`：第1–18页主讲，第19–23页备份。','','原13页主讲内容加入1页Contents及4页Part过渡，研究正文不增加。参考时长10分钟（600秒），其中目录8秒、每个Part过渡3秒。现场选择中文或英文讲述，不连续朗读两种语言；实际时长须试讲校准。','']
cn=['# 开题答辩中文逐字稿（含目录与Part过渡页）','','对应v4：第1–18页主讲，第19–23页备份。参考时长10分钟，非实测时长。','']
elapsed=0
for r in rows[:18]:
 start=elapsed;elapsed+=r['seconds']
 timing=f"预计 {r['seconds']} 秒；累计 {start//60:02d}:{start%60:02d}–{elapsed//60:02d}:{elapsed%60:02d}"
 lines += [f"## 第{r['page']}页：{r['title']}",'',timing,'','**中文**','',r['chinese'],'','**English**','',r['english'],'']
 cn += [f"## 第{r['page']}页：{r['title']}",'',timing,'',r['chinese'],'']
backup='第19页：参考文献；第20页：Hybrid公式与选参；第21页：Evidence Gate与人工评分；第22页：消融定义与指标分母；第23页：数据与备用方案。按评委提问跳转。'
lines+=['## 备份页 / Backup slides','',backup,'','Slide 19: references. Slide 20: Hybrid scoring and selection. Slide 21: Evidence Gate and human scoring. Slide 22: ablation contracts and denominators. Slide 23: data risks and fallback scope. Use these slides in response to questions.','']
cn+=['## 备份页','',backup,'']
(out/'OCS_Proposal_Defense_CN_EN_Script.md').write_text('\n'.join(lines),encoding='utf-8')
(out/'OCS_Proposal_Defense_CN_Script.md').write_text('\n'.join(cn),encoding='utf-8')
qa=(old/'OCS_Defense_QA_CN.md').read_text(encoding='utf-8').replace('对应交大模板版 v3','对应交大模板分节版 v4')
qa=re.sub(r'可跳转：PPT 第([^\n]+)页。',lambda m:'可跳转：PPT 第'+re.sub(r'\d+',lambda n:str(mapping[int(n[0])]),m[1])+'页。',qa)
(out/'OCS_Defense_QA_CN.md').write_text(qa,encoding='utf-8')
inputs=[old/'OCS_Proposal_Defense_EN_v3_SWJTU_Template_Bilingual_Notes.pptx',root/'docs/交大ppt模板-1.pptx']
(out/'validation/input-hashes.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},ensure_ascii=False,indent=2),encoding='utf-8')
print('23 slides: 18 main + 5 backup; reference timing 600 seconds. Scripts and Q&A remapped.')
