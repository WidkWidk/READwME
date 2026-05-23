# 伴读 Agent — Phase 3: Frontend (React + PDF Reader + Mobile-first)

## 目标

实现前端界面：PDF/TXT 阅读器、文本选择交互、Agent 对话面板、词典翻译卡片、笔记侧栏。移动端优先设计。

## 技术栈

- React 18 + TypeScript + Vite
- TailwindCSS 4 (响应式)
- pdfjs-dist (PDF 渲染 + 文本选择)
- EventSource (SSE 流式接收)
- React Router (页面路由)

## 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── public/
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css              # Tailwind directives
    ├── types/index.ts         # TypeScript 类型定义
    ├── services/
    │   └── api.ts             # 后端 API 调用封装
    ├── hooks/
    │   ├── useTextSelection.ts    # 文本选择 hook
    │   ├── useSSE.ts              # SSE 流式接收 hook
    │   └── useSession.ts          # Session 状态管理
    ├── components/
    │   ├── Layout.tsx             # 响应式布局容器
    │   ├── Reader/
    │   │   ├── PdfReader.tsx      # PDF 渲染 + 文本层
    │   │   ├── TxtReader.tsx      # TXT 渲染
    │   │   └── SelectionToolbar.tsx  # 选中浮动工具栏
    │   ├── Chat/
    │   │   ├── ChatPanel.tsx      # Agent 对话面板
    │   │   └── MessageBubble.tsx  # 消息气泡
    │   ├── Dictionary/
    │   │   └── DictCard.tsx       # 翻译卡片（音标+释义）
    │   ├── Notes/
    │   │   └── NotesSidebar.tsx   # 笔记列表侧栏
    │   └── Session/
    │       ├── SessionList.tsx    # Session 列表页
    │       └── CreateSession.tsx  # 创建 Session（上传文件）
    └── pages/
        ├── HomePage.tsx           # Session 列表
        └── ReadingPage.tsx        # 阅读主界面
```

## 页面设计

### 首页 (HomePage)
- Session 列表卡片
- 右上角 "+" 按钮创建新 session
- 点击 session 进入阅读页

### 阅读页 (ReadingPage) — 移动端
```
┌─────────────────────┐
│  ← 书名             │  ← 顶部导航栏
├─────────────────────┤
│                     │
│  [文档内容区域]      │  ← 可滚动，支持文本选择
│                     │
│  ┌───────────────┐  │
│  │解释│翻译│记录│  │  ← 选中文本后弹出浮动工具栏
│  └───────────────┘  │
│                     │
├─────────────────────┤
│ 📖阅读 │ 💬对话 │ 📝笔记│  ← 底部 Tab 切换
└─────────────────────┘
```

### 阅读页 (ReadingPage) — 桌面端
```
┌──────────┬──────────────┬──────────┐
│  Notes   │   Reader     │   Chat   │
│  250px   │   flex-1     │   350px  │
└──────────┴──────────────┴──────────┘
```

## 施工指引

### 环境
- 工作目录: /workspace/reading-companion/frontend
- Node.js 20, npm
- Dev server 端口: 5173 (已映射)
- 后端 API: http://localhost:8000/api

### npm 配置
- registry: https://registry.npmmirror.com

### 代码规范
- 函数组件 + hooks
- TypeScript strict mode
- 组件文件用 PascalCase
- 中文注释

### 关键实现细节

**PDF 渲染 (PdfReader.tsx):**
- 使用 pdfjs-dist 的 canvas 渲染 + 文本层
- 文本层支持原生文本选择
- 分页加载，显示当前页码
- worker 使用 CDN: https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs

**文本选择 (useTextSelection.ts):**
- 监听 mouseup/touchend 事件
- 获取选中文本 + 位置坐标
- 返回 { text, rect, isActive }
- 点击空白处清除选择

**浮动工具栏 (SelectionToolbar.tsx):**
- 绝对定位，跟随选区位置
- 三个按钮：解释、翻译、记入笔记
- 移动端适配：避免被键盘遮挡

**SSE Hook (useSSE.ts):**
- 接收 SSE 流，逐 token 拼接
- 返回 { content, isStreaming, error }
- 支持取消

**Chat Panel (ChatPanel.tsx):**
- 消息列表 + 输入框
- 流式显示 AI 回复
- 移动端：底部 sheet 模式（从底部滑出）
- 桌面端：右侧固定面板

**词典卡片 (DictCard.tsx):**
- 弹出式卡片
- 显示：单词、音标、词性、释义、例句
- 底部按钮：记入笔记、加入词汇表

### Vite 配置要点
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### 执行顺序
1. 初始化 Vite + React + TS 项目
2. 安装依赖 (tailwindcss, pdfjs-dist, react-router-dom)
3. 配置 Tailwind + Vite proxy
4. 实现 types + api service
5. 实现 hooks (useTextSelection, useSSE, useSession)
6. 实现 Layout + 路由
7. 实现 SessionList + CreateSession
8. 实现 PdfReader + TxtReader
9. 实现 SelectionToolbar
10. 实现 ChatPanel + MessageBubble
11. 实现 DictCard
12. 实现 NotesSidebar
13. 组装 ReadingPage
14. 验证 dev server 启动 + 基本交互可用
