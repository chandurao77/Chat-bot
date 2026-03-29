export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: SourceCitation[]
  status?: string
  isStreaming?: boolean
  createdAt: number
}

export interface SourceCitation {
  title: string
  space: string
  score: number
  url: string
  snippet?: string
}

export interface Conversation {
  id: string
  title: string
  folder_id?: string | null
  created_at: number
  updated_at: number
}

export interface Folder {
  id: string
  name: string
  created_at: number
}

export type Theme = "light" | "dark"
