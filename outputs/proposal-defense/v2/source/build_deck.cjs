/* Rebuild v2 using editable PowerPoint text, shapes, connectors and tables.
 * Usage: node build_deck.cjs [candidate.pptx]
 * Dependency: pptxgenjs 4.0.1. No whole-slide image rendering is used.
 */
const fs=require('fs'), path=require('path');
let pptxgen;
try {pptxgen=require('pptxgenjs');}
catch(e){pptxgen=require(process.env.PPTXGENJS_MODULE || 'C:/Users/44282/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs');}
const pptx=new pptxgen();
pptx.layout='LAYOUT_WIDE';
pptx.author='Junkai Huang'; pptx.subject='SWJTU-Leeds Joint School undergraduate project proposal defense';
pptx.title='A Study on a Large-Model-Based Intelligent Question-Answering System for the Overhead Contact System Field';
pptx.company='Southwest Jiaotong University - Leeds Joint School';
pptx.lang='en-GB'; pptx.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'en-GB'};
const C={navy:'183E69',blue:'245A8A',ink:'23364B',muted:'586D80',teal:'247B79',amber:'A56825',line:'D7E1EA',pale:'F2F6FA',tealPale:'EAF4F1',amberPale:'FBF4E9',white:'FFFFFF'};
const W=13.333333,H=7.5;
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'content.json'),'utf8'));
const assets=path.join(__dirname,'assets');
const geometry=[];
let sl, pg;
function text(str,x,y,w,h,size=20,bold=false,color=C.ink,extra={}){
  sl.addText(str,{x,y,w,h,fontFace:'Arial',fontSize:size,bold,color,margin:0,breakLine:false,
    valign:'mid',paraSpaceAfterPt:0,charSpacing:0,transparency:0,...extra});
  geometry.push({page:pg,kind:'text',text:str,x,y,w,h,size,...extra});
}
function rect(x,y,w,h,fill=C.pale,line=C.line,radius=false){
 sl.addShape(radius?pptx.ShapeType.roundRect:pptx.ShapeType.rect,{x,y,w,h,rectRadius:0.08,
   fill:{color:fill},line:{color:line,width:.8},radius:.08});
 geometry.push({page:pg,kind:'container',x,y,w,h});
}
function line(x1,y1,x2,y2,color=C.line,width=1.1,arrow=false){
 sl.addShape(pptx.ShapeType.line,{x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(x2-x1),h:Math.abs(y2-y1),flipH:x2<x1,flipV:y2<y1,line:{color,width,...(arrow?{endArrowType:'triangle'}:{})},rotate:0});
}
function node(label,sub,x,y,w=2.5,h=.95,color=C.blue){
 rect(x,y,w,h,C.pale,C.line);
 if(sub){text(label,x+.12,y+.11,w-.24,.35,19,true,color,{align:'center'});text(sub,x+.12,y+.47,w-.24,h-.52,16,false,C.ink,{align:'center'});}
 else text(label,x+.12,y+.12,w-.24,h-.24,19,true,color,{align:'center'});
}
function note(i){const d=data[i-1];sl.addNotes(`第${i}页 ${d.title}\n${i<=13?'主讲，预计 '+d.seconds+' 秒':'备份页，不计入主讲时长'}\n\n中文逐字稿：\n${d.script}\n\n事实与素材来源：\n${d.source}\n正式报告：${REPORT}\n${i===2?'照片许可及作者详见 source/asset_credits.json。':''}`);}
const REPORT='开题材料/交大开题报告/3.2023115799_黄俊凯_开题报告.pdf';
function page(i,title,category,source='Proposal §§1–4'){
 pg=i;sl=pptx.addSlide();sl.background={color:C.white};
 line(.55,.31,1.15,.31,C.teal,4);
 text(category.toUpperCase(),1.3,.16,10,.3,11,true,C.muted);
 text(title,.55,.61,12.2,.62,30,true,C.navy);
 line(.55,7.0,12.78,7.0,C.line,.7);
 text(source,.55,7.10,11.3,.18,9.5,false,C.muted);
 text(i<=13?`${String(i).padStart(2,'0')} / 13`:`B${i-13} / 5`,12.05,7.06,.73,.28,10,false,C.muted,{align:'right'});
 note(i);return sl;
}
function takeaway(str,y=6.43,color=C.navy,size=21){text(str,.65,y,12,.43,size,true,color);}
function pair(head,body,x,y,w=5.75,color=C.blue){text(head,x,y,w,.4,22,true,color);text(body,x,y+.55,w,.78,20);}
function smallTable(rows,x,y,widths,rowH,font=18){
 const colW=widths;
 sl.addTable(rows,{x,y,w:widths.reduce((a,b)=>a+b,0),h:rows.length*rowH,colW,
   rowH,fontFace:'Arial',fontSize:font,color:C.ink,margin:[4,7,4,7],valign:'middle',
   border:{type:'solid',pt:.6,color:C.line},fill:C.white,
   autoPage:false,verbose:false,
   bold:false});
 // Header cells explicitly styled without changing data cells.
}
function tableRows(arr){return arr.map((r,i)=>r.map(t=>({text:t,options:i===0?{bold:true,color:C.white,fill:C.navy}:{fill:i%2?C.pale:C.white}})));}

// 01: title. Original identity asset, no campus photograph on content pages.
pg=1;sl=pptx.addSlide();sl.background={color:C.white};
rect(10.2,0,W-10.2,H,C.navy,C.navy);
sl.addImage({path:path.join(assets,'swjtu-logo.png'),x:10.58,y:.62,w:2.35,h:.663});
text('SWJTU-LEEDS JOINT SCHOOL',.65,.65,9,.36,18,true,C.blue);
text('Undergraduate Project Proposal Defense',.65,1.13,9,.45,22,false,C.muted);
text('A Study on a Large-Model-Based Intelligent\nQuestion-Answering System for the\nOverhead Contact System Field',.65,2.03,9.1,2.5,31,true,C.navy,{breakLine:false});
line(.65,4.77,9.35,4.77,C.teal,2);
text('Junkai Huang',.65,5.13,8,.43,24,true,C.navy);
text('Student ID: 2023115799\nSupervisor: Prof. Deqing Huang',.65,5.77,8.7,.82,21,false,C.ink);
text('EVIDENCE-BASED\nDOCUMENT CONSULTATION',10.55,4.7,2.4,1.3,18,true,C.white);
text('Electronic and Electrical Engineering',.65,7.0,9,.25,14,false,C.muted);note(1);

// 02: contextual photograph and concrete document-use needs.
page(2,'Standards consultation needs traceable answers','Why this project','Proposal pp.1–2. Photo: AlexHe34, Wikimedia Commons, CC BY-SA 3.0');
sl.addImage({path:path.join(assets,'overhead-lines-railway.jpg'),x:.65,y:1.48,w:3.84,h:5.12});
text('Overhead-line context',.65,6.63,3.84,.22,11,false,C.muted);
pair('Find the requirement','Technical requirements and test methods\nmay appear in different documents.',5.1,1.57,7.1);
pair('Check the edition','The answer must preserve the requested\nedition, units and applicable conditions.',5.1,3.08,7.1);
text('Candidate documents in the proposal',5.1,4.65,7.1,.35,20,true,C.blue);
text('TB/T 2073-2020: fittings requirements\nTB/T 2074-2020: test methods',5.1,5.14,7.1,.8,20);
text('For learning and consultation. Engineering approval and operational decisions remain outside scope.',5.1,6.2,7.1,.55,17,true,C.navy);

// 03: illustrative question. No actual clause/value/year is fabricated.
page(3,'An edition-specific query needs more than a fluent answer','Motivating example','Design illustration only. Fictional Standard S, editions A/B and fitting X. No real clause or value.');
rect(.65,1.48,12.05,.85,C.pale,C.line);
text('Question',.85,1.63,1.5,.28,18,true,C.blue);
text('Which test requirements apply to fitting X in edition A?',2.4,1.6,10,.39,23,true);
text('UNCHECKED ANSWER: POSSIBLE FAILURE',.65,2.75,5.65,.38,17,true,C.amber);
text('An edition-B requirement appears\nwithout a traceable source.',.65,3.35,5.55,1.0,24);
text('Illustrative failure scenario.\nNot an observed model output.',.65,4.66,5.4,.62,17,false,C.muted);
line(6.55,2.75,6.55,6.2,C.line,1);
text('TARGET SYSTEM: CHECKED RESPONSE PATH',7.0,2.75,5.7,.38,17,true,C.teal);
pair('Edition available + sufficient evidence','Answer with the document edition\nand PDF page / DOCX location.',7.0,3.35,5.6,C.teal);
pair('Missing edition / weak evidence','Refuse explicitly. Clarify an ambiguous edition.',7.0,5.04,5.6,C.teal);

// 04: literature, concise and sourced from the report.
page(4,'Existing methods leave three questions to test','Related work and research gap','Proposal pp.3–4, references [1]–[7]. Full bibliography: backup B1.');
const lit=[['RAG [1]','Documents supply context\nfor model generation.'],['BM25 / Dense [2,3]','Exact terms and paraphrases\nfavour different signals.'],['Evidence checks [5,6]','Relevant context alone\ncannot prove correctness.']];
lit.forEach((v,j)=>{let x=.65+j*4.15;text(v[0],x,1.65,3.8,.43,23,true,C.blue);text(v[1],x,2.32,3.8,1.14,22);line(x,3.75,x+3.7,3.75,C.line,1);});
text('Project focus',.65,4.22,12,.38,23,true,C.navy);
text('A bounded study of Chinese OCS standards:\nretrieval recall, edition compatibility and evidence sufficiency.',.65,4.86,12,1.05,27,true,C.navy);
text('Rule-based follow-ups draw on [4]. Chinese retrieval context draws on [7].\nNo domain performance claim follows from the cited papers.',.65,6.15,12,.57,17,false,C.muted);

// 05: exact RQs, no conclusions.
page(5,'Three research questions map to three testable modules','Research aim','Proposal pp.4–5, §3. RQs are hypotheses to evaluate.');
text('Aim: evidence-based QA for Chinese OCS standards',.65,1.48,12,.6,25,true,C.navy);
const rqs=[['RQ1','Retrieval','Does Hybrid retrieval improve evidence recall compared\nwith BM25-only and Dense-only retrieval?','BM25 / Dense / Hybrid',C.blue],['RQ2','Standard editions','Does edition filtering reduce answers using\na non-requested edition?','Identifier + edition filtering',C.amber],['RQ3','Evidence sufficiency','Does an Evidence Gate reduce unsupported answers\nwithout excessive refusal?','Evidence Gate + refusal',C.teal]];
rqs.forEach((r,j)=>{const y=2.42+j*1.32;text(r[0],.65,y,.85,.45,26,true,r[4]);text(r[1],1.67,y,7.0,.38,22,true,r[4]);text(r[2],1.67,y+.43,7.9,.68,20);line(9.78,y+.55,10.19,y+.55,r[4],1.2,true);text(r[3],10.45,y+.15,2.23,.78,18,true,r[4]);});

// 06: fully editable architecture. All boxes and connectors are native.
page(6,'System architecture','How the system will work','Proposal pp.5–7, §§4.1–4.4. Planned workflow. Only permitted text may leave the device.');
node('PDF / DOCX','Permitted documents',.65,1.55);
node('Parse + chunk','Units + locations',3.68,1.55);
node('Metadata','Identifier, year, hash',6.71,1.55);
node('SQLite + indexes','Eligible chunks',9.74,1.55);
for(let x of [3.15,6.18,9.21])line(x,2.02,x+.53,2.02,C.blue,1.3,true);
line(10.99,2.5,10.99,2.88,C.blue,1.2);line(10.99,2.88,4.93,2.88,C.blue,1.2);line(4.93,2.88,4.93,3.25,C.blue,1.2,true);
node('Query','Family + edition',.65,3.25,2.5,1.05);
text('Rule-based follow-ups',.65,2.85,2.5,.27,14,false,C.muted,{align:'center'});
node('Retrieve','3 retrieval modes',3.68,3.25,2.5,1.05);
node('Evidence Gate','Coverage OR raw cosine',6.71,3.25,2.5,1.05,C.teal);
node('DeepSeek','Citation / excerpt checks',9.74,3.25,2.5,1.05);
for(let x of [3.15,6.18,9.21])line(x,3.78,x+.53,3.78,C.blue,1.3,true);
text('Pass',9.21,3.31,.53,.25,12,true,C.teal,{align:'center'});
node('Refuse / clarify','Missing edition or weak evidence',6.71,5.4,2.5,1.05,C.amber);
node('Streamlit','Answer + source locations',9.74,5.4,2.5,1.05,C.teal);
line(7.96,4.3,7.96,5.4,C.amber,1.3,true);text('Below thresholds',8.07,4.65,1.7,.55,14,false,C.amber);
line(10.99,4.3,10.99,5.4,C.blue,1.3,true);
line(9.21,5.92,9.74,5.92,C.amber,1.3,true);
line(1.9,4.3,1.9,5.92,C.amber,1.3);line(1.9,5.92,6.71,5.92,C.amber,1.3,true);
text('Missing / ambiguous edition',2.1,5.33,4.25,.37,17,false,C.amber);
text('PDF page / DOCX location',9.3,6.59,3.45,.32,16,true,C.teal,{align:'right'});

// 07: conceptual comparison without invented performance data.
page(7,'RQ1: exact matching, semantic matching and fusion','Hybrid retrieval','Proposal p.6, §4.2. Conceptual comparison, not measured retrieval results.');
const methods=[['BM25','Exact terms\nStandard identifiers','Lexical score B',C.blue],['Dense','Different wording\nSemantic similarity','Dense score D',C.teal],['Hybrid','Combine the two signals\nTest complementarity','(1 - w)B + wD',C.navy]];
methods.forEach((v,j)=>{const x=.65+j*4.15;text(v[0],x,1.72,3.75,.5,29,true,v[3]);text(v[1],x,2.54,3.75,1.17,24);line(x,4.02,x+3.75,4.02,C.line,1.1);text(v[2],x,4.35,3.75,.55,j===2?26:23,true,v[3]);});
takeaway('Shared chunks and questions. Compare pre-gate Recall@5 at Top-K = 5.',5.59,C.navy,22);
text('B and D use the proposal\'s normalisation rule. Select w on development data only.\nHybrid may reorder useful evidence incorrectly, so improvement remains to be tested.',.65,6.18,12,.61,18,false,C.muted);

// 08: parallel schematic safeguards.
page(8,'RQ2 and RQ3 address different failure paths','Edition compatibility and evidence sufficiency','Proposal p.6, §§4.3–4.4. Illustrative scenarios, not standard clauses or observed outputs.');
text('RQ2  Standard editions',.65,1.5,5.7,.42,25,true,C.amber);
text('RQ3  Evidence sufficiency',7.0,1.5,5.7,.42,25,true,C.teal);
node('Request edition A','Only edition B is available',.65,2.25,5.65,.98,C.amber);
node('Candidate passages','Below both evidence thresholds',7.0,2.25,5.65,.98,C.teal);
line(3.48,3.23,3.48,3.8,C.amber,1.3,true);line(9.83,3.23,9.83,3.8,C.teal,1.3,true);
node('Explicit refusal','No silent substitution of edition B',.65,3.8,5.65,1.0,C.amber);
node('Explicit refusal','Avoid generating from weak context',7.0,3.8,5.65,1.0,C.teal);
text('Ambiguous editions require clarification.\nFamily filtering remains active in A1.',.65,5.25,5.65,.85,20);
text('High scores can still lack semantic support.\nHuman scoring checks facts and conditions.',7.0,5.25,5.65,.85,20);
takeaway('Measure both unsupported answers and false refusals',6.43,C.navy,23);

// 09: clear benchmark split and five configurations, not a dense matrix.
page(9,'A fixed benchmark supports five controlled comparisons','How the study will be evaluated','Proposal pp.4–7, O3–O4 and §4.5. All counts are planned. Strict ablation definitions: backup B4.');
text('100 manually checked questions',.65,1.5,12,.5,28,true,C.navy);
pair('20 development','16 answerable + 4 unanswerable\nSelect weights and thresholds',.65,2.32,5.5,C.blue);
pair('80 fixed test','64 answerable + 16 unanswerable\nEvaluate once under frozen settings',7.0,2.32,5.5,C.teal);
line(.65,3.95,12.65,3.95,C.line,1);
const configs=[['B1','BM25'],['B2','Dense'],['B3','Hybrid'],['A1','Hybrid\nNo edition checks'],['A2','Hybrid\nGate off']];
configs.forEach((r,j)=>{let x=.65+j*2.44;text(r[0],x,4.3,2.2,.38,24,true,j<3?C.blue:C.amber);text(r[1],x,4.84,2.18,.87,19);});
text('A1 retains family filtering. A2 retains prompts, citation checks and error handling.',.65,5.9,12,.42,17,true,C.muted);
takeaway('80 × 5 = 400 main test executions after data and configuration freeze',6.47,C.navy,22);

// 10: definitions are separated from targets. No results chart.
page(10,'Evaluation measures useful answers and justified refusal','Metrics and planned targets','Proposal pp.6–7, §4.5. Counts, coverage, paired differences, uncertainty and failures will be reported.');
const metrics=[
 ['Recall@5','≥ 0.80','64 answerable items, pre-gate rankings',.65,1.58],
 ['Answer Correctness','≥ 0.80','Fully correct answers / 64',.65,3.13],
 ['Citation Support','≥ 0.90','Supported cited claims / all cited claims',.65,4.68],
 ['Wrong-edition Rate','B3 vs A1','All unambiguous edition requests, including missing editions',7.0,1.58],
 ['Refusal Recall','≥ 0.80','Justified non-answering / 16',7.0,3.13],
 ['False Refusal','≤ 0.10','Refusals or unnecessary clarifications / 64',7.0,4.68]];
metrics.forEach(([name,target,def,x,y])=>{text(name,x,y,4.15,.4,22,true,C.blue);text(target,x+4.25,y,1.4,.4,target==='B3 vs A1'?18:24,true,C.teal,{align:'right'});text(def,x,y+.58,5.65,.65,18);line(x,y+1.36,x+5.65,y+1.36,C.line,.7);});
text('Planned targets only. Formal test results are pending.',.65,6.45,12,.36,22,true,C.navy);

// 11: status is explicitly bounded by the dated record.
page(11,'Preliminary progress supports limited feasibility','Recorded progress and remaining risks','Sources: Week 9 evidence E09-03/E09-04, 4 Nov 2026. Proposal §4.6. Historical snapshot only.');
text('RECORDED BY 4 NOV 2026',.65,1.57,5.7,.34,17,true,C.teal);
text('TO BE VERIFIED',7.0,1.57,5.7,.34,17,true,C.amber);
text('Three-document BM25 prototype\n503 text chunks, 0 vectors\nDeepSeek checks with synthetic evidence',.65,2.18,5.65,1.8,22,false,C.ink,{paraSpaceAfterPt:14});
text('Live Embedding access and model identity\nDense / Hybrid effectiveness\nFormal benchmark and manual scoring',7.0,2.18,5.65,1.8,22,false,C.ink,{paraSpaceAfterPt:14});
line(.65,4.34,12.65,4.34,C.line,1);
pair('Risk 1: usable edition pairs','Seek permitted alternatives.\nLimit RQ2 to available formal editions.',.65,4.75,5.65,C.amber);
pair('Risk 2: heuristic evidence signals','Heuristics can accept unsupported evidence.\nReport errors and false refusals.',7.0,4.75,5.65,C.amber);

// 12: editable planning chart with milestone labels, no completed-task encoding.
page(12,'Milestones connect implementation to controlled evaluation','Planned schedule and outputs','Proposal p.8 and task CSV. Planning weeks, not completed work or a confirmed institutional calendar.');
const gx=3.55,gy=2.04,gw=9.08,cw=gw/16;
text('Planned task',.65,1.49,2.7,.3,17,true,C.muted);
[9,11,13,16,17,18,20,21,24].forEach(w=>text('W'+w,gx+(w-9)*cw+.01,1.46,.54,.35,15,true,C.muted,{align:'center'}));
const tasks=[['Corpus + baseline',9,11],['Benchmark + checks',12,16],['Integration',16,16],['Configuration freeze',17,17],['Evaluation',18,20],['Report + video',20,21],['Final checks / submit',24,24]];
rect(gx+(22-9)*cw,1.92,2*cw,3.62,'F3F3F3','F3F3F3');
tasks.forEach(([label,a,b],j)=>{let y=gy+j*.48;text(label,.65,y-.04,2.8,.4,18,false,C.ink);line(gx,y+.39,gx+gw,y+.39,C.line,.5);rect(gx+(a-9)*cw+.06,y+.04,(b-a+1)*cw-.12,.22,j===4?C.teal:C.blue,j===4?C.teal:C.blue);});
text('M2 W11     M3 W16     M4 W17     M5 W20     M7 W24',.65,5.62,12,.36,19,true,C.navy);
text('Expected outputs',.65,6.13,2.6,.35,20,true,C.blue);
text('QA system',3.55,6.13,1.8,.4,19,true,C.ink);
text('Checked benchmark',5.67,6.13,3.15,.4,19,true,C.ink);
text('Experiment report',9.12,6.13,3.5,.4,19,true,C.ink);
text('W18 Symposium. W22–23 planned break. Budget: 400 hours and GBP 50.',.65,6.64,12,.25,15,false,C.muted);

// 13: clean conclusion and Q&A.
page(13,'Traceable evidence for standards consultation','Conclusion and Q&A','Expected research contribution. No performance improvement is claimed before controlled evaluation.');
text('Traceable answers to standards queries',.65,2.0,12,1.0,34,true,C.navy);
text('Retrieve relevant evidence\nRespect the requested edition\nRefuse when support is insufficient',.65,3.25,10.5,1.75,27,false,C.ink,{paraSpaceAfterPt:15});
text('Thank you. Questions and discussion.',.65,6.0,12,.54,27,true,C.teal);

// B1 (14): complete references from the supplied report.
page(14,'Full references','Backup B1','References reproduced from the supplied formal report, p.9. No new literature performance claims.');
const refs=[
'[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” Advances in Neural Information Processing Systems, vol.33, pp.9459–9474, 2020.',
'[2] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Foundations and Trends in Information Retrieval, vol.3, no.4, pp.333–389, 2009. doi: 10.1561/1500000019.',
'[3] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” EMNLP, pp.6769–6781, 2020. doi: 10.18653/v1/2020.emnlp-main.550.',
'[4] X. Ma, Y. Gong, P. He, H. Zhao, and N. Duan, “Query Rewriting in Retrieval-Augmented Large Language Models,” EMNLP, pp.5303–5315, 2023. doi: 10.18653/v1/2023.emnlp-main.322.',
'[5] F. Shi et al., “Large Language Models Can Be Easily Distracted by Irrelevant Context,” ICML, PMLR, vol.202, pp.31210–31227, 2023.',
'[6] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” EACL: System Demonstrations, pp.150–158, 2024. doi: 10.18653/v1/2024.eacl-demo.16.',
'[7] Z. Feng, K. Zhu, W. Ma, L. Huang, B. Qin, T. Liu, and X. Feng, “Enhancing Large Language Models with Retrieval-Augmented Techniques: Trends, Challenges, and Prospects,” 23rd Chinese National Conference on Computational Linguistics (Vol.2: Frontier Forum), pp.151–168, 2024 (in Chinese). https://aclanthology.org/2024.ccl-2.9/'];
refs.forEach((r,j)=>text(r,.65,1.47+j*.74,12,j===6?.76:.65,14.3,false,C.ink));

// B2 (15): exact scoring and selection contract.
page(15,'Hybrid scoring and development-only selection','Backup B2','Proposal p.6, §4.2. Top-K = 5. No parameter selection on the test set.');
text('S(q, c) = (1 - w)B(q, c) + wD(q, c)',.65,1.55,12,.67,30,true,C.navy);
pair('Per-query normalisation','Min-max normalise BM25 and cosine scores\nover eligible chunks for each query.',.65,2.65,5.65,C.blue);
pair('Constant-score rule','Constant positive scores map to 1.\nOther constant scores map to 0.',7.0,2.65,5.65,C.blue);
text('w ∈ {0.25, 0.50, 0.75}',.65,4.33,12,.52,27,true,C.teal);
text('Select by development Recall@5, then MRR@5. Ties favour 0.50.',.65,5.1,12,.63,23);
text('Freeze Chinese tokenisation, domain dictionary, stopwords, chunking,\ncorpus, models, prompts, thresholds and weight before testing.',.65,6.03,12,.72,19,false,C.muted);

// B3 (16): gate with thresholds intentionally unspecified.
page(16,'Evidence Gate signals and semantic assessment','Backup B3','Proposal pp.6–7, §§4.4–4.5. Numerical thresholds remain to be selected on development data.');
text('Accept if coverage > τlex OR raw cosine > τcos',.65,1.56,12,.63,27,true,C.navy);
pair('Coverage definition','Matched distinct query content tokens /\nall distinct query content tokens.',.65,2.59,5.65,C.blue);
pair('Fixed preprocessing','Exclude IDs and fixed stopwords.\nSame segmenter. Empty sets score 0.',7.0,2.59,5.65,C.blue);
pair('Automatic checks','Metadata, citation identifiers\nand literal excerpts.',.65,4.17,5.65,C.teal);
pair('Human scoring','Semantic support, facts, values,\nunits and applicable conditions.',7.0,4.17,5.65,C.teal);
text('No numerical threshold is claimed as tuned. Similarity is not semantic proof.\nAPI/format failures are errors. Clarification is justified only for labelled ambiguity.',.65,6.1,12,.65,18,true,C.amber);

// B4 (17): strict ablation and metric denominators, readable 16+ pt.
page(17,'Strict ablation contracts and scoring denominators','Backup B4','Proposal pp.5–7 and readable ELEC3801 Proposal. Report citation/answer coverage. Zero denominators: N/A.');
pair('A1: remove edition checks','Disable year restrictions and edition availability/ambiguity checks.\nRetain standard-family filtering.',.65,1.48,12,C.amber);
pair('A2: remove the retrieval gate','Retain prompts, citation validation and error handling.\nThis measures only the gate\'s incremental effect.',.65,2.99,12,C.teal);
const denominators=tableRows([
 ['Metric','Scoring population / denominator'],
 ['Retrieval, correctness, false refusal','64 answerable items. Retrieval uses pre-gate rankings.'],
 ['Refusal recall / unsupported answers','16 unanswerable / all 80 test items, respectively.'],
 ['Wrong-edition rate','All unambiguous edition requests, including missing ones.'],
 ['Citation support','All cited claims. Judge each claim\'s citations jointly.']]);
smallTable(denominators,.65,4.58,[5.05,7.0],.42,16);

// B5 (18): risks, fallback limits, resource/schedule commitments.
page(18,'Data availability and fallback limits','Backup B5','Proposal O1, §4.6 and schedule. Replacement-provider comparisons must use one consistent configuration.');
text('Corpus target: 20–30 usable documents',.65,1.48,12,.44,25,true,C.navy);
text('Seek 2 families × 2 formal editions. Verify provenance, permissions, hashes,\nidentifier/year, extraction quality and PDF/DOCX source locations.',.65,2.12,12,.76,21);
pair('Insufficient formal edition pairs','Seek permitted alternatives.\nKeep A1 and limit RQ2 to available editions.',.65,3.27,5.65,C.amber);
pair('Embedding service unavailable','Resolve access or document replacement.\nBM25 alone cannot validate Dense/Hybrid.',7.0,3.27,5.65,C.amber);
text('Rights and scope',.65,4.99,12,.34,22,true,C.blue);
text('Only permitted text goes online. Protect keys and test labels.\nExclude scans/drafts, training, OCR, agents, drawings, hardware and deployment.',.65,5.48,12,.8,19);
text('Budget: GBP 35 generation + 10 embeddings + 5 reserve. Review at GBP 40.\n372 h through W24 + 28 h viva. W22–23 break, W25–27 viva, subject to official notices.',.65,6.42,12,.56,15.5,false,C.muted);

const output=process.argv[2] || path.join(__dirname,'../.build/candidate-raw.pptx');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(path.join(__dirname,'layout-manifest.json'),JSON.stringify(geometry,null,2));
pptx.writeFile({fileName:output}).then(()=>console.log(output));
