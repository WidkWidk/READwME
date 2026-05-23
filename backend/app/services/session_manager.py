"""Session 管理服务 — SQLite 存储"""

import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite

from app.config import settings
from app.models.schemas import SessionResponse


@asynccontextmanager
async def _db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """异步上下文管理器：获取并自动关闭数据库连接"""
    async with aiosqlite.connect(str(settings.db_path)) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn


async def create_session(title: str) -> SessionResponse:
    """创建新的阅读 session"""
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    async with _db() as db:
        await db.execute(
            "INSERT INTO sessions (id, title, created_at, status) VALUES (?, ?, ?, ?)",
            (session_id, title, now, "active"),
        )
        await db.commit()
    return SessionResponse(id=session_id, title=title, created_at=now, status="active")


async def list_sessions() -> list[SessionResponse]:
    """列出所有 session"""
    async with _db() as db:
        cursor = await db.execute("SELECT * FROM sessions ORDER BY created_at DESC")
        rows = await cursor.fetchall()
    return [SessionResponse(**dict(row)) for row in rows]


async def get_session(session_id: str) -> SessionResponse | None:
    """获取单个 session 详情"""
    async with _db() as db:
        cursor = await db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = await cursor.fetchone()
    if row is None:
        return None
    return SessionResponse(**dict(row))


async def update_session(session_id: str, **kwargs) -> bool:
    """更新 session 字段"""
    if not kwargs:
        return False
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [session_id]
    async with _db() as db:
        cursor = await db.execute(f"UPDATE sessions SET {fields} WHERE id = ?", values)
        await db.commit()
        return cursor.rowcount > 0
