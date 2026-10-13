"""文档解析模块。

把 PDF / DOCX 文档解析成"纯文本"，并在解析阶段抽取标准文档的关键元数据
（标准号、文件名、页码），供后续切块、入库和检索过滤使用。

工程实践中，规范类 PDF 抽取出来的文本经常带有噪声，例如：
- 中文字符之间被插入空格："接 触 网 零 部 件"
- 控制字符、全角空格、连续空行
所以这里先做文本清洗，再返回结构化结果。
"""

import os
import re
from typing import Dict, Iterator, List, Optional

import fitz  # PyMuPDF
from docx import Document

# 识别 TB/T、Q/CR、GB/T 等标准号（允许带部分号和年份）
STANDARD_PATTERN = re.compile(
    r"((?:Q\s*/\s*CR|TB\s*/\s*T|GB\s*/\s*T|TB|GB)\s*\d+(?:\.\d+)*(?:\s*[-—]\s*\d{4})?)",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """清洗文档抽取文本中的常见噪声。"""
    if not text:
        return ""
    # 全角空格 -> 半角
    text = text.replace("\u3000", " ")
    # 去掉控制字符
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    # 合并中文字符之间被误插入的空格（"接 触 网" -> "接触网"）
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", text)
    # 合并多余空格与空行
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_standard_no(raw: str) -> str:
    """把标准号归一化成便于匹配的紧凑形式，例如 TB/T 2075-2024 -> TBT20752024。"""
    if not raw:
        return ""
    text = raw.upper()
    text = re.sub(r"\s+", "", text)
    text = text.replace("—", "-")
    text = text.replace("TB/T", "TBT").replace("Q/CR", "QCR").replace("GB/T", "GBT")
    return text


def extract_metadata(file_path: str, text: str, page: Optional[int] = None) -> Dict:
    """从文件名和正文开头抽取元数据。"""
    file_name = os.path.basename(file_path)
    # 优先从文件名识别标准号；文件名没有再看正文前 200 字
    match = STANDARD_PATTERN.search(file_name) or STANDARD_PATTERN.search(text[:200])
    return {
        "file_name": file_name,
        "page": page,
        "standard_no": normalize_standard_no(match.group(1)) if match else "",
    }


def parse_pdf(file_path: str) -> List[Dict]:
    """解析 PDF，按页返回文本（每一页作为一个 Doc）。"""
    docs: List[Dict] = []
    with fitz.open(file_path) as pdf:
        for page_index, page in enumerate(pdf, start=1):
            raw = page.get_text("text")
            content = clean_text(raw)
            if len(content) < 20:
                # 文本过少的页面大概率是空白页或扫描页（扫描页需 OCR，本实现从略）
                continue
            docs.append(
                {
                    "content": content,
                    "metadata": extract_metadata(file_path, content, page=page_index),
                }
            )
    return docs


def parse_docx(file_path: str) -> List[Dict]:
    """解析 DOCX，返回正文段落与表格文本。"""
    document = Document(file_path)
    parts: List[str] = []
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text)

    # 表格内容：用制表符连接单元格，尽量保留行列关系
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                parts.append("\t".join(cells))

    content = clean_text("\n".join(parts))
    if not content:
        return []
    return [{"content": content, "metadata": extract_metadata(file_path, content)}]


def parse_file(file_path: str) -> List[Dict]:
    """按扩展名分派解析器。"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext in (".docx", ".doc"):
        return parse_docx(file_path)
    return []


def iter_supported_files(dir_path: str, recursive: bool = True) -> Iterator[str]:
    """遍历目录下所有支持的文档。"""
    if recursive:
        for root, _, files in os.walk(dir_path):
            for name in files:
                if name.lower().endswith((".pdf", ".docx")):
                    yield os.path.join(root, name)
    else:
        for name in os.listdir(dir_path):
            path = os.path.join(dir_path, name)
            if os.path.isfile(path) and name.lower().endswith((".pdf", ".docx")):
                yield path


def parse_directory(dir_path: str, recursive: bool = True) -> List[Dict]:
    """解析整个目录，返回所有文档的文本块。"""
    docs: List[Dict] = []
    for path in iter_supported_files(dir_path, recursive=recursive):
        try:
            docs.extend(parse_file(path))
        except Exception as exc:  # 单个文件失败不影响整体导入
            print(f"[跳过] 解析失败: {path} ({exc!r})")
    return docs
