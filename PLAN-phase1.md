# 伴读 Agent — Phase 1: Backend 骨架

## 目标

搭建 FastAPI 后端骨架，实现：文档上传/解析（PDF/TXT）、Obsidian Vault 读写、词典翻译服务、Session 管理。所有 API 可通过 curl 验证。

## 技术栈

- Python 3.11, FastAPI, uvicorn
- PyMuPDF (fitz) — PDF 解析
- SQLite + aiosqlite — Session 元数据
- pydantic v2 — 数据模型
- python-multipart — 文件上传
- httpx — 异步 HTTP（词典 fallback）
- pytest + httpx — 测试

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, lifespan
│   ├── config.py            # Settings (vault path, db path, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── sessions.py      # Session CRUD
│   │   ├── documents.py     # Upload + content retrieval
│   │   └── dictionary.py    # 翻译/释义
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_parser.py   # PDF/TXT → 结构化段落
│   │   ├── vault_adapter.py     # Obsidian vault 读写
│   │   ├── dict_service.py      # 词典查询
│   │   └── session_manager.py   # SQLite session 管理
│   └── db.py                # Database init
├── vault/                   # Obsidian vault (dev)
│   └── Reading/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_sessions.py
│   ├── test_documents.py
│   └── test_dictionary.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## API 设计

```
POST   /api/sessions                    → 创建阅读 session
GET    /api/sessions                    → 列出所有 sessions
GET    /api/sessions/{id}               → 获取 session 详情
DELETE /api/sessions/{id}               → 删除 session

POST   /api/documents/upload            → 上传 PDF/TXT（关联 session）
GET    /api/documents/{id}/content      → 获取解析后内容（分页，page/page_size）

POST   /api/dictionary/lookup           → 词典查询（word → 释义+音标）
```

## 施工指引

### 环境
- 工作目录: /workspace/reading-companion/backend
- Python 3.11, 使用 venv
- 端口: 8000 (已映射到宿主机)

### 代码规范
- 类型注解所有公开函数
- Docstring 用中文
- 4 空格缩进
- async 优先
- 错误返回 HTTPException with detail

### 执行顺序
1. 初始化项目 (requirements.txt, pyproject.toml, venv)
2. 实现 config + db + schemas
3. 实现 services (document_parser, vault_adapter, dict_service, session_manager)
4. 实现 routers (sessions, documents, dictionary)
5. 组装 main.py (CORS, lifespan, include routers)
6. 写测试
7. 验证所有测试通过 + 手动 curl 测试

### 关键实现细节

**DocumentParser:**
- PDF: 用 pymupdf 提取文本，按页分段，保留页码
- TXT: 按双换行分段
- 返回 List[Paragraph] 其中 Paragraph = {page: int, index: int, text: str}

**VaultAdapter:**
- vault_path 从 config 读取，默认 ./vault
- create_session_folder(session_id, title) → 创建 Reading/{title}/ 目录
- write_note(session_id, filename, content) → 写 markdown 文件
- read_note(session_id, filename) → 读取
- list_notes(session_id) → 列出所有笔记

**DictService:**
- 使用免费词典 API: https://api.dictionaryapi.dev/api/v2/entries/en/{word}
- 返回: word, phonetic, meanings[{partOfSpeech, definitions[]}]
- 超时 fallback: 返回 "查询失败" 而非报错

**SessionManager:**
- SQLite 表: sessions(id TEXT PK, title TEXT, doc_type TEXT, file_path TEXT, created_at TEXT, status TEXT)
- 文档存储在 vault/Reading/{title}/ 下的 _source/ 子目录
