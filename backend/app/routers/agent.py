"""Agent 路由 — explain / summarize / chat (SSE) / note (JSON)"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import (
    ExplainRequest,
    SummarizeRequest,
    ChatRequest,
    NoteRequest,
    NoteResponse,
)
from app.services.agent_core import AgentCore
from app.services.session_manager import get_session

router = APIRouter(prefix="/api/agent", tags=["agent"])

# 模块级单例，方便测试时 monkeypatch
agent = AgentCore()


def _sse_generator(
    token_stream: AsyncGenerator[str, None],
) -> AsyncGenerator[dict, None]:
    """将 token 流转换为 SSE 事件序列"""

    async def _gen():
        try:
            async for token in token_stream:
                yield {
                    "event": "token",
                    "data": json.dumps({"content": token}, ensure_ascii=False),
                }
            yield {
                "event": "done",
                "data": json.dumps({"content": ""}),
            }
        except Exception as exc:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(exc)}),
            }

    return _gen()


async def _require_session(session_id: str) -> None:
    """校验 session 存在，不存在则抛出 404"""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} 不存在")


@router.post("/explain")
async def explain(req: ExplainRequest):
    """解释选中段落（流式 SSE）"""
    await _require_session(req.session_id)
    stream = agent.explain(
        session_id=req.session_id,
        text=req.text,
        context_before=req.context_before,
        context_after=req.context_after,
    )
    return EventSourceResponse(_sse_generator(stream))


@router.post("/summarize")
async def summarize(req: SummarizeRequest):
    """总结章节/段落（流式 SSE）"""
    await _require_session(req.session_id)
    stream = agent.summarize(session_id=req.session_id, text=req.text)
    return EventSourceResponse(_sse_generator(stream))


@router.post("/chat")
async def chat(req: ChatRequest):
    """自由对话（流式 SSE，带 session 上下文）"""
    await _require_session(req.session_id)
    stream = agent.chat(
        session_id=req.session_id,
        message=req.message,
        history=req.history,
    )
    return EventSourceResponse(_sse_generator(stream))


@router.post("/note", response_model=NoteResponse)
async def note(req: NoteRequest) -> NoteResponse:
    """智能记笔记（JSON 响应，非流式）"""
    await _require_session(req.session_id)
    try:
        result = await agent.take_note(
            session_id=req.session_id,
            content=req.content,
            note_title=req.note_title,
            source_text=req.source_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"记笔记失败: {exc}") from exc
    return NoteResponse(**result)
