# 伴读 Agent — Phase 2: Agent Core + LLM 集成

## 目标

实现 Agent 核心：基于 LLM 的段落解释、章节总结、智能记笔记、对话式交互。支持流式输出(SSE)。

## 技术栈

- openai Python SDK (兼容 Anthropic/DeepSeek 的 OpenAI-compatible API)
- Server-Sent Events (SSE) via sse-starlette
- Agent tools 架构（函数调用模式）

## 新增依赖

```
openai>=1.30.0
sse-starlette>=1.6.0
```

## 新增/修改文件

```
backend/app/
├── services/
│   └── agent_core.py        # Agent 核心：LLM 调用、tools、上下文管理
├── routers/
│   └── agent.py             # Agent API: explain, summarize, chat (SSE)
└── config.py                # 新增 LLM 配置项
```

## API 设计

```
POST /api/agent/explain          → 解释选中段落（流式 SSE）
POST /api/agent/summarize        → 总结章节/段落（流式 SSE）
POST /api/agent/note             → 智能记笔记（agent 格式化后写入 vault）
POST /api/agent/chat             → 自由对话（流式 SSE，带 session 上下文）
```

## 施工指引

### LLM 配置

在 config.py 中新增：
```python
# LLM 配置
llm_base_url: str = "https://www.packyapi.com/v1"  # OpenAI-compatible endpoint
llm_api_key: str = ""  # 从环境变量 LLM_API_KEY 读取
llm_model: str = "deepseek-chat"  # 默认用 deepseek，便宜
llm_max_tokens: int = 2048
llm_temperature: float = 0.7
```

环境变量: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`

### AgentCore 设计

```python
class AgentCore:
    """Agent 核心服务"""

    def __init__(self, config: Settings):
        self.client = AsyncOpenAI(base_url=config.llm_base_url, api_key=config.llm_api_key)
        self.model = config.llm_model
        self.vault = VaultAdapter(config)
        self.session_mgr = SessionManager(config)

    async def explain(self, session_id: str, text: str, context_before: str = "", context_after: str = "") -> AsyncGenerator[str, None]:
        """解释选中段落，结合书籍上下文，流式返回"""
        # 1. 获取 session 信息（书名、类型）
        # 2. 构造 system prompt（你是一个伴读助手，正在帮用户阅读《xxx》）
        # 3. 构造 user prompt（上下文 + 选中文本 + "请解释"）
        # 4. 流式调用 LLM，yield 每个 chunk

    async def summarize(self, session_id: str, text: str) -> AsyncGenerator[str, None]:
        """总结段落/章节"""

    async def chat(self, session_id: str, message: str, history: list[dict] = None) -> AsyncGenerator[str, None]:
        """自由对话，带 session 上下文"""
        # 1. 获取 session 信息
        # 2. 获取最近笔记摘要（最多 5 条）
        # 3. 构造 messages（system + history + user）
        # 4. 流式返回

    async def take_note(self, session_id: str, content: str, note_title: str = None) -> dict:
        """智能记笔记：格式化内容并写入 vault"""
        # 1. 调用 LLM 格式化内容（加标题、整理格式）
        # 2. 写入 vault
        # 3. 返回写入结果
```

### SSE 流式响应格式

```
event: token
data: {"content": "这段话"}

event: token
data: {"content": "的意思是"}

event: done
data: {"content": "", "usage": {"prompt_tokens": 100, "completion_tokens": 50}}

event: error
data: {"error": "LLM 调用失败: timeout"}
```

### Router 实现要点

- 使用 `sse-starlette` 的 `EventSourceResponse`
- explain/summarize/chat 都返回 SSE 流
- take_note 返回普通 JSON（非流式）
- 所有端点需要 session_id 参数

### Schemas 新增

```python
class ExplainRequest(BaseModel):
    session_id: str
    text: str                    # 选中的文本
    context_before: str = ""     # 前文（可选）
    context_after: str = ""      # 后文（可选）

class SummarizeRequest(BaseModel):
    session_id: str
    text: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: list[dict] = []     # [{"role": "user/assistant", "content": "..."}]

class NoteRequest(BaseModel):
    session_id: str
    content: str                 # 要记录的内容
    note_title: str | None = None  # 目标笔记文件名，None 则自动生成
    source_text: str = ""        # 原文引用

class NoteResponse(BaseModel):
    success: bool
    file_path: str               # vault 中的路径
    formatted_content: str       # 格式化后的内容
```

### 测试策略

- Mock openai client，不实际调用 LLM
- 测试 SSE 响应格式正确
- 测试 take_note 写入 vault 正确
- 测试 session 不存在时返回 404

### 执行顺序

1. 安装新依赖 (openai, sse-starlette)
2. 更新 config.py 加 LLM 配置
3. 更新 schemas.py 加新模型
4. 实现 agent_core.py
5. 实现 routers/agent.py
6. 在 main.py 注册新 router
7. 写测试 tests/test_agent.py
8. 确保所有测试通过（包括之前的 21 个）
