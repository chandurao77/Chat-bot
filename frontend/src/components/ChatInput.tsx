import { useState, useRef, useEffect } from "react"
import { Send, Square } from "lucide-react"

interface Props { onSend: (msg: string) => void; onStop: () => void; isLoading: boolean }

export const SUGGESTIONS = [
  "What is the onboarding checklist for day 1?",
  "How do I deploy to production?",
  "What should I do during a P0 incident?",
  "How do I roll back a deployment?",
]

export default function ChatInput({ onSend, onStop, isLoading }: Props) {
  const [value, setValue] = useState("")
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = "auto"
      ref.current.style.height = Math.min(ref.current.scrollHeight, 200) + "px"
    }
  }, [value])

  const submit = () => { const t = value.trim(); if (!t || isLoading) return; onSend(t); setValue("") }
  const onKey  = (e: React.KeyboardEvent) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit() } }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700
        rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 transition-all">
        <textarea ref={ref} value={value} onChange={e => setValue(e.target.value)} onKeyDown={onKey}
          placeholder="Ask JARVIS anything about your documentation..." rows={1}
          className="w-full resize-none bg-transparent px-4 pt-3.5 pb-12 text-sm text-gray-800
            dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 outline-none max-h-48 leading-relaxed" />
        <div className="absolute bottom-2.5 right-2.5 flex items-center gap-2">
          <span className={`text-xs ${value.length > 1800 ? "text-red-400" : "text-gray-300 dark:text-gray-600"}`}>
            {value.length > 0 ? `${value.length}/2000` : ""}
          </span>
          {isLoading ? (
            <button onClick={onStop} className="p-2 rounded-xl bg-red-500 hover:bg-red-600 text-white transition-colors">
              <Square size={14} fill="currentColor" />
            </button>
          ) : (
            <button onClick={submit} disabled={!value.trim()}
              className={`p-2 rounded-xl transition-colors ${value.trim()
                ? "bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                : "bg-gray-100 dark:bg-gray-700 text-gray-300 dark:text-gray-500 cursor-not-allowed"}`}>
              <Send size={14} />
            </button>
          )}
        </div>
      </div>
      <p className="text-center text-xs text-gray-400 dark:text-gray-600 mt-2">
        JARVIS may make mistakes. Verify important information.
      </p>
    </div>
  )
}
