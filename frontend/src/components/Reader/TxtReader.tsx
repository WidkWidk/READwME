import type { Paragraph } from '../../types'

interface TxtReaderProps {
  paragraphs: Paragraph[]
}

/** TXT 阅读器 — 渲染段落列表，支持文本选择 */
export function TxtReader({ paragraphs }: TxtReaderProps) {
  if (paragraphs.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        暂无内容
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto px-6 py-4 select-text">
      <div className="max-w-prose mx-auto space-y-4">
        {paragraphs.map((p) => (
          <p
            key={`${p.page}-${p.index}`}
            className="text-base leading-relaxed text-gray-800"
          >
            {p.text}
          </p>
        ))}
      </div>
    </div>
  )
}
