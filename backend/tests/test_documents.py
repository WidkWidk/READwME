"""文档上传与内容获取接口测试"""

import io
from pathlib import Path

import pytest
from httpx import AsyncClient


async def _create_session(client: AsyncClient, title: str = "Test Book") -> str:
    """辅助：创建 session 并返回 id"""
    resp = await client.post("/api/sessions", json={"title": title})
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_upload_txt(client: AsyncClient, sample_txt: Path) -> None:
    """测试上传 TXT 文件"""
    session_id = await _create_session(client, "TXT Book")
    content = sample_txt.read_bytes()

    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("sample.txt", content, "text/plain")},
        data={"session_id": session_id},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["session_id"] == session_id
    assert data["filename"] == "sample.txt"
    assert data["paragraphs"] == 3


async def test_upload_unsupported_type(client: AsyncClient) -> None:
    """测试上传不支持的文件类型返回 400"""
    session_id = await _create_session(client, "Bad File Book")

    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("test.docx", b"fake content", "application/octet-stream")},
        data={"session_id": session_id},
    )
    assert resp.status_code == 400
    assert "仅支持" in resp.json()["detail"]


async def test_upload_session_not_found(client: AsyncClient, sample_txt: Path) -> None:
    """测试上传到不存在的 session 返回 404"""
    content = sample_txt.read_bytes()

    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("sample.txt", content, "text/plain")},
        data={"session_id": "nonexistent-id"},
    )
    assert resp.status_code == 404


async def test_get_document_content(client: AsyncClient, sample_txt: Path) -> None:
    """测试获取文档内容"""
    session_id = await _create_session(client, "Content Book")
    content = sample_txt.read_bytes()

    await client.post(
        "/api/documents/upload",
        files={"file": ("sample.txt", content, "text/plain")},
        data={"session_id": session_id},
    )

    resp = await client.get(f"/api/documents/{session_id}/content")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_paragraphs"] == 3
    assert data["page"] == 1
    assert len(data["paragraphs"]) == 3


async def test_get_document_content_pagination(
    client: AsyncClient, sample_txt: Path
) -> None:
    """测试文档内容分页"""
    session_id = await _create_session(client, "Paged Book")
    content = sample_txt.read_bytes()

    await client.post(
        "/api/documents/upload",
        files={"file": ("sample.txt", content, "text/plain")},
        data={"session_id": session_id},
    )

    resp = await client.get(
        f"/api/documents/{session_id}/content", params={"page": 1, "page_size": 2}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_paragraphs"] == 3
    assert len(data["paragraphs"]) == 2

    resp2 = await client.get(
        f"/api/documents/{session_id}/content", params={"page": 2, "page_size": 2}
    )
    assert resp2.status_code == 200
    assert len(resp2.json()["paragraphs"]) == 1


async def test_get_content_no_document(client: AsyncClient) -> None:
    """测试未上传文档时获取内容返回 404"""
    session_id = await _create_session(client, "Empty Book")
    resp = await client.get(f"/api/documents/{session_id}/content")
    assert resp.status_code == 404


async def test_get_content_session_not_found(client: AsyncClient) -> None:
    """测试 session 不存在时返回 404"""
    resp = await client.get("/api/documents/nonexistent-id/content")
    assert resp.status_code == 404
