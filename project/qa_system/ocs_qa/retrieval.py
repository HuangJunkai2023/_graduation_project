"""BM25 / dense / hybrid retrieval with explicit edition constraints."""
from collections import Counter, defaultdict
import math
import re
import numpy as np
from .documents import STANDARD, standards
from .api import APIError


def tokens(text):
    result = []
    for part in re.findall(r"[\u4e00-\u9fff]+|[a-z0-9_.-]+", text.lower()):
        if re.fullmatch(r"[\u4e00-\u9fff]+", part):
            for n in (1, 2, 3): result.extend(part[i:i+n] for i in range(len(part)-n+1))
        else: result.append(part)
    return result


def content_terms(query):
    query = STANDARD.sub(" ", query)
    query = re.sub(r"请问|请介绍|请说明|根据|有关|规定|标准|哪些|什么|如何|多少|是否|怎么|里面|其中|要求|有什么|有哪些|的|是|了|吗|呢", " ", query)
    return {t for t in tokens(query) if len(t) >= 2}


def normalize(values):
    if not values: return {}
    low, high = min(values.values()), max(values.values())
    if math.isclose(low, high): return {k: (1.0 if v > 0 else 0.0) for k,v in values.items()}
    return {k: (v-low)/(high-low) for k,v in values.items()}


class Retriever:
    def __init__(self, store, client):
        self.settings, self.client = store.settings, client
        self.records = store.records()
        self.tf = [Counter(tokens(r["text"])) for r in self.records]
        self.lengths = [sum(t.values()) for t in self.tf]
        self.df = Counter(t for counter in self.tf for t in counter)
        self.avg_len = sum(self.lengths)/max(1,len(self.lengths))

    def search(self, query, mode="bm25", top_k=None, edition_filter=True, include_drafts=False):
        if mode not in ("bm25", "dense", "hybrid"): raise ValueError("未知检索模式。")
        top_k = self.settings.top_k if top_k is None else top_k
        if not 1 <= top_k <= 20: raise ValueError("Top-K 须在 1–20。")
        if not query.strip(): return {"status": "empty_question", "sources": []}
        if not self.records: return {"status": "empty_kb", "sources": []}
        candidates = [i for i,r in enumerate(self.records) if include_drafts or r["document"]["publication_status"] != "draft"]
        specs = standards(query)
        if edition_filter and specs:
            wanted = set()
            for standard, year in specs:
                hits = [i for i in candidates if self.records[i]["document"]["standard"] == standard]
                editions = sorted({self.records[i]["document"]["year"] or "未标年份" for i in hits})
                if year: hits = [i for i in hits if self.records[i]["document"]["year"] == year]
                if not hits: return {"status": "missing_edition", "sources": [], "requested": f"{standard}-{year}".rstrip("-"), "available_editions": editions}
                if not year and len(editions)>1:
                    return {"status": "clarify_edition", "sources": [], "requested": standard, "available_editions": editions}
                wanted.update(hits)
            candidates = sorted(wanted)
        q_tokens = set(tokens(query)); lexical = {}
        for i in candidates:
            score = 0.
            for term in q_tokens:
                freq = self.tf[i].get(term, 0)
                if not freq: continue
                idf = math.log(1+(len(self.records)-self.df[term]+.5)/(self.df[term]+.5))
                score += idf*freq*2.5/(freq+1.5*(.25+.75*self.lengths[i]/(self.avg_len or 1)))
            lexical[i] = score
        dense = {}
        if mode in ("dense", "hybrid"):
            if any(self.records[i]["vector_identity"] != self.settings.embedding_identity for i in candidates):
                raise APIError("index_not_ready", "候选文档尚未使用当前 Embedding 模型完成向量化，请先补齐向量或切换 BM25。")
            if candidates:
                query_vector = np.asarray(self.client.embed([query])[0], dtype=float)
                matrix = np.asarray([self.records[i]["vector"] for i in candidates], dtype=float)
                if matrix.ndim != 2 or matrix.shape[1] != len(query_vector):
                    raise APIError("embedding_dimension", "查询与知识库向量维度不一致。")
                sims = matrix @ query_vector / (np.linalg.norm(matrix,axis=1)*np.linalg.norm(query_vector))
                dense = dict(zip(candidates, map(float, sims)))
        ln, dn = normalize(lexical), normalize(dense)
        weight = self.settings.vector_weight
        fused = {i: lexical[i] if mode=="bm25" else dense[i] if mode=="dense" else (1-weight)*ln[i]+weight*dn[i] for i in candidates}
        ranked = sorted(candidates, key=lambda i:(-fused[i],self.records[i]["id"]))
        # Never return zero-overlap keyword candidates just to fill Top-K.
        if mode == "bm25": ranked = [i for i in ranked if lexical[i]>0]
        # Multiple requested standards each get one slot, then fill by rank.
        if edition_filter and len(specs)>1:
            selected = []
            for spec in specs:
                first = next((i for i in ranked if self.records[i]["document"]["standard"]==spec[0] and (not spec[1] or self.records[i]["document"]["year"]==spec[1]) and i not in selected),None)
                if first is not None: selected.append(first)
            ranked = selected+[i for i in ranked if i not in selected]
        terms = content_terms(query)
        sources = []
        for i in ranked[:top_k]:
            record = self.records[i]
            coverage = sum(t in record["text"].lower() for t in terms)/len(terms) if terms else 0.
            sources.append({k:v for k,v in record.items() if k not in ("vector", "vector_identity")})
            sources[-1].update(source=len(sources), bm25_score=lexical[i], vector_score=dense.get(i),
                               score=fused[i], lexical_coverage=coverage)
        return {"status": "retrieved" if sources else "insufficient_evidence", "sources": sources, "query": query}
