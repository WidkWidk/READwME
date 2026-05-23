# Reading Companion — Backend

FastAPI 后端骨架，Phase 1。

## 快速启动

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## 运行测试

```bash
cd backend
./venv/bin/python -m pytest tests/ -v
```

## API 端点

| 方法   | 路径                              | 说明                     |
|--------|-----------------------------------|--------------------------|
| POST   | /api/sessions                     | 创建阅读 session         |
| GET    | /api/sessions                     | 列出所有 sessions        |
| GET    | /api/sessions/{id}                | 获取 session 详情        |
| DELETE | /api/sessions/{id}                | 软删除 session           |
| POST   | /api/documents/upload             | 上传 PDF/TXT 文档        |
| GET    | /api/documents/{id}/content       | 获取解析内容（分页）     |
| POST   | /api/dictionary/lookup            | 查询单词释义             |
| GET    | /health                           | 健康检查                 |

## curl 示例

```bash
# 创建 session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"title": "The Great Gatsby"}'

# 上传文档
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/book.txt" \
  -F "session_id=<session_id>"

# 查询单词
curl -X POST http://localhost:8000/api/dictionary/lookup \
  -H "Content-Type: application/json" \
  -d '{"word": "ephemeral"}'
```

## 目录说明

- `app/` — 应用代码
- `vault/` — Obsidian vault（开发用）
- `data/` — SQLite 数据库
- `tests/` — pytest 测试
