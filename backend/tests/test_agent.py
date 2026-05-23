"""Agent 端点测试 — mock openai，不实际调用 LLM"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

import app.routers.agent as agent_router


# ── Mock 工厂 ─────────────────────────────────────────────────────────────────

def _make_stream_chunks(tokens: list[str]):
    """构造模拟的 openai 流式 chunk 列表"""
    chunks = []
    for t in tokens:
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = t
        chunks.append(chunk)
    # 最后一个 chunk content 为 None（流结束标志）
    end_chunk = MagicMock()
    end_chunk.choices = [MagicMock()]
    end_chunk.choices[0].delta.content = None
    chunks.append(end_chunk)
    return chunks


def _make_async_iter(items):
    """将列表包装为异步迭代器"""
    async def _aiter():
        for item in items:
            yield item
    return _aiter()


def _mock_stream_create(tokens: list[str]):
    """返回模拟流式 create 的 coroutine"""
    mock_stream = MagicMock()
    mock_stream.__aiter__ = lambda self: _make_async_iter(
        _make_stream_chunks(tokens)
    )
    async def _create(**kwargs):
        return mock_stream
    return _create


def _mock_nonstream_create(content: str):
    """返回模拟非流式 create 的 coroutine"""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    async def _create(**kwargs):
        return response
    return _create


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_agent(tmp_path, monkeypatch):
    """替换 agent_router.agent 为使用 tmp_path vault 的实例"""
    from app.config import settings
    from app.services.agent_core import AgentCore

    monkeypatch.setattr(settings, "vault_path", tmp_path / "vault")
    new_agent = AgentCore(settings)
    monkeypatch.setattr(agent_router, "agent", new_agent)
    return new_agent


# ── SSE 辅助 ──────────────────────────────────────────────────────────────────

def _parse_sse(text: str) -> list[dict]:
    """解析 SSE 响应文本，返回事件列表 [{"event": ..., "data": ...}]"""
    events = []
    current: dict = {}
    for line in text.splitlines():
        if line.startswith("event:"):
            current["event"] = line[len("event:"):].strip()
        elif line.startswith("data:"):
            current["data"] = json.loads(line[len("data:"):].strip())
        elif line == "" and current:
            events.append(current)
            current = {}
    if current:
        events.append(current)
    return events


# ── /api/agent/explain ────────────────────────────────────────────────────────

async def test_explain_streams_tokens(client: AsyncClient, mock_agent) -> None:
    """测试 explain 端点返回正确的 SSE token 流"""
    # 先创建 session
    resp = await client.post("/api/sessions", json={"title": "测试书"})
    session_id = resp.json()["id"]

    tokens = ["这", "段话", "的意思是"]
    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_stream_create(tokens),
    ):
        resp = await client.post(
            "/api/agent/explain",
            json={"session_id": session_id, "text": "测试文本"},
        )

    assert resp.status_code == 200
    events = _parse_sse(resp.text)
    token_events = [e for e in events if e.get("event") == "token"]
    done_events = [e for e in events if e.get("event") == "done"]

    assert len(token_events) == len(tokens)
    assert [e["data"]["content"] for e in token_events] == tokens
    assert len(done_events) == 1


async def test_explain_with_context(client: AsyncClient, mock_agent) -> None:
    """测试 explain 携带前后文"""
    resp = await client.post("/api/sessions", json={"title": "上下文书"})
    session_id = resp.json()["id"]

    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_stream_create(["ok"]),
    ):
        resp = await client.post(
            "/api/agent/explain",
            json={
                "session_id": session_id,
                "text": "核心文本",
                "context_before": "前文内容",
                "context_after": "后文内容",
            },
        )
    assert resp.status_code == 200


async def test_explain_session_not_found(client: AsyncClient) -> None:
    """测试 explain 传入不存在的 session_id 返回 404"""
    resp = await client.post(
        "/api/agent/explain",
        json={"session_id": "nonexistent", "text": "文本"},
    )
    assert resp.status_code == 404


# ── /api/agent/summarize ──────────────────────────────────────────────────────

async def test_summarize_streams_tokens(client: AsyncClient, mock_agent) -> None:
    """测试 summarize 端点返回 SSE 流"""
    resp = await client.post("/api/sessions", json={"title": "总结书"})
    session_id = resp.json()["id"]

    tokens = ["核心", "观点", "是"]
    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_stream_create(tokens),
    ):
        resp = await client.post(
            "/api/agent/summarize",
            json={"session_id": session_id, "text": "一大段需要总结的文字"},
        )

    assert resp.status_code == 200
    events = _parse_sse(resp.text)
    token_events = [e for e in events if e.get("event") == "token"]
    assert len(token_events) == len(tokens)


async def test_summarize_session_not_found(client: AsyncClient) -> None:
    """测试 summarize 传入不存在的 session_id 返回 404"""
    resp = await client.post(
        "/api/agent/summarize",
        json={"session_id": "ghost", "text": "文本"},
    )
    assert resp.status_code == 404


# ── /api/agent/chat ───────────────────────────────────────────────────────────

async def test_chat_streams_tokens(client: AsyncClient, mock_agent) -> None:
    """测试 chat 端点返回 SSE 流"""
    resp = await client.post("/api/sessions", json={"title": "对话书"})
    session_id = resp.json()["id"]

    tokens = ["你好", "，有什么", "可以帮你？"]
    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_stream_create(tokens),
    ):
        resp = await client.post(
            "/api/agent/chat",
            json={"session_id": session_id, "message": "你好"},
        )

    assert resp.status_code == 200
    events = _parse_sse(resp.text)
    token_events = [e for e in events if e.get("event") == "token"]
    assert len(token_events) == len(tokens)


async def test_chat_with_history(client: AsyncClient, mock_agent) -> None:
    """测试 chat 携带历史记录"""
    resp = await client.post("/api/sessions", json={"title": "历史书"})
    session_id = resp.json()["id"]

    history = [
        {"role": "user", "content": "第一轮问题"},
        {"role": "assistant", "content": "第一轮回答"},
    ]
    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_stream_create(["继续"]),
    ):
        resp = await client.post(
            "/api/agent/chat",
            json={
                "session_id": session_id,
                "message": "继续聊",
                "history": history,
            },
        )
    assert resp.status_code == 200


async def test_chat_session_not_found(client: AsyncClient) -> None:
    """测试 chat 传入不存在的 session_id 返回 404"""
    resp = await client.post(
        "/api/agent/chat",
        json={"session_id": "ghost", "message": "hi"},
    )
    assert resp.status_code == 404


# ── /api/agent/note ───────────────────────────────────────────────────────────

async def test_note_writes_to_vault(client: AsyncClient, mock_agent) -> None:
    """测试 note 端点写入 vault 并返回正确 JSON"""
    resp = await client.post("/api/sessions", json={"title": "笔记书"})
    session_id = resp.json()["id"]

    formatted = "# 笔记标题\n\n整理后的内容。"
    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_nonstream_create(formatted),
    ):
        resp = await client.post(
            "/api/agent/note",
            json={
                "session_id": session_id,
                "content": "原始笔记内容",
                "note_title": "my-note",
            },
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["file_path"].endswith("my-note.md")
    assert data["formatted_content"] == formatted


async def test_note_auto_title(client: AsyncClient, mock_agent) -> None:
    """测试 note 不传 note_title 时自动生成文件名"""
    resp = await client.post("/api/sessions", json={"title": "自动标题书"})
    session_id = resp.json()["id"]

    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_nonstream_create("# 自动\n内容"),
    ):
        resp = await client.post(
            "/api/agent/note",
            json={"session_id": session_id, "content": "内容"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["file_path"].endswith(".md")


async def test_note_with_source_text(client: AsyncClient, mock_agent) -> None:
    """测试 note 携带原文引用"""
    resp = await client.post("/api/sessions", json={"title": "引用书"})
    session_id = resp.json()["id"]

    with patch.object(
        mock_agent.client.chat.completions,
        "create",
        side_effect=_mock_nonstream_create("# 带引用\n> 原文\n\n笔记"),
    ):
        resp = await client.post(
            "/api/agent/note",
            json={
                "session_id": session_id,
                "content": "笔记内容",
                "source_text": "原文引用段落",
            },
        )
    assert resp.status_code == 200


async def test_note_session_not_found(client: AsyncClient) -> None:
    """测试 note 传入不存在的 session_id 返回 404"""
    resp = await client.post(
        "/api/agent/note",
        json={"session_id": "ghost", "content": "内容"},
    )
    assert resp.status_code == 404
