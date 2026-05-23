import { useState, useEffect, useCallback } from 'react'
import type { TextSelection } from '../types'

/** 监听文本选择事件，返回选中文本和位置 */
export function useTextSelection(): TextSelection & { clear: () => void } {
  const [selection, setSelection] = useState<TextSelection>({ text: '', rect: null, isActive: false })

  const handleSelectionChange = useCallback(() => {
    const sel = window.getSelection()
    if (sel && sel.toString().trim().length > 0) {
      const range = sel.getRangeAt(0)
      const rect = range.getBoundingClientRect()
      setSelection({ text: sel.toString().trim(), rect, isActive: true })
    }
  }, [])

  const clear = useCallback(() => {
    window.getSelection()?.removeAllRanges()
    setSelection({ text: '', rect: null, isActive: false })
  }, [])

  useEffect(() => {
    document.addEventListener('mouseup', handleSelectionChange)
    document.addEventListener('touchend', handleSelectionChange)
    return () => {
      document.removeEventListener('mouseup', handleSelectionChange)
      document.removeEventListener('touchend', handleSelectionChange)
    }
  }, [handleSelectionChange])

  return { ...selection, clear }
}
