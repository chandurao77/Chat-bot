import { useState, useRef, useEffect } from "react"
import { MessageSquare, FolderPlus, Search, Plus, ChevronRight, ChevronDown,
         Folder, MoreHorizontal, Trash2, Pencil, FolderInput, Check, X, Bot } from "lucide-react"
import type { Conversation, Folder as FolderType } from "../types"
import { api } from "../services/api"

interface Props {
  conversations: Conversation[]
  folders: FolderType[]
  activeId?: string
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
  onRename: (id: string, title: string) => void
  onMove: (id: string, folderId: string | null) => void
  onCreateFolder: (name: string) => void
  onDeleteFolder: (id: string) => void
  onRenameFolder: (id: string, name: string) => void
  isOpen: boolean
}

export default function Sidebar({ conversations, folders, activeId, onSelect, onNew,
  onDelete, onRename, onMove, onCreateFolder, onDeleteFolder, onRenameFolder, isOpen }: Props) {
  const [search,        setSearch]        = useState("")
  const [expanded,      setExpanded]      = useState<Record<string, boolean>>({})
  const [menuId,        setMenuId]        = useState<string | null>(null)
  const [menuType,      setMenuType]      = useState<"conversation"|"folder">("conversation")
  const [menuPos,       setMenuPos]       = useState({ x: 0, y: 0 })
  const [renamingId,    setRenamingId]    = useState<string | null>(null)
  const [renameVal,     setRenameVal]     = useState("")
  const [moveTarget,    setMoveTarget]    = useState<string | null>(null)
  const [newFolder,     setNewFolder]     = useState(false)
  const [newFolderName, setNewFolderName] = useState("")
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const h = (e: MouseEvent) => { if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuId(null) }
    document.addEventListener("mousedown", h)
    return () => document.removeEventListener("mousedown", h)
  }, [])

  const filtered   = conversations.filter(c => c.title.toLowerCase().includes(search.toLowerCase()))
  const ungrouped  = filtered.filter(c => !c.folder_id)
  const inFolder   = (fid: string) => filtered.filter(c => c.folder_id === fid)

  const openMenu = (e: React.MouseEvent, type: "conversation"|"folder", id: string) => {
    e.preventDefault(); e.stopPropagation()
    setMenuType(type); setMenuId(id); setMenuPos({ x: e.clientX, y: e.clientY })
  }

  const startRename = (id: string, val: string) => { setRenamingId(id); setRenameVal(val); setMenuId(null) }
  const commitRename = (id: string) => {
    if (renameVal.trim()) menuType === "conversation" ? onRename(id, renameVal.trim()) : onRenameFolder(id, renameVal.trim())
    setRenamingId(null)
  }

  const ConvItem = ({ c }: { c: Conversation }) => (
    <div onClick={() => onSelect(c.id)}
      className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all text-sm
        ${activeId === c.id ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"}`}>
      <MessageSquare size={14} className="shrink-0 opacity-50" />
      {renamingId === c.id ? (
        <form onSubmit={e => { e.preventDefault(); commitRename(c.id) }} className="flex-1 flex gap-1" onClick={e => e.stopPropagation()}>
          <input autoFocus value={renameVal} onChange={e => setRenameVal(e.target.value)}
            className="flex-1 bg-white dark:bg-gray-700 border border-blue-400 rounded px-1 text-xs outline-none" />
          <button type="submit"><Check size={12} className="text-green-500" /></button>
          <button type="button" onClick={() => setRenamingId(null)}><X size={12} className="text-red-400" /></button>
        </form>
      ) : (
        <>
          <span className="flex-1 truncate text-xs">{c.title}</span>
          <button onClick={e => openMenu(e, "conversation", c.id)}
            className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 shrink-0">
            <MoreHorizontal size={14} />
          </button>
        </>
      )}
    </div>
  )

  return (
    <>
      <aside className={`fixed left-0 top-0 h-full z-30 flex flex-col bg-gray-50 dark:bg-gray-900
        border-r border-gray-200 dark:border-gray-800 transition-all duration-300
        ${isOpen ? "w-64" : "w-0 overflow-hidden"}`}>

        <div className="p-4 border-b border-gray-200 dark:border-gray-800 shrink-0">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
              <Bot size={15} className="text-white" />
            </div>
            <span className="font-bold text-gray-900 dark:text-white text-sm tracking-wide">JARVIS</span>
          </div>
          <button onClick={onNew} className="w-full flex items-center justify-center gap-2 px-3 py-2
            bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium transition-colors">
            <Plus size={15} /> New Chat
          </button>
        </div>

        <div className="px-3 py-2 shrink-0">
          <div className="flex items-center gap-2 bg-white dark:bg-gray-800 border border-gray-200
            dark:border-gray-700 rounded-lg px-2.5 py-1.5">
            <Search size={12} className="text-gray-400 shrink-0" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search chats..."
              className="flex-1 bg-transparent text-xs outline-none text-gray-700 dark:text-gray-300 placeholder-gray-400" />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5">
          {folders.map(f => (
            <div key={f.id}>
              <div onClick={() => setExpanded(p => ({ ...p, [f.id]: !p[f.id] }))}
                className="group flex items-center gap-1.5 px-2 py-1.5 rounded-lg cursor-pointer
                  hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400">
                {expanded[f.id] ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                <Folder size={12} className="text-blue-400" />
                {renamingId === f.id ? (
                  <form onSubmit={e => { e.preventDefault(); commitRename(f.id) }} className="flex-1 flex gap-1" onClick={e => e.stopPropagation()}>
                    <input autoFocus value={renameVal} onChange={e => setRenameVal(e.target.value)}
                      className="flex-1 bg-white dark:bg-gray-700 border border-blue-400 rounded px-1 text-xs outline-none" />
                    <button type="submit"><Check size={11} className="text-green-500" /></button>
                    <button type="button" onClick={() => setRenamingId(null)}><X size={11} className="text-red-400" /></button>
                  </form>
                ) : (
                  <>
                    <span className="flex-1 truncate text-xs font-medium uppercase tracking-wide">{f.name}</span>
                    <span className="text-xs text-gray-400">{inFolder(f.id).length}</span>
                    <button onClick={e => openMenu(e, "folder", f.id)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700">
                      <MoreHorizontal size={12} />
                    </button>
                  </>
                )}
              </div>
              {expanded[f.id] && (
                <div className="ml-3 space-y-0.5">
                  {inFolder(f.id).map(c => <ConvItem key={c.id} c={c} />)}
                  {inFolder(f.id).length === 0 && <p className="text-xs text-gray-400 px-3 py-1 italic">Empty</p>}
                </div>
              )}
            </div>
          ))}

          {ungrouped.length > 0 && (
            <div className="space-y-0.5">
              {folders.length > 0 && <p className="text-xs text-gray-400 px-2 pt-2 pb-1 uppercase tracking-wide font-medium">Recent</p>}
              {ungrouped.map(c => <ConvItem key={c.id} c={c} />)}
            </div>
          )}

          {conversations.length === 0 && (
            <p className="text-xs text-gray-400 text-center py-8">No conversations yet</p>
          )}

          {newFolder ? (
            <form onSubmit={e => { e.preventDefault(); if (newFolderName.trim()) { onCreateFolder(newFolderName.trim()); setNewFolderName(""); setNewFolder(false) } }}
              className="flex items-center gap-1 px-2 py-1 mt-1">
              <input autoFocus value={newFolderName} onChange={e => setNewFolderName(e.target.value)}
                placeholder="Folder name" className="flex-1 bg-white dark:bg-gray-700 border border-blue-400
                rounded px-2 py-1 text-xs outline-none text-gray-700 dark:text-gray-200" />
              <button type="submit"><Check size={12} className="text-green-500" /></button>
              <button type="button" onClick={() => setNewFolder(false)}><X size={12} className="text-red-400" /></button>
            </form>
          ) : (
            <button onClick={() => setNewFolder(true)} className="w-full flex items-center gap-2 px-2 py-1.5
              text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg
              hover:bg-gray-100 dark:hover:bg-gray-800 mt-1">
              <FolderPlus size={12} /> New folder
            </button>
          )}
        </div>
      </aside>

      {/* Context Menu */}
      {menuId && (
        <div ref={menuRef} style={{ position: "fixed", top: menuPos.y, left: menuPos.x, zIndex: 200 }}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700
            rounded-xl shadow-2xl py-1 min-w-[180px]">
          {menuType === "conversation" && <>
            <button onClick={() => { setMoveTarget(menuId); setMenuId(null) }}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200
                hover:bg-gray-50 dark:hover:bg-gray-700">
              <FolderInput size={14} className="text-blue-500" /> Move to folder
            </button>
            <button onClick={() => { const c = conversations.find(x => x.id === menuId); if (c) { setMenuType("conversation"); startRename(c.id, c.title) } }}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200
                hover:bg-gray-50 dark:hover:bg-gray-700">
              <Pencil size={14} className="text-gray-400" /> Rename
            </button>
            <div className="border-t border-gray-100 dark:border-gray-700 my-1" />
            <button onClick={() => { onDelete(menuId); setMenuId(null) }}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-500
                hover:bg-red-50 dark:hover:bg-red-900/20">
              <Trash2 size={14} /> Delete
            </button>
          </>}
          {menuType === "folder" && <>
            <button onClick={() => { const f = folders.find(x => x.id === menuId); if (f) { setMenuType("folder"); startRename(f.id, f.name) } }}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200
                hover:bg-gray-50 dark:hover:bg-gray-700">
              <Pencil size={14} className="text-gray-400" /> Rename folder
            </button>
            <div className="border-t border-gray-100 dark:border-gray-700 my-1" />
            <button onClick={() => { onDeleteFolder(menuId); setMenuId(null) }}
              className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-500
                hover:bg-red-50 dark:hover:bg-red-900/20">
              <Trash2 size={14} /> Delete folder
            </button>
          </>}
        </div>
      )}

      {/* Move to Folder Modal */}
      {moveTarget && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-xs p-5">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1 flex items-center gap-2">
              <FolderInput size={17} className="text-blue-500" /> Move to folder
            </h3>
            <p className="text-xs text-gray-400 mb-4">Select a folder for this conversation</p>
            <div className="space-y-1 max-h-56 overflow-y-auto">
              <button onClick={() => { onMove(moveTarget, null); setMoveTarget(null) }}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm
                  text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                <MessageSquare size={14} className="text-gray-400" /> No folder
              </button>
              {folders.map(f => (
                <button key={f.id} onClick={() => { onMove(moveTarget, f.id); setMoveTarget(null) }}
                  className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm
                    text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-blue-900/30">
                  <Folder size={14} className="text-blue-500" /> {f.name}
                </button>
              ))}
              {folders.length === 0 && <p className="text-xs text-gray-400 text-center py-3">No folders yet</p>}
            </div>
            <button onClick={() => setMoveTarget(null)} className="mt-3 w-full py-2 text-xs text-gray-400 hover:text-gray-600">Cancel</button>
          </div>
        </div>
      )}
    </>
  )
}
