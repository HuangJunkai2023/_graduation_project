# 本科毕业设计资料包 —— 面向规范文档的 RAG 问答系统

本文件夹是从项目 **Trae-RAG**（接触网规范文档问答系统）整理出的**本科毕业设计参考资料**，
包含三部分：**主要代码**、**RAG 参考文献**、**技术说明**。

> 关键约定：代码**全部调用在线 API**（在线向量化 + 在线大模型），
> **不需要在本机部署 embedding 模型或本地大模型**，只需一个有效的在线 API Key。

---

## 目录结构

```text
毕设资料/
├── README.md                    本文件：资料总览与使用指引
│
├── 01_主要代码/                 可直接运行的参考实现（在线 API 版）
│   ├── README.md                代码说明 + 运行步骤 + 与原项目的对应关系
│   ├── config.py                配置（API Key、切块、检索参数）
│   ├── online_api.py            在线 embedding / chat 接口封装
│   ├── document_parser.py       PDF / DOCX 解析、清洗、标准号抽取
│   ├── text_splitter.py         递归字符切分（含重叠）
│   ├── vector_store.py          向量入库 + 自实现 BM25 + 混合检索融合 ★核心
│   ├── rag_pipeline.py          RAG 问答链路 + 多轮记忆 ★核心
│   ├── build_kb.py              命令行建库脚本
│   ├── ask.py                   命令行问答
│   ├── web_app.py               Streamlit 网页演示（可选）
│   ├── selftest.py              离线自检（不消耗 API 额度）
│   ├── requirements.txt         依赖（无 torch/transformers）
│   └── .env.example             配置模板
│
├── 02_参考文献/                 RAG 参考文献
│   ├── RAG参考文献.md           分类整理的 38 篇关键文献（含贡献说明与引用建议）
│   └── references.bib           对应的 BibTeX，可直接用于 LaTeX
│
└── 03_技术说明/                 论文写作素材
    ├── 系统设计说明.md           架构、流程、算法、参数、可扩展方向
    └── 论文写作建议.md           章节大纲、可复用图表、实验设计、创新点提炼
```

---

## 五分钟上手

```bash
cd 01_主要代码

# 1) 安装依赖
pip install -r requirements.txt

# 2) 离线自检（无需 API Key，验证检索算法）
python selftest.py

# 3) 配置 API Key
copy .env.example .env        # 然后编辑 .env 填入 ZHIPUAI_API_KEY

# 4) 建库
python build_kb.py --dir "D:/你的文档目录" --reset

# 5) 提问
python ask.py --question "接触网零部件的技术条件是什么？"
```

> 网页演示：`streamlit run web_app.py`

---

## 三个部分怎么用

| 部分            | 用途                         | 对应论文               |
| --------------- | ---------------------------- | ---------------------- |
| `01_主要代码` | 系统实现与答辩演示           | 第3、4章（设计与实现） |
| `02_参考文献` | 写"相关工作/综述"，附 BibTeX | 第1、2章，参考文献表   |
| `03_技术说明` | 架构描述、图表素材、实验设计 | 第3、5、6章            |

---

## 与原项目的区别（重要）

| 维度     | 原项目 Trae-RAG                                | 本资料包                                  |
| -------- | ---------------------------------------------- | ----------------------------------------- |
| 向量化   | 本地`BAAI/bge-small-zh` + torch/transformers | **在线 embedding API**              |
| 向量存储 | ChromaDB 持久化（约 6 万切片）                 | numpy 内存检索 + JSON 持久化              |
| 大模型   | 智谱 glm-4.5-air 等 + 本地摘要兜底             | **在线 chat API**，单一链路         |
| 代码规模 | `vector_store.py` 约 1700 行                 | 约 260 行，聚焦算法主干                   |
| 定位     | 工程原型                                       | **教学/毕设参考实现**，便于逐行讲解 |

进阶优化（目录页追踪、章节质量重排、对比类分标准召回、动态标准号过滤等）
已在 `03_技术说明/系统设计说明.md` 的"可扩展方向"中整理，可作为论文的改进点。
