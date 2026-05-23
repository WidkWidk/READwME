"""数据库初始化模块"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite
from app.config import settings


async def init_db() -> None:
    """初始化数据库，创建必要的表"""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(settings.db_path)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                doc_type TEXT,
                file_path TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            )
        """)
        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """异步上下文管理器：获取数据库连接"""
    async with aiosqlite.connect(str(settings.db_path)) as db:
        db.row_factory = aiosqlite.Row
        yield db

