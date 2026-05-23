import { useState, useEffect } from 'react'
import type { DictResult } from '../../types'
import { lookupWord } from '../../services/api'

interface DictCardProps {
  word: string
  onClose: () => void
  /** 点击"记笔记"时回调，传入格式化后的笔记内容 */
  onNote: (content: string) => void
}

/** 词典弹窗 — 居中遮罩，显示音标+释义，支持关闭和记笔记 */
export function DictCard({ word, onClose, onNote }: DictCardProps) {
  const [result, setResult] = useState<DictResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 查询词典
  useEffect(() => {
    setLoading(true)
    setError(null)
    setResult(null)
    lookupWord(word)
      .then(setResult)
      .catch(() => setError('查询失败，请重试'))
      .finally(() => setLoading(false))
  }, [word])

  // 将查询结果格式化为笔记内容
  const handleNote = () => {
    if (!result) return
    const lines = [`**${result.word}**${result.phonetic ? `  ${result.phonetic}` : ''}`]
    result.meanings.forEach((m) => {
      lines.push(`\n[${m.part_of_speech}]`)
      m.definitions.forEach((d, i) => {
        lines.push(`${i + 1}. ${d.definition}`)
        if (d.example) lines.push(`   例：${d.example}`)
      })
    })
    onNote(lines.join('\n'))
  }

  return (
    // 遮罩层 — 点击遮罩关闭
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`词典：${word}`}
    >
      {/* 弹窗卡片 — 阻止冒泡避免误关闭 */}
      <div
        className="bg-white rounded-xl shadow-2xl w-full max-w-sm mx-4 p-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 标题栏 */}
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-800 truncate">{word}</h2>
          <button
            onClick={onClose}
            className="ml-2 shrink-0 text-gray-400 hover:text-gray-600 text-2xl leading-none"
            aria-label="关闭"
          >
            ×
          </button>
        </div>

        {/* 加载中 */}
        {loading && (
          <div className="text-center py-8 text-gray-400 text-sm">查询中...</div>
        )}

        {/* 查询失败 */}
        {error && (
          <div className="text-center py-8 text-red-400 text-sm">{error}</div>
        )}

        {/* 查询结果 */}
        {result && !loading && (
          <div className="space-y-3">
            {/* 音标 */}
            {result.phonetic && (
              <p className="text-blue-500 text-sm font-mono">{result.phonetic}</p>
            )}
            {/* 释义列表 */}
            <div className="space-y-3 max-h-56 overflow-auto pr-1">
              {result.meanings.map((m, i) => (
                <div key={i}>
                  <span className="inline-block text-xs font-semibold text-white bg-gray-400 rounded px-1.5 py-0.5 uppercase">
                    {m.part_of_speech}
                  </span>
                  <ol className="mt-1.5 space-y-1.5 list-decimal list-inside">
                    {m.definitions.map((d, j) => (
                      <li key={j} className="text-sm text-gray-700">
                        {d.definition}
                        {d.example && (
                          <p className="text-xs text-gray-400 italic mt-0.5 ml-4">{d.example}</p>
                        )}
                      </li>
                    ))}
                  </ol>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex gap-2 mt-4 pt-3 border-t">
          <button
            onClick={handleNote}
            disabled={!result}
            className="flex-1 py-2 text-sm bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 disabled:opacity-40 transition-colors"
          >
            📝 记笔记
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-2 text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  )
}
