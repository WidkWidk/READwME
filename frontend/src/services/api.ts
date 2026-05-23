import type { Session, DocumentContent, DictResult } from '../types'

const BASE = '/api'

/** 获取所有 sessions */
export async function getSessions(): Promise<Session[]> {
  const res = await fetch(`${BASE}/sessions`)
  return res.json()
}

/** 创建 session（上传文件） */
export async function createSession(file: File, title: string): Promise<Session> {
  const form = new FormData()
  form.append('file', file)
  form.append('title', title)
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form })
  return res.json()
}

/** 获取文档内容（分页） */
export async function getDocumentContent(docId: string, page = 1, pageSize = 10): Promise<DocumentContent> {
  const res = await fetch(`${BASE}/documents/${docId}/content?page=${page}&page_size=${pageSize}`)
  return res.json()
}

/** 词典查询 */
export async function lookupWord(word: string): Promise<DictResult> {
  const res = await fetch(`${BASE}/dictionary/lookup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ word })
  })
  return res.json()
}

/** 删除 session */
export async function deleteSession(id: string): Promise<void> {
  await fetch(`${BASE}/sessions/${id}`, { method: 'DELETE' })
}

/** Agent: 记笔记 */
export async function takeNote(sessionId: string, content: string, sourceText = '', noteTitle?: string) {
  const res = await fetch(`${BASE}/agent/note`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, content, source_text: sourceText, note_title: noteTitle })
  })
  return res.json()
}
