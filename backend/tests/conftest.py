"""测试配置与公共 fixtures"""

import pytest
import pytest_asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport

import app.routers.sessions as sessions_router
import app.routers.documents as documents_router
import app.routers.agent as agent_router
from app.main import app
from app.db import init_db
from app.config import settings
from app.services.vault_adapter import VaultAdapter
from app.services.agent_core import AgentCore


@pytest_asyncio.fixture
async def client(tmp_path, monkeypatch):
    """提供测试用 AsyncClient，使用临时数据库和 vault"""
    # 覆盖数据库路径
    db_path = tmp_path / "data" / "reading.db"
    monkeypatch.setattr(settings, "db_path", db_path)

    # 覆盖 vault 路径
    vault_path = tmp_path / "vault"
    monkeypatch.setattr(settings, "vault_path", vault_path)

    # 替换路由中的 vault 实例
    test_vault = VaultAdapter(vault_path=vault_path)
    monkeypatch.setattr(sessions_router, "vault", test_vault)
    monkeypatch.setattr(documents_router, "vault", test_vault)

    # 替换 agent 实例（使用 tmp vault，避免写入真实路径）
    test_agent = AgentCore(settings)
    monkeypatch.setattr(agent_router, "agent", test_agent)

    # 清空文档缓存，避免测试间污染
    monkeypatch.setattr(documents_router, "_doc_cache", {})

    # 初始化数据库
    await init_db()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_txt(tmp_path) -> Path:
    """创建测试用 TXT 文件"""
    txt = tmp_path / "sample.txt"
    txt.write_text(
        "第一段落内容。\n\n第二段落内容。\n\n第三段落内容。",
        encoding="utf-8",
    )
    return txt
