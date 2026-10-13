"""配置模块：集中读取 .env 中的在线 API 参数与检索参数。

本参考实现刻意去掉了任何"本地模型部署"：
- 文本向量化：调用在线 embedding 接口（默认智谱 embedding-3）
- 答案生成：调用在线对话接口（默认智谱 glm-4-flash）

因此运行本代码只需要一个有效的在线 API Key，不需要在本机下载
bge / torch / transformers 等模型，也不需要本地大模型。
"""

import os

from dotenv import load_dotenv

# 读取同目录下的 .env 文件
load_dotenv()


class Config:
    """运行期配置。所有字段都可以通过 .env 覆盖。"""

    # ---------- 在线 API（智谱开放平台，兼容 OpenAI 风格 SDK）----------
    ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-3")
    LLM_MODEL = os.getenv("LLM_MODEL", "glm-4-flash")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))

    # ---------- 文本切分 ----------
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))

    # ---------- 检索 ----------
    TOP_K = int(os.getenv("TOP_K", "5"))
    BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.4"))
    VECTOR_WEIGHT = float(os.getenv("VECTOR_WEIGHT", "0.6"))

    # ---------- 知识库持久化文件 ----------
    KB_PATH = os.getenv("KB_PATH", os.path.join("kb", "knowledge_base.json"))

    # ---------- 多轮对话记忆 ----------
    MEMORY_ROUNDS = int(os.getenv("MEMORY_ROUNDS", "5"))
