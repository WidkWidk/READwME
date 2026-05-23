import { useState, useCallback, useRef } from 'react'

interface SSEState {
  content: string
  isStreaming: boolean
  error: string | null
}

/** SSE 流式接收 hook */
export function useSSE() {
  const [state, setState] = useState<SSEState>({ content: '', isStreaming: false, error: null })
  const abortRef = useRef<AbortController | null>(null)

  const start = useCallback(async (url: string, body: object) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setState({ content: '', isStreaming: true, error: null })

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const reader = res.body?.getReader()
      if (!reader) throw new Error('No reader')

      const decoder = new TextDecoder()
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        const lines = text.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.content) {
                accumulated += data.content
                setState(s => ({ ...s, content: accumulated }))
              }
              if (data.error) {
                setState(s => ({ ...s, error: data.error, isStreaming: false }))
                return
              }
            } catch { /* 忽略解析错误 */ }
          }
        }
      }
      setState(s => ({ ...s, isStreaming: false }))
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setState(s => ({ ...s, error: err instanceof Error ? err.message : 'Unknown error', isStreaming: false }))
      }
    }
  }, [])

  const stop = useCallback(() => {
    abortRef.current?.abort()
    setState(s => ({ ...s, isStreaming: false }))
  }, [])

  return { ...state, start, stop }
}
