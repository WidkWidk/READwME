import type { ChatMessage } from '../../types'

interface MessageBubbleProps {
  message: ChatMessage
  isStreaming?: boolean
}

/** 消息气泡 — user 右对齐蓝色，assistant 左对齐灰色 */
export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div
        className={`max-w-[80%] px-3 py-2 rounded-lg text-sm whitespace-pre-wrap ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-sm'
            : 'bg-gray-100 text-gray-800 rounded-bl-sm'
        }`}
      >
        {message.content}
        {/* 流式输出时显示闪烁光标 */}
        {isStreaming && (
          <span className="inline-block w-1.5 h-4 ml-0.5 bg-gray-400 animate-pulse rounded-sm" />
        )}
      </div>
    </div>
  )
}
