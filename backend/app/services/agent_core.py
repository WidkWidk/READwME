"""Agent 核心服务 — 封装 LLM 调用、流式输出、笔记写入"""

import json
from datetime import datetime, timezone
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.config import Settings, settings as default_settings
from app.services.session_manager import get_session
from app.services.vault_adapter import VaultAdapter


# ── 系统提示模板 ──────────────────────────────────────────────────────────────

_SYSTEM_BASE = (
    "你是一位专业的阅读伴侣助手，帮助用户深入理解所阅读的书籍。"
    "回答简洁、准确，使用与用户相同的语言。"
)

_SYSTEM_WITH_BOOK = (
    "你是一位专业的阅读伴侣助手，正在帮助用户阅读《{title}》。"
    "回答简洁、准确，使用与用户相同的语言。"
)


class AgentCore:
    """Agent 核心服务，封装所有 LLM 交互逻辑"""

    def __init__(self, cfg: Settings | None = None):
        """初始化 AgentCore，注入配置和依赖服务"""
        cfg = cfg or default_settings
        self.client = AsyncOpenAI(
            base_url=cfg.llm_base_url,
            api_key=cfg.llm_api_key or "placeholder",
        )
        self.model = cfg.llm_model
        self.max_tokens = cfg.llm_max_tokens
        self.temperature = cfg.llm_temperature
        self.vault = VaultAdapter(cfg.vault_path)

    # ── 内部工具 ──────────────────────────────────────────────────────────────

    async def _get_system_prompt(self, session_id: str) -> str:
        """根据 session 信息构造系统提示"""
        session = await get_session(session_id)
        if session:
            return _SYSTEM_WITH_BOOK.format(title=session.title)
        return _SYSTEM_BASE

    async def _stream(
        self, messages: list[dict]
    ) -> AsyncGenerator[str, None]:
        """调用 LLM 流式接口，逐 token yield 内容字符串"""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    # ── 公开接口 ──────────────────────────────────────────────────────────────

    async def explain(
        self,
        session_id: str,
        text: str,
        context_before: str = "",
        context_after: str = "",
    ) -> AsyncGenerator[str, None]:
        """解释选中段落，结合书籍上下文，流式返回"""
        system = await self._get_system_prompt(session_id)

        # 构造带上下文的用户提示
        parts = []
        if context_before:
            parts.append(f"【前文】\n{context_before}")
        parts.append(f"【选中文本】\n{text}")
        if context_after:
            parts.append(f"【后文】\n{context_after}")
        parts.append("请对【选中文本】进行详细解释，包括含义、背景和重要性。")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n\n".join(parts)},
        ]
        async for token in self._stream(messages):
            yield token

    async def summarize(
        self, session_id: str, text: str
    ) -> AsyncGenerator[str, None]:
        """总结段落/章节，流式返回"""
        system = await self._get_system_prompt(session_id)
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": f"请对以下内容进行简洁的总结，提炼核心观点：\n\n{text}",
            },
        ]
        async for token in self._stream(messages):
            yield token

    async def chat(
        self,
        session_id: str,
        message: str,
        history: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """自由对话，携带 session 上下文和历史记录，流式返回"""
        system = await self._get_system_prompt(session_id)

        # 获取最近笔记摘要（最多 5 条）作为上下文
        session = await get_session(session_id)
        note_context = ""
        if session:
            notes = self.vault.list_notes(session.title)[:5]
            if notes:
                note_context = "【已有笔记文件】\n" + "\n".join(notes)

        full_system = system
        if note_context:
            full_system = f"{system}\n\n{note_context}"

        messages: list[dict] = [{"role": "system", "content": full_system}]
        for h in (history or []):
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        async for token in self._stream(messages):
            yield token

    async def take_note(
        self,
        session_id: str,
        content: str,
        note_title: str | None = None,
        source_text: str = "",
    ) -> dict:
        """智能记笔记：LLM 格式化内容后写入 vault，返回写入结果"""
        session = await get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} 不存在")

        # 构造格式化提示
        prompt_parts = [
            "请将以下笔记内容整理为规范的 Markdown 格式。",
            "要求：添加合适的标题（# 开头）、分段清晰、保留原意。",
            "只输出 Markdown 内容，不要额外说明。",
            f"\n【笔记内容】\n{content}",
        ]
        if source_text:
            prompt_parts.append(f"\n【原文引用】\n> {source_text}")

        messages = [
            {"role": "system", "content": _SYSTEM_BASE},
            {"role": "user", "content": "\n".join(prompt_parts)},
        ]

        # 非流式调用，收集完整响应
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=0.3,  # 格式化任务用低温度
            stream=False,
        )
        formatted = response.choices[0].message.content or content

        # 生成文件名
        if not note_title:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            note_title = f"note-{ts}.md"
        elif not note_title.endswith(".md"):
            note_title = f"{note_title}.md"

        note_path = self.vault.write_note(session.title, note_title, formatted)
        rel_path = str(note_path.relative_to(self.vault.vault_path))

        return {
            "success": True,
            "file_path": rel_path,
            "formatted_content": formatted,
        }
