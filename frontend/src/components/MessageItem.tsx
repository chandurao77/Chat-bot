import { useState } from "react"
import { Copy, Check, RefreshCw, Bot, User, ExternalLink, ChevronDown, ChevronUp } from "lucide-react"
import type { Message } from "../types"

interface Props { message: Message; onRetry?: () => void }

export default function MessageItem({ message, onRetry }: Props) {
  const [copied,      setCopied]      = useState(false)
  const [showSources, setShowSources] = useState(false)
  const isUser     = message.role === "user"
  const hasSources = (message.sources?.length ?? 0) > 0

  const copy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`group flex gap-3 py-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center
        ${isUser ? "bg-gray-500 dark:bg-gray-600" : "bg-blue-600"}`}>
        {isUser ? <User size={14} className="text-white" /> : <Bot size={14} className="text-white" />}
      </div>
      <div className={`flex flex-col gap-1.5 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        {message.status && (
          <div className="flex items-center gap-1.5 text-xs text-blue-500 dark:text-blue-400">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse inline-block" />
            {message.status}
          </div>
        )}
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words
          ${isUser
            ? "bg-blue-600 text-white rounded-tr-sm"
            : "bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-gray-700 rounded-tl-sm shadow-sm"}`}>
          {message.content || (!message.isStreaming && <span className="text-gray-400 italic text-xs">No response.</span>)}
          {message.isStreaming && <span className="inline-block w-2 h-4 bg-current opacity-60 ml-0.5 animate-pulse rounded-sm align-middle" />}
        </div>

        {hasSources && (
          <div className="w-full">
            <button onClick={() => setShowSources(s => !s)}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500 transition-colors mt-0.5">
              {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {message.sources!.length} source{message.sources!.length !== 1 ? "s" : ""}
            </button>
            {showSources && (
              <div className="mt-2 space-y-1.5">
                {message.sources!.map((s, i) => (
                  <a key={i} href={s.url || "#"} target="_blank" rel="noreferrer"
                    className="flex items-start gap-2 p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/80
                      border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600
                      hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all group/s block">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1">
                        <span className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">{s.title}</span>
                        <ExternalLink size={9} className="text-gray-300 opacity-0 group-hover/s:opacity-100 shrink-0" />
                      </div>
                      {s.snippet && <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">{s.snippet}</p>}
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-1.5 py-0.5 rounded-md">{s.space}</span>
                        <span className="text-xs text-gray-400">{Math.round(s.score * 100)}% match</span>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}

        {!isUser && !message.isStreaming && (
          <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={copy} title="Copy"
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600 transition-colors">
              {copied ? <Check size={12} className="text-green-500" /> : <Copy size={12} />}
            </button>
            {onRetry && (
              <button onClick={onRetry} title="Retry"
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600 transition-colors">
                <RefreshCw size={12} />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
