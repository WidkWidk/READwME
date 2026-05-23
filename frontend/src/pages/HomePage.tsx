import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../hooks/useSession'
import { createSession, deleteSession } from '../services/api'

/** 首页 — Session 列表 */
export function HomePage() {
  const { sessions, loading, refresh } = useSession()
  const navigate = useNavigate()
  const [showUpload, setShowUpload] = useState(false)
  const [title, setTitle] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  const handleUpload = async () => {
    if (!file || !title.trim()) return
    setUploading(true)
    try {
      const session = await createSession(file, title)
      await refresh()
      setShowUpload(false)
      setTitle('')
      setFile(null)
      navigate(`/read/${session.id}`)
    } catch {
      alert('上传失败')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('确定删除？')) {
      await deleteSession(id)
      refresh()
    }
  }

  if (loading) return <div className="flex items-center justify-center h-full">加载中...</div>

  return (
    <div className="h-full flex flex-col">
      <header className="flex items-center justify-between px-4 py-3 border-b bg-white">
        <h1 className="text-xl font-bold">📚 伴读</h1>
        <button
          onClick={() => setShowUpload(true)}
          className="w-9 h-9 rounded-full bg-blue-500 text-white text-xl flex items-center justify-center hover:bg-blue-600"
        >+</button>
      </header>

      {/* Session 列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {sessions.length === 0 && (
          <p className="text-center text-gray-400 mt-10">还没有阅读记录，点击 + 开始</p>
        )}
        {sessions.map(s => (
          <div
            key={s.id}
            onClick={() => navigate(`/read/${s.id}`)}
            className="bg-white rounded-lg p-4 shadow-sm border cursor-pointer hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium">{s.title}</h3>
                <p className="text-sm text-gray-500 mt-1">{s.doc_type.toUpperCase()} · {new Date(s.created_at).toLocaleDateString()}</p>
              </div>
              <button
                onClick={(e) => handleDelete(s.id, e)}
                className="text-gray-400 hover:text-red-500 text-sm"
              >删除</button>
            </div>
          </div>
        ))}
      </div>

      {/* 上传弹窗 */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-bold">新建阅读</h2>
            <input
              type="text"
              placeholder="书名/标题"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
            />
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={e => setFile(e.target.files?.[0] || null)}
              className="w-full"
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowUpload(false)} className="px-4 py-2 text-gray-600">取消</button>
              <button
                onClick={handleUpload}
                disabled={uploading || !file || !title.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
              >{uploading ? '上传中...' : '开始阅读'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
