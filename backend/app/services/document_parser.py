"""文档解析服务 — 支持 PDF 和 TXT"""

from pathlib import Path

import fitz

from app.models.schemas import Paragraph


def parse_pdf(file_path: Path) -> list[Paragraph]:
    """解析 PDF 文件，按页提取文本段落"""
    paragraphs: list[Paragraph] = []
    doc = fitz.open(str(file_path))
    idx = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if text:
            paragraphs.append(Paragraph(page=page_num + 1, index=idx, text=text))
            idx += 1
    doc.close()
    return paragraphs


def parse_txt(file_path: Path) -> list[Paragraph]:
    """解析 TXT 文件，按双换行分段"""
    content = file_path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    paragraphs: list[Paragraph] = []
    for idx, block in enumerate(blocks):
        paragraphs.append(Paragraph(page=1, index=idx, text=block))
    return paragraphs


def parse_document(file_path: Path) -> list[Paragraph]:
    """根据文件类型自动选择解析器"""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")
