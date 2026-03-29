import { useState, useCallback, useRef } from "react"
import { streamChat } from "../services/api"
import type { Message, SourceCitation } from "../types"

let _id = 0
const uid = () => `msg-${++_id}-${Date.now()}`

export function useChat(conversationId: string | undefined, onFirstMessage: (id: string) => void) {
  const [messages,   setMessages]   = useState<Message[]>([])
  const [isLoading,  setIsLoading]  = useState(false)
  const abortRef = useRef(false)

  const sendMessage = useCallback(async (question: string) => {
    const userMsg: Message  = { id: uid(), role: "user",      content: question, createdAt: Date.now() }
    const asstId            = uid()
    const asstMsg: Message  = { id: asstId, role: "assistant", content: "", isStreaming: true, status: "Thinking...", createdAt: Date.now() }
    setMessages(prev => [...prev, userMsg, asstMsg])
    setIsLoading(true)
    abortRef.current = false

    try {
      for await (const event of streamChat(question, conversationId)) {
        if (abortRef.current) break
        if      (event.type === "status")  setMessages(prev => prev.map(m => m.id === asstId ? { ...m, status: event.message } : m))
        else if (event.type === "token")   setMessages(prev => prev.map(m => m.id === asstId ? { ...m, content: m.content + event.text, status: undefined } : m))
        else if (event.type === "sources") setMessages(prev => prev.map(m => m.id === asstId ? { ...m, sources: event.data } : m))
        else if (event.type === "error")   setMessages(prev => prev.map(m => m.id === asstId ? { ...m, content: event.message, isStreaming: false, status: undefined } : m))
        else if (event.type === "done")    setMessages(prev => prev.map(m => m.id === asstId ? { ...m, isStreaming: false, status: undefined } : m))
      }
    } catch {
      setMessages(prev => prev.map(m => m.id === asstId ? { ...m, content: "An error occurred. Please try again.", isStreaming: false, status: undefined } : m))
    } finally {
      setIsLoading(false)
    }
    onFirstMessage(conversationId ?? uid())
  }, [conversationId, onFirstMessage])

  const retry = useCallback((messageId: string) => {
    const idx = messages.findIndex(m => m.id === messageId)
    if (idx < 1) return
    const userMsg = messages[idx - 1]
    setMessages(prev => prev.slice(0, idx - 1))
    sendMessage(userMsg.content)
  }, [messages, sendMessage])

  const stop  = useCallback(() => { abortRef.current = true; setIsLoading(false); setMessages(prev => prev.map(m => m.isStreaming ? { ...m, isStreaming: false, status: undefined } : m)) }, [])
  const clear = useCallback(() => setMessages([]), [])

  return { messages, isLoading, sendMessage, retry, stop, clear }
}
