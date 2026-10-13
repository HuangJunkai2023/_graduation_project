"""Page/paragraph/table provenance, edition parsing and bounded text chunks."""
from pathlib import Path
import hashlib
import re
import zipfile
import pymupdf
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

STANDARD = re.compile(
    r"(?<![A-Z0-9])(?P<prefix>Q[\s/∕]*CR|CJJ(?:[\s/∕-]*T)?|TB(?:[\s/∕-]*T)?|GB(?:[\s/∕-]*T)?)"
    r"\s*(?P<number>\d+(?:\.\d+)*)(?:\s*[-—–]\s*(?P<year>\d{4})(?!\d))?", re.I)


def standards(text):
    return list(dict.fromkeys((re.sub(r"[\s/∕-]", "", m["prefix"]).upper() + m["number"], m["year"] or "") for m in STANDARD.finditer(text)))


def clean(text):
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text).replace("\u3000", " ")
    text = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def split_text(text, size=600, overlap=80):
    if not 0 <= overlap < size: raise ValueError("Invalid overlap")
    start = 0
    while start < len(text):
        end = min(start+size, len(text))
        if end < len(text):
            cut = max(text.rfind(sep, start+size//2, end) for sep in ["\n", "。", "；", "！", "？"])
            if cut >= 0: end = cut+1
        value = text[start:end].strip()
        if value: yield value, start, end
        if end == len(text): break
        start = max(start+1, end-overlap)


def parse_file(path, settings, *, display_name=None, allow_cloud=False, standard_override=None):
    path = Path(path).resolve()
    name = Path(display_name or path.name).name
    if path.suffix.lower() not in (".pdf", ".docx"):
        raise ValueError("只支持 PDF/DOCX；旧版 DOC 请先另存为 DOCX。")
    if path.stat().st_size > 100*1024*1024: raise ValueError("单个文件超过 100 MB 上限。")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    hints = standards(name)
    # Multi-part collections cannot safely be assigned just their first part.
    is_collection = bool(re.search(r"\d[～~]\d", name))
    standard, year = hints[0] if hints and not is_collection else ("", "")
    if standard_override:
        parsed = standards(standard_override)
        if len(parsed) != 1: raise ValueError("手工标准号须为一个有效编号，可带年份。")
        standard, year = parsed[0]
    units, warnings = [], []
    if path.suffix.lower() == ".pdf":
        with pymupdf.open(path) as pdf:
            if pdf.needs_pass: raise ValueError("PDF 已加密，需先提供可读取版本。")
            if len(pdf) > 3000: raise ValueError("PDF 超过 3000 页，请先按分册拆分。")
            for i, page in enumerate(pdf, 1):
                text = clean(page.get_text(sort=True))
                if len(re.sub(r"\s", "", text)) < 30:
                    warnings.append({"location": f"PDF第{i}页", "reason": "文本过少，可能为空白/图表/扫描页，未入库；未执行 OCR。"})
                    continue
                units.append({"text": text, "location": f"PDF第{i}页", "page": i})
    else:
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist()) > 200*1024*1024:
                raise ValueError("DOCX 解压后超过 200 MB 上限。")
        doc = Document(path)
        p_no = t_no = 0
        for child in doc.element.body.iterchildren():
            if child.tag.endswith("}p"):
                p_no += 1
                text = clean(Paragraph(child, doc).text)
                if text: units.append({"text": text, "location": f"段落{p_no}", "page": None})
            elif child.tag.endswith("}tbl"):
                t_no += 1
                table = Table(child, doc)
                for r_no, row in enumerate(table.rows, 1):
                    text = clean(" | ".join(c.text for c in row.cells))
                    if text: units.append({"text": text, "location": f"表格{t_no}第{r_no}行", "page": None})
    if not standard and units and not is_collection:
        found = standards(units[0]["text"][:300])
        if found: standard, year = found[0]
    if not standard: warnings.append({"location": "文件", "reason": "未可靠识别单一标准号，可在导入时手工指定。"})
    state = "draft" if any(x in name for x in ["报批稿", "送审", "讨论稿", "过程稿"]) else "historical" if "作废" in name else "unverified"
    document = {"id": digest, "name": name, "path": str(path), "standard": standard, "year": year,
                "publication_status": state, "allow_cloud": bool(allow_cloud), "warnings": warnings,
                "size_bytes": path.stat().st_size}
    chunks = []
    for unit in units:
        for text, start, end in split_text(unit["text"], settings.chunk_size, settings.chunk_overlap):
            key = f"{digest}:{unit['location']}:{start}:{end}:{text}"
            chunks.append({"id": hashlib.sha256(key.encode()).hexdigest()[:32], "document_id": digest,
                           "text": text, "location": unit["location"], "page": unit["page"], "start": start, "end": end})
    return document, chunks
