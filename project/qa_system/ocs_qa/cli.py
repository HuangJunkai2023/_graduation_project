import argparse
import json
from pathlib import Path
from .config import Settings
from .store import Store
from .api import ModelClient, APIError
from .pipeline import Pipeline
from .evaluation import run_evaluation


def main():
    parser=argparse.ArgumentParser(description="接触网规范问答：本地检索 / DeepSeek 生成")
    parser.add_argument("--db",help="SQLite 知识库路径")
    sub=parser.add_subparsers(dest="command",required=True)
    ingest=sub.add_parser("ingest",help="仅本地解析入库，不调用模型")
    ingest.add_argument("files",nargs="+")
    ingest.add_argument("--allow-cloud",action="store_true",help="标记所选资料允许发送至配置的模型服务")
    sub.add_parser("status",help="文档、向量及配置状态，不显示密钥")
    auth=sub.add_parser("allow-cloud",help="标记指定文档可用于在线处理")
    auth.add_argument("document_ids",nargs="+")
    sub.add_parser("embed",help="对获准的文档补建向量；调用 Embedding API")
    ask=sub.add_parser("ask",help="检索或问答")
    ask.add_argument("question")
    evaluate=sub.add_parser("evaluate",help="运行已标注的 JSONL 评测集")
    evaluate.add_argument("dataset")
    evaluate.add_argument("--output",required=True)
    for p in (ask,evaluate):
        p.add_argument("--mode",choices=["bm25","dense","hybrid"],default="bm25")
        p.add_argument("--generate",action="store_true",help="调用 DeepSeek 生成答案")
        p.add_argument("--no-edition-filter",action="store_true",help="消融：关闭版本约束")
        p.add_argument("--no-evidence-check",action="store_true",help="消融：关闭检索证据门槛")
    args=parser.parse_args()
    try:
        settings=Settings.load(args.db); store=Store(settings); client=ModelClient(settings)
        if args.command=="ingest":
            result=[store.ingest(path,allow_cloud=args.allow_cloud) for path in args.files]
        elif args.command=="status":
            docs=store.documents(); records=store.records()
            result={"documents":len(docs),"chunks":len(records),"vectors_current_model":sum(r["vector_identity"]==settings.embedding_identity for r in records),
                    "deepseek_configured":bool(settings.chat_key),"embedding_configured":bool(settings.embedding_key and settings.embedding_url and settings.embedding_model),
                    "model":settings.chat_model,"files":docs}
        elif args.command=="allow-cloud":
            store.set_cloud_permission(args.document_ids,True); result={"updated":len(args.document_ids)}
        elif args.command=="embed": result=store.embed_pending(client)
        else:
            pipeline=Pipeline(store,client)
            options={"mode":args.mode,"generate":args.generate,"edition_filter":not args.no_edition_filter,"evidence_check":not args.no_evidence_check}
            result=pipeline.answer(args.question,**options) if args.command=="ask" else run_evaluation(pipeline,args.dataset,args.output,**options)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if args.command=="ingest": return int(any(r["status"]=="error" for r in result))
        return int(isinstance(result,dict) and result.get("status") in ("api_error","invalid_response","invalid_citation"))
    except (ValueError,APIError,OSError) as exc:
        print(json.dumps({"status":"error","message":str(exc)},ensure_ascii=False)); return 1


if __name__=="__main__": raise SystemExit(main())
