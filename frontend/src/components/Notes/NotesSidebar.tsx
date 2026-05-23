/** 本地笔记条目（不依赖后端返回结构） */
export interface LocalNote {
  id: string
  content: string
  /** 笔记来源的原文片段 */
  sourceText: string
  createdAt: string
}

interface NotesSidebarProps {
  notes: LocalNote[]
}

/** 笔记侧栏 — 显示本次阅读中记录的笔记列表 */
export function NotesSidebar({ notes }: NotesSidebarProps) {
  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* 标题栏 */}
      <div className="px-4 py-3 border-b bg-white shrink-0">
        <h2 className="font-medium text-gray-700 text-sm flex items-center gap-1.5">
          <span>📝</span>
          <span>笔记</span>
          {notes.length > 0 && (
            <span className="ml-auto text-xs text-gray-400">{notes.length} 条</span>
          )}
        </h2>
      </div>

      {/* 笔记列表 */}
      <div className="flex-1 overflow-auto p-3 space-y-3">
        {notes.length === 0 ? (
          // 空状态提示
          <div className="text-center text-gray-400 mt-10 space-y-1">
            <p className="text-2xl">🗒️</p>
            <p className="text-sm">暂无笔记</p>
            <p className="text-xs">选中文本点击"记录"添加笔记</p>
          </div>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className="bg-white rounded-lg p-3 shadow-sm border border-gray-100"
            >
              {/* 来源原文 */}
              {note.sourceText && (
                <p className="text-xs text-gray-400 italic mb-1.5 line-clamp-2 border-l-2 border-yellow-300 pl-2">
                  {note.sourceText}
                </p>
              )}
              {/* 笔记内容 */}
              <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {note.content}
              </p>
              {/* 时间戳 */}
              <p className="text-xs text-gray-300 mt-1.5 text-right">{note.createdAt}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
