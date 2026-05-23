import { useState, useEffect } from 'react'
import type { Session } from '../types'
import { getSessions } from '../services/api'

/** Session 状态管理 */
export function useSession() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [currentSession, setCurrentSession] = useState<Session | null>(null)

  const refresh = async () => {
    setLoading(true)
    try {
      const data = await getSessions()
      setSessions(data)
    } catch (e) {
      console.error('获取 sessions 失败', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])

  return { sessions, loading, currentSession, setCurrentSession, refresh }
}
