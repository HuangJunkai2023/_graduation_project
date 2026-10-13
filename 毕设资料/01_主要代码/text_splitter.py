"""轻量文本切分器（递归字符切分）。

实现思路与 LangChain 的 RecursiveCharacterTextSplitter 一致：
1. 按"段落 -> 换行 -> 句号 -> 分号 -> 逗号 -> 空格 -> 字符"的优先级，
   递归地把长文本切成不超过 chunk_size 的片段；
2. 再把相邻的小片段合并回 chunk_size 大小，并保留 chunk_overlap 的重叠，
   避免把完整语义切碎、也避免相邻块之间丢失上下文。

这样切出来的块既保持语义相对完整，又控制了长度，便于做强语义检索。
"""

from typing import List, Optional

DEFAULT_SEPARATORS = ["\n\n", "\n", "。", "；", "！", "？", "，", " ", ""]


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
    separators: Optional[List[str]] = None,
) -> List[str]:
    """把长文本切成带重叠的文本块。"""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    separators = separators or DEFAULT_SEPARATORS
    pieces = _split_recursive(text, separators, chunk_size)
    return _merge(pieces, chunk_size, chunk_overlap)


def _split_recursive(text: str, separators: List[str], chunk_size: int) -> List[str]:
    """按分隔符优先级递归切分。"""
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        # 兜底：没有任何分隔符时，直接按字符硬切
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    sep, rest = separators[0], separators[1:]

    # 当前分隔符在文本中不存在，则降级到下一个分隔符
    if sep not in text:
        return _split_recursive(text, rest, chunk_size)

    pieces: List[str] = []
    parts = text.split(sep)
    for index, part in enumerate(parts):
        # 除最后一段外，把分隔符补回片段尾部，尽量保留原有标点
        if index < len(parts) - 1:
            part = part + sep
        if not part:
            continue
        if len(part) <= chunk_size:
            pieces.append(part)
        else:
            pieces.extend(_split_recursive(part, rest, chunk_size))
    return pieces


def _merge(pieces: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
    """把切碎的小片段合并成不超过 chunk_size 的块，并保留重叠。"""
    chunks: List[str] = []
    current = ""

    for piece in pieces:
        if not current:
            current = piece
        elif len(current) + len(piece) <= chunk_size:
            current += piece
        else:
            chunks.append(current)
            # 用上一块尾部的一部分作为下一块开头，形成上下文重叠
            overlap = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            current = overlap + piece

        # 单块已经达到上限就立刻落盘，避免超长
        if len(current) >= chunk_size:
            chunks.append(current)
            current = ""

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]
