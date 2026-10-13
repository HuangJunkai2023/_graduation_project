"""Batch runs with gold-evidence metrics; answer grading remains explicit/manual."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from .pipeline import compact


def retrieval_metrics(sources, gold):
    if not gold: return {"recall_at_5": None, "mrr_at_5": None}
    matched = set(); first = None
    for rank, source in enumerate(sources[:5], 1):
        for i, unit in enumerate(gold):
            if (source["document_id"] == unit["document_id"] and source["location"] == unit["location"]
                    and compact(unit["quote"]) in compact(source["text"])):
                matched.add(i)
                if first is None: first = rank
    return {"recall_at_5": len(matched)/len(gold), "mrr_at_5": 1/first if first else 0.}


def run_evaluation(pipeline, dataset_path, output, *, mode="bm25", generate=False,
                   edition_filter=True, evidence_check=True):
    dataset_path, output = Path(dataset_path), Path(output)
    questions = [json.loads(line) for line in dataset_path.read_text().splitlines() if line.strip()]
    ids = set()
    for q in questions:
        if not isinstance(q.get("question"),str) or not q["question"].strip(): raise ValueError("评测题缺少有效 question。")
        if not q.get("question_id") or q["question_id"] in ids: raise ValueError("question_id 缺失或重复。")
        ids.add(q["question_id"])
        if type(q.get("answerable")) is not bool: raise ValueError("answerable 必须显式标注 true/false。")
        gold = q.get("evidence_units",[])
        if q["answerable"] and not gold: raise ValueError("可回答题必须标注 evidence_units。")
        if not q["answerable"] and gold: raise ValueError("不可回答题不能有 gold evidence。")
        for unit in gold:
            if not all(isinstance(unit.get(k),str) and unit[k].strip() for k in ["document_id","location","quote"]):
                raise ValueError("证据须含 document_id、location 与非空 quote。")
    if output.resolve()==dataset_path.resolve(): raise ValueError("输出路径不能覆盖评测题。")
    if output.exists() or output.with_suffix(".summary.json").exists(): raise ValueError("输出已存在，请使用新的运行文件名。")
    config = {"mode":mode,"generate":generate,"edition_filter":edition_filter,"evidence_check":evidence_check,
              "top_k":5,"chat_model":pipeline.settings.chat_model,"embedding_identity":pipeline.settings.embedding_identity,
              "vector_weight":pipeline.settings.vector_weight,"min_coverage":pipeline.settings.min_coverage,
              "min_cosine":pipeline.settings.min_cosine,"chunk_size":pipeline.settings.chunk_size,"chunk_overlap":pipeline.settings.chunk_overlap}
    records = pipeline.retriever.records
    corpus_hash=hashlib.sha256(json.dumps([{k:r[k] for k in ("id","text","document")} for r in records],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    results=[]
    for q in questions:
        r = pipeline.answer(q["question"],history=q.get("history",[]),mode=mode,generate=generate,
                            edition_filter=edition_filter,evidence_check=evidence_check,top_k=5)
        # Store raw pre-gate retrieval separately so refused questions stay in the denominator.
        raw_sources = r.get("retrieved_sources",r["sources"])
        metrics = retrieval_metrics(raw_sources,q.get("evidence_units",[]))
        results.append({"question_id":q["question_id"],"split":q.get("split","unspecified"),"category":q.get("category","unspecified"),
                        "answerable":q["answerable"],"reference_answer":q.get("reference_answer"),"result":r,"metrics":metrics,
                        "manual_grade":{"answer_correct":None,"citation_supported":None,"notes":""}})
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x",encoding="utf-8") as f:
        for row in results: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    aggregate={}
    for name in ["recall_at_5","mrr_at_5"]:
        scores=[r["metrics"][name] for r in results if r["metrics"][name] is not None]
        aggregate[name]=sum(scores)/len(scores) if scores else None
    summary={"created_at":datetime.now(timezone.utc).isoformat(),"questions":len(results),"config":config,
             "dataset_sha256":hashlib.sha256(dataset_path.read_bytes()).hexdigest(),"corpus_sha256":corpus_hash,
             "metrics":aggregate,"answerable_count":sum(q["answerable"] for q in questions),
             "api_errors":sum(r["result"]["status"]=="api_error" for r in results),
             "note":"答案和引用语义支撑尚待人工判分；本结果不等于正式论文结论。"}
    output.with_suffix(".summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    return summary
