# 主要代码说明

> **全部走在线 API。**
>
> - 向量化：调用在线 embedding 接口（默认智谱 `embedding-3`）
> - 答案生成：调用在线对话接口（默认智谱 `glm-4-flash`）
> - 不依赖 `torch / transformers / sentence-transformers / 本地 bge 模型 / 本地大模型`

同时，为了把 RAG 的每一步计算都讲清楚，这里**没有使用 Chroma / FAISS**，
向量检索用 numpy 直接实现，BM25 由本代码自实现，适合在论文里逐行讲解。

---

## 一、文件清单

| 文件                   | 作用                                                 | 对应论文中的环节           |
| ---------------------- | ---------------------------------------------------- | -------------------------- |
| `config.py`          | 读取`.env` 配置（API Key、模型名、切块与检索参数） | 系统配置                   |
| `online_api.py`      | 封装在线 embedding 与 chat 接口                      | 调用在线大模型/向量化服务  |
| `document_parser.py` | PDF / DOCX 解析、文本清洗、标准号元数据抽取          | 文档预处理                 |
| `text_splitter.py`   | 递归字符切分（含重叠）                               | 文本分块                   |
| `vector_store.py`    | 向量入库 + 自实现 BM25 + 混合检索融合                | **检索（核心算法）** |
| `rag_pipeline.py`    | 组装上下文与提示词、在线生成、多轮记忆               | **生成（核心链路）** |
| `build_kb.py`        | 命令行建库脚本                                       | 知识库构建                 |
| `ask.py`             | 命令行问答                                           | 系统调用示例               |
| `web_app.py`         | Streamlit 网页演示（可选）                           | 系统界面                   |
| `selftest.py`        | 离线自检（不消耗 API 额度）                          | 功能测试                   |

---

## 二、系统流程

```text
                ┌─────────────────────────────┐
   离线建库：   │ PDF/DOCX -> 解析清洗 -> 切块 │
                │      -> 在线 embedding 向量化 │
                │      -> 写入知识库文件        │
                └─────────────────────────────┘

                ┌───────────────────────────────────────────┐
   在线问答：   │ 用户问题 -> 抽取标准号检索线索              │
                │   -> 向量检索(余弦) + BM25 稀疏检索         │
                │   -> 加权融合 -> Top-K 证据片段             │
                │   -> 组装上下文与提示词 -> 在线大模型生成   │
                │   -> 返回带来源引用的答案 + 更新对话记忆     │
                └───────────────────────────────────────────┘
```

---

## 三、快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
copy .env.example .env      # Windows
# 或 cp .env.example .env   # Linux/macOS
```

编辑 `.env`，把 `ZHIPUAI_API_KEY` 换成你自己的在线 API Key
（智谱开放平台：https://open.bigmodel.cn/ ）。

### 3. 离线自检（不需要 API Key，验证算法链路）

```bash
python selftest.py
```

### 4. 构建知识库

```bash
python build_kb.py --dir "D:/你的文档目录" --reset
```

### 5. 提问

```bash
# 单次提问
python ask.py --question "接触网零部件的技术条件是什么？"

# 交互式问答
python ask.py
```

### 6.（可选）网页演示

```bash
streamlit run web_app.py
```

---

## 四、核心算法说明

### 1. 文本切分（`text_splitter.py`）

按"段落 → 换行 → 句号 → 分号 → 逗号 → 空格 → 字符"的优先级递归切分，
再合并为不超过 `CHUNK_SIZE` 的块，块间保留 `CHUNK_OVERLAP` 重叠，
兼顾语义完整性与长度可控。

### 2. 混合检索（`vector_store.py`）

对同一个 query 做两路检索后融合：

- **向量检索（稠密）**：`cosine(query, chunk)`，捕捉语义相似；
- **BM25（稀疏）**：基于词频与逆文档频率的关键词匹配，公式为

  ```
  score(q,d) = Σ  IDF(t) · f(t,d)·(k1+1) / ( f(t,d) + k1·(1-b+b·|d|/avgdl) )
  IDF(t)     = ln( 1 + (N - n(t) + 0.5) / (n(t) + 0.5) )
  ```

  其中 `k1=1.5`、`b=0.75` 为常用经验值；中文分词采用"单字 + 2/3 元 ngram"。
- **融合排序**：

  ```
  fusion = VECTOR_WEIGHT · normalize(向量分) + BM25_WEIGHT · normalize(BM25分)
  ```

  两路得分各自线性归一化到 `[0,1]` 后再加权，避免量纲不一致。

### 3. 检索线索与元数据过滤（`rag_pipeline.py`）

从问题中抽取标准号（如 `TB/T 2075-2024` → `TBT20752024`），
在检索前按文档元数据 `standard_no` 过滤候选，提升"指定标准类问题"的命中稳定性。

### 4. 提示词与幻觉抑制（`rag_pipeline.py`）

提示词明确要求：只依据参考文档作答、无法确认要说明、答案标注 `[来源n]`；
检索不到证据时回退为通用回答，避免"强行引用无关文档"。

---
