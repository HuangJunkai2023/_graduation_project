# 接触网规范问答系统

当前实现采用 **DeepSeek 问答 + 本地知识库**。无需 GPU，不训练大模型。原始教学参考实现保留在 `毕设资料/01_主要代码/`，本目录是独立实现。

## 先运行

在工程根目录，已有 `.venv` 可直接使用。首次安装：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e 'project/qa_system[dev]'
```

启动本地界面（在应用目录运行，以加载本目录的 Streamlit 配置）：

```bash
cd project/qa_system
../../.venv/bin/python -m streamlit run app.py
```

访问 `http://127.0.0.1:8501`。在“知识库”上传 PDF/DOCX，选择“关键词 BM25”即可检索原文，不需要 API Key。扫描件和低文本量页面会记录提示，首版未执行 OCR。

## DeepSeek 配置

将本目录 `.env.example` 复制为 `.env`，在本机编辑：

```dotenv
DEEPSEEK_API_KEY=你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
```

模型名采用 2026-10-13 查阅的 [DeepSeek 官方示例](https://api-docs.deepseek.com/)，可替换为自己账户可用的模型。接口使用 `/chat/completions`，输出按 [官方 JSON Output](https://api-docs.deepseek.com/guides/json_mode/) 配置。密钥不写进代码、不显示在配置状态中，`.env` 已被 Git 忽略。

在“知识库”选择有权发送至模型服务的资料，点击“允许所选文档在线处理”，然后开启“使用 DeepSeek 生成答案”。导入时也可直接标记。这样发送的是检索到的文本片段；单纯本地 BM25 不需要开启在线处理。

本系统把问答和向量服务分开。**DeepSeek Key 足以运行 BM25 + DeepSeek 问答**；只有做向量或混合检索时，才需要额外配置兼容 `/embeddings` 的文本向量服务：

```dotenv
EMBEDDING_API_KEY=向量服务密钥
EMBEDDING_BASE_URL=https://你的服务提供商/API基址
EMBEDDING_MODEL=该服务的文本向量模型名
```

然后点击“补建允许在线处理文档的向量”，再切换检索模式。不要把对话模型名填入 Embedding 配置。已有批次会保存，失败后可重试补齐；更换服务地址或模型后须重建对应向量，系统不会混用不同模型的向量。

首版不依赖多模态模型：文本 PDF/DOCX 直接解析；扫描件需另加 OCR，图纸理解留作后续扩展。此处没有把文字提取成功等同于表格、公式或图纸理解正确。

## 已实现功能

- PDF 按文件页码、DOCX 按段落/表格行保留出处；正文顺序、数字、单位及换行尽量保留。
- 基于文件 SHA-256 去重，SQLite 事务保存文档和切片；解析失败和跳过页面有导入记录。
- 标准号统一处理空格、斜杠、连字符、分册号及年份；精确筛选版本。指定版本不存在时不退回其他年份；未指定年份且存在多版时要求澄清。
- BM25、向量、混合检索及消融开关；默认排除文件名标记的报批/讨论稿。文件名状态只是线索，不代表标准现行性认定。
- 简单追问在检索前继承主题；显式新标准覆盖旧主题；不明确且没有历史时要求补充。
- 启发式证据检查、模型明确拒答、逐条陈述引用、来源编号和原文摘录校验。未通过引用校验的模型输出不会作为正常答案展示。
- 本地页面可查看证据和 PDF 原文页、管理文档在线处理许可、移除索引文档、清空会话和导出 JSONL。
- DeepSeek 超时、鉴权失败、限流、空输出、截断/异常 JSON 分别报告；不会用通用知识伪装成规范答案。
- 批量评测导出配置、数据哈希、逐题结果、原始检索和阶段耗时；答案语义正确性保留人工评分栏。

## 命令行

以下均在工程根目录运行：

```bash
# 本地建库，不调用 API
.venv/bin/python -m ocs_qa ingest '/绝对路径/规范.pdf' '/绝对路径/规范.docx'

# 查看文档 ID、索引数量与配置状态（不输出密钥）
.venv/bin/python -m ocs_qa status

# 原文检索
.venv/bin/python -m ocs_qa ask 'TB/T 2073-2020 对零部件表面质量有什么要求？'

# 明确标记允许在线处理的文档（填写 status 输出中的 document id）
.venv/bin/python -m ocs_qa allow-cloud 文档ID

# 调用 DeepSeek 生成带出处的回答
.venv/bin/python -m ocs_qa ask 'TB/T 2073-2020 对零部件表面质量有什么要求？' --generate

# 向量化，然后使用混合检索
.venv/bin/python -m ocs_qa embed
.venv/bin/python -m ocs_qa ask '零部件表面缺陷如何处理？' --mode hybrid --generate
```

`--db /路径/kb.sqlite3` 放在子命令前，可使用独立知识库。目录中的 `runtime/` 保存默认数据库与上传副本，已被 Git 忽略。移除知识库文档不会删除原始资料。

## 实验接口

自行核对原文后建立 JSONL 文件，每行一题：

```json
{"question_id":"dev-001","split":"dev","category":"clause","question":"填写实际问题","history":[],"answerable":true,"reference_answer":"填写人工核验的答案","evidence_units":[{"document_id":"填写导入后的文档SHA-256","location":"PDF第7页","quote":"填写该位置中的准确连续原文"}]}
```

不可回答问题设 `answerable=false`、`evidence_units=[]`。历史字段使用前序 `question` 和可选 `resolved_query`，不把模型回答当事实证据。此示例是结构说明，不能直接用作已标注评测题。

```bash
.venv/bin/python -m ocs_qa evaluate /路径/dev.jsonl --mode bm25 --output project/qa_system/outputs/bm25.jsonl
.venv/bin/python -m ocs_qa evaluate /路径/dev.jsonl --mode dense --output project/qa_system/outputs/dense.jsonl
.venv/bin/python -m ocs_qa evaluate /路径/dev.jsonl --mode hybrid --generate --output project/qa_system/outputs/hybrid.jsonl
# 消融：分别添加 --no-edition-filter 或 --no-evidence-check
```

输出包含每题结果及同名 `.summary.json`。已有结果不会覆盖。Recall@5 按 gold 证据单元覆盖计算，MRR@5 为首个正确证据的排名倒数；必须同时满足文档、位置与原文片段匹配，仅同页不算命中。分母为 0 输出 null。证据门槛之前的检索结果单独保存，拒答题不会被移出检索评测分母。

正式 100 题人工标注集尚未构建，不用合成测试数据充当论文实验。详见上层 `开题材料/03_实验与验收方案.md`。

## 测试与边界

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest project/qa_system/tests -q
```

测试涵盖文件定位、扫描页报告、去重、版本缺失/歧义、追问、无关问题拒答、云处理许可、引用伪造、向量维度/模型切换、DeepSeek 请求结构和失败响应、评测公式，以及 Streamlit 提问与清空会话流程。模型契约测试使用模拟 HTTP 响应，不消耗 API 额度，不代表真实在线服务已验证。

词面/余弦门槛未经开发集校准；不能视为置信概率。引用编号和摘录可验证“来源确实存在”，**不能自动证明每条陈述在语义上被充分支持**。复杂追问、复杂 PDF 排版、跨页表格、OCR、标准有效性核验仍需补充。初版追问使用规则，不能代替完整的对话理解。

## 来源与个人工作记录

算法路线沿用资料包中的 BM25 + 向量融合 RAG 思路。实现参考来源：`毕设资料/01_主要代码/vector_store.py`、`document_parser.py`、`rag_pipeline.py`。新模块补充了持久化、来源定位、版本约束、DeepSeek 接口、输出校验、隔离会话、管理界面及评测入口。不要将通用 RAG/BM25 算法写成个人原创；实际改动与验证情况以 Git 和测试记录为准。
