/** 阅读 Session */
export interface Session {
  id: string
  title: string
  doc_type: string
  file_path: string
  created_at: string
  status: string
}

/** 文档段落 */
export interface Paragraph {
  page: number
  index: number
  text: string
}

/** 文档内容响应 */
export interface DocumentContent {
  paragraphs: Paragraph[]
  total_pages: number
  current_page: number
}

/** 词典释义 */
export interface DictMeaning {
  part_of_speech: string
  definitions: { definition: string; example: string | null }[]
}

export interface DictResult {
  word: string
  phonetic: string | null
  meanings: DictMeaning[]
}

/** 聊天消息 */
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

/** 文本选择状态 */
export interface TextSelection {
  text: string
  rect: DOMRect | null
  isActive: boolean
}
