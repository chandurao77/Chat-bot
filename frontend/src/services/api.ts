import type { SourceCitation } from "../types"

const BASE = "/api"
const KEY  = (import.meta as any).env?.VITE_API_KEY ?? ""
const h    = () => ({ "Content-Type": "application/json", "X-API-Key": KEY })

export type SSEEvent =
  | { type: "status";  message: string }
  | { type: "token";   text: string }
  | { type: "sources"; data: SourceCitation[] }
  | { type: "error";   message: string }
  | { type: "done" }

export async function* streamChat(question: string, conversationId?: string): AsyncGenerator<SSEEvent> {
  const res = await fetch(`${BASE}/chat/stream`, {
    method: "POST", headers: h(),
    body: JSON.stringify({ question, conversation_id: conversationId }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const reader  = res.body!.getReader()
  const decoder = new TextDecoder()
  let buf = ""
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    const parts = buf.split("\n\n")
    buf = parts.pop() ?? ""
    for (const part of parts) {
      const lines     = part.split("\n")
      const eventLine = lines.find(l => l.startsWith("event:"))
      const dataLine  = lines.find(l => l.startsWith("data:"))
      if (!eventLine || !dataLine) continue
      const event = eventLine.slice(6).trim()
      const raw   = dataLine.slice(5).trim()
      try {
        const p = JSON.parse(raw)
        if      (event === "status")  yield { type: "status",  message: p.message }
        else if (event === "token")   yield { type: "token",   text: p.text }
        else if (event === "sources") yield { type: "sources", data: p }
        else if (event === "error")   yield { type: "error",   message: p.message }
        else if (event === "done")    yield { type: "done" }
      } catch {}
    }
  }
}

export const api = {
  getConversations: ()                           => fetch(`${BASE}/conversations`, { headers: h() }).then(r => r.json()),
  deleteConversation: (id: string)               => fetch(`${BASE}/conversations/${id}`, { method: "DELETE", headers: h() }).then(r => r.json()),
  renameConversation: (id: string, title: string)=> fetch(`${BASE}/conversations/${id}`, { method: "PATCH",  headers: h(), body: JSON.stringify({ title }) }).then(r => r.json()),
  moveConversation: (id: string, folder_id: string | null) => fetch(`${BASE}/conversations/${id}/move`, { method: "PATCH", headers: h(), body: JSON.stringify({ folder_id }) }).then(r => r.json()),
  getFolders: ()                                 => fetch(`${BASE}/folders`, { headers: h() }).then(r => r.json()),
  createFolder: (name: string)                   => fetch(`${BASE}/folders`, { method: "POST",   headers: h(), body: JSON.stringify({ name }) }).then(r => r.json()),
  deleteFolder: (id: string)                     => fetch(`${BASE}/folders/${id}`, { method: "DELETE", headers: h() }).then(r => r.json()),
  renameFolder: (id: string, name: string)       => fetch(`${BASE}/folders/${id}`, { method: "PATCH",  headers: h(), body: JSON.stringify({ name }) }).then(r => r.json()),
  ingestLocal: ()                                => fetch(`${BASE}/ingest/local`, { method: "POST", headers: h(), body: "{}" }).then(r => r.json()),
  health: ()                                     => fetch(`${BASE}/health`).then(r => r.json()),
}
