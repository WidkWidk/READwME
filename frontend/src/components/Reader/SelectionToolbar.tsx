interface SelectionToolbarProps {
  rect: DOMRect | null
  onExplain: () => void
  onTranslate: () => void
  onNote: () => void
}

/** 选中文本后浮动工具栏 — 绝对定位在选区上方 */
export function SelectionToolbar({ rect, onExplain, onTranslate, onNote }: SelectionToolbarProps) {
  if (!rect) return null

  // 计算位置：选区上方居中
  const top = rect.top + window.scrollY - 48
  const left = rect.left + window.scrollX + rect.width / 2

  return (
    <div
      className="fixed z-50 flex items-center gap-1 px-2 py-1.5 bg-white rounded-lg shadow-lg border border-gray-200"
      style={{ top: rect.top - 48, left: rect.left + rect.width / 2, transform: 'translateX(-50%)' }}
    >
      <button
        onClick={onExplain}
        className="px-2 py-1 text-sm rounded hover:bg-blue-50 transition-colors"
        title="解释"
      >
        💡 解释
      </button>
      <button
        onClick={onTranslate}
        className="px-2 py-1 text-sm rounded hover:bg-green-50 transition-colors"
        title="翻译"
      >
        📖 翻译
      </button>
      <button
        onClick={onNote}
        className="px-2 py-1 text-sm rounded hover:bg-yellow-50 transition-colors"
        title="记录"
      >
        📝 记录
      </button>
    </div>
  )
}
