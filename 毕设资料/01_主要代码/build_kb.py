"""知识库构建脚本。

用法示例：
    # 导入一个目录下的所有 PDF / DOCX
    python build_kb.py --dir "D:/docs/规范"

    # 导入单个文件
    python build_kb.py --file "D:/docs/TBT 2075-2024.pdf"

    # 清空知识库后重新导入
    python build_kb.py --dir "D:/docs/规范" --reset
"""

import argparse
import os
import sys

try:
    from .document_parser import parse_directory, parse_file
    from .vector_store import VectorStore
except ImportError:
    from document_parser import parse_directory, parse_file
    from vector_store import VectorStore


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 RAG 知识库（在线 embedding）")
    parser.add_argument("--dir", help="要导入的目录（递归解析 PDF/DOCX）")
    parser.add_argument("--file", help="要导入的单个文件")
    parser.add_argument("--reset", action="store_true", help="导入前清空现有知识库")
    args = parser.parse_args()

    if not args.dir and not args.file:
        parser.error("请至少指定 --dir 或 --file 之一")

    store = VectorStore()
    if args.reset:
        print("已清空原有知识库。")
        store.clear()

    # 1) 解析文档
    if args.dir:
        if not os.path.isdir(args.dir):
            print(f"目录不存在：{args.dir}")
            return 1
        print(f"开始解析目录：{args.dir}")
        docs = parse_directory(args.dir)
    else:
        if not os.path.isfile(args.file):
            print(f"文件不存在：{args.file}")
            return 1
        print(f"开始解析文件：{args.file}")
        docs = parse_file(args.file)

    print(f"共解析出 {len(docs)} 个文档单元。")
    if not docs:
        print("没有可导入的内容。")
        return 0

    # 2) 切块 + 向量化 + 入库
    added = store.add_documents(docs)
    print(f"导入完成：新增 {added} 个文本块，知识库当前共 {store.count()} 个文本块。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
