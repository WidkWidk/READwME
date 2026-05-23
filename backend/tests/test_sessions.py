"""Session CRUD 接口测试"""

import pytest
from httpx import AsyncClient


async def test_create_session(client: AsyncClient) -> None:
    """测试创建 session"""
    resp = await client.post("/api/sessions", json={"title": "测试书目"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "测试书目"
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data


async def test_create_session_empty_title(client: AsyncClient) -> None:
    """测试空标题被拒绝"""
    resp = await client.post("/api/sessions", json={"title": ""})
    assert resp.status_code == 422


async def test_list_sessions_empty(client: AsyncClient) -> None:
    """测试空列表"""
    resp = await client.get("/api/sessions")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_sessions(client: AsyncClient) -> None:
    """测试列出多个 session"""
    await client.post("/api/sessions", json={"title": "Book A"})
    await client.post("/api/sessions", json={"title": "Book B"})
    resp = await client.get("/api/sessions")
    assert resp.status_code == 200
    titles = [s["title"] for s in resp.json()]
    assert "Book A" in titles
    assert "Book B" in titles


async def test_get_session(client: AsyncClient) -> None:
    """测试获取单个 session"""
    create_resp = await client.post("/api/sessions", json={"title": "Book C"})
    session_id = create_resp.json()["id"]

    resp = await client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == session_id
    assert resp.json()["title"] == "Book C"


async def test_get_session_not_found(client: AsyncClient) -> None:
    """测试获取不存在的 session 返回 404"""
    resp = await client.get("/api/sessions/nonexistent-id")
    assert resp.status_code == 404
    assert "不存在" in resp.json()["detail"]


async def test_delete_session(client: AsyncClient) -> None:
    """测试软删除 session"""
    create_resp = await client.post("/api/sessions", json={"title": "Book D"})
    session_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/sessions/{session_id}")
    assert del_resp.status_code == 204

    # 状态变为 deleted
    get_resp = await client.get(f"/api/sessions/{session_id}")
    assert get_resp.json()["status"] == "deleted"


async def test_delete_session_not_found(client: AsyncClient) -> None:
    """测试删除不存在的 session 返回 404"""
    resp = await client.delete("/api/sessions/nonexistent-id")
    assert resp.status_code == 404
