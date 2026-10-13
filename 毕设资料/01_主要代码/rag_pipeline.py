"""RAG 问答链路模块。

负责把「检索到的证据 + 对话记忆 + 用户问题」组织成提示词，
调用在线大模型生成带来源引用的回答，并维护多轮对话记忆。

核心流程（对应论文中的"检索增强生成"章节）：
    用户问题
      -> 抽取标准号等检索线索
      -> 混合检索得到证据片段
      -> 组装上下文与提示词
      -> 在线大模型生成回答
      -> 记录本轮问答到记忆
"""

import re
from collections import deque
from typing import Deque, Dict, List, Optional

try:
    from .config import Config
    from .online_api import OnlineClient
    from .vector_store import VectorStore
except ImportError:
    from config import Config
    from online_api import OnlineClient
    from vector_store import VectorStore

# 从问题中抽取标准号，用于检索时按标准过滤
STANDARD_PATTERN = re.compile(
    r"(?:Q\s*/\s*CR|TB\s*/\s*T|GB\s*/\s*T|TB|GB)\s*\d+(?:\.\d+)*",
    re.IGNORECASE,
)

# 判断是否属于闲聊（闲聊不检索知识库，直接走通用回答）
CHITCHAT_PATTERN = re.compile(
    r"^(你好|您好|嗨|hi|hello|hey|谢谢|感谢|多谢|再见|拜拜|bye|"
    r"你是谁|你叫什么|你能做什么|在吗)[呀啊呢嘛。！？!?]*$",
    re.IGNORECASE,
)

SYSTEM_PROMPT = "你是一个严谨的知识库问答助手，回答必须基于给定的参考文档，不得编造。"


class RAGPipeline:
    """检索增强问答链路。"""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.config = Config()
        self.client = OnlineClient(self.config)
        self.vector_store = vector_store or VectorStore(client=self.client)
        # 多轮记忆：保存最近的 (question, answer)
        self.memory: Deque[Dict[str, str]] = deque(maxlen=self.config.MEMORY_ROUNDS)

    # ------------------------------------------------------------------
    # 检索线索抽取
    # ------------------------------------------------------------------
    def _extract_standard_no(self, question: str) -> str:
        """从问题中抽标准号（例如 TB/T 2075-2024），检索时用于过滤。"""
        match = STANDARD_PATTERN.search(question or "")
        if not match:
            return ""
        text = match.group(0).upper().replace(" ", "")
        return text.replace("TB/T", "TBT").replace("Q/CR", "QCR").replace("GB/T", "GBT")

    @staticmethod
    def _is_chitchat(question: str) -> bool:
        return bool(CHITCHAT_PATTERN.match((question or "").strip()))

    # ------------------------------------------------------------------
    # 上下文与提示词
    # ------------------------------------------------------------------
    def _build_context(self, docs: List[Dict]) -> str:
        """把检索结果拼成带来源标注的上下文。"""
        blocks: List[str] = []
        for index, doc in enumerate(docs, start=1):
            metadata = doc.get("metadata", {})
            source = metadata.get("file_name", "unknown")
            if metadata.get("page"):
                source += f" 第{metadata['page']}页"
            if metadata.get("standard_no"):
                source += f" 标准号:{metadata['standard_no']}"
            blocks.append(f"[来源{index}] {source}\n{doc['content']}")
        return "\n\n".join(blocks)

    def _build_memory_text(self) -> str:
        """把最近若干轮对话整理成记忆文本。"""
        if not self.memory:
            return ""
        lines = [
            f"用户：{turn['question']}\n助手：{turn['answer']}"
            for turn in self.memory
        ]
        return "以下是最近的对话历史，仅用于理解追问中的指代：\n" + "\n".join(lines)

    def _build_rag_prompt(self, question: str, context: str) -> str:
        memory_text = self._build_memory_text()
        memory_block = f"\n{memory_text}\n" if memory_text else ""
        return (
            "请根据下面的参考文档回答用户问题。\n\n"
            f"参考文档：\n{context}\n"
            f"{memory_block}\n"
            f"用户问题：{question}\n\n"
            "回答要求：\n"
            "1. 只依据参考文档作答，不要编造文档中没有的内容；\n"
            "2. 如果文档只覆盖了部分信息，请明确说明哪部分无法确认；\n"
            "3. 回答末尾用 [来源1] 的形式标注依据。"
        )

    def _build_general_prompt(self, question: str) -> str:
        memory_text = self._build_memory_text()
        memory_block = f"\n{memory_text}\n" if memory_text else ""
        return (
            "你是中文助手。当前问题在知识库中未检索到直接相关的文档，"
            "请用一句简短的话说明这一点，然后基于通用能力自然回答。\n"
            f"{memory_block}\n用户问题：{question}"
        )

    # ------------------------------------------------------------------
    # 问答入口
    # ------------------------------------------------------------------
    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[Dict]:
        """仅执行检索，返回证据片段。"""
        standard_no = self._extract_standard_no(question)
        return self.vector_store.search(question, top_k=top_k, standard_no=standard_no)

    def answer(self, question: str, top_k: Optional[int] = None) -> Dict:
        """完整问答：返回 {"answer", "sources"}。"""
        # 1) 闲聊直接走通用回答，不检索
        if self._is_chitchat(question):
            answer = self.client.chat(question)
            self._remember(question, answer)
            return {"answer": answer, "sources": []}

        # 2) 检索证据
        docs = self.retrieve(question, top_k=top_k)

        # 3) 有证据 -> 走 RAG；无证据 -> 走通用回答兜底
        if docs:
            prompt = self._build_rag_prompt(question, self._build_context(docs))
        else:
            prompt = self._build_general_prompt(question)

        answer = self.client.chat(prompt, system=SYSTEM_PROMPT)
        self._remember(question, answer)
        return {"answer": answer, "sources": docs}

    def _remember(self, question: str, answer: str) -> None:
        """记录一轮问答到短期记忆。"""
        self.memory.append({"question": question, "answer": answer})

    def clear_memory(self) -> None:
        self.memory.clear()
