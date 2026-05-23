# READwME — 伴读 Agent

一个基于 LLM 的智能伴读助手，帮助你在阅读 PDF/TXT 文档时进行段落解释、词典翻译、智能笔记，底层使用 Obsidian Vault 存储。

## 功能

- 📖 PDF/TXT 文档阅读器（支持文本选择）
- 💡 选中段落 → AI 解释（流式 SSE）
- 📖 选中单词 → 词典翻译（音标 + 释义）
- 📝 智能记笔记（AI 格式化 → 写入 Obsidian Vault）
- 💬 自由对话（带阅读上下文）
- 📱 移动端适配（底部 Tab 切换）
- 🖥️ 桌面端三栏布局

## 技术栈

**后端:** Python 3.11 / FastAPI / PyMuPDF / SQLite / OpenAI SDK

**前端:** React 18 / TypeScript / Vite / TailwindCSS / pdfjs-dist

**存储:** Obsidian Vault (Markdown) + SQLite (元数据)

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

环境变量：
- `LLM_BASE_URL` — LLM API 地址
- `LLM_API_KEY` — API Key
- `LLM_MODEL` — 模型名称（默认 deepseek-chat）

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── routers/      # API 路由 (sessions, documents, dictionary, agent)
│   │   ├── services/     # 业务逻辑 (agent_core, vault_adapter, dict_service, etc.)
│   │   └── models/       # Pydantic schemas
│   ├── tests/            # pytest 测试 (33 passing)
│   └── vault/            # Obsidian Vault (dev)
├── frontend/         # React 前端
│   └── src/
│       ├── components/   # UI 组件 (Reader, Chat, Dictionary, Notes)
│       ├── hooks/        # React hooks (useSSE, useTextSelection, useSession)
│       ├── pages/        # 页面 (HomePage, ReadingPage)
│       └── services/     # API 调用封装
└── PLAN-*.md         # 实施计划文档
```

## License

MIT
