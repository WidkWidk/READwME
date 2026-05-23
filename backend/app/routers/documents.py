"""文档上传与内容获取路由"""

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.models.schemas import DocumentContent, Paragraph
from app.services import session_manager
from app.services.document_parser import parse_document
from app.services.vault_adapter import VaultAdapter

router = APIRouter(prefix="/api/documents", tags=["documents"])
vault = VaultAdapter()

_doc_cache: dict[str, list[Paragraph]] = {}


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
) -> dict:
    """上传文档并关联到 session"""
    session = await session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session 不存在")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".pdf", ".txt"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 和 TXT 文件")

    source_dir = vault.get_source_dir(session.title)
    source_dir.mkdir(parents=True, exist_ok=True)
    file_path = source_dir / file.filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    paragraphs = parse_document(file_path)
    _doc_cache[session_id] = paragraphs

    await session_manager.update_session(
        session_id, doc_type=suffix.lstrip("."), file_path=str(file_path)
    )

    return {"session_id": session_id, "filename": file.filename, "paragraphs": len(paragraphs)}


@router.get("/{session_id}/content", response_model=DocumentContent)
async def get_document_content(
    session_id: str,
    page: int = 1,
    page_size: int = 10,
) -> DocumentContent:
    """获取文档解析后的内容（分页）"""
    session = await session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session 不存在")

    if session_id not in _doc_cache:
        if not session.file_path:
            raise HTTPException(status_code=404, detail="该 session 尚未上传文档")
        file_path = Path(session.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文档文件不存在")
        _doc_cache[session_id] = parse_document(file_path)

    paragraphs = _doc_cache[session_id]
    total = len(paragraphs)
    start = (page - 1) * page_size
    end = start + page_size

    return DocumentContent(
        session_id=session_id,
        total_paragraphs=total,
        page=page,
        page_size=page_size,
        paragraphs=paragraphs[start:end],
    )
