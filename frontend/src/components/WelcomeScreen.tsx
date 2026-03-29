import { Bot, Zap, Shield, Search } from "lucide-react"
import { SUGGESTIONS } from "./ChatInput"

interface Props { onSuggestion: (s: string) => void }

export default function WelcomeScreen({ onSuggestion }: Props) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-6 py-12 text-center">
      <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center mb-5 shadow-lg shadow-blue-200 dark:shadow-blue-900/40">
        <Bot size={30} className="text-white" />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Hi, I'm JARVIS</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-sm text-sm leading-relaxed">
        Your AI assistant for internal documentation. Ask me anything about your team's knowledge base.
      </p>
      <div className="flex flex-wrap gap-2 justify-center mb-10">
        {[{ icon: Search, label: "Semantic search" }, { icon: Zap, label: "Instant answers" }, { icon: Shield, label: "Secure & local" }]
          .map(({ icon: Icon, label }) => (
            <span key={label} className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-800
              text-gray-600 dark:text-gray-400 rounded-full text-xs font-medium border border-gray-200 dark:border-gray-700">
              <Icon size={11} /> {label}
            </span>
          ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-2xl">
        {SUGGESTIONS.map(s => (
          <button key={s} onClick={() => onSuggestion(s)}
            className="text-left px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200
              dark:border-gray-700 rounded-xl text-sm text-gray-600 dark:text-gray-300
              hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20
              hover:text-blue-700 dark:hover:text-blue-300 transition-all shadow-sm">
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
