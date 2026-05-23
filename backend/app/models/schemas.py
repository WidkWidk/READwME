"""Pydantic 数据模型定义"""

from datetime import datetime
from pydantic import BaseModel, Field


class Paragraph(BaseModel):
    """文档段落"""
    page: int
    index: int
    text: str


class SessionCreate(BaseModel):
    """创建 Session 请求"""
    title: str = Field(..., min_length=1, max_length=200)


class SessionResponse(BaseModel):
    """Session 响应"""
    id: str
    title: str
    doc_type: str | None = None
    file_path: str | None = None
    created_at: str
    status: str


class DocumentContent(BaseModel):
    """文档内容响应"""
    session_id: str
    total_paragraphs: int
    page: int
    page_size: int
    paragraphs: list[Paragraph]


class DictLookupRequest(BaseModel):
    """词典查询请求"""
    word: str = Field(..., min_length=1, max_length=100)


class DictDefinition(BaseModel):
    """词典释义"""
    definition: str
    example: str | None = None


class DictMeaning(BaseModel):
    """词典词义"""
    part_of_speech: str
    definitions: list[DictDefinition]


class DictLookupResponse(BaseModel):
    """词典查询响应"""
    word: str
    phonetic: str | None = None
    meanings: list[DictMeaning]
    source: str = "api"


# ── Agent 相关 Schema ──────────────────────────────────────────────────────────

class ExplainRequest(BaseModel):
    """解释段落请求"""
    session_id: str
    text: str                       # 选中的文本
    context_before: str = ""        # 前文（可选）
    context_after: str = ""         # 后文（可选）


class SummarizeRequest(BaseModel):
    """总结段落/章节请求"""
    session_id: str
    text: str                       # 需要总结的文本


class ChatRequest(BaseModel):
    """自由对话请求"""
    session_id: str
    message: str                    # 用户消息
    history: list[dict] = []        # [{"role": "user/assistant", "content": "..."}]


class NoteRequest(BaseModel):
    """智能记笔记请求"""
    session_id: str
    content: str                    # 要记录的内容
    note_title: str | None = None   # 目标笔记文件名，None 则自动生成
    source_text: str = ""           # 原文引用


class NoteResponse(BaseModel):
    """记笔记响应"""
    success: bool
    file_path: str                  # vault 中的路径
    formatted_content: str          # 格式化后的内容
