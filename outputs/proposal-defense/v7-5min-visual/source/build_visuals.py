from pathlib import Path
import json,re
from lxml import etree as E
from xml.sax.saxutils import escape

out=Path(__file__).resolve().parent.parent
w=out/'workspace'
prior=out.parent/'v6-5min-background'
rows=json.loads((prior/'source/content_5min.json').read_text(encoding='utf-8'))
S='http://www.w3.org/2000/svg';ns={'s':S}
BLUE='#194B8C';DARK='#23364B';TEAL='#178783';GRAY='#64748B'
def rect(x,y,width,height,fill='#FFFFFF',stroke='none',r=0):
 return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
def text(x,y,value,size=23,color=DARK,bold=False):
 return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" fill="{color}" font-weight="{ "bold" if bold else "normal" }">{escape(value)}</text>'
def line(x1,y1,x2,y2,color='#CBD5E1',width=2):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
def group(id,bounds,body):
 return f'<g id="{id}" data-pptx-bounds="{bounds}">{body}</g>'
def browser(x,y,width,height,title):
 return rect(x,y,width,height,'#FFFFFF','#CCD7E3',10)+rect(x,y,width,36,'#EAF0F7',r=10)+text(x+18,y+25,'●  ●  ●',15,GRAY)+text(x+95,y+25,title,17,GRAY)
def page(number,title,body,footer):
 path=w/f'authoring-svg-flat/slide_{number:02}.svg'
 root=E.parse(str(path)).getroot()
 for n in list(root):
  if n.tag.endswith('rect'):continue
  if n.get('id','').startswith(('layout-','master-')):continue
  f=n.get('data-pptx-frame')
  if not f:
   if n.get('id') in ['frontend-window','usage-steps','source-preview','refusal-preview','system-workflow','question-benchmark','experiment-configurations']:root.remove(n)
   continue
  x,y,ww,hh=map(float,f.split())
  keep=y<90 or y>=670
  if keep:
   for t in n.xpath('.//s:text',namespaces=ns):
    val=''.join(t.itertext())
    if y<90:new=title
    elif re.fullmatch(r'\d{2} / 15',val):continue
    elif val.strip():new=footer
    else:continue
    nodes=[e for e in t.iter() if e.text]
    nodes[0].text=new
    for e in nodes[1:]:e.text=''
  else:root.remove(n)
 fragment=E.fromstring(f'<svg xmlns="{S}">{body}</svg>'.encode())
 for child in fragment:root.append(child)
 path.write_bytes(E.tostring(root,encoding='utf-8'))

# Page 5: large editable front-end concept. No real standard claim is invented.
b=browser(50,110,930,520,'OCS Standards Assistant / planned Streamlit interface')
b+=rect(51,147,200,482,'#F1F5F9')
b+=text(70,185,'Query settings',23,BLUE,True)
for y,label,value in [(220,'Standard family','Standard S'),(310,'Requested edition','Edition A'),(400,'Retrieval','Hybrid')]:
 b+=text(70,y,label,18,GRAY)+rect(68,y+12,165,46,'#FFFFFF','#CBD5E1',5)+text(80,y+42,value,20)
b+=text(70,520,'Learning and',17,GRAY)+text(70,545,'consultation only',17,GRAY)
b+=text(278,188,'Ask the permitted documents',26,BLUE,True)
b+=rect(276,213,676,72,'#EAF1FA',r=8)+text(295,244,'Which test requirements apply to fitting X',22)+text(295,272,'in edition A?',22)
b+=rect(276,308,676,172,'#F4FAF9',r=8)+text(296,344,'Answer with evidence [1]',25,TEAL,True)
b+=text(296,383,'A requirement summary would appear here.',22)+text(296,418,'Each factual claim links to its source.',22)+text(296,455,'No actual standard clause is reproduced.',18,GRAY)
b+=rect(276,501,676,57,'#FFFFFF','#B4CED0',6)+text(294,537,'[1] Standard S · Edition A · source location',21,TEAL,True)
b+=rect(276,577,676,37,'#FFFFFF','#CBD5E1',5)+text(295,603,'Ask a follow-up question…',19,GRAY)
labels=text(1010,174,'1  SET EDITION',22,BLUE,True)+text(1010,213,'Keep the requested',20)+text(1010,241,'document context.',20)
labels+=text(1010,333,'2  ASK',22,BLUE,True)+text(1010,372,'Use a practical',20)+text(1010,400,'document question.',20)
labels+=text(1010,510,'3  CHECK SOURCE',22,TEAL,True)+text(1010,549,'Open the citation',20)+text(1010,577,'and inspect evidence.',20)
page(5,'What the user will see',group('frontend-window','50 110 930 520',b)+group('usage-steps','1008 145 230 470',labels),
 'Planned interface illustration. Fictional Standard S, editions A/B and fitting X. Not a live result.')

# Page 8: two recognizable application screens, with a simple workflow below.
b=browser(50,112,710,382,'Open source [1]')
b+=rect(70,166,235,306,'#F1F5F9')+text(88,200,'Citation details',23,BLUE,True)
for y,v in [(240,'Standard S'),(278,'Edition A'),(316,'PDF page /'),(345,'DOCX location')]:b+=text(88,y,v,21)
b+=text(88,406,'Matched edition',19,TEAL,True)
b+=rect(332,164,403,308,'#FFFFFF','#CBD5E1')+text(350,199,'SOURCE DOCUMENT',21,GRAY,True)
for y in [225,242,259,353,370,387,425]:b+=rect(353,y,352 if y%2 else 295,5,'#DDE4ED')
b+=rect(347,281,371,55,'#FFF0B5')+text(359,305,'Highlighted supporting passage',18,DARK)+text(359,328,'(illustrative placeholder)',18,GRAY)
left=group('source-preview','50 112 710 382',b)
b=browser(790,112,440,382,'When evidence is insufficient')
b+=text(814,190,'Requested: Edition A',22,BLUE,True)+text(814,230,'Available: Edition B only',21)
b+=rect(811,262,397,158,'#FFF5E9',r=8)+text(830,299,'Cannot answer reliably',24,'#AA641C',True)
b+=text(830,337,'The requested edition is missing.',20)+text(830,373,'Please provide edition A.',20)
b+=text(814,458,'No silent substitution of edition B.',20,GRAY)
right=group('refusal-preview','790 112 440 382',b)
b=''
steps=[('PDF / DOCX','Parse + metadata'),('Retrieve','BM25 / Dense / Hybrid'),('Evidence Gate','Coverage OR cosine'),('DeepSeek → UI','Answer + citations')]
for i,(a,c) in enumerate(steps):
 x=50+i*302
 b+=rect(x,530,276,95,'#EAF1FA',r=6)+text(x+16,563,a,23,BLUE,True)+text(x+16,600,c,19)
 if i<3:b+=text(x+281,586,'→',25,TEAL,True)
page(8,'Make the evidence visible — or refuse',left+right+group('system-workflow','50 530 1182 95',b),
 'Planned interface states. Gate signals are heuristic; evidence support requires human scoring.')

# Page 10: planned question counts shown as 100 editable question tiles.
b=text(55,125,'100 manually checked questions',31,BLUE,True)
b+=text(55,161,'Each tile represents one planned question.',21,GRAY)
for i in range(100):
 x=58+(i%20)*34;y=192+(i//20)*42
 color=BLUE if i<20 else (TEAL if i<84 else '#CB863A')
 b+=rect(x,y,25,29,color,r=3)
b+=rect(58,425,20,20,BLUE)+text(92,443,'20 development: 16 answerable + 4 unanswerable',22)
b+=rect(58,468,20,20,TEAL)+text(92,486,'64 answerable test',20)
b+=rect(398,468,20,20,'#CB863A')+text(432,486,'16 unanswerable test',20)
b+=text(58,542,'Select weights and thresholds on development data.',20,GRAY)
b+=text(58,580,'Freeze data, prompts, configurations and model settings.',20,GRAY)
left=group('question-benchmark','50 95 710 520',b)
b=text(805,127,'5 controlled configurations',27,BLUE,True)
for j,(code,name) in enumerate([('B1','BM25'),('B2','Dense'),('B3','Hybrid'),('A1','Hybrid · edition checks off'),('A2','Hybrid · Gate off')]):
 y=154+j*64
 b+=rect(799,y,430,54,'#F0F5FA',r=5)+text(816,y+35,code,24,BLUE,True)+text(873,y+35,name,21)
b+=text(803,510,'80 × 5 = 400',34,TEAL,True)+text(803,546,'planned main test executions',21)
b+=text(803,582,'A1 retains standard-family filtering.',18,GRAY)+text(803,608,'A2 retains prompts and citation checks.',18,GRAY)
page(10,'How the study will be tested',left+group('experiment-configurations','790 95 440 530',b),
 'Planned counts, not completed tests. A2 also retains error handling. Definitions and denominators: backup slides.')

for p in ['source','validation','previews']:(out/p).mkdir(exist_ok=True,parents=True)
newnotes={
5:('这就是计划中的前端界面示意，不是已经运行的结果，也不引用真实条款。评委可以按右侧三个动作理解：先选标准和版本，再输入实际问题，最后点击答案下面的引用查看依据。这里最重要的不是聊天框，而是回答与来源能够连起来。普通模型可能混用版本或给出没有来源的回答；本课题希望让使用者能够检查答案来自哪里。示意中的标准S和部件X都是占位内容，系统效果还需要后面的正式实验验证。',
'This is a planned interface illustration, not a live result or a real standard quotation. The three actions are to select the standard and edition, ask a practical question, and open the citation below the answer. The key feature is the connection between the answer and its evidence. A model may otherwise mix editions or answer without sources. Here, users would be able to inspect where an answer comes from. Standard S and fitting X are fictional placeholders, and the system still requires formal evaluation.'),
8:('点击引用后，左侧会展示文档版本、来源位置和高亮证据；如果用户要求A版而资料中只有B版，右侧展示计划中的拒答提示，不偷偷换版本。下面的流程可以概括为：解析文档、检索证据、Gate筛选、DeepSeek组织回答并在界面展示。Gate使用词项覆盖率或原始余弦相似度，只是启发式信号；证据是否真正支持答案仍由人工评价。',
'Opening a citation would show the edition, source location, and highlighted passage on the left. The right illustrates refusal when edition A is requested but only edition B is available. The workflow below is document parsing, retrieval, evidence screening, and DeepSeek generation with source display. The gate uses term coverage or raw cosine similarity. These are heuristic signals; human scoring must still establish whether evidence supports the answer.'),
10:('左侧每个小方块代表一道计划题目，共一百道人工校核题。二十道开发题包含十六道可回答、四道不可回答；八十道测试题包含六十四道可回答、十六道不可回答。右侧五组配置比较BM25、Dense、Hybrid，以及关闭版本检查或关闭Gate的效果。A1仍保留标准系列过滤；A2仍保留提示词、引用校验和错误处理。计划语料为二十到三十份，尽可能覆盖两个系列、各两个正式版本。测试前冻结数据和设置，计划执行八十乘五，共四百次，并不是已经完成。',
'Each tile represents one planned question: one hundred manually checked questions in total. Twenty development questions contain sixteen answerable and four unanswerable items; eighty test questions contain sixty-four answerable and sixteen unanswerable items. The five configurations compare BM25, Dense, Hybrid, and Hybrid with edition checks or the gate disabled. A1 retains family filtering; A2 retains prompts, citation validation, and error handling. We plan twenty to thirty usable documents, ideally two families with two formal editions each. Frozen settings will be used for four hundred planned test runs, which have not been completed.')
}
titles={5:'What the user will see',8:'Make the evidence visible — or refuse',10:'How the study will be tested'}
for r in rows:
 p=r['page']
 if p in newnotes:r.update(chinese=newnotes[p][0],english=newnotes[p][1],title=titles[p])
 notes=f"第{p}页 / Slide {p}: {r['title']}\n\n中文逐字稿\n{r['chinese']}\n\nEnglish Script\n{r['english']}"
 if p in [5,8]:notes+='\n\nInterface concept based on local app.py controls; fictional content, not a live output.'
 if p==4:notes+='\n\nPhoto: AlexHe34 / Wikimedia Commons / CC BY-SA 3.0. https://commons.wikimedia.org/wiki/File:Overhead-lines-railway.JPG'
 (w/f'notes/slide_{p:02}.md').write_text(notes,encoding='utf-8')
(out/'source/content_5min.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 五分钟开题答辩中英文逐字稿（界面可视化版）','','对应 `OCS_Proposal_Defense_EN_5min_SWJTU_Visual.pptx`。15页主讲、5页备份；配时合计300秒，选择一种语言讲述，需试讲校准。所有界面为设计示意，不代表已验证功能或真实标准答案。','']
elapsed=0
for r in rows:
 lines += [f"## 第{r['page']}页：{r['title']}",'',f"预计 {r['seconds']} 秒；累计 {elapsed//60:02}:{elapsed%60:02}" if r['page']<=15 else '备份页，不计入主讲。','','**中文**','',r['chinese'],'','**English**','',r['english'],'']
 elapsed+=r['seconds']
(out/'OCS_Proposal_Defense_CN_EN_Script_5min.md').write_text('\n'.join(lines),encoding='utf-8')
(out/'Modification_Summary.md').write_text('''# 五分钟界面可视化版

- 保留交大模板、接触网场景照片、Contents、4个Part过渡，15页主讲及5页备份。
- 第5页用大尺寸前端示意代替文字比较：选择版本、提问、回答和引用。
- 第8页展示查看原文与高亮证据、版本缺失时拒答两个界面状态，底部保留简化技术流程。
- 第10页用100个可编辑方块表达计划题目划分，配合5组配置和400次计划执行。
- 界面根据本地project/qa_system/app.py的信息组织设计，均明确标注为计划示意。没有声称功能已完成，没有虚构真实标准条款、数值或性能结果。
- 新界面、文档预览、流程和题目图均为可编辑PowerPoint形状及文字，未把整页文字烘焙成图片。
- 中英文讲稿与全部备注同步，参考时长保持300秒，实际需试讲。
''',encoding='utf-8')
print('Authored three visual pages; 20 bilingual notes; planned duration 300 seconds.')
