from pathlib import Path
import json,re,hashlib

out=Path(__file__).resolve().parent.parent
w=out/'workspace'
old=out.parent/'v4-sections'
data=json.loads((old/'source/sections_content.json').read_text(encoding='utf-8'))
selection=[1,2,3,5,7,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23]
seconds=[10,6,3,27,3,36,38,26,3,42,28,3,38,28,9]
pairs=[
('各位老师好，我是黄俊凯，指导老师是黄德青教授。我的课题是基于大模型的接触网领域智能问答系统研究。下面用五分钟介绍研究方案。','Good morning. I am Junkai Huang, supervised by Professor Deqing Huang. My project studies a large-model-based question-answering system for the Overhead Contact System field.'),
('汇报分为背景动机、研究方法、实验评价，以及可行性与进度四部分。','I will cover motivation, research methods, evaluation, and feasibility.'),
('首先介绍研究动机。','First, the motivation.'),
('接触网技术文档查询不仅要找到答案，还要核对标准版本并追溯原文。本页是示意案例，不代表真实标准条款。用户指定某一版本时，普通模型可能混用版本，也可能在没有证据时作答。RAG把文档检索接入生成过程，目标是返回指定版本的证据和位置；证据不足时明确拒答。','Standards consultation requires both an answer and its source edition. This is an illustrative example, not an actual standard clause. A model may mix editions or answer without evidence. RAG retrieves documents before generation. Our goal is to provide evidence from the requested edition, locate its source, and refuse when evidence is insufficient.'),
('下面介绍研究问题与方法。','Next, the research questions and methods.'),
('本项目不训练新的大模型，而是研究证据可追溯的RAG系统，服务技术文档学习和查询。三个问题分别是：RQ1，Hybrid是否比BM25和Dense提高证据召回；RQ2，版本过滤能否减少非指定版本答案；RQ3，Evidence Gate能否减少无依据回答，同时避免过度拒答。它们都需要通过实验验证，目前不是结论。','This project develops an evidence-traceable RAG system for document learning and consultation; it does not train a new foundation model. RQ1 asks whether Hybrid improves evidence recall over BM25 and Dense. RQ2 asks whether edition filtering reduces answers from a non-requested edition. RQ3 asks whether an Evidence Gate reduces unsupported answers without excessive refusal. These are research questions, not established conclusions.'),
('整体流程从许可使用的PDF和DOCX开始。解析分块时保存标准编号、版本和来源位置，再建立关键词与向量索引。用户提问后，先按标准系列和指定版本限定范围，再检索证据。BM25匹配关键词，Dense匹配语义，Hybrid组合归一化得分。证据通过Gate后交给DeepSeek组织回答，由Streamlit展示引用和原文位置；不通过则拒答。','The pipeline starts with licensed PDF and DOCX files. Parsing and chunking preserve the standard identifier, edition, and source location. We build keyword and vector indexes. A query is filtered by standard family and requested edition before retrieval. BM25 matches terms; Dense captures semantic similarity; Hybrid combines normalized scores. Evidence passing the gate is sent to DeepSeek, and Streamlit displays the answer with citations and source locations. Otherwise, the system refuses.'),
('这两个检查分别对应RQ2和RQ3。版本检查依据文档元数据，不让非指定版本进入回答证据。Evidence Gate使用词项覆盖率或原始余弦相似度阈值。它只是启发式筛选，不证明证据语义正确，也不能宣称消除幻觉。证据是否支持答案，以及数值、单位和适用条件是否正确，仍由人工评分。','Edition checks use document metadata to exclude evidence from an unrequested edition. The Evidence Gate uses term coverage or raw cosine-similarity thresholds. These are heuristic signals, not proof of semantic correctness or a guarantee against hallucination. Human scoring checks whether evidence supports the answer, including numerical values, units, and applicability conditions.'),
('下面说明实验评价。','Next, the evaluation plan.'),
('计划收集二十到三十份可用文档，尽可能覆盖两个标准系列，每个系列两个正式版本。人工校核一百道题：二十道开发题，其中十六道可回答、四道不可回答；八十道测试题，其中六十四道可回答、十六道不可回答。五组配置是B1 BM25、B2 Dense、B3 Hybrid，以及关闭版本检查的A1和关闭Gate的A2。A1仍保留标准系列过滤；A2仍保留提示词、引用校验和错误处理。测试前冻结数据和设置，计划执行八十乘五，共四百次。','We plan to collect twenty to thirty usable documents, ideally two standard families with two formal editions each. One hundred manually checked questions are split into twenty development questions, sixteen answerable and four unanswerable, and eighty test questions, sixty-four answerable and sixteen unanswerable. We compare B1 BM25, B2 Dense, B3 Hybrid, A1 without edition checks, and A2 without the gate. A1 retains family filtering; A2 retains prompts, citation validation, and error handling. Data and settings are frozen before the planned four hundred test runs.'),
('评价同时检查检索和回答。Recall@5看前五条是否召回证据；Answer Correctness和Citation Support由人工判断；Wrong-edition Rate检查版本错误。Refusal Recall和False Refusal分别衡量该拒答时是否拒答，以及可回答时是否误拒。页面中的零点八、零点九等数值都是计划目标，没有现有测试结果支撑。','Recall at five evaluates evidence retrieval. Human scoring evaluates answer correctness and citation support. Wrong-edition rate measures edition errors. Refusal recall measures appropriate refusal, while false refusal measures rejected answerable questions. Values such as point eight and point nine are planned targets, not measured results.'),
('最后介绍进度与可行性。','Finally, progress and feasibility.'),
('根据十一月四日已记录快照，已有三文档BM25原型，记录五百零三个文本块、零个向量，并完成合成证据下的DeepSeek接口检查。实际Embedding访问、Dense和Hybrid效果，以及正式基准测试尚未确认完成。两个主要风险是正式版本不足，以及Gate误接受或误拒绝。前者必要时缩小RQ2结论范围；后者通过开发集选阈值、人工核查和消融实验评估，不能承诺消除。','The recorded November fourth snapshot contains a three-document BM25 prototype, five hundred and three chunks, and zero vectors. DeepSeek was checked using synthetic evidence. Live embedding access, Dense and Hybrid performance, and the formal benchmark remain unverified. The main risks are insufficient formal editions and incorrect gate acceptance or refusal. We will narrow the scope of RQ2 if editions are insufficient, and evaluate gate errors through development-set calibration, human review, and ablation experiments.'),
('进度安排按正式开题报告推进：Week 11完成语料准备，Week 16完成系统集成，Week 17冻结评估设置，Week 20完成实验分析，Week 24完成提交。预期交付可编辑维护的问答原型、人工校核基准和实验报告。系统用于学习查询，不用于铁路工程认证或实际运营决策。','The proposal milestones are corpus preparation by Week eleven, integration by Week sixteen, evaluation freeze in Week seventeen, experiment analysis by Week twenty, and submission in Week twenty-four. Outputs are a maintainable prototype, a manually checked benchmark, and an experimental report. The system supports learning and consultation, not engineering certification or operational decisions.'),
('本研究的核心是让接触网文档问答有版本依据、有可追溯证据，并知道何时拒答。感谢各位老师，请批评指正。','The aim is traceable evidence, explicit edition control, and refusal when evidence is insufficient. Thank you. I welcome your questions.')
]
assert sum(seconds)==300
(out/'source').mkdir(exist_ok=True,parents=True)
(out/'validation').mkdir(exist_ok=True)
(out/'previews').mkdir(exist_ok=True)
plan={'schema':'ppt-master.roundtrip-page-plan.v1','pages':[{'source_slide':s} for s in selection]}
(w/'page_plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
rows=[]
for i,s in enumerate(selection,1):
 r=dict(data['slides'][s-1]);r.update(page=i,sourcePage=s)
 if i<=15:r.update(seconds=seconds[i-1],chinese=pairs[i-1][0],english=pairs[i-1][1])
 else:r['seconds']=0
 notes=f"第{i}页 / Slide {i}: {r['title']}\n\n中文逐字稿\n{r['chinese']}\n\nEnglish Script\n{r['english']}"
 (w/f'notes/slide_{s:02}.md').write_text(notes,encoding='utf-8')
 svg=w/f'authoring-svg-flat/slide_{s:02}.svg'
 t=svg.read_text(encoding='utf-8')
 if i<=15:t=re.sub(r'\d{2} / 18',f'{i:02} / 15',t)
 if s==3:t=t.replace('Related work and research gap','Evidence-traceable RAG')
 svg.write_text(t,encoding='utf-8')
 rows.append(r)
(out/'source/content_5min.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 五分钟开题答辩中英文对照逐字稿','','对应 `OCS_Proposal_Defense_EN_5min_SWJTU.pptx`。第1–15页主讲，第16–20页备份。参考配时300秒；选择中文或英文讲述，不连续朗读两种语言。需通过试讲校准实际时长。','']
elapsed=0
for r in rows:
 timing=f"预计 {r['seconds']} 秒；累计 {elapsed//60:02}:{elapsed%60:02}"
 elapsed+=r['seconds']
 lines += [f"## 第{r['page']}页：{r['title']}",'',timing if r['page']<=15 else '备份页，不计入主讲时长。','','**中文**','',r['chinese'],'','**English**','',r['english'],'']
(out/'OCS_Proposal_Defense_CN_EN_Script_5min.md').write_text('\n'.join(lines),encoding='utf-8')
mapping={s:i for i,s in enumerate(selection,1)}
qa=(old/'OCS_Defense_QA_CN.md').read_text(encoding='utf-8')
qa=re.sub(r'可跳转：PPT 第[^\n]+','请参照本版对应主题页或第16–20页备份。',qa)
(out/'OCS_Defense_QA_CN.md').write_text(qa,encoding='utf-8')
(out/'Modification_Summary.md').write_text('''# 五分钟版本修改与验证记录

- 来源：v4交大模板版。原文件保持不变。
- 主讲15页：封面、目录、4页Part过渡、8页内容及结束页；另5页备份。
- 原背景、相关工作、Hybrid公式三页不再独立主讲；动机、方法在短稿中说明，参考文献和公式保留备份。
- 保留正式题目、身份信息、三个RQ、样本划分、五组配置、计划目标及2026-11-04进度边界。未宣称已完成正式评估。
- 每页备注及独立讲稿提供中英文对照，主讲配时合计300秒。实际语速须试讲确认。
- 使用ppt-master Edit Native PPTX原生往返流程。导入器对渐变和转场有预览告警；未编辑的原生对象由源包恢复，最终通过PowerPoint渲染检查。
- 目录与四个独立Part过渡页均保留。无配音或新增动画。
''',encoding='utf-8')
print('Prepared 20 slides, 15 main + 5 backup, 300 seconds.')
