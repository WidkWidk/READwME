"""Session CRUD 路由"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import SessionCreate, SessionResponse
from app.services import session_manager
from app.services.vault_adapter import VaultAdapter

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
vault = VaultAdapter()


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate) -> SessionResponse:
    """创建新的阅读 session"""
    session = await session_manager.create_session(body.title)
    vault.create_session_folder(body.title)
    return session


@router.get("", response_model=list[SessionResponse])
async def list_sessions() -> list[SessionResponse]:
    """列出所有 session"""
    return await session_manager.list_sessions()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """获取 session 详情"""
    session = await session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session 不存在")
    return session


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    """删除 session"""
    session = await session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session 不存在")
    await session_manager.update_session(session_id, status="deleted")
