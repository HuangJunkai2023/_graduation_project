"""命令行问答演示。

运行前请先在 .env 中配置 ZHIPUAI_API_KEY，并确保已经构建过知识库
（可用 build_kb.py 导入文档）。

用法：
    python ask.py                       # 进入交互式问答
    python ask.py --question "接触网零部件的技术条件是什么？"   # 单次提问
"""

import argparse
import sys

try:
    from .rag_pipeline import RAGPipeline
except ImportError:
    from rag_pipeline import RAGPipeline


def print_result(result: dict) -> None:
    print("\n================ 回答 ================")
    print(result["answer"])
    if result["sources"]:
        print("\n---------------- 引用来源 ----------------")
        for index, doc in enumerate(result["sources"], start=1):
            metadata = doc.get("metadata", {})
            print(
                f"[来源{index}] {metadata.get('file_name', 'unknown')} "
                f"第{metadata.get('page', '-')}页 "
                f"(融合分={doc.get('fusion_score')})"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="RAG 命令行问答")
    parser.add_argument("--question", help="单次提问；不填则进入交互模式")
    args = parser.parse_args()

    pipeline = RAGPipeline()

    if args.question:
        print_result(pipeline.answer(args.question))
        return 0

    print("已进入交互式问答，输入 exit / quit 退出。")
    while True:
        try:
            question = input("\n请输入问题> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "退出"}:
            break
        print_result(pipeline.answer(question))
    return 0


if __name__ == "__main__":
    sys.exit(main())
