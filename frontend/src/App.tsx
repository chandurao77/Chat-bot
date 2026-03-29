import { useState, useEffect, useRef, useCallback } from "react"
import { Sun, Moon, PanelLeftClose, PanelLeft } from "lucide-react"
import Sidebar from "./components/Sidebar"
import MessageItem from "./components/MessageItem"
import ChatInput from "./components/ChatInput"
import WelcomeScreen from "./components/WelcomeScreen"
import { useTheme } from "./hooks/useTheme"
import { useChat } from "./hooks/useChat"
import { api } from "./services/api"
import type { Conversation, Folder } from "./types"

export default function App() {
  const { theme, toggle }                 = useTheme()
  const [sidebarOpen, setSidebarOpen]     = useState(true)
  const [activeId, setActiveId]           = useState<string | undefined>()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [folders, setFolders]             = useState<Folder[]>([])
  const bottomRef                         = useRef<HTMLDivElement>(null)

  const handleFirstMsg = useCallback((_id: string) => { loadData() }, [])
  const { messages, isLoading, sendMessage, retry, stop, clear } = useChat(activeId, handleFirstMsg)

  const loadData = async () => {
    try {
      const [c, f] = await Promise.all([api.getConversations(), api.getFolders()])
      setConversations(c); setFolders(f)
    } catch {}
  }

  useEffect(() => { loadData() }, [])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])

  const handleNew    = () => { setActiveId(undefined); clear() }
  const handleSelect = (id: string) => { setActiveId(id); clear() }
  const handleDelete = async (id: string) => { await api.deleteConversation(id); if (activeId === id) handleNew(); loadData() }
  const handleRename = async (id: string, t: string) => { await api.renameConversation(id, t); loadData() }
  const handleMove   = async (id: string, fid: string | null) => { await api.moveConversation(id, fid); loadData() }
  const handleCF     = async (name: string) => { await api.createFolder(name); loadData() }
  const handleDF     = async (id: string) => { await api.deleteFolder(id); loadData() }
  const handleRF     = async (id: string, n: string) => { await api.renameFolder(id, n); loadData() }

  const activeTitle = conversations.find(c => c.id === activeId)?.title

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar conversations={conversations} folders={folders} activeId={activeId}
        onSelect={handleSelect} onNew={handleNew} onDelete={handleDelete}
        onRename={handleRename} onMove={handleMove} onCreateFolder={handleCF}
        onDeleteFolder={handleDF} onRenameFolder={handleRF} isOpen={sidebarOpen} />

      <div className={`flex flex-col flex-1 min-w-0 transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-0"}`}>
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-gray-200
          dark:border-gray-800 bg-white dark:bg-gray-900 shrink-0">
          <button onClick={() => setSidebarOpen(s => !s)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors">
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
          </button>
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-200 truncate max-w-xs">
            {activeTitle ?? "JARVIS"}
          </span>
          <button onClick={toggle}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors">
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0
            ? <WelcomeScreen onSuggestion={sendMessage} />
            : <div className="max-w-3xl mx-auto px-4 py-6">
                {messages.map(m => (
                  <MessageItem key={m.id} message={m}
                    onRetry={m.role === "assistant" ? () => retry(m.id) : undefined} />
                ))}
                <div ref={bottomRef} />
              </div>
          }
        </div>

        {/* Input */}
        <div className="shrink-0 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
          <ChatInput onSend={sendMessage} onStop={stop} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}
