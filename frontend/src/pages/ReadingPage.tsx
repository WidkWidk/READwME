import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import type { Session, Paragraph } from '../types'
import { getSessions, getDocumentContent, takeNote } from '../services/api'
import { useTextSelection } from '../hooks/useTextSelection'
import { SelectionToolbar } from '../components/Reader/SelectionToolbar'
import { TxtReader } from '../components/Reader/TxtReader'
import { PdfReader } from '../components/Reader/PdfReader'
import { ChatPanel } from '../components/Chat/ChatPanel'
import type { ChatPanelHandle } from '../components/Chat/ChatPanel'
import { DictCard } from '../components/Dictionary/DictCard'
import { NotesSidebar } from '../components/Notes/NotesSidebar'
import type { LocalNote } from '../components/Notes/NotesSidebar'

type Tab = 'read' | 'chat' | 'notes'

/** 底部 tab 配置 */
const TABS: { id: Tab; icon: string; label: string }[] = [
  { id: 'read',  icon: '📖', label: '阅读' },
  { id: 'chat',  icon: '💬', label: '对话' },
  { id: 'notes', icon: '📝', label: '笔记' },
]

/** 完整阅读页 — 移动端底部 tab 切换，桌面端三栏布局 */
export function ReadingPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const chatRef = useRef<ChatPanelHandle>(null)

  // Session 基本信息
  const [session, setSession] = useState<Session | null>(null)
  // TXT 文档段落列表
  const [paragraphs, setParagraphs] = useState<Paragraph[]>([])
  const [loading, setLoading] = useState(true)

  // 移动端当前激活的 tab
  const [activeTab, setActiveTab] = useState<Tab>('read')

  // 词典弹窗：查词内容 + 触发时的原文（记笔记时回填 sourceText）
  const [dictWord, setDictWord] = useState<string | null>(null)
  const [dictSource, setDictSource] = useState('')

  // 本地笔记列表（同时异步持久化到后端）
  const [notes, setNotes] = useState<LocalNote[]>([])

  // 文本选择状态
  const { text: selText, rect: selRect, isActive: hasSelection, clear: clearSel } = useTextSelection()

  // 加载 session 信息及文档内容
  useEffect(() => {
    if (!sessionId) return
    let cancelled = false
    ;(async () => {
      try {
        const sessions = await getSessions()
        if (cancelled) return
        const s = sessions.find((s) => s.id === sessionId) ?? null
        setSession(s)
        // PDF 由 PdfReader 自行加载，TXT 需要预取段落
        if (s && s.doc_type !== 'pdf') {
          const content = await getDocumentContent(sessionId)
          if (!cancelled) setParagraphs(content.paragraphs)
        }
      } catch (e) {
        console.error('加载文档失败', e)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [sessionId])

  // ——— 工具栏操作处理 ———

  /** 解释：将选中文本发送到对话面板 */
  const handleExplain = () => {
    if (!selText) return
    chatRef.current?.sendExplain(selText)
    clearSel()
    setActiveTab('chat')
  }

  /** 翻译：打开词典弹窗，保存原文供后续记笔记使用 */
  const handleTranslate = () => {
    if (!selText) return
    setDictSource(selText)
    setDictWord(selText.trim())
    clearSel()
  }

  /** 记录笔记：content 由 DictCard 传入时为格式化内容，否则直接用选中文本 */
  const handleNote = async (content?: string, sourceText?: string) => {
    if (!sessionId) return
    const noteContent = content ?? selText
    if (!noteContent) return
    const newNote: LocalNote = {
      id: Date.now().toString(),
      content: noteContent,
      sourceText: sourceText ?? selText,
      createdAt: new Date().toLocaleString('zh-CN'),
    }
    setNotes((prev) => [newNote, ...prev])
    clearSel()
    setActiveTab('notes')
    // 异步持久化，失败不影响本地展示
    takeNote(sessionId, noteContent, newNote.sourceText).catch(console.error)
  }

  /** 根据文档类型渲染对应阅读器 */
  const renderReader = () => {
    if (loading) {
      return <div className="flex items-center justify-center h-full text-gray-400">加载中...</div>
    }
    if (!session) {
      return <div className="flex items-center justify-center h-full text-gray-400">未找到文档</div>
    }
    if (session.doc_type === 'pdf') {
      return <PdfReader url={`/api/documents/${sessionId}/file`} />
    }
    return <TxtReader paragraphs={paragraphs} />
  }

  if (!sessionId) return null

  return (
    <div className="h-full flex flex-col">
      {/* 顶部导航栏 */}
      <header className="flex items-center px-4 py-3 border-b bg-white shrink-0">
        <button
          onClick={() => navigate('/')}
          className="mr-3 text-gray-500 hover:text-gray-700 text-lg"
          aria-label="返回首页"
        >
          ←
        </button>
        <h1 className="font-medium truncate text-gray-800">
          {session?.title ?? '阅读中'}
        </h1>
      </header>

      {/* 主内容区 */}
      <div className="flex-1 overflow-hidden relative">

        {/* ── 桌面端：三栏布局 (>=md) ── */}
        <div className="hidden md:flex h-full">
          {/* 笔记侧栏 250px */}
          <div className="w-[250px] shrink-0 h-full overflow-hidden border-r">
            <NotesSidebar notes={notes} />
          </div>
          {/* 阅读器 flex-1 */}
          <div className="flex-1 h-full overflow-hidden">
            {renderReader()}
          </div>
          {/* 对话面板 350px */}
          <div className="w-[350px] shrink-0 h-full overflow-hidden border-l">
            <ChatPanel ref={chatRef} sessionId={sessionId} />
          </div>
        </div>

        {/* ── 移动端：tab 内容区 (<md) ── */}
        <div className="md:hidden h-full">
          <div className={activeTab === 'read'  ? 'h-full' : 'hidden'}>
            {renderReader()}
          </div>
          <div className={activeTab === 'chat'  ? 'h-full' : 'hidden'}>
            <ChatPanel ref={chatRef} sessionId={sessionId} />
          </div>
          <div className={activeTab === 'notes' ? 'h-full' : 'hidden'}>
            <NotesSidebar notes={notes} />
          </div>
        </div>

        {/* 文本选择浮动工具栏 */}
        {hasSelection && selRect && (
          <SelectionToolbar
            rect={selRect}
            onExplain={handleExplain}
            onTranslate={handleTranslate}
            onNote={() => handleNote()}
          />
        )}
      </div>

      {/* 移动端底部 tab 栏 */}
      <nav className="md:hidden flex border-t bg-white shrink-0" aria-label="页面导航">
        {TABS.map(({ id, icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex-1 flex flex-col items-center py-2 text-xs transition-colors ${
              activeTab === id ? 'text-blue-500' : 'text-gray-400 hover:text-gray-600'
            }`}
            aria-current={activeTab === id ? 'page' : undefined}
          >
            <span className="text-xl">{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* 词典弹窗 */}
      {dictWord && (
        <DictCard
          word={dictWord}
          onClose={() => setDictWord(null)}
          onNote={(content) => {
            handleNote(content, dictSource)
            setDictWord(null)
          }}
        />
      )}
    </div>
  )
}



