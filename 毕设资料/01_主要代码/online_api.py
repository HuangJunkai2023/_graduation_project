"""在线 API 封装层。

把"向量化"和"对话生成"两类外部能力封装成稳定的本地接口，
后续即使更换供应商（智谱 / DeepSeek / 通义 / OpenAI 兼容网关），
只需要改这一个文件，检索与问答逻辑都不用动。
"""

from typing import List, Optional

try:
    from .config import Config
except ImportError:  # 允许以脚本方式直接运行
    from config import Config


class OnlineClient:
    """封装在线 embedding 与 chat 接口。"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        if not self.config.ZHIPUAI_API_KEY:
            raise RuntimeError(
                "未配置 ZHIPUAI_API_KEY。请复制 .env.example 为 .env，并填入你的在线 API Key。"
            )
        # 延迟导入：这样即使本机未安装 SDK，也能对检索算法做离线自检
        from zhipuai import ZhipuAI

        self.client = ZhipuAI(api_key=self.config.ZHIPUAI_API_KEY)

    # ------------------------------------------------------------------
    # 向量化
    # ------------------------------------------------------------------
    def embed(self, texts: List[str]) -> List[List[float]]:
        """批量把文本转成向量（在线 embedding 接口）。

        注意：接口对单次批量大小有限制，调用方应分批传入。
        """
        if not texts:
            return []
        response = self.client.embeddings.create(
            model=self.config.EMBEDDING_MODEL,
            input=texts,
        )
        # 接口返回顺序与输入顺序一致
        return [item.embedding for item in response.data]

    def embed_one(self, text: str) -> List[float]:
        """单条文本向量化。"""
        vectors = self.embed([text])
        return vectors[0] if vectors else []

    # ------------------------------------------------------------------
    # 对话生成
    # ------------------------------------------------------------------
    def chat(self, prompt: str, system: Optional[str] = None) -> str:
        """调用在线对话模型，返回完整回答文本。"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.config.LLM_MODEL,
            messages=messages,
            temperature=self.config.LLM_TEMPERATURE,
            max_tokens=self.config.LLM_MAX_TOKENS,
        )
        message = response.choices[0].message
        return message.content or ""
