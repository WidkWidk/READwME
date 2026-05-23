import { useRef, useState, useEffect, useCallback } from 'react'
import * as pdfjsLib from 'pdfjs-dist'

// 设置 PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs'

interface PdfReaderProps {
  url: string
  onPageChange?: (page: number) => void
}

/** PDF 阅读器组件 — 支持 canvas 渲染 + 文本层选择 */
export function PdfReader({ url, onPageChange }: PdfReaderProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const textLayerRef = useRef<HTMLDivElement>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [pdfDoc, setPdfDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null)
  const [loading, setLoading] = useState(true)

  // 加载 PDF 文档
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    pdfjsLib.getDocument(url).promise.then((doc) => {
      if (!cancelled) {
        setPdfDoc(doc)
        setTotalPages(doc.numPages)
        setLoading(false)
      }
    }).catch((err) => {
      console.error('PDF 加载失败:', err)
      setLoading(false)
    })
    return () => { cancelled = true }
  }, [url])

  // 渲染指定页面
  const renderPage = useCallback(async (pageNum: number) => {
    if (!pdfDoc || !canvasRef.current || !textLayerRef.current) return
    const page = await pdfDoc.getPage(pageNum)
    const viewport = page.getViewport({ scale: 1.5 })

    // Canvas 渲染
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')!
    canvas.width = viewport.width
    canvas.height = viewport.height
    await page.render({ canvasContext: ctx, viewport }).promise

    // 文本层渲染
    const textLayer = textLayerRef.current
    textLayer.innerHTML = ''
    textLayer.style.width = `${viewport.width}px`
    textLayer.style.height = `${viewport.height}px`

    const textContent = await page.getTextContent()
    // 渲染文本 span 到文本层
    textContent.items.forEach((item) => {
      if (!('str' in item)) return
      const tx = pdfjsLib.Util.transform(
        viewport.transform,
        (item as { transform: number[] }).transform
      )
      const span = document.createElement('span')
      span.textContent = item.str
      span.style.position = 'absolute'
      span.style.left = `${tx[4]}px`
      span.style.top = `${tx[5]}px`
      span.style.fontSize = `${Math.hypot(tx[0], tx[1])}px`
      span.style.fontFamily = 'sans-serif'
      span.style.transformOrigin = '0% 0%'
      textLayer.appendChild(span)
    })
  }, [pdfDoc])

  useEffect(() => {
    if (pdfDoc) renderPage(currentPage)
  }, [pdfDoc, currentPage, renderPage])

  // 翻页
  const goPage = (delta: number) => {
    const next = currentPage + delta
    if (next >= 1 && next <= totalPages) {
      setCurrentPage(next)
      onPageChange?.(next)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-full text-gray-400">加载 PDF 中...</div>
  }

  return (
    <div className="flex flex-col items-center h-full overflow-auto">
      {/* PDF 渲染区域 */}
      <div className="relative flex-1 overflow-auto p-4">
        <canvas ref={canvasRef} className="mx-auto shadow" />
        <div ref={textLayerRef} className="absolute top-4 left-1/2 -translate-x-1/2 select-text opacity-40 pointer-events-auto" />
      </div>
      {/* 分页控制 */}
      <div className="flex items-center gap-4 py-3 border-t bg-white">
        <button onClick={() => goPage(-1)} disabled={currentPage <= 1}
          className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 disabled:opacity-40">
          上一页
        </button>
        <span className="text-sm text-gray-600">{currentPage} / {totalPages}</span>
        <button onClick={() => goPage(1)} disabled={currentPage >= totalPages}
          className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 disabled:opacity-40">
          下一页
        </button>
      </div>
    </div>
  )
}
