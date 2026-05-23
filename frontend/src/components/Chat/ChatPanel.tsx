import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react'
import type { ChatMessage } from '../../types'
import { useSSE } from '../../hooks/useSSE'
import { MessageBubble } from './MessageBubble'

interface ChatPanelProps {
  sessionId: string
}

export type ChatPanelHandle = { sendExplain: (text: string) => void }

/** 对话面板 — 消息列表 + 底部输入框，流式显示 AI 回复 */
export const ChatPanel = forwardRef<ChatPanelHandle, ChatPanelProps>(
function ChatPanel({ sessionId }, ref) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const { content, isStreaming, start } = useSSE()

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, content])

  // 流式内容完成后追加到消息列表
  useEffect(() => {
    if (!isStreaming && content) {
      setMessages((prev) => [...prev, { role: 'assistant', content }])
    }
  }, [isStreaming, content])

  // 发送消息
  const handleSend = () => {
    const text = input.trim()
    if (!text || isStreaming) return
    setInput('')
    const userMsg: ChatMessage = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    start('/api/agent/chat', {
      session_id: sessionId,
      message: text,
      history: [...messages, userMsg]
    })
  }

  /** 外部调用：发送解释请求 */
  const sendExplain = (text: string) => {
    const userMsg: ChatMessage = { role: 'user', content: `请解释：${text}` }
    setMessages((prev) => [...prev, userMsg])
    start('/api/agent/explain', { session_id: sessionId, text })
  }

  // 通过 ref 暴露 sendExplain 给父组件
  useImperativeHandle(ref, () => ({ sendExplain }), [sessionId])

  return (
    <div className="flex flex-col h-full bg-white">
      {/* 消息列表 */}
      <div className="flex-1 overflow-auto p-3">
        {messages.length === 0 && !isStreaming && (
          <div className="text-center text-gray-400 text-sm mt-8">
            选中文本点击"解释"，或直接输入问题
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {/* 流式回复 */}
        {isStreaming && content && (
          <MessageBubble message={{ role: 'assistant', content }} isStreaming />
        )}
        <div ref={bottomRef} />
      </div>
      {/* 输入框 */}
      <div className="border-t p-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="输入问题..."
          className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          disabled={isStreaming}
        />
        <button
          onClick={handleSend}
          disabled={isStreaming || !input.trim()}
          className="px-4 py-2 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 disabled:opacity-40"
        >
          发送
        </button>
      </div>
    </div>
  )
})
