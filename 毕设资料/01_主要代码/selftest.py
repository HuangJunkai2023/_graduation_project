"""离线自检脚本：不消耗在线 API，即可验证切分、分词、BM25 与融合检索是否正常。

它用一个确定性的"伪向量"客户端替换真实的在线 embedding，
专门用来验证算法链路（切块 / 分词 / BM25 / 归一化 / 融合排序）的正确性。

运行：
    python selftest.py
"""

import math
import os
import tempfile

from text_splitter import split_text
from vector_store import VectorStore
from config import Config


class FakeEmbeddingClient:
    """用字符哈希构造确定性向量，替代在线 embedding，便于离线验证检索逻辑。"""

    DIM = 128

    def embed(self, texts):
        return [self._vector(text) for text in texts]

    def embed_one(self, text):
        return self._vector(text)

    def _vector(self, text):
        vector = [0.0] * self.DIM
        for char in text:
            vector[ord(char) % self.DIM] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def test_split():
    text = "第一句测试内容。" * 300
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert chunks, "切分结果不应为空"
    assert all(len(chunk) <= 130 for chunk in chunks), "文本块不应明显超过 chunk_size"
    print(f"[通过] split_text：{len(text)} 字 -> {len(chunks)} 个文本块")


def test_retrieval():
    # 用临时知识库路径，避免污染真实数据
    store = VectorStore.__new__(VectorStore)  # 跳过 __init__，手动注入依赖
    store.config = Config()
    store.config.KB_PATH = os.path.join(tempfile.gettempdir(), "_selftest_kb.json")
    store.client = FakeEmbeddingClient()
    store.records = []

    docs = [
        {
            "content": "接触网零部件的技术要求：零部件表面应光洁，无裂纹、疤痕和剥离。",
            "metadata": {"file_name": "TBT 2073-2020.pdf", "page": 7, "standard_no": "TBT20732020"},
        },
        {
            "content": "本文件规定了电气化铁路接触网零部件的分类、技术要求、检验规则和试验方法。",
            "metadata": {"file_name": "TBT 2075-2024.pdf", "page": 3, "standard_no": "TBT20752024"},
        },
        {
            "content": "电缆敷设施工应符合 110kV 及以下电缆敷设的国家标准图集要求。",
            "metadata": {"file_name": "12D101-5 电缆敷设.pdf", "page": 1, "standard_no": ""},
        },
    ]
    added = store.add_documents(docs)
    assert added >= 3, "至少应写入 3 个文本块"
    print(f"[通过] add_documents：写入 {added} 个文本块")

    # 分词自检
    tokens = store._tokenize("接触网零部件")
    assert "接" in tokens and "接触" in tokens, "分词应同时包含单字和 ngram"
    print(f"[通过] _tokenize：{tokens[:8]} ...")

    # 打分自检
    candidate_ids = list(range(store.count()))
    bm25 = store._bm25_scores("接触网零部件", candidate_ids)
    assert bm25, "BM25 应能给出非零得分"
    assert max(bm25, key=bm25.get) != 2, "电缆敷设文档不应排在接触网文档之前"
    print(f"[通过] _bm25_scores：命中 {len(bm25)} 篇")

    # 融合检索自检
    results = store.search("接触网零部件的技术要求是什么？", top_k=2)
    assert results, "检索结果不应为空"
    assert "接触网" in results[0]["content"], "排序第一应是与问题相关的接触网文档"
    print(f"[通过] search：第 1 条来源 = {results[0]['metadata']['file_name']}")

    # 标准号过滤自检
    filtered = store.search("技术要求", top_k=3, standard_no="TBT20752024")
    assert filtered and filtered[0]["metadata"]["standard_no"] == "TBT20752024"
    print(f"[通过] 标准号过滤：命中 {filtered[0]['metadata']['standard_no']}")

    os.remove(store.config.KB_PATH)


if __name__ == "__main__":
    test_split()
    test_retrieval()
    print("\n全部自检通过 ✅")
