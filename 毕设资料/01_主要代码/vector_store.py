"""向量库与混合检索模块（本项目的算法核心）。

整体思路：
1. 入库：把文档切块 -> 调在线 embedding 得到向量 -> 连同原文和元数据一起保存；
2. 检索：对同一个 query 分别做「稠密向量检索」和「稀疏 BM25 检索」，
   再按权重把两路得分归一化后融合，得到最终排序。

这里用 numpy 直接做向量点积（向量已归一化，点积即余弦相似度），
BM25 也由本模块自实现，从而把"检索"这条链路完整、透明地展示出来，
不依赖 Chroma / FAISS 等外部向量库，便于在论文中讲解每一步计算。
"""

import json
import math
import os
import re
from collections import Counter
from typing import Dict, List, Optional

import numpy as np

try:
    from .config import Config
    from .online_api import OnlineClient
    from .text_splitter import split_text
except ImportError:
    from config import Config
    from online_api import OnlineClient
    from text_splitter import split_text


class VectorStore:
    """在线向量化 + 自实现 BM25 的混合检索库。"""

    # BM25 的两个经验系数，取信息检索中的常用默认值
    BM25_K1 = 1.5
    BM25_B = 0.75

    def __init__(self, client: Optional[OnlineClient] = None):
        self.config = Config()
        self.client = client or OnlineClient()
        self.records: List[Dict] = []  # 每条: {"content", "metadata", "vector"}
        self._load()

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------
    def _load(self) -> None:
        """从磁盘恢复知识库。"""
        path = self.config.KB_PATH
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                self.records = json.load(handle)
            print(f"已加载知识库：{path}（{len(self.records)} 个文本块）")

    def _save(self) -> None:
        """把知识库写回磁盘。"""
        path = self.config.KB_PATH
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.records, handle, ensure_ascii=False)

    # ------------------------------------------------------------------
    # 入库
    # ------------------------------------------------------------------
    def add_documents(self, docs: List[Dict], batch_size: int = 16) -> int:
        """把一批文档切块、向量化并写入知识库，返回新增文本块数。"""
        # 1) 切块
        chunks: List[Dict] = []
        for doc in docs:
            pieces = split_text(
                doc["content"],
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP,
            )
            for index, piece in enumerate(pieces):
                metadata = dict(doc["metadata"])
                metadata["chunk_index"] = index
                chunks.append({"content": piece, "metadata": metadata})

        if not chunks:
            return 0

        # 2) 分批向量化（在线接口）并写入
        total = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = self.client.embed([item["content"] for item in batch])
            for item, vector in zip(batch, vectors):
                item["vector"] = vector
                self.records.append(item)
            total += len(batch)
            print(f"  已入库 {total}/{len(chunks)} 个文本块")

        # 3) 持久化
        self._save()
        return total

    def clear(self) -> None:
        """清空知识库。"""
        self.records = []
        self._save()

    def count(self) -> int:
        return len(self.records)

    # ------------------------------------------------------------------
    # 分词（供 BM25 使用）
    # ------------------------------------------------------------------
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """轻量中文/英文分词：中文取单字 + 2/3 元 ngram，英文数字整体保留。"""
        text = (text or "").lower()
        if not text:
            return []
        tokens: List[str] = []
        for piece in re.findall(r"[\u4e00-\u9fff]+|[a-z0-9_./\-]+", text):
            if re.fullmatch(r"[\u4e00-\u9fff]+", piece):
                tokens.extend(piece)  # 单字
                for n in (2, 3):
                    tokens.extend(piece[i : i + n] for i in range(len(piece) - n + 1))
            else:
                tokens.append(piece)
        return tokens

    # ------------------------------------------------------------------
    # BM25 稀疏检索
    # ------------------------------------------------------------------
    def _bm25_scores(self, query: str, candidate_ids: List[int]) -> Dict[int, float]:
        """在候选集合上计算 BM25 得分（返回 id -> 原始分）。"""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return {}

        # 建立候选集合的词频统计
        doc_tokens: Dict[int, Counter] = {}
        doc_len: Dict[int, int] = {}
        df: Counter = Counter()  # 词 -> 出现该词的文档数

        for idx in candidate_ids:
            tokens = self._tokenize(self.records[idx]["content"])
            counter = Counter(tokens)
            doc_tokens[idx] = counter
            doc_len[idx] = len(tokens)
            for token in counter:
                df[token] += 1

        n_docs = len(candidate_ids)
        avg_len = sum(doc_len.values()) / n_docs if n_docs else 0.0

        scores: Dict[int, float] = {}
        for idx in candidate_ids:
            score = 0.0
            length = doc_len[idx]
            for token in query_tokens:
                freq = doc_tokens[idx].get(token, 0)
                if freq == 0:
                    continue
                idf = math.log(1 + (n_docs - df[token] + 0.5) / (df[token] + 0.5))
                denom = freq + self.BM25_K1 * (1 - self.BM25_B + self.BM25_B * length / (avg_len or 1))
                score += idf * freq * (self.BM25_K1 + 1) / denom
            if score > 0:
                scores[idx] = score
        return scores

    # ------------------------------------------------------------------
    # 向量稠密检索
    # ------------------------------------------------------------------
    def _cosine_scores(self, query: str, candidate_ids: List[int]) -> Dict[int, float]:
        """计算 query 与候选文本块的余弦相似度。"""
        if not candidate_ids:
            return {}
        query_vector = np.asarray(self.client.embed_one(query), dtype=np.float32)
        if query_vector.size == 0:
            return {}
        matrix = np.asarray([self.records[idx]["vector"] for idx in candidate_ids], dtype=np.float32)

        # 归一化，保证点积即余弦相似度
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-9)
        row_norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-9
        sims = (matrix / row_norms) @ query_norm
        return {idx: float(sims[i]) for i, idx in enumerate(candidate_ids)}

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize(scores: Dict[int, float]) -> Dict[int, float]:
        """把一组得分线性归一化到 [0, 1]。"""
        if not scores:
            return {}
        values = list(scores.values())
        low, high = min(values), max(values)
        if math.isclose(low, high):
            return {key: 1.0 for key in scores}
        return {key: (value - low) / (high - low) for key, value in scores.items()}

    def _filter_by_standard(self, standard_no: str) -> List[int]:
        """按标准号元数据过滤候选（命中不到时退回全集，避免空召回）。"""
        key = (standard_no or "").lower().replace("/", "").replace(" ", "")
        if not key:
            return list(range(len(self.records)))
        hits = [
            idx
            for idx, record in enumerate(self.records)
            if key in (record["metadata"].get("standard_no", "") or "").lower()
        ]
        return hits or list(range(len(self.records)))

    # ------------------------------------------------------------------
    # 对外检索入口
    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        standard_no: str = "",
    ) -> List[Dict]:
        """混合检索：向量 + BM25，加权融合后返回 top_k。"""
        if not self.records or not query.strip():
            return []
        top_k = top_k or self.config.TOP_K

        candidate_ids = self._filter_by_standard(standard_no)
        vector_scores = self._normalize(self._cosine_scores(query, candidate_ids))
        bm25_scores = self._normalize(self._bm25_scores(query, candidate_ids))

        fused: Dict[int, float] = {}
        for idx in candidate_ids:
            fused[idx] = (
                self.config.VECTOR_WEIGHT * vector_scores.get(idx, 0.0)
                + self.config.BM25_WEIGHT * bm25_scores.get(idx, 0.0)
            )

        ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]

        results: List[Dict] = []
        for idx, score in ranked:
            record = self.records[idx]
            results.append(
                {
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "vector_score": round(vector_scores.get(idx, 0.0), 4),
                    "bm25_score": round(bm25_scores.get(idx, 0.0), 4),
                    "fusion_score": round(score, 4),
                }
            )
        return results
