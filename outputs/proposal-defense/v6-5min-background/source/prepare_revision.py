from pathlib import Path
import json,re
from lxml import etree as E

out=Path(__file__).resolve().parent.parent
w=out/'workspace'
base=out.parent/'v4-sections'
data=json.loads((base/'source/sections_content.json').read_text(encoding='utf-8'))
previous=json.loads((out.parent/'v5-5min/source/content_5min.json').read_text(encoding='utf-8'))
by_source={r['sourcePage']:r for r in previous}
selection=[1,2,3,4,5,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23]
seconds=[10,5,2,45,40,2,30,30,2,45,25,2,20,32,10]
assert sum(seconds)==300
revised={
4:('这张照片展示了铁路上方的接触网场景。围绕接触网部件开展学习和技术文档查询时，常常需要同时查找技术要求、试验方法和适用条件。这些信息可能分散在不同文件里，同一标准也可能存在不同版本。查询的难点因此不只是找到一句相关的话，而是确认它来自哪份文件、哪个版本，是否适用于当前问题。普通大模型即使表达流畅，也不一定能给出可核查的依据。本课题希望把文档检索与生成回答结合，让使用者能够从答案直接回到原文。本系统定位于学习与查询辅助，不用于铁路工程认证或实际运营决策。',
'This photograph shows the overhead-line setting above a railway. When learning about OCS components or consulting technical documents, users may need requirements, test methods, and applicability conditions from different files. A standard may also have several editions. Finding a relevant sentence is therefore only the beginning: users must establish which document and edition it comes from, and whether it applies to their question. A fluent model response does not necessarily provide that evidence. This project will connect retrieval with answer generation so users can follow an answer back to its source. Its scope is learning and consultation, not engineering certification or operational decisions.'),
5:('以这一查询为例，用户问的是某个部件在指定版本下有哪些试验要求。本页仅为示意，不引用真实标准条款或数值。如果模型直接凭已有知识回答，可能引用另一版本，也可能给出没有来源的内容，这就是需要研究的问题。目标系统将先核对文档与版本，再寻找相关证据；能够回答时提供原文位置，版本缺失或证据不足时拒答或澄清。RAG的价值就在于让回答建立在可检查的文档上，而不是只看它说得是否像正确答案。但引入RAG本身不保证可靠，因此还需要后面的对照实验。',
'Consider this query about test requirements for a fitting in a requested edition. It is an illustration, not a quotation of real clauses or values. A model answering from its existing knowledge could use another edition or provide unsupported content. The proposed system will check the document and edition, retrieve evidence, and provide a source location when answering. If the edition is missing or evidence is insufficient, it will refuse or ask for clarification. RAG makes the document basis inspectable rather than relying on a fluent response. However, RAG alone does not guarantee reliability, so controlled experiments are still needed.'),
8:('本研究围绕三个问题展开。RQ1：Hybrid能否比BM25和Dense提高证据召回；RQ2：版本过滤能否减少非指定版本答案；RQ3：Evidence Gate能否减少无依据回答，同时避免过度拒答。对应的是检索、版本控制和证据充分性三个层次。它们是拟验证的问题，不是已经证实的效果，也不涉及训练新的基础模型。',
'The study has three questions. RQ1 asks whether Hybrid improves evidence recall over BM25 and Dense. RQ2 asks whether edition filtering reduces answers from a non-requested edition. RQ3 asks whether an Evidence Gate reduces unsupported answers without excessive refusal. These address retrieval, edition control, and evidence sufficiency. They are questions to test, not established benefits, and the project does not train a new foundation model.'),
9:('技术路线可以概括为先找依据，再组织回答。计划解析许可使用的PDF和DOCX，分块并保存版本与来源位置。提问后限定标准系列和版本，再用BM25、Dense或Hybrid检索。Evidence Gate通过词项覆盖率或原始余弦相似度作启发式筛选；通过后交给DeepSeek生成回答，由Streamlit展示引用。Gate不能证明语义正确，数值、单位和适用条件仍需人工评分验证。',
'The workflow is to find evidence before generating an answer. We will parse licensed PDF and DOCX files, preserving edition metadata and source locations. Queries will be filtered by standard family and edition, then retrieved using BM25, Dense, or Hybrid. An Evidence Gate will screen passages using term coverage or raw cosine similarity. DeepSeek will generate an answer, and Streamlit will display citations. The gate is heuristic, not proof of semantic correctness; human scoring will check values, units, and applicability conditions.'),
15:('最后介绍可行性与计划。','Finally, feasibility and the plan.'),
16:('可行性上，计划采用现有RAG组件，并把范围限定在许可文档查询。主要风险是正式版本不足和Gate误判：前者必要时缩小RQ2范围，后者通过开发集与人工评估报告误接受和误拒答。这里不预设系统已经实现或达到目标。',
'The plan uses established RAG components within a bounded document-consultation task. The main risks are insufficient formal editions and gate errors. We will narrow RQ2 if necessary, and report false acceptance and refusal through development-set calibration and human evaluation. Implementation and target performance remain to be verified.'),
17:('计划在Week 11完成语料准备，Week 16完成集成，Week 17冻结数据、提示词和模型设置，Week 20完成实验分析，Week 24提交。预期成果是问答系统、人工校核基准与实验报告。开发集用于选择Hybrid权重和Gate阈值，正式测试集不用于调参。所有效果都将以冻结配置后的评估为依据，不预先承诺达到目标。',
'The plan is corpus preparation by Week eleven, integration by Week sixteen, a freeze of data, prompts, and model settings in Week seventeen, experiment analysis by Week twenty, and submission in Week twenty-four. Outputs will be a QA system, a manually checked benchmark, and an experimental report. Hybrid weights and gate thresholds will be selected on the development set, not the test set. Performance will be established by evaluation after the configuration freeze, without assuming that targets will be met.')
}
for p in ['source','validation','previews']:(out/p).mkdir(parents=True,exist_ok=True)
(w/'page_plan.json').write_text(json.dumps({'schema':'ppt-master.roundtrip-page-plan.v1','pages':[{'source_slide':s} for s in selection]},indent=2),encoding='utf-8')
ns={'s':'http://www.w3.org/2000/svg'}
def replace_text(tree,old,new):
 for t in tree.xpath('//s:text',namespaces=ns):
  if ''.join(t.itertext())==old:
   spans=[n for n in t.iter() if n.text]
   spans[0].text=new
   for n in spans[1:]:n.text=''
   return
 raise ValueError(old)
rows=[]
for i,s in enumerate(selection,1):
 r=dict(data['slides'][s-1]);r.update(page=i,sourcePage=s,seconds=seconds[i-1] if i<=15 else 0)
 if s in by_source:r.update(chinese=by_source[s]['chinese'],english=by_source[s]['english'])
 if s in revised:r.update(chinese=revised[s][0],english=revised[s][1])
 if s==16:r['title']='Feasibility and key risks'
 if s==15:r['title']='Part 04: Feasibility and Schedule'
 notes=f"第{i}页 / Slide {i}: {r['title']}\n\n中文逐字稿\n{r['chinese']}\n\nEnglish Script\n{r['english']}"
 if s==4:notes+='\n\nPhoto credit: AlexHe34, Wikimedia Commons, CC BY-SA 3.0. https://commons.wikimedia.org/wiki/File:Overhead-lines-railway.JPG'
 (w/f'notes/slide_{s:02}.md').write_text(notes,encoding='utf-8')
 path=w/f'authoring-svg-flat/slide_{s:02}.svg'
 raw=path.read_text(encoding='utf-8')
 if i<=15:raw=re.sub(r'\d{2} / 18',f'{i:02} / 15',raw)
 tree=E.fromstring(raw.encode())
 if s==3:raw=raw.replace('Related work and research gap','Evidence-traceable RAG');tree=E.fromstring(raw.encode())
 if s==15:
  for t in tree.xpath('//s:tspan',namespaces=ns):
   if t.text=='Recorded progress':t.text='Planned feasibility'
 if s==16:
  changes={
   'Preliminary progress and feasibility':'Feasibility and key risks',
   'RECORDED BY 4 NOV 2026':'BOUNDED PROJECT SCOPE',
   'TO BE VERIFIED':'PLANNED VALIDATION',
   'Three-document BM25 prototype':'Use established RAG components',
   '503 text chunks, 0 vectors':'Permitted PDF / DOCX documents',
   'DeepSeek checks with synthetic evidence':'Learning and consultation only',
   'Live Embedding access and model identity':'Confirm Embedding access',
   'Dense / Hybrid effectiveness':'Compare retrieval configurations',
   'Formal benchmark and manual scoring':'Human-check evidence support',
  }
  source_text=next(''.join(t.itertext()) for t in tree.xpath('//s:text',namespaces=ns) if ''.join(t.itertext()).startswith('Sources: Week 9'))
  changes[source_text]='Source: Proposal, section 4.6. Planned approach; no performance claim.'
  for old,new in changes.items():replace_text(tree,old,new)
 if s in [3,15,16]:path.write_bytes(E.tostring(tree,encoding='utf-8'))
 else:path.write_text(raw,encoding='utf-8')
 rows.append(r)
(out/'source/content_5min.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 五分钟开题答辩中英文对照逐字稿（背景加强版）','','对应 `OCS_Proposal_Defense_EN_5min_SWJTU_Background.pptx`。第1–15页主讲，第16–20页备份。配时300秒；中文或英文择一讲述，实际时长需试讲。第4–5页背景与动机共85秒。','']
elapsed=0
for r in rows:
 timing=f"预计 {r['seconds']} 秒；累计 {elapsed//60:02}:{elapsed%60:02}"
 elapsed+=r['seconds']
 lines += [f"## 第{r['page']}页：{r['title']}",'',timing if r['page']<=15 else '备份页，不计入主讲时长。','','**中文**','',r['chinese'],'','**English**','',r['english'],'']
(out/'OCS_Proposal_Defense_CN_EN_Script_5min.md').write_text('\n'.join(lines),encoding='utf-8')
(out/'Modification_Summary.md').write_text('''# 五分钟背景加强版

- 保留交大模板、Contents、四个独立Part过渡和5页备份；主讲15页。
- 加回v4第4页接触网场景照片及原图署名。背景与动机安排85秒，原版27秒。
- 主讲方法仅保留三个RQ和整体架构，共60秒，原版100秒；RQ2/RQ3独立案例页不再主讲。
- Preliminary progress改为Feasibility and key risks；去除已完成原型、503块、0向量、接口检查等叙述，采用计划表述。未声称项目事实上没有开始，也未更改既有进度记录。
- 可行性讲述由38秒缩为20秒。总配时仍300秒，需试讲校准。
- 三个RQ、100题划分、5组配置、400次计划执行及目标值均保留，参数与评分细节留在备份。
- 中英文备注与独立逐字稿同步更新。所有主讲页采用拟开展研究的语气，无已验证性能宣称。
''',encoding='utf-8')
print('Prepared 20 slides; 85s background, 60s methods, 20s feasibility; 300s total.')
